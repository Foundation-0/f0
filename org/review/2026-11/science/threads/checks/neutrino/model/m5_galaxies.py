"""Tasks 5, 6 and extra item A: largest phase-space-limited fermion halo in galaxies and high-z discs, against the excess;
weak-lensing upper limits at 300 kpc (Mistele+2024 Table 2)."""
import math, csv, pathlib, numpy as np
from m_lib import *
from scipy.optimize import brentq
U = pathlib.Path(__file__).resolve().parents[2] / "gravity2" / "unified" / "unified_table.csv"
rows = list(csv.DictReader(open(U)))
out = []
def P(*a): print(*a, flush=True); out.append(" ".join(map(str, a)))
def rho0(m, g, sig, occ_eta=0.0):
    return g * (m * EV_KG) ** 4 / H ** 3 * (2 * math.pi * sig ** 2) ** 1.5 * float(f32(occ_eta)) / MSUN * KPC ** 3   # Msun/kpc^3
MS = [3, 6, 12, 25]
P("== task 5: upper bound on fermion mass inside r = (4pi/3) r^3 rho0 (density is highest at the centre), g=2, occupation 1/2 (and x(f32(2)/f32(0)) for occupation 0.88)")
P(f"   f32(0) = {float(f32(0)):.3f}, f32(2) = {float(f32(2)):.3f}")
for cls in ["ATLAS3D_Re", "giant_spirals", "SPARC_outer", "SPARC_inner"]:
    sub = [d for d in rows if d["cls"] == cls]
    r = np.array([float(d["r"]) for d in sub]); sg = np.array([float(d["sigma"]) for d in sub]) * 1e3
    Mex = np.array([float(d["M_extraB"]) for d in sub]); Mb = np.array([float(d["Mb"]) for d in sub])
    pos = Mex > 0
    P(f"\n   {cls}: n={len(sub)}, median r {np.median(r):.1f} kpc, sigma {np.median(sg)/1e3:.0f} km/s; excess M_extra>0 in {pos.sum()}; median M_extra/M_b {np.median(Mex/Mb):+.3f}; median positive M_extra {np.median(Mex[pos]):.2e} Msun")
    for m in MS:
        cap = np.array([4 / 3 * math.pi * ri ** 3 * rho0(m, 2, si) for ri, si in zip(r, sg)])
        share = np.clip(cap[pos] / Mex[pos], 0, None)
        P(f"     m={m:2d} eV: bound median {np.median(cap):.2e} Msun; share of the positive excess it can supply: median {np.median(np.minimum(share,1)):.2e}, max {np.max(np.minimum(share,1)):.2e}")
    if cls == "ATLAS3D_Re":
        P(f"     remainder as a stellar M/L change: median log(M_tot/M_N-needed) i.e. 0.5 x? -> stellar M/L must rise by median {np.median(np.log10((Mb[pos]+Mex[pos])/Mb[pos])):.3f} dex (Kroupa baseline) or hot gas of M_extra = {np.median(Mex[pos]/Mb[pos]):.2f} M_b inside R_e")
    if cls == "giant_spirals":
        P(f"     remainder: stellar M/L +{np.median(np.log10((Mb[pos]+Mex[pos])/Mb[pos])):.3f} dex, or hot/undetected gas {np.median(Mex[pos]/Mb[pos]):.2f} M_b inside r")
P("\n== task 6: high-z discs (RC100), same bound inside R_e with sigma = V_c/sqrt2")
sub = [d for d in rows if d["cls"] == "highz_RC100"]
r = np.array([float(d["r"]) for d in sub]); sg = np.array([float(d["sigma"]) for d in sub]) * 1e3
Mt = np.array([float(d["Mtot"]) for d in sub]); Mb = np.array([float(d["Mb"]) for d in sub])
for m in MS:
    cap = np.array([4 / 3 * math.pi * ri ** 3 * rho0(m, 2, si) for ri, si in zip(r, sg)])
    P(f"   m={m:2d} eV: largest fermion share of M_tot inside R_e: median {np.median(cap/Mt):.2e}, max {np.max(cap/Mt):.2e}  (observed f_DM median {np.median(1-Mb/Mt):.2f})")
