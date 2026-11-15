"""The symmetric flat family n = (a, a, b, b), a^2 + b^2 = 1/2 (two equal pairs of charges).
Here the cubic term at the flat point is degenerate: it is y times a quadratic form, with lines of critical points
through the origin. The multiplicity of the flat point depends on the order of the potential along those lines.
This program finds the critical lines and prints the Taylor coefficients of the potential along each."""
import numpy as np, sys
from numpy.polynomial import legendre as L
from scipy.optimize import least_squares
from flat_param import flat_config, cubic_parts
import quadrics as qd
def line_coeffs(A, q, e, kmax=8):
    r = np.linalg.norm(A, axis=1); cs = A @ e / r
    return np.array([sum(q[i] * L.legval(cs[i], [0] * k + [1]) / r[i] ** (k + 1) for i in range(4)) for k in range(kmax + 1)])
def critical_lines(T):
    rng = np.random.default_rng(0); nrm = np.sqrt((T ** 2).sum())
    E = rng.normal(size=(4000, 3)); E /= np.linalg.norm(E, axis=1)[:, None]
    F = np.linalg.norm(np.einsum('abc,mb,mc->ma', T, E, E), axis=1) / nrm
    found = []
    for i in np.argsort(F)[:60]:
        e0 = E[i]; th0 = np.arccos(e0[2]); ph0 = np.arctan2(e0[1], e0[0])
        def res(p):
            e = np.array([np.sin(p[0]) * np.cos(p[1]), np.sin(p[0]) * np.sin(p[1]), np.cos(p[0])])
            return np.einsum('abc,b,c->a', T, e, e) / nrm
        s = least_squares(res, [th0, ph0], xtol=1e-15, ftol=1e-15, gtol=1e-15)
        e = np.array([np.sin(s.x[0]) * np.cos(s.x[1]), np.sin(s.x[0]) * np.sin(s.x[1]), np.cos(s.x[0])])
        if np.linalg.norm(res(s.x)) < 1e-9 and all(abs(abs(e @ b) - 1) > 1e-5 for b in found): found.append(e)
    return found
if __name__ == "__main__":
    print("  a       b      charge ratio | lines | per line: s^4, s^5, s^6 coefficient over the cubic scale")
    for a in np.concatenate([np.linspace(0.02, 0.5, 25), np.linspace(0.5, 0.7, 21)[1:]]):
        b = np.sqrt(0.5 - a * a); A, q, _ = flat_config(np.array([a, a, b, b]))
        U, c = cubic_parts(A, q); T = qd.tensor(U[None], c[None])[0]; c3 = np.sqrt((T ** 2).sum())
        lines = critical_lines(T); out = []
        for e in lines:
            co = line_coeffs(A, q, e); out.append((co[4] / c3, co[5] / c3, co[6] / c3))
        out.sort()
        print("  %.4f  %.4f  %8.4f | %d | " % (a, b, q[0] / q[2] if abs(A[0, 2]) < 1e-9 or True else 0, len(lines)) + " ; ".join("%+.5f %+.5f %+.5f" % t for t in out))
