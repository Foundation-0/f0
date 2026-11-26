"""Test 2. Second sample for the threshold: 43 giant spirals with V_flat from 223 to 530 km/s.

Data: Di Teodoro et al. 2021, "Rotation curves and scaling relations of extremely massive spiral galaxies",
arXiv:2109.03828, Table 1 (TeX source fetched 2026-11-15). Columns used: log stellar mass (WISE W1, M/L = 0.6,
error about 0.2 dex) and V_flat with its error. The paper gives gas fractions of 0.08 to 0.20 for the sample
(its section on the baryonic relation), no per-galaxy value, so M_b = M_star * (1 + 0.14) here.
Comparison sample: SPARC (same files as test 1), M_b = 0.5 L[3.6] + 1.33 M_HI.

Statistic, per galaxy:  d = log10(V_flat) - 0.25 log10(G M_b a0).
Under the RAR alone d is the same for all speeds (apart from a small finite-radius term). The zero point c0 is the
mean d of SPARC galaxies with 100 <= sigma < 185.59 km/s (sigma = V_flat/sqrt 2).
Model prediction for the extra offset of a galaxy above threshold, at the radius where V_flat is read:
    0.5 log10( (nu(y) + f_trap R) / nu(y) ),  y = g_b/a0 there.  y is not tabulated for this sample, so the
prediction is given for y = 0.1 and y = 0.3, which bracket optical radii of 30 to 60 kpc for these masses.
"""
import math, re, statistics as st, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
G, A0, MSUN = 6.67430e-11, 1.20e-10, 1.98847e30
SJ = 185.59


def nu(y):
    s = math.sqrt(y)
    return 1.0 / (1.0 - math.exp(-s))


def d_stat(v_kms, mb_msun):
    return math.log10(v_kms * 1e3) - 0.25 * math.log10(G * mb_msun * MSUN * A0)


def sparc():
    out = []
    lines = (HERE / "sources/sparc/SPARC_Lelli2016c.mrt").read_text().splitlines()
    start = max(i for i, l in enumerate(lines) if l.startswith("-----")) + 1
    for l in lines[start:]:
        p = l.split()
        if len(p) < 18:
            continue
        inc, L, mhi, vf, ev, q = float(p[5]), float(p[7]), float(p[13]), float(p[15]), float(p[16]), int(p[17])
        if q > 2 or inc < 30 or vf <= 0:
            continue
        mb = (0.5 * L + 1.33 * mhi) * 1e9
        out.append((p[0], vf, ev, mb))
    return out


def diteodoro():
    out = []
    tex = (HERE / "sources/arxiv-2109.03828/paper_ss.tex").read_text()
    body = tex.split(r"\label{tab:sample}")[1].split("Discarded galaxies")[0]
    for row in body.split(r"\\"):
        c = [x.strip() for x in row.split("&")]
        if len(c) < 9 or not re.match(r"^(2MASX|SDSS)", c[0]):
            continue
        logm = float(c[3])
        m = re.match(r"(\d+)\s*\$\\pm\$\s*(\d+)", c[7])
        out.append((c[0][:22], float(m.group(1)), float(m.group(2)), logm))
    return out


def pred(sig, sj, R, y):
    f = max(0.0, 1.0 - (sj / sig) ** 2)
    return 0.5 * math.log10((nu(y) + f * R) / nu(y))


