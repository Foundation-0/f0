"""A law that uses baryons only, so it cannot be circular: M_extra = K (M_b / 1e11 Msun)^p (form B).
Questions: (1) K, p and their bootstrap ranges; (2) does a law fitted on clusters alone predict the offsets seen in
galaxies, and the reverse; (3) is a threshold in baryonic mass preferred over the smooth power law;
(4) what the law predicts for the high-redshift class with no refitting."""
import csv, math, sys
import numpy as np
from scipy.optimize import least_squares
G, A0, MSUN, KPC = 6.67430e-11, 1.2e-10, 1.98847e30, 3.085677581491367e19
allrows = list(csv.DictReader(open(sys.argv[1])))
def arrs(rows):
    return (np.array([float(r["r"]) for r in rows]), np.array([float(r["Mb"]) for r in rows]), np.array([float(r["Mtot"]) for r in rows]))
nu = lambda y: 1.0 / (1.0 - np.exp(-np.sqrt(np.maximum(y, 1e-30))))
def resid(r_, Mb, Mt, Mx):
    Mn = np.maximum(Mb + Mx, 1e-3 * Mb); gN = G * Mn * MSUN / (r_ * KPC) ** 2
    return np.log10(Mt) - np.log10(nu(gN / A0) * Mn)
local = [r for r in allrows if r["cls"] != "highz_RC100"]; cls = sorted({r["cls"] for r in local})
r_, Mb, Mt = arrs(local); c = np.array([cls.index(r["cls"]) for r in local])
def weights(mask): 
    k = len({ci for ci in c[mask]}); return np.array([1.0 / math.sqrt(np.sum((c == ci) & mask) * k) for ci in c[mask]])
def fit(mask, form="power"):
    w = weights(mask)
    if form == "power":
        f = least_squares(lambda q: w * resid(r_[mask], Mb[mask], Mt[mask], 10 ** q[0] * (Mb[mask] / 1e11) ** q[1]), [10.3, 1.3])
    else:   # threshold in baryonic mass: M_extra = R M_b max(0, 1 - (M_J/M_b)^(1/2))
        best = None
        for mj in np.arange(9.0, 12.6, 0.1):
            g = least_squares(lambda q: w * resid(r_[mask], Mb[mask], Mt[mask], 10 ** q[0] * Mb[mask] * np.maximum(0, 1 - np.sqrt(10 ** mj / Mb[mask]))), [0.0])
            s = float(np.sqrt(np.sum(g.fun ** 2)))
            if best is None or s < best[0]: best = (s, mj, g.x[0])
        return best
    return f.x, float(np.sqrt(np.sum(f.fun ** 2)))
allm = np.ones(len(local), bool)
(q, s) = fit(allm); print(f"all local classes: M_extra = 10^{q[0]:.3f} (M_b/1e11)^{q[1]:.3f} Msun; score {s:.4f} dex (standard relation alone 0.1895)")
print(f"   ratio M_extra/M_b at M_b = 1e9, 1e10, 1e11, 1e12, 1e13, 1e14: " + ", ".join(f"{10**q[0]*(m/1e11)**q[1]/m:.3f}" for m in (1e9,1e10,1e11,1e12,1e13,1e14)))
th = fit(allm, "threshold"); print(f"threshold in baryonic mass (same number of parameters): best log M_J = {th[1]:.1f}, R = {10**th[2]:.2f}; score {th[0]:.4f} dex")
rng = np.random.default_rng(11); P = []; K = []
idx_by = [np.where(c == i)[0] for i in range(len(cls))]
for t in range(300):
    pick = np.concatenate([rng.choice(ix, size=len(ix), replace=True) for ix in idx_by])
    w = np.array([1.0 / math.sqrt(len(idx_by[c[i]]) * len(cls)) for i in pick])
    f = least_squares(lambda z: w * resid(r_[pick], Mb[pick], Mt[pick], 10 ** z[0] * (Mb[pick] / 1e11) ** z[1]), q); K.append(f.x[0]); P.append(f.x[1])
pp = np.percentile(P, [2.5, 16, 50, 84, 97.5]); kk = np.percentile(K, [2.5, 50, 97.5])
print(f"bootstrap (300): p = {pp[2]:.3f} (68% {pp[1]:.3f} to {pp[3]:.3f}; 95% {pp[0]:.3f} to {pp[4]:.3f}); log K = {kk[1]:.3f} (95% {kk[0]:.3f} to {kk[2]:.3f}); share of resamples with p <= 1: {np.mean(np.array(P) <= 1):.3f}")
is_cl = np.array([k.startswith("GC_") for k in cls])[c]
for label, train in (("fit on clusters only", is_cl), ("fit on galaxies only", ~is_cl)):
    (qq, ss) = fit(train)
    print(f"{label}: log K = {qq[0]:.3f}, p = {qq[1]:.3f}")
    for i, k in enumerate(cls):
        m = c == i
        rs = resid(r_[m], Mb[m], Mt[m], 10 ** qq[0] * (Mb[m] / 1e11) ** qq[1]); r0 = resid(r_[m], Mb[m], Mt[m], 0 * Mb[m])
        tag = "trained" if train[m][0] else "PREDICTED"
        print(f"     {k:14s} {tag:9s} median residual: standard {np.median(r0):+.3f} -> law {np.median(rs):+.3f}; rms {np.sqrt(np.mean(r0**2)):.3f} -> {np.sqrt(np.mean(rs**2)):.3f}")
hz = [r for r in allrows if r["cls"] == "highz_RC100"]; rh, Mbh, Mth = arrs(hz)
r0 = resid(rh, Mbh, Mth, 0 * Mbh); r1 = resid(rh, Mbh, Mth, 10 ** q[0] * (Mbh / 1e11) ** q[1])
print(f"high redshift (100 galaxies, no refit): median residual standard {np.median(r0):+.3f}, law {np.median(r1):+.3f}; rms {np.sqrt(np.mean(r0**2)):.3f} -> {np.sqrt(np.mean(r1**2)):.3f}")
