# Thread: the 880 engine tried on the open Maxwell cases

Follow-up to the science pass, 15 November 2026. Pinned heads `rigid-realizations@298926c` and `point-charges@a2fd159`. Marks: **[F]** fact, **[I]** inference.

## Question

Two repositories solve sibling problems. One asks how many complex solutions of the edge-length equations of a rigid graph can be real, and found a push that drives complex pairs onto the real axis. The other studies Maxwell's bound on the balance points of point charges, where three charges (bound 4) and four charges (bound 9) are open.

Nobody had tried the first repository's engine on the second repository's open cases. This thread does.

## Result

[F] The push found nothing above the bound: no three-charge configuration with more than 4 balance points and no four-charge configuration with more than 9. Everything in this note is numerical except where marked proved.

| | Pushes | Steps | Best count reached |
|---|---|---|---|
| Three charges | 311 | 46,063 | 4 in 197 pushes, 2 in 114 |
| Four charges | 130 | 16,495 | 9 in 17, 7 in 23, 5 in 56, 3 in 34 |

[F] The engine was rewritten for this system. It reproduces the repository's 4 and 9, and climbs from 3 to 9 from a random start without help.

## One certified by-product

[F] The push found a second way to reach 9 with four charges, from a random start. The charges sit at the corners of an irregular tetrahedron with no symmetry, with charges near 1, 1.90, 1.20 and 8.30. All nine balance points lie within about 0.05 of one point.

[F] The separate checker from the point-charges thread proves the count is exactly 9 for this configuration, rounded to nine decimals (`checks/charges/configs/n4-second-family.json`). Verdict: **VERIFIED**. The repository's own example is a triangle with a charge near its centre, so this is a different family.

## The complex counts

The system is written with one unknown per charge for the inverse distance, which keeps every equation at degree 4.

- [F] Three charges in a plane: 68 complex solutions, which is 34 points. Two different solvers agree.
- [F] Four charges in space: 420 complex solutions, which is 210 points. Two different solvers agree.

[I] These counts are numerical. They would give upper bounds of 34 and 210 if proved, which is weaker than the published 6 for three charges (Gabrielov, Novikov, Novikov and Shapiro, arXiv:2607.28785).

[F] Proved here: three positive charges have all their balance points in their own plane, because the force across the plane never vanishes off it.

## Why the push stalls, and what that suggests

[F] One complex solution set covers every choice of signs for the charges. The solutions with all charges positive are only part of the real ones.

- **Three charges.** [F] In 333 of 344 configurations that reach 4, no complex pair lies in the all-positive region at all. Where one does, the nearest stays far away. The pairs that are close would become balance points of a system with one negative charge.
- **Four charges.** [F] At 9 there are still one or two candidate pairs, and one comes close. Moving toward it first merges two existing balance points, so the count falls from 9 to 7. When that merge is forbidden the push stops.

[I] For three charges this is new evidence of a specific kind. The earlier evidence was that sampling never found a fifth point. This says where a fifth point would have to come from, and that nothing is there. It suggests a route to a proof: show that at count 4 no complex solution lies in the all-positive region.

[I] For four charges the picture is different. A tenth point is close and blocked by a merge. That is the pattern one would expect near a configuration where the potential is unusually flat at a balance point. The five-charge counterexample was built around such a point.

## Rerun

Scripts and the summary are in `checks/cross/`. They need NumPy and SciPy.

## Not verified

- The counts 68 and 420.
- Every count in the tables above comes from floating-point tracking. Only the second 9-configuration is certified.
- A fault in the rewritten engine could hide a better configuration.

## Next steps

1. Prove the counts 68 and 420 with a certified solver.
2. Look for a four-charge configuration where the potential is flat to second order at a balance point, starting from the second family.
3. Try to prove the three-charge observation above.
