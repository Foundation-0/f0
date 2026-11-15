"""One scale of a separated-scale unfolding. For harmonic forms A (degree m+1) and B (degree m), the non-zero critical
points of A + B number 3m^2-3m+1 (= m^3 - (m-1)^3; the origin absorbs (m-1)^3). They are found by solving A + B + tiny
lower terms with the homotopy solver, keeping the roots that Newton on the exact A + B carries to a non-zero simple
root, and checking that exactly 3m^2-3m+1 distinct ones are found."""
import numpy as np, htrack as ht, hmodel as hm

_low = {}
def lowterms(m, d, seed=7):
    key = (m, d)
    if key not in _low:
        rng = np.random.default_rng(seed)
        _low[key] = [hm.harm(j, rng.normal(size=2 * j + 1) / np.sqrt(2 * j + 1)) for j in range(1, m)]
    return _low[key]

def outer_roots(Aterm, Bterm, m, delta=1e-10, seed=0):
    d = m + 1
    C0 = hm.to_array([Aterm, Bterm], d)
    lows = [(mm, delta * c) for mm, c in lowterms(m, d)]
    P = ht.Poly(hm.to_array([Aterm, Bterm] + lows, d))
    X = ht.roots(P, seed)
    if X is None: return None
    P0 = ht.Poly(C0)
    nout = 3 * m * m - 3 * m + 1; r = np.abs(X).max(1); o = np.argsort(-r)
    if m > 1 and r[o[nout - 1]] < 5 * r[o[nout]]: return None
    Y = X[o[:nout]].copy()
    for it in range(8):
        g, H = P0.gh(Y); Y = Y - np.linalg.solve(H, g[..., None])[..., 0]
    g, H = P0.gh(Y); ok = (np.abs(g).max(1) < 1e-9 * (1 + np.abs(Y).max(1) ** m)) & (np.abs(Y).max(1) > 1e-3)
    Y = Y[ok]
    D = np.abs(Y[:, None] - Y[None]).max(-1) + 1e300 * np.eye(len(Y))
    if len(Y) != 3 * m * m - 3 * m + 1 or (len(Y) > 1 and D.min() < 1e-7): return None
    return Y, P0

def count(Aterm, Bterm, m, seed=0):
    out = outer_roots(Aterm, Bterm, m, seed=seed)
    if out is None: return None
    Y, P0 = out
    Xr, idx, pok = ht.real_roots(P0, Y)
    if not pok: return None
    im = np.abs(Y.imag).max(1) / np.abs(Y).max(1); cx = np.sort(im[im > 1e-9])
    return dict(real=len(Xr), idx=np.bincount(idx, minlength=4).tolist(), gap=float(cx[:2].sum()) if len(cx) else 0.0, Y=Y)
