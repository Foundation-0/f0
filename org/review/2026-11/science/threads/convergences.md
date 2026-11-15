# Convergences: where separate threads or many cases agree

15 November 2026. An index of the statistical patterns found in this pass, each with its numbers, what it turned into, and where the evidence is. Marks: **[F]** fact from a run, **[I]** inference, **[C]** conjecture. A pattern is listed only if it was measured. Where a pattern failed a test, that is listed too.

## Patterns that became theorems or certified results

### 1. The square law

- [F] The characteristic polynomials of 211 proved recurrences were factored. 209 are perfect squares and the other two are a square times (x + 1).
- [F] In all 88 families where both conditions are proved, "exactly once" and "at most once" share one polynomial.
- [F] For 168 of the 170 entries small enough to test, the square root is the minimal recurrence of the count with no marked pair. For the other two that recurrence is the square root times (x + 1).

What it became: a theorem with a full proof. One defect squares the recurrence. It re-proves the 211 and proves 27 more that were too large for the first method, 238 in all. Note: `square-law.md`.

### 2. Walls between charges

- [F] In eight certified configurations of 3 to 9 charges, the number of loops in the wall network equals the number of index-1 balance points. The same holds in the three 11-point configurations, which were traced by a second program.
- [F] Every configuration that beats Maxwell's bound does it by putting more than one wall between the same pair of charges. The three large charges share 2, 2, 3, 3 and 4 walls per pair at 5, 6, 7, 8 and 9 charges.
- [F] Two predictions were written down before they were tested: four walls per large pair at nine charges, and seven walls for a four-charge configuration above the bound. Both held.

What it became: a reading of Maxwell's bound as "one wall per pair", and the search that found four charges with 11 balance points. Notes: `relational-geometry.md`, `four-charges-eleven.md`.

### 3. Records sit beside the most degenerate arrangement

| Problem | Record | Where it sits |
|---|---|---|
| Rigid graph, 11 vertices | at least 2,288 real realizations, the full complex count | every edge within 0.8% of the same length |
| Four charges | 11 balance points | one route: within 0.05 of the regular tetrahedron, whose centre has multiplicity 11. The other: beside a flat point of multiplicity 8 |
| Ten equal masses | the classes random search missed | beside the regular polygon |
| Point-mass lens, published | 5n - 5 images | a regular polygon with a small mass at its centre |

[I] In each problem the largest count is reached where the most sheets of solutions meet and can be pulled apart. The four-charge result was found by acting on this.

### 4. A flat point is worth eight

[F] At a point where the gradient and the whole Hessian vanish, the nearby balance points solve three quadrics. In 200,000 random draws near the regular tetrahedron, all 8 solutions were real in 2,197. Across the whole family of flat configurations it was 139 in 200,000.

What it became: a closed form for every flat four-charge configuration, and the second of the two certified configurations with 11. Note: `four-charges-eleven.md`.

### 5. Levels stack

[F] A point flat to order d - 1 can be unfolded one degree at a time, each at its own scale. Level p gives I(p) - 1 balance points, about p²/2. The counts 5, 7, 11, 17, 25 and on to 71 were found by three numerical programs, which search and could miss points. The stacked totals up to seven levels are proved by an exact one. In exact 21-charge arithmetic the groups 1, 5, 7, 11, 17, 25 are proved.

What it became: an argument that balance points can grow like n^(3/2). Note: `growth.md`.

### 6. Low degrees reach the full count

[F] A harmonic polynomial of degree d has at most (d - 1)³ critical points. All 8 are real for a cubic and all 27 for a quartic, both proved. At degrees 5 and 6 the searches reached 52 of 64 and 83 of 125. Note: `flat-centres.md`.

## Patterns that are measured and not yet explained

### 7. Realizations turn real near equal edge lengths

| Vertices | Mean real share near equal lengths | Mean real share far from them |
|---|---|---|
| 6 | 0.90 | 0.52 |
| 8 | 0.80 | 0.27 |
| 10 | 0.73 | 0.14 |
| 11 | 0.68 | 0.10 |

- [F] 12,307 samples, with p-values between 1e-32 and 1e-121.
- [F] Near equal lengths the solutions split into a fixed part, always real and on the triangular lattice, and a moving part whose real share is close to two thirds for every graph.
- [I] Two thirds is what independent random real quadratics give (0.65).
- [C] An open cone of all-real directions exists at the all-equal point for the largest graph of each size. It was found for 8, 9 and 10 vertices and not yet for 11.

Note: `unit-point.md`.

