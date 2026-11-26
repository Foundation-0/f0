"""Reviewer's own fit to the unified table (separate code from the thread's fitlib).
Law (form B): the extra mass enters the Newtonian source.  g_N = G (M_b + M_extra)/r^2,  g_tot = nu(g_N/a0) g_N,
M_extra = K (sigma/200 km/s)^a (r/100 kpc)^b.  Score: mean over local classes of the mean squared residual in
log10 M_tot, so each class weighs the same.  Also scored: the standard relation alone (K = 0) and three fixed laws."""
import csv, math, sys
import numpy as np
from scipy.optimize import least_squares
G, A0, MSUN, KPC = 6.67430e-11, 1.2e-10, 1.98847e30, 3.085677581491367e19
rows = [r for r in csv.DictReader(open(sys.argv[1])) if r["cls"] != "highz_RC100"]
cls = sorted({r["cls"] for r in rows})
r_ = np.array([float(r["r"]) for r in rows]); Mb = np.array([float(r["Mb"]) for r in rows]); Mt = np.array([float(r["Mtot"]) for r in rows])
sg = np.array([float(r["sigma"]) for r in rows]); c = np.array([cls.index(r["cls"]) for r in rows])
w = np.array([1.0 / math.sqrt(np.sum(c == ci) * len(cls)) for ci in c])
def nu(y):
    s = np.sqrt(np.maximum(y, 1e-30)); return 1.0 / (1.0 - np.exp(-s))
def pred(Mx):
    gN = G * (Mb + Mx) * MSUN / (r_ * KPC) ** 2
    return nu(gN / A0) * (Mb + Mx)
def resid(Mx): return np.log10(Mt) - np.log10(pred(Mx))
def score(Mx): return float(np.sqrt(np.sum((w * resid(Mx)) ** 2)))
def law(p): return 10 ** p[0] * (sg / 200.0) ** p[1] * (r_ / 100.0) ** p[2]
print("rows used:", len(rows), "classes:", {k: int(np.sum(c == i)) for i, k in enumerate(cls)})
print(f"standard relation alone: {score(np.zeros_like(Mb)):.4f} dex")
best = None
for p0 in ([11.5, 4.0, 0.5], [12.0, 3.0, 1.0], [11.0, 5.0, 0.0], [12.5, 2.0, 2.0]):
    f = least_squares(lambda p: w * resid(law(p)), p0)
    s = score(law(f.x))
    if best is None or s < best[0]: best = (s, f.x)
s, p = best
print(f"two-variable law: logK = {p[0]:.3f}, a = {p[1]:.3f}, b = {p[2]:.3f}; score {s:.4f} dex")
for name, a, b in (("fully packed phase space a=3, b=3", 3.0, 3.0), ("isothermal a=2, b=1", 2.0, 1.0)):
    f = least_squares(lambda q: w * resid(10 ** q[0] * (sg / 200.0) ** a * (r_ / 100.0) ** b), [11.5])
    print(f"{name}: logK = {f.x[0]:.3f}; score {score(10 ** f.x[0] * (sg / 200.0) ** a * (r_ / 100.0) ** b):.4f} dex")
f = least_squares(lambda q: w * resid(10 ** q[0] * Mb), [-0.5])
print(f"proportional to baryons: factor {10 ** f.x[0]:.3f}; score {score(10 ** f.x[0] * Mb):.4f} dex")
# bootstrap over systems within class
rng = np.random.default_rng(20261115); A = []; B = []
idx_by = [np.where(c == i)[0] for i in range(len(cls))]
for t in range(200):
    pick = np.concatenate([rng.choice(ix, size=len(ix), replace=True) for ix in idx_by])
    def rr(p_):
        Mx = 10 ** p_[0] * (sg[pick] / 200.0) ** p_[1] * (r_[pick] / 100.0) ** p_[2]
        gN = G * (Mb[pick] + Mx) * MSUN / (r_[pick] * KPC) ** 2
        return w[pick] * (np.log10(Mt[pick]) - np.log10(nu(gN / A0) * (Mb[pick] + Mx)))
    f = least_squares(rr, p); A.append(f.x[1]); B.append(f.x[2])
qa = np.percentile(A, [2.5, 16, 50, 84, 97.5]); qb = np.percentile(B, [2.5, 16, 50, 84, 97.5])
print(f"bootstrap (200): a = {qa[2]:.2f} (68% {qa[1]:.2f} to {qa[3]:.2f}; 95% {qa[0]:.2f} to {qa[4]:.2f}); b = {qb[2]:.2f} (68% {qb[1]:.2f} to {qb[3]:.2f}; 95% {qb[0]:.2f} to {qb[4]:.2f}); corr {np.corrcoef(A, B)[0, 1]:+.2f}")
# per-class bias of the two-variable law and of the standard relation
Mx = law(p)
for i, k in enumerate(cls):
    m = c == i
    print(f"  {k:14s} n={int(m.sum()):3d} median residual: standard {np.median(resid(np.zeros_like(Mb))[m]):+.3f}  two-variable {np.median(resid(Mx)[m]):+.3f}")
