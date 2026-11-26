"""Test 1. Does extra mass switch on in galaxies whose speed is above the threshold?

Model under test (gravity@8f96c4b:wave10_covariant_jeans_unification.py:219-231):
    g_tot = g_b * ( nu(g_b/a0) + f_trap * R ),  f_trap = max(0, 1 - (sigma_J/sigma)^2),
    nu(y) = 1/(1 - exp(-sqrt(y))),  sigma = V_flat/sqrt(2) for galaxies (wave7...py:48).
Two parameter sets:
    A  "zero fitted parameters": sigma_J = 185.59 km/s, R = 8.524   (the repository's claim C-26)
    B  best like-for-like fit of our science pass: sigma_J = 200 km/s, R = 4.0

Data: SPARC (Lelli, McGaugh, Schombert 2016, AJ 152, 157), tables fetched from
https://astroweb.case.edu/SPARC/ on 2026-11-15. Mass-to-light 0.5 (disk) and 0.7 (bulge) at 3.6 micron,
the values of McGaugh, Lelli, Schombert 2016 (PRL 117, 201101). Quality cuts as in that paper:
Q <= 2, inclination >= 30 deg. Every radius with a positive baryonic acceleration is used.

For each point:  resid = log10(g_obs) - log10(g_b * nu(g_b/a0))   (0 if the point sits on the RAR)
Model prediction: pred  = log10( (nu + f_trap R) / nu ).
"""
import math, sys, statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "sources" / "sparc"
A0 = 1.20e-10
KPC = 3.085677581491367e19
YD, YB = 0.5, 0.7


def nu(y):
    s = math.sqrt(max(y, 0.0))
    return 1.0 if s > 40 else 1.0 / (1.0 - math.exp(-s))


def read_table1():
    out = {}
    lines = (SRC / "SPARC_Lelli2016c.mrt").read_text().splitlines()
    start = max(i for i, l in enumerate(lines) if l.startswith("-----")) + 1
    for l in lines[start:]:
        p = l.split()
        if len(p) < 18:
            continue
        out[p[0]] = dict(T=int(p[1]), D=float(p[2]), inc=float(p[5]), L36=float(p[7]),
                         vflat=float(p[15]), e_vflat=float(p[16]), Q=int(p[17]))
    return out


def read_table2():
    pts = {}
    lines = (SRC / "MassModels_Lelli2016c.mrt").read_text().splitlines()
    start = max(i for i, l in enumerate(lines) if l.startswith("-----")) + 1
    for l in lines[start:]:
        p = l.split()
        if len(p) < 8:
            continue
        name = p[0]
        R, vobs, ev, vgas, vdisk, vbul = (float(x) for x in p[2:8])
        pts.setdefault(name, []).append((R, vobs, ev, vgas, vdisk, vbul))
    return pts


