"""Part 1: one table, one row per system and radius.  build(dlogMs=0, hse=1.0) returns a list of dicts.
dlogMs shifts every stellar mass (not gas) by that many dex; hse multiplies hydrostatic cluster masses.
Reuses parsers of ../t3, ../t4, ../t5, ../t6 (same thread, my own code)."""
import math, re, json, pathlib, sys
import numpy as np
HERE = pathlib.Path(__file__).resolve().parent; T = HERE.parent
sys.path.insert(0, str(T))
from model import nu, G, MSUN, KPC, A0
GS = T.parent / "gravity" / "sources"
MK = MSUN / KPC  # G*M/r with M in Msun, r in kpc -> multiply by G*MK
def gN(M, r): return G * M * MSUN / (r * KPC) ** 2
def solve_gN(gtot):
    """g_tot = nu(g_N/a0) g_N, monotone in g_N -> bisection in log"""
    gtot = np.atleast_1d(np.asarray(gtot, float)); lo = np.full_like(gtot, 1e-16); hi = gtot.copy()
    for _ in range(80):
        mid = np.sqrt(lo * hi); f = nu(mid / A0) * mid
        lo = np.where(f < gtot, mid, lo); hi = np.where(f < gtot, hi, mid)
    return np.sqrt(lo * hi)

def sparc(dl):
    tab = {}
    L = (GS / "sparc/SPARC_Lelli2016c.mrt").read_text().splitlines()
    st = max(i for i, l in enumerate(L) if l.startswith("-----")) + 1
    for l in L[st:]:
        p = l.split()
        if len(p) < 18: continue
        tab[p[0]] = dict(inc=float(p[5]), Reff=float(p[9]), Rd=float(p[11]), vf=float(p[15]), q=int(p[17]))
    curves = {}
    for l in (GS / "sparc/MassModels_Lelli2016c.mrt").read_text().splitlines():
        p = l.split()
        if len(p) != 10 or not re.match(r"^-?[\d.]+$", p[1]): continue
        curves.setdefault(p[0], []).append([float(x) for x in p[1:8]])
    rows = []
    for gname, c in curves.items():
        t = tab[gname]
        if t["q"] > 2 or t["inc"] < 30: continue
        c = np.array(c)  # D R Vobs eV Vgas Vdisk Vbul
        R, V, eV, Vg, Vd, Vb = c[:, 1], c[:, 2], c[:, 3], c[:, 4], c[:, 5], c[:, 6]
        ys = 10 ** dl
        vb2 = Vg * np.abs(Vg) + ys * (0.5 * Vd ** 2 + 0.7 * Vb ** 2)
        vf = t["vf"] if t["vf"] > 0 else V[-1]
        sig = vf / math.sqrt(2)
        picks = [("SPARC_outer", len(R) - 1)]
        j = int(np.argmin(np.abs(R - t["Reff"])))
        if j < len(R) - 2: picks.append(("SPARC_inner", j))
        for cls, i in picks:
            if vb2[i] <= 0: continue
            r = R[i]
            Mt = V[i] ** 2 * r / (G * MK) * 1e6; Mb = vb2[i] * r / (G * MK) * 1e6
            fst = ys * (0.5 * Vd[i] ** 2 + 0.7 * Vb[i] ** 2) / vb2[i]
            rows.append(dict(cls=cls, name=gname, z=0.0, r=r, Mb=Mb, Mtot=Mt, sigma=sig,
                             e_logMtot=2 * eV[i] / V[i] / math.log(10), e_logMb=0.1 * min(fst, 1.0),
                             sigma_def="V_flat/sqrt2 (V_last/sqrt2 if no V_flat)", src="Lelli+2016 SPARC mass models",
                             sel="HI rotation curve quality Q<=2, inc>=30; radius: last point / point nearest R_eff[3.6]"))
    return rows

