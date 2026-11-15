"""All solutions of three polynomial equations of degree e in three unknowns (e^3 of them), by the null space of the
Macaulay matrix in degree 3e-2 and the eigenvectors of a multiplication matrix. Polynomials are coefficient vectors
over the monomials of degree <= e. Used for grad f = 0 with f harmonic of degree e+1."""
import numpy as np, itertools
class System:
    def __init__(self, e):
        self.e = e; self.D = 3 * e - 2
        self.mons = [m for d in range(self.D + 1) for m in itertools.product(range(d + 1), repeat=3) if sum(m) == d]
        self.idx = {m: i for i, m in enumerate(self.mons)}
        self.mons_e = [m for m in self.mons if sum(m) <= e]
        self.mult = [m for m in self.mons if sum(m) <= self.D - e]
        self.add = np.array([[self.idx[tuple(np.add(a, b))] for b in self.mons_e] for a in self.mult])
        self.basis = [m for m in itertools.product(range(e), repeat=3)]
        self.rows_b = np.array([self.idx[b] for b in self.basis])
        self.rows_xb = [np.array([self.idx[tuple(np.add(b, np.eye(3, dtype=int)[a]))] for b in self.basis]) for a in range(3)]
        self.E = np.array(self.mons_e)
        self.L = np.array([[1.0, 0.37, -0.52], [0.29, 1.0, 0.61], [-0.43, 0.23, 1.0]])
    def evalf(self, co, X):
        """co [3, len(mons_e)], X [K,3] complex -> values [K,3]"""
        P = np.prod(X[:, None, :] ** self.E[None, :, :], axis=2)
        return P @ co.T
    def jac(self, co, X):
        J = np.zeros((X.shape[0], 3, 3), complex)
        for v in range(3):
            Ev = self.E.copy(); c = Ev[:, v].astype(float); Ev[:, v] = np.maximum(Ev[:, v] - 1, 0)
            P = np.prod(X[:, None, :] ** Ev[None, :, :], axis=2) * c[None, :]
            J[:, :, v] = P @ co.T
        return J
    def substitute(self, co):
        """coefficients of f(L y) from those of f(x), by sampling and least squares (exact up to rounding)."""
        rng = np.random.default_rng(1); Y = rng.normal(size=(4 * len(self.mons_e), 3))
        V = np.prod(Y[:, None, :] ** self.E[None, :, :], axis=2)
        return np.linalg.lstsq(V, self.evalf(co, (Y @ self.L.T).astype(complex)).real, rcond=None)[0].T
    def solve(self, co, rng):
        com = self.substitute(co)
        M = np.zeros((3 * len(self.mult), len(self.mons)))
        for a in range(3):
            for m in range(len(self.mult)): M[a * len(self.mult) + m, self.add[m]] = com[a]
        u, sv, vt = np.linalg.svd(M)
        nb = self.e ** 3; N = vt[len(self.mons) - nb:].T
        NB = N[self.rows_b]; r = rng.normal(size=3)
        NX = sum(r[a] * N[self.rows_xb[a]] for a in range(3))
        if np.linalg.cond(NB) > 1e13: return None
        w, V = np.linalg.eig(NX @ np.linalg.inv(NB)); V = V / V[0:1, :]
        Y = np.stack([V[self.basis.index((1, 0, 0))], V[self.basis.index((0, 1, 0))], V[self.basis.index((0, 0, 1))]], axis=1)
        X = Y @ self.L.T
        for it in range(12):
            F = self.evalf(co, X); J = self.jac(co, X)
            try: X = X - np.linalg.solve(J, F[..., None])[..., 0]
            except np.linalg.LinAlgError: break
        return X
    def count_real(self, co, X, tol=1e-8):
        if X is None or not np.isfinite(X).all(): return -1, -1
        F = np.abs(self.evalf(co, X)).max(1); scale = np.abs(X).max() + 1e-300
        if F.max() > 1e-7 * (np.abs(co).max() * (1 + scale) ** self.e): return -1, -1
        d = np.abs(X[:, None] - X[None]).max(-1) + np.eye(len(X)) * 1e300
        if d.min() < 1e-7 * scale: return -1, -1
        real = np.abs(X.imag).max(1) < tol * scale
        J = self.jac(co, X[real]).real
        return int(real.sum()), int((np.linalg.det(J) > 0).sum())
def harmonic_basis(j):
    """orthonormal basis (rows, over monomials of exact degree j) of the harmonic polynomials of degree j."""
    mons = [m for m in itertools.product(range(j + 1), repeat=3) if sum(m) == j]
    if j < 2: return mons, np.eye(len(mons))
    low = [m for m in itertools.product(range(j - 1), repeat=3) if sum(m) == j - 2]; li = {m: i for i, m in enumerate(low)}
    Lap = np.zeros((len(low), len(mons)))
    for c, m in enumerate(mons):
        for v in range(3):
            if m[v] >= 2:
                t = list(m); t[v] -= 2; Lap[li[tuple(t)], c] += m[v] * (m[v] - 1)
    u, s, vt = np.linalg.svd(Lap); return mons, vt[len(low):]
def grad_coeffs(S, terms):
    """terms: list of (mons, coefficient vector) of homogeneous polynomials; returns co [3, len(S.mons_e)] of the gradient."""
    co = np.zeros((3, len(S.mons_e))); ie = {m: i for i, m in enumerate(S.mons_e)}
    for mons, c in terms:
        for m, cv in zip(mons, c):
            if cv == 0: continue
            for v in range(3):
                if m[v] >= 1:
                    t = list(m); t[v] -= 1; co[v, ie[tuple(t)]] += cv * m[v]
    return co
def solid_term(U, k):
    """coefficients over degree-k monomials of sum_i P_k(x.u_i/|x|) |x|^k for unit vectors u_i."""
    from numpy.polynomial import legendre as Lg
    mons = [m for m in itertools.product(range(k + 1), repeat=3) if sum(m) == k]
    rng = np.random.default_rng(2); X = rng.normal(size=(6 * len(mons), 3)); r = np.linalg.norm(X, axis=1)
    val = sum(Lg.legval(X @ u / r, [0] * k + [1]) for u in U) * r ** k
    V = np.prod(X[:, None, :] ** np.array(mons)[None], axis=2)
    return mons, np.linalg.lstsq(V, val, rcond=None)[0]
if __name__ == "__main__":
    rng = np.random.default_rng(0)
    for e in (2, 3, 5):
        S = System(e); co = np.zeros((3, len(S.mons_e))); ie = {m: i for i, m in enumerate(S.mons_e)}
        for v in range(3):
            m = [0, 0, 0]; m[v] = e; co[v, ie[tuple(m)]] = 1.0; m[v] = 1; co[v, ie[tuple(m)]] = -(v + 2.0)   # x^e = (v+2) x
        X = S.solve(co, rng); print("self-test degree", e, ": roots", None if X is None else len(X), " real, positive-determinant:", S.count_real(co, X), " expected real:", (3 if e % 2 else 2) ** 3)
