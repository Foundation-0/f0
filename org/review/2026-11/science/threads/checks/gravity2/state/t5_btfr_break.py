"""T5: is there a break at the top of the baryonic Tully-Fisher relation (BTFR)? Errors in both variables.
Data (read-only, cached by the gravity thread): SPARC (Lelli+2016), Di Teodoro+2021 (DT21, Table 1),
Di Teodoro+2023 (DT23, tables tab:sample and tab:dynquant, HI gas), Ogle+2019 (O19, Table 1, H-alpha V_max)."""
import re, math, pathlib, sys
import numpy as np
from scipy.optimize import minimize
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from model import nu, ftrap, PARAMS, M_threshold
GS = pathlib.Path(__file__).resolve().parents[1] / "gravity" / "sources"
out = []
def P(*a): print(*a); out.append(" ".join(map(str, a)))
def sparc():
    rows = []
    L = (GS / "sparc/SPARC_Lelli2016c.mrt").read_text().splitlines()
    st = max(i for i, l in enumerate(L) if l.startswith("-----")) + 1
    for l in L[st:]:
        p = l.split()
        if len(p) < 18: continue
        D, eD, inc, Lum, eL, mhi, vf, ev, q = float(p[2]), float(p[3]), float(p[5]), float(p[7]), float(p[8]), float(p[13]), float(p[15]), float(p[16]), int(p[17])
        if q > 2 or inc < 30 or vf <= 0: continue
        mb = (0.5 * Lum + 1.33 * mhi) * 1e9
        ex = math.sqrt(0.1 ** 2 + (2 * eD / D / math.log(10)) ** 2)
        rows.append(("SPARC", p[0], math.log10(mb), ex, math.log10(vf), ev / vf / math.log(10)))
    return rows
def dt21():
    rows = []
    tex = (GS / "arxiv-2109.03828/paper_ss.tex").read_text()
    body = tex.split(r"\label{tab:sample}")[1].split("Discarded galaxies")[0]
    for row in body.split(r"\\"):
        c = [x.strip() for x in row.split("&")]
        if len(c) < 9 or not re.match(r"^(2MASX|SDSS)", c[0]): continue
        m = re.match(r"(\d+)\s*\$\\pm\$\s*(\d+)", c[7])
        v, ev = float(m.group(1)), float(m.group(2))
        rows.append(("DT21", c[0].replace("$-$", "-"), float(c[3]) + math.log10(1.14), 0.2, math.log10(v), ev / v / math.log(10)))
    return rows
def dt23():
    tex = (GS / "arxiv-2207.02906/paper_ssvla.tex").read_text()
    s = tex[tex.index(r"\label{tab:sample}"):]; s = s[:s.index(r"\end{tabular}")]
    mass = {}
    for row in s.split(r"\\"):
        c = [x.strip() for x in row.split("&")]
        if len(c) == 5 and re.match(r"^(NGC|UGC)", c[0].split("\n")[-1]):
            mass[re.sub(r"\$.*", "", c[0].split("\n")[-1]).strip()] = (float(c[3]), float(c[4]))
    t = (GS / "arxiv-2207.02906/table_dyn.tex").read_text()
    rows = []
    for row in t.split(r"\\"):
        c = [x.strip() for x in row.split("&")]
        nm = c[0].split("\n")[-1].strip()
        if len(c) < 5 or nm not in mass: continue
        m = re.match(r"\$(\d+)\\pm(\d+)\$", c[1]); v, ev = float(m.group(1)), float(m.group(2))
        ms, mg = mass[nm]
        rows.append(("DT23", nm, math.log10(10 ** ms + 10 ** mg), 0.2, math.log10(v), ev / v / math.log(10)))
    return rows
