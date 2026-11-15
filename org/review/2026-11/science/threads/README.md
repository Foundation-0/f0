# Threads pulled after the science pass

15 November 2026. The science pass ended with a list of threads worth pulling (`new-ground.md` on draft PR 56). This folder holds what came out when each was pulled as far as it would go in one pass. Each thread has its own note, with the programs and saved outputs under `checks/`.

Marks: **[F]** a fact read from a repository or produced by a run, **[I]** an inference. Verdict words are those of `glossary.md` (draft PR 55).

## The short version

Seven threads produced results that hold under separate code. The largest is four point charges with 11 balance points, above Maxwell's bound of 9. The gravity thread produced clear failures and one survivor. Two threads ended without a decision, and each names what would decide it. One confirmed known lists and corrected three table entries.

Later threads followed what the first ones turned up. They are in the second table. `convergences.md` indexes the patterns found across threads, and `SYMBIOSIS.md` lists what was returned to each source repository.

| Thread | Outcome | Note |
|---|---|---|
| Four point charges | 11 balance points, above Maxwell's bound of 9. Three configurations, each proved by two exact programs and a third lower-bound proof. **VERIFIED** | `four-charges-eleven.md` |
| 11-vertex rigid graph | All 2,288 realizations can be real. New growth bound 2.4116 per vertex, above the published 2.3780. **VERIFIED** | `l2288.md` |
| 10-vertex rigid graph | The complex count of 880 is confirmed by three implementations, so "all 880 are real" is complete. **VERIFIED** | `rigid-realizations.md` |
| Point charges | The counts 4, 9, 24, 29 and 44 now have a proof by separate code. New exact counts: 49 for eight charges and 64 for nine. **VERIFIED** | `point-charges.md` |
| Code tables | One standard bound improves at least 2,418 entries of the reference tables for GF(7), GF(8) and GF(9). **VERIFIED** | `codes.md` |
| Recurrences | 238 recurrences that the OEIS lists as empirical are proved, 227 of them new. A theorem explains all of them: one defect squares the recurrence. **VERIFIED** for 46, REPRODUCED for the rest | `recurrences.md`, `square-law.md` |
| Lattice elasticity and the fold | The theorem holds for dimensions 2 to 9 and the fold to the densest packing is confirmed. One wording error found. **VERIFIED** | `incentre-lattices.md` |
| Gravity threshold | The zero-parameter version and the falling threshold fail against published data. A weaker large-scale residual survives. | `gravity.md` |
| Acceleration scale and expansion | **Undecided.** The one fit possible leans against, and mass errors can reverse it. | `acceleration-evolution.md` |
| Central configurations | At least 20, 42 and 67 classes proved to exist for 8, 9 and 10 equal masses, matching published numerical lists. Three table entries corrected. Completeness not proved. **REPRODUCED** | `central-configurations.md` |
| The 880 engine on the open Maxwell cases | The engine found no count above the bound for three or four charges. A second four-charge family with exactly 9 is certified. The four-charge case fell later to a different method. | `maxwell-push.md` |

Threads that followed from the first ones:

| Thread | Outcome | Note |
|---|---|---|
| 12-vertex rigid graph | 3,904 of 6,180 realizations real, certified. The graph has no triangle, so it cannot raise the growth bound. | `l2288.md` |
| Realizations near equal edge lengths | The real share is far higher near equal lengths. All-real directions exist for 8, 9 and 10 vertices. Numerical. | `unit-point.md` |
| Walls between charges | Each index-2 balance point is a wall between two charges. Maxwell's bound is the count for one wall per pair. Two predictions made from this held. | `relational-geometry.md` |
| Three charges | Still open. Proved with a computer for the equilateral triangle and any charges: at most one minimum, so at most 4 balance points. The question is reduced to whether one curve crosses itself. Every cusp sampled is of the harmless kind. | `three-charges.md` |
| Growth with the number of charges | Balance points can grow like n^(3/2), where every known construction grows like 10n. A four-step argument with a proof sketch, numerical checks of each step, and proved lower bounds of 26 for 9 charges and 87 near one point for 21. No single record is beaten. | `growth.md` |
| Centres flat to high order | By an inversion rule, the centre of twelve equal charges on an icosahedron could give up to 125 balance points, against a record of 89. How many can be real is open and being worked. | `flat-centres.md` |
| A light particle for the surviving residual | One fermion of 9 to 21 eV fits galaxies, groups and clusters. Its weakest point is the count of light species at recombination. A conjecture with stated tests. | `neutrino-like.md`, `fabric.md` |

## What is new and holds

1. **Four charges with 11 balance points.** [F] Maxwell's bound for four charges is 9. Three configurations are certified, one of them with coordinates of five decimals. [I] It was found by looking where the problem is most degenerate: the centre of a regular tetrahedron of equal charges is a balance point of multiplicity 11. The July 2026 counterexample starts at five charges.
2. **Growth faster than linear.** [I] A point where the potential is flat to high order can be unfolded level by level, and the count of balance points then grows like the number of charges to the power 3/2. [F] Each step is checked numerically, and the pattern is proved as a lower bound in two exact configurations. It is an argument with a proof sketch, not yet a proof.
3. **A rigid graph on 11 vertices with every realization real.** [F] 2,288 of 2,288, certified in exact arithmetic and checked by a third program written for this review. [I] It raises the best known growth rate for real realizations from 2.3780 to 2.4116 per vertex. A survey from February 2025 still quotes the older figure.
4. **Exact counts for eight and nine point charges.** [F] 49 and 64, each equal to Maxwell's bound. No explicit configuration or exact count for these was found in print.
5. **Thousands of sharper entries in the standard code tables.** [F] Every one has an exact certificate that three checkers accept. The method is old. What is new is running it across the tables.
6. **227 more proved recurrences, and the law behind them.** [F] None of the empirical recurrences tested was false. [F] The recurrence for grids with one marked pair is the square of the recurrence for grids with none, and this is now a theorem.

