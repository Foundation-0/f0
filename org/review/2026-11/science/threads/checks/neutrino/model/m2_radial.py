"""Task 2: the radial discrepancy. Non-falling = M_extra(r500) >= M_extra(r2500); also checked on a 12-point grid."""
import math, numpy as np
from m_sys import *
S = [s for s in load() if s.two]
out = []
def P(*a): print(*a, flush=True); out.append(" ".join(map(str, a)))
def stats(o, grid=False):
    rat, nf, neg5 = [], 0, 0
    for s in S:
        e2 = s.extra(s.r25, o)[0]; e5 = s.extra(s.r5, o)[0]
        rat.append(e5 / e2 if e2 > 0 else np.nan); neg5 += e5 < 0
        ok = e5 >= e2
        if grid and ok:
            rr = np.geomspace(s.r25, s.r5, 12); ee = [s.extra(x, o)[0] for x in rr]; ok = all(np.diff(ee) >= -1e-6 * abs(ee[0]))
        nf += ok
    return nf / len(S), np.nanmedian(rat), neg5
P(f"systems: {len(S)}; 95% means at least {math.ceil(0.95*len(S))} non-falling")
f, med, neg = stats(opts(), grid=True)
P(f"nominal (no bias, sqrtC 1, no EFE, exp nu, a0 1.2e-10, stars x1.5 in r2500): non-falling {f:.2f} (grid check), median M_extra(r500)/M_extra(r2500) {med:.2f}, negative at r500: {neg}")
per = []
for s in S:
    e2 = s.extra(s.r25, opts())[0]; e5 = s.extra(s.r5, opts())[0]; per.append((s.kT, e5 / e2))
per = np.array(per); P(f"radial ratio vs kT: log-slope fit on positive ratios: {np.polyfit(np.log10(per[per[:,1]>0,0]), np.log10(per[per[:,1]>0,1]),1)[0]:+.2f}; median for kT<2: {np.median(per[per[:,0]<2,1]):.2f}, kT>=4: {np.median(per[per[:,0]>=4,1]):.2f}")
def scan(lab, key, vals, base=None, extra_fn=None):
    P(f"\n-- {lab}")
    first = None
    for v in vals:
        o = opts(**(base or {}))
        if extra_fn: o.update(extra_fn(v))
        else: o[key] = v
        f, med, neg = stats(o)
        P(f"   {key if not extra_fn else 'value'} = {v}: non-falling {f:.2f}, median ratio {med:.2f}, negative at r500 {neg}")
        if first is None and f >= 0.95: first = v
    P(f"   => value giving >= 95% non-falling: {first}")
    return first
scan("(a1) hydrostatic bias at r500, none at r2500 (true = HSE/(1-b))", "b500", [0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5])
scan("(a2) bias with the simulated radial shape b2500 = 0.64 b500 (Nelson+2014: f_nth 0.128 at 0.17 r200m, 0.200 at 0.37 r200m)", None,
     [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], extra_fn=lambda v: dict(b500=v, b2500=0.64 * v))
scan("(a3) bias difference with b2500 = 0.05", "b500", [0.1, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5], base=dict(b2500=0.05))
scan("(b) clumping: sqrt(C) applied to the r2500-r500 shell gas", "sqrtC", [1.0, 1.05, 1.1, 1.2, 1.3, 1.5, 2.0, 3.0])
scan("(c) external field g_e/a0 (1D QUMOND approximation)", "ge", [0, 0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.3, 0.5])
P("\n-- (d) interpolating function x a0")
for nu in NU:
    for a0 in (1.0e-10, 1.2e-10):
        f, med, neg = stats(opts(nu=nu, a0=a0)); P(f"   {nu:10s} a0={a0:.1e}: non-falling {f:.2f}, median ratio {med:.2f}, negative at r500 {neg}")
scan("(e) stars inside r2500 as k x f_star,500 (capped at all r500 stars)", "kstar", [1.0, 1.5, 2.0, 2.5, 3.0, 5.0])
g = np.median([s.extra(s.r25, opts())[1] for s in S])
P("   accelerations: median g_b/a0 at r2500 %.3f, at r500 %.3f; median g_tot/a0 at r500 %.3f" % (
    np.median([G * s.extra(s.r25, opts())[1] * MSUN / (s.r25 * KPC) ** 2 / 1.2e-10 for s in S]),
    np.median([G * s.extra(s.r5, opts())[1] * MSUN / (s.r5 * KPC) ** 2 / 1.2e-10 for s in S]),
    np.median([G * s.M5 * MSUN / (s.r5 * KPC) ** 2 / 1.2e-10 for s in S])))
P("\n-- combinations at published sizes")
COMBOS = {
 "obs-low (X-COP f_nth 6% at r500, ~3% at r2500; sqrtC 1.03; g_e 0.01 a0; stars x1.5)": dict(b2500=0.03, b500=0.06, sqrtC=1.03, ge=0.01, kstar=1.5),
 "simulation (Nelson+14 0.13/0.20; sqrtC 1.10; g_e 0.03 a0; stars x1.6)": dict(b2500=0.13, b500=0.20, sqrtC=1.10, ge=0.03, kstar=1.6),
 "lensing-high (WtG 1-b=0.69 at r500, 0.10 at r2500; sqrtC 1.15; g_e 0.05 a0; stars x1.9)": dict(b2500=0.10, b500=0.31, sqrtC=1.15, ge=0.05, kstar=1.9),
 "lensing-high bias alone": dict(b2500=0.10, b500=0.31),
 "LoCuSS-like (X-ray/lensing 0.95 at r500: b500 0.05, b2500 0.02) + simulation clumping/EFE/stars": dict(b2500=0.02, b500=0.05, sqrtC=1.10, ge=0.03, kstar=1.6),
}
import json
for k, o in COMBOS.items():
    f, med, neg = stats(opts(**o), grid=True); P(f"   {k}: non-falling {f:.2f} (grid), median ratio {med:.2f}, negative at r500 {neg}")
json.dump(COMBOS, open("m2_combos.json", "w"), indent=1)
open("m2_radial.out", "w").write("\n".join(out) + "\n")
