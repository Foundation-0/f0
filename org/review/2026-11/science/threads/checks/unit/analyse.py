"""Analyse the saved samples (tags w*).  Prints tables and writes analysis.json."""
import glob, json, os, re
from collections import defaultdict
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
FULL = {6: 24, 7: 56, 8: 136, 9: 344, 10: 880, 11: 2288}
CELLS = ["e0.001", "e0.003", "e0.01", "e0.03", "e0.1", "e0.3", "e1", "far"]


def load():
    D = defaultdict(list)
    for f in glob.glob(os.path.join(HERE, "samples", "n*_*_w*.json")):
        m = re.match(r"n(\d+)_(.+)_(w\w+)\.json", os.path.basename(f))
        n, cell = int(m.group(1)), m.group(2)
        try:
            D[(n, cell)] += json.load(open(f))
        except json.JSONDecodeError:
            pass
    return D


def ci(k, n):
    if n == 0:
        return (float("nan"), float("nan"))
    r = stats.binomtest(k, n).proportion_ci(confidence_level=0.95, method="exact")
    return (r.low, r.high)


def main():
    D = load()
    out = {"cells": {}, "tests": {}}
    print("n  cell     tot  ok  rej%   meanfrac  q10   q50   q90   allreal  share  95%CI           rej_meanfrac_found")
    for n in sorted(FULL):
        for cell in CELLS:
            R = D.get((n, cell), [])
            if not R:
                continue
            ok = [r for r in R if r["ok"]]
            bad = [r for r in R if not r["ok"]]
            N = R[0]["N"]
            fr = np.array([r["nreal"] / N for r in ok])
            ar = int(sum(r["nreal"] == N for r in ok))
            lo, hi = ci(ar, len(ok))
            badfr = np.mean([r["nreal"] / max(r["nfound"], 1) for r in bad]) if bad else float("nan")
            hist = np.bincount((2 * np.array([r["nreal"] for r in ok])).astype(int), minlength=FULL[n] + 1) if ok else []
            rec = dict(total=len(R), ok=len(ok), rej_share=len(bad) / len(R), mean_frac=float(fr.mean()) if len(fr) else None,
                       q10=float(np.quantile(fr, .1)) if len(fr) else None, q50=float(np.median(fr)) if len(fr) else None,
                       q90=float(np.quantile(fr, .9)) if len(fr) else None, allreal=ar,
                       allreal_share=ar / len(ok) if ok else None, ci95=(lo, hi),
                       rej_found_realfrac=float(badfr),
                       allreal_share_bounds_if_rejects=((ar) / len(R), (ar + len(bad)) / len(R)),
                       counts={int(c): int(v) for c, v in enumerate(hist) if v} if ok else {})
            out["cells"][f"{n}_{cell}"] = rec
            if len(fr):
                print(f"{n:2d} {cell:7s} {len(R):4d} {len(ok):4d} {100*rec['rej_share']:5.1f}  {fr.mean():.4f}  "
                      f"{rec['q10']:.3f} {rec['q50']:.3f} {rec['q90']:.3f}  {ar:4d}  {rec['allreal_share']:.3f}  "
                      f"[{lo:.3f},{hi:.3f}]  {badfr:.3f}")
    # ---- tests ----
    print("\nNear (each eps) vs far: Mann-Whitney U on real fraction (two-sided), Fisher exact on all-real share")
    for n in sorted(FULL):
        far = [r for r in D.get((n, "far"), []) if r["ok"]]
        if not far:
            continue
        ffr = [r["nreal"] / r["N"] for r in far]
        far_ar = sum(r["nreal"] == r["N"] for r in far)
        for cell in CELLS[:-1]:
            near = [r for r in D.get((n, cell), []) if r["ok"]]
            if len(near) < 5:
                continue
            nfr = [r["nreal"] / r["N"] for r in near]
            u = stats.mannwhitneyu(nfr, ffr, alternative="two-sided")
            near_ar = sum(r["nreal"] == r["N"] for r in near)
            fe = stats.fisher_exact([[near_ar, len(near) - near_ar], [far_ar, len(far) - far_ar]])
            out["tests"][f"{n}_{cell}_vs_far"] = dict(mw_p=float(u.pvalue), fisher_p=float(fe.pvalue),
                                                      near_mean=float(np.mean(nfr)), far_mean=float(np.mean(ffr)))
            if cell in ("e0.01", "e0.001", "e1"):
                print(f"  n={n} {cell}: near mean {np.mean(nfr):.3f} vs far {np.mean(ffr):.3f}; MW p={u.pvalue:.2e}; "
                      f"all-real {near_ar}/{len(near)} vs {far_ar}/{len(far)}, Fisher p={fe.pvalue:.2e}")
    # ---- paired per-ray profiles ----
    print("\nPer-ray profiles (same direction u at every eps; rays complete at all eps in the ladder)")
    eps_cells = CELLS[:-1]
    for n in sorted(FULL):
        byk = defaultdict(dict)
        for cell in eps_cells:
            for r in D.get((n, cell), []):
                byk[r["k"]][cell] = r
        rays = [v for v in byk.values() if all(c in v and v[c]["ok"] for c in eps_cells)]
        if not rays:
            continue
        N = rays[0]["e1"]["N"]
        A = np.array([[v[c]["nreal"] for c in eps_cells] for v in rays])  # columns small eps -> large eps
        stable3 = np.mean((A[:, 0] == A[:, 1]) & (A[:, 1] == A[:, 2]))
        stable2 = np.mean(A[:, 0] == A[:, 1])
        allreal_small = int((A[:, 0] == N).sum())
        allreal_ray = int(((A[:, :3] == N).all(axis=1)).sum())
        mono = np.mean((np.diff(A, axis=1) <= 0).all(axis=1))   # nreal non-increasing as eps grows
        w = stats.wilcoxon(A[:, 0], A[:, 4]) if (A[:, 0] != A[:, 4]).any() else None
        rho = stats.spearmanr(np.tile(np.log10([1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1, 1]), len(A)), A.ravel())
        out["tests"][f"{n}_rays"] = dict(nrays=len(A), stable_last3=float(stable3), stable_last2=float(stable2),
                                         allreal_at_1em3=allreal_small, allreal_ray_1em3_to_1em2=allreal_ray,
                                         monotone_share=float(mono),
                                         wilcoxon_1em3_vs_1em1_p=(float(w.pvalue) if w else None),
                                         spearman_rho=float(rho.correlation), spearman_p=float(rho.pvalue),
                                         mean_by_eps=(A.mean(axis=0) / N).tolist())
        print(f"  n={n}: {len(A)} rays; count same at 1e-3,3e-3,1e-2: {stable3:.2f}; same at 1e-3,3e-3: {stable2:.2f}; "
              f"non-increasing in eps: {mono:.2f}; all-real at 1e-3: {allreal_small}; all-real on 1e-3..1e-2: {allreal_ray}; "
              f"Spearman(log eps, nreal) rho={rho.correlation:.3f} p={rho.pvalue:.1e}; "
              f"Wilcoxon 1e-3 vs 1e-1 p={(w.pvalue if w else float('nan')):.1e}")
    # ---- trend of the all-real share at small eps with n ----
    print("\nAll-real share at eps=1e-3 by n (exact 95% CI)")
    xs, ks, ns = [], [], []
    for n in sorted(FULL):
        R = [r for r in D.get((n, "e0.001"), []) if r["ok"]]
        if not R:
            continue
        k = sum(r["nreal"] == r["N"] for r in R)
        lo, hi = ci(k, len(R))
        print(f"  n={n}: {k}/{len(R)} = {k/len(R):.3f} [{lo:.3f}, {hi:.3f}]   mean real fraction {np.mean([r['nreal']/r['N'] for r in R]):.3f}")
        xs.append(n); ks.append(k); ns.append(len(R))
    out["trend_allreal_1e-3"] = dict(n=xs, k=ks, N=ns)
    print("\nNon-real conjugate pairs per ray (full count: pairs of realizations = N - nreal over half-solutions)")
    print("  n  cell     mean_pairs  var/mean  P(0) obs  exp(-mean)  best full real count seen")
    out["pairs"] = {}
    for n in sorted(FULL):
        for cell in ("e0.001", "e0.01", "e0.1", "e1", "far"):
            R = [r for r in D.get((n, cell), []) if r["ok"]]
            if not R:
                continue
            p = np.array([r["N"] - r["nreal"] for r in R], float)   # half-solution non-real = conjugate pairs of SE2 realizations
            mean, var = p.mean(), p.var()
            best = 2 * max(r["nreal"] for r in R)
            out["pairs"][f"{n}_{cell}"] = dict(mean=float(mean), var=float(var), p0=float((p == 0).mean()), best=int(best))
            print(f"  {n:2d} {cell:7s} {mean:10.2f}  {var/mean if mean else float('nan'):8.2f}  {(p==0).mean():8.3f}  {np.exp(-mean):10.2e}  {best}/{FULL[n]}")
    # ---- rejection vs eps and a correlation check ----
    print("\nRejected share by cell, and min separation (median) of accepted samples")
    for n in sorted(FULL):
        row = []
        for cell in CELLS:
            R = D.get((n, cell), [])
            if R:
                row.append(f"{cell}:{sum(not r['ok'] for r in R)}/{len(R)} ms={np.median([r['minsep'] for r in R if r['ok']] or [np.nan]):.1e}")
        print(f"  n={n}: " + "  ".join(row))
    json.dump(out, open(os.path.join(HERE, "analysis.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
