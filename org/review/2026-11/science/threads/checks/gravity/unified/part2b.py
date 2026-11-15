"""Part 2b: (1) control variable sigma_RAR (system velocity predicted from baryons alone, no M_tot inside);
(2) onset of the sigma threshold with bootstrap; (3) two-variable law M_extra = K sigma^a r^b; (4) high-z prediction, no refit."""
import sys, math, pathlib, json
import numpy as np
from scipy.optimize import minimize
from multiprocessing import Pool
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import build_table as bt
from fitlib import *
NB = 100
out = []
def P(*a): print(*a, flush=True); out.append(" ".join(map(str, a)))
def add_sigma_rar(rows):
    """per system: sigma_RAR = sqrt(nu(g_b) g_b r / 2) at the system's outermost row"""
    outer = {}
    for d in rows:
        key = (d["cls"].split("_")[0] if d["cls"].startswith(("SPARC", "GC")) else d["cls"], d["name"])
        if key not in outer or d["r"] > outer[key]["r"]: outer[key] = d
    for d in rows:
        key = (d["cls"].split("_")[0] if d["cls"].startswith(("SPARC", "GC")) else d["cls"], d["name"])
        o = outer[key]; gt = float(nu(o["g_b"] / A0)) * o["g_b"]
        d["sigma_rar"] = math.sqrt(gt * o["r"] * KPC / 2) / 1e3
    return rows
def local(dl=0.0, hse=1.0):
    rows = add_sigma_rar(bt.build(dl, hse, with_highz=False))
    A = arrays(rows); A["sigma_rar"] = np.array([d["sigma_rar"] for d in rows]); return A
A = local(); X0 = {v: float(np.median(np.log10(A[v]))) for v in VARS + ["sigma_rar"]}
w = weights(A)
# ---------- (1) control variable
P("== (1) control: sigma_RAR = sqrt(nu(g_b) g_b r/2) at each system's outer radius (no M_tot information)")
P(f"   correlation of log sigma_RAR with log sigma: {np.corrcoef(np.log10(A['sigma_rar']), np.log10(A['sigma']))[0,1]:.3f}")
for law in LAWS:
    for v in ["sigma", "sigma_rar", "Mb"]:
        p, L = fit(A, law, v, X0[v]); lo = []
        for c in LOCAL:
            m = A["cls"] != c
            pc, _ = fit(sub(A, m), law, v, X0[v], starts=[list(p)] + LAWS[law][2])
            r = np.log10(A["Mtot"][~m]) - LAWS[law][1](pc, sub(A, ~m), v, X0[v]); lo.append(np.sqrt(np.mean(r ** 2)))
        P(f"   {law:14s} {v:9s}: in-sample {math.sqrt(L):.3f}  LOCO {np.sqrt(np.mean(np.square(lo))):.3f}  (per class " + " ".join(f"{x:.2f}" for x in lo) + ")")
# ---------- (2) sigma onset
def thr_fixed_s(form, s):
    def f(p, A, v, x0):
        y = 10 ** min(p[0], 1.5) * np.clip(1 - 10 ** (-s * (lx(A, v, x0) - p[1])), 0, None)
        return mt_from_delta(A, y) if form == "A" else mt_from_Mextra(A, A["Mb"] * y)
    return f
def fit_custom(A, f, v, starts):
    w = weights(A); best = None
    for s0 in starts:
        o = minimize(lambda p: loss(f(p, A, v, X0[v]), A, w), s0, method="Nelder-Mead", options=dict(maxiter=4000, xatol=1e-5, fatol=1e-9))
        if best is None or o.fun < best.fun: best = o
    return best.x, best.fun
