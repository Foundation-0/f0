# Threads pulled after the science pass

15 November 2026. The science pass ended with a list of threads worth pulling (`new-ground.md` on draft PR 56). This folder holds what came out when each was pulled as far as it would go in one pass. Each thread has its own note, with the programs and saved outputs under `checks/`.

Marks: **[F]** a fact read from a repository or produced by a run, **[I]** an inference. Verdict words are those of `glossary.md` (draft PR 55).

## The short version

Six threads produced results that hold under separate code. The gravity thread produced clear failures and one survivor. Two threads ended without a decision, and each names what would decide it. One confirmed known lists and corrected three table entries.

| Thread | Outcome | Note |
|---|---|---|
| 11-vertex rigid graph | All 2,288 realizations can be real. New growth bound 2.4116 per vertex, above the published 2.3780. **VERIFIED** | `l2288.md` |
| 10-vertex rigid graph | The complex count of 880 is confirmed by three implementations, so "all 880 are real" is complete. **VERIFIED** | `rigid-realizations.md` |
| Point charges | The counts 4, 9, 24, 29 and 44 now have a proof by separate code. New exact counts: 49 for eight charges and 64 for nine. **VERIFIED** | `point-charges.md` |
| Code tables | One standard bound improves at least 2,418 entries of the reference tables for GF(7), GF(8) and GF(9). **VERIFIED** | `codes.md` |
| Recurrences | 211 recurrences that the OEIS lists as empirical are proved, 200 of them new. **VERIFIED** for 46, REPRODUCED for the rest | `recurrences.md` |
| Lattice elasticity and the fold | The theorem holds for dimensions 2 to 9 and the fold to the densest packing is confirmed. One wording error found. **VERIFIED** | `incentre-lattices.md` |
| Gravity threshold | The zero-parameter version and the falling threshold fail against published data. A weaker large-scale residual survives. | `gravity.md` |
| Acceleration scale and expansion | **Undecided.** The one fit possible leans against, and mass errors can reverse it. | `acceleration-evolution.md` |
| Central configurations | At least 20, 42 and 67 classes proved to exist for 8, 9 and 10 equal masses, matching published numerical lists. Three table entries corrected. Completeness not proved. **REPRODUCED** | `central-configurations.md` |
| The 880 engine on the open Maxwell cases | No count above the bound for three or four charges. A second four-charge family with exactly 9 is certified. | `maxwell-push.md` |

## What is new and holds

1. **A rigid graph on 11 vertices with every realization real.** [F] 2,288 of 2,288, certified in exact arithmetic and checked by a third program written for this review. [I] It raises the best known growth rate for real realizations from 2.3780 to 2.4116 per vertex. A survey from February 2025 still quotes the older figure.
2. **Exact counts for eight and nine point charges.** [F] 49 and 64, each equal to Maxwell's bound. No explicit configuration or exact count for these was found in print.
3. **Thousands of sharper entries in the standard code tables.** [F] Every one has an exact certificate that three checkers accept. The method is old. What is new is running it across the tables.
4. **200 more proved recurrences.** [F] None of the empirical recurrences tested was false.

Novelty in every case means "no earlier report found" after a stated search. It is not a priority claim.

## What failed

- [F] **Gravity, the zero-parameter claim.** Fast early-type galaxies show none of the extra mass it predicts, by nine standard errors. It also counts the modified-gravity boost twice.
- [F] **Gravity, the threshold that falls with redshift.** The repository states this prediction itself. Of 41 galaxies at redshift 0.7 to 2.5, none shows the predicted dark fraction.
- [I] **Maxwell's bound beyond nine charges.** Every known construction adds about 10 balance points per charge, and the bound grows with the square. Nothing known reaches the bound from 10 charges up.

A failed prediction that was stated in advance is a result. The repository wrote its redshift test down before anyone ran it, which is what made the test possible.

## How the threads tie together

### 1. The results that hold all have one shape

[I] Each verified result is a finite object that anyone can re-check with a short program: boxes that each hold one solution, a polynomial with the right signs, a run of zero residuals as long as a matrix is wide. The search that found it does not need to be trusted. The physics claims do not yet have this shape, and they are the ones that failed or stay open.

### 2. Two repositories ask the same question

[I] "How many of the complex solutions can be made real?" is the question behind the rigid graphs and behind Maxwell's conjecture. For the rigid graphs the answer is now "all of them" at 10 and 11 vertices. The local model in the five-charge counterexample has 21 complex solutions, all real.

[F] So the engine that made the rigid graphs real was run on the open three- and four-charge cases. It found nothing above the bound. [I] For three charges it showed why: the nearby complex solutions belong to systems with a negative charge. For four charges a tenth balance point is close and blocked, which marks where to look.

### 3. Three repositories are one programme

[I] Balance points of fixed charges are also the balance points of fixed masses under gravity, because the equations are the same. Central configurations are the rotating version. The orbit repository is the moving version. One checker design serves all three.

[F] The central-configuration thread used that design and certified the known lists for 8, 9 and 10 equal masses, with the index and symmetry of every class. A complete list for 8 is out of reach of one pass: the published method would need decades of processor time.

### 4. Striking counts sat in narrow windows

[I] Maxwell's bound is beaten only for 5, 6 and 7 charges with what is known. The four speeds near 185 km/s met in a range, 200 to 280 km/s, where the data table held no system. In both cases the test was to look outside the window: larger numbers of charges, and systems in the gap.

### 5. One set of galaxies speaks to two ideas

[F] The same hundred galaxies at redshift 0.6 to 2.5 test both the falling threshold and the growing acceleration scale. Both ideas predict more gravity at early times than the baryons give with today's constant scale. The galaxies show about what the constant scale predicts.

[I] The threshold fails outright, because it would need baryonic masses seven times too large. The growing scale only leans toward failing, because a mass drift of 0.2 dex per unit of redshift would rescue it.

### 6. Checkers that pass when they should fail

[F] The repository verifier for the point charges prints VERIFIED on a corrupted certificate when Python runs with `-O`. The science pass found the same fault in the gravity scripts and in vitruvian3d. That is three repositories. Every checker written in this pass raises an error instead of using `assert`, and was run under `-O` against corrupted input.

## On the larger aim

[I] Nothing here is a step toward a single physical theory. What holds is exact mathematics. In the physics threads the pass removed two claims that later work should not build on, and left one residual that existing proposals already try to explain.

[I] The way forward that this pass supports is narrow. Predict the same quantity the data holds. Write the test down before running it. Fill the gap in the data before reading meaning into a coincidence across it.

## What to do next, in order

1. Have someone outside the organisation check the 2,288 certificate, then write to the authors of the published bound.
2. Send the code-table improvements to the table's maintainer. A draft message is ready.
3. Fix the `assert` fault in the point-charge verifier and add the eight- and nine-charge certificates.
4. Tell the authors of the July paper about the exact counts for 6 to 9 charges.
5. Correct the "every shear modulus" wording in incentre-lattices.
6. In gravity, retire the zero-parameter claim and the falling threshold, and rebuild the table from published values.
7. Offer the recurrence proofs to the OEIS after a person has read the argument.

Items that would change a label on a merged claim or a published record are for the owners to decide. This folder changes no research repository.