### 8. Where the code tables are weak

- [F] 2,418 entries improve. The drop is one unit in 2,066 of them, two in 344 and three in 8.
- [F] The improved entries cluster at low rate. Across the three fields the lower quartile of dimension over length is 0.14, the median 0.20 to 0.22 and the upper quartile 0.28 to 0.30.
- [F] The improvements close 7 to 10% of the remaining gap in those entries. Three entries are settled exactly.

[I] The tables were never swept with this bound in that region. Note: `codes.md`.

### 9. A baryon-only law for the mass discrepancy, and its limit

- [F] In the 663 local rows of the table, from dwarf galaxies to clusters, the extra mass follows the baryonic mass with exponent 1.36. Some systems appear at two radii. The 95% range of 1.32 to 1.39 comes from resampling rows, which treats the two radii of one system as independent, so the true range is wider. The exponent was above 1 in all 300 resamples.
- [F] This law scores 0.148 dex against 0.190 for the standard relation alone. `gravity.md` also finds that no law in one variable describes every class. The score weights six classes of system equally, and that scheme was this study's own choice.
- [F] An earlier headline law in terms of speed and radius was found to be partly forced by how extra mass is defined. It was replaced by the baryon-only law, which cannot be circular.

Note: `gravity.md`.

### 10. One particle scale across galaxy groups and clusters

- [I] Taking the extra mass as a light fermion, the packing limit and the cosmic abundance bound the mass from both sides. One fermion of 9 to 21 eV at 15 to 100% of the thermal abundance fits both. Two of the three numbers behind this come from the same clusters the third is tested on, so the fit is partly by construction.
- [C] The central case, 11 eV at three quarters, gives a cosmic ratio of dark to baryonic matter of 3.96 and a ratio of 0.50 in a galaxy at 300 kpc. The three quarters is a postulate with no production mechanism.
- [I] Its weakest point is the count of light species at recombination: 2.28 against a measured 2.99 ± 0.17, about four standard errors away. The comparison assumes the standard model with cold matter.

Status: a conjecture with stated tests. Notes: `neutrino-like.md`, `fabric.md`.

## Patterns that did not survive

### 11. The four speeds near 185 km/s

[F] Drawn blindly, four speeds landing that close has a chance of about 1 in 100,000. With the ranges each speed could honestly have taken, the chance is about 2%, with a 16 to 84% range of 0.4% to 5%. [I] The four are about two independent scales. Note: `gravity.md`.

### 12. Two signals made by the way the sample was cut

- [F] Sorted by speed, the eight fastest spirals sit 0.10 dex above the standard relation, as the threshold model predicts. Sorted by baryonic mass the excess is gone.
- [F] A slope of 0.553 ± 0.063 in giant spirals looked like confirmation. A sample chosen in a narrow range of mass gives a positive slope from scatter in speed alone. No program in this folder computes how large.

[I] Both came from selecting on a quantity that enters the statistic. Every later test states its selection variable. Note: `gravity.md`.

### 13. A random direction is all real

[F] The first form of the unit-point hypothesis said a random direction near equal lengths gives every realization real with a chance that does not shrink. It does shrink: 0.395 at 6 vertices, 0.090 at 7, and zero in every sample from 8 up. Note: `unit-point.md`.

## A pattern in the checks themselves

### 14. Verifiers that pass corrupted input

[F] In three repositories, vitruvian3d, point-charges and gravity, a verifier printed success on a corrupted certificate when Python ran with `-O`, because its proof steps were `assert` statements. Only the point-charges run is saved in this folder. The other two are in the science pass.

[F] Each now has a fix on a pull request. In this folder, `checks/claims/checkers.md` lists the 22 checking programs: none has a bare `assert`, and 15 have a corruption test saved here.

### 15. Exact identities as built-in tests

- [F] For 8, 9 and 10 equal masses the Morse identity of the certified classes comes out exactly: 1/56, -1/72 and 1/90.
- [F] For every certified charge configuration, index-2 minus index-1 points equals the number of charges minus one.

[I] A count that satisfies such an identity can still be incomplete, but a count that breaks it is wrong. Both were used to reject bad runs.

## What the list suggests

1. Factor, tabulate and compare before proving. The square law was visible in the data before anyone looked for it.
2. Look where the problem is most degenerate. Three records were found there, and one was predicted there.
3. State the selection rule with every statistic. Two apparent confirmations were artefacts of it.
4. Write the prediction down first. Both wall predictions and the failed redshift test were decisive because of that.