def o19():
    tex = (GS / "arxiv-1909.09080/pogle.tex").read_text()
    s = tex[tex.index("Super Spiral Sample"):]; s = s[s.index("startdata") + 9:s.index("enddata")]
    rows = []
    for row in s.split(r"\\"):
        c = [x.strip() for x in row.split("&")]
        if len(c) < 12: continue
        ms = float(c[7]); mg = float(c[8].replace("$<", "").replace("$", ""))
        m = re.match(r"(\d+)\s*\(\s*(\d+)\)", c[10]); v, ev = float(m.group(1)), float(m.group(2))
        rows.append(("O19", c[0].replace("$+$", "+").replace("$-$", "-").replace(" ", ""), math.log10(10 ** ms + 10 ** mg), 0.2, math.log10(v), ev / v / math.log(10)))
    return rows
SP, A21, A23, O = sparc(), dt21(), dt23(), o19()
SP = [r for r in SP if r[1] != "UGC02885"]          # also in DT23; keep the HI-based DT23 entry
P(f"SPARC {len(SP)}, DT21 {len(A21)}, DT23 {len(A23)}, O19 {len(O)}")
X0 = 10.5
def line(p, x, xb=None):
    a, b1 = p[0], p[1]
    if xb is None: return a + b1 * (x - X0)
    b2 = p[2]; yb = a + b1 * (xb - X0)
    return np.where(x < xb, a + b1 * (x - X0), yb + b2 * (x - xb))
def slope_at(p, x, xb):
    return np.full_like(x, p[1]) if xb is None else np.where(x < xb, p[1], p[2])
def m2lnL(p, x, ex, y, ey, xb):
    lns = p[-1]
    v = ey ** 2 + (slope_at(p, x, xb) * ex) ** 2 + math.exp(2 * lns)
    return float(np.sum((y - line(p, x, xb)) ** 2 / v + np.log(2 * math.pi * v)))
def fit(data, xb=None):
    x, ex, y, ey = (np.array([r[i] for r in data]) for i in (2, 3, 4, 5))
    p0 = [2.3, 0.25, -2.5] if xb is None else [2.3, 0.25, 0.25, -2.5]
    best = None
    for b2 in ([None] if xb is None else [0.25, 0.0, 0.6]):
        q0 = list(p0) if b2 is None else [2.3, 0.25, b2, -2.5]
        o = minimize(lambda p: m2lnL(p, x, ex, y, ey, xb), q0, method="Nelder-Mead", options=dict(maxiter=40000, xatol=1e-7, fatol=1e-9))
        if best is None or o.fun < best.fun: best = o
    return best
for label, data in [("SPARC+DT21+DT23 (V_flat)", SP + A21 + A23), ("SPARC+O19 (Ogle's V_max)", SP + O), ("SPARC+DT21+DT23+O19 not in DT21", SP + A21 + A23 + O)]:
    n = len(data)
    o1 = fit(data)
    P(f"\n== {label}: N={n}")
    P(f"  single line: slope dlogV/dlogMb = {o1.x[1]:.4f} (BTFR index {1/o1.x[1]:.2f}), intercept at logMb=10.5: {o1.x[0]:.3f}, intrinsic scatter {math.exp(o1.x[-1]):.3f} dex, -2lnL {o1.fun:.2f}")
    prof = []
    for xb in np.arange(10.6, 11.86, 0.05):
        nab = sum(r[2] >= xb for r in data)
        if nab < 4: continue
        o = fit(data, xb); prof.append((xb, o.fun, o.x[1], o.x[2], nab))
    bb = min(prof, key=lambda t: t[1])
    dchi = o1.fun - bb[1]
    P(f"  best broken line: break at logMb={bb[0]:.2f} ({bb[4]} galaxies above), slopes {bb[2]:.3f} -> {bb[3]:.3f} (indices {1/bb[2]:.2f} -> {1/bb[3] if abs(bb[3])>1e-3 else float('inf'):.2f}); -2dlnL vs single line = {dchi:.2f} for 2 extra params (break position + slope)")
    P("  profile over break position (-2lnL relative to single line; negative = better): " + " ".join(f"{t[0]:.2f}:{t[1]-o1.fun:+.1f}(b2={t[3]:.2f})" for t in prof))
    # significance by parametric bootstrap from the single-line fit (break location is a non-regular parameter)
    rng = np.random.default_rng(7)
    x, ex, y, ey = (np.array([r[i] for r in data]) for i in (2, 3, 4, 5))
    # latent x: shrink observed x toward mean is ignored; simulate y from single line at observed x plus all errors
    s_int = math.exp(o1.x[-1]); sims = []
    for k in range(60):
        ys = line(o1.x, x) + rng.normal(size=n) * np.sqrt(ey ** 2 + (o1.x[1] * ex) ** 2 + s_int ** 2)
        dd = [(r[0], r[1], r[2], r[3], ys[i], r[5]) for i, r in enumerate(data)]
        f1 = fit(dd).fun
        f2 = min(fit(dd, xb).fun for xb in np.arange(10.6, 11.86, 0.1) if sum(r[2] >= xb for r in data) >= 4)
        sims.append(f1 - f2)
    P(f"  bootstrap under no-break null (60 sims): -2dlnL 95th pct {np.percentile(sims,95):.2f}, max {max(sims):.2f}; observed {dchi:.2f}; p ~ {np.mean(np.array(sims) >= dchi):.2f}")
