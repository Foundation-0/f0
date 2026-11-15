"""Local models F(Y) = P(Y) + sum_j q_j/|Y - b_j| with P a harmonic polynomial (the background jet in scaled
variables) and a small cluster of charges b_j.  Numerical: seeds + damped Newton + dedup.  The origin may be a
degenerate critical point (a flat point that the next nesting level reuses); points with |Y| < r0 are reported
separately and not counted."""
import numpy as np
from scipy.spatial import cKDTree
from harm import monos, evalmon, deriv_mat
import finder


class Local:
    def __init__(self, Pc, d, b, q):
        self.Pc = np.asarray(Pc, float); self.d = d
        self.b = np.asarray(b, float).reshape(-1, 3); self.q = np.asarray(q, float)
        D = [deriv_mat(d, a) for a in range(3)]
        self.g = [Dm @ self.Pc for Dm in D]
        self.h = [[D[a] @ self.g[b_] for b_ in range(3)] for a in range(3)]

    def gh(self, X):
        M = evalmon(self.d, X)
        g = np.stack([M @ gg for gg in self.g], 1)
        H = np.stack([np.stack([M @ self.h[a][b_] for b_ in range(3)], 1) for a in range(3)], 1)
        if len(self.q):
            g2, H2 = finder.grad_hess(X, self.b, self.q)
            g = g + g2; H = H + H2
        return g, H

    def newton(self, X, iters=100):
        X = X.copy()
        for _ in range(iters):
            g, H = self.gh(X)
            det = np.linalg.det(H)
            good = np.isfinite(det) & (np.abs(det) > 0)
            st = np.zeros_like(X)
            st[good] = np.linalg.solve(H[good], g[good][..., None])[..., 0]
            if len(self.q):
                rmin = np.sqrt(((X[:, None] - self.b[None]) ** 2).sum(2)).min(1)
            else:
                rmin = np.full(len(X), np.inf)
            lim = np.minimum(0.5 * rmin, 0.3 * np.maximum(np.linalg.norm(X, axis=1), 1e-3))
            n = np.linalg.norm(st, axis=1)
            f = np.minimum(1, lim / np.maximum(n, 1e-300))
            X = X - st * f[:, None]
        return X

    def scale(self, X):
        """local length scale for tolerances: min(distance to nearest charge, |X|)"""
        s = np.linalg.norm(X, axis=1)
        if len(self.q):
            s = np.minimum(s, np.sqrt(((X[:, None] - self.b[None]) ** 2).sum(2)).min(1))
        return s

    def find(self, rng, Rmax=4.0, ngrid=6000, ndir=60, r0=1e-3, rounds=2):
        S = [rng.uniform(-Rmax, Rmax, (ngrid, 3))]
        S.append(rng.standard_normal((ngrid, 3)) * Rmax / 3)
        U = finder.fib_sphere(ndir)
        if len(self.q):
            dn = cKDTree(self.b).query(self.b, k=2)[0][:, 1] if len(self.q) > 1 else np.array([np.linalg.norm(self.b[0])])
            for i in range(len(self.q)):
                for s in np.geomspace(0.02, 1.5, 8):
                    S.append(self.b[i] + s * dn[i] * U)
        for s in np.geomspace(0.05, Rmax, 12):
            S.append(s * U)
        X = np.vstack(S)
        found = np.zeros((0, 3))
        for rnd in range(rounds):
            if rnd > 0 and len(found):
                sc = self.scale(found)
                X = np.vstack([np.repeat(found, 10, 0) + e * rng.standard_normal((10 * len(found), 3)) * np.repeat(sc, 10)[:, None] for e in (0.3, 0.05)])
            with np.errstate(all='ignore'):
                Y = self.newton(X)
                g, H = self.gh(Y)
                det = np.linalg.det(H)
                ok = np.isfinite(Y).all(1) & np.isfinite(det) & (np.abs(det) > 0)
                st = np.full(len(Y), np.inf)
                st[ok] = np.linalg.norm(np.linalg.solve(H[ok], g[ok][..., None])[..., 0], axis=1)
                sc = self.scale(Y)
                ok &= (st < 1e-10 * sc) & (sc > 0)
            found = finder.dedup(np.vstack([found, Y[ok]]), np.vstack([self.b, [[0, 0, 0]]]) if len(self.q) else np.zeros((1, 3)))
        g, H = self.gh(found)
        ev = np.linalg.eigvalsh(H)
        rn = np.linalg.norm(found, axis=1)
        keep = rn > r0
        return found[keep], (ev[keep] < 0).sum(1), ev[keep], found[~keep]


def K4():
    """x^4+y^4+z^4 - 3/5 r^4 (positive toward the axes: the octahedron's quartic)."""
    d = 4; L, ix = monos(d); c = np.zeros(len(L))
    for m in [(4, 0, 0), (0, 4, 0), (0, 0, 4)]:
        c[ix[m]] += 1
    for m, co in {(4, 0, 0): 1, (0, 4, 0): 1, (0, 0, 4): 1, (2, 2, 0): 2, (2, 0, 2): 2, (0, 2, 2): 2}.items():
        c[ix[m]] -= 0.6 * co
    return c, d


def poly_from_charges_jet(a, q, d, centre=(0, 0, 0)):
    """Taylor polynomial (degree <= d, harmonic) of sum q/|x-a| at centre, via least squares on samples.
    Returned in monomial coefficients of x - centre. Numerical."""
    a = np.asarray(a, float) - np.asarray(centre, float); q = np.asarray(q, float)
    L, ix = monos(d)
    rr = 0.02 * np.linalg.norm(a, axis=1).min()
    rng = np.random.default_rng(0)
    X = rng.standard_normal((4 * len(L), 3)); X *= rr / np.linalg.norm(X, axis=1)[:, None] * rng.random((len(X), 1)) ** (1 / 3)
    V = (q[None] / np.sqrt(((X[:, None] - a[None]) ** 2).sum(2))).sum(1)
    M = evalmon(d, X)
    c, *_ = np.linalg.lstsq(M, V, rcond=None)
    return c
