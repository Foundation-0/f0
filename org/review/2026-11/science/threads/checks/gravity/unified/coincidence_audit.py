"""Part 3: honest ranges for the four ~185 km/s scales of claim C-27, and the chance of such a coincidence.
Collapse scale and cooling scale use the repository's own code (copied to repo_copy/, unmodified) with varied conventions."""
import sys, math, pathlib, itertools, json
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE / "repo_copy"))
import wave10_covariant_jeans_unification as w
out = []
def P(*a): print(*a); out.append(" ".join(map(str, a)))
G, MSUN, MPC = w.G, w.M_SUN, w.MPC
sigR, D = w.build_eh98_power_spectrum()
rho_m0 = w.OMEGA_M * w.RHO_CRIT0
def Rstar(dc, s8fac=1.0):
    lo, hi = 1e-3, 30.0
    for _ in range(60):
        mid = math.sqrt(lo * hi)
        if sigR(mid) * s8fac > dc: lo = mid
        else: hi = mid
    return math.sqrt(lo * hi)
P("== (a) collapse scale sigma_*(z=0) under conventions (repository code for sigma(R); Planck 2018 EH98)")
OmM = w.OMEGA_M; x = OmM - 1
Dvir = 18 * math.pi ** 2 + 82 * x - 39 * x * x        # Bryan & Norman 1998, w.r.t. rho_crit
coll = {}
for dcn, dc in [("delta_c=1.686 (spherical, repo)", 1.686), ("sqrt(a) delta_c=1.418 (Sheth-Tormen a=0.707)", 1.686 * math.sqrt(0.707))]:
    for s8n, s8 in [("sigma8=0.811", 1.0), ("sigma8=0.78 (low-S8 lensing)", 0.78 / 0.8111)]:
        Rs = Rstar(dc, s8); Ms = 4 / 3 * math.pi * (Rs * MPC) ** 3 * rho_m0
        for mdn, Delta in [("M*=M200c (repo)", 200.0), ("M*=Mvir (Delta_c=%.0f)" % Dvir, Dvir), ("M*=M200m", 200 * OmM)]:
            r = (3 * Ms / (4 * math.pi * Delta * w.RHO_CRIT0)) ** (1 / 3); V = math.sqrt(G * Ms / r) / 1e3
            for cvn, s in [("V/sqrt2 (repo)", V / math.sqrt(2)),
                           ("Evrard+2008 sigma_DM(M200c)", 1082.9 * (w.H_LITTLE * Ms / MSUN / 1e15) ** 0.3361 if mdn.startswith("M*=M200c") else None)]:
                if s is None: continue
                coll[(dcn, s8n, mdn, cvn)] = s
for k, v in sorted(coll.items(), key=lambda t: t[1]):
    P(f"  {v:7.1f} km/s  | {k[0]}; {k[1]}; {k[2]}; {k[3]}")
cv = np.array(list(coll.values()))
P(f"  range {cv.min():.0f} - {cv.max():.0f} km/s over {len(cv)} convention sets (repo value {coll[('delta_c=1.686 (spherical, repo)','sigma8=0.811','M*=M200c (repo)','V/sqrt2 (repo)')]:.2f})")
P("\n== (b) (G M_b a0)^(1/4) for the knee of the galaxy mass function")
def vbtf(M, a0=1.2e-10): return (G * M * MSUN * a0) ** 0.25 / 1e3
for lm in [10.5, 10.66, 10.78, 10.9, 11.0, 11.1]:
    P(f"  log M_b = {lm:5.2f}: V = {vbtf(10**lm):6.1f} km/s  (a0 1.0-1.44: {vbtf(10**lm,1.0e-10):.1f}-{vbtf(10**lm,1.44e-10):.1f}); V/sqrt2 = {vbtf(10**lm)/math.sqrt(2):.1f}")
P("  knee range adopted: log M_b 10.6-11.1 (stellar knee 10.6-11.0 for Chabrier/Kroupa across surveys, +~0.05 dex gas; a0 = 1.2 +/- 0.24 systematic)")
kb = (vbtf(10 ** 10.6, 1.0e-10), vbtf(10 ** 11.1, 1.44e-10))
P(f"  -> V range {kb[0]:.0f}-{kb[1]:.0f} km/s.  The repository compares this V (not V/sqrt2) with sigma scales: as a sigma it would be {kb[0]/math.sqrt(2):.0f}-{kb[1]/math.sqrt(2):.0f} km/s")
P("\n== (c) cooling scale, repository definition: t_ff,brems(T) = t_H at overdensity Delta, sigma = sqrt(kT/(mu m_p))")
def cooling(Delta, gff=1.2, mu=0.60, time="hubble"):
    c_ff = (16 / 3) * math.sqrt(2 * math.pi / 3) * gff * (w.ALPHA_EM ** 3) * ((w.HBAR / (w.M_E * w.C_SI)) ** 2) * w.C_SI * math.sqrt(w.M_E * w.C_SI ** 2)
    n_e = (w.OMEGA_B / w.OMEGA_M) * Delta * w.RHO_CRIT0 / (1.14 * w.M_P)
    t = 1 / w.H0_SI if time == "hubble" else math.sqrt(3 * math.pi / (32 * G * Delta * w.RHO_CRIT0))
    sq = 1.15 * c_ff * n_e * t / 3
    return math.sqrt(sq ** 2 / (mu * w.M_P)) / 1e3
