"""Interval certification (python-flint arb) of real critical points of the model f = F/lam + L, where F is the EXACT
Platonic leading form (sum of P_d over the unit vertex vectors; icosahedron coordinates involve sqrt5, carried as arb
balls), lam is the largest absolute coefficient of F (as in hmodel.leading), and L is the lower-degree part, taken
exactly from its double-precision coefficients. For each approximate real root a Krawczyk test on a small box proves a
unique, non-degenerate critical point there; boxes are checked pairwise disjoint. Output: number of certified roots and
their index split (Hessian sign pattern at the centre, checked by interval determinant signs).
Usage: certify.py <result.json from sym_scan.py | full model json with key "C"> """
import numpy as np, sys, json, itertools
from flint import arb, arb_mat, ctx
import htrack as ht, hmodel as hm, sym
ctx.prec = 200

def exact_leading(solid):
    s5 = arb(5).sqrt(); ph = (1 + s5) / 2
    if solid == "icosahedron":
        V = [p for s1 in (-1, 1) for s2 in (-1, 1) for p in ((0, s1, s2 * ph), (s1, s2 * ph, 0), (s2 * ph, 0, s1))]
        d = 6; P = {6: 231, 4: -315, 2: 105, 0: -5}; den = 16
    else:
        V = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
        d = 4; P = {4: 35, 2: -30, 0: 3}; den = 8
    V = [tuple(arb(c) for c in v) for v in V]
    C = {}
    def add(mon, c):
        C[mon] = C.get(mon, arb(0)) + c
    from math import comb, factorial
    for v in V:
        nv = (v[0] ** 2 + v[1] ** 2 + v[2] ** 2).sqrt(); u = [c / nv for c in v]
        for k, coef in P.items():         # coef * (x.u)^k * r^(d-k) / den
            # (x.u)^k = sum multinomial, r^(d-k) = (x^2+y^2+z^2)^((d-k)/2)
            h = (d - k) // 2
            for a in range(k + 1):
                for b in range(k + 1 - a):
                    c3 = k - a - b; m1 = factorial(k) // (factorial(a) * factorial(b) * factorial(c3))
                    t1 = arb(m1) * u[0] ** a * u[1] ** b * u[2] ** c3
                    for i in range(h + 1):
                        for j in range(h + 1 - i):
                            l = h - i - j; m2 = factorial(h) // (factorial(i) * factorial(j) * factorial(l))
                            add((a + 2 * i, b + 2 * j, c3 + 2 * l), t1 * m2 * coef / den)
    lam = max((abs(c) for c in C.values()), key=lambda z: float(z.mid()))
    return d, {m: c / lam for m, c in C.items()}

def poly_from(solid, Cfloat_total, Cfloat_lead):
    d, CF = exact_leading(solid)
    L = Cfloat_total - Cfloat_lead
    coeffs = dict(CF)
    for m in itertools.product(range(d + 1), repeat=3):
        if sum(m) <= d and L[m] != 0: coeffs[m] = coeffs.get(m, arb(0)) + arb(float(L[m]))
    return d, coeffs

def grad_hess(coeffs, X):
    """X: list of 3 arb. Returns gradient (3 arb) and Hessian (3x3 arb)."""
    g = [arb(0)] * 3; H = [[arb(0)] * 3 for _ in range(3)]
    def pw(x, n): return x ** n if n > 0 else arb(1)
    for (a, b, c), v in coeffs.items():
        e = (a, b, c)
        for i in range(3):
            if e[i] == 0: continue
            ei = list(e); ei[i] -= 1
            g[i] += v * e[i] * pw(X[0], ei[0]) * pw(X[1], ei[1]) * pw(X[2], ei[2])
            for j in range(3):
                if ei[j] == 0: continue
                eij = list(ei); eij[j] -= 1
                H[i][j] += v * e[i] * ei[j] * pw(X[0], eij[0]) * pw(X[1], eij[1]) * pw(X[2], eij[2])
    return g, H

def krawczyk(coeffs, x0, r):
    xm = [arb(float(c)) for c in x0]
    box = [arb(float(c), r) for c in x0]
    gm, Hm = grad_hess(coeffs, xm)
    Y = np.linalg.inv(np.array([[float(Hm[i][j].mid()) for j in range(3)] for i in range(3)]))
    Ya = [[arb(float(Y[i][j])) for j in range(3)] for i in range(3)]
    gB, HB = grad_hess(coeffs, box)
    K = []
    for i in range(3):
        k = xm[i] - sum((Ya[i][j] * gm[j] for j in range(3)), arb(0))
        for j in range(3):
            Mij = (arb(1) if i == j else arb(0)) - sum((Ya[i][l] * HB[l][j] for l in range(3)), arb(0))
            k += Mij * (box[j] - xm[j])
        K.append(k)
    inside = all(float(K[i].mid()) - float(K[i].rad()) > float(x0[i]) - r and float(K[i].mid()) + float(K[i].rad()) < float(x0[i]) + r for i in range(3))
    # index: signs of leading principal minors of the Hessian over the box
    Hd = arb_mat([[HB[i][j] for j in range(3)] for i in range(3)])
    det = Hd.det(); m1 = HB[0][0]; m2 = HB[0][0] * HB[1][1] - HB[0][1] * HB[1][0]
    signs = [(1 if z > 0 else -1 if z < 0 else 0) for z in (m1, m2, det)]
    return inside, signs

def certify(solid, Ctot, Clead, Xr):
    d, coeffs = poly_from(solid, Ctot, Clead)
    out = []; dmin = np.inf
    D = np.linalg.norm(Xr[:, None] - Xr[None], axis=-1) + 1e300 * np.eye(len(Xr)); sep = D.min(1)
    nidx = {1: 0, 2: 0}; ok = 0
    for x0, s in zip(Xr, sep):
        r = min(1e-7 * np.abs(x0).max() + 1e-300, s / 4)
        inside, signs = krawczyk(coeffs, x0, r)
        if inside and signs[2] != 0:
            # trace of the Hessian is 0 (f harmonic), so det > 0 means index 2 and det < 0 means index 1
            ok += 1; neg = 2 if signs[2] > 0 else 1; nidx[neg] += 1
        else: print("    not certified:", x0, inside, signs)
    return ok, nidx

if __name__ == "__main__":
    solid, d, F, th = hm.load_model(sys.argv[1]); fam = sys.argv[1]
    Ctot = hm.model(F, d, th); Clead = hm.to_array([F], d)
    P = ht.Poly(Ctot); X = ht.roots(P, 11); Xr, idx, pok = ht.real_roots(P, X)
    print(f"{fam}: double-precision solve: {len(Xr)} real of {len(X)}, index counts {np.bincount(idx, minlength=4).tolist()}, pairing ok {pok}")
    print(f"  smallest distance between real roots {np.min(np.linalg.norm(Xr[:,None]-Xr[None],axis=-1)+1e9*np.eye(len(Xr))):.2e}; smallest |Im| of non-real roots "
          f"{(np.abs(X.imag).max(1)[np.abs(X.imag).max(1) > 1e-9].min() if len(Xr) < len(X) else float('nan')):.2e}")
    ok, nidx = certify(solid, Ctot, Clead, Xr)
    print(f"  CERTIFIED (arb Krawczyk, exact leading form): {ok} distinct non-degenerate real critical points; index counts {nidx}")
