"""Independent exact check of the cab -> fcc curve of results/fold-continuous-fcc/PROOF.md (Section 1 only is used:
the formula for L(s) and the motif). Shares no code with the repository.

What it checks, all in exact arithmetic over Q(sqrt2):
 1. all 15 bars (12 octahedron edges, 3 bridges) have squared length 2 for every s, as a polynomial identity;
 2. non-overlap |n L(s) + v|^2 >= 2 for every motif difference v and every integer n in the box [-B,B]^3
    (B = 3 by default, 343 translations, a superset of the 171 the proof uses), on the whole interval [0,1],
    by Bernstein coefficients with de Casteljau subdivision when a coefficient is negative (a method choice made here);
 3. far images: the smallest eigenvalue of L(s)^T L(s) is >= 1 for all s, via its characteristic polynomial
    (an argument different from the repository's symmetric-part bound): we check that det(L^T L - lam I) has no
    root lam < 1, by showing the cubic g(lam) = -det(L^T L - lam I) ... see far_bound() for the exact test;
 4. the endpoint: 12 contacts per ball, determinant 12, density pi/sqrt18;
 5. det L(s) is strictly decreasing on [0,1] (exact Bernstein sign of the derivative numerator).
A corrupted curve (bridge sign flipped) must fail; run with --corrupt.
"""
import sys, itertools, argparse
sys.path.insert(0, __import__("os").path.dirname(__file__))
from elastic_indep import Q2, ZERO, check
from flint import fmpq
from math import comb

R2 = Q2(0, 1)          # sqrt2
ONE = Q2(1)


# ---------- polynomials in s with Q2 coefficients (list, low degree first) ----------
def padd(p, q):
    r = [ZERO] * max(len(p), len(q))
    for i, x in enumerate(p):
        r[i] = r[i] + x
    for i, x in enumerate(q):
        r[i] = r[i] + x
    return r


def pmul(p, q):
    r = [ZERO] * (len(p) + len(q) - 1)
    for i, x in enumerate(p):
        if x.iszero():
            continue
        for j, y in enumerate(q):
            r[i + j] = r[i + j] + x * y
    return r


def pscale(p, c):
    return [x * c for x in p]


def ptrim(p):
    p = list(p)
    while len(p) > 1 and p[-1].iszero():
        p.pop()
    return p


def pderiv(p):
    return [p[i] * i for i in range(1, len(p))] or [ZERO]


def to_bernstein(p, deg):
    """power coefficients -> Bernstein coefficients on [0,1] of degree deg (deg >= len(p)-1)."""
    p = p + [ZERO] * (deg + 1 - len(p))
    b = []
    for k in range(deg + 1):
        acc = ZERO
        for j in range(k + 1):
            acc = acc + p[j] * Q2(fmpq(comb(k, j), comb(deg, j)))
        b.append(acc)
    return b


def casteljau_split(b):
    """Split Bernstein coefficients on [0,1] into those on [0,1/2] and [1/2,1]."""
    half = Q2(fmpq(1, 2))
    left, right = [b[0]], [b[-1]]
    cur = list(b)
    while len(cur) > 1:
        cur = [(cur[i] + cur[i + 1]) * half for i in range(len(cur) - 1)]
        left.append(cur[0])
        right.append(cur[-1])
    return left, right[::-1]


def nonneg_on_unit(p, depth=0, maxdepth=30):
    """Exact proof that p >= 0 on [0,1] by Bernstein + subdivision. Returns (ok, n_leaves, n_zero_coeffs_top)."""
    deg = len(p) - 1
    b = to_bernstein(p, deg)
    return _nn(b, 0, maxdepth)


def _nn(b, depth, maxdepth):
    if all(x.sign() >= 0 for x in b):
        return True, 1
    # a negative endpoint value is a genuine counterexample
    if b[0].sign() < 0 or b[-1].sign() < 0:
        return False, 1
    if depth >= maxdepth:
        return False, 1
    l, r = casteljau_split(b)
    ok1, n1 = _nn(l, depth + 1, maxdepth)
    if not ok1:
        return False, n1
    ok2, n2 = _nn(r, depth + 1, maxdepth)
    return ok2, n1 + n2


# ---------- the curve (PROOF.md Section 1), as polynomial vectors after multiplying by (1+s^2) ----------
CM = [[0, -1, -1], [1, 0, -1], [1, -1, 0]]


