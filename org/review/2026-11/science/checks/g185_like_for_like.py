"""
Regenerates g185_like_for_like.out: the like-for-like comparison for gravity C-26 and C-27.
It scores the 60-system clean subset with the model's mass ratio against the table's mass ratio,
over a grid of the dust-to-baryon ratio D and the threshold sigma_J.
Functions come from g185_independent.py in this directory.
Usage: python3 g185_like_for_like.py <path-to-gravity-clone> > g185_like_for_like.out
Needs NumPy and SciPy.
"""
import importlib.util, math, os, sys

here = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("g185_independent", os.path.join(here, "g185_independent.py"))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

SIGMA_J = (120.0, 150.0, 170.0, 185.59, 200.0, 220.0, 250.0, 300.0)
DUST = (3.0, 3.5, 4.0, 4.5, 5.0)
CLAIM_SIGMA_J = 185.59
CLAIM_DUST = (1 - 0.105) / 0.105


def clean_rows(repo):
    spec = importlib.util.spec_from_file_location("w7data", repo + "/wave7_group_cluster_threshold_audit.py")
    w7 = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(w7)
    return [r for r in w7.build_catalog() if r["cat"] not in ("Milgrom2019_opt", "Milgrom2019_rich")]


def chi2_mass(rows, sigma_j, dust):
    """chi2 with R_mass, the quantity the data table holds."""
    return g.chi2(rows, lambda s: math.log10(g.model_ratios(s, sigma_j, dust)[1]))


def chi2_acc(rows, sigma_j, dust):
    """chi2 with R_acc, the quantity the repository's scripts compare."""
    return g.chi2(rows, lambda s: math.log10(g.model_ratios(s, sigma_j, dust)[0]))


def main(repo):
    rows = clean_rows(repo)
    print("Like-for-like comparison (mass ratio against mass ratio), 60-system subset")
    print("chi2 as a function of the dust-to-baryon ratio D and the threshold sigma_J")
    print("sigma_J" + "".join(f"  D={d:4.1f}" for d in DUST))
    best = None
    for sj in SIGMA_J:
        vals = [chi2_mass(rows, sj, d) for d in DUST]
        for d, v in zip(DUST, vals):
            if best is None or v < best[0]:
                best = (v, sj, d)
        print(f"{sj:7.2f}" + "".join(f"{v:8.1f}" for v in vals))
    print(f"best on this grid: chi2 {best[0]:.2f} at sigma_J={best[1]:.0f}, D={best[2]:.1f} (two fitted parameters, N={len(rows)})")
    print(f"claim as stated (D={CLAIM_DUST:.3f} fixed, sigma_J={CLAIM_SIGMA_J}): chi2 {chi2_mass(rows, CLAIM_SIGMA_J, CLAIM_DUST):.2f} like for like; "
          f"{chi2_acc(rows, CLAIM_SIGMA_J, CLAIM_DUST):.2f} as the scripts compare")


if __name__ == "__main__":
    main(sys.argv[1])
