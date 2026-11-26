"""T4: groups and clusters at r2500 and r500. delta = M_tot/M_b - nu(y_b); model: delta = R f_trap(sigma), same at every radius."""
import json, pathlib, sys, math
import numpy as np
from scipy.optimize import minimize
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from model import nu, y_of, sigma_from_mass, ftrap, PARAMS
rng = np.random.default_rng(1)
STAR_SCALE = 1.0
rows = json.load(open(pathlib.Path(__file__).parent / "t4_systems.json"))
out = []
def P(*a): print(*a); out.append(" ".join(map(str, a)))
# --- stellar fraction prescription fitted to Gonzalez+2013 (3D-deprojected, includes ICL) inside r500
g = [r for r in rows if r["sample"] == "G13" and r["fstar500"]]
lx = np.log10([r["M500"] / 1e14 for r in g]); ly = np.log10([r["fstar500"] for r in g])
slope, icpt = np.polyfit(lx, ly, 1)
P(f"f_star,500 = {10**icpt:.4f} (M500/1e14)^{slope:+.2f}   (fit to {len(g)} Gonzalez+2013 systems)")
def fstar500(M500): return 10 ** icpt * (M500 / 1e14) ** slope
# dedupe: drop S09 MKW4/A1991 (in V06) and G13 A478/A2029/A2390 (in V06)
drop = {("S09", "MKW4"), ("S09", "A1991"), ("G13", "Abell0478"), ("G13", "Abell2029"), ("G13", "Abell2390")}
rows = [r for r in rows if (r["sample"], r["name"]) not in drop]
two = [r for r in rows if "M2500" in r]
P(f"systems with both radii: {len(two)} (V06 {sum(r['sample']=='V06' for r in two)}, S09 {sum(r['sample']=='S09' for r in two)}, L15 {sum(r['sample']=='L15' for r in two)}); r500 only: {len(rows)-len(two)}")

def deltas(r, k_star=1.5, b500=0.0, b2500=0.0, draw=False):
    """returns sigma, delta2500, delta500, (M/Mb)2500, (M/Mb)500, y2500, y500"""
    M5, M2 = r["M500"], r.get("M2500")
    fg5, fg2 = r["fg500"], r.get("fg2500")
    if draw:
        M5 = M5 * math.exp(rng.normal() * r["eM500"] / r["M500"])
        fg5 = fg5 * math.exp(rng.normal() * r["efg500"] / r["fg500"])
        if M2:
            M2 = M2 * math.exp(rng.normal() * r["eM2500"] / r["M2500"]); fg2 = fg2 * math.exp(rng.normal() * r["efg2500"] / r["fg2500"])
    fs5 = STAR_SCALE * (r.get("fstar500") or fstar500(r["M500"]))
    sig = float(sigma_from_mass(M5 / (1 - b500), r["r500"]))
    Mb5 = M5 * (fg5 + fs5); Mt5 = M5 / (1 - b500)
    y5 = float(y_of(Mb5, r["r500"])); d5 = Mt5 / Mb5 - float(nu(y5))
    if M2 is None: return sig, None, d5, None, Mt5 / Mb5, None, y5
    Mb2 = M2 * (fg2 + k_star * fs5); Mt2 = M2 / (1 - b2500)
    y2 = float(y_of(Mb2, r["r2500"])); d2 = Mt2 / Mb2 - float(nu(y2))
    return sig, d2, d5, Mt2 / Mb2, Mt5 / Mb5, y2, y5

P("\n=== per system, nominal (stars k=1.5 at r2500, no hydrostatic bias) ===")
P("sample name               sigma  M/Mb2500 nu2500 d2500 | M/Mb500 nu500 d500 | d2500/d500  R_A(2500) R_A(500)  R_B(2500) R_B(500)")
for r in two:
    s, d2, d5, q2, q5, y2, y5 = deltas(r)
    fa = float(ftrap(s, 185.59)); fb = float(ftrap(s, 200.0))
    P(f"{r['sample']} {r['name']:18s} {s:6.0f} {q2:7.2f} {float(nu(y2)):6.2f} {d2:6.2f} | {q5:6.2f} {float(nu(y5)):5.2f} {d5:5.2f} | {d2/d5:6.2f}    {d2/fa:6.2f}  {d5/fa:6.2f}    {d2/fb:6.2f}  {d5/fb:6.2f}")

