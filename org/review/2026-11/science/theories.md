# F1: theory map

Science pass, 15 November 2026. This lists the distinct theories, frameworks and results in the 35 public repositories, each with its statement, formulas, constants and the repositories that use it. Every repository was read from a fresh clone at the head listed in `org/review/2026-11/tools/heads.tsv`, which is on the H1 branch (draft PR 45).

Marks: **[F]** a fact read from a repository or a run, **[I]** an inference. Pins are `repo@sha:path:line`. The column "State" gives the label from `glossary.md` where one applies, with a short note. The glossary also defines the statuses "not a claim" and "not yet judged". Verdicts for each claim are in `verdicts.csv`. `verdicts.csv`, `notes/` and `checks/` are in `org/review/2026-11/science/` on draft PR 51, and `glossary.md` is on draft PR 55.

## The short version

The organisation does not hold one theory. It holds 17 separate bodies of work. Two of them carry results that have a check with separate code written for this review: the 880 real realizations of a rigid graph, and 18 exact upper bounds on linear codes (held in 15 certificate files).

A third, the exact counts of equilibria of point charges, is REPRODUCED with the repository's own verifier. Its check with separate code is still to come.

One body, the gravity wave series, is the only candidate for a physical theory. Its own ledger says it is not one. Its central fit does not survive a like-for-like comparison with its own data table unless a second number is fitted.

| # | Body of work | Repositories | Kind | State of the main result |
|---|---|---|---|---|
| 1 | Gravity wave series | gravity | physics model evaluations | REPRODUCED as arithmetic. The 185 km/s convergence is OVERSTATED |
| 2 | Acceleration evolution | gravity | a test design | OPEN. No fit has been done |
| 3 | Fractal scaling | fractals | exploration | no new result claimed |
| 4 | Incentre lattices | incentre-lattices | geometry and elasticity | REPRODUCED. Written proofs not yet checked line by line |
| 5 | Vitruvian 3D geometry | vitruvian3d | geometry | REPRODUCED bare. Proofs not yet checked |
| 6 | Real realizations of rigid graphs | rigid-realizations | computer-assisted proof | VERIFIED (L880) |
| 7 | Point-charge equilibria | point-charges, physics0 | computer-assisted proof | REPRODUCED |
| 8 | Bounds on linear codes | gfq-codes, math0 | exact certificates | VERIFIED. The GF(9) part is KNOWN |
| 9 | Finite-state recurrences | finite-state-proofs | computer-assisted proof | REPRODUCED |
| 10 | Covering systems | covering-min-modulus | plan | nothing to judge |
| 11 | Certified orbits, relative equilibria | certified-orbits, relative-equilibria | plans | nothing to judge |
| 12 | Integer multiplication study | math0 | exploration | not yet judged. Its Lean files do not compile |
| 13 | TESS transit vetting | exoplanets-frontier, gaia-dr4 | data pipeline | OVERSTATED in five of eight claims |
| 14 | Archive and catalogue studies | plate-novae, plate-eclipses, lost-eclipses, overdue-data, rism-anon, wwssn-microseisms | data pilots | claimed pilots or plans |
| 15 | Human-body data and models | nhanes-bioimpedance, virtual-human, project-asma | data analysis | not yet judged |
| 16 | Engineering notes | cfrp-strengthening, thermal-capture, ductricity | calculations and essays | REPRODUCED (cfrp). The other two hold no computation |
| 17 | Proof-checking tools | proven-commons, formal-claims-audit | infrastructure | no mathematical claim |

## 1. Gravity wave series

**Where.** `gravity`, claims C-01 to C-33 in `CLAIMS.md`, one script per "wave".

**What it says about itself.** [F] `gravity@8f96c4b:README.md:8`: the repository "is **not** a derivation of a new fundamental theory of gravity, dark matter, or quantum mechanics, and its scripts are **not** parameter-free". Most claims carry the label `COMPUTED (KNOWN-FRAMEWORK)`, defined as an evaluation of a published equation under chosen inputs (`CLAIMS.md:9`).

**The model that the later waves build.** A two-part acceleration at radius r, stated in `CLAIMS.md:118`:

```
g_tot(r) = g_RAR(g_b; a_0) + f_trap(sigma) * R * g_b(r)
g_RAR(g_b) = g_b / (1 - exp(-sqrt(g_b / a_0)))
f_trap(sigma) = max(0, 1 - sigma_J^2 / sigma^2)
```

