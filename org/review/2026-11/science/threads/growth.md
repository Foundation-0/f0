# Thread: balance points can grow faster than the number of charges

Follow-up to `point-charges.md`, `relational-geometry.md` and `flat-centres.md`, 15 November 2026. Marks: **[F]** fact from a run, **[P]** a published result, **[I]** inference, **[C]** conjecture.

## Result

[I] With n positive charges the number of balance points can grow like n^(3/2). Every construction known before this grows like 10n.

Status: an argument in four steps with a proof sketch, numerical checks of every step, and two exact lower bounds in actual charges. It is not a finished proof. No count for any particular number of charges is beaten. On the numbers below this route passes the known constructions only near 160 charges.

## The mechanism

**Step 1. A point that is flat to high order.** By the inversion rule in `flat-centres.md`, charges can be placed so that the potential at a point has no terms of degree 1 to d - 1.

- [P] Equal charges at the points of a spherical design do this, and designs exist with a number of points that grows like the square of their order (Bondarenko, Radchenko and Viazovska, 2013).
- [F] Solving for sites and charges together finds such points with fewer charges: 6, 9, 12, 16 and 21 charges for d = 4 to 8. That is about (d² - 1)/3. None was found with 5 charges for d = 4 or with 8 for d = 5.

**Step 2. One level.** Let A be the zonal harmonic of degree p about the z axis and B the zonal harmonic of degree p - 1 about the x axis.

[F] A + B has exactly I(p) - 1 real, non-degenerate critical points away from the origin, where I(p) is p²/2 rounded down, plus 2 when p leaves remainder 3 on division by 4.

| p | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|---|---|---|---|---|---|---|---|---|---|---|
| I(p) - 1 | 5 | 7 | 11 | 17 | 25 | 31 | 39 | 49 | 61 | 71 |

- [F] The thread found these counts for p = 3 to 14 by a search on a grid over the sphere, and for p = 3 to 9 by a homotopy method.
- [F] A program written apart from both finds the same counts for p = 3 to 12 (`checks/growth/verify/levels_check.py`). It uses a different fact: a critical point away from the origin lies in a direction where the gradients of A and B are parallel, and its distance is then fixed.
- [I] Proof sketch. These directions are the critical points, on the sphere with opposite points identified, of a function that goes to minus infinity on the zero set of A and plus infinity on the zero set of B. The two zero sets cut the surface into faces. A face with 2m sides forces m - 1 critical points, and Euler's formula sums these to I(p) - 1.

**Step 3. Stacking levels.** Take the sum of zonal harmonics of degrees 1 to D, with axes alternating between z and x and with coefficients chosen so that each degree rules at its own distance from the origin. Each level then behaves as in step 2.

[F] The sum has exactly S(D) real critical points, where S(D) adds I(p) - 1 for p from 2 to D.

| D | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|
| S(D) | 6 | 13 | 24 | 41 | 66 | 97 | 136 | 185 |

- [F] The thread finds these exactly for D = 3 to 10 with the levels a factor of 100 apart. With a factor of 33 a few points are lost from D = 7 up.
- [F] The separate program finds 6, 13 and 24 for D = 3, 4 and 5, each split by scale as predicted.
- [I] S(D) grows like D³/6.

**Step 4. Charges.** Start from a point that is flat to order d - 1. Small changes of the charges set the terms of degree 1 to d - 1 to any small values, here the stacked levels of step 3. The balance points near the flat point are then the critical points counted in step 3, once the scale is small enough.

[I] With about d²/3 charges and about d³/6 balance points, the count grows like 0.87 n^(3/2).

## The same thing in actual charges

Two configurations were built with exact rational sites and charges. For each, a lower bound is proved by `checks/growth/verify/lower_bound_hp.py`, written for this review. It trusts no candidate: each is refined in 260-digit arithmetic and then enclosed in a cube where a ball-arithmetic test proves exactly one balance point.