def dt(dl):
    rows = []
    tex = (GS / "arxiv-2109.03828/paper_ss.tex").read_text()
    body = tex.split(r"\label{tab:sample}")[1].split("Discarded galaxies")[0]
    for row in body.split(r"\\"):
        c = [x.strip() for x in row.split("&")]
        if len(c) < 10 or not re.match(r"^(2MASX|SDSS)", c[0]): continue
        m = re.match(r"(\d+)\s*\$\\pm\$\s*(\d+)", c[7]); v, ev = float(m.group(1)), float(m.group(2))
        lj = float(re.match(r"([\d.]+)", c[9]).group(1))
        Ms = 10 ** (float(c[3]) + dl); Mb = Ms * 1.0 + 0.14 * 10 ** float(c[3])
        rows.append((c[0].replace("$-$", "-"), v, ev, lj, Mb, Ms, "DT21"))
    t23 = (GS / "arxiv-2207.02906/paper_ssvla.tex").read_text()
    s = t23[t23.index(r"\label{tab:sample}"):]; s = s[:s.index(r"\end{tabular}")]
    mass = {}
    for row in s.split(r"\\"):
        c = [x.strip() for x in row.split("&")]
        nm = re.sub(r"\$.*", "", c[0].split("\n")[-1]).strip()
        if len(c) == 5 and re.match(r"^(NGC|UGC)", nm): mass[nm] = (float(c[3]), float(c[4]))
    for row in (GS / "arxiv-2207.02906/table_dyn.tex").read_text().split(r"\\"):
        c = [x.strip() for x in row.split("&")]
        nm = c[0].split("\n")[-1].strip()
        if len(c) < 5 or nm not in mass: continue
        m = re.match(r"\$(\d+)\\pm(\d+)\$", c[1]); v, ev = float(m.group(1)), float(m.group(2))
        lj = float(re.match(r"\$([\d.]+)", c[2]).group(1))
        ms, mg = mass[nm]; Ms = 10 ** (ms + dl)
        rows.append((nm, v, ev, lj, Ms + 10 ** mg, Ms, "DT23"))
    out = []
    for nm, v, ev, lj, Mb, Ms, src in rows:
        Rd = 10 ** lj / (2 * v); r = 3 * Rd
        Mbr = 0.80 * Mb                       # exponential disk: 80% inside 3 R_d
        Mt = v ** 2 * r / (G * MK) * 1e6
        out.append(dict(cls="giant_spirals", name=nm, z=0.0, r=r, Mb=Mbr, Mtot=Mt, sigma=v / math.sqrt(2),
                        e_logMtot=2 * ev / v / math.log(10), e_logMb=0.2,
                        sigma_def="V_flat/sqrt2", src=("Di Teodoro+2021 Table 1" if src == "DT21" else "Di Teodoro+2023 tab:sample+tab:dynquant"),
                        sel="stellar mass (WISE W1, log M*>~11) [r = 3 R_d with R_d = j*/(2 V_flat) ASSUMED; M_b(<r)=0.8 M_b ASSUMED]"))
    return out

def atlas(dl):
    src = T / "sources/atlas3d"
    def load(fn, ncol):
        d = {}
        for ln in open(src / fn):
            if ln.startswith("#") or not ln.strip(): continue
            s = ln.split(); d[s[0]] = [float(x) if x.strip("-") else np.nan for x in s[1:ncol]]
        return d
    t15 = load("Cappellari2013a_Atlas3D_Paper15_Table1.txt", 16); t20 = load("Cappellari2013b_Atlas3D_Paper20_Table1.txt", 7)
    t1 = load("Cappellari2011a_Atlas3D_Paper1_Table3.txt", 13)
    out = []
    for g, a in t15.items():
        if g not in t20 or g not in t1: continue
        logsig, _, _, _, mlj, _, q, _, logRe, _, _, _, _, _, logL = a[:15][:15] if False else a[:14] + [a[13]]
        logsig, mlj, q, logRe, logL = a[0], a[4], a[6], a[8], a[13]
        mls = t20[g][3]
        if not (q >= 1 and np.isfinite(mlj) and np.isfinite(mls) and np.isfinite(logL)): continue
        Re = 10 ** logRe / 206265.0 * t1[g][6] * 1e3
        Lin = 0.42 * 10 ** logL
        Mt = 10 ** mlj * Lin; Mb = 10 ** (mls - 0.20 + dl) * Lin          # Kroupa baseline
        out.append(dict(cls="ATLAS3D_Re", name=g, z=0.0, r=Re, Mb=Mb, Mtot=Mt, sigma=10 ** logsig,
                        e_logMtot=0.05, e_logMb=0.10, sigma_def="sigma_e (luminosity-weighted, within R_e)",
                        src="Cappellari+2013a,b Tables 1; Cappellari+2011a Table 3 (distances)",
                        sel="volume-limited K-band M_K<-21.5 ETGs; JAM quality>=1; M_tot=(M/L)_JAM L(<r=R_e), stars Kroupa=(M/L)_Salp-0.2dex"))
    return out

