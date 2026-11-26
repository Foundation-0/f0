"""All complex critical points of a polynomial f of degree d in three variables, by total-degree homotopy
continuation (gamma trick), vectorised over the (d-1)^3 paths. f is a dense coefficient array C[a,b,c] for x^a y^b z^c.
The result is checked: every endpoint must be a simple root (Newton converges, Jacobian invertible) and the
endpoints must be pairwise distinct; then they are all (d-1)^3 roots (no roots at infinity for a generic leading form).
Real roots are found by conjugate pairing: a root is real when the root nearest to its conjugate is itself."""
import numpy as np

def deriv(C, v):
    n = C.shape[0]; D = np.zeros_like(C); a = np.arange(1, n)
    sl = [slice(None)] * 3; sl[v] = slice(1, None); sh = [1, 1, 1]; sh[v] = n - 1
    src = C[tuple(sl)] * a.reshape(sh)
    dl = [slice(None)] * 3; dl[v] = slice(0, n - 1); D[tuple(dl)] = src
    return D

class Poly:
    def __init__(self, C):
        C = np.asarray(C); self.C = C; self.n = C.shape[0]
        self.G = np.stack([deriv(C, v) for v in range(3)])
        self.H = np.stack([np.stack([deriv(self.G[i], j) for j in range(3)]) for i in range(3)])
    def _pw(self, X):
        k = np.arange(self.n); return [X[:, v][:, None] ** k[None] for v in range(3)]
    def val(self, X):
        px, py, pz = self._pw(X); return np.einsum('abc,ka,kb,kc->k', self.C, px, py, pz)
    def grad(self, X):
        px, py, pz = self._pw(X); return np.einsum('iabc,ka,kb,kc->ki', self.G, px, py, pz)
    def gh(self, X):
        px, py, pz = self._pw(X)
        return (np.einsum('iabc,ka,kb,kc->ki', self.G, px, py, pz), np.einsum('ijabc,ka,kb,kc->kij', self.H, px, py, pz))

def solve(P, rng=None, gamma=None, maxsteps=4000, tol=1e-10, start=None, h0=0.02):
    """start=(P0, X0): parameter homotopy from the known simple roots X0 of grad P0 (same degree) instead of the
    total-degree start system."""
    rng = np.random.default_rng(0) if rng is None else rng
    e = P.n - 2; K = e ** 3
    if gamma is None: th = rng.uniform(0, 2 * np.pi); gamma = np.exp(1j * th)
    if start is None:
        w = np.exp(2j * np.pi * np.arange(e) / e)
        X = np.array(np.meshgrid(w, w, w, indexing='ij')).reshape(3, -1).T.astype(complex)
    else:
        P0, X = start[0], start[1].astype(complex).copy(); K = len(X)
    t = np.zeros(K); h = np.full(K, h0); done = np.zeros(K, bool)
    def HJ(Xa, ta):
        g, Hs = P.gh(Xa)
        if start is None:
            S = Xa ** e - 1; dSm = (e * Xa ** (e - 1))[:, :, None] * np.eye(3)[None]
        else:
            S, dSm = P0.gh(Xa)
        Hv = (1 - ta)[:, None] * gamma * S + ta[:, None] * g
        J = ta[:, None, None] * Hs + (1 - ta)[:, None, None] * gamma * dSm
        Ht = g - gamma * S
        return Hv, J, Ht
    def tangent(Xa, ta):
        Hv, J, Ht = HJ(Xa, ta); return -np.linalg.solve(J, Ht[..., None])[..., 0]
    for it in range(maxsteps):
        act = ~done
        if not act.any(): break
        Xa, ta, ha = X[act], t[act], np.minimum(h[act], 1 - t[act])
        try:
            k1 = tangent(Xa, ta); k2 = tangent(Xa + 0.5 * ha[:, None] * k1, ta + 0.5 * ha)
            k3 = tangent(Xa + 0.5 * ha[:, None] * k2, ta + 0.5 * ha); k4 = tangent(Xa + ha[:, None] * k3, ta + ha)
        except np.linalg.LinAlgError:
            h[act] *= 0.5; continue
        Xn = Xa + ha[:, None] * (k1 + 2 * k2 + 2 * k3 + k4) / 6; tn = ta + ha
        ok = np.ones(len(Xa), bool); sc = 1 + np.abs(Xn).max(1)
        for c in range(3):
            Hv, J, _ = HJ(Xn, tn)
            try: dx = np.linalg.solve(J, Hv[..., None])[..., 0]
            except np.linalg.LinAlgError: ok[:] = False; break
            Xn = Xn - dx; nd = np.abs(dx).max(1)
            if c == 0: ok &= nd < 1e-3 * sc
        ok &= (nd < 1e-9 * sc) & np.isfinite(Xn).all(1)
        idx = np.where(act)[0]
        acc = idx[ok]; rej = idx[~ok]
        X[acc] = Xn[ok]; t[acc] = tn[ok]; h[acc] = np.minimum(h[acc] * 1.5, 0.1)
        h[rej] *= 0.5
        done |= t >= 1 - 1e-15
        if (h[~done] < 1e-12).any(): break
    # polish on the target
    for c in range(6):
        g, Hs = P.gh(X)
        try: X = X - np.linalg.solve(Hs, g[..., None])[..., 0]
        except np.linalg.LinAlgError: break
    return X, done

def check(P, X, done):
    """returns (ok, info): ok if all paths finished, endpoints distinct and simple."""
    if not done.all() or not np.isfinite(X).all(): return False, "unfinished"
    g, Hs = P.gh(X); sc = 1 + np.abs(X).max(1)
    dx = np.linalg.solve(Hs, g[..., None])[..., 0]; nd = np.abs(dx).max(1) / sc
    if nd.max() > 1e-8: return False, f"newton step {nd.max():.1e}"
    D = np.abs(X[:, None] - X[None]).max(-1) + np.eye(len(X)) * 1e300
    # distinct relative to the local Newton step size and to the local scale
    if (D.min(1) < 1e3 * nd * sc + 1e-12 * sc).any(): return False, "duplicate endpoints"
    return True, float(D.min())

def real_roots(P, X):
    """indices of real roots via conjugate pairing, then real Newton polish; returns (Xr real array, index counts)."""
    K = len(X); Xc = X.conj(); D = np.abs(Xc[:, None] - X[None]).max(-1)
    nn = D.argmin(1); real = nn == np.arange(K)
    # consistency: non-real roots must pair up mutually
    pair_ok = all(nn[nn[i]] == i for i in range(K))
    Xr = X[real].real.copy()
    for c in range(4):
        g, Hs = P.gh(Xr.astype(complex)); Xr = Xr - np.linalg.solve(Hs.real, g.real[..., None])[..., 0]
    g, Hs = P.gh(Xr.astype(complex)); ev = np.linalg.eigvalsh(Hs.real)
    idx = (ev < 0).sum(1)
    return Xr, idx, pair_ok

def roots(P, seed=0, tries=4):
    rng = np.random.default_rng(seed)
    for k in range(tries):
        X, done = solve(P, rng)
        ok, info = check(P, X, done)
        if ok: return X
    return None

def count(P, seed=0):
    X = roots(P, seed)
    if X is None: return None
    Xr, idx, pok = real_roots(P, X)
    if not pok: return None
    return dict(real=len(Xr), idx=np.bincount(idx, minlength=4).tolist(), X=X, Xr=Xr)
