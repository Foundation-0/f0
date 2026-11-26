"""Vectorised numerical algebraic geometry for planar Laman frameworks (search code, not proof code).

Isotropic coordinates u = x + i y, w = x - i y.  A pinned triangle (A, B, C) fixes the frame:
A at the origin, B at (1, 0) (scale fixed by lambda_AB = 1), C at (xC, yC).
Parameters P (complex vector, length 2 + m):  P[0] = uC, P[1] = wC, P[2:] = squared lengths of the m
remaining edges.  A real point has wC = conj(uC) and real P[2:].
Unknowns z (length 2 f): u of the f free vertices, then w.
Equations: (u_a - u_b)(w_a - w_b) - s_e = 0 for the m = 2 f remaining edges.
"""
import itertools
import numpy as np


def decode(n, code):
    # Bit order: most significant bit first over the pairs (1,2),(1,3),... as in checks/l2288/lam.py.
    # checks/laman/laman_count.py reads the same integer least significant bit first (the lnumber order).
    # The two give isomorphic graphs with different labels.
    pairs = list(itertools.combinations(range(1, n + 1), 2)); m = len(pairs)
    return [pairs[k] for k in range(m) if (code >> (m - 1 - k)) & 1]


class Laman:
    def __init__(self, n, edges, tri):
        self.n, self.E = n, [tuple(e) for e in edges]
        A, B, C = tri
        self.tri = tri
        es = {frozenset(e): i for i, e in enumerate(self.E)}
        self.tri_edges = [es[frozenset((A, B))], es[frozenset((A, C))], es[frozenset((B, C))]]
        self.free = [v for v in range(1, n + 1) if v not in tri]
        self.f = len(self.free)
        self.rem = [i for i in range(len(self.E)) if i not in self.tri_edges]
        self.m = len(self.rem)
        assert self.m == 2 * self.f
        # column of each vertex in the full (B, n+?) arrays: free vertices 0..f-1, then A, B, C
        col = {v: i for i, v in enumerate(self.free)}
        col[A], col[B], col[C] = self.f, self.f + 1, self.f + 2
        self.col = col
        self.ea = np.array([col[self.E[i][0]] for i in self.rem])
        self.eb = np.array([col[self.E[i][1]] for i in self.rem])
        self.nP = 2 + self.m

    # ---------- parameter conversions ----------
    def real_params_from_lengths(self, lam):
        """lam: real lengths for all edges (any scale).  Returns (P, scale)."""
        lam = np.asarray(lam, dtype=float)
        sc = lam[self.tri_edges[0]]
        L = lam / sc
        sab, sac, sbc = 1.0, L[self.tri_edges[1]] ** 2, L[self.tri_edges[2]] ** 2
        xc = (sab + sac - sbc) / 2.0
        yc = np.sqrt(sac - xc * xc)
        P = np.zeros(self.nP, dtype=complex)
        P[0], P[1] = xc + 1j * yc, xc - 1j * yc
        P[2:] = L[self.rem] ** 2
        return P, sc

    def lengths_from_real_params(self, P):
        xc, yc = P[0].real, (P[0].imag)
        lam = np.zeros(len(self.E))
        lam[self.tri_edges[0]] = 1.0
        lam[self.tri_edges[1]] = np.hypot(xc, yc)
        lam[self.tri_edges[2]] = np.hypot(xc - 1, yc)
        lam[self.rem] = np.sqrt(P[2:].real)
        return lam

    # ---------- evaluation ----------
    def full(self, Z, P):
        Bn = Z.shape[0]; f = self.f
        U = np.empty((Bn, f + 3), dtype=complex); W = np.empty((Bn, f + 3), dtype=complex)
        U[:, :f] = Z[:, :f]; W[:, :f] = Z[:, f:]
        U[:, f] = 0; W[:, f] = 0
        U[:, f + 1] = 1; W[:, f + 1] = 1
        U[:, f + 2] = P[..., 0] if np.ndim(P) == 2 else P[0]
        W[:, f + 2] = P[..., 1] if np.ndim(P) == 2 else P[1]
        return U, W

    def F(self, Z, P):
        U, W = self.full(Z, P)
        du = U[:, self.ea] - U[:, self.eb]; dw = W[:, self.ea] - W[:, self.eb]
        s = P[..., 2:]
        return du * dw - s

    def FJ(self, Z, P):
        U, W = self.full(Z, P)
        du = U[:, self.ea] - U[:, self.eb]; dw = W[:, self.ea] - W[:, self.eb]
        Fv = du * dw - P[..., 2:]
        Bn = Z.shape[0]; f = self.f; m = self.m
        J = np.zeros((Bn, m, 2 * f + 6), dtype=complex)
        r = np.arange(m)
        J[:, r, self.ea] += dw; J[:, r, f + 3 + self.ea] += du
        J[:, r, self.eb] -= dw; J[:, r, f + 3 + self.eb] -= du
        # columns: u-free 0..f-1, u-pins f..f+2, w-free f+3..2f+2, w-pins 2f+3..2f+5
        Jz = np.concatenate([J[:, :, :f], J[:, :, f + 3:2 * f + 3]], axis=2)
        JuC = J[:, :, f + 2]; JwC = J[:, :, 2 * f + 5]
        return Fv, Jz, JuC, JwC

    def dFdP(self, Z, P):
        """Full parameter Jacobian (B, m, nP)."""
        Fv, Jz, JuC, JwC = self.FJ(Z, P)
        D = np.zeros((Z.shape[0], self.m, self.nP), dtype=complex)
        D[:, :, 0] = JuC; D[:, :, 1] = JwC
        D[:, np.arange(self.m), 2 + np.arange(self.m)] = -1.0
        return Jz, D

    def Ht(self, Z, P, dP):
        """dF/dt along direction dP (dP shape (nP,) or (B, nP))."""
        Fv, Jz, JuC, JwC = self.FJ(Z, P)
        if np.ndim(dP) == 1:
            dP = np.broadcast_to(dP, (Z.shape[0], self.nP))
        return Fv, Jz, JuC * dP[:, :1] + JwC * dP[:, 1:2] - dP[:, 2:]

    # ---------- Newton ----------
    def newton(self, Z, P, steps=6, tol=1e-13):
        Z = Z.copy()
        if len(Z) == 0:
            return Z, np.zeros(0)
        for _ in range(steps):
            Fv, Jz, _, _ = self.FJ(Z, P)
            err = np.abs(Fv).max(axis=1)
            if err.max() < tol:
                break
            try:
                Z = Z - np.linalg.solve(Jz, Fv[..., None])[..., 0]
            except np.linalg.LinAlgError:
                bad = np.abs(np.linalg.det(Jz)) < 1e-300
                Jz[bad] = np.eye(self.m)
                Z = Z - np.linalg.solve(Jz, Fv[..., None])[..., 0]
        Fv = self.F(Z, P)
        return Z, np.abs(Fv).max(axis=1)

    # ---------- adaptive vectorised tracker along P(t) = P0 + t (P1 - P0) + 4 t (1 - t) G ----------
    def track(self, Z0, P0, P1, G=None, h0=0.05, hmin=1e-7, hmax=0.2, max_iter=4000, tol_rel=1e-3):
        P0 = np.asarray(P0, complex); P1 = np.asarray(P1, complex)
        G = np.zeros_like(P0) if G is None else np.asarray(G, complex)
        Pt = lambda t: P0[None, :] + t[:, None] * (P1 - P0)[None, :] + (4 * t * (1 - t))[:, None] * G[None, :]
        dPt = lambda t: (P1 - P0)[None, :] + (4 - 8 * t)[:, None] * G[None, :]
        Bn = Z0.shape[0]
        Z = Z0.copy(); t = np.zeros(Bn); h = np.full(Bn, h0); ok = np.ones(Bn, bool)
        succ = np.zeros(Bn, int)

        def vel(Zc, tc):
            Fv, Jz, Htv = self.Ht(Zc, Pt(tc), dPt(tc))
            return -np.linalg.solve(Jz, Htv[..., None])[..., 0]

        it = 0
        while it < max_iter:
            act = ok & (t < 1.0)
            if not act.any():
                break
            it += 1
            ia = np.where(act)[0]
            Za, ta = Z[ia], t[ia]
            ha = np.minimum(h[ia], 1.0 - ta)
            try:
                k1 = vel(Za, ta)
                k2 = vel(Za + 0.5 * ha[:, None] * k1, ta + 0.5 * ha)
                k3 = vel(Za + 0.5 * ha[:, None] * k2, ta + 0.5 * ha)
                k4 = vel(Za + ha[:, None] * k3, ta + ha)
            except np.linalg.LinAlgError:
                h[ia] *= 0.5; ok[ia[h[ia] < hmin]] = False
                continue
            Zp = Za + (ha / 6.0)[:, None] * (k1 + 2 * k2 + 2 * k3 + k4)
            tn = ta + ha
            Pn = Pt(tn)
            scale = 1.0 + np.abs(Zp).max(axis=1)
            good = np.ones(len(ia), bool)
            prev = None
            for kk in range(3):
                Fv, Jz, _, _ = self.FJ(Zp, Pn)
                try:
                    d = np.linalg.solve(Jz, Fv[..., None])[..., 0]
                except np.linalg.LinAlgError:
                    good[:] = False; break
                nd = np.abs(d).max(axis=1)
                if kk == 0:
                    good &= nd < tol_rel * scale
                else:
                    good &= (nd < 0.25 * prev) | (nd < 1e-7 * scale)
                prev = nd
                Zp = Zp - d
            good &= np.isfinite(Zp).all(axis=1)
            gi = ia[good]; bi = ia[~good]
            Z[gi] = Zp[good]; t[gi] = tn[good]
            succ[gi] += 1
            grow = gi[succ[gi] >= 3]
            h[grow] = np.minimum(h[grow] * 2.0, hmax); succ[grow] = 0
            h[bi] *= 0.5; succ[bi] = 0
            ok[bi[h[bi] < hmin]] = False
            # tracked to infinity guard
            ok[gi[np.abs(Z[gi]).max(axis=1) > 1e8]] = False
        ok &= t >= 1.0
        Z, err = self.newton(Z, P1, steps=4)
        return Z, ok & (err < 1e-9), it

    # ---------- utilities ----------
    def conj_partner(self, Z):
        f = self.f
        return np.concatenate([np.conj(Z[:, f:]), np.conj(Z[:, :f])], axis=1)

    def imag_norm(self, Z):
        """max |Im x|, |Im y| over free vertices (0 for a real realization)."""
        f = self.f
        X = 0.5 * (Z[:, :f] + Z[:, f:]); Y = -0.5j * (Z[:, :f] - Z[:, f:])
        return np.maximum(np.abs(X.imag), np.abs(Y.imag)).max(axis=1)

    def min_sep(self, Z):
        D = np.abs(Z[:, None, :] - Z[None, :, :]).max(axis=2)
        np.fill_diagonal(D, np.inf)
        return D.min(), D


def dedup_add(store, Znew, tol=1e-6):
    """store: (N, d) array; returns merged array with new distinct rows."""
    if store is None or len(store) == 0:
        out = []
        for z in Znew:
            if all(np.abs(z - o).max() > tol for o in out):
                out.append(z)
        return np.array(out)
    keep = []
    allz = store
    for z in Znew:
        if np.abs(allz - z).max(axis=1).min() > tol:
            allz = np.vstack([allz, z[None]]); keep.append(z)
    return allz