The first term is the radial acceleration relation of McGaugh and co-authors, a fit used in modified-gravity work. The second term adds ordinary dark matter ("dust") in systems whose velocity dispersion sigma exceeds a threshold sigma_J. R is the ratio of dark to baryonic mass.

**The 185 km/s scale (C-26, C-27).** [F] `CLAIMS.md:135,140` compare four speeds: a fitted group onset (180 to 190), a collapse scale from the Planck 2018 power spectrum (185.59), a Milgrom rotation speed for a chosen galaxy mass (175.82), and a gas cooling scale (178.42).

**Constants.**

| Quantity | Value | Pin |
|---|---|---|
| a_0 | 1.20e-10 m/s^2 | `wave10_covariant_jeans_unification.py:27` |
| a_dS = c H_0 / (2 pi) | 1.0422e-10 m/s^2 at H_0 = 67.4 | `CLAIMS.md:72` |
| H_0 | 67.36 (Wave 10), 67.4 (C-07), 72 (Wave 7 lensing rows), 73.0 (KiDS fit) km/s/Mpc | `wave10...py:30`, `CLAIMS.md:42`, `wave7...py:102`, `CLAIMS.md:48` |
| Omega_c / Omega_b | 5.3895 | `CLAIMS.md:118` |
| gas fraction at R_2500 | 0.105, giving R = 8.5238 | `CLAIMS.md:121` |
| baryon fraction used to build 28 data rows | 0.130 | `wave7_group_cluster_threshold_audit.py:119` |
| galaxy baryonic mass for the Milgrom speed | 6e10 solar masses | `wave10...py:267` |
| overdensity for the cooling scale | 1000 | `wave10...py:281` |
| halo convention for the collapse scale | 200 times critical density, sigma = V_200 / sqrt(2) | `wave10...py:186-188` |

**Evidence.** Python scripts in floating point with bare asserts. 32 Lean theorems of integer arithmetic, all of which build on standard axioms. A hand-entered table of 126 systems (`wave7...py:34-141`).

**What this pass found.** Details and commands are in `notes/gravity.md`.

- [F] Every wave script passes its own check from a fresh clone. An independent recomputation gives 185.59 km/s.
- [F] The collapse scale moves from 153 to 216 km/s under other common halo conventions. The cooling scale is exactly proportional to the chosen overdensity. The Milgrom speed moves from 148 to 200 km/s for galaxy masses from 3e10 to 1e11.
- [F] The data table holds ratios of baryonic mass. The model prediction that is compared with it is a ratio of accelerations (`wave10...py:233`). The two differ whenever g_b is below a_0, which in this model is the case for every system at 250 kpc.
- [F] Compared as the scripts do, chi-squared is 60.26 on 60 systems. Compared like with like, with the same fixed inputs, it is 256.53.
- [F] Compared like with like and with the dark-to-baryon ratio left free, the table is fitted well (chi-squared 54 on 60 systems) by a threshold near 185 to 200 km/s and a ratio near 4. The threshold survives. "Zero fitted parameters" does not.

## 2. Acceleration evolution

**Where.** [F] Only `gravity@8f96c4b:acceleration-evolution/`. The issue places this thread in fractals, astr0 and physics0 as well. At their pinned heads those three repositories do not mention it. gravity cites companion notes at commits that are not on their default branches (`acceleration-evolution/STATUS.md`, `research/convergences-20261112/PROVENANCE.md:16-18`). Those commits are the heads of open pull requests fractals 51, physics0 15 and astr0 4, from the branch `aeva/acceleration-evolution-links`.

**Statement.** [F] `acceleration-evolution/README.md:12`:

```
E(z) = H(z)/H_0 = sqrt(Omega_m (1+z)^3 + 1 - Omega_m),   a_0(z) = A E(z)^q
```

q = 0 is a constant scale. q = 1 is a scale that follows the expansion rate. A = 1.2e-10 m/s^2 and Omega_m = 0.315 (`README.md:15`).

**State.** [F] `acceleration-evolution/INFERENCE.md:3`: "The raw-data fit has not been performed." The folder compares growth ratios with published fitted curves from one survey paper. It is a test design with a worked example. OPEN.

## 3. Fractal scaling

**Where.** `fractals`. [F] `fractals@48b923b:README.md:7`: "exploration, not peer reviewed, no new result claimed."