def main():
    sp = sparc()
    ref = [d_stat(v, mb) for _, v, _, mb in sp if 100 <= v / math.sqrt(2) < SJ]
    c0 = st.mean(ref)
    s0 = st.pstdev(ref)
    print(f"SPARC reference (100 <= sigma < 185.59): {len(ref)} galaxies, c0 = {c0:.4f}, scatter {s0:.4f} dex in V")
    print("\nSPARC by speed bin: mean of d - c0 (dex in V)")
    for lo, hi in [(0, 60), (60, 100), (100, 140), (140, 185.59), (185.59, 215), (215, 400)]:
        sel = [d_stat(v, mb) - c0 for _, v, _, mb in sp if lo <= v / math.sqrt(2) < hi]
        if sel:
            print(f"  sigma {lo:6.1f}-{hi:6.1f}: n={len(sel):3d} mean {st.mean(sel):+.4f} sem {st.pstdev(sel)/math.sqrt(len(sel)):.4f}")

    dt = diteodoro()
    print(f"\nDi Teodoro et al. 2021: {len(dt)} galaxies read from Table 1")
    for ml_label, ml_shift in (("M/L 0.6 as published", 0.0), ("M/L 0.5, the SPARC convention", math.log10(0.5 / 0.6))):
        print(f"\n== stellar masses with {ml_label}; gas fraction 0.14 ==")
        rows = []
        for name, v, ev, logm in dt:
            mb = 10 ** (logm + ml_shift) * 1.14
            sig = v / math.sqrt(2)
            d = d_stat(v, mb) - c0
            e = math.hypot(ev / v / math.log(10), 0.25 * 0.2)   # V error and 0.2 dex in mass
            rows.append((name, v, sig, d, e))
        print(f"{'bin (sigma)':>14} {'n':>3} {'mean d':>8} {'sem':>7} | pred A y=.1 y=.3 | pred B y=.1 y=.3")
        for lo, hi in [(150, 185.59), (185.59, 200), (200, 215), (215, 235), (235, 260), (260, 400)]:
            sel = [r for r in rows if lo <= r[2] < hi]
            if not sel:
                continue
            m = st.mean(r[3] for r in sel)
            sem = math.sqrt(sum(r[4] ** 2 for r in sel)) / len(sel)
            pa = [st.mean(pred(r[2], 185.59, 8.524, y) for r in sel) for y in (0.1, 0.3)]
            pb = [st.mean(pred(r[2], 200.0, 4.0, y) for r in sel) for y in (0.1, 0.3)]
            print(f"{lo:6.1f}-{hi:6.1f} {len(sel):3d} {m:+8.4f} {sem:7.4f} |      {pa[0]:.3f} {pa[1]:.3f} |      {pb[0]:.3f} {pb[1]:.3f}")
        allm = st.mean(r[3] for r in rows)
        sem = math.sqrt(sum(r[4] ** 2 for r in rows)) / len(rows)
        print(f"all {len(rows)}: mean d - c0 = {allm:+.4f} +/- {sem:.4f} (statistical); sample scatter {st.pstdev([r[3] for r in rows]):.4f}")
        for label, sj, R in (("RAR only", 1e9, 0.0), ("model A", 185.59, 8.524), ("model B", 200.0, 4.0)):
            for y in (0.1, 0.3):
                chi2 = sum(((r[3] - pred(r[2], sj, R, y)) / r[4]) ** 2 for r in rows)
                print(f"   chi2 {label:8s} y={y}: {chi2:8.2f} on {len(rows)}")
                if R == 0.0:
                    break
        # slope of offset against log sigma within the sample (model predicts a steep rise)
        xs = [math.log10(r[2]) for r in rows]; ys = [r[3] for r in rows]
        mx, my = st.mean(xs), st.mean(ys)
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        res = [y - my - b * (x - mx) for x, y in zip(xs, ys)]
        sb = math.sqrt(sum(r * r for r in res) / (len(xs) - 2) / sum((x - mx) ** 2 for x in xs))
        pa = [pred(r[2], 185.59, 8.524, 0.2) for r in rows]; pb = [pred(r[2], 200.0, 4.0, 0.2) for r in rows]
        ba = sum((x - mx) * (y - st.mean(pa)) for x, y in zip(xs, pa)) / sum((x - mx) ** 2 for x in xs)
        bb = sum((x - mx) * (y - st.mean(pb)) for x, y in zip(xs, pb)) / sum((x - mx) ** 2 for x in xs)
        print(f"   slope of offset vs log sigma: observed {b:+.3f} +/- {sb:.3f}; model A {ba:+.3f}; model B {bb:+.3f} (y=0.2); RAR only 0")
    return 0


if __name__ == "__main__":
    sys.exit(main())