| Charges | Flat to order | Proved balance points | Of index 2, of index 1 | Groups by distance from the flat point |
|---|---|---|---|---|
| 9 | 4 | at least 26 | 17, 9 | 1, 5 and 7 at three scales, then 13 further out |
| 21 | 7 | at least 87 near the flat point | 47, 40 | 1, 5, 7, 11, 17 and 25 at six scales, then 21 at the top level |

- [F] The groups are the predicted I(p) - 1 for p = 2 to 4 and p = 2 to 7.
- [F] For 9 charges the 26 satisfy the index relation, so they are plausibly all of them. That is not proved: the exact count prover did not finish in an hour.
- [F] For 21 charges the 87 are only those within 0.06 of the flat point. The index relation shows at least 13 more further out.
- [F] These are needles. In the 21-charge example the level coefficients run from 1.8 down to 1.8e-54, and the innermost balance point is 1e-14 from the flat point.

## What it means

- [I] The largest number of real critical points of a harmonic polynomial of degree d in three variables is at least of order d³/6. `flat-centres.md` asked whether three variables behave like two, where the answer is d - 1. They do not.
- [I] Walls between charges, the index-2 points, also grow faster than the number of charges. So no bound of the form "a fixed number of walls per charge" can hold.
- [I] Maxwell's bound of (n - 1)² is not threatened by this for large n. The route here gives n^(3/2), and at most 8 n^(3/2) even if every complex solution were real.
- [F] It does not beat any known count yet. The best known counts are 10n - 26 and 10n - 31.

| d | Charges needed, about | Balance points from the levels | Best known for that many charges |
|---|---|---|---|
| 8 | 21 | 66 | 184 |
| 12 | 48 | 246 | 449 |
| 20 | 133 | 1,222 | 1,304 |
| 22 | 161 | 1,640 | 1,584 |
| 28 | 261 | 3,446 | 2,584 |

## Other findings of the thread

- [F] Random clusters of 5 to 30 charges, chains and lattice blocks have n - 1 balance points, the least possible. Rings have n + 1.
- [F] Equal charges on the regular solids have 3, 5, 17, 11 and 43 balance points once the degenerate centre is split. None has a balance point on a face.
- [F] A tiny charge placed at a balance point gives new points at the positive critical points of the leading harmonic on the sphere. This is confirmed for the cube, where it adds 20.
- [F] Small clusters placed at a flat point gave 4 to 7 new balance points per charge, below the 10 of the known constructions.
- [F] Climbing at random reached 19 of 27 real critical points for a harmonic quartic and 26 of 64 for a quintic. The stacked levels give 13 and 24, so they are not the best for small degree.

## Not verified

- The proof of step 2 is a sketch. It needs each face to be a disc and each critical point to be non-degenerate, for every p.
- The scaling argument that carries step 3 into step 4 is standard and is not written out.
- That changing the charges alone reaches every small set of low-degree terms is argued from the orthogonality of harmonics on a design. It was checked by rank for 6, 9 and 21 charges only.
- No exact count was completed for either configuration. The lower bounds are proved.
- No earlier statement of growth faster than linear was found in arXiv:2607.27197, arXiv:2501.05315 or arXiv:2609.09637, or by search. That is not proof that it is new.

## Next

1. Write out step 2 and the scaling step as full proofs.
2. Find the best real count for a harmonic polynomial of each small degree. The stacked levels are a lower bound and random climbs already beat them at degree 4 and 5.
3. Look for a level pair that fills more of the available solutions without spreading over many scales. That would bring the crossing point down from 160 charges.

## Rerun

```
python3 checks/growth/verify/levels_check.py
python3 -O checks/growth/verify/lower_bound_hp.py checks/growth/thread/configs/demo_d5_n9.json checks/growth/thread/out/demo_d5_n9_pts.npy 26
python3 -O checks/growth/verify/lower_bound_hp.py checks/growth/thread/configs/demo_d8_n21_s100.json checks/growth/verify/n21_candidates.npy 87
```

They need NumPy, mpmath and python-flint. The thread's own programs and saved outputs are in `checks/growth/thread/`, with its notes.
