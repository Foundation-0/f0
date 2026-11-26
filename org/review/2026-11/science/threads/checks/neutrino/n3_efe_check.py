"""Check of the external-field lever, with the field stated unambiguously.

The 1D formula (Famaey & McGaugh 2012):  g_int = nu((gN + gNe)/a0) (gN + gNe) - nu(gNe/a0) gNe,
where gNe is the NEWTONIAN external field. The physical (true) external field felt by the system is
g_ext = nu(gNe/a0) gNe.  A physical field of 0.03 a0 corresponds to gNe of about 0.0009 a0, not 0.03 a0.
The earlier halo study passed 0.01, 0.03, 0.05 a0 as gNe. Those are physical fields of about 0.10, 0.19, 0.25 a0.

Here the field is given as the PHYSICAL g_ext, converted to gNe, and the cluster analysis is repeated:
share of systems whose enclosed extra mass does not fall between r2500 and r500, the median and scatter of
M_extra/M_b inside r500, and the abundance-equivalent mass. Hydrostatic bias (b2500, b500) can be added."""
import csv, math, sys
import numpy as np
from scipy.optimize import brentq
G, A0, MSUN, KPC = 6.67430e-11, 1.2e-10, 1.98847e30, 3.085677581491367e19
rows = [r for r in csv.DictReader(open(sys.argv[1])) if r["cls"].startswith("GC_")]
by = {}
for r in rows: by.setdefault(r["name"], {})[r["cls"]] = r
both = [d for d in by.values() if "GC_r2500" in d and "GC_r500" in d]
nu = lambda y: 1.0 / (1.0 - math.exp(-math.sqrt(y)))
def gNe_of(gext):            # gext in units of a0 (physical); returns Newtonian external field in m/s^2
    if gext <= 0: return 0.0
    return A0 * 10 ** brentq(lambda ly: math.log10(nu(10 ** ly) * 10 ** ly) - math.log10(gext), -12, 2)
def g_int(gN, gNe):
    if gNe <= 0: return nu(gN / A0) * gN
    return nu((gN + gNe) / A0) * (gN + gNe) - nu(gNe / A0) * gNe
def extra(Mtot, Mb, r_kpc, gNe):
    gt = G * Mtot * MSUN / (r_kpc * KPC) ** 2
    gN = 10 ** brentq(lambda lg: math.log(g_int(10 ** lg, gNe)) - math.log(gt), -18, math.log10(gt) + 0.5)
    return gN * (r_kpc * KPC) ** 2 / G / MSUN - Mb
print("physical g_ext/a0 -> Newtonian gNe/a0:", ", ".join(f"{x} -> {gNe_of(x)/A0:.5f}" for x in (0.01, 0.02, 0.03, 0.05, 0.10, 0.19, 0.25)))
print("typical baryonic g_N/a0: r2500 median", np.median([float(d['GC_r2500']['g_b']) for d in both]) / A0, " r500 median", np.median([float(d['GC_r500']['g_b']) for d in both]) / A0)
print(f"\n{'g_ext':>6} {'b2500':>5} {'b500':>5} | {'non-falling':>11} {'ratio med':>9} | {'y500 med':>8} {'scatter dex':>11} {'m_A500 eV':>9} | {'y2500 med':>9} | {'neg r500':>8}")
for gext in (0.0, 0.01, 0.02, 0.03, 0.05, 0.10, 0.25):
    for (b2, b5) in ((0.0, 0.0), (0.03, 0.06), (0.05, 0.20), (0.10, 0.31)):
        gNe = gNe_of(gext); rat = []; y5 = []; y2 = []; neg = 0
        for d in both:
            a, b = d["GC_r500"], d["GC_r2500"]
            x5 = extra(float(a["Mtot"]) / (1 - b5), float(a["Mb"]), float(a["r"]), gNe); x2 = extra(float(b["Mtot"]) / (1 - b2), float(b["Mb"]), float(b["r"]), gNe)
            if x5 <= 0: neg += 1
            if x2 > 0: rat.append(x5 / x2)
            y5.append(x5 / float(a["Mb"])); y2.append(x2 / float(b["Mb"]))
        pos = np.array([v for v in y5 if v > 0]); sc = np.std(np.log10(pos)) if len(pos) > 5 else float("nan")
        print(f"{gext:6.2f} {b2:5.2f} {b5:5.2f} | {np.mean(np.array(rat) >= 1):11.2f} {np.median(rat):9.2f} | {np.median(y5):8.2f} {sc:11.2f} {2.084*np.median(y5):9.2f} | {np.median(y2):9.2f} | {neg:8d}")
