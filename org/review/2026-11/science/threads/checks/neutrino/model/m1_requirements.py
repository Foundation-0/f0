"""Task 1: per-system phase-space lower limits and abundance-equivalent masses, dispersion from measured kT (mu = 0.60)."""
import math, csv, numpy as np
from m_sys import *
S = load(); o = opts()
out = []
def P(*a): print(*a); out.append(" ".join(map(str, a)))
rows = []
for s in S:
    d = dict(sample=s.sample, name=s.name, kT=s.kT, T_def=s.r["T_def"], sigma_T=s.sig / 1e3,
             sigma_M500=math.sqrt(G * s.M5 * MSUN / (2 * s.r5 * KPC)) / 1e3)
    e5, b5, t5 = s.extra(s.r5, o); d.update(Mextra500=e5, Mb500=b5, ratio500=e5 / b5, mab500_g2=M_AB_G2 * e5 / b5)
    if s.two:
        d["c500_two_point"] = s.r5 / s.nfw[0]; d["c500_pub"] = s.r["c500_pub"]
        e2, b2, t2 = s.extra(s.r25, o)
        d.update(Mextra2500=e2, Mb2500=b2, ratio2500=e2 / b2, mab2500_g2=M_AB_G2 * e2 / b2, radial_ratio=e5 / e2)
        rho_in = e2 / (4 / 3 * math.pi * s.r25 ** 3)
        rho_sh = (e5 - e2) / (4 / 3 * math.pi * (s.r5 ** 3 - s.r25 ** 3))
        # local extra density at 0.5 r2500 from the profile models (extrapolated inward: flagged)
        rr = 0.5 * s.r25; dr = 0.02 * rr
        rho_loc = (s.extra(rr + dr, o)[0] - s.extra(rr - dr, o)[0]) / (4 * math.pi * rr ** 2 * 2 * dr)
        for lab, rho in [("in2500", rho_in), ("shell", rho_sh), ("local0.5r2500", rho_loc)]:
            for g in (2, 4):
                d[f"mP_{lab}_g{g}"] = m_pauli(rho, s.sig, g) if rho > 0 else float("nan")
                d[f"mTG_{lab}_g{g}"] = m_tg(rho, s.sig, g) if rho > 0 else float("nan")
            d[f"mP_{lab}_g2_sigM500"] = m_pauli(rho, d["sigma_M500"] * 1e3, 2) if rho > 0 else float("nan")
    rows.append(d)
keys = sorted({k for d in rows for k in d}, key=lambda k: (k not in ("sample", "name", "kT"), k))
with open("m1_requirements.csv", "w", newline="") as f:
    w = csv.DictWriter(f, keys); w.writeheader(); [w.writerow(d) for d in rows]
two = [d for d in rows if "Mextra2500" in d]
def q(v): v = np.array([x for x in v if np.isfinite(x)]); return f"min {v.min():.2f}, quartiles {np.percentile(v,25):.2f} {np.median(v):.2f} {np.percentile(v,75):.2f}, max {v.max():.2f} (n={len(v)})"
def trend(lab, key, sub=two):
    x = np.log10([d["kT"] for d in sub if np.isfinite(d.get(key, np.nan))]); y = np.log10([d[key] for d in sub if np.isfinite(d.get(key, np.nan))])
    p = np.polyfit(x, y, 1); P(f"   trend {lab}: log m = {p[1]:.2f} + {p[0]:+.2f} log kT  (r = {np.corrcoef(x,y)[0,1]:+.2f}, n={len(x)})")
P(f"sigma_T/sigma_M500: {q([d['sigma_T']/d['sigma_M500'] for d in rows])}")
P(f"c500 two-point vs published (V06, S09 where given): ratio {q([d['c500_two_point']/d['c500_pub'] for d in two if d.get('c500_pub')])}")
for lab in ["in2500", "shell", "local0.5r2500"]:
    for conv in ["mP", "mTG"]:
        for g in (2, 4):
            P(f"{conv} {lab:13s} g={g}: {q([d[f'{conv}_{lab}_g{g}'] for d in two])}")
    trend(f"mP {lab} g2", f"mP_{lab}_g2")
P(f"first-look convention (sigma from M500), mP in2500 g2: {q([d['mP_in2500_g2_sigM500'] for d in two])}")
P(f"shell extra density negative (extra mass falls outward) in {sum(1 for d in two if d['Mextra500'] < d['Mextra2500'])} of {len(two)} systems")
P(f"abundance-equivalent m (g=2, one species; m = 2.084 eV x M_extra/M_b): r500 {q([d['mab500_g2'] for d in rows])}; r2500 {q([d['mab2500_g2'] for d in two])}")
trend("m_ab r500", "mab500_g2", [d for d in rows if d["mab500_g2"] > 0]); trend("m_ab r2500", "mab2500_g2")
for lo, hi in [(0, 1.5), (1.5, 3), (3, 6), (6, 12)]:
    sub = [d for d in two if lo <= d["kT"] < hi]
    if sub: P(f"kT {lo}-{hi} keV n={len(sub)}: median mP(in2500,g2) {np.median([d['mP_in2500_g2'] for d in sub]):.2f}, m_ab r500 {np.median([d['mab500_g2'] for d in sub]):.2f}, r2500 {np.median([d['mab2500_g2'] for d in sub]):.2f}, radial ratio {np.median([d['radial_ratio'] for d in sub]):.2f}")
open("m1_requirements.out", "w").write("\n".join(out) + "\n")