P("\n=== radius test: ratio delta2500/delta500 (model: 1). Monte Carlo 2000 draws per system for errors ===")
P("stars k  b500 b2500 | sample  n  median ratio  weighted mean +/- err   frac(ratio>1) | mean R_A(2500) R_A(500) | mean R_B(2500) R_B(500)")
for k in [0.0, 1.0, 1.5, 2.5]:
    for b5, b2 in [(0, 0), (0.1, 0.05), (0.2, 0.1), (0.3, 0.15), (0.3, 0.0)]:
        for samp in ["V06", "S09", "L15", "all"]:
            sel = [r for r in two if samp == "all" or r["sample"] == samp]
            rat, err, RA2, RA5, RB2, RB5 = [], [], [], [], [], []
            for r in sel:
                s, d2, d5, *_ = deltas(r, k, b5, b2)
                mc = np.array([deltas(r, k, b5, b2, draw=True)[1:3] for _ in range(400)])
                rr = mc[:, 0] / mc[:, 1]
                rat.append(d2 / d5); err.append(0.5 * (np.percentile(rr, 84) - np.percentile(rr, 16)))
                fa = float(ftrap(s, 185.59)); fb = float(ftrap(s, 200.0))
                RA2.append(d2 / fa); RA5.append(d5 / fa); RB2.append(d2 / fb); RB5.append(d5 / fb)
            rat = np.array(rat); w = 1 / np.array(err) ** 2
            wm = (rat * w).sum() / w.sum(); we = 1 / math.sqrt(w.sum())
            # include scatter: error of mean from sample scatter
            se = rat.std(ddof=1) / math.sqrt(len(rat))
            P(f"  {k:3.1f}  {b5:4.2f} {b2:4.2f} | {samp:4s} {len(sel):2d}  {np.median(rat):6.2f}   {wm:6.2f} +/- {max(we,se):.2f}   {np.mean(rat>1):.2f} | {np.mean(RA2):6.2f} {np.mean(RA5):6.2f} | {np.mean(RB2):6.2f} {np.mean(RB5):6.2f}")
# bias needed
P("\nhydrostatic bias at r500 (with b2500=0, stars k=1.5) that makes the median ratio equal 1:")
for samp in ["V06", "S09", "L15", "all"]:
    sel = [r for r in two if samp == "all" or r["sample"] == samp]
    f = lambda b: np.median([deltas(r, 1.5, b, 0)[1] / deltas(r, 1.5, b, 0)[2] for r in sel]) - 1
    lo, hi = 0.0, 0.8
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0: lo = mid
        else: hi = mid
    P(f"  {samp}: b500 = {0.5*(lo+hi):.2f}")