P("\n== extra item A: Mistele+2024 (arXiv:2406.09685) Table 2, isolated KiDS lenses, V_flat averaged over 50 < R < 300 kpc")
T2 = [("All", 10.10, 137.3, 11.5), ("All", 10.66, 182.1, 10.8), ("All", 10.96, 204.7, 8.2), ("All", 11.29, 260.2, 6.2),
      ("ETG", 10.68, 197.4, 17.7), ("ETG", 10.97, 211.0, 11.3), ("ETG", 11.30, 266.5, 6.7),
      ("LTG", 10.08, 137.4, 11.9), ("LTG", 10.66, 180.1, 13.6), ("LTG", 10.95, 200.5, 11.9), ("LTG", 11.23, 236.1, 15.9)]
R = 300.0
def Mextra_at(V, Mb, ge=0.0):
    gt = (V * 1e3) ** 2 / (R * KPC)
    gN = solve_gN(gt, 1.2e-10, nu_exp, ge * 1.2e-10)
    return gN * (R * KPC) ** 2 / G / MSUN - Mb
P("   bin           logMb   V_flat   M_extra/M_b at 300 kpc: central, 2-sigma upper (V+2err), upper with M_b -0.1 dex | phase-space bound/M_b (m=3,12 eV) | cosmic share m/2.084 (3, 12 eV) | need if g_e=0.01 a0")
for lab, lm, V, e in T2:
    Mb = 10 ** lm
    c = Mextra_at(V, Mb) / Mb; u = Mextra_at(V + 2 * e, Mb) / Mb; u2 = Mextra_at(V + 2 * e, Mb / 10 ** 0.1) / (Mb / 10 ** 0.1)
    sig = V * 1e3 / math.sqrt(2)
    caps = [4 / 3 * math.pi * R ** 3 * rho0(m, 2, sig) / Mb for m in (3, 12)]
    efe = Mextra_at(V, Mb, 0.01) / Mb
    P(f"   {lab} {lm:5.2f}  {V:6.1f}+-{e:4.1f}   {c:+6.2f}  {u:+6.2f}  {u2:+6.2f}   | {caps[0]:.1e} {caps[1]:.1e} | {3/M_AB_G2:.2f} {12/M_AB_G2:.2f} | {efe:+.2f}")
# equilibrium FD halo in a flat-V field (cored isothermal potential, core 5 kpc), occupation 1/2
P("\n   equilibrium halo (occupation 1/2) in a flat-V field Phi = V^2 ln(1+(r/5 kpc)^2)/2, V = 200 km/s: M(<300 kpc)/M_b for M_b = 10^10.96")
for m in (3, 6, 12):
    Vv = 200e3; sig = Vv / math.sqrt(2)
    Mh, rr = halo_mass(300.0, m, 2, sig, lambda r: 0.5 * Vv ** 2 * np.log1p((np.asarray(r) / 5.0) ** 2))
    P(f"     m={m:2d} eV: M_halo(<300 kpc) = {Mh[-1]:.2e} Msun = {Mh[-1]/10**10.96:.2f} M_b")
# relic speeds and capture timescales
Tnu = (4 / 11) ** (1 / 3) * 2.7255 * 8.617333262e-5          # eV
P(f"\n   relic speed: <p> = 3.151 T_nu, T_nu0 = {Tnu:.4e} eV -> <v> = {3.151*Tnu*C/1e3:.1f} (1+z) (1 eV/m) km/s")
for m in (3, 12):
    P(f"     m={m:2d} eV: <v> at z=0,1,2,5,10 = " + ", ".join(f"{3.151*Tnu*C/1e3*(1+z)/m:.0f}" for z in (0, 1, 2, 5, 10)) + " km/s")
V = 200.0; rr = 300.0
P(f"   galaxy at 300 kpc, V=200 km/s: crossing time r/V = {rr*KPC/(V*1e3)/3.156e16:.2f} Gyr; escape speed (flat to 1 Mpc) {V*math.sqrt(2*(1+math.log(1000/rr))):.0f} km/s")
P(f"   cluster at r500=1.2 Mpc, sigma=1000 km/s: crossing {1200*KPC/1e6/3.156e16:.2f} Gyr; escape ~ {1000*math.sqrt(2)*math.sqrt(2*(1+math.log(3))):.0f} km/s")
open("m5_galaxies.out", "w").write("\n".join(out) + "\n")
