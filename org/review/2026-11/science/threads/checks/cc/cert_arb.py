"""
Certify planar central configurations of n equal unit masses with a Krawczyk test in Arb ball arithmetic.

System.  Masses 1, lambda = 1:   F_i(q) = sum_{j != i} (q_i - q_j) r_ij^-3 - q_i,   i = 0..n-1  (2n equations).
 * Summing over i gives sum_i q_i = 0 for every zero, so the centre of mass is 0 (translation removed).
 * lambda = 1 fixes the scale.
 * Rotation is removed by pinning one body k on the positive x-axis: y_k = 0 is not an unknown.
 * Identity (all q, no assumption):  sum_i q_i x F_i = 0  (cross product).  With y_k = 0 it reads
   x_k F_{k,y} = - sum_{i != k} q_i x F_i.  So if every equation except F_{k,y} vanishes and x_k > 0,
   F_{k,y} vanishes too.  We drop F_{k,y}: 2n-1 equations in 2n-1 unknowns (the reduced system G).
 * Zeros of G with x_k > 0  <->  central configurations (lambda = 1, c = 0) with body k on the positive x-axis.

Krawczyk.  X = x0 + [-h, h]^(2n-1), x0 dyadic, C a dyadic approximate inverse of DG(x0).
  K(X) = x0 - C G(x0) + (I - C DG(X)) (X - x0).   If K(X) is inside the interior of X, then X holds exactly
  one zero of G, and every matrix in DG(X) is nonsingular (Krawczyk 1969, Moore 1977, Rump 1983).
  DG(X) is an Arb enclosure of the derivative on all of X: the only analytic bounds used are those of Arb's
  rigorous +, -, *, / and rsqrt on balls; a ball for r^2 that touches 0 gives a non-finite result and the
  test fails (it can never pass by accident).  x_k > 0 is checked on X.

Also certified for each class (all from the tight enclosure Y = K(X) of the zero):
  * I = sum |q_i|^2 (equals U and fixes the class: invariant under rotation, reflection, relabelling);
  * Morse index h = number of positive eigenvalues of DG at the zero (Gershgorin after a congruence);
  * the symmetry group order s (number of g in O(2), with the induced relabelling, mapping the zero to itself),
    by exclusion with distances and by uniqueness in X for the symmetries found.
Usage: python cert_arb.py census.json cert_out.json [corrupt]
"""
import sys, json, itertools
import numpy as np
from flint import arb, ctx

ctx.prec = 200
E = 50            # centres on the grid 2^-50
import os
HEXP = int(os.environ.get("HEXP", "30"))   # box radius 2^-HEXP
CEXP = 40         # preconditioner entries on the grid 2^-40


def fail(msg):
    raise SystemExit("FAIL: " + msg)


def full_F_J(q, n):
    """q: list of n pairs (arb or float).  Returns F (2n list) and J (2n x 2n nested list)."""
    F = [None] * (2 * n)
    J = [[0] * (2 * n) for _ in range(2 * n)]
    for i in range(n):
        Fx = -q[i][0]; Fy = -q[i][1]
        dxx = dxy = dyy = 0
        for j in range(n):
            if j == i:
                continue
            dx = q[i][0] - q[j][0]; dy = q[i][1] - q[j][1]
            r2 = dx * dx + dy * dy
            if isinstance(r2, arb):
                ri = r2.rsqrt()
            else:
                ri = r2 ** -0.5
            r3 = ri * ri * ri; r5 = r3 * ri * ri
            Fx += dx * r3; Fy += dy * r3
            bxx = r3 - 3 * r5 * dx * dx; bxy = -3 * r5 * dx * dy; byy = r3 - 3 * r5 * dy * dy
            J[2 * i][2 * j] = -bxx; J[2 * i][2 * j + 1] = -bxy
            J[2 * i + 1][2 * j] = -bxy; J[2 * i + 1][2 * j + 1] = -byy
            dxx += bxx; dxy += bxy; dyy += byy
        J[2 * i][2 * i] = dxx - 1; J[2 * i][2 * i + 1] = dxy
        J[2 * i + 1][2 * i] = dxy; J[2 * i + 1][2 * i + 1] = dyy - 1
        F[2 * i] = Fx; F[2 * i + 1] = Fy
    return F, J


def reduce_idx(n, k):
    return [t for t in range(2 * n) if t != 2 * k + 1]


def polish(x, n):
    """Float: centre, pin the farthest body on the positive x-axis, Newton on the reduced system."""
    q = np.array(x, float).reshape(n, 2)
    q -= q.mean(0)
    k = int(np.argmax((q ** 2).sum(1)))
    a = np.arctan2(q[k, 1], q[k, 0]); c, s = np.cos(-a), np.sin(-a)
    q = q @ np.array([[c, s], [-s, c]])
    q[k, 1] = 0.0
    idx = reduce_idx(n, k)
    for _ in range(8):
        F, J = full_F_J([tuple(p) for p in q], n)
        F = np.array(F)[idx]; J = np.array(J)[np.ix_(idx, idx)]
        d = np.linalg.solve(J, -F)
        v = q.reshape(-1); v[idx] += d; q = v.reshape(n, 2)
    return q, k


