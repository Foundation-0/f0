"""Three positive charges in a plane: search for degenerate balance points of high order.
All balance points lie in the plane of the charges. There the in-plane Hessian has positive trace, so a degenerate
point has one zero eigenvalue. Along that direction the potential reduces to a function phi(t) of one variable
(the other in-plane direction is solved out). The point has order k if phi'' = ... = phi^(k) = 0.
Order 2 is a fold, order 3 a cusp, order 4 would unfold into 2 minima and 2 saddles and give 6 balance points.
Unknowns: third site (x3, y3), log charges (alpha, beta), point (px, py): 6. Conditions for order k: 2 + (k - 1).
The program minimises the residual of the order-3 and order-4 conditions from many random starts and reports
whether solutions exist, and for cusps, the sign of phi'''' (positive: a degenerate minimum, which would unfold
into two minima and a saddle)."""
import numpy as np, sys
from scipy.optimize import least_squares
rng = np.random.default_rng(int(sys.argv[1])); NST = int(sys.argv[2]); ORDER = int(sys.argv[3])
def setup(u):
    x3, y3, al, be, px, py = u
    A = np.array([[0, 0], [1, 0], [x3, y3]], float); q = np.array([1.0, np.exp(al), np.exp(be)])
    return A, q, np.array([px, py])
def v_grad_hess(P, A, q):
    D = P[None, :] - A; r2 = (D * D).sum(1); r = np.sqrt(r2)
    g = -(q[:, None] * D / (r2 * r)[:, None]).sum(0)
    H = (q[:, None, None] * (3 * D[:, :, None] * D[:, None, :] - r2[:, None, None] * np.eye(2)) / (r2 * r2 * r)[:, None, None]).sum(0)
    return g, H
def reduced(u, nt=9, h=None):
    """derivatives phi2, phi3, phi4, phi5 of the reduced function at the point, by solving out the stiff direction."""
    A, q, P = setup(u); g, H = v_grad_hess(P, A, q)
    w, V = np.linalg.eigh(H); e = V[:, 0]; f = V[:, 1]         # e: soft direction (smallest eigenvalue)
    d = np.min(np.linalg.norm(P[None] - A, axis=1)); h = 0.04 * d if h is None else h
    ts = np.linspace(-1, 1, nt) * h; vals = []
    for t in ts:
        s = 0.0
        for it in range(30):
            X = P + t * e + s * f; gg, HH = v_grad_hess(X, A, q)
            ds = (gg @ f) / (f @ HH @ f); s -= ds
            if abs(ds) < 1e-15: break
        X = P + t * e + s * f
        vals.append((q / np.linalg.norm(X[None] - A, axis=1)).sum())
    c = np.polynomial.polynomial.polyfit(ts / h, np.array(vals), 6)
    scale = q.sum() / d
    return [c[k] * np.math.factorial(k) / h**k * d**k / scale for k in (2, 3, 4, 5)], g * d**2 / q.sum(), w
import math; np.math = math
def resid(u):
    try: ph, g, w = reduced(u)
    except Exception: return np.ones(2 + ORDER - 1) * 1e3
    return np.concatenate([g, ph[:ORDER - 1]])
sols = []
for s in range(NST):
    u0 = np.array([rng.uniform(-1.5, 2.5), rng.uniform(0.05, 2.5), rng.uniform(-3, 3), rng.uniform(-3, 3), rng.uniform(-0.5, 1.5), rng.uniform(-0.3, 1.5)])
    try: r = least_squares(resid, u0, xtol=1e-14, ftol=1e-14, gtol=1e-14, max_nfev=300, bounds=([-4, 0.01, -7, -7, -4, -4], [5, 6, 7, 7, 5, 5]))
    except Exception: continue
    if np.abs(r.fun).max() < 1e-7:
        ph, g, w = reduced(r.x); sols.append((r.x, ph, w))
print(f"order {ORDER}: starts {NST}, converged solutions {len(sols)}")
if ORDER == 3:
    s4 = np.array([s[1][2] for s in sols]); print("  sign of the fourth derivative at the cusps: positive %d, negative %d; smallest |value| %.2e" % ((s4 > 0).sum(), (s4 < 0).sum(), np.abs(s4).min() if len(s4) else float('nan')))
    print("  stiff eigenvalue sign: positive %d, negative %d" % (sum(1 for s in sols if s[2][1] > 0), sum(1 for s in sols if s[2][1] < 0)))
    for x, ph, w in sorted(sols, key=lambda s: s[1][2])[-3:]: print("   largest fourth derivative:", np.round(x, 4), "phi4 = %.4f" % ph[2])
if ORDER >= 4:
    for x, ph, w in sols[:10]: print("   ", np.round(x, 5), "phi5 = %.4f" % ph[3], " max residual %.1e" % np.abs(resid(x)).max())