P(f"  repository setting (Delta=1000, g_ff=1.2, mu=0.60, t_H): {cooling(1000):.2f} km/s")
for D_ in [200, 500, 1000, 2500]:
    P(f"  Delta={D_:5d}: t_H -> {cooling(D_):7.1f} km/s;  free-fall time instead -> {cooling(D_, time='ff'):7.1f} km/s; g_ff 1.1-1.4, mu 0.59-0.62 -> {cooling(D_,1.1,0.62):.1f}-{cooling(D_,1.4,0.59):.1f}")
P("  sigma scales linearly with Delta for t_H (kT ~ n^2 t^2), so the choice Delta=1000 sets the answer.")
cool_lo, cool_hi = cooling(500), cooling(2500)

P("\n== (d) empirical onset from the Part-1/2 unified fit (part2b.out, part2c.out)")
P("  nominal: 158-211 km/s depending on form (bootstrap 95%: 146-241); stellar masses +0.2 dex: 335-356; -0.2 dex: 55-145; hydrostatic x1.2: 176-238")
P("  clusters-only r500 fit (../t4_clusters.out): best 230-345, 95% envelope 160-365")
P("\n== (e) chance coincidence: four scales drawn independently, log-uniform on [30, 1500] km/s")
L = math.log10(1500 / 30)
def p_spread(wdex):
    u = min(wdex / L, 1.0); return 4 * u ** 3 - 3 * u ** 4      # P(max-min <= w) for 4 iid uniforms
def spread(v): return math.log10(max(v) / min(v))
stated = [185.0, 185.59, 175.82, 178.42]
P(f"  repository values {stated}: spread {spread(stated):.4f} dex -> P = {p_spread(spread(stated)):.2e}")
st2 = [190.0, 185.59, 175.82, 178.42]
P(f"  same with the empirical onset at the edge of its stated 180-190: spread {spread(st2):.4f} dex -> P = {p_spread(spread(st2)):.2e}")
st3 = [185.0, 185.59, 175.82 / math.sqrt(2), 178.42]
P(f"  repository values but the BTFR speed converted to a 1D dispersion (V/sqrt2 = {175.82/math.sqrt(2):.1f}): spread {spread(st3):.3f} dex -> P = {p_spread(spread(st3)):.2e}")
rng = np.random.default_rng(5)
def mc(ranges, n=200000):
    lo = np.log10([r[0] for r in ranges]); hi = np.log10([r[1] for r in ranges])
    x = lo + (hi - lo) * rng.random((n, len(ranges)))
    w_ = x.max(1) - x.min(1); u = np.clip(w_ / L, 0, 1); p = 4 * u ** 3 - 3 * u ** 4
    return w_, p
for lab, ranges in [
    ("honest ranges A: collapse 141-261, knee V 152-221, cooling (Delta 500-2500) 89-446, onset 95-356", [(141, 261), (152, 221), (89, 446), (95, 356)]),
    ("honest ranges B: as A but cooling Delta 200-2500 (36-446) and onset 55-365", [(141, 261), (152, 221), (36, 446), (55, 365)]),
    ("honest ranges C: as A but knee as a dispersion V/sqrt2 (107-157)", [(141, 261), (107, 157), (89, 446), (95, 356)]),
    ("three scales only (drop onset, which was fitted near the others): ranges A", [(141, 261), (152, 221), (89, 446)]),
]:
    w_, p = mc(ranges)
    if len(ranges) == 3:
        u = np.clip(w_ / L, 0, 1); p = 3 * u ** 2 - 2 * u ** 3
    P(f"  {lab}:\n     spread median {np.median(w_):.3f} dex (16-84% {np.percentile(w_,16):.3f}-{np.percentile(w_,84):.3f}); P median {np.median(p):.3f} (16-84% {np.percentile(p,16):.3f}-{np.percentile(p,84):.3f})")
open(pathlib.Path(__file__).with_suffix(".out"), "w").write("\n".join(out) + "\n")
