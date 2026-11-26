"""Test 1b. SPARC residuals from the RAR, binned by baryonic mass instead of speed.

Binning by V_flat selects galaxies whose speed is high for their mass, which by itself produces a positive
residual (the statistic contains V). Baryonic mass does not enter the residual with that sign, so mass bins are
the fair split. Threshold in mass: (G M_b a0)^(1/4) / sqrt 2 = sigma_J.
Same data, cuts and mass-to-light ratios as t1_sparc_threshold.py. Also reports outer points only (y < 0.3).
"""
import math, statistics as st, sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import t1_sparc_threshold as t1

G, MSUN = 6.67430e-11, 1.98847e30
def m_thresh(sj): return (sj * math.sqrt(2) * 1e3) ** 4 / (G * t1.A0) / MSUN

tab1, tab2 = t1.read_table1(), t1.read_table2()
lines = (t1.SRC / "SPARC_Lelli2016c.mrt").read_text().splitlines()
start = max(i for i, l in enumerate(lines) if l.startswith("-----")) + 1
mhi = {l.split()[0]: float(l.split()[13]) for l in lines[start:] if len(l.split()) >= 18}
gal = []
for name, g in tab1.items():
    if g["Q"] > 2 or g["inc"] < 30 or name not in tab2: continue
    mb = (0.5 * g["L36"] + 1.33 * mhi[name]) * 1e9
    res_all, res_out = [], []
    for (R, vobs, ev, vgas, vdisk, vbul) in tab2[name]:
        vb2 = vgas*abs(vgas) + t1.YD*vdisk*abs(vdisk) + t1.YB*vbul*abs(vbul)
        if vb2 <= 0 or vobs <= 0: continue
        gb = vb2*1e6/(R*t1.KPC); go = vobs**2*1e6/(R*t1.KPC); y = gb/t1.A0
        r = math.log10(go) - math.log10(gb*t1.nu(y))
        res_all.append(r)
        if y < 0.3: res_out.append(r)
    if res_all:
        gal.append(dict(name=name, mb=mb, vflat=g["vflat"], r=st.mean(res_all), ro=st.mean(res_out) if res_out else None))
print(f"galaxies: {len(gal)} (Q<=2, inc>=30; V_flat not required here)")
print(f"mass thresholds: sigma_J=185.59 -> M_b = {m_thresh(185.59):.3e} Msun ; sigma_J=200 -> {m_thresh(200):.3e} Msun")
edges = [0, 1e9, 1e10, 3e10, 1e11, 2e11, m_thresh(185.59), 1e13]
print(f"{'M_b bin (Msun)':>24} {'n':>3} {'mean resid':>10} {'sem':>7} {'outer only':>10} {'sem':>7}")
for lo, hi in zip(edges[:-1], edges[1:]):
    sel = [g for g in gal if lo <= g["mb"] < hi]
    if not sel: continue
    a = [g["r"] for g in sel]; o = [g["ro"] for g in sel if g["ro"] is not None]
    sem = lambda x: st.pstdev(x)/math.sqrt(len(x)) if len(x) > 1 else float("nan")
    print(f"{lo:11.2e}-{hi:11.2e} {len(sel):3d} {st.mean(a):+10.4f} {sem(a):7.4f} {st.mean(o):+10.4f} {sem(o):7.4f}")
top = sorted([g for g in gal if g["mb"] >= 2e11], key=lambda g: g["mb"])
print("\nGalaxies with M_b >= 2e11 Msun:")
for g in top:
    print(f"  {g['name']:>12} M_b={g['mb']:.2e} Vflat={g['vflat']:6.1f} resid={g['r']:+.4f} outer={g['ro'] if g['ro'] is None else round(g['ro'],4)}")
allr = [g["r"] for g in gal if g["mb"] < 2e11]
print(f"\nscatter of galaxy mean residual below 2e11: {st.pstdev(allr):.4f} dex; mean {st.mean(allr):+.4f}")
