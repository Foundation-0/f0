"""Core numerics for three positive charges in the plane (written for this thread).

Sites A1=(0,0), A2=(1,0), A3=(a,b), b>0. Charges q (positive). V = sum q_i/|x-A_i|
restricted to the plane. Everything here is floating point (exploration only).
"""
import numpy as np


def sites(a, b):
    return np.array([[0.0, 0.0], [1.0, 0.0], [a, b]])


def lami(A, X):
    """Inverse map Z: point(s) X (...,2) -> charge ratios (...,3) normalised to sum 1,
    plus the 'Lami weights' w and distances r. Valid inside the triangle."""
    d = X[..., None, :] - A  # (...,3,2)
    r = np.sqrt((d * d).sum(-1))
    u = d / r[..., None]
    cr = lambda p, q: p[..., 0] * q[..., 1] - p[..., 1] * q[..., 0]
    w = np.stack([cr(u[..., 1, :], u[..., 2, :]), cr(u[..., 2, :], u[..., 0, :]), cr(u[..., 0, :], u[..., 1, :])], -1)
    q = r ** 2 * w
    q = q / q.sum(-1, keepdims=True)
    return q, w, r, u


def grad_hess(A, q, X):
    d = X[..., None, :] - A
    r2 = (d * d).sum(-1)
    r = np.sqrt(r2)
    c3 = q / (r2 * r)
    c5 = q / (r2 * r2 * r)
    g = -(c3[..., None] * d).sum(-2)
    H = 3 * np.einsum('...n,...nk,...nl->...kl', c5, d, d) - c3.sum(-1)[..., None, None] * np.eye(2)
    return g, H


def derivs(A, q, x):
    """Gradient, Hessian, third and fourth derivative tensors of V at a single point x (2,)."""
    g = np.zeros(2); H = np.zeros((2, 2)); T = np.zeros((2, 2, 2)); F = np.zeros((2, 2, 2, 2))
    I = np.eye(2)
    for i in range(3):
        y = x - A[i]
        r = np.linalg.norm(y)
        g += q[i] * (-y / r ** 3)
        H += q[i] * (3 * np.outer(y, y) - r * r * I) / r ** 5
        yyy = np.einsum('a,b,c->abc', y, y, y)
        dy = np.einsum('ab,c->abc', I, y)
        T += q[i] * (-15 * yyy / r ** 7 + 3 * (dy + dy.transpose(0, 2, 1) + dy.transpose(2, 1, 0)) / r ** 5)
        y4 = np.einsum('a,b,c,d->abcd', y, y, y, y)
        dyy = np.einsum('ab,c,d->abcd', I, y, y)
        sym6 = (dyy + np.einsum('ac,b,d->abcd', I, y, y) + np.einsum('ad,b,c->abcd', I, y, y)
                + np.einsum('bc,a,d->abcd', I, y, y) + np.einsum('bd,a,c->abcd', I, y, y) + np.einsum('cd,a,b->abcd', I, y, y))
        dd = np.einsum('ab,cd->abcd', I, I) + np.einsum('ac,bd->abcd', I, I) + np.einsum('ad,bc->abcd', I, I)
        F += q[i] * (105 * y4 / r ** 9 - 15 * sym6 / r ** 7 + 3 * dd / r ** 5)
    return g, H, T, F


def mu(A, X):
    """Minimum margin at X for its own equilibrium charges: lam_min/lam_max of
    M = sum (q_i/r_i^3) u_i u_i^T, minus 1/2. Positive <=> X is a local min of V_{Z(X)}."""
    q, w, r, u = lami(A, X)
    c = q / r ** 3
    M = np.einsum('...n,...nk,...nl->...kl', c, u, u)
    tr = M[..., 0, 0] + M[..., 1, 1]
    det = M[..., 0, 0] * M[..., 1, 1] - M[..., 0, 1] ** 2
    disc = np.sqrt(np.maximum(tr * tr / 4 - det, 0))
    lmin = tr / 2 - disc; lmax = tr / 2 + disc
    return lmin / lmax - 0.5


def Dnorm(A, X):
    """det(H)/trace(H)^2 for the equilibrium charges at X (sign = min/saddle)."""
    q, w, r, u = lami(A, X)
    g, H = grad_hess(A, q, X)
    det = H[..., 0, 0] * H[..., 1, 1] - H[..., 0, 1] ** 2
    tr = H[..., 0, 0] + H[..., 1, 1]
    return det / tr ** 2


def newton_all(A, q, X0, iters=80):
    X = X0.copy()
    for _ in range(iters):
        d = X[:, None, :] - A[None]
        r = np.sqrt((d * d).sum(2))
        g, H = grad_hess(A, q, X)
        det = H[:, 0, 0] * H[:, 1, 1] - H[:, 0, 1] ** 2
        det = np.where(np.abs(det) < 1e-300, 1e-300, det)
        st = np.c_[H[:, 1, 1] * g[:, 0] - H[:, 0, 1] * g[:, 1], H[:, 0, 0] * g[:, 1] - H[:, 0, 1] * g[:, 0]] / det[:, None]
        n = np.linalg.norm(st, axis=1)
        f = np.minimum(1, 0.3 * r.min(1) / np.maximum(n, 1e-300))
        X = X - st * f[:, None]
    return X


def crit_points(A, q, nseed=400, seed=0):
    """All critical points (numerical) of planar V inside the triangle.
    Seeds: interior Dirichlet points + points along edges + near vertices at the scale
    sqrt(q_i/|E_i|). Returns points, Hessian eigenvalues, and Morse check flag."""
    rng = np.random.default_rng(seed)
    S = [rng.dirichlet(np.full(3, 0.7), size=nseed) @ A]
    for i in range(3):
        for j in range(3):
            if i != j:
                t0 = np.sqrt(q[i]) / (np.sqrt(q[i]) + np.sqrt(q[j]))
                t = np.clip(t0 * 10 ** rng.uniform(-1.0, 0.2, 15), 1e-9, 1 - 1e-9)
                k = 3 - i - j
                s = 10 ** rng.uniform(-4, -0.5, 15)
                S.append(A[i] + t[:, None] * (A[j] - A[i]) + (s * t)[:, None] * (A[k] - A[i]))
    X = np.vstack(S)
    X = newton_all(A, q, X)
    g, H = grad_hess(A, q, X)
    d = X[:, None, :] - A[None]; r = np.sqrt((d * d).sum(2))
    scale = (q / r ** 2).sum(1)
    ok = np.isfinite(X).all(1) & (np.linalg.norm(g, axis=1) < 1e-10 * scale) & (r.min(1) > 1e-12)
    X = X[ok]; rm = r.min(1)[ok]
    pts = []; rr = []
    for k in np.argsort(rm):
        if all(np.linalg.norm(X[k] - pts[j]) > 1e-7 * min(rm[k], rr[j]) for j in range(len(pts))):
            pts.append(X[k]); rr.append(rm[k])
    pts = np.array(pts).reshape(-1, 2)
    if len(pts):
        g, H = grad_hess(A, q, pts)
        ev = np.linalg.eigvalsh(H)
    else:
        ev = np.zeros((0, 2))
    m = int((ev[:, 0] > 0).sum()); s = int((ev[:, 0] < 0).sum())
    return pts, ev, m, s, (s - m == 2)