Novelty in every case means "no earlier report found" after a stated search. It is not a priority claim.

## What failed

- [F] **Gravity, the zero-parameter claim.** Fast early-type galaxies show none of the extra mass it predicts, by nine standard errors. It also counts the modified-gravity boost twice.
- [F] **Gravity, the threshold that falls with redshift.** The repository states this prediction itself. Of 41 galaxies at redshift 0.7 to 2.5, none shows the predicted dark fraction.
- [I] **Maxwell's bound beyond nine charges.** Every construction known before this pass adds about 10 balance points per charge, and the bound grows with the square. Nothing known reaches the bound from 10 charges up. The growth found here, n^(3/2), does not reach it either.

A failed prediction that was stated in advance is a result. The repository wrote its redshift test down before anyone ran it, which is what made the test possible.

## How the threads tie together

### 1. The results that hold all have one shape

[I] Each verified result is a finite object that anyone can re-check with a short program: boxes that each hold one solution, a polynomial with the right signs, a run of zero residuals as long as a matrix is wide. The search that found it does not need to be trusted. The physics claims do not yet have this shape, and they are the ones that failed or stay open.

### 2. Two repositories ask the same question

[I] "How many of the complex solutions can be made real?" is the question behind the rigid graphs and behind Maxwell's conjecture. For the rigid graphs the answer is now "all of them" at 10 and 11 vertices. The local model in the five-charge counterexample has 21 complex solutions, all real.

[F] So the engine that made the rigid graphs real was run on the open three- and four-charge cases. It found nothing above the bound. [I] For three charges it showed why: the nearby complex solutions belong to systems with a negative charge. For four charges a tenth balance point was close and blocked.

[F] The four-charge case then fell to the same idea used differently. At the centre of a regular tetrahedron 11 solutions coincide, and a small move of the charges makes all 11 real and distinct. The rigid graph with every realization real sits beside the point where all edge lengths are equal. Both records sit next to the most degenerate arrangement.

### 3. Three repositories are one programme

[I] Balance points of fixed charges are also the balance points of fixed masses under gravity, because the equations are the same. Central configurations are the rotating version. The orbit repository is the moving version. One checker design serves all three.

[F] The central-configuration thread used that design and certified the known lists for 8, 9 and 10 equal masses, with the index and symmetry of every class. A complete list for 8 is out of reach of one pass: the published method would need decades of processor time.

### 4. Striking counts sat in narrow windows

[I] With the constructions known before this pass, Maxwell's bound was beaten only for 5, 6 and 7 charges. Four charges now join them. The four speeds near 185 km/s met in a range, 200 to 280 km/s, where the data table held no system. In both cases the test was to look outside the window: larger numbers of charges, and systems in the gap.

### 5. One set of galaxies speaks to two ideas

[F] The same hundred galaxies at redshift 0.6 to 2.5 test both the falling threshold and the growing acceleration scale. Both ideas predict more gravity at early times than the baryons give with today's constant scale. The galaxies show about what the constant scale predicts.

[I] The threshold fails outright, because it would need baryonic masses seven times too large. The growing scale only leans toward failing, because a mass drift of 0.2 dex per unit of redshift would rescue it.

### 6. Checkers that pass when they should fail

[F] The repository verifier for the point charges prints VERIFIED on a corrupted certificate when Python runs with `-O`. The science pass found the same fault in the gravity scripts and in vitruvian3d. That is three repositories. Every checker written in this pass raises an error instead of using `assert`, and was run under `-O` against corrupted input.

## On the larger aim

[I] Nothing here is a step toward a single physical theory. What holds is exact mathematics. One of those results shows that the bound Maxwell proposed in 1873 already fails at four charges. In the physics threads the pass removed two claims that later work should not build on, and left one residual that existing proposals already try to explain.

[I] The way forward that this pass supports is narrow. Predict the same quantity the data holds. Write the test down before running it. Fill the gap in the data before reading meaning into a coincidence across it.

## What to do next, in order

1. Have someone outside the organisation check the four-charge certificate. It is four charges and twelve coordinates of five decimals, and the eleven points are listed. Then write to the authors of the July paper.
2. Have someone outside the organisation check the 2,288 certificate, then write to the authors of the published bound.
3. Send the code-table improvements to the table's maintainer. A draft message is ready.
4. Review the draft pull requests listed in `SYMBIOSIS.md`. They carry the verifier fixes, the new certificates and the corrected wording.
5. In gravity, retire the zero-parameter claim and the falling threshold, and rebuild the table from published values.
6. Offer the recurrence proofs and the square law to the OEIS after a person has read the argument.

Items that would change a label on a merged claim or a published record are for the owners to decide. This folder changes no research repository. The draft pull requests in `SYMBIOSIS.md` do, and none is merged.
