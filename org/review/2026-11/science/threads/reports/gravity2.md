# Gravity threshold tests T3 to T7: full report

15 November 2026. Repository head pinned by the report: gravity at 8f96c4b.

Short note for this thread: `../gravity.md`.

S is the working folder of this thread. It is archived outside the repository. Paths that start with S/ point into it. Where a file was copied into the repository, its repository path is listed at the end.

---

**Result.** Parameter set A is dead. The threshold that falls with redshift is dead under both parameter sets. Set B only survives as a constant (non-evolving) dark component that sits outside galaxy R_e and appears above roughly 230 to 345 km/s. That is close to restating MOND's known shortfall in clusters.

All scripts and their outputs are in S/threads/gravity2/. The first gravity pass (tests T1 and T2) is in S/threads/gravity/.

**A problem with set A before any data.** The repository sets R = (1 − 0.105)/0.105 at r2500 (gravity@8f96c4b:wave10_covariant_jeans_unification.py:44-45). That counts all non-baryonic mass as trapped dark mass. The formula then adds nu(y) on top, which is 3 to 5 at cluster r2500. So set A counts the MOND boost twice, and its R is about nu − 1 too large by construction.
Measured at r2500, R comes out at 4 to 7 per cluster, not 8.5. [F]/[I]

**T3. Early-type galaxies inside R_e (ATLAS3D).** 187 galaxies, 36 of them above the threshold.
- Selection: binned on sigma_e. The dynamical mass scales with sigma^2, so errors push the high bins up, the same direction as the model's signal. A null result is therefore conservative.
- Observed log(M_tot/M_star, Salpeter) is about 0.00 above the threshold. The models predict +0.75 (A) and +0.47 (B).
- A test that does not depend on the IMF compares the residual above the threshold with a 120 to 185.6 km/s control bin. The step is −0.35 ± 0.04 dex for A (9σ) and −0.11 ± 0.03 for B (3.3σ). For B at sigma_e 230 to 400 it is −0.34 ± 0.05 (6.6σ). If f_trap is computed from V_c/√2 instead, A fails at 11σ and B at 8σ. [F]
- I did not use SLACS.

**T4. Groups and clusters at r2500 and r500.** 51 systems at both radii (Vikhlinin 2006, Sun 2009, Lovisari 2015) and 63 at r500 (adding Gonzalez 2013).
- Radius test: the ratio delta2500/delta500 within one system does not depend on sigma_J. The median is 2.12, so R is not one number.
- The ratio reaches 1 only if the hydrostatic bias at r500 exceeds the bias at r2500 by about 0.23 (0.22 to 0.24 by sample). [F]
- Fit at r500: a threshold form beats a constant and a power law in all four star and bias scenarios. But the best sigma_J moves between 230 and 345 km/s, and R between 3.4 and 6.2. sigma_J = 200 is excluded in 3 of the 4 scenarios.
- Fixed A overpredicts the mass ratio, leaving residuals of −2.3 to −5.5. Fixed B leaves −1.5 to +1.8.
- No system lies between 200 and 280 km/s. The lowest is 296 km/s.
- Selection: sigma is computed from M500, which also enters M_tot/M_b, so the bias is upward.
- Weak-lensing fractions from Akino 2022 give delta500 = 2.5, 4.0 and 2.7 at 1e13, 1e14 and 1e15 Msun. delta falls at the top, which a saturating threshold cannot follow.

**T5. Top of the baryonic Tully-Fisher relation.** Errors-in-both-variables broken-line fit.
- With V_flat data (SPARC plus Di Teodoro 2021 and 2023, N = 179): best break at log M_b = 10.70, slope 0.26 to 0.31, bootstrap p ≈ 0.08. Not significant.
- With Ogle's H-alpha V_max: break at 10.85, p < 0.02.
- Either way the break is a gentle steepening 0.6 to 0.9 dex below the model's threshold masses (11.47 for A, 11.60 for B), not a jump at them.
- A's predicted jump to 435 to 535 km/s gives chi2 167 to 391, against 71 for the RAR line. B gives 47 to 56 and is not excluded here.
- Literature explanation: Di Teodoro 2021 traced Ogle's break to H-alpha V_max versus V_flat, inclinations and asymmetric emission. Also, Ogle's "10 fastest" fit selects on V, the dependent variable. [I]

