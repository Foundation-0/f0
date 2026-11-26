"""Task 3: largest equilibrium Fermi-Dirac halo each cluster can hold, in its measured (bias-corrected) field.
Isothermal FD gas, dispersion sigma^2 = kT/(mu m_p), central occupation 1/2 (eta0 = 0, the fine-grained maximum of a
thermal relic; Tremaine-Gunn) or 0.88 (eta0 = 2, for a non-thermal species near the Pauli limit)."""
import math, json, numpy as np
from m_sys import *
from m_lib import *
S = [s for s in load() if s.two]
COMBOS = json.load(open("m2_combos.json"))
SETS = {"nominal (no corrections)": {}, "obs-low": COMBOS[list(COMBOS)[0]], "simulation": COMBOS[list(COMBOS)[1]],
        "lensing-high": COMBOS[list(COMBOS)[2]]}
out = []
def P(*a): print(*a, flush=True); out.append(" ".join(map(str, a)))
def field(s, o):
    """NFW through the bias-corrected masses at r2500 and r500"""
    return nfw_two_point(s.r25, s.M25 / (1 - o["b2500"]), s.r5, s.M5 / (1 - o["b500"]))
def max_halo(s, o, m, g, eta0):
    rs, rhos = field(s, o)
    dphi = lambda r: nfw_dphi(r, rs, rhos)
    Mh, r = halo_mass(s.r5 * 1.0001, m, g, s.sig, dphi, eta0)
    return float(np.interp(s.r25, r, Mh)), float(np.interp(s.r5, r, Mh))
def m_needed(s, o, g, eta0):
    e2 = s.extra(s.r25, o)[0]; e5 = s.extra(s.r5, o)[0]
    need2, need5 = max(e2, 0), max(e5, 0)
    lo, hi = 0.1, 100.0
    for _ in range(40):
        mid = math.sqrt(lo * hi); h2, h5 = max_halo(s, o, mid, g, eta0)
        if h2 >= need2 and h5 >= need5: hi = mid
        else: lo = mid
    return hi
if __name__ != "__main__": SETS_ONLY = True
if __name__ == '__main__':
    res = {}
    for setname, corr in SETS.items():
        o = opts(**corr)
        P(f"\n== correction set: {setname} {corr}")
        for g, eta0 in [(2, 0.0), (4, 0.0), (2, 2.0)]:
            ms = np.array([m_needed(s, o, g, eta0) for s in S]); kT = np.array([s.kT for s in S])
            p = np.polyfit(np.log10(kT), np.log10(ms), 1)
            P(f"   g={g} occupation {1/(1+math.exp(-eta0)):.2f}: m needed per system: min {ms.min():.2f}, median {np.median(ms):.2f}, 95th pct {np.percentile(ms,95):.2f}, max {ms.max():.2f} eV "
              f"[{S[int(np.argmax(ms))].name}, kT {kT[np.argmax(ms)]:.2f}]; trend log m = {p[1]:.2f} {p[0]:+.2f} log kT (r={np.corrcoef(np.log10(kT),np.log10(ms))[0,1]:+.2f})")
            res[(setname, g, eta0)] = ms
        # abundance: predicted ratio at r500 = min(cosmic, phase-space cap); compare with need
        need = np.array([s.extra(s.r5, o)[0] / s.extra(s.r5, o)[1] for s in S])
        P("   abundance test at r500 (g=2, occupation 1/2): predicted M_h/M_b = min(f m/2.084, cap(m)); score = rms of log(pred/need) over systems with need>0")
        good = need > 0
        for lab, f_sp in [("one species, fully thermal (Omega h^2 = m/93.14)", 1.0), ("g=4 equivalent / two species (x2)", 2.0), ("three species (x3)", 3.0), ("half-thermalised (x0.5)", 0.5)]:
            best = None; table = []
            for m in [1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 10, 11, 12, 15, 20, 25, 30]:
                cap = np.array([max_halo(s, o, m, 2, 0.0)[1] / s.extra(s.r5, o)[1] for s in S])
                pred = np.minimum(f_sp * m / M_AB_G2, cap)
                sc = float(np.sqrt(np.mean(np.log10(pred[good] / need[good]) ** 2)))
                capped = int(np.sum(cap[good] < f_sp * m / M_AB_G2))
                corr_ = np.corrcoef(np.log10(pred[good]), np.log10(need[good]))[0, 1] if np.std(np.log10(pred[good])) > 0 else float("nan")
                table.append((m, sc, capped, corr_, float(np.median(np.log10(pred[good] / need[good])))))
                if best is None or sc < best[1]: best = table[-1]
            ok = [t[0] for t in table if t[1] <= best[1] + 0.05]
            P(f"     {lab}: best m = {best[0]} eV, rms {best[1]:.3f} dex, capped by phase space in {best[2]}/{good.sum()} systems, corr(pred,need) {best[3]:+.2f}; m within +0.05 dex of best: {ok}")
            P("        " + " ".join(f"{t[0]}:{t[1]:.2f}/{t[2]}/{t[4]:+.2f}" for t in table))
        P(f"   need M_extra/M_b at r500: median {np.median(need):.2f}; vs kT slope {np.polyfit(np.log10([s.kT for s in np.array(S)[good]]), np.log10(need[good]),1)[0]:+.2f}; richest (kT>6) median {np.median(need[[s.kT>6 for s in S]]):.2f}")
if __name__ == '__main__':
    json.dump({f"{k[0]}|g{k[1]}|eta{k[2]}": v.tolist() for k, v in res.items()}, open("m3_needed_m.json", "w"))
    # core radius scaling (item B): King radius r0 = sqrt(9 sigma^2/(4 pi G rho0)), rho0 = g m^4 (2 pi sigma^2)^1.5 f32(0)/h^3
    P("\n== core radius of the phase-space-limited halo (King radius, self-gravity only), g=2, occupation 1/2")
    for m in (2, 3, 5, 11):
        for kT in (1, 3, 8):
            sg = sigma_T(kT); rho0 = 2 * (m * EV_KG) ** 4 / H ** 3 * (2 * math.pi * sg ** 2) ** 1.5 * float(f32(0))
            P(f"   m={m:2d} eV kT={kT} keV: rho0 = {rho0/MSUN*KPC**3:.2e} Msun/kpc^3, r0 = {math.sqrt(9*sg**2/(4*math.pi*G*rho0))/KPC:.0f} kpc   (r0 ~ m^-2 kT^-1/4)")
    open("m3_fermion_halo.out", "w").write("\n".join(out) + "\n")
