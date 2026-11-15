"""T3: ATLAS3D early-type galaxies. Observable: total M/L within a sphere of radius Re (JAM, Cappellari+2013a,
'(M/L)_JAM ~ (M/L)(r=Re)') divided by stellar-population M/L for a fixed IMF (Salpeter, Cappellari+2013b col 5;
Kroupa taken as Salpeter - 0.20 dex). Model: ratio = nu(y) + R f_trap(sigma), y from stellar mass in the Re sphere."""
import numpy as np, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from model import nu, ratio, y_of, PARAMS, ftrap
src = pathlib.Path(__file__).parent / "sources" / "atlas3d"
def load(fn, ncol):
    d = {}
    for ln in open(src / fn):
        if ln.startswith("#") or not ln.strip(): continue
        s = ln.split(); d[s[0]] = [float(x) if x.strip("-") else np.nan for x in s[1:ncol]]
    return d
t15 = load("Cappellari2013a_Atlas3D_Paper15_Table1.txt", 16)
t20 = load("Cappellari2013b_Atlas3D_Paper20_Table1.txt", 7)
t1 = load("Cappellari2011a_Atlas3D_Paper1_Table3.txt", 13)
FRAC_SPHERE = 0.42      # fraction of total light inside a sphere of radius Re (de Vaucouleurs; r_1/2 ~ 1.33 Re)
KROUPA_OFF = 0.20       # log (M/L)_Salp - log (M/L)_Kroupa, assumed
rows = []
for g, a in t15.items():
    if g not in t20 or g not in t1: continue
    logsig, _, _, inc, logMLjam, logVc, qual, _, logRe_as, _, _, _, _, logL = a[:14]
    _, fdm, logMLst, logMLsalp, hb = t20[g]
    Dmpc = t1[g][7]
    Re_kpc = 10 ** logRe_as / 206265.0 * Dmpc * 1e3
    rows.append((g, 10 ** logsig, 10 ** logVc / np.sqrt(2), qual, logMLjam, logMLsalp, logL, Re_kpc, fdm, hb))
g, sig, vcs, q, mlj, mls, logL, Re, fdm, hb = map(np.array, zip(*rows))
print("galaxies matched:", len(g), "; quality>=1:", (q >= 1).sum())
good = (q >= 1) & np.isfinite(mlj) & np.isfinite(mls) & np.isfinite(Re) & np.isfinite(logL)
out = []
def P(*a): print(*a); out.append(" ".join(map(str, a)))
for imf, off in [("Salpeter", 0.0), ("Kroupa", KROUPA_OFF)]:
    mlpop = mls - off
    obs = mlj - mlpop                                      # log (M_tot / M_star) inside Re sphere
    Mst_in = 10 ** (mlpop + logL) * FRAC_SPHERE
    y = y_of(Mst_in, Re)
    P(f"\n=== IMF {imf}: observable log10(M_tot/M_star) within r=Re ; RAR-only prediction log nu(y) ===")
    for selname, selvar, edges in [("sigma_e", sig, [0, 100, 150, 185.59, 200, 230, 260, 400]),
                                   ("Vc_max/sqrt2", vcs, [0, 100, 150, 185.59, 200, 230, 260, 400]),
                                   ("log L_r", logL, [9, 9.8, 10.1, 10.4, 10.7, 11.5])]:
        P(f"-- binned by {selname} (quality>=1)")
        P("   bin            n  obs mean   sem   | RAR  |  A(sig_e) A(Vc) | B(sig_e) B(Vc)")
        for lo, hi in zip(edges[:-1], edges[1:]):
            m = good & (selvar >= lo) & (selvar < hi)
            if m.sum() < 2: continue
            o = obs[m]; r = np.log10(nu(y[m]))
            pa = np.log10(ratio("A", y[m], sig[m])); pav = np.log10(ratio("A", y[m], vcs[m]))
            pb = np.log10(ratio("B", y[m], sig[m])); pbv = np.log10(ratio("B", y[m], vcs[m]))
            P(f"  {lo:7.2f}-{hi:7.2f} {m.sum():3d}  {o.mean():+.3f} {o.std(ddof=1)/np.sqrt(m.sum()):.3f} | {r.mean():+.3f} | {pa.mean():+.3f} {pav.mean():+.3f} | {pb.mean():+.3f} {pbv.mean():+.3f}")
    hi = good & (sig > 185.59)
    oh = obs[hi]
    for p in "AB":
        pr = np.log10(ratio(p, y[hi], sig[hi]))
        # implied stellar M/L relative to the assumed IMF if the model were right
        need = oh - pr
        P(f"  sigma_e>185.59 ({hi.sum()} gal): model {p} needs log(M*/L)/(M*/L)_{imf} = {need.mean():+.3f} (median {np.median(need):+.3f}, max {need.max():+.3f})")
        P(f"     fraction of these galaxies where obs >= model {p} prediction: {(oh >= pr).mean():.3f}")
    hiB = good & (sig > 200)
    P(f"  sigma_e>200 ({hiB.sum()} gal): obs mean {obs[hiB].mean():+.3f}; RAR {np.log10(nu(y[hiB])).mean():+.3f}")
    # slope of obs vs log sigma above / below threshold, and model's slope
    for lo, hi_ in [(60, 185.59), (185.59, 400)]:
        m = good & (sig >= lo) & (sig < hi_)
        x = np.log10(sig[m])
        so = np.polyfit(x, obs[m], 1)[0]
        sa = np.polyfit(x, np.log10(ratio("A", y[m], sig[m])), 1)[0]
        sb = np.polyfit(x, np.log10(ratio("B", y[m], sig[m])), 1)[0]
        sr = np.polyfit(x, np.log10(nu(y[m])), 1)[0]
        P(f"  slope d obs/d log sigma for {lo}-{hi_}: obs {so:+.2f}, RAR {sr:+.2f}, A {sa:+.2f}, B {sb:+.2f}  (n={m.sum()})")
