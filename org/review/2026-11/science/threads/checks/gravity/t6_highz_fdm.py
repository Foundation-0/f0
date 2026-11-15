"""T6: dark-matter fractions inside R_e of z = 0.6-2.5 star-forming galaxies vs the falling threshold.
Data: Genzel+2020 (RC41, arXiv:2006.03046) Table D1 (logM*, logMgas, logMbar, v_c(R_e), R_e, B/T, f_DM(R_e)) and
Table 1 (z), text extraction made by fetch_sources.py; Ubler+2017 KMOS3D (VizieR J/ApJ/842/121 table3: z, logMbar, V_circ,max).
Prediction: f_DM = 1 - 1/(nu(y) + R f_trap(v_c/sqrt2; sigma_J(z))), y = g_b(R_e)/a0 from M_bar, R_e, B/T."""
import re, math, pathlib, sys
import numpy as np
from scipy.special import i0, i1, k0, k1
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from model import nu, ftrap, PARAMS, sigJ, G, MSUN, KPC, A0
src = pathlib.Path(__file__).parent / "sources" / "from_accel"
out = []
def P(*a): print(*a); out.append(" ".join(map(str, a)))
Z = [0.66, 0.67, 0.73, 0.75, 0.76, 0.81, 0.82, 0.83, 0.85, 0.91, 0.92, 0.99, 1.03, 1.03, 1.12, 1.20, 1.23, 1.36, 1.40, 1.45, 1.50,
     1.53, 1.61, 1.62, 2.04, 2.15, 2.17, 2.18, 2.18, 2.19, 2.20, 2.21, 2.23, 2.24, 2.24, 2.26, 2.31, 2.38, 2.39, 2.43, 2.45]  # Table 1 col 3, by index
VC_T1 = [326, 230, 187, 327, 156, 145, 146, 249, 290, 145, 194, 200, 282, 269, 220, 354, 393, 356, 300, 204, 308, 348, 257, 397, 250,
         139, 189, 331, 280, 222, 301, 327, 308, 162, 289, 293, 190, 268, 416, 260, 171]  # Table 1 col 5, used to check row matching
txt = (src / "rc41_2006.03046.txt").read_text()
txt = txt[txt.index("Appendix D"):]
rows = {}
for ln in txt.splitlines():
    m = re.match(r"^\s{0,4}(\d{1,2})\s+(.*)$", ln)
    if not m: continue
    toks = m.group(2).split()
    if toks and not re.match(r"^-?[\d.]+(E[+-]\d+)?$", toks[0]): toks = toks[1:]
    nums = []
    for t in toks:
        if re.match(r"^-?[\d.]+(E[+-]\d+)?$", t): nums.append(float(t))
        else: break
    if len(nums) >= 22: rows[int(m.group(1))] = nums
P(f"RC41 Table D1 rows parsed: {len(rows)}")
gal = []
for i in range(1, 42):
    n = rows[i]
    lms, lmdm, lmg, lmb, dlmb, md, md2, dsfr, sfr, vc, s0, Re, ns, inc, bt, rvir, sdm1, sdm2, defi, jj, fdm = n[:21]
    if abs(vc - VC_T1[i - 1]) > 0.5: P("  row mismatch", i, vc, VC_T1[i - 1])
    gal.append(dict(i=i, z=Z[i - 1], lms=lms, lmb=lmb, vc=vc, Re=Re, bt=bt, fdm=fdm))
def gb_at_Re(Mb, Re, bt):
    """thin exponential disk (R_e = 1.678 R_d) plus a bulge wholly inside R_e"""
    Rd = Re / 1.678; yy = Re / (2 * Rd)
    v2d = 2 * G * (1 - bt) * Mb * MSUN / (Rd * KPC) * yy ** 2 * (i0(yy) * k0(yy) - i1(yy) * k1(yy))
    return v2d / (Re * KPC) + G * bt * Mb * MSUN / (Re * KPC) ** 2
P("\n idx    z  logMb   vc   Re   y    f_DM obs | RAR  | A(evolving) | B(evolving) B(sigma_J fixed 200)")
res = []
for g in gal:
    y = gb_at_Re(10 ** g["lmb"], g["Re"], g["bt"]) / A0
    s = g["vc"] / math.sqrt(2)
    fr = 1 - 1 / float(nu(y))
    fa = 1 - 1 / (float(nu(y)) + PARAMS["A"]["R"] * float(ftrap(s, sigJ("A", g["z"]))))
    fb = 1 - 1 / (float(nu(y)) + PARAMS["B"]["R"] * float(ftrap(s, sigJ("B", g["z"]))))
    fb0 = 1 - 1 / (float(nu(y)) + PARAMS["B"]["R"] * float(ftrap(s, 200.0)))
    # implied baryon-only acceleration from the published decomposition (circular check)
    res.append((g["z"], g["fdm"], fr, fa, fb, fb0, y))
    P(f" {g['i']:3d} {g['z']:5.2f} {g['lmb']:5.2f} {g['vc']:4.0f} {g['Re']:4.1f} {y:5.2f}  {g['fdm']:5.2f}   | {fr:4.2f} | {fa:4.2f}        | {fb:4.2f}        {fb0:4.2f}")
