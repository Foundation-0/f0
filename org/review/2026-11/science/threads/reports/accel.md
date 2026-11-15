# Acceleration scale and expansion: full report

15 November 2026. Repository head pinned by the report: gravity at 8f96c4b.

Short note for this thread: `../acceleration-evolution.md`.

S is the working folder of this thread. It is archived outside the repository. Paths that start with S/ point into it. Where a file was copied into the repository, its repository path is listed at the end.

---

RESULT: undecided. The only like-for-like high-z fit leans against H tracking, but the lean does not survive plausible systematics.

Everything else is in S/threads/accel/.

## Summary (under 500 words)

1. **Hypothesis and repo numbers.** The repo's hypothesis is a0(z) = A·E(z)^q with A = 1.2e-10 and Ωm = 0.315. q = 1 is H tracking (README.md:12-21, model.py:37-59). This is not cH(z)/2π, which the repo keeps separate. comparison.json holds ratios of curve values at the sample edges z = 0.33 and 1.44:
   - 1.9207 = E(1.44)/E(0.33)
   - 2.1575 is from Ciocan Eq. 4 (1.00 + 1.59z)
   - 1.9341 is from Eq. 14 (1.03 + 1.20z)
   I reproduced all six numbers with independent exact-rational and arb code (agree to better than 1e-12). 1.0422e-10 is cH0/2π at H0 = 67.40. The test with H0 = 70 gives 1.0824e-10.

2. **Fit to 100 real galaxies.** I fitted RC100 (Nestor Shachar+2023, z = 0.6 to 2.5): predicted v(R_e) from the published baryonic mass, bulge mass and R_e, compared with the measured V_c(R_e).
   - **A fixed at 1.2e-10:** p = 0.10 (95%: -0.25 to 0.40). p = 1 is worse by Δ(-2lnL) = 32.8.
   - **A with a 20% prior:** p = -0.01 (95%: -0.50 to 0.45), Δ = 18.4.
   - **A free:** p = -0.74 (95%: -1.8 to 0.25), Δ = 9.8, and p = 1 needs A = 0.58e-10, half the local value.
   - **Binned a0 (1e-10):** 1.82, 1.51, 1.15, 1.26 at z = 0.81, 1.41, 2.11, 2.30. H tracking predicts 1.92, 2.71, 3.83, 4.16.
   - **Other baryon inputs:** photometric-plus-gas masses and the paper's own decomposition give the same sign.

3. **Power and systematics.** The sample does reach the transition regime: median gN/a0 = 1.6 at R_e, and 29% of galaxies are below 1.2e-10. The result is systematics-limited, not power-limited.
   - A redshift-dependent mass bias of -0.2 dex per unit z flips the preference to p ≈ 1.2.
   - A pressure-support correction 1.5 times the published one cuts Δ to about 4.
   - Gas is about 50% of the baryons and comes from scaling relations.

4. **MUSE-DARK III.** The per-galaxy data could not be retrieved (dark-matter.osu-lyon.fr and cdsarc timed out). At summary level, their fitted lines match p ≈ 1.0 to 1.15. They agree with RC100 at z ~ 0.8 and disagree at z ~ 1.4.

5. **ΛCDM is not a clean contrast.** Mayer+2023 simulations give an RAR a0 that grows about 3x to z = 2.3, so a rising a0 does not single out MOND. Milgrom 2017 "all but exclude[s]" about 4a0 at z ~ 2.

6. **Decisive observation.** Measure asymptotic outer speeds (gN < 0.3 a0) for about 50 to 100 discs each at z ~ 1 and z ~ 2. Use per-galaxy CO/[CII] gas and JWST resolved stellar masses, with the same mass method as at z ~ 0. Then fit the slope-4 BTFR zero point.
   - H tracking predicts -0.25 dex at z = 1 and -0.48 dex at z = 2. Constant a0 predicts 0.
   - This needs redshift-dependent mass systematics below about 0.08 dex.

