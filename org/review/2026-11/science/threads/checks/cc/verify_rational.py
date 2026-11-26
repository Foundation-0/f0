"""
Independent verifier for the central-configuration certificates written by cert_arb.py.
Shares no code with cert_arb.py and does not use Arb: exact rational interval arithmetic (fractions.Fraction),
with outward rounding of every interval end to the grid 2^-P, and an explicitly proved bound for r^-1.

Reads only: n, centre_scale_exp2, box_radius_exp2, and for each class the pinned body k and the centre numerators.
It builds its own preconditioner, and checks:
  (1) x_k > 0 on the box;
  (2) Krawczyk: K(X) = c - C G(c) + (I - C DG(X)) [-h,h]  lies strictly inside X = c + [-h,h].
      Then X holds exactly one zero of the reduced system G (see cert_arb.py docstring for G and why its zeros are
      exactly the central configurations with lambda = 1 and body k on the positive x-axis);
  (3) the classes are pairwise distinct: the enclosures of I = sum |q_i|^2 over K(X) ∩ X are pairwise disjoint
      (I is invariant under rotation, reflection and relabelling, and the scale is fixed by lambda = 1).

Bound for r^-1.  For r^2 in [a, b] with a > 0, r^-1 = (r^2)^(-1/2) is decreasing in r^2, so
r^-1 in [1/sqrt(b), 1/sqrt(a)].  We use integer square roots: for t > 0 and s = isqrt(floor(t 4^P)),
s/2^P <= sqrt(t) and sqrt(t) <= (isqrt(ceil(t 4^P)) + 1)/2^P.  Then r^-3, r^-5 are powers of a positive interval.
Usage: python -I verify_rational.py cert.json
"""
import sys, json
from fractions import Fraction as Fr
from math import isqrt
import numpy as np

P = 120
SC = 1 << P


def die(msg):
    raise SystemExit("REJECT: " + msg)