r = np.array(res)
for lo, hi in [(0.6, 1.2), (1.2, 2.5), (0.6, 2.5)]:
    m = (r[:, 0] >= lo) & (r[:, 0] < hi)
    P(f"z {lo}-{hi}: n={m.sum()}  median f_DM obs {np.median(r[m,1]):.2f} (max {r[m,1].max():.2f}) | RAR {np.median(r[m,2]):.2f} | A {np.median(r[m,3]):.2f} (min {r[m,3].min():.2f}) | B {np.median(r[m,4]):.2f} (min {r[m,4].min():.2f}) | B fixed {np.median(r[m,5]):.2f}")
P(f"galaxies with obs f_DM >= model A prediction: {(r[:,1] >= r[:,3]).sum()} of {len(r)}; >= model B (evolving): {(r[:,1] >= r[:,4]).sum()}; >= RAR-only: {(r[:,1] >= r[:,2]).sum()}")
# what baryon overestimate would rescue A?  need (nu+Rf) = 1/(1-fdm_obs) -> impossible if 1/(1-fdm) < 1 + R f
need = 1 / (1 - np.clip(r[:, 1], 0, 0.99))
P(f"obs total/baryon inside R_e = 1/(1-f_DM): median {np.median(need):.2f}, max {need.max():.2f}; model A floor 1+R f_trap = {1+PARAMS['A']['R']*0.97:.1f}, model B floor {1+PARAMS['B']['R']*0.97:.1f}")
P("  -> for model A to hold, M_bar would have to be overestimated by a factor ~ (nu+Rf)/(1/(1-f_DM)); median: "
  f"{np.median((np.array([float(nu(x)) for x in r[:,6]]) + PARAMS['A']['R']*0.97) / need):.1f}")

# ---- Ubler+2017 KMOS3D baryonic TF: offset of log V from the z=0 SPARC-calibrated BTFR, against z
P("\n== Ubler+2017 KMOS3D (V_circ,max, logMbar): offset d = log V - 0.25 log(G Mb a0) relative to SPARC c0 = 0.0327 (gravity/t2)")
L = [l for l in (src / "ubler2017_vizier.tsv").read_text().splitlines() if l and not l.startswith("#")]
hdr = L[0].split("\t"); data = [l.split("\t") for l in L[3:]]
iz, imb, iv = hdr.index("z"), hdr.index("logMb"), hdr.index("Vcirc")
zz = np.array([float(d[iz]) for d in data]); lmb = np.array([float(d[imb]) for d in data]); vv = np.array([float(d[iv]) for d in data])
d = np.log10(vv * 1e3) - 0.25 * np.log10(G * 10 ** lmb * MSUN * A0) - 0.0327
for lo, hi in [(0.6, 1.1), (1.9, 2.7)]:
    m = (zz >= lo) & (zz < hi)
    zm = np.median(zz[m]); s = vv[m] / math.sqrt(2)
    pa = [0.5 * math.log10((float(nu(y)) + PARAMS["A"]["R"] * float(ftrap(s.mean(), sigJ("A", zm)))) / float(nu(y))) for y in (0.3, 1, 3)]
    pb = [0.5 * math.log10((float(nu(y)) + PARAMS["B"]["R"] * float(ftrap(s.mean(), sigJ("B", zm)))) / float(nu(y))) for y in (0.3, 1, 3)]
    P(f"  z {lo}-{hi} (median {zm:.2f}, n={m.sum()}, median V {np.median(vv[m]):.0f}): observed offset median {np.median(d[m]):+.3f}, mean {d[m].mean():+.3f} +/- {d[m].std(ddof=1)/math.sqrt(m.sum()):.3f} dex; "
      f"model A extra offset at y=0.3,1,3: {', '.join(f'{x:+.2f}' for x in pa)}; model B: {', '.join(f'{x:+.2f}' for x in pb)}")
open(pathlib.Path(__file__).with_suffix(".out"), "w").write("\n".join(out) + "\n")