**T6. High redshift (Genzel 2020 RC41, 41 galaxies, z 0.66 to 2.45. Table copied from the accel thread with credit).**
- Observed median f_DM(R_e) is 0.25. The RAR alone predicts 0.21.
- A predicts at least 0.79 and evolving B at least 0.64. 0 of 41 galaxies reach A and 2 of 41 reach evolving B.
- For A to fit, the published baryonic masses would have to be about 7 times too large.
- KMOS3D (Übler 2017, 135 galaxies) shows a total offset from the z = 0 relation of +0.09 to +0.13 dex. The model's extra offset alone would be +0.29 to +0.45 for A and +0.18 to +0.31 for B. Clean fail.

**T7. Literature.**
- MOND's cluster shortfall: Sanders 2003. Pointecouteau and Silk 2005. Tian 2020.
- Extra components only in deep potentials: about 2 eV neutrinos. 11 eV sterile neutrinos (Angus 2010). Milgrom's cluster baryonic dark matter (2008). EMOND, where a0 grows with potential depth (Zhao and Famaey 2012, 1207.6232. Hodson and Zhao 2017). Superfluid dark matter, which goes normal-phase at high velocity dispersion (Berezhiani and Khoury 2015).
- Environment results: Brouwer 2021 lensing difference between early and late types. arXiv:2603.23591 finds that only central galaxies of groups and clusters deviate from the RAR.
- Distinctive feature: the tie to the nonlinear collapse scale sigma_*(z). Five arXiv API queries found no earlier report of this tie. It is also the part T6 rejects.

| test | selection | A | B | RAR only | strength |
|---|---|---|---|---|---|
| T3 | sigma_e (bias up) | fail, 9 to 11σ | fail, 3.3 to 8σ | pass | strong / moderate to strong |
| T4 radius | within-system ratio | fail | fail unless bias rises 0.23 | n/a | moderate |
| T4 r500 | M500-derived sigma | fail | marginal | fail | moderate |
| T5 | M_b, or V for Ogle | fail | pass | pass | strong / weak |
| T6 | stellar mass and rotation-curve quality | fail, 0/41 | fail if evolving | pass | strong |

**Decisive observation for what survives:** weak-lensing M_tot/M_b at a fixed 100 to 300 kpc for isolated galaxies and fossil groups, binned by baryonic mass (log M_b 11.3 to 12.5, sigma 200 to 350 km/s). A threshold predicts a kink at one sigma. a smooth law does not.

**Not verified or not done:**
- Stars inside r2500 come from a prescription, not a measurement.
- Akino 2022 publishes no per-system table, so I used only the fractions stated in its text.
- T5's bootstrap has only 60 simulations.
- T6 uses a thin-disk approximation for g_b at R_e.
- All analysis is independent code. The threshold model is reimplemented in model.py without importing the repository.

Files are in S/threads/gravity2/:
- model.py
- t3_atlas3d.py and .out
- t4_data.py, t4_systems.json, t4_clusters.py and .out
- t5_btfr_break.py and .out
- t6_highz_fdm.py and .out
- t0_checks.py and .out (sanity and corruption checks, pass under -O)
- fetch_vizier.py, arx_abs.py, arxq_copy.py
- sources/ (ATLAS3D tables, arXiv TeX sources, from_accel/ with CREDIT.txt, abstracts, arxiv_novelty_search.txt)

Rerun with S/work/pc-venv/bin/python on each script in that order.

## Where the named files are in the repository

Paths are relative to `org/review/2026-11/science/threads/`. Names that are not listed were not copied. `checks/STATE-NOTES.md` says why.

| Name in this report | Repository path |
|---|---|
| `arx_abs.py` | `checks/gravity2/state/arx_abs.py` |
| `arxq_copy.py` | `checks/gravity2/state/arxq_copy.py` |
| `fetch_vizier.py` | `checks/gravity/fetch_vizier.py`, `checks/gravity2/state/fetch_vizier.py` |
| `model.py` | `checks/gravity/model.py`, `checks/gravity2/state/model.py` |
| `t0_checks.py` | `checks/gravity/t0_checks.py`, `checks/gravity2/state/t0_checks.py` |
| `t3_atlas3d.py` | `checks/gravity/t3_atlas3d.py`, `checks/gravity2/state/t3_atlas3d.py` |
| `t4_clusters.py` | `checks/gravity/t4_clusters.py`, `checks/gravity2/state/t4_clusters.py` |
| `t4_data.py` | `checks/gravity/t4_data.py`, `checks/gravity2/state/t4_data.py` |
| `t4_systems.json` | `checks/gravity/t4_systems.json`, `checks/gravity2/state/t4_systems.json` |
| `t5_btfr_break.py` | `checks/gravity/t5_btfr_break.py`, `checks/gravity2/state/t5_btfr_break.py` |
| `t6_highz_fdm.py` | `checks/gravity/t6_highz_fdm.py`, `checks/gravity2/state/t6_highz_fdm.py` |