# Cappellari's own f_DM(Re) from models with a halo, for reference
for lo, hi_ in [(0, 185.59), (185.59, 400)]:
    m = good & (sig >= lo) & (sig < hi_)
    P(f"published f_DM(Re) (Cappellari+2013b, NFW models), sigma_e {lo}-{hi_}: median {np.median(fdm[m]):.2f}, mean {fdm[m].mean():.2f}, n={m.sum()}")
m = good & (sig > 185.59)
for p in "AB":
    pf = 1 - 1 / ratio(p, y_of(10 ** (mls[m] - KROUPA_OFF + logL[m]) * FRAC_SPHERE, Re[m]), sig[m])
    P(f"model {p} f_DM(Re) predicted for sigma_e>185.59 (Kroupa stars): median {np.median(pf):.2f}")

# Differential test, independent of the IMF normalisation: residual = obs - log(prediction).
# If a model is right, mean residual above threshold equals mean residual in the 120-185.59 control bin.
P("\n=== differential test (Salpeter; IMF offset cancels) ===")
obs = mlj - mls
Mst_in = 10 ** (mls + logL) * FRAC_SPHERE; y = y_of(Mst_in, Re)
ctrl = good & (sig >= 120) & (sig < 185.59)
for selname, s in [("sigma_e", sig), ("Vc/sqrt2", vcs)]:
    for p in ["RAR", "A", "B"]:
        pr = np.log10(nu(y)) if p == "RAR" else np.log10(ratio(p, y, s))
        res = obs - pr
        c0 = res[ctrl].mean()
        for lo, hi_ in [(185.59, 230), (230, 400), (185.59, 400)]:
            m = good & (sig >= lo) & (sig < hi_)
            d = res[m] - c0
            se = np.sqrt(res[m].var(ddof=1) / m.sum() + res[ctrl].var(ddof=1) / ctrl.sum())
            P(f"  f_trap from {selname:9s} model {p:3s} sigma_e {lo:6.1f}-{hi_:5.0f}: residual step {d.mean():+.3f} +/- {se:.3f} dex ({d.mean()/se:+.1f} sigma), n={m.sum()}")
