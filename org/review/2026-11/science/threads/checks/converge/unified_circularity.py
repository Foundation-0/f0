"""Is the 'sigma organises the extra mass' result circular?
sigma is a dynamical quantity. In the low-acceleration limit the definition of form B gives, identically,
M_b + M_extra = V^4/(G a0) = 4 sigma^4/(G a0) when sigma^2 = V^2/2 is measured at the same radius. So a law
M_extra ~ sigma^4 r^0 is partly forced. Tests:
  T1  the forced law with NO free parameter: M_b + M_extra = 4 sigma^4/(G a0)
  T2  the two-variable fit with sigma replaced by sigma_RAR, the speed the baryons alone predict (no M_tot in it)
  T3  the same fit with sigma shuffled within each class (destroys any real link, keeps the class structure)
  T4  one-variable baryon-only laws: M_extra = K M_b^p, and K (M_b^p)(r^b)"""
import csv, math, sys
import numpy as np
from scipy.optimize import least_squares
G, A0, MSUN, KPC = 6.67430e-11, 1.2e-10, 1.98847e30, 3.085677581491367e19
rows = [r for r in csv.DictReader(open(sys.argv[1])) if r["cls"] != "highz_RC100"]
cls = sorted({r["cls"] for r in rows})
r_ = np.array([float(r["r"]) for r in rows]); Mb = np.array([float(r["Mb"]) for r in rows]); Mt = np.array([float(r["Mtot"]) for r in rows])
sg = np.array([float(r["sigma"]) for r in rows]); c = np.array([cls.index(r["cls"]) for r in rows])
w = np.array([1.0 / math.sqrt(np.sum(c == ci) * len(cls)) for ci in c])
nu = lambda y: 1.0 / (1.0 - np.exp(-np.sqrt(np.maximum(y, 1e-30))))
def pred(Mx):
    Mn = np.maximum(Mb + Mx, 1e-3 * Mb); gN = G * Mn * MSUN / (r_ * KPC) ** 2
    return nu(gN / A0) * Mn
resid = lambda Mx: np.log10(Mt) - np.log10(pred(Mx))
score = lambda Mx: float(np.sqrt(np.sum((w * resid(Mx)) ** 2)))
def fit2(x, y, p0=(11.0, 4.0, 0.4)):
    f = least_squares(lambda p: w * resid(10 ** p[0] * x ** p[1] * y ** p[2]), p0)
    return f.x, score(10 ** f.x[0] * x ** f.x[1] * y ** f.x[2])
print(f"standard relation alone: {score(0 * Mb):.4f}")
p, s = fit2(sg / 200.0, r_ / 100.0); print(f"sigma, r (as measured): a={p[1]:.2f} b={p[2]:.2f} score {s:.4f}")
# T1 forced law
Mn_forced = 4 * (sg * 1e3) ** 4 / (G * A0) / MSUN
print(f"T1 forced law, no free parameter (M_b + M_extra = 4 sigma^4/(G a0)): score {score(Mn_forced - Mb):.4f}")
for i, k in enumerate(cls):
    m = c == i; print(f"     {k:14s} median residual {np.median(resid(Mn_forced - Mb)[m]):+.3f}")
# T2 baryon-only speed
gb = G * Mb * MSUN / (r_ * KPC) ** 2
s_rar = np.sqrt(nu(gb / A0) * gb * r_ * KPC / 2.0) / 1e3
print(f"correlation of log sigma with log sigma_RAR: {np.corrcoef(np.log10(sg), np.log10(s_rar))[0,1]:.3f}")
p, s = fit2(s_rar / 200.0, r_ / 100.0); print(f"T2 sigma_RAR, r (baryons only): a={p[1]:.2f} b={p[2]:.2f} score {s:.4f}")
# T3 shuffle
rng = np.random.default_rng(7); sc = []
for t in range(30):
    sh = sg.copy()
    for i in range(len(cls)):
        ix = np.where(c == i)[0]; sh[ix] = rng.permutation(sg[ix])
    sc.append(fit2(sh / 200.0, r_ / 100.0)[1])
print(f"T3 sigma shuffled within class (30 draws): score median {np.median(sc):.4f}, min {min(sc):.4f}")
# T4 baryon-only mass laws
f = least_squares(lambda q: w * resid(10 ** q[0] * (Mb / 1e11) ** q[1]), [10.5, 1.0]); print(f"T4 M_extra = K M_b^p: p={f.x[1]:.2f} score {score(10 ** f.x[0] * (Mb / 1e11) ** f.x[1]):.4f}")
p, s = fit2(Mb / 1e11, r_ / 100.0, (10.5, 1.0, 0.3)); print(f"T4 M_extra = K M_b^p r^b: p={p[1]:.2f} b={p[2]:.2f} score {s:.4f}")
