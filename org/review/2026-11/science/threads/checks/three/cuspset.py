"""The fold and cusp sets of the three-charge problem in direction coordinates.

At a degenerate critical point x with kernel direction t = (1,0), let psi_i be the angle of
u_i = (x - a_i)/r_i measured from t, beta the barycentric coordinates of x. Then
  fold:     sum beta_i exp(2 i psi_i) = -1/3,  sum beta_i = 1   (linear in beta: beta = beta(psi))
  geometry: beta_i r_i = w_i (Lami weights of the unit vectors u_i), so r_i = w_i/beta_i
  cusp:     G(psi) = sum beta_i^2 P3(cos psi_i)/w_i = 0
  type:     K(psi) = sum beta_i^3 P4(cos psi_i)/w_i^2 - (9/8)(sum beta_i^2 sin psi_i (5cos^2 psi_i - 1)/w_i)^2
            (sign of the effective quartic coefficient; K > 0 gives two minima nearby)
"""
import numpy as np


def beta_of(psi):
    """Barycentric coordinates of the point -1/3 in the triangle exp(2 i psi_k) (fold condition)."""
    psi = np.asarray(psi, float)
    Px = np.cos(2 * psi); Py = np.sin(2 * psi)
    X0, Y0 = -1.0 / 3.0, 0.0
    def area(ax, ay, bx, by, cx, cy):
        return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    tot = area(Px[..., 0], Py[..., 0], Px[..., 1], Py[..., 1], Px[..., 2], Py[..., 2])
    b1 = area(X0, Y0, Px[..., 1], Py[..., 1], Px[..., 2], Py[..., 2])
    b2 = area(Px[..., 0], Py[..., 0], X0, Y0, Px[..., 2], Py[..., 2])
    b3 = area(Px[..., 0], Py[..., 0], Px[..., 1], Py[..., 1], X0, Y0)
    with np.errstate(divide='ignore', invalid='ignore'):
        return np.stack([b1, b2, b3], -1) / tot[..., None]


def lami_w(psi):
    p = psi
    w1 = np.sin(p[..., 2] - p[..., 1]); w2 = np.sin(p[..., 0] - p[..., 2]); w3 = np.sin(p[..., 1] - p[..., 0])
    return np.stack([w1, w2, w3], -1)


def P3(c): return (5 * c ** 3 - 3 * c) / 2
def P4(c): return (35 * c ** 4 - 30 * c ** 2 + 3) / 8


def GK(psi):
    b = beta_of(psi); w = lami_w(psi)
    # orientation: allow overall sign of w (both orientations of the triangle)
    sgn = np.sign(w[..., :1])
    w = w * sgn
    c = np.cos(psi); s = np.sin(psi)
    r = w / b
    G = (b * P3(c) / r).sum(-1)
    e = (b * P4(c) / r ** 2).sum(-1)
    bb = (b * s * (5 * c ** 2 - 1) / r).sum(-1)
    K = e - 9.0 / 8.0 * bb ** 2
    Kn = K / (np.abs(e) + 9.0 / 8.0 * bb ** 2)
    with np.errstate(invalid='ignore'):
        valid = (b > 0).all(-1) & (w > 0).all(-1) & np.isfinite(G)
    return G, K, Kn, valid, b, w, r


def config(psi):
    """Triangle and point for a fold configuration: x = 0, a_i = -r_i u_i, scaled so that a1a2 = 1."""
    G, K, Kn, valid, b, w, r = GK(np.asarray(psi)[None])
    r = r[0]; psi = np.asarray(psi)
    u = np.c_[np.cos(psi), np.sin(psi)]
    A = -r[:, None] * u
    q = b[0] * r ** 3; q = q / q.sum()
    return A, q, np.zeros(2)