def clusters(dl, hse):
    rows = json.load(open(T / "t4_systems.json"))
    drop = {("S09", "MKW4"), ("S09", "A1991"), ("G13", "Abell0478"), ("G13", "Abell2029"), ("G13", "Abell2390")}
    rows = [r for r in rows if (r["sample"], r["name"]) not in drop]
    g = [r for r in rows if r["sample"] == "G13" and r["fstar500"]]
    sl, ic = np.polyfit(np.log10([r["M500"] / 1e14 for r in g]), np.log10([r["fstar500"] for r in g]), 1)
    out = []
    srcs = dict(V06="Vikhlinin+2006 Table 3", S09="Sun+2009 Table 3", L15="Lovisari+2015 Table 3", G13="Gonzalez+2013 Tables 3,4")
    for r in rows:
        fs5 = (r.get("fstar500") or 10 ** ic * (r["M500"] / 1e14) ** sl) * 10 ** dl
        M5 = r["M500"] * hse
        sig = math.sqrt(G * M5 * MSUN / (2 * r["r500"] * KPC)) / 1e3
        meas = []
        meas.append(("GC_r500", r["r500"], r["M500"], r["fg500"], fs5, r["eM500"] / r["M500"], r["efg500"] / r["fg500"]))
        if "M2500" in r:
            meas.append(("GC_r2500", r["r2500"], r["M2500"], r["fg2500"], 1.5 * fs5, r["eM2500"] / r["M2500"], r["efg2500"] / r["fg2500"]))
        for cls, rr, M, fg, fs, eM, efg in meas:
            Mb = M * (fg + fs); Mt = M * hse
            out.append(dict(cls=cls, name=r["name"], z=r["z"], r=rr, Mb=Mb, Mtot=Mt, sigma=sig,
                            e_logMtot=eM / math.log(10), e_logMb=math.hypot(efg * fg, 0.3 * fs) / (fg + fs) / math.log(10),
                            sigma_def="sqrt(G M500/(2 r500)) (repository convention g=2 sigma^2/r)", src=srcs[r["sample"]],
                            sel="X-ray flux/luminosity-selected, hydrostatic masses; stars from Gonzalez+2013 fit (x1.5 inside r2500) unless measured",
                            subsample=r["sample"]))
    return out

def highz():
    out = []
    L = [l for l in open(T.parent / "accel/data/rc100_table3.csv") if not l.startswith("#")]
    hdr = L[0].strip().split(","); seen = set()
    for l in L[1:]:
        d = dict(zip(hdr, l.strip().split(",")))
        Re, Vc, f = float(d["Re"]), float(d["Vc"]), float(d["fDM"])
        Mt = Vc ** 2 * Re / (G * MK) * 1e6; Mb = (1 - f) * Mt
        seen.add(re.sub(r"[ _\-]", "", d["name"]).upper())
        out.append(dict(cls="highz_RC100", name=d["name"], z=float(d["z"]), r=Re, Mb=Mb, Mtot=Mt, sigma=Vc / math.sqrt(2),
                        e_logMtot=2 * float(d["e_Vc"]) / Vc / math.log(10), e_logMb=float(d["e_fDM"]) / max(1 - f, 0.05) / math.log(10),
                        sigma_def="V_c(R_e)/sqrt2", src="Nestor Shachar+2023 Table 3 (transcribed by accel thread, S/threads/accel/data/rc100_table3.csv)",
                        sel="mass-selected SFGs, z 0.6-2.5, resolved RC quality; M_b(<R_e)=(1-f_DM) M_tot from the published decomposition"))
    return out

def build(dl=0.0, hse=1.0, with_highz=True):
    rows = sparc(dl) + dt(dl) + atlas(dl) + clusters(dl, hse)
    if with_highz: rows += highz()
    for d in rows:
        r, Mb, Mt = d["r"], d["Mb"], d["Mtot"]
        d["g_b"] = gN(Mb, r); d["g_tot"] = gN(Mt, r)
        d["deltaA"] = Mt / Mb - float(nu(d["g_b"] / A0))
        gn = float(solve_gN(d["g_tot"])[0]); Mn = gn * (r * KPC) ** 2 / G / MSUN
        d["M_extraB"] = Mn - Mb; d["yB"] = Mn / Mb - 1
    return rows

if __name__ == "__main__":
    import csv
    rows = build()
    cols = ["cls", "name", "z", "r", "Mb", "Mtot", "e_logMb", "e_logMtot", "sigma", "g_b", "g_tot", "deltaA", "M_extraB", "yB", "sigma_def", "src", "sel"]
    with open(HERE / "unified_table.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(cols)
        for d in rows: w.writerow([("%.5g" % d[c]) if isinstance(d[c], float) else d[c] for c in cols])
    from collections import Counter
    cnt = Counter(d["cls"] for d in rows)
    for k, v in cnt.items():
        sub = [d for d in rows if d["cls"] == k]
        print(f"{k:14s} n={v:4d}  median sigma {np.median([d['sigma'] for d in sub]):6.0f}  median r {np.median([d['r'] for d in sub]):8.1f} kpc  "
              f"median log g_b/a0 {np.median([math.log10(d['g_b']/A0) for d in sub]):+.2f}  median deltaA {np.median([d['deltaA'] for d in sub]):+.2f}  median yB {np.median([d['yB'] for d in sub]):+.2f}")