# where are the model thresholds and what jumps does the model predict on this BTFR?
P("\n== model thresholds in baryonic mass (deep-MOND BTFR mapping): A log M = %.2f, B log M = %.2f" % (math.log10(M_threshold(185.59)), math.log10(M_threshold(200.0))))
# Model-predicted log V offset from the RAR-only BTFR, solved self-consistently: V_obs^2 = V_rar^2 (nu+R f(V_obs))/nu
data = SP + A21 + A23
x = np.array([r[2] for r in data]); y = np.array([r[4] for r in data]); ex = np.array([r[3] for r in data]); ey = np.array([r[5] for r in data])
ref = (x > 9.5) & (x < 11.0)
c = np.mean(y[ref] - 0.25 * x[ref])
P(f"  RAR-only reference line logV = 0.25 logMb + {c:.4f} (fit to logMb 9.5-11.0, slope fixed to 1/4)")
for yy in [0.1, 0.3]:
    for p in "AB":
        def vpred(lm):
            v0 = 10 ** (0.25 * lm + c); v = v0
            for _ in range(200):
                v = v0 * math.sqrt((float(nu(yy)) + PARAMS[p]["R"] * float(ftrap(v / math.sqrt(2), PARAMS[p]["sigJ0"]))) / float(nu(yy)))
            return v
        pred = np.array([math.log10(vpred(lm)) for lm in x])
        hi = x > 11.2
        r_obs = y[hi] - (0.25 * x[hi] + c)
        r_mod = pred[hi] - (0.25 * x[hi] + c)
        chi_m = np.sum((y[hi] - pred[hi]) ** 2 / (ey[hi] ** 2 + (0.25 * ex[hi]) ** 2 + 0.03 ** 2))
        chi_r = np.sum((y[hi] - (0.25 * x[hi] + c)) ** 2 / (ey[hi] ** 2 + (0.25 * ex[hi]) ** 2 + 0.03 ** 2))
        jump = [round(vpred(lm)) for lm in (11.3, 11.45, 11.5, 11.55, 11.6, 11.65, 11.8)]
        P(f"  y={yy} model {p}: V at logMb 11.3,11.45,11.5,11.55,11.6,11.65,11.8 = {jump}; logMb>11.2 (n={hi.sum()}): obs offset {r_obs.mean():+.3f}, model {r_mod.mean():+.3f}; chi2 model {chi_m:.1f} vs RAR line {chi_r:.1f}")
open(pathlib.Path(__file__).with_suffix(".out"), "w").write("\n".join(out) + "\n")
