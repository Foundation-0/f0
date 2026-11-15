"""Where could one fermion species sit?  Two numbers per correction set, then a two-parameter map.

A = abundance-equivalent mass: 2.084 eV * (M_extra/M_b inside r500), for the whole sample and for the richest
    clusters (dispersion >= 900 km/s), which are the closest to closed boxes.  For a species of mass m populated at a
    fraction chi of the thermal relic number,  chi * m = A / phi,  phi <= 1 the share of the cosmic supply the
    cluster holds inside r500.
K = phase-space scale: cluster cores need  chi * m^4 >= K_lo^4  (K_lo from the halo model: the mass a fully
    thermal species needs so that 95% of systems can hold their extra mass), and galaxy lensing allows
    chi * m^4 <= K_hi^4  (K_hi from the halo model: 10.4 to 13.4 eV for a 5 kpc core; 7.4 to 21 eV for 2 to 10 kpc).
Early-universe load: Delta N_eff ~ chi for a species at the neutrino temperature.  Omega h^2 = chi m / 93.14 eV.
For phi = 1 (closed box) the solution is  chi = (A/K)^(4/3),  m = K (K/A)^(1/3)."""
import contextlib, io, math, sys
import numpy as np
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
with contextlib.redirect_stdout(io.StringIO()):   # n3_efe_check prints its own table on import
    import n3_efe_check as e
out = []
def P(s=""): print(s); out.append(s)
SETS = [(0.00, 0.00, 0.00, "none"), (0.01, 0.03, 0.06, "observation-low"), (0.03, 0.05, 0.20, "middle"),
        (0.03, 0.13, 0.20, "simulation bias"), (0.03, 0.10, 0.31, "lensing-high bias"), (0.05, 0.10, 0.31, "lensing-high bias, strong field")]
KS = (8.0, 10.4, 13.4, 15.6)
res = []
for gext, b2, b5, lab in SETS:
    gNe = e.gNe_of(gext); y = []; sg = []
    for d in e.both:
        a = d["GC_r500"]
        y.append(e.extra(float(a["Mtot"]) / (1 - b5), float(a["Mb"]), float(a["r"]), gNe) / float(a["Mb"])); sg.append(float(a["sigma"]))
    y = np.array(y); sg = np.array(sg)
    pos = y > 0
    slope = np.polyfit(np.log10(sg[pos]), np.log10(y[pos]), 1)[0]
    res.append((gext, b2, b5, lab, 2.084 * np.median(y), 2.084 * np.median(y[sg < 500]), 2.084 * np.median(y[(sg >= 500) & (sg < 900)]),
                2.084 * np.median(y[sg >= 900]), slope, int((sg >= 900).sum())))
P("Abundance-equivalent mass A = 2.084 eV x M_extra/M_b inside r500 (median), by physical external field and bias")
P(f"{'g_ext':>6} {'b2500':>5} {'b500':>5} | {'all 51':>7} {'sigma<500':>9} {'500-900':>8} {'>=900 (6)':>9} | slope of log ratio vs log sigma")
for r in res:
    P(f"{r[0]:6.2f} {r[1]:5.2f} {r[2]:5.2f} | {r[4]:7.2f} {r[5]:9.2f} {r[6]:8.2f} {r[7]:9.2f} | {r[8]:+.2f}   [{r[3]}]")
P()
P("Solutions for a closed box (phi = 1): chi = (A/K)^(4/3), m = K (K/A)^(1/3); Delta N_eff ~ chi; Omega h^2 = A/93.14")
P(f"{'correction set':<35} {'A used':>6} | " + " | ".join(f"K={K:>4g}: m, chi" for K in KS))
for r in res:
    for sub, A in (("all", r[4]), ("richest", r[7])):
        cells = []
        for K in KS:
            chi = (A / K) ** (4 / 3)
            cells.append(f"chi>1 ({chi:.2f})" if chi > 1 else f"{K * (K / A) ** (1 / 3):.1f} eV, {chi:.2f}")
        P(f"{r[3] + ' / ' + sub:<34} {A:7.2f} | " + " | ".join(f"{c:>15}" for c in cells) + f" | Omega h2 {A / 93.14:.3f}")
open(__import__("pathlib").Path(__file__).with_suffix(".out"), "w").write("\n".join(out) + "\n")
