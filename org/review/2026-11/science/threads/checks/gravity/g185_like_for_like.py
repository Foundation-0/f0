"""Like-for-like comparison on the 60-system subset: model mass ratio against the table's mass ratio.
Grid of chi-squared over the dust-to-baryon ratio D and the threshold sigma_J. Uses the functions of
g185_independent.py and the repository's data table (wave7 build_catalog), imported from the pinned copy in unified/repo_copy.
Usage: python3 g185_like_for_like.py [folder with the repository scripts] (default: unified/repo_copy, made by fetch_sources.py)"""
import importlib.util, math, pathlib, sys
here = pathlib.Path(__file__).resolve().parent
repo = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else here / "unified" / "repo_copy"
spec = importlib.util.spec_from_file_location("g185", here / "g185_independent.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
spec = importlib.util.spec_from_file_location("w7data", repo / "wave7_group_cluster_threshold_audit.py")
w7 = importlib.util.module_from_spec(spec); spec.loader.exec_module(w7)
clean = [r for r in w7.build_catalog() if r["cat"] not in ("Milgrom2019_opt", "Milgrom2019_rich")]
print("Like-for-like comparison (mass ratio against mass ratio), 60-system subset")
print("chi2 as a function of the dust-to-baryon ratio D and the threshold sigma_J")
Ds = (3.0, 3.5, 4.0, 4.5, 5.0)
print("sigma_J" + "".join(f"  D={d:4.1f}" for d in Ds))
best = (1e99, None, None)
for sj in (120, 150, 170, 185.59, 200, 220, 250, 300):
    vals = []
    for d in Ds:
        c = g.chi2(clean, lambda s, d=d, sj=sj: math.log10(g.model_ratios(s, sj, d)[1]))
        vals.append(c)
        if c < best[0]: best = (c, sj, d)
    print(f"{sj:7.2f}" + "".join(f"  {v:6.1f}" for v in vals))
print(f"best on this grid: chi2 {best[0]:.2f} at sigma_J={best[1]:g}, D={best[2]:.1f} (two fitted parameters, N=60)")
dust = (1 - 0.105) / 0.105
c1 = g.chi2(clean, lambda s: math.log10(g.model_ratios(s, 185.59, dust)[1]))
c0 = g.chi2(clean, lambda s: math.log10(g.model_ratios(s, 185.59, dust)[0]))
print(f"claim as stated (D={dust:.3f} fixed, sigma_J=185.59): chi2 {c1:.2f} like for like; {c0:.2f} as the scripts compare")