CASES = [("A free s", None, "A"), ("A s=2 (repo form)", 2.0, "A"), ("B s=2", 2.0, "B"), ("B free s", None, "B")]
def onset_job(seed):
    B = A if seed < 0 else None
    if seed >= 0:
        rng = np.random.default_rng(1000 + seed)
        idx = np.concatenate([rng.choice(np.where(A["cls"] == c)[0], (A["cls"] == c).sum()) for c in LOCAL]); B = sub(A, idx)
    res = []
    for name, s, form in CASES:
        if s is None:
            p, L = fit(B, form + "_threshold", "sigma", X0["sigma"])
            res.append((10 ** (X0["sigma"] + p[1]), 10 ** min(p[0], 1.5), float(sharp(p[2])), math.sqrt(L)))
        else:
            p, L = fit_custom(B, thr_fixed_s(form, s), "sigma", [[0.5, x, ] for x in (-0.3, 0.0, 0.2, 0.4)])
            res.append((10 ** (X0["sigma"] + p[1]), 10 ** min(p[0], 1.5), s, math.sqrt(L)))
    return res
# ---------- (3) two-variable law
def two_var(p, A):
    return mt_from_Mextra(A, 10 ** (p[0] + p[1] * (np.log10(A["sigma"]) - 2.3) + p[2] * (np.log10(A["r"]) - 2.0)))
def fit2(B, fixed=None):
    w = weights(B)
    if fixed is None:
        best = min((minimize(lambda p: loss(two_var(p, B), B, w), s0, method="Nelder-Mead", options=dict(maxiter=6000, xatol=1e-6, fatol=1e-10))
                    for s0 in ([11, 3, 1], [12, 2, 1], [11, 5, 0], [10, 3, 3])), key=lambda o: o.fun)
        return best.x, best.fun
    a, b = fixed
    o = minimize(lambda q: loss(two_var([q[0], a, b], B), B, w), [11.0], method="Nelder-Mead"); return np.array([o.x[0], a, b]), o.fun
def two_job(seed):
    rng = np.random.default_rng(2000 + seed)
    idx = np.concatenate([rng.choice(np.where(A["cls"] == c)[0], (A["cls"] == c).sum()) for c in LOCAL])
    return fit2(sub(A, idx))[0].tolist()