# ---- r500 fits
from scipy.optimize import minimize_scalar
STAR_SCALE = 1.0
def fit_block(star_scale, b500):
    global STAR_SCALE
    STAR_SCALE = star_scale
    S, Dl, E = [], [], []
    for r in rows:
        s, _, d5, *_ = deltas(r, 1.5, b500, 0.0)
        mc = np.array([deltas(r, 1.5, b500, 0.0, draw=True)[2] for _ in range(300)])
        S.append(s); Dl.append(d5); E.append(mc.std())
    S, Dl, E = map(np.array, (S, Dl, E))
    P(f"\n=== r500 fits: stellar fractions x{star_scale}, hydrostatic bias b500={b500} ===")
    P(f"N = {len(S)}; sigma range {S.min():.0f}-{S.max():.0f} km/s; systems with 200<=sigma<=280: {int(((S>=200)&(S<=280)).sum())}; below 300: {int((S<300).sum())}; delta500<0: {int((Dl<0).sum())}")
    def prof_lin(basis):
        """delta = A*basis; for each scatter s, A by weighted LS; minimise -2lnL over s"""
        def m2l(lns):
            v = E**2 + np.exp(2*lns); A = np.sum(basis*Dl/v)/np.sum(basis**2/v)
            return np.sum((Dl-A*basis)**2/v + np.log(2*np.pi*v)), A
        o = minimize_scalar(lambda q: m2l(q)[0], bounds=(-6, 3), method="bounded")
        return o.fun, m2l(o.x)[1], math.exp(o.x)
    n = len(S); out_ = {}
    c = prof_lin(np.ones_like(S)); out_["constant"] = (c[0], 2)
    P(f"  constant : C={c[1]:.2f}, scatter {c[2]:.2f}, -2lnL {c[0]:.2f}, BIC {c[0]+2*math.log(n):.2f}")
    best = min(((prof_lin((S/500)**pp), pp) for pp in np.arange(-2, 4.01, 0.02)), key=lambda t: t[0][0])
    out_["powerlaw"] = (best[0][0], 3)
    P(f"  powerlaw : A={best[0][1]:.2f}, p={best[1]:.2f}, scatter {best[0][2]:.2f}, -2lnL {best[0][0]:.2f}, BIC {best[0][0]+3*math.log(n):.2f}")
    grid = np.arange(0, 451, 5.0)
    prof = [(sj,) + prof_lin(np.clip(1-(sj/S)**2, 0, None)) for sj in grid]
    m2 = min(p[1] for p in prof); bj = min(prof, key=lambda p: p[1])
    i1 = [p for p in prof if p[1]-m2 <= 1]; i2 = [p for p in prof if p[1]-m2 <= 4]
    P(f"  threshold: sigma_J={bj[0]:.0f} (68% {i1[0][0]:.0f}-{i1[-1][0]:.0f}, 95% {i2[0][0]:.0f}-{i2[-1][0]:.0f}), R={bj[2]:.2f} (R over 95% range {min(p[2] for p in i2):.2f}-{max(p[2] for p in i2):.2f}), scatter {bj[3]:.2f}, -2lnL {bj[1]:.2f}, BIC {bj[1]+3*math.log(n):.2f}")
    P("    profile -2dlnL: " + " ".join(f"{p[0]:.0f}:{p[1]-m2:.1f}" for p in prof[::4]))
    for sj in [185.59, 200.0]:
        q = prof_lin(np.clip(1-(sj/S)**2, 0, None))
        P(f"  sigma_J fixed {sj}: best R={q[1]:.2f}, -2lnL {q[0]:.2f} (vs threshold best {m2:.2f})")
    for p_ in "AB":
        pred = PARAMS[p_]["R"]*ftrap(S, PARAMS[p_]["sigJ0"])
        o = minimize_scalar(lambda lns: np.sum((Dl-pred)**2/(E**2+np.exp(2*lns)) + np.log(2*np.pi*(E**2+np.exp(2*lns)))), bounds=(-6,3), method="bounded")
        P(f"  fixed {p_}: -2lnL {o.fun:.2f}, scatter {math.exp(o.x):.2f}, mean residual (obs-model) {np.mean(Dl-pred):+.2f}")
for ss, bb in [(1.0, 0.0), (0.5, 0.0), (1.0, 0.2), (0.5, 0.2)]:
    fit_block(ss, bb)
# ---- weak-lensing check (Akino+2022 baseline fractions at r500, Chabrier): f_b/(Omega_b/Omega_m)= 0.5, 0.6, 1.0 at 1e13,1e14,1e15
P("\n=== weak-lensing masses (Akino+2022 text: f_b ~ 50%, 60%, 100% of 0.1564 at M500 = 1e13, 1e14, 1e15) ===")
from t4_data import r_from_M
for M, fr in [(1e13, 0.5), (1e14, 0.6), (1e15, 1.0)]:
    r5 = r_from_M(M, 500, 0.3, 0.7); fb = fr * 0.1564
    y = float(y_of(fb * M, r5)); s = float(sigma_from_mass(M, r5))
    d = 1 / fb - float(nu(y))
    P(f"  M500={M:.0e}: r500={r5:.0f} kpc sigma={s:.0f} M/Mb={1/fb:.2f} nu={float(nu(y)):.2f} delta={d:.2f}  R_A={d/float(ftrap(s,185.59)):.2f} R_B={d/float(ftrap(s,200)):.2f}")
open(pathlib.Path(__file__).with_suffix(".out"), "w").write("\n".join(out) + "\n")