def main():
    t1, t2 = read_table1(), read_table2()
    sets = {"A (185.59, 8.524)": (185.59, 8.524), "B (200, 4.0)": (200.0, 4.0)}
    rows = []  # per point
    for name, g in t1.items():
        if g["Q"] > 2 or g["inc"] < 30.0 or g["vflat"] <= 0 or name not in t2:
            continue
        sig = g["vflat"] / math.sqrt(2.0)
        for (R, vobs, ev, vgas, vdisk, vbul) in t2[name]:
            vb2 = vgas * abs(vgas) + YD * vdisk * abs(vdisk) + YB * vbul * abs(vbul)
            if vb2 <= 0 or vobs <= 0 or R <= 0:
                continue
            gb = vb2 * 1e6 / (R * KPC)
            go = vobs ** 2 * 1e6 / (R * KPC)
            y = gb / A0
            resid = math.log10(go) - math.log10(gb * nu(y))
            e_resid = 2.0 * ev / vobs / math.log(10.0)
            preds = {}
            for k, (sj, RR) in sets.items():
                f = max(0.0, 1.0 - (sj / sig) ** 2)
                preds[k] = math.log10((nu(y) + f * RR) / nu(y))
            rows.append(dict(name=name, sig=sig, R=R, y=y, resid=resid, e=e_resid, **preds))

    gal = sorted({(r["name"], r["sig"]) for r in rows}, key=lambda t: t[1])
    print(f"galaxies after cuts: {len(gal)}   points: {len(rows)}")
    print(f"RAR residual, all points: mean {st.mean(r['resid'] for r in rows):+.4f} dex, "
          f"sd {st.pstdev([r['resid'] for r in rows]):.4f} dex")

    print("\nBy speed bin (sigma = V_flat/sqrt 2, km/s). Residuals in dex; 'pred' is the model's mean prediction.")
    print(f"{'bin':>12} {'gal':>4} {'pts':>5} {'mean resid':>11} {'sem(gal)':>9} {'pred A':>8} {'pred B':>8}")
    edges = [0, 60, 100, 140, 170, 185.59, 200, 215, 400]
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = [r for r in rows if lo <= r["sig"] < hi]
        if not sel:
            continue
        names = sorted({r["name"] for r in sel})
        gm = [st.mean(r["resid"] for r in sel if r["name"] == n) for n in names]
        sem = st.pstdev(gm) / math.sqrt(len(gm)) if len(gm) > 1 else float("nan")
        pa = st.mean(r["A (185.59, 8.524)"] for r in sel)
        pb = st.mean(r["B (200, 4.0)"] for r in sel)
        print(f"{lo:5.0f}-{hi:<6.0f} {len(names):4d} {len(sel):5d} {st.mean(gm):+11.4f} {sem:9.4f} {pa:8.4f} {pb:8.4f}")

    print("\nGalaxies above 185.59 km/s, one line each (mean over the galaxy's points):")
    print(f"{'galaxy':>12} {'Vflat':>6} {'sigma':>6} {'pts':>4} {'resid':>8} {'pred A':>7} {'pred B':>7}")
    above = [n for n, s in gal if s > 185.59]
    gm_obs, gm_a, gm_b = [], [], []
    for n in above:
        sel = [r for r in rows if r["name"] == n]
        o = st.mean(r["resid"] for r in sel)
        a = st.mean(r["A (185.59, 8.524)"] for r in sel)
        b = st.mean(r["B (200, 4.0)"] for r in sel)
        gm_obs.append(o); gm_a.append(a); gm_b.append(b)
        print(f"{n:>12} {t1[n]['vflat']:6.1f} {sel[0]['sig']:6.1f} {len(sel):4d} {o:+8.4f} {a:7.4f} {b:7.4f}")
    n = len(above)
    sem = st.pstdev(gm_obs) / math.sqrt(n)
    print(f"\nabove threshold: {n} galaxies. observed mean residual {st.mean(gm_obs):+.4f} +/- {sem:.4f} dex (galaxy-to-galaxy)")
    print(f"model A predicts {st.mean(gm_a):+.4f} dex, model B predicts {st.mean(gm_b):+.4f} dex")
    # chi-squared per galaxy using the galaxy-to-galaxy scatter of the below-threshold sample as the error
    below = [nm for nm, s in gal if s <= 185.59]
    gb_res = [st.mean(r["resid"] for r in rows if r["name"] == nm) for nm in below]
    s_gal = st.pstdev(gb_res)
    print(f"galaxy-to-galaxy scatter of mean residual below threshold: {s_gal:.4f} dex ({len(below)} galaxies)")
    for label, pred in (("RAR only", [0.0] * n), ("model A", gm_a), ("model B", gm_b)):
        chi2 = sum(((o - p) / s_gal) ** 2 for o, p in zip(gm_obs, pred))
        print(f"  chi2 {label:9s} = {chi2:8.2f} on {n} galaxies")
    # outer points only: the model's own choice of large radius
    print("\nSame, last measured point of each above-threshold galaxy:")
    for nme in above:
        sel = sorted((r for r in rows if r["name"] == nme), key=lambda r: r["R"])[-1]
        print(f"{nme:>12} R={sel['R']:6.1f} kpc y={sel['y']:.3f} resid {sel['resid']:+.4f} +/- {sel['e']:.4f}  pred A {sel['A (185.59, 8.524)']:.4f}  pred B {sel['B (200, 4.0)']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
