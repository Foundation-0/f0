"""Polynomial system for equilibria of n point charges, plus a batched adaptive path tracker.

Unknowns z = (x_0..x_{D-1}, t_0..t_{n-1}), with t_i = 1/r_i, r_i = |x - p_i|.
Equations (all polynomial, no denominators):
  F_i = t_i^2 * sum_k (x_k - p_ik)^2 - 1           i = 0..n-1
  G_k = sum_i q_i t_i^3 (x_k - p_ik)                k = 0..D-1
G = 0 is grad V = 0 for V = sum q_i/r_i, multiplied by -1. Since t_i^2 d_i = 1, t_i != 0 on every
solution, so the spurious r_i = 0 components of the cleared-denominator form never appear.
Symmetry: t_i -> -t_i maps a solution for charges q to one for q with q_i -> -q_i, so the complex
solution set for fixed |q| covers every sign pattern. (x, t) -> (x, -t) is a solution of the same system.
Physical (positive charges) solutions: x real, t real, all t_i > 0 (or all < 0, the mirror copy).

Parameters theta = (p (n x D), q (n)), stored batched: P (B,n,D), Q (B,n).
Everything here is numerical (float64 / complex128).
"""
import numpy as np


def F_J(Z, P, Q, D):
    """Z: (B, D+n). P: (B,n,D). Q: (B,n). Returns F (B,N), J (B,N,N) with N = D+n."""
    B = Z.shape[0]
    n = Q.shape[1]
    N = D + n
    x = Z[:, :D]
    t = Z[:, D:]
    dx = x[:, None, :] - P  # (B,n,D)
    d = np.sum(dx * dx, axis=2)  # (B,n)
    F = np.empty((B, N), dtype=complex)
    J = np.zeros((B, N, N), dtype=complex)
    t2 = t * t
    t3 = t2 * t
    F[:, :n] = t2 * d - 1.0
    F[:, n:] = np.einsum('bi,bik->bk', Q * t3, dx)
    # dF_i/dx_k = 2 t_i^2 dx_ik ; dF_i/dt_i = 2 t_i d_i
    J[:, :n, :D] = 2.0 * t2[:, :, None] * dx
    idx = np.arange(n)
    J[:, idx, D + idx] = 2.0 * t * d
    # dG_k/dx_l = delta_kl sum_i q_i t_i^3 ; dG_k/dt_i = 3 q_i t_i^2 dx_ik
    s = np.sum(Q * t3, axis=1)
    for k in range(D):
        J[:, n + k, k] = s
    J[:, n:, D:] = np.transpose(3.0 * (Q * t2)[:, :, None] * dx, (0, 2, 1))
    return F, J


def dF_dtheta(Z, P, Q, D, dP, dQ):
    """Directional derivative of F wrt parameters along (dP, dQ) (batched or broadcast)."""
    n = Q.shape[1]
    x = Z[:, :D]
    t = Z[:, D:]
    dx = x[:, None, :] - P
    t2 = t * t
    t3 = t2 * t
    out = np.empty((Z.shape[0], D + n), dtype=complex)
    out[:, :n] = t2 * np.sum(-2.0 * dx * dP, axis=2)
    out[:, n:] = np.einsum('bi,bik->bk', dQ * t3, dx) + np.einsum('bi,bik->bk', Q * t3, -dP)
    return out


def param_jac(Z, P, Q, D):
    """Full dF/dtheta for theta = (P.flatten(), Q). Returns (B, N, n*D + n)."""
    B = Z.shape[0]
    n = Q.shape[1]
    cols = []
    for i in range(n):
        for k in range(D):
            dP = np.zeros((B, n, D), dtype=complex)
            dP[:, i, k] = 1.0
            cols.append(dF_dtheta(Z, P, Q, D, dP, np.zeros((B, n), dtype=complex)))
    for i in range(n):
        dQ = np.zeros((B, n), dtype=complex)
        dQ[:, i] = 1.0
        cols.append(dF_dtheta(Z, P, Q, D, np.zeros((B, n, D), dtype=complex), dQ))
    return np.stack(cols, axis=2)


def newton(Z, P, Q, D, steps=6, tol=1e-12):
    Z = Z.copy()
    for _ in range(steps):
        F, J = F_J(Z, P, Q, D)
        try:
            dz = np.linalg.solve(J, F[..., None])[..., 0]
        except np.linalg.LinAlgError:
            dz = np.zeros_like(Z)
            for b in range(Z.shape[0]):
                try:
                    dz[b] = np.linalg.solve(J[b], F[b])
                except np.linalg.LinAlgError:
                    dz[b] = 0
        Z = Z - dz
        if np.max(np.abs(dz)) < tol:
            break
    F, J = F_J(Z, P, Q, D)
    return Z, np.max(np.abs(F), axis=1)