**Content.** Textbook and literature scalings stated in prose: quantum path dimension 2, the scale of cosmic homogeneity, a turbulence cascade check, a cloud-edge dimension, percolation and Ising exponents. `CORRECTIONS.md` holds items 1 to 20. Item 21 appears only in the `CORRECTIONS.md` of open pull requests: fractals 26 and 35 add one item numbered 21, and fractals 54 adds a different one.

**Note.** [F] In fractals the symbol a₀ is the Bohr radius of a gravitational atom (`fractals@48b923b:README.md:289`, and `a0` in `gravitational-atom/atom.js:6`). In gravity a_0 is the acceleration scale (`gravity@8f96c4b:CLAIMS.md:18`).

## 4. Incentre lattices

**Where.** `incentre-lattices`. math0 lists it as a preprint on Zenodo that is not peer reviewed (`math0@e649250:README.md:18`).

**Construction.** Join the incentres of the four triangles of a square, and follow the same rule in n dimensions. The repository identifies the resulting family as the bridged cross-polytope framework and says the family itself is prior art (Borcea and Streinu 2021).

**Main theorem.** [F] `incentre-lattices@2d374ff:results/rigidity-nd/PROOF.md:33-35`. For ideal unit springs on this framework in n dimensions:

```
C11 / C12 = (n-1)^2,   all shear moduli = 0,   nu_100 = 1 / (n^2 - n - 1)
```

Labelled PROVEN for n at least 3 and VERIFIED for n = 2 to 8. [I] The last formula follows from the first by the standard relation nu = C12 / (C11 + (n-2) C12), which was checked here by hand.

**Other results.** A packing maximum for the CaB6 structure in three dimensions, (pi/6)(30 sqrt(2) - 41) = 0.746865. Folding motions from the framework to close packings, some sampled in floating point and one supported by an exact certificate. A Lean file of counting arithmetic.

**State.** [F] Reader run: all verifiers pass bare and under `-O`, and none relies on a bare assert. The written proofs have review by AI agents only. No material constants or stiffness numbers are claimed.

## 5. Vitruvian 3D geometry

**Where.** `vitruvian3d`. [F] `vitruvian3d@7099f5c:README.md:7`: "geometric results with written proofs and internal AI review. Human mathematical review, historical priority, mechanical performance, and anatomical significance remain unestablished."

**Content.** A passage theorem, a window theorem, rod and volume bounds, and a transport theorem that separates rank two from rank three conduction. None is formalised.

**State.** [F] `replay_all.py` passes its first 22 steps on a fresh clone. `research/passage_verify.py` accepts a corrupted certificate under `python3 -O` (lead run). [F] The proof states two thresholds for the rod radius a. The probe-exclusion threshold for an equal-size probe is a <= (sqrt(3) - 1) r (`research/connectors_proof.md:27`). The simultaneous certificate holds for 0 < a/r < 1/2 (`:57`). The summaries state the certificate bound, for example `README.md:22` and `research/status.md:15`.

## 6. Real realizations of rigid graphs

**Where.** `rigid-realizations`. Paper reserved at DOI 10.5281/zenodo.24145786 (`README.md:11`).

**Statement.** [F] `rigid-realizations@298926c:README.md:20`. For the 10-vertex minimally rigid graph with 880 complex realizations, there are bar lengths for which all 880 are real. Label: "claimed (pending independent verification)".

**Method.** 17 rational bar lengths, one triangle pinned, and 440 small boxes in 14 unknowns. Each box is shown to hold exactly one real solution. Mirror images give the other 440.

**State.** [F] VERIFIED by `checks/l880_independent.py`, which shares no code with the repository. [F] The earlier published figure is 860 certified and 868 numerical (Bartzos, Emiris, Legersky and Tsigaridas, arXiv:1811.12800). [I] The count of 880 complex realizations is the repository's own computation from a published recurrence (`rigid_realizations_l880_pr_bundle/scripts/verify_capco_laman.py`). It was not recomputed here.

**Related rows.** L344 is KNOWN: the same paper says all its embeddings can be real. G160 at least 132 certifies a value that paper already reports numerically.

## 7. Point-charge equilibria

**Where.** `point-charges`. `physics0@913468f:README.md:14` quotes it.

**Statement.** [F] `point-charges@a2fd159:README.md:16-22`. Exact numbers of equilibrium points for explicit configurations of 3, 4, 5, 6 and 7 positive charges: 4, 9, 24, 29 and 44. Maxwell's bound (n-1)^2 gives 4, 9, 16, 25 and 36.

