"""Which correction sets the level and scatter of the r500 need; and group-property variants for task 4."""
import math, json, numpy as np
from m_sys import *
import m3_fermion_halo as m3
S = m3.S
out = []
def P(*a): print(*a, flush=True); out.append(" ".join(map(str, a)))
P("need M_extra/M_b at r500: median, rms scatter (dex), slope vs log kT; abundance-equivalent m = 2.084 x median (g=2, one thermal species)")
for lab, c in [("none", {}), ("bias 0.10/0.31 only", dict(b2500=0.10, b500=0.31)), ("bias 0.13/0.20 only", dict(b2500=0.13, b500=0.20)),
               ("EFE 0.01 only", dict(ge=0.01)), ("EFE 0.03 only", dict(ge=0.03)), ("EFE 0.05 only", dict(ge=0.05)),
               ("clumping 1.15 + stars 1.9 only", dict(sqrtC=1.15, kstar=1.9)),
               ("bias 0.10/0.31 + EFE 0.01", dict(b2500=0.10, b500=0.31, ge=0.01)), ("bias 0.10/0.31 + EFE 0.03", dict(b2500=0.10, b500=0.31, ge=0.03)),
               ("lensing-high full", m3.SETS["lensing-high"]), ("simulation full", m3.SETS["simulation"]), ("obs-low full", m3.SETS["obs-low"])]:
    o = opts(**c); need = np.array([s.extra(s.r5, o)[0] / s.extra(s.r5, o)[1] for s in S]); kT = np.array([s.kT for s in S]); g = need > 0
    sl = np.polyfit(np.log10(kT[g]), np.log10(need[g]), 1)[0]
    nf = np.mean([s.extra(s.r5, o)[0] >= s.extra(s.r25, o)[0] for s in S])
    P(f"   {lab:30s}: median {np.median(need):5.2f}, scatter {np.std(np.log10(need[g])):.2f} dex (n>0 {g.sum()}), slope {sl:+.2f}, m_ab {M_AB_G2*np.median(need):5.2f} eV; non-falling {nf:.2f}")
P("\ntask 4: required m (g=2, occupation 1/2, lensing-high set) under group-property variants")
o = opts(**m3.SETS["lensing-high"])
def run(lab, mod):
    ms = []
    for s in S:
        sv = s.sig; s.sig = mod(s)
        ms.append(m3.m_needed(s, o, 2, 0.0)); s.sig = sv
    ms = np.array(ms); kT = np.array([s.kT for s in S])
    p = np.polyfit(np.log10(kT), np.log10(ms), 1)
    P(f"   {lab:55s}: median {np.median(ms):.2f}, 95th {np.percentile(ms,95):.2f}, max {ms.max():.2f} eV; slope {p[0]:+.2f} (r={np.corrcoef(np.log10(kT),np.log10(ms))[0,1]:+.2f}); kT<2: {np.median(ms[kT<2]):.2f}, kT>4: {np.median(ms[kT>4]):.2f}")
    return ms
base = run("as measured (sigma from T)", lambda s: s.sig)
run("fermion sigma from 1.3 x T for kT < 2.5 keV (peak of group T profiles)", lambda s: s.sig * (math.sqrt(1.3) if s.kT < 2.5 else 1))
run("fermion sigma from M500 (sqrt(G M500/2 r500)) instead of T", lambda s: math.sqrt(G * s.M5 / (1 - o['b500']) * MSUN / (2 * s.r5 * KPC)))
worst = sorted(zip(base, S), key=lambda t: -t[0])[:6]
P("   most demanding systems: " + "; ".join(f"{s.name} ({s.sample}, kT {s.kT}, m {m:.1f}, need r2500/r500 {s.extra(s.r25,o)[0]:.2e}/{s.extra(s.r5,o)[0]:.2e})" for m, s in worst))
open("m3b_decompose.out", "w").write("\n".join(out) + "\n")