def lattice_poly(corrupt=False):
    """Return M(s) = (1+s^2) L(s) as 3x3 matrix of polynomials in s. d(1+s^2) = (2+sqrt2) + (2-sqrt2) s^2, t(1+s^2) = 2s."""
    sgn = -1 if corrupt else 1
    M = [[None] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            dpart = [Q2(2, 1), ZERO, Q2(2, -1)] if i == j else [ZERO, ZERO, ZERO]
            tpart = [ZERO, Q2(2 * CM[i][j] * sgn), ZERO]
            M[i][j] = padd(dpart, tpart)
    return M


MOTIF = []
for a in range(3):
    for sg in (1, -1):
        v = [0, 0, 0]
        v[a] = sg
        MOTIF.append(v)
W = [Q2(1), Q2(0), Q2(1)]   # weight (1+s^2) as polynomial


def vec_poly(n, v, M):
    """(1+s^2) (n L(s) + v) as 3 polynomials."""
    out = []
    for k in range(3):
        acc = pscale(W, Q2(v[k]))
        for i in range(3):
            if n[i]:
                acc = padd(acc, pscale(M[i][k], Q2(n[i])))
        out.append(acc)
    return out


def sq_poly(vp):
    acc = [ZERO]
    for c in vp:
        acc = padd(acc, pmul(c, c))
    return acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--box", type=int, default=3)
    ap.add_argument("--corrupt", action="store_true")
    args = ap.parse_args()
    M = lattice_poly(args.corrupt)
    W2x2 = pscale(pmul(W, W), Q2(2))        # 2 (1+s^2)^2
    # 1. bars
    nbars = 0
    for p in MOTIF:
        for q in MOTIF:
            if p < q and p != [-x for x in q]:
                f = ptrim(padd(sq_poly([pscale(W, Q2(p[k] - q[k])) for k in range(3)]), pscale(W2x2, Q2(-1))))
                check(all(x.iszero() for x in f), "octahedron edge not length sqrt2")
                nbars += 1
    for i in range(3):
        n = [1 if k == i else 0 for k in range(3)]
        p = MOTIF[2 * i]        # +e_i
        q = MOTIF[2 * i + 1]    # -e_i
        # bridge: +e_i (cell 0) to -e_i (cell n): vector = n L + q - p
        v = [q[k] - p[k] for k in range(3)]
        f = ptrim(padd(sq_poly(vec_poly(n, v, M)), pscale(W2x2, Q2(-1))))
        check(all(x.iszero() for x in f), f"bridge {i} not length sqrt2 for all s")
        nbars += 1
    check(nbars == 12 + 3, "bar count")
    # 2. non-overlap on the box
    diffs = sorted({tuple(p[k] - q[k] for k in range(3)) for p in MOTIF for q in MOTIF})
    check(len(diffs) == 19, "motif differences")
    npairs = 0
    nzero_ident = 0
    leaves_total = 0
    touching_end = 0
    B = args.box
    for n in itertools.product(range(-B, B + 1), repeat=3):
        for v in diffs:
            if all(x == 0 for x in n) and all(x == 0 for x in v):
                continue
            f = ptrim(padd(sq_poly(vec_poly(n, v, M)), pscale(W2x2, Q2(-1))))
            npairs += 1
            if all(x.iszero() for x in f):
                nzero_ident += 1
                continue
            ok, leaves = nonneg_on_unit(f)
            leaves_total += leaves
            check(ok, f"overlap: n={n} v={v} f={f}")
            # value at s = 1
            val1 = ZERO
            for x in f:
                val1 = val1 + x
            if val1.iszero():
                touching_end += 1
    print(f"non-overlap: {npairs} (n,v) pairs in box [-{B},{B}]^3 proved >= 0 on [0,1]; "
          f"{nzero_ident} identically zero (bars); {touching_end} more touch at s=1; Bernstein leaves {leaves_total}")
    # 3. far images. Claim: |w L(s)| >= |w| for all real w and s in [0,1].
    # Equivalent: G(s) = L L^T - I is PSD. Check via the principal minors of (1+s^2)^2 G(s) being >= 0 on [0,1]
    # (Sylvester for PSD needs ALL principal minors >= 0).
    G = [[None] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            acc = [ZERO]
            for k in range(3):
                acc = padd(acc, pmul(M[i][k], M[j][k]))
            if i == j:
                acc = padd(acc, pscale(pmul(W, W), Q2(-1)))
            G[i][j] = acc

    def det2(a, b, c, d):
        return padd(pmul(a, d), pscale(pmul(b, c), Q2(-1)))

    minors = []
    for i in range(3):
        minors.append(G[i][i])
    for i, j in ((0, 1), (0, 2), (1, 2)):
        minors.append(det2(G[i][i], G[i][j], G[j][i], G[j][j]))
    d3 = [ZERO]
    for j in range(3):
        a, b = [k for k in range(3) if k != j]
        cof = det2(G[1][a], G[1][b], G[2][a], G[2][b])
        term = pmul(G[0][j], cof)
        d3 = padd(d3, term if j % 2 == 0 else pscale(term, Q2(-1)))
    minors.append(d3)
    for mnr in minors:
        ok, _ = nonneg_on_unit(ptrim(mnr))
        check(ok, "L L^T - I not PSD on [0,1]")
    # with |w L| >= |w|: |nL + v| >= |n| - 2 >= sqrt2 once |n| >= 2 + sqrt2 (|n|^2 >= 12). Every n with |n|^2 <= 11
    # lies in [-3,3]^3, which the box covers when B >= 3.
    check(B >= 3, "box too small for the far bound")
    print("far images: L(s) L(s)^T - I is PSD on [0,1] (all 7 principal minors certified >= 0), so |nL+v| >= |n|-2")
    # 4. endpoint s = 1
    L1 = [[sum((x for x in M[i][j]), ZERO) / Q2(2) for j in range(3)] for i in range(3)]
    print("L(1) =", [[str(x) for x in row] for row in L1])
    det1 = (L1[0][0] * (L1[1][1] * L1[2][2] - L1[1][2] * L1[2][1]) - L1[0][1] * (L1[1][0] * L1[2][2] - L1[1][2] * L1[2][0])
            + L1[0][2] * (L1[1][0] * L1[2][1] - L1[1][1] * L1[2][0]))
    check(det1 == Q2(12), "endpoint determinant")
    contacts = [0] * 6
    for pi, p in enumerate(MOTIF):
        for n in itertools.product(range(-3, 4), repeat=3):
            for q in MOTIF:
                if n == (0, 0, 0) and p == q:
                    continue
                x = [sum((Q2(n[i]) * L1[i][k] for i in range(3)), ZERO) + Q2(q[k] - p[k]) for k in range(3)]
                d2 = x[0] * x[0] + x[1] * x[1] + x[2] * x[2]
                check(not (d2 < Q2(2)), "endpoint overlap")
                if d2 == Q2(2):
                    contacts[pi] += 1
    check(all(c == 12 for c in contacts), f"endpoint contacts {contacts}")
    print("endpoint: det 12, 12 contacts at each of 6 balls; density = 6*(4pi/3)(1/sqrt2)^3/12 = pi/sqrt18")
    # 5. det L(s) strictly decreasing. P(s) = det M(s) = (1+s^2)^3 det L(s). D' sign = sign of P'(1+s^2) - 6 s P.
    def det3(A):
        out = [ZERO]
        for j in range(3):
            a, b = [k for k in range(3) if k != j]
            cof = det2(A[1][a], A[1][b], A[2][a], A[2][b])
            term = pmul(A[0][j], cof)
            out = padd(out, term if j % 2 == 0 else pscale(term, Q2(-1)))
        return ptrim(out)
    P = det3(M)
    Qn = ptrim(padd(pmul(pderiv(P), W), pscale(pmul([ZERO, ONE], P), Q2(-6))))
    negQ = pscale(Qn, Q2(-1))
    ok, _ = nonneg_on_unit(negQ)
    check(ok, "det not non-increasing")
    # strictness: -Q has a zero at s=0 (t'(0) != 0 but D'(t) ~ t); show -Q(s)/s > 0 on [0,1]
    check(Qn[0].iszero(), "expected Q(0) = 0")
    q1 = ptrim(negQ[1:])
    b = to_bernstein(q1, len(q1) - 1)
    ok2, _ = nonneg_on_unit(q1)
    check(ok2 and b[0].sign() > 0 and b[-1].sign() > 0, "strictness")
    # a nonnegative polynomial with positive end values could still touch zero inside; check all Bernstein coeffs > 0
    check(all(x.sign() > 0 for x in b), "strict decrease needs all coefficients > 0 (refine if this fails)")
    print("density: det L(s) strictly decreasing on [0,1] (exact Bernstein, all coefficients of -Q(s)/s positive)")
    print("ALL FOLD CHECKS PASSED")


if __name__ == "__main__":
    main()