**Prior art as the repository gives it.** A five-charge counterexample with at least 24 equilibria, published in July 2026 by Arathoon, Ball and Kvalheim (`README.md:10`). The repository adds the exact count for that case, a four-charge example that reaches the bound, and the six and seven charge counts.

**State.** [F] REPRODUCED. Lead run of `verify_arb.py` on all five certificates returns the five counts. That is a run of the repository's own verifier. A check with separate code is still to come. The Lean file holds definitions only.

## 8. Bounds on linear codes

**Where.** `gfq-codes`. `math0` holds the census of open table entries.

**Statement.** 18 statements, held in 15 certificate files, of the form "no linear code [n, k, d] over GF(q) exists", for q = 7 and q = 9. Each lowers by one the upper bound shown at codetables.de.

**Method.** The Delsarte linear programming bound, with integer coefficients stored in `results/*/certificate.json`.

**State.** [F] VERIFIED by `checks/delsarte_independent.py` for all 18. [F] codetables.de, read on 15 November, shows upper bounds one higher than the certificates allow for all six GF(7) cells, so those six improve the table. They rest on two base facts. [F] For GF(9), Maruta's table of n_9(4,d) already gives n_9(4,26) = 32 and n_9(4,27) = 33. [I] The other ten GF(9) cells follow from those two by shortening a code. The GF(9) part is KNOWN.

**Note.** The repository holds no codes. The question in its title, better codes, has no result yet.

## 9. Finite-state recurrences

**Where.** `finite-state-proofs`. Eleven recurrences from the OEIS (A268881 to A268885 and A268989 to A268994) are proved from a transfer matrix. [F] Reader run: both verifiers use exact integers, pass under `-O`, and reject a corrupted coefficient. REPRODUCED.

## 10 and 11. Covering systems, certified orbits, relative equilibria

[F] All three say "Status: not started" (`covering-min-modulus@e8ecf1b:README.md:19`, `certified-orbits@51f6983:README.md:20`, `relative-equilibria@bf1e1ce:README.md:22`). No covering system, orbit or count is stored. Each has a published Zenodo record.

## 12. Integer multiplication study

**Where.** `math0/studies/integer-mult/`. [F] `math0@e649250:studies/integer-mult/carbon-2026-11-13/PROVENANCE.md:60` records that `BaseMathConvergence.lean` fails to compile. The reader confirmed that both Lean files fail on Lean 4.35.0. Not yet judged.

## 13. TESS transit vetting

**Where.** `exoplanets-frontier`, claims C-01 to C-08. It builds on an outside project that is not included in the repository.

**State.** [F] Three of the five hash prefixes quoted in `CLAIMS.md` do not match the files (lead run). [F] The 22 "confirmed candidates" of C-01 are 22 rows from 18 stars, passed at a signal-to-noise of 3.0. [F] The 348 "clean" targets of C-08 all carry the default RUWE of 1.0. Details in `notes/exoplanets-frontier.md`.

## 14 to 17. The remaining bodies

| Body | Result as stated | State |
|---|---|---|
| plate-eclipses | Period of ASASSN-21co, 4343.3 +/- 1.1 days | Reader re-fit offline gives 4343.28 +/- 1.06. REPRODUCED by the reader |
| plate-novae | Pilot scores on 17 stars, scored by hand | claimed pilot |
| overdue-data, rism-anon | Counts from archives. The data is not in the repositories | claimed pilots |
| lost-eclipses, wwssn-microseisms, gaia-dr4 | none | plans |
| nhanes-bioimpedance | Survival associations of bioimpedance measures in 13,276 people | not yet judged |
| virtual-human | Validators on 100 clinical datasets (`virtual-human@6b10b45:README.md:70`). `docs/validation_body.md:3` lists 28 IV and 54 oral datasets, which is 82. The two files disagree | not yet judged |
| cfrp-strengthening | A checker that matches ten printed values of a worked design example | REPRODUCED. The example is not in the repository |
| thermal-capture, ductricity | Essays with textbook figures | no computation to judge |
| proven-commons, formal-claims-audit | Tools. formal-claims-audit has no verdicts yet | no mathematical claim |

project-asma is in scope only where another repository depends on it. Two dependencies were found. The virtual-human script `scripts/validate_asma_interventions.py` needs a project-asma checkout (`--asma-root`). project-asma holds a pinned copy of `vh/graph/core.py` (`project-asma@4817821:NOTICE:70`). Its claims were not judged in this pass. H1's claims index holds 128 project-asma rows, more than any other repository, and verdicts.csv has no row for them.
