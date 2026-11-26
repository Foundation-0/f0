#!/usr/bin/env python3
"""The centre of a regular tetrahedron of equal charges is a T(4,4,4) point.

Run: python3 -O t444_check.py      (needs sympy; raises on any failure)

1. Exact Taylor jet of V = sum 1/|x - p_i| at the centre, p_i the vertices
   (1,1,1), (1,-1,-1), (-1,1,-1), (-1,-1,1): degrees 1 and 2 vanish, the cubic
   is c3 xyz with c3 != 0, the quartic is c4 K4 with K4 = x^4 + ... and
   c4 != 0 on each axis.
2. Milnor number of the 4-jet f4 = xyz + (c4/c3) K4 by a Groebner basis:
   the quotient C[x,y,z]/(grad f4) has dimension 27; the critical points
   other than 0 are 16 distinct simple ones; so 0 has multiplicity 11.
"""
import sympy as sp


class Fail(Exception):
    pass


def need(c, msg):
    if not c:
        raise Fail(msg)


x, y, z, t = sp.symbols("x y z t")
P = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
V = sum(1 / sp.sqrt((x - a) ** 2 + (y - b) ** 2 + (z - c) ** 2) for a, b, c in P)
ser = sp.series(V.subs({x: t * x, y: t * y, z: t * z}), t, 0, 6).removeO()
J = {k: sp.expand(ser.coeff(t, k)) for k in range(6)}
K4 = x**4 + y**4 + z**4 - 3 * (x**2 * y**2 + y**2 * z**2 + z**2 * x**2)
need(sp.simplify(J[1]) == 0 and sp.simplify(J[2]) == 0, "gradient or Hessian does not vanish")
c3 = sp.simplify(J[3] / (x * y * z))
need(c3.free_symbols == set() and c3 != 0, "cubic is not a multiple of xyz")
c4 = sp.simplify(J[4] / K4)
need(c4.free_symbols == set() and c4 != 0, "quartic is not a multiple of K4")
need(sp.simplify(J[5]) == 0, "quintic expected to vanish by symmetry")
print("jet: cubic %s xyz, quartic %s K4, quintic 0" % (c3, c4))
lam = sp.nsimplify(c4 / c3)
need(lam == sp.Rational(-7, 90), "ratio c4/c3 is not -7/90")
f = x * y * z + lam * K4
for v in (x, y, z):
    need(sp.expand(f.subs({w: 0 for w in (x, y, z) if w != v})) == lam * v**4, "axis restriction")
print("axis restrictions of the 4-jet: (-7/90) x^4 and the same in y, z, so T(4,4,4)")

g = [sp.diff(f, v) for v in (x, y, z)]
G = sp.groebner(g, x, y, z, order="grevlex")
lead = [sp.Poly(p, x, y, z).monoms(order="grevlex")[0] for p in G.exprs]
B = 30
std = [(a, b, c) for a in range(B) for b in range(B) for c in range(B)
       if not any(a >= l[0] and b >= l[1] and c >= l[2] for l in lead)]
need(all(max(m) < B - 1 for m in std), "quotient not finite inside the search box")
need(len(std) == 27, "total multiplicity is %d, not 27" % len(std))
sols = sp.solve_poly_system(g, x, y, z)
others = [s for s in sols if any(sp.simplify(v) != 0 for v in s)]
H = sp.hessian(f, (x, y, z))
dets = [sp.simplify(H.subs(dict(zip((x, y, z), s))).det()) for s in others]
need(all(d != 0 for d in dets), "a critical point away from 0 is degenerate")
mu = len(std) - len(others)
print("total multiplicity 27; %d simple critical points away from 0; Milnor number at 0: %d" % (len(others), mu))
need(mu == 11, "Milnor number is not 11")
print("PASS: the centre is T(4,4,4) with Milnor number 11")