def to_dyadic(v, e):
    return [int(round(float(t) * 2 ** e)) for t in v]


def certify(n, k, num, hexp=None):
    hexp = HEXP if hexp is None else hexp
    idx = reduce_idx(n, k); m = len(idx)
    two = arb(2)
    c = [arb(t) / two ** E for t in num]                       # exact dyadic centre (reduced coords)
    if any(t.rad() != 0 for t in c):
        fail("centre not exact")
    h = two ** -hexp

    def assemble(red):
        v = [arb(0)] * (2 * n)
        for a, t in zip(idx, red):
            v[a] = t
        return [(v[2 * i], v[2 * i + 1]) for i in range(n)]

    q0 = assemble(c)
    F0, _ = full_F_J(q0, n)
    G0 = [F0[a] for a in idx]
    X = [t + arb(0, h) for t in c]
    if not (X[idx.index(2 * k)] > 0):
        fail("x_k > 0 not certain on the box")
    _, JX = full_F_J(assemble(X), n)
    DG = [[JX[a][b] for b in idx] for a in idx]
    # preconditioner: float inverse of DG(x0), rounded to dyadics (exact numbers; any C is allowed)
    qf = [(float(a.mid()), float(b.mid())) for a, b in q0]
    _, Jf = full_F_J(qf, n)
    Cf = np.linalg.inv(np.array(Jf)[np.ix_(idx, idx)])
    C = [[arb(int(round(Cf[i][j] * 2 ** CEXP))) / two ** CEXP for j in range(m)] for i in range(m)]
    CG0 = [sum((C[i][j] * G0[j] for j in range(m)), arb(0)) for i in range(m)]
    K = []
    worst = 0.0
    for i in range(m):
        acc = c[i] - CG0[i]
        for j in range(m):
            cij = sum((C[i][l] * DG[l][j] for l in range(m)), arb(0))
            e = (1 if i == j else 0) - cij
            acc += e * arb(0, h)
        K.append(acc)
        if not (abs(acc - c[i]) < h):
            fail(f"Krawczyk inclusion fails in coordinate {i}")
        worst = max(worst, float((abs(acc - c[i])).upper()) / float(h))
    Y = [Ki.intersection(Xi) for Ki, Xi in zip(K, X)]
    return dict(X=X, Y=Y, assemble=assemble, worst_ratio=worst, h=h, idx=idx)


def invariants(res, n, k):
    qY = res['assemble'](res['Y'])
    I = sum((a * a + b * b for a, b in qY), arb(0))
    return qY, I


def morse_index(res, n, k):
    """Inertia of DG at the zero, from DG(Y): congruence by float eigenvectors V, then Gershgorin."""
    idx = res['idx']; m = len(idx)
    _, JY = full_F_J(res['assemble'](res['Y']), n)
    DG = [[JY[a][b] for b in idx] for a in idx]
    Mf = np.array([[float(t.mid()) for t in row] for row in DG]); Mf = (Mf + Mf.T) / 2
    w, V = np.linalg.eigh(Mf)
    Vd = [[arb(int(round(V[i][j] * 2 ** CEXP))) / arb(2) ** CEXP for j in range(m)] for i in range(m)]
    def mul_tAB(A, B):  # A^T B
        return [[sum((A[l][i] * B[l][j] for l in range(m)), arb(0)) for j in range(m)] for i in range(m)]
    G = mul_tAB(Vd, Vd)
    for i in range(m):   # V^T V positive definite by Gershgorin, so V is nonsingular
        R = sum((abs(G[i][j]) for j in range(m) if j != i), arb(0))
        if not (G[i][i] - R > 0):
            fail("eigenvector matrix not certified nonsingular")
    DV = [[sum((DG[i][l] * Vd[l][j] for l in range(m)), arb(0)) for j in range(m)] for i in range(m)]
    M = mul_tAB(Vd, DV)
    pos = neg = 0
    for i in range(m):
        R = sum((abs(M[i][j]) for j in range(m) if j != i), arb(0))
        if M[i][i] - R > 0:
            pos += 1
        elif M[i][i] + R < 0:
            neg += 1
        else:
            fail("Gershgorin disc touches 0")
    return pos, neg


