"""Part 2 machinery. Every law predicts M_tot for each row; the score is the residual log10(M_tot,obs/M_tot,pred) in dex.
Class-balanced: every local class carries equal total weight."""
import math, numpy as np
from scipy.optimize import minimize
import build_table as bt
from build_table import nu, solve_gN, G, MSUN, KPC, A0
LOCAL = ["SPARC_outer", "SPARC_inner", "giant_spirals", "ATLAS3D_Re", "GC_r2500", "GC_r500"]
VARS = ["sigma", "r", "Mb", "g_b", "g_tot", "Sigma_b", "sigma2", "t_cross", "rho_tot", "psi"]
VDESC = dict(sigma="velocity scale sigma [km/s]", r="radius [kpc]", Mb="enclosed baryonic mass [Msun]", g_b="baryonic acceleration [m/s2]",
             g_tot="total acceleration [m/s2] (contains M_tot)", Sigma_b="M_b/(pi r^2) [Msun/kpc2]", sigma2="potential depth sigma^2",
             t_cross="r/sigma", rho_tot="3 M_tot/(4 pi r^3) (contains M_tot)", psi="sigma^3 r^3 (phase-space capacity proxy)")
def arrays(rows):
    A = {k: np.array([d[k] for d in rows], float) for k in ["r", "Mb", "Mtot", "sigma", "g_b", "g_tot", "e_logMb", "e_logMtot", "deltaA", "yB", "M_extraB", "z"]}
    A["cls"] = np.array([d["cls"] for d in rows])
    A["Sigma_b"] = A["Mb"] / (math.pi * A["r"] ** 2); A["sigma2"] = A["sigma"] ** 2; A["t_cross"] = A["r"] / A["sigma"]
    A["rho_tot"] = 3 * A["Mtot"] / (4 * math.pi * A["r"] ** 3); A["psi"] = A["sigma"] ** 3 * A["r"] ** 3
    A["nu_b"] = nu(A["g_b"] / A0)
    return A
def sub(A, m): return {k: (v[m] if isinstance(v, np.ndarray) else v) for k, v in A.items()}
def weights(A):
    w = np.zeros(len(A["r"]))
    for c in np.unique(A["cls"]):
        m = A["cls"] == c; w[m] = 1.0 / m.sum()
    return w / w.sum()
# ---------------- laws: each returns predicted log10 M_tot
def mt_from_delta(A, delta): return np.log10(np.clip(A["Mb"] * (A["nu_b"] + delta), 1e-30, None))
def mt_from_Mextra(A, Mex):
    MN = np.clip(A["Mb"] + Mex, 1e-3 * A["Mb"], None)
    gn = G * MN * MSUN / (A["r"] * KPC) ** 2
    return np.log10(nu(gn / A0) * gn * (A["r"] * KPC) ** 2 / G / MSUN)
def lx(A, v, x0): return np.log10(A[v]) - x0
def sharp(q): return 0.5 + 5.5 / (1 + np.exp(-q))          # threshold sharpness s in (0.5, 6)
def thr(p, A, v, x0):
    R = 10 ** min(p[0], 1.5)
    return R * np.clip(1 - 10 ** (-sharp(p[2]) * (lx(A, v, x0) - p[1])), 0, None)
LAWS = {
 # name: (npar, function(p, A, var, x0) -> log Mtot pred, starting points)
 "A_power":     (2, lambda p, A, v, x0: mt_from_delta(A, 10 ** p[0] * 10 ** (p[1] * lx(A, v, x0))), [[0, 0.5], [0, 2], [-1, 1]]),
 "A_threshold": (3, lambda p, A, v, x0: mt_from_delta(A, thr(p, A, v, x0)),
                 [[0.5, 0.0, 0.0], [0.5, 0.5, 1.0], [0.7, -0.5, -1.0], [0.5, 1.0, 0.0], [0.8, 0.3, 2.0]]),
 "B_power":     (2, lambda p, A, v, x0: mt_from_Mextra(A, 10 ** (p[0] + p[1] * lx(A, v, x0))), [[10, 1], [12, 2], [11, 0.5]]),
 "B_ratio_power": (2, lambda p, A, v, x0: mt_from_Mextra(A, A["Mb"] * 10 ** (p[0] + p[1] * lx(A, v, x0))), [[0, 0.5], [0, 2], [-1, 1]]),
 "B_threshold": (3, lambda p, A, v, x0: mt_from_Mextra(A, A["Mb"] * thr(p, A, v, x0)),
                 [[0.5, 0.0, 0.0], [0.5, 0.5, 1.0], [0.7, -0.5, -1.0], [0.5, 1.0, 0.0], [0.8, 0.3, 2.0]]),
}
BASE = {"RAR_only": lambda A: mt_from_delta(A, 0.0)}
def loss(pred, A, w): r = np.log10(A["Mtot"]) - pred; return float(np.sum(w * r ** 2))
def fit(A, law, v, x0, starts=None):
    n, f, st = LAWS[law]
    w = weights(A); best = None
    for s0 in (starts or st):
        if law == "B_power": s0 = [s0[0], s0[1]]
        o = minimize(lambda p: loss(f(p, A, v, x0), A, w), s0, method="Nelder-Mead", options=dict(maxiter=4000, xatol=1e-5, fatol=1e-9))
        if best is None or o.fun < best.fun: best = o
    return best.x, best.fun
def class_rms(A, pred):
    out = {}
    for c in np.unique(A["cls"]):
        m = A["cls"] == c; r = np.log10(A["Mtot"][m]) - pred[m]
        out[c] = (float(np.sqrt(np.mean(r ** 2))), float(np.mean(r)))
    return out