**Failed or unfinished:**
- MUSE raw data not retrieved.
- RC100 Table 3 is an image, so I transcribed it by hand. It passed internal checks, and a second reader agreed on 1295 of 1300 cells. All 5 disagreements resolved to my values on zoomed images.
- No injection-recovery test of p.

## Full report

### 1. Repo
- **[F] Hypothesis.** a0 = A E(z)^q, as above. Repo pinned at gravity@8f96c4b.
  - The H0 = 70 test is test_model.py:39-44.
  - 1.0422e-10 appears at CLAIMS.md:72,94.
  - a0 = 1.2e-10 would need H0 = 77.6.
- **[F] Reproduction.** repro_repo_numbers.py rejects a corrupted reference value with exit 1 under -O (outputs/corruption_tests.txt).

### 2. Predictions
**[F] BTFR zero point** (theory_numbers.py):

| Hypothesis | Velocity shift at fixed M_b | Mass shift at fixed V | Slope |
|---|---|---|---|
| Constant a0 | 0 | 0 | 4 |
| H tracking | (1/4) log E | -log E | 4 |
| Naive ΛCDM (M_vir = V^3/(10 G H)) | (1/3) log E | n/a | 3 |

- At z = 1 the velocity shifts are +0.063 dex (H tracking) and +0.084 dex (naive ΛCDM).
- At z = 2.3 they are +0.135 and +0.180 dex.

**[F] Example disc at z = 2.2** (log Mb = 10.8, R_e = 5 kpc):
- gN/a0 = 1.83 at R_e.
- v(R_e) is 214 km/s for constant a0 and 254 km/s for H tracking.
- v_flat is 178 vs 240 km/s.
- Even at gN/a0 = 7.2 (log Mb = 11.2, R_e = 4 kpc), v(R_e) differs by 10%.

**[I] Reading.**
- Dense discs still carry signal, so the test has power.
- ΛCDM shifts the zero point the same way as H tracking. Only the slope, the scatter and the asymptote separate them.

### 3. Data
- **[F] Ciocan 2026, arXiv:2604.22613v1.**
  - HTML sha256 matches evidence.json.
  - Retrieved values: Eq. 2, 4, 9, 13 and 14, plus bin end values 1.99 and 2.71.
  - The data server timed out at 20 s and 45 s.
  - J/A+A/708/A112 is absent from the CfA VizieR mirror.
  - MUSE-DARK I Table 5 has halo parameters for example galaxies only.
- **[F] RC100, arXiv:2209.12199.** Table 3 is a raster image on PDF pages 27-29, saved as data/rc100_table3.csv. Checks:
  - V_c errors are 20% of V_c.
  - The paper's Σ_DM column is reproduced from f_DM, V_c and R_e with median offset 0.000 dex.
  - The second reading agreed on 1295 of 1300 cells (outputs/xcheck_diff.txt).
  - Three corrupted inputs are rejected.
- **[F] Übler 2017.** All 135 rows came from the vizier.cfa.harvard.edu mirror. The repo had only 5.
  - Gas is molecular only (HI omitted), so baryonic masses are lower limits.
  - Mass errors are 0.15 dex (stars) and 0.20 dex (gas).
- **[F] Not used:**
  - Tiley 2019: stellar mass only.
  - Sharma 2021: no masses.
  - RC41: a subset of RC100.
  - MXDF: no outer velocities.
- **[F] Tacconi 2018 Table 3b coefficients** (0.12, -3.62, 0.66, 0.53, -0.35) were used for gas masses.

### 4. Fit model
- **[F] Baryons.** Exponential disc plus Hernquist bulge with R_e = 1 kpc, as RC100 assumed.
  - One global disc factor of 0.775 matches the paper's baryonic v²(R_e). Scatter is 0.106 dex.
- **[F] Likelihood.** Gaussian in log V. Errors combine the published V_c error, the mass error and the R_e error, plus a free intrinsic scatter.
  - The fitted scatter is 0, so the errors are conservative.