def symmetry_order(res, n, k):
    """Exact order of the stabiliser in O(2) x S_n (mod rotation), or fail."""
    qY = res['assemble'](res['Y']); X = res['X']; Y = res['Y']; idx = res['idx']
    nrm = [a * a + b * b for a, b in qY]          # squared norms (no sqrt: a ball near 0 stays finite)
    dist = [[((qY[i][0] - qY[j][0]) ** 2 + (qY[i][1] - qY[j][1]) ** 2) if i != j else arb(0)
             for j in range(n)] for i in range(n)]
    perms = []
    def bt(sig):
        i = len(sig)
        if i == n:
            perms.append(tuple(sig)); return
        for j in range(n):
            if j in sig or not nrm[j].overlaps(nrm[i]):
                continue
            if all(dist[j][sig[t]].overlaps(dist[i][t]) for t in range(i)):
                bt(sig + [j])
    bt([])
    cert = 0; undecided = 0
    for sig in perms:
        for refl in (False, True):
            p = [(qY[sig[i]][0], -qY[sig[i]][1] if refl else qY[sig[i]][1]) for i in range(n)]
            px, py = p[k]
            if not (px * px + py * py > 0):
                fail('pinned body image not away from 0')
            rr = (px * px + py * py).rsqrt(); ux = px * rr; uy = py * rr
            pn = [(ux * a + uy * b, -uy * a + ux * b) for a, b in p]
            flat = [t for pair in pn for t in pair]
            red = [flat[a] for a in idx]
            if all(X[i].contains(red[i]) for i in range(len(idx))):
                cert += 1
            elif any(not Y[i].overlaps(red[i]) for i in range(len(idx))):
                pass
            else:
                undecided += 1
    if undecided:
        fail(f"symmetry undecided for {undecided} candidates")
    return cert, len(perms)


def main():
    src = json.load(open(sys.argv[1])); out = sys.argv[2]
    corrupt = len(sys.argv) > 3 and sys.argv[3] == 'corrupt'
    n = src['n']
    rows = []
    for ci, cl in enumerate(src['classes']):
        q, k = polish(cl['x'], n)
        idx = reduce_idx(n, k)
        num = to_dyadic(q.reshape(-1)[idx], E)
        if corrupt and ci == 0:
            num[0] += 2 ** (E - 12)          # move one coordinate by 2^-12 (about 2.4e-4)
        res = certify(n, k, num)
        big = None
        for hb in range(12, HEXP, 2):      # largest box (radius 2^-hb) on which uniqueness is also proved
            try:
                certify(n, k, num, hb); big = hb; break
            except SystemExit:
                pass
        qY, I = invariants(res, n, k)
        pos, neg = morse_index(res, n, k)
        s, npm = symmetry_order(res, n, k)
        rows.append(dict(cls=ci, pinned_body=k, unique_exp2=big if big is not None else HEXP, centre_num=num, I=I, P=I ** 1.5, morse_index=pos, s=s,
                         worst_ratio=res['worst_ratio'], qY=qY))
        print(f"class {ci+1:3d}: certified. P=U*sqrt(I) in {I**1.5}, Morse index {pos} (neg {neg}), |Sym|={s}, "
              f"Krawczyk ratio {res['worst_ratio']:.2e}, unique in radius 2^-{big if big is not None else HEXP}", flush=True)
    # distinctness: pairwise disjoint enclosures of I (fallback: sorted distance lists)
    N = len(rows)
    for a, b in itertools.combinations(range(N), 2):
        if rows[a]['I'].overlaps(rows[b]['I']):
            fail(f"classes {a+1} and {b+1}: I enclosures overlap")
    print(f"all {N} classes pairwise distinct (I enclosures disjoint)")
    fact = 1
    for t in range(2, n + 1):
        fact *= t
    from fractions import Fraction as Fr
    morse_sum = sum((Fr((-1) ** r['morse_index'] * 2, r['s']) for r in rows), Fr(0))
    nlab = sum(2 * fact // r['s'] for r in rows)
    target = Fr((-1) ** n, n * (n - 1))
    print(f"labelled solutions up to rotation (mirror images separate): {nlab}")
    print(f"Morse sum  sum (-1)^h 2/s = {morse_sum};  Euler characteristic target (-1)^n/(n(n-1)) = {target};  equal: {morse_sum == target}")
    hist = {}
    for r in rows:
        hist.setdefault(r['morse_index'], 0); hist[r['morse_index']] += 2 * fact // r['s']
    print("Morse counts by index (labelled, mod rotation):", dict(sorted(hist.items())))
    json.dump({'n': n, 'lambda': '1', 'masses': '1', 'centre_scale_exp2': E, 'box_radius_exp2': HEXP,
               'normalisation': 'lambda=1 (scale), centre of mass forced to 0 by the equations, body k on the positive x-axis (y_k=0 not an unknown), equation F_{k,y} dropped (implied when x_k>0)',
               'coordinate_order': 'x_0,y_0,...,x_{n-1},y_{n-1} with y_k removed',
               'classes': [{'pinned_body': r['pinned_body'], 'centre_num': [str(t) for t in r['centre_num']],
                            'I_enclosure': r['I'].str(radius=True), 'P_enclosure': r['P'].str(radius=True),
                            'morse_index': r['morse_index'], 'sym_order': r['s'], 'uniqueness_radius_exp2': r['unique_exp2']} for r in rows],
               'labelled_count': nlab, 'morse_sum': str(morse_sum)}, open(out, 'w'), indent=1)


if __name__ == '__main__':
    main()