if __name__ == "__main__":
    P("\n== (2) onset of the sigma law (local sample; bootstrap over systems within classes, %d replicates)" % NB)
    base = onset_job(-1)
    with Pool(2) as pool: bs = pool.map(onset_job, range(NB))
    for i, (name, s, form) in enumerate(CASES):
        sj = np.array([b[i][0] for b in bs]); R = np.array([b[i][1] for b in bs]); ss = np.array([b[i][2] for b in bs])
        P(f"   {name:18s}: sigma_J = {base[i][0]:.0f} km/s (68% {np.percentile(sj,16):.0f}-{np.percentile(sj,84):.0f}, 95% {np.percentile(sj,2.5):.0f}-{np.percentile(sj,97.5):.0f}); "
          f"R = {base[i][1]:.2f} (68% {np.percentile(R,16):.2f}-{np.percentile(R,84):.2f}); sharpness s = {base[i][2]:.2f} (68% {np.percentile(ss,16):.2f}-{np.percentile(ss,84):.2f}); rms {base[i][3]:.3f}")
    P("\n== (3) two-variable law M_extra = K (sigma/200 km/s)^a (r/100 kpc)^b  [form B]")
    p, L = fit2(A)
    with Pool(2) as pool: tb = np.array(pool.map(two_job, range(NB)))
    P(f"   best: log K = {p[0]:.2f}, a = {p[1]:.2f} (68% {np.percentile(tb[:,1],16):.2f}-{np.percentile(tb[:,1],84):.2f}; 95% {np.percentile(tb[:,1],2.5):.2f}-{np.percentile(tb[:,1],97.5):.2f}), "
      f"b = {p[2]:.2f} (68% {np.percentile(tb[:,2],16):.2f}-{np.percentile(tb[:,2],84):.2f}; 95% {np.percentile(tb[:,2],2.5):.2f}-{np.percentile(tb[:,2],97.5):.2f}); rms {math.sqrt(L):.3f}")
    P(f"   correlation of a and b across bootstrap: {np.corrcoef(tb[:,1], tb[:,2])[0,1]:.2f}")
    for lab, fx in [("a=3,b=3 (max phase-space density, packed)", (3, 3)), ("a=2,b=1 (isothermal halo)", (2, 1))]:
        q, Lq = fit2(A, fx)
        P(f"   {lab:42s}: log K = {q[0]:.2f}, rms {math.sqrt(Lq):.3f} (vs free {math.sqrt(L):.3f}); n*Delta(MSE) class-balanced = {(Lq-L):.4f} dex^2")
    pr, Lr = fit(A, "B_ratio_power", "sigma", X0["sigma"])
    w = weights(A)
    o = minimize(lambda q: loss(mt_from_Mextra(A, A["Mb"] * 10 ** q[0]), A, w), [0.0], method="Nelder-Mead")
    P(f"   M_extra = c M_b                           : c = {10**o.x[0]:.3f}, rms {math.sqrt(o.fun):.3f}")
    P(f"   RAR only                                  : rms {math.sqrt(loss(mt_from_delta(A, 0.0), A, w)):.3f}")
    q33, _ = fit2(A, (3, 3))
    K = 10 ** q33[0] / (200 ** 3 * 100 ** 3)        # Msun per (km/s)^3 kpc^3
    # Pauli bound: phase-space mass density F <= g m^4 / h^3 ; for a Maxwellian core M(<r) = (4pi/3) r^3 F (2 pi sigma^2)^(3/2)
    h = 6.62607015e-34; Fsi = K * MSUN / ((1e3) ** 3 * KPC ** 3) / ((4 * math.pi / 3) * (2 * math.pi) ** 1.5)
    for g in (2, 1):
        m = (Fsi * h ** 3 / g) ** 0.25; P(f"   a=b=3 normalisation -> fermion mass (Pauli bound F = g m^4/h^3, Maxwellian core, g={g}): {m/1.78266192e-36:.2f} eV  (Tremaine-Gunn F<=g m^4/(2h^3) gives x2^(1/4)={m*2**0.25/1.78266192e-36:.2f} eV)")
    # ---------- (4) high-z, no refit
    P("\n== (4) high-z class (RC100, Nestor Shachar+2023), laws fitted on the local sample only, no refit")
    H = arrays(add_sigma_rar(bt.build(0.0, 1.0, with_highz=True)))
    m = H["cls"] == "highz_RC100"; Hz = sub(H, m)
    preds = {"RAR only": mt_from_delta(Hz, 0.0)}
    for law, v in [("B_power", "sigma"), ("A_threshold", "sigma"), ("B_threshold", "sigma"), ("A_threshold", "Mb"), ("A_threshold", "psi")]:
        pp, _ = fit(A, law, v, X0[v]); preds[f"{law}|{v}"] = LAWS[law][1](pp, Hz, v, X0[v])
    preds["two-variable law"] = two_var(p, Hz)
    fobs = 1 - Hz["Mb"] / Hz["Mtot"]
    for k, pr in preds.items():
        res = np.log10(Hz["Mtot"]) - pr; fpred = 1 - Hz["Mb"] / 10 ** pr
        lowz = Hz["z"] < 1.2
        P(f"   {k:22s}: residual log M_tot obs-pred median {np.median(res):+.3f}, rms {np.sqrt(np.mean(res**2)):.3f}; f_DM(R_e) median pred {np.median(fpred):.2f} vs obs {np.median(fobs):.2f}"
          f" (z<1.2: {np.median(fpred[lowz]):.2f} vs {np.median(fobs[lowz]):.2f}; z>=1.2: {np.median(fpred[~lowz]):.2f} vs {np.median(fobs[~lowz]):.2f})")
    open(HERE / "part2b.out", "w").write("\n".join(out) + "\n")
