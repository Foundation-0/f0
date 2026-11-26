"""Rank of (sites, charges) -> harmonic Taylor coefficients of degrees 1..k at the centre, for Platonic solids."""
import numpy as np, sys
from numpy.polynomial import legendre as Lg
import hmodel as hm
for solid, k in (("octahedron", 3), ("icosahedron", 5)):
    U0 = hm.SOLIDS[solid] / np.linalg.norm(hm.SOLIDS[solid][0]); N = len(U0)
    rng = np.random.default_rng(3); XS = rng.normal(size=(400, 3)); XS /= np.linalg.norm(XS, axis=1)[:, None]
    fit = {}
    for j in range(1, k + 1):
        mons, B = hm.hbasis(j); E = np.array(mons); fit[j] = np.linalg.pinv(np.prod(XS[:, None, :] ** E[None], axis=2) @ B.T)
    def cond(u):
        A = u[:3 * N].reshape(N, 3); q = u[3 * N:]; r = np.linalg.norm(A, axis=1); ah = A / r[:, None]
        return np.concatenate([fit[j] @ (q[None] / r[None] ** (j + 1) * Lg.legval(XS @ ah.T, [0] * j + [1])).sum(1) for j in range(1, k + 1)])
    u0 = np.concatenate([U0.ravel(), np.ones(N)]); h = 1e-6
    J = np.array([(cond(u0 + h * e) - cond(u0 - h * e)) / (2 * h) for e in np.eye(4 * N)]).T
    u, s, vt = np.linalg.svd(J)
    r = (s > 1e-8 * s[0]).sum()
    print(f"{solid}: Jacobian {J.shape}, rank {r}, singular values (smallest 4) {np.round(s[-4:], 10)}")
    if r < J.shape[0]:
        # left null vectors: coefficient functionals that cannot be moved to first order
        nullL = u[:, r:]
        o = 0
        for j in range(1, k + 1):
            n = 2 * j + 1; print(f"   left-null component in degree {j}: norm {np.linalg.norm(nullL[o:o+n]):.3f}"); o += n
