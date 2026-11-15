"""Edge-pinned frame for triangle-free Laman graphs (search code).  Reuses the tracker of ../lam.py.

Frame: vertex A at 0, vertex B at 1 (u = w = 1), which fixes translation, rotation and scale (lambda_AB = 1).
Parameters P (complex, length m): squared lengths of the m = 2 f remaining edges.  Real point: P real.
Unknowns z: u of the f free vertices, then w.  Every class of realizations modulo direct isometries has exactly
one solution, so the generic count is the full Laman number (no halving); mirror images are separate solutions.
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from lam import Laman


class EdgeFrame(Laman):
    def __init__(self, n, edges, ab):
        self.n, self.E = n, [tuple(e) for e in edges]
        A, B = ab
        self.tri = ab
        es = {frozenset(e): i for i, e in enumerate(self.E)}
        self.tri_edges = [es[frozenset((A, B))]]
        self.free = [v for v in range(1, n + 1) if v not in ab]
        self.f = len(self.free)
        self.rem = [i for i in range(len(self.E)) if i not in self.tri_edges]
        self.m = len(self.rem)
        assert self.m == 2 * self.f
        col = {v: i for i, v in enumerate(self.free)}
        col[A], col[B] = self.f, self.f + 1
        self.ea = np.array([col[self.E[i][0]] for i in self.rem])
        self.eb = np.array([col[self.E[i][1]] for i in self.rem])
        self.nP = self.m

    def real_params_from_lengths(self, lam):
        lam = np.asarray(lam, float); sc = lam[self.tri_edges[0]]
        return ((lam / sc)[self.rem] ** 2).astype(complex), sc

    def lengths_from_real_params(self, P):
        lam = np.ones(len(self.E)); lam[self.rem] = np.sqrt(np.real(P)); return lam

    def full(self, Z, P):
        Bn = Z.shape[0]; f = self.f
        U = np.empty((Bn, f + 2), complex); W = np.empty((Bn, f + 2), complex)
        U[:, :f] = Z[:, :f]; W[:, :f] = Z[:, f:]
        U[:, f] = 0; W[:, f] = 0; U[:, f + 1] = 1; W[:, f + 1] = 1
        return U, W

    def F(self, Z, P):
        U, W = self.full(Z, P)
        return (U[:, self.ea] - U[:, self.eb]) * (W[:, self.ea] - W[:, self.eb]) - P

    def FJ(self, Z, P):
        U, W = self.full(Z, P)
        du = U[:, self.ea] - U[:, self.eb]; dw = W[:, self.ea] - W[:, self.eb]
        Fv = du * dw - P
        Bn = Z.shape[0]; f = self.f; m = self.m
        J = np.zeros((Bn, m, 2 * f + 4), complex)
        r = np.arange(m)
        J[:, r, self.ea] += dw; J[:, r, f + 2 + self.ea] += du
        J[:, r, self.eb] -= dw; J[:, r, f + 2 + self.eb] -= du
        Jz = np.concatenate([J[:, :, :f], J[:, :, f + 2:2 * f + 2]], axis=2)
        return Fv, Jz, None, None

    def dFdP(self, Z, P):
        Fv, Jz, _, _ = self.FJ(Z, P)
        D = np.broadcast_to(-np.eye(self.m, dtype=complex), (Z.shape[0], self.m, self.m))
        return Jz, D

    def Ht(self, Z, P, dP):
        Fv, Jz, _, _ = self.FJ(Z, P)
        if np.ndim(dP) == 1:
            dP = np.broadcast_to(dP, (Z.shape[0], self.nP))
        return Fv, Jz, -dP

    def min_sep(self, Z, block=512):
        """Smallest L_inf distance between distinct rows (chunked; returns (value, None))."""
        R = np.concatenate([Z.real, Z.imag], axis=1)
        sq = (R ** 2).sum(axis=1)
        best = np.inf
        for i in range(0, len(R), block):
            G = sq[i:i + block, None] + sq[None, :] - 2 * R[i:i + block] @ R.T
            idx = np.arange(i, min(i + block, len(R)))
            G[idx - i, idx] = np.inf
            # candidates by L2; exact L_inf for the closest few per row
            cand = np.argpartition(G, 2, axis=1)[:, :2]
            for a, row in zip(idx, cand):
                for b in row:
                    if b != a:
                        best = min(best, np.abs(Z[a] - Z[b]).max())
        return best, None
