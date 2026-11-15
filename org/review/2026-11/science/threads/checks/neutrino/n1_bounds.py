"""First look: what would a fermion have to be, system by system, to supply the extra mass in groups and clusters?
Uses the unified table (form B extra mass). Two separate requirements on one species of mass m with g spin states:
  (P) phase space: the mean extra density inside a radius cannot exceed the Pauli limit for a Maxwellian of
      dispersion sigma:  rho <= g m^4 (2 pi sigma^2)^(3/2) / h^3.   So m >= m_P(rho, sigma).
      (The Tremaine-Gunn bound for a relic is a factor 2 tighter in density: m_TG = 2^(1/4) m_P.)
      Mean densities understate central ones, so these are lower limits on m.
  (A) abundance: a species with the full thermal relic number density has Omega h^2 = m / 93.14 eV. If a cluster
      held the cosmic share inside the radius, M_extra/M_b = (m/93.14)/0.02237. So the ratio gives the mass
      'in eV of thermal relic' the cluster holds:  m_A = 2.084 eV * M_extra/M_b.
A single species must satisfy m >= max m_P and, if the cluster is a fair sample at that radius, m ~ m_A."""
import csv, math, sys, statistics as st
G, MSUN, KPC, H, EV = 6.67430e-11, 1.98847e30, 3.085677581491367e19, 6.62607015e-34, 1.78266192e-36
rows = [r for r in csv.DictReader(open(sys.argv[1])) if r["cls"].startswith("GC_")]
by = {}
for r in rows: by.setdefault(r["name"], {})[r["cls"]] = r
def mP(rho, sig_kms, g=2):
    return (rho * H ** 3 / (g * (2 * math.pi * (sig_kms * 1e3) ** 2) ** 1.5)) ** 0.25 / EV
out = []
for name, d in by.items():
    if "GC_r500" not in d: continue
    a = d["GC_r500"]; s = float(a["sigma"]); r5 = float(a["r"]); x5 = float(a["M_extraB"]); mb5 = float(a["Mb"])
    rec = dict(name=name, sigma=s, y500=x5 / mb5, mA500=2.084 * x5 / mb5)
    if x5 > 0: rec["mP500"] = mP(3 * x5 * MSUN / (4 * math.pi * (r5 * KPC) ** 3), s)
    if "GC_r2500" in d:
        b = d["GC_r2500"]; r2 = float(b["r"]); x2 = float(b["M_extraB"]); mb2 = float(b["Mb"])
        rec.update(y2500=x2 / mb2, mA2500=2.084 * x2 / mb2, ratio_x=(x5 / x2 if x2 > 0 else float("nan")), ratio_r=r5 / r2, ratio_b=mb5 / mb2)
        if x2 > 0: rec["mP2500"] = mP(3 * x2 * MSUN / (4 * math.pi * (r2 * KPC) ** 3), s)
        if x5 > x2 > 0: rec["mPshell"] = mP(3 * (x5 - x2) * MSUN / (4 * math.pi * ((r5 * KPC) ** 3 - (r2 * KPC) ** 3)), s)
    out.append(rec)
def q(v): 
    v = sorted(v); n = len(v); return f"min {v[0]:.2f}, quartiles {v[n//4]:.2f} {v[n//2]:.2f} {v[(3*n)//4]:.2f}, max {v[-1]:.2f} (n={n})"
print("systems:", len(out), " with both radii:", sum(1 for r in out if "y2500" in r))
for key, label in (("mP2500", "phase-space lower limit on m from the mean density inside r2500 [eV], g=2"), ("mPshell", "same, shell between r2500 and r500"), ("mP500", "same, mean inside r500"),
                   ("mA2500", "abundance: thermal-relic eV held inside r2500"), ("mA500", "abundance: thermal-relic eV held inside r500"), ("y500", "M_extra/M_b inside r500"), ("ratio_x", "M_extra(r500)/M_extra(r2500)"), ("ratio_b", "M_b(r500)/M_b(r2500)"), ("ratio_r", "r500/r2500")):
    v = [r[key] for r in out if key in r and r[key] == r[key] and r[key] > 0]
    print(f"{label}: {q(v)}")
print("negative extra mass (below the standard relation): inside r2500:", sum(1 for r in out if "y2500" in r and r["y2500"] <= 0), "; inside r500:", sum(1 for r in out if r["y500"] <= 0))
# trends with sigma
import numpy as np
for key in ("mP2500", "mA500", "mA2500"):
    v = [(math.log10(r["sigma"]), math.log10(r[key])) for r in out if key in r and r[key] > 0]
    x, y = np.array(v).T; b, a = np.polyfit(x, y, 1); rr = np.corrcoef(x, y)[0, 1]
    print(f"trend: log {key} = {a:.2f} + {b:.2f} log sigma (r = {rr:+.2f}, n = {len(v)})")
for lo, hi in ((250, 400), (400, 600), (600, 900), (900, 1400)):
    sel = [r for r in out if lo <= r["sigma"] < hi and "mP2500" in r]
    if sel: print(f"sigma {lo}-{hi}: n={len(sel)}  median m_P(r2500) {st.median(r['mP2500'] for r in sel):.2f} eV, max {max(r['mP2500'] for r in sel):.2f};  median m_A(r500) {st.median(r['mA500'] for r in sel):.2f}, m_A(r2500) {st.median(r['mA2500'] for r in sel):.2f}; median extra ratio r500/r2500 {st.median(r['ratio_x'] for r in sel):.2f} vs baryons {st.median(r['ratio_b'] for r in sel):.2f}")
