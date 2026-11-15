#!/usr/bin/env python3
"""A harmonic quartic in three variables with all 27 critical points real: an exact check, written by the reviewer.

The polynomial, with rational coefficients a1..a5 read from the command line (decimal strings, used exactly):
  f = K4/3 + a1 (x+y+z) + a2 (xy+yz+zx) + a3 xyz
      + a4 [x^3+y^3+z^3 - (3/2)(x^2 y + x^2 z + y^2 x + y^2 z + z^2 x + z^2 y)] + a5 [x^2 y + y^2 z + z^2 x - x y^2 - y z^2 - z x^2],
  K4 = x^4 + y^4 + z^4 - 3 (x^2 y^2 + y^2 z^2 + z^2 x^2).
Every term is harmonic, so f is harmonic for any a. Its gradient is three cubics, so it has at most 27 critical points.
Candidates are found by Newton in 50-digit arithmetic from starts spread over all scales. Each is then proved by the
Krawczyk test in ball arithmetic (python-flint arb) on a small cube, which also fixes the sign of det(Hessian).
Cubes are checked pairwise disjoint in exact rationals. If 27 are proved, all critical points are real and simple.
Usage: quartic27_check.py a1 a2 a3 a4 a5"""
import sys, itertools
from fractions import Fraction
import numpy as np, mpmath as mp
from flint import arb, ctx, fmpq
ctx.prec = 300; mp.mp.dps = 50
class CheckFailure(Exception): pass
a = [Fraction(s) for s in sys.argv[1:6]]
# exact coefficient table: monomial (i,j,k) -> Fraction
C = {}
def add(m, c): C[m] = C.get(m, Fraction(0)) + c
for m in [(4,0,0),(0,4,0),(0,0,4)]: add(m, Fraction(1, 3))
for m in [(2,2,0),(0,2,2),(2,0,2)]: add(m, Fraction(-1))
for m in [(1,0,0),(0,1,0),(0,0,1)]: add(m, a[0])
for m in [(1,1,0),(0,1,1),(1,0,1)]: add(m, a[1])
add((1,1,1), a[2])
for m in [(3,0,0),(0,3,0),(0,0,3)]: add(m, a[3])
for m in [(2,1,0),(2,0,1),(1,2,0),(0,2,1),(1,0,2),(0,1,2)]: add(m, -Fraction(3, 2) * a[3])
for m in [(2,1,0),(0,2,1),(1,0,2)]: add(m, a[4])
for m in [(1,2,0),(0,1,2),(2,0,1)]: add(m, -a[4])
# exact check that f is harmonic
lap = {}
for (i, j, k), c in C.items():
    for v, e in enumerate((i, j, k)):
        if e >= 2:
            t = [i, j, k]; t[v] -= 2; lap[tuple(t)] = lap.get(tuple(t), Fraction(0)) + c * e * (e - 1)
if any(v != 0 for v in lap.values()): raise CheckFailure("the polynomial is not harmonic")
def grad_hess(X, num):
    g = [num(0)] * 3; H = [[num(0)] * 3 for _ in range(3)]
    for (i, j, k), c in C.items():
        e = (i, j, k); cc = num(c)
        for u in range(3):
            if e[u] == 0: continue
            eu = list(e); eu[u] -= 1
            g[u] = g[u] + cc * e[u] * X[0] ** eu[0] * X[1] ** eu[1] * X[2] ** eu[2]
            for v in range(3):
                if eu[v] == 0: continue
                ev = list(eu); ev[v] -= 1
                H[u][v] = H[u][v] + cc * e[u] * eu[v] * X[0] ** ev[0] * X[1] ** ev[1] * X[2] ** ev[2]
    return g, H
mpn = lambda c: mp.mpf(c.numerator) / mp.mpf(c.denominator) if isinstance(c, Fraction) else mp.mpf(c)
arn = lambda c: arb(fmpq(c.numerator, c.denominator)) if isinstance(c, Fraction) else arb(c)
rng = np.random.default_rng(1); found = []
for trial in range(6000):
    v = rng.normal(size=3); v *= 10 ** rng.uniform(-5, 1.5) / np.linalg.norm(v)
    x = mp.matrix([mp.mpf(float(t)) for t in v]); ok = False
    for it in range(80):
        g, H = grad_hess(x, mpn)
        try: dx = mp.lu_solve(mp.matrix(H), mp.matrix(g))
        except ZeroDivisionError: break
        x = x - dx
        if mp.norm(dx) < mp.mpf(10) ** -40 * (mp.norm(x) + mp.mpf(10) ** -30): ok = True; break
    if not ok: continue
    if all(mp.norm(x - y) > mp.mpf(10) ** -12 * (mp.norm(x) + mp.norm(y) + mp.mpf(10) ** -20) for y in found): found.append(x)
print("candidates found by Newton from 6,000 starts:", len(found))
proved = []
for x in found:
    sep = min([mp.norm(x - y) for y in found if y is not x])
    centre = [Fraction(int(mp.nint(x[k] * mp.mpf(10) ** 40)), 10 ** 40) for k in range(3)]
    cA = [arn(c) for c in centre]
    g, H = grad_hess(x, mpn); Ainv = mp.matrix(H) ** -1
    Aq = [[arn(Fraction(int(mp.nint(Ainv[i, j] * mp.mpf(10) ** 30)), 10 ** 30)) for j in range(3)] for i in range(3)]
    r = Fraction(int(mp.nint(sep / 4 * mp.mpf(10) ** 40)), 10 ** 40); done = False
    for attempt in range(40):
        r = r / 2; rb = arn(r); box = [cA[k] + arb(0, 1) * rb for k in range(3)]
        gc, _ = grad_hess(cA, arn); _, HB = grad_hess(box, arn)
        K = []
        for i in range(3):
            v = -sum(Aq[i][j] * gc[j] for j in range(3))
            for j in range(3): v = v + ((1 if i == j else 0) - sum(Aq[i][k] * HB[k][j] for k in range(3))) * (arb(0, 1) * rb)
            K.append(v)
        det = (HB[0][0] * (HB[1][1] * HB[2][2] - HB[1][2] * HB[2][1]) - HB[0][1] * (HB[1][0] * HB[2][2] - HB[1][2] * HB[2][0]) + HB[0][2] * (HB[1][0] * HB[2][1] - HB[1][1] * HB[2][0]))
        if all(K[i].abs_upper() < rb * arb("0.999") for i in range(3)) and (det > 0 or det < 0):
            proved.append((centre, r, 2 if det > 0 else 1)); done = True; break
    if not done: print("  not proved: candidate at distance %.3e" % float(mp.norm(x)))
for i in range(len(proved)):
    for j in range(i):
        ci, ri, _ = proved[i]; cj, rj, _ = proved[j]
        if not any(abs(ci[k] - cj[k]) > ri + rj for k in range(3)): raise CheckFailure("two cubes overlap")
rad = sorted(float(mp.sqrt(sum(mpn(c) ** 2 for c in p[0]))) for p in proved)
print("coefficients a1..a5:", [str(x) for x in a])
print("distances of the proved critical points from the origin:", " ".join("%.3g" % v for v in rad))
m2 = sum(1 for p in proved if p[2] == 2); m1 = sum(1 for p in proved if p[2] == 1)
print(f"PROVED: {len(proved)} real non-degenerate critical points; det(Hessian) positive at {m2}, negative at {m1}")
if len(proved) != 27: raise CheckFailure(f"proved {len(proved)}, not 27")
print("OK: all 27 critical points are real and simple")