- **[F] Bootstrap, 200 galaxy resamples (p at the 2.5/50/97.5 percentiles):**
  - A prior: -0.35 / -0.01 / 0.27
  - A free: -1.48 / -0.76 / 0.00
- **[F] Variant B** (photometric M* plus Tacconi gas, independent of the kinematics): A prior gives p = -0.54, Δ = +23.5.
- **[F] Variant C** (the paper's own decomposition used as one RAR point per galaxy, like the MUSE method): A prior gives p = -0.31, Δ = +42.5. A free gives p = -0.51, Δ = +17.7.

### 5. Systematics and power
**[F] Sensitivity.** Each cell is best p, then Δ(-2lnL) for p = 1 minus p = 0:

| Change | A prior | A free |
|---|---|---|
| None (main) | -0.01, +18.4 | -0.74, +9.8 |
| Thin disc (no thickness factor) | -0.31, +26.2 | -0.98, +9.0 |
| All masses +0.2 dex | -1.35, +35.8 | -1.74, +4.5 |
| All masses -0.2 dex | +0.73, -10.3 | -0.43, +12.8 |
| Mass bias +0.1 dex per unit z | -0.25, +26.6 | -1.73, +17.2 |
| Mass bias -0.1 dex per unit z | +0.25, +9.4 | +0.23, +2.2 |
| Mass bias -0.2 dex per unit z | +0.52, -0.4 | +1.19, -5.7 |
| Mass bias -0.3 dex per unit z | +0.80, -10.9 | +2.16, -13.9 |
| Pressure correction halved | -0.72, +30.4 | -2.23, +11.1 |
| Pressure correction x1.5 | +0.40, +4.4 | -0.19, +6.5 |
| No pressure correction | -2.25, +10.2 (scatter 0.35 dex) | poorly constrained |

**[F] Size of the pressure correction.** It is 8% of V_c² at z ~ 0.8 and 24% at z ~ 2.3 (medians).

**[F] Power.**
- The median predicted shift from p = 0 to p = 1 is 0.052 dex in v.
- The median per-galaxy error is 0.10 dex.
- The Fisher error on p with no systematics is 0.20.

**[F] KMOS3D bound.** In MOND V_max ≥ V_flat, so each galaxy gives a0 ≤ V_max⁴/(G M_b).
- At z ~ 2.2 the median bound is 4.05e-10, equal to the H-tracking value of 4.03e-10.
- 50% of galaxies fall below the H-tracking value and 15% below 1.2e-10.
- [I] This mildly disfavours H tracking. It is not independent of RC100 (same parent survey).

**[I] Beam smearing and selection.**
- Residual beam smearing would push p down. it can't be tested without the data cubes.
- RC100 is massive. If the apparent a0 depends on galaxy mass at fixed z, that points to systematics.

### 6. MUSE at summary level
- **[F] Shape-equivalent p.** Eq. 4 gives 1.15, Eq. 14 gives 0.99, Eq. 9 gives 1.14.
- **[F] Their per-galaxy MOND a0.** Values range from 1.3e-11 to 9.6e-10. They say MOND fits underperform the dark-matter fits for over 60% of the sample.
- **[I] Comparison with RC100.**
  - At z ~ 0.8 the two agree.
  - At z ~ 1.4 MUSE gives 2.7 to 3.2e-10 and RC100 gives 1.51 [1.09, 1.99]e-10.

### 7. Literature
All quotes were checked by exact string match in cached text under sources/lit/.
- **Milgrom 2017, arXiv:1703.06110:** "all but exclude a value of the MOND constant of ∼ 4a0 at z ∼ 2". The galaxies have "g(R1/2 ) = (3 − 11)a0". The clean test "is not possible with the present data".
- **Hossenfelder & Mistele 2018, arXiv:1803.08683:** the predicted z-dependence "is, however, small compared to that expected from particle dark matter".
- **Mayer 2023, arXiv:2206.04333:** a0 increases "by a factor ≃3 from redshift 𝑧 = 0 to 𝑧 = 2.3".
- **Vărăşteanu 2025, arXiv:2504.20857:** "tentative evidence" at z < 0.08.
- **Vărăşteanu 2026, arXiv:2608.03576:** "no significant redshift evolution". H tracking predicts only 4% change by z = 0.09, so neither result tests it.
- **Alcock 2026, arXiv:2609.38796:** γ = 0.78 ± 0.15, with H tracking "consistent with the measurement within 2.1σ".
- **Bekenstein & Sagi 2008 (TeVeS), arXiv:0802.1526:** any a0 variation should be "imperceptible back to redshift unity".
- I found no JWST-era kinematic MOND test at z > 2.

### Rerun
```
cd checks
python3 gravity/fetch_sources.py      # once, for the KMOS3D table
python3 check_all.py --full           # runs every program below and compares with outputs/
cd accel
python3 -O repro_repo_numbers.py
python3 -I -O check_transcription.py data/rc100_table3.csv
python3 rc100_fit.py data/rc100_table3.csv outputs/rc100_fit.json > outputs/rc100_fit.txt   # about 6 min, 1 core
python3 ubler_bound.py ../gravity/sources/from_accel/ubler2017_vizier.tsv outputs/ubler_bound.json
python3 muse_summary.py
python3 theory_numbers.py
```
Saved output, not re-runnable here: the second reading of the table (`outputs/xcheck_diff.txt`), made on page images that are not in this folder.

### Not verified
- **Transcription:** columns z, dMS and log M* are checked only by the second reading.
- **Baryon model:** thin disc plus one global thickness factor. RC100's fitted Sérsic n is not tabulated.
- **Not modelled or not run:** the algebraic RAR is used for discs instead of full QUMOND. no external-field effect. no injection-recovery test.
- **Independence:** RC100 and KMOS3D come from the same team, so they are not independent replications.

### Next step
1. Retry the MUSE server from another network to get the 79 galaxies' RAR points and posteriors.
2. Fit MUSE and RC100 jointly, with a shared A and p, per-survey mass offsets, and an explicit redshift-dependent mass-bias term.
3. Run injection-recovery for p = 0 and p = 1 before reading p.

### Files
All in S/threads/accel/:
- Code: accel_lib.py, rc100_fit.py, ubler_bound.py, muse_summary.py, theory_numbers.py, repro_repo_numbers.py, check_transcription.py
- Data: data/rc100_table3.csv; xcheck/
- Results: outputs/ (all .txt and .json results)
- Sources: sources/ (cached papers, the VizieR table, lit/, rc100_img/)
- Scratch to delete: tmp_corrupt/

## Where the named files are in the repository

Paths are relative to `org/review/2026-11/science/threads/`. Names that are not listed were not copied. `checks/STATE-NOTES.md` says why.

| Name in this report | Repository path |
|---|---|
| `accel_lib.py` | `checks/accel/accel_lib.py` |
| `check_transcription.py` | `checks/accel/check_transcription.py` |
| `data/rc100_table3.csv` | `checks/accel/data/rc100_table3.csv` |
| `muse_summary.py` | `checks/accel/muse_summary.py` |
| `outputs/` | `checks/accel/outputs/` (9 files) |
| `outputs/corruption_tests.txt` | `checks/accel/outputs/corruption_tests.txt` |
| `outputs/rc100_fit.json` | `checks/accel/outputs/rc100_fit.json` |
| `outputs/rc100_fit.txt` | `checks/accel/outputs/rc100_fit.txt` |
| `outputs/ubler_bound.json` | `checks/accel/outputs/ubler_bound.json` |
| `outputs/xcheck_diff.txt` | `checks/accel/outputs/xcheck_diff.txt` |
| `rc100_fit.py` | `checks/accel/rc100_fit.py` |
| `repro_repo_numbers.py` | `checks/accel/repro_repo_numbers.py` |
| `theory_numbers.py` | `checks/accel/theory_numbers.py` |
| `ubler_bound.py` | `checks/accel/ubler_bound.py` |