def dn(x):  # round down to grid
    return Fr((x.numerator * SC) // x.denominator, SC)


def up(x):
    return Fr(-((-x.numerator * SC) // x.denominator), SC)


class Iv:
    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        if hi is None:
            hi = lo
        self.lo = lo; self.hi = hi

    def __add__(s, o):
        o = o if isinstance(o, Iv) else Iv(Fr(o))
        return Iv(s.lo + o.lo, s.hi + o.hi)
    __radd__ = __add__

    def __sub__(s, o):
        o = o if isinstance(o, Iv) else Iv(Fr(o))
        return Iv(s.lo - o.hi, s.hi - o.lo)

    def __rsub__(s, o):
        return Iv(Fr(o)) - s

    def __neg__(s):
        return Iv(-s.hi, -s.lo)

    def __mul__(s, o):
        o = o if isinstance(o, Iv) else Iv(Fr(o))
        p = (s.lo * o.lo, s.lo * o.hi, s.hi * o.lo, s.hi * o.hi)
        return Iv(dn(min(p)), up(max(p)))
    __rmul__ = __mul__

    def mag(s):
        return max(abs(s.lo), abs(s.hi))


def sqrt_lo(t):
    return Fr(isqrt((t.numerator * SC * SC) // t.denominator), SC)


def sqrt_hi(t):
    return Fr(isqrt(-((-t.numerator * SC * SC) // t.denominator)) + 1, SC)


def rinv(r2):
    if not r2.lo > 0:
        die("r^2 interval touches 0")
    lo_s = sqrt_lo(r2.lo)
    if not lo_s > 0:
        die("r^2 too small for the sqrt bound")
    return Iv(dn(1 / sqrt_hi(r2.hi)), up(1 / lo_s))


def sq(a):  # square of an interval (tighter than a*a when it straddles 0)
    if a.lo >= 0:
        return Iv(dn(a.lo * a.lo), up(a.hi * a.hi))
    if a.hi <= 0:
        return Iv(dn(a.hi * a.hi), up(a.lo * a.lo))
    return Iv(Fr(0), up(max(a.lo * a.lo, a.hi * a.hi)))


def system(q, n):
    """Full F (2n) and Jacobian (2n x 2n) as intervals, for q a list of n pairs of intervals."""
    F = []
    J = [[Iv(Fr(0)) for _ in range(2 * n)] for _ in range(2 * n)]
    for i in range(n):
        fx = -q[i][0]; fy = -q[i][1]
        sxx = Iv(Fr(0)); sxy = Iv(Fr(0)); syy = Iv(Fr(0))
        for j in range(n):
            if j == i:
                continue
            dx = q[i][0] - q[j][0]; dy = q[i][1] - q[j][1]
            ri = rinv(sq(dx) + sq(dy))
            r3 = ri * ri * ri; r5 = r3 * ri * ri
            fx = fx + dx * r3; fy = fy + dy * r3
            axx = r3 - 3 * (r5 * sq(dx)); axy = -3 * (r5 * (dx * dy)); ayy = r3 - 3 * (r5 * sq(dy))
            J[2 * i][2 * j] = -axx; J[2 * i][2 * j + 1] = -axy
            J[2 * i + 1][2 * j] = -axy; J[2 * i + 1][2 * j + 1] = -ayy
            sxx = sxx + axx; sxy = sxy + axy; syy = syy + ayy
        J[2 * i][2 * i] = sxx - 1; J[2 * i][2 * i + 1] = sxy
        J[2 * i + 1][2 * i] = sxy; J[2 * i + 1][2 * i + 1] = syy - 1
        F += [fx, fy]
    return F, J


def float_jac(c, n):
    q = c.reshape(n, 2); J = np.zeros((2 * n, 2 * n))
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            d = q[i] - q[j]; r = np.sqrt(d @ d)
            A = np.eye(2) / r ** 3 - 3 * np.outer(d, d) / r ** 5
            J[2 * i:2 * i + 2, 2 * j:2 * j + 2] = -A
            J[2 * i:2 * i + 2, 2 * i:2 * i + 2] += A
        J[2 * i:2 * i + 2, 2 * i:2 * i + 2] -= np.eye(2)
    return J


def check_class(n, k, cnum, E, H):
    free = [t for t in range(2 * n) if t != 2 * k + 1]
    m = len(free)
    if len(cnum) != m:
        die("wrong number of coordinates")
    c = [Fr(int(t), 1 << E) for t in cnum]
    h = Fr(1, 1 << H)
    full_c = [Fr(0)] * (2 * n); full_X = [Iv(Fr(0))] * (2 * n)
    for a, v in zip(free, c):
        full_c[a] = v; full_X[a] = Iv(v - h, v + h)
    if not full_X[2 * k].lo > 0:
        die("x_k not positive on the box")
    Fc, _ = system([(Iv(full_c[2 * i]), Iv(full_c[2 * i + 1])) for i in range(n)], n)
    _, JX = system([(full_X[2 * i], full_X[2 * i + 1]) for i in range(n)], n)
    G = [Fc[a] for a in free]
    D = [[JX[a][b] for b in free] for a in free]
    Jf = float_jac(np.array([float(v) for v in full_c]), n)[np.ix_(free, free)]
    Cf = np.linalg.inv(Jf)
    C = [[Fr(int(round(Cf[i, j] * 2.0 ** 36)), 1 << 36) for j in range(m)] for i in range(m)]
    hI = Iv(-h, h)
    K = []
    for i in range(m):
        acc = Iv(c[i])
        for j in range(m):
            acc = acc - C[i][j] * G[j]
        for j in range(m):
            e = Iv(Fr(1 if i == j else 0))
            for l in range(m):
                e = e - C[i][l] * D[l][j]
            acc = acc + e * hI
        if not (acc.lo > c[i] - h and acc.hi < c[i] + h):
            die(f"Krawczyk inclusion fails (coordinate {i})")
        K.append(acc)
    Y = [Iv(max(Ki.lo, ci - h), min(Ki.hi, ci + h)) for Ki, ci in zip(K, c)]
    ratio = max(float(max(Ki.hi - ci, ci - Ki.lo) / h) for Ki, ci in zip(K, c))
    full_Y = [Iv(Fr(0))] * (2 * n)
    for a, v in zip(free, Y):
        full_Y[a] = v
    I = Iv(Fr(0))
    for t in full_Y:
        I = I + sq(t)
    return I, ratio, dict(Y=Y, full_Y=full_Y, c=c, h=h, free=free)


def inertia_exact(A):
    """Signs of the pivots of symmetric Gaussian elimination in exact rationals (Sylvester/Jacobi)."""
    A = [row[:] for row in A]; m = len(A); pos = neg = 0
    for i in range(m):
        piv = A[i][i]
        if piv == 0:
            die("zero pivot in inertia computation")
        if piv > 0:
            pos += 1
        else:
            neg += 1
        for r in range(i + 1, m):
            f = A[r][i] / piv
            if f:
                for cidx in range(i + 1, m):
                    A[r][cidx] -= f * A[i][cidx]
    return pos, neg


def morse_index(n, info):
    """Number of positive eigenvalues of the reduced Jacobian at the certified zero.
    J (true, symmetric) lies in the interval matrix DG(Y).  Take a symmetric rational M0; then |J - M0|_2 <= t'
    (max row sum of entrywise bounds; valid for symmetric J - M0).  If M0 - tI and M0 + tI (t = 2t') have the
    same inertia, M0 has no eigenvalue in [-t, t], and by Weyl's inequality J has the same inertia as M0."""
    free = info['free']; m = len(free)
    _, JY = system([(info['full_Y'][2 * i], info['full_Y'][2 * i + 1]) for i in range(n)], n)
    A = [[JY[a][b] for b in free] for a in free]
    mid = lambda v: (v.lo + v.hi) / 2
    M0 = [[dn((mid(A[i][j]) + mid(A[j][i])) / 2) for j in range(m)] for i in range(m)]
    for i in range(m):
        for j in range(i):
            M0[i][j] = M0[j][i]
    tp = max(sum(max(abs(A[i][j].lo - M0[i][j]), abs(A[i][j].hi - M0[i][j])) for j in range(m)) for i in range(m))
    t = 2 * tp + Fr(1, 1 << 100)
    plus = inertia_exact([[M0[i][j] + (t if i == j else 0) for j in range(m)] for i in range(m)])
    minus = inertia_exact([[M0[i][j] - (t if i == j else 0) for j in range(m)] for i in range(m)])
    if plus != minus:
        die("eigenvalue of the Jacobian not separated from 0")
    return plus[0]


def overlap(a, b):
    return a.lo <= b.hi and b.lo <= a.hi


def sym_order(n, k, info):
    """Order of the group of g in O(2) (with the induced relabelling) fixing the certified zero.
    A symmetry permutes bodies preserving |q_i|^2 and all r_ij^2: permutations violating this on the enclosures are
    excluded.  For a surviving permutation s and a choice of reflection, the image p_i = g q_s(i), rotated so that
    body k is on the positive x-axis, is again a zero of the reduced system; if its enclosure lies in the box it is
    the certified zero (uniqueness), so the map is a symmetry; if its enclosure misses Y it is not."""
    fy = info['full_Y']; free = info['free']; c = info['c']; h = info['h']; Y = info['Y']
    q = [(fy[2 * i], fy[2 * i + 1]) for i in range(n)]
    N2 = [sq(a) + sq(b) for a, b in q]
    R2 = [[sq(q[i][0] - q[j][0]) + sq(q[i][1] - q[j][1]) for j in range(n)] for i in range(n)]
    found = []
    def ext(sig):
        i = len(sig)
        if i == n:
            found.append(sig); return
        for j in range(n):
            if j not in sig and overlap(N2[j], N2[i]) and all(overlap(R2[j][sig[t]], R2[i][t]) for t in range(i)):
                ext(sig + (j,))
    ext(())
    count = 0
    for sig in found:
        for refl in (1, -1):
            p = [(q[sig[i]][0], q[sig[i]][1] * refl) for i in range(n)]
            px, py = p[k]
            inv = rinv(sq(px) + sq(py))
            ux = px * inv; uy = py * inv
            img = []
            for a, b in p:
                img += [ux * a + uy * b, uy * (-a) + ux * b]
            red = [img[a] for a in free]
            if all(r.lo >= ci - h and r.hi <= ci + h for r, ci in zip(red, c)):
                count += 1
            elif not all(overlap(r, y) for r, y in zip(red, Y)):
                pass
            else:
                die("symmetry candidate undecided")
    return count


def main():
    d = json.load(open(sys.argv[1]))
    n = int(d["n"]); E = int(d["centre_scale_exp2"]); H = int(d["box_radius_exp2"])
    Is = []; hs = []
    for ci, cl in enumerate(d["classes"]):
        k = int(cl["pinned_body"])
        if not 0 <= k < n:
            die("pinned body index")
        I, ratio, info = check_class(n, k, cl["centre_num"], E, H)
        Is.append(I)
        h_m = morse_index(n, info); s_ord = sym_order(n, k, info)
        hs.append((h_m, s_ord))
        if "morse_index" in cl and int(cl["morse_index"]) != h_m:
            die(f"class {ci+1}: Morse index in certificate disagrees")
        if "sym_order" in cl and int(cl["sym_order"]) != s_ord:
            die(f"class {ci+1}: symmetry order in certificate disagrees")
        Hu = int(cl.get("uniqueness_radius_exp2", H))
        if Hu != H:
            check_class(n, k, cl["centre_num"], E, Hu)   # same centre, larger box: uniqueness there too
        print(f"class {ci+1:3d}: one zero in radius 2^-{H} box (Krawczyk ratio {ratio:.2e}), unique in radius 2^-{Hu}; Morse index {h_m}, |Sym| {s_ord}; I in [{float(I.lo):.12f}, {float(I.hi):.12f}]", flush=True)
    order = sorted(range(len(Is)), key=lambda i: Is[i].lo)
    for a, b in zip(order, order[1:]):
        if not Is[a].hi < Is[b].lo:
            die(f"classes {a+1} and {b+1} not proved distinct")
    nf = 1
    for t in range(2, n + 1):
        nf *= t
    msum = sum((Fr(2 * (-1) ** a, b) for a, b in hs), Fr(0)); lab = sum(2 * nf // b for a, b in hs)
    poly = {}
    for a, b in hs:
        poly[a] = poly.get(a, 0) + 2 * nf // b
    print(f"labelled count (mod rotation, mirror images separate) {lab}; Morse polynomial coefficients {dict(sorted(poly.items()))}")
    print(f"Morse sum {msum}; Euler characteristic target {Fr((-1) ** n, n * (n - 1))}; equal: {msum == Fr((-1) ** n, n * (n - 1))}")
    if "labelled_count" in d and int(d["labelled_count"]) != lab:
        die("labelled count in certificate disagrees")
    print(f"ACCEPT: n = {n}: {len(Is)} pairwise distinct classes of planar central configurations, each certified "
          f"to exist and be unique in its box (so at least {len(Is)} classes)")


main()
