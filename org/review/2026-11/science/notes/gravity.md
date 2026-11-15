# Note: gravity

Pinned head `gravity@8f96c4b`. Verdicts are in `verdicts.csv`. Marks: **[F]** fact, **[I]** inference. This note cites `ties.md` (draft PR 53) and `recheck-1114.md` (draft PR 54).

## What was run

| Check | Command | Result |
|---|---|---|
| Every wave script | `python3 <script> --check`, nine scripts, fresh copy | all exit 0, certificates byte-identical |
| Waves 1 and 2 | `python3 verify_all.py --check` | exit 0. This mode rewrites the certificate and does not compare it |
| Lean | `lake build`, then `#print axioms` on all 32 theorems | builds. Standard axioms only |
| Checksums | all 39 entries of `SHA256SUMS` | all match |
| Independent recomputation | `python3 -I checks/g185_independent.py <gravity>` | output in `checks/g185_independent.out`. Floating point, and it prints numbers instead of rejecting input. Needs NumPy and SciPy |
| Like-for-like fit | `python3 checks/g185_like_for_like.py <gravity>` | regenerates `checks/g185_like_for_like.out`, a chi-squared table over both parameters. It imports functions from `g185_independent.py` |

## The strongest case for the 185 km/s claims

- [F] The collapse scale is computed correctly. Separate code gives 185.59 km/s with the same transfer function and 186.93 with the fuller Eisenstein and Hu form.
- [F] The ledger labels the common origin of the four speeds CONJECTURE, and the README says the scripts are not parameter-free.
- [F] A trapping threshold near 185 to 200 km/s does describe the 60-system table. That holds as the scripts compare and also like for like.
- [I] So the idea that extra mass switches on in systems above roughly 190 km/s is a fair reading of this table. It restates the known result that modified gravity fits galaxies and falls short in groups and clusters.

## What does not hold

1. **"Zero fitted parameters" (C-26).** [F] The prediction is `log10(g_tot / (g_b nu(g_b/a_0)))`, a ratio of accelerations (`wave10...py:233`). The table holds ratios of baryonic mass: `(v_obs/v_MOND)^4` for galaxies (`wave7...py:48`), MOND mass over baryonic mass for the X-ray systems (`:95`), and needed over assumed baryonic acceleration for the lensing clusters (`:119`).

   [I] The two ratios agree only when g_b is well above a_0. In this model g_b at 250 kpc stays below half of a_0 for every system in the table. [F] With the stated inputs the like-for-like chi-squared is 256.53 on 60 systems, against 60.26 as compared. With the dark-to-baryon ratio free, the table prefers about 4, not 8.52.
2. **The data table (C-21, C-22).** [F] 28 rows are computed from cluster masses with a halo model, a concentration relation and a baryon fraction of 0.130 (`wave7...py:101-119`). 10 rows are divided by `0.80 + 1.60 * min(1, max(0, (sigma - 180)/220))` (`:81`). One row is set by hand to 1.70 (`:95`). That is 39 of 126 rows that are not published values: 38 computed and one set by hand. The four KiDS rows (`:37-40`) do not match Table 2 of the cited paper.
3. **Where the onset sits.** [F] In the 60-system subset the fastest galaxy row is at 201.5 km/s and the slowest group row is at 282.5 km/s. No system lies between. [I] The fitted onset is fixed by the assumed curve shape across that gap.
4. **Independence of the four speeds (C-27).** See `ties.md`, section 5.
5. **Lens counts (C-08).** See `recheck-1114.md`, P3c.

## What would settle it

- Rebuild the table from the published tables with a pin for each row, and keep model-derived rows out of the fitted data.
- Predict the same quantity the data holds. Then fit the threshold and the dark-to-baryon ratio together and report both with intervals.
- Add systems between 200 and 280 km/s. Poor groups with lensing masses are the test.

## The other claims

[F] C-01 to C-07, C-09 to C-20, C-24, C-25 and C-28 to C-33 regenerate from the scripts. They were not recomputed with separate code, apart from three hand checks: `c H_0 / (2 pi) = 1.0422e-10` at 67.4, the crossover `g_b = 0.02897 a_0` in C-23, and the string tension conversion in C-12. Their labels describe evaluations of published equations, and this pass found no reason to change them.

The review dispositions D01 to D09 limit claims C-28 to C-33. [F] The ledger text for those claims carries the limits. The published page does not (`recheck-1114.md`, P3a).
