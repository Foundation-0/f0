"""Multiplicity of the balance point at the centre of a regular tetrahedron of equal charges.

Step 1 (exact rationals): Taylor coefficients of V = sum 1/|x - a_i| at the centre, for the tetrahedron with
vertices (1,1,1), (1,-1,-1), (-1,1,-1), (-1,-1,1), up to degree 4, by differentiating 1/r symbolically along
monomials (done numerically here with high-order finite differences replaced by the closed form of the
harmonic expansion: 1/|x - a| = sum_l |x|^l P_l(cos gamma)/|a|^(l+1)).
Step 2: the 4-jet is c3 * xyz + c4 * K4 with K4 = x^4+y^4+z^4 - 3(x^2y^2+y^2z^2+z^2x^2). Count the solutions of
grad(c3 xyz + c4 K4) = 0 in C^3 other than the origin, by Newton iteration from many random complex starts.
With no solutions at infinity the Bezout number is 27, so the multiplicity at the origin is 27 minus that count
(each counted with its own multiplicity; here they are checked to be simple)."""
import numpy as np, itertools, math
from fractions import Fraction as Fr
A = [(1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1)]
# Legendre expansion: 1/|x-a| = sum_l r^l P_l(x.a/(r|a|)) / |a|^(l+1); degree-3 and degree-4 parts as polynomials.
# P3(t) = (5t^3 - 3t)/2 ; P4(t) = (35 t^4 - 30 t^2 + 3)/8.  With s = x.a and R = |a| (R^2 = 3):
# r^3 P3 = (5 s^3 - 3 s r^2 R^2)/(2 R^3) ; r^4 P4 = (35 s^4 - 30 s^2 r^2 R^2 + 3 r^4 R^4)/(8 R^4)
def poly_add(p, q, c=1):
    for k, v in q.items(): p[k] = p.get(k, 0) + c * v
def poly_mul(p, q):
    out = {}
    for (a, va) in p.items():
        for (b, vb) in q.items():
            k = tuple(i + j for i, j in zip(a, b)); out[k] = out.get(k, 0) + va * vb
    return out
X = {(1,0,0): Fr(1)}; Y = {(0,1,0): Fr(1)}; Z = {(0,0,1): Fr(1)}
r2 = {(2,0,0): Fr(1), (0,2,0): Fr(1), (0,0,2): Fr(1)}
deg3 = {}; deg4 = {}; deg2 = {}; deg1 = {}
for a in A:
    s = {(1,0,0): Fr(a[0]), (0,1,0): Fr(a[1]), (0,0,1): Fr(a[2])}
    s2 = poly_mul(s, s); s3 = poly_mul(s2, s); s4 = poly_mul(s2, s2); R2 = Fr(3)
    poly_add(deg1, s)                                             # times 1/R^3
    t = dict(); poly_add(t, s2, 3); poly_add(t, r2, -R2); poly_add(deg2, t)   # times 1/(2 R^5)
    t = dict(); poly_add(t, s3, 5); poly_add(t, poly_mul(s, r2), -3 * R2); poly_add(deg3, t)   # times 1/(2 R^7)
    t = dict(); poly_add(t, s4, 35); poly_add(t, poly_mul(s2, r2), -30 * R2); poly_add(t, poly_mul(r2, r2), 3 * R2 * R2); poly_add(deg4, t)  # times 1/(8 R^9)
clean = lambda p: {k: v for k, v in p.items() if v != 0}
print("degree 1 part (x 1/R^3):", clean(deg1)); print("degree 2 part (x 1/(2R^5)):", clean(deg2))
print("degree 3 part (x 1/(2R^7)):", clean(deg3)); print("degree 4 part (x 1/(8R^9)):", clean(deg4))
R = math.sqrt(3.0)
c3 = float(clean(deg3)[(1,1,1)]) / (2 * R ** 7)
d4 = clean(deg4); c4 = float(d4[(4,0,0)]) / (8 * R ** 9); mix = float(d4[(2,2,0)]) / (8 * R ** 9)
print(f"c3 (coefficient of xyz) = {c3:.6f}; coefficient of x^4 = {c4:.6f}; of x^2y^2 = {mix:.6f}; ratio mixed/pure = {mix/c4:.4f} (K4 has -3)")
lam = c4 / c3
def F(v):
    x, y, z = v
    return np.array([y*z + lam*(4*x**3 - 6*x*(y*y+z*z)), x*z + lam*(4*y**3 - 6*y*(x*x+z*z)), x*y + lam*(4*z**3 - 6*z*(x*x+y*y))])
def J(v):
    x, y, z = v
    return np.array([[lam*(12*x*x - 6*(y*y+z*z)), z - 12*lam*x*y, y - 12*lam*x*z],
                     [z - 12*lam*x*y, lam*(12*y*y - 6*(x*x+z*z)), x - 12*lam*y*z],
                     [y - 12*lam*x*z, x - 12*lam*y*z, lam*(12*z*z - 6*(x*x+y*y))]])
rng = np.random.default_rng(1); roots = []
scale = 1.0 / abs(lam)
for t in range(40000):
    v = (rng.normal(size=3) + 1j * rng.normal(size=3)) * scale * rng.uniform(0.05, 3)
    for it in range(80):
        try: dv = np.linalg.solve(J(v), F(v))
        except np.linalg.LinAlgError: break
        v = v - dv
        if np.linalg.norm(dv) < 1e-13 * (1 + np.linalg.norm(v)): break
    if np.linalg.norm(F(v)) < 1e-9 * scale ** 2 and np.linalg.norm(v) > 1e-6 * scale:
        if not any(np.linalg.norm(v - r) < 1e-7 * scale for r in roots): roots.append(v)
nz = len(roots)
simple = sum(1 for r in roots if abs(np.linalg.det(J(r))) > 1e-8 * scale ** 6)
real = sum(1 for r in roots if np.linalg.norm(np.imag(r)) < 1e-8 * scale)
print(f"lambda = c4/c3 = {lam:.6f}; nonzero solutions found: {nz} (simple: {simple}; real: {real})")
print(f"multiplicity at the centre = 27 - {nz} = {27 - nz}   (valid if all found, all simple, none at infinity)")
norms = sorted(round(float(np.linalg.norm(r) / scale), 4) for r in roots); print("norms/scale:", sorted(set(norms)))