def track(Z0, path, D, s_end=1.0, h0=0.02, hmin=1e-9, max_iter=20000, corr_tol=1e-9):
    """Batched adaptive predictor-corrector tracking.
    path(s) -> (P, Q, dP, dQ) for s a (B,) array: parameters and their s-derivative.
    Returns Z at s_end and a status array (True = reached end)."""
    B = Z0.shape[0]
    Z = Z0.astype(complex).copy()
    s = np.zeros(B)
    h = np.full(B, h0)
    done = np.zeros(B, bool)
    fail = np.zeros(B, bool)
    it = 0
    while True:
        act = ~(done | fail)
        if not act.any() or it > max_iter:
            break
        it += 1
        ia = np.where(act)[0]
        za = Z[ia]
        sa = s[ia]
        ha = np.minimum(h[ia], s_end - sa)
        P0, Q0, dP0, dQ0 = path(sa)
        F0, J0 = F_J(za, P0, Q0, D)
        ds0 = dF_dtheta(za, P0, Q0, D, dP0, dQ0)
        try:
            v0 = -np.linalg.solve(J0, ds0[..., None])[..., 0]
        except np.linalg.LinAlgError:
            v0 = np.zeros_like(za)
        # Heun-type predictor
        z1 = za + ha[:, None] * v0
        s1 = sa + ha
        P1, Q1, dP1, dQ1 = path(s1)
        F1, J1 = F_J(z1, P1, Q1, D)
        ds1 = dF_dtheta(z1, P1, Q1, D, dP1, dQ1)
        try:
            v1 = -np.linalg.solve(J1, ds1[..., None])[..., 0]
        except np.linalg.LinAlgError:
            v1 = v0
        zp = za + 0.5 * ha[:, None] * (v0 + v1)
        # corrector: 3 Newton steps, require contraction
        zc = zp.copy()
        ok = np.ones(len(ia), bool)
        prev = None
        scale = 1.0 + np.max(np.abs(zp), axis=1)
        for c in range(3):
            Fc, Jc = F_J(zc, P1, Q1, D)
            try:
                dz = np.linalg.solve(Jc, Fc[..., None])[..., 0]
            except np.linalg.LinAlgError:
                dz = np.full_like(zc, np.inf)
            nd = np.max(np.abs(dz), axis=1)
            nd = np.where(np.isfinite(nd), nd, np.inf)
            zc = zc - np.where(np.isfinite(dz), dz, 0)
            if prev is not None:
                ok &= (nd <= 0.5 * prev + 1e-14 * scale) | (nd < corr_tol * scale)
            if c == 0:
                ok &= nd < 0.1 * scale
            prev = nd
        ok &= prev < 1e-8 * scale
        ok &= np.all(np.isfinite(zc), axis=1)
        # accept
        acc = ia[ok]
        rej = ia[~ok]
        Z[acc] = zc[ok]
        s[acc] = s1[ok]
        h[acc] = np.minimum(h[acc] * 1.6, 0.1)
        h[rej] *= 0.5
        done |= s >= s_end - 1e-15
        fail[rej[h[rej] < hmin]] = True
        big = np.max(np.abs(Z), axis=1) > 1e8
        fail |= big & ~done
    return Z, done & ~fail


def linear_path(Pa, Qa, Pb, Qb):
    """Straight segment theta(s) = (1-s) a + s b; a, b unbatched."""
    dP = Pb - Pa
    dQ = Qb - Qa

    def path(sv):
        sv = np.asarray(sv)
        P = Pa[None] + sv[:, None, None] * dP[None]
        Q = Qa[None] + sv[:, None] * dQ[None]
        return P, Q, np.broadcast_to(dP, P.shape), np.broadcast_to(dQ, Q.shape)
    return path


def arc_path(Pa, Qa, Pb, Qb, Pm, Qm):
    """theta(s) = (1-s) a + s b + 4 s (1-s) m (complex detour m)."""
    def path(sv):
        sv = np.asarray(sv)
        w = 4 * sv * (1 - sv)
        dw = 4 - 8 * sv
        P = Pa[None] + sv[:, None, None] * (Pb - Pa)[None] + w[:, None, None] * Pm[None]
        Q = Qa[None] + sv[:, None] * (Qb - Qa)[None] + w[:, None] * Qm[None]
        dP = (Pb - Pa)[None] + dw[:, None, None] * Pm[None]
        dQ = (Qb - Qa)[None] + dw[:, None] * Qm[None]
        return P, Q, dP, dQ
    return path


def dedupe(Z, tol=1e-6):
    keep = []
    for z in Z:
        if all(np.max(np.abs(z - k)) > tol * (1 + np.max(np.abs(z))) for k in keep):
            keep.append(z)
    return np.array(keep) if keep else np.zeros((0, Z.shape[1]), complex)


def merge(A, Bz, tol=1e-6):
    out = list(A)
    added = 0
    for z in Bz:
        if all(np.max(np.abs(z - k)) > tol * (1 + np.max(np.abs(z))) for k in out):
            out.append(z)
            added += 1
    return np.array(out), added


def classify(Z, D, im_tol=1e-8):
    """Return per-solution: is_real flag, sign pattern of Re t (tuple), max |Im|."""
    imm = np.max(np.abs(Z.imag), axis=1) / (1 + np.max(np.abs(Z.real), axis=1))
    real = imm < im_tol
    sg = np.sign(Z[:, D:].real).astype(int)
    return real, sg, imm


def count_physical(Z, D, im_tol=1e-8):
    real, sg, imm = classify(Z, D, im_tol)
    pos = real & np.all(sg > 0, axis=1)
    return int(pos.sum())
