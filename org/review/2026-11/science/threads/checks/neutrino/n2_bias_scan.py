"""How do the three cluster discrepancies move if hydrostatic masses are biased low, by different amounts at the
two radii?  True mass = hydrostatic mass / (1 - b).  For each (b2500, b500): recompute the form-B extra mass and
report (1) the share of systems where the enclosed extra mass does not fall between r2500 and r500,
(2) the phase-space lower limit on m from the mean density inside r2500 (Pauli, g = 2), sample maximum and trend,
(3) the abundance-equivalent mass m_A = 2.084 eV * M_extra/M_b inside r500, median and for the richest clusters."""
import csv, math, sys
import numpy as np
from scipy.optimize import brentq
G, A0, MSUN, KPC, H, EV = 6.67430e-11, 1.2e-10, 1.98847e30, 3.085677581491367e19, 6.62607015e-34, 1.78266192e-36
rows = [r for r in csv.DictReader(open(sys.argv[1])) if r["cls"].startswith("GC_")]
by = {}
for r in rows: by.setdefault(r["name"], {})[r["cls"]] = r
nu = lambda y: 1.0 / (1.0 - math.exp(-math.sqrt(y)))
def extra(Mtot, Mb, r_kpc):
    gt = G * Mtot * MSUN / (r_kpc * KPC) ** 2
    f = lambda lg: nu(10 ** lg / A0) * 10 ** lg - gt
    gN = 10 ** brentq(f, -16, -6)
    return gN * (r_kpc * KPC) ** 2 / G / MSUN - Mb
def mP(rho, sig, g=2): return (rho * H ** 3 / (g * (2 * math.pi * (sig * 1e3) ** 2) ** 1.5)) ** 0.25 / EV if rho > 0 else float("nan")
both = [d for d in by.values() if "GC_r2500" in d and "GC_r500" in d]
print(f"systems with both radii: {len(both)}")
print(f"{'b2500':>6} {'b500':>5} | {'non-falling':>11} {'median ratio':>12} | {'m_P max':>8} {'slope':>6} | {'m_A500 med':>10} {'rich':>6} {'m_A2500 rich':>12} | {'neg at r500':>11}")
for b2 in (0.0, 0.05, 0.10, 0.15):
    for b5 in (0.0, 0.10, 0.20, 0.30, 0.40):
        if b5 < b2: continue
        rat = []; mp = []; sg = []; mA = []; mArich = []; mA2rich = []; neg = 0
        for d in both:
            a, b = d["GC_r500"], d["GC_r2500"]; s = float(a["sigma"])
            x5 = extra(float(a["Mtot"]) / (1 - b5), float(a["Mb"]), float(a["r"])); x2 = extra(float(b["Mtot"]) / (1 - b2), float(b["Mb"]), float(b["r"]))
            if x5 <= 0: neg += 1
            if x2 > 0: rat.append(x5 / x2); mp.append(mP(3 * x2 * MSUN / (4 * math.pi * (float(b["r"]) * KPC) ** 3), s)); sg.append(s)
            mA.append(2.084 * x5 / float(a["Mb"]))
            if s >= 900: mArich.append(2.084 * x5 / float(a["Mb"])); mA2rich.append(2.084 * x2 / float(b["Mb"]))
        slope = np.polyfit(np.log10(sg), np.log10(mp), 1)[0]
        print(f"{b2:6.2f} {b5:5.2f} | {np.mean(np.array(rat) >= 1):11.2f} {np.median(rat):12.2f} | {max(mp):8.2f} {slope:6.2f} | {np.median(mA):10.2f} {np.median(mArich):6.2f} {np.median(mA2rich):12.2f} | {neg:11d}")
