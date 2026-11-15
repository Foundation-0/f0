# Thread: what the box method delivers for 8, 9 and 10 equal masses

Follow-up to the science pass, 15 November 2026. Pinned head `relative-equilibria@bf1e1ce` (status: not started). Marks: **[F]** fact, **[I]** inference.

## Question

A central configuration is an arrangement of masses that can rotate rigidly under gravity. For equal masses in a plane, a complete proved list exists for 5, 6 and 7 bodies. The paper that proved those says of eight: "we were not able to obtain a rigorous listing" (Moczurad and Zgliczynski 2019, arXiv:1812.07279).

The repository proposes to use the box method here. This thread finds out what that method can deliver in one pass.

## Result

Classes are counted up to rotation, scaling, reflection and relabelling.

| Bodies | Classes proved to exist | With no symmetry | Published numerical lists |
|---|---|---|---|
| 8 | at least 20 | 2 | 20 (Ferrario 2002, Doicu and co-authors 2022) |
| 9 | at least 42 | 3 | 42 |
| 10 | at least 67 | 12 | 64 and 67 |

- [F] Every class is proved to exist, to be the only solution in its box and to be non-degenerate. The classes are proved different from one another.
- [F] The Morse index and the exact symmetry group of every class are proved as well.
- [F] Two programs that share no code accept every certificate, one in ball arithmetic and one in exact rational arithmetic. Both reject 15 kinds of corrupted input, also under `python3 -O`.

**Completeness is not proved for any of the three.** These are lower bounds. The lists match counts that were already published as numerical results, so this is not a new count.

Verdict: **REPRODUCED**. The two programs were written together. For this review the exact-rational verifier was re-run on 8 and 9 bodies, and a separate numerical check confirmed that every class satisfies the equations to 1e-14 (`checks/cc/spot_cc.py`). No third proof was written.

## What is new, as far as found

1. [F] **Public certificates.** The 2019 authors wrote that existence for the known lists was easy for them, and a later paper reports that they tested it up to 12 bodies. No certificates were found in print.
2. [F] **Proved Morse indices and symmetry groups.** With them the lists satisfy the Morse identity exactly: the alternating sum over classes equals 1/56 for 8 bodies, -1/72 for 9 and 1/90 for 10.
3. [F] **A match with a conjecture.** The counts by index equal Hampton's conjectured polynomials for 8 and 9 bodies (arXiv:1810.13011), term by term.
4. [F] **Three corrections to the published tables.**
   - For 9 bodies, one entry of the 2002 table has symmetry order 2, as Hampton suspected.
   - For 10 bodies, the entry that table calls the regular decagon is a different configuration with symmetry order 4. The true decagon is a separate class missing from it.
   - For 10 bodies there are 12 classes with no symmetry. Two papers say 11.

[I] Point 3 has a consequence. Every proved class is non-degenerate and the counts already equal the conjectured polynomial. Any further non-degenerate class would add to one coefficient. So for 8 bodies the conjecture holds exactly when the list of 20 is complete, and likewise for 9 and the list of 42.

Each of these is "no earlier report found".

## A caution from 10 bodies

[F] About 1.1 million random starts never found the regular decagon. Only a search started near the regular polygon found it. So a census that has stopped finding new classes can still be missing one. The census is evidence. It is not proof.

## What a complete list would cost

[I] The published method needed 8.5 million CPU-seconds for 7 bodies, and its cost grows about 200 times per added body. For 8 bodies that is 27 to 54 CPU-years in the authors' compiled code. It was not attempted.

[I] Three things could change that estimate. Clustered regions could be ruled out by formula, since most boxes die there. Boxes could be larger, since uniqueness holds here at radius 2^-12. Mirror symmetry could be used inside the search.

## How it ties to the other threads

[I] The equations are the gravity version of the point-charge equations with a rotation term. The certifier has the same design as the point-charge and rigid-graph checkers. The repository's plan to port one to the other is sound.

## Before anything goes further

The repository has an open issue saying to tell the Krakow group about the project before publishing any count. This note claims no new count. The owners should still write to that group before this is taken beyond the organisation's review record.

## Rerun

```
python3 -I -O checks/cc/verify_rational.py checks/cc/cert_n8.json      # exact rationals, standard library only, a few seconds
python3 checks/cc/cert_arb.py <census file> out.json                    # needs python-flint
python3 checks/cc/spot_cc.py checks/cc/cert_n8.json checks/cc/cert_n9.json checks/cc/cert_n10.json
```

## Not verified

- Completeness, for any number of bodies above 7.
- The step that turns the Morse index into a count of positive eigenvalues is the thread's own derivation. It reproduces the published indices for 3 to 9 bodies.
- Counts from the literature were read from text extracted from the papers.

## Next steps

1. Write to the Krakow group with the certificates and the three corrections.
2. Seed searches near regular polygons for 8 and 9 bodies, where the 10-body census failed.
3. Decide whether a fast exclusion search restricted to that region is worth building.
