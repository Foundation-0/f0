"""Critical points of an axisymmetric harmonic polynomial, counted reliably.

f(rho, z) = sum_{j=1..k+1} a_j r^j P_j(z/r) with integer a_j. Its critical points are
  on the axis: the real roots of A'(z), A(z) = sum a_j z^j;
  off the axis: circles, the real solutions with s = rho^2 > 0 of  df/ds = 0 and df/dz = 0.
The off-axis system is solved by an exact resultant in s (sympy), real roots in z, then the common root in s.
Claim tested: (points on the axis) + 2 (circles) = k whenever all critical points are non-degenerate.
Reason: in the (rho, z) plane, with f extended evenly in rho, every critical point is a saddle, because
f_rho_rho + f_zz = -f_rho / rho vanishes there, and the gradient of the leading term winds -k times at infinity."""
import sympy as sp, random, sys
from math import comb
s, z = sp.symbols('s z')
def F(a):
    f = 0
    for j in range(1, len(a)):
        for m in range(j // 2 + 1):
            p = sp.Rational((-1) ** m * comb(j, m) * comb(2 * j - 2 * m, j), 2 ** j)
            f += a[j] * p * z ** (j - 2 * m) * (s + z ** 2) ** m
    return sp.expand(f)
random.seed(int(sys.argv[1])); NS = int(sys.argv[2])
print(" k | samples | (on axis, circles): how many samples | identity on-axis + 2 circles = k holds in")
for k in range(2, 8):
    hist = {}; okc = 0; done = 0
    for t in range(NS):
        a = [0] + [random.randint(-9, 9) for _ in range(k)] + [random.choice([-1, 1]) * random.randint(1, 9)]
        f = F(a); fs = sp.diff(f, s); fz = sp.diff(f, z)
        A1 = sp.Poly(sum(j * a[j] * z ** (j - 1) for j in range(1, len(a))), z)
        on_axis = len(set(sp.real_roots(A1)))
        circles = 0
        if sp.degree(fs, s) >= 1:
            R = sp.Poly(sp.resultant(fs, fz, s), z)
            for zr in set(sp.real_roots(R)):
                zv = sp.N(zr, 40)
                ps = sp.Poly(fs.subs(z, zv), s); 
                for sr in ps.nroots(n=30):
                    if abs(sp.im(sr)) < 1e-20 and sp.re(sr) > 1e-15:
                        val = abs(sp.N(fz.subs({z: zv, s: sp.re(sr)}), 30)); scale = sum(abs(sp.N(c, 20)) for c in sp.Poly(fz.subs(z, zv), s).all_coeffs()) * (1 + abs(sp.re(sr))) ** sp.degree(fz, s)
                        if val < 1e-12 * scale: circles += 1
        else:
            # df/ds does not depend on s: solve it for z and then df/dz for s
            for zr in set(sp.real_roots(sp.Poly(fs, z))):
                for sr in sp.Poly(fz.subs(z, zr), s).nroots(n=30) if sp.degree(fz, s) >= 1 else []:
                    if abs(sp.im(sr)) < 1e-20 and sp.re(sr) > 1e-15: circles += 1
        done += 1; hist[(on_axis, circles)] = hist.get((on_axis, circles), 0) + 1; okc += (on_axis + 2 * circles == k)
    print(f" {k} | {done} | {dict(sorted(hist.items()))} | {okc} of {done}", flush=True)
