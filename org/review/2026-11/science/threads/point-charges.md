# Thread: a separate proof of the point-charge counts, and two more

Follow-up to the science pass, 15 November 2026. Pinned head `point-charges@a2fd159`. Marks: **[F]** fact, **[I]** inference.

## Question

The repository gives exact counts of the balance points of 3 to 7 positive charges. The science pass could only re-run the repository's own verifier, which is a reproduction. The open step was a proof by code written separately. This thread supplies it, then asks where the counts lead for more charges.

## Result

| Charges | Maxwell's bound | Exact count | Split by index (1 / 2) | Source of the configuration |
|---|---|---|---|---|
| 3 | 4 | 4 | 1 / 3 | repository |
| 4 | 9 | 9 | 3 / 6 | repository |
| 5 | 16 | 24 | 10 / 14 | repository |
| 6 | 25 | 29 | 12 / 17 | repository |
| 7 | 36 | 44 | 19 / 25 | repository |
| 8 | 49 | 49 | 21 / 28 | new here |
| 9 | 64 | 64 | 28 / 36 | new here |

[F] `checks/charges/indep_count.py` proves every row. It reads only the positions and the charges. Verdict for the five repository counts: **VERIFIED**. They were REPRODUCED before.

[F] The two new configurations are also verified by the repository's own verifier, fed the balance points found here. So two programs agree on them.

## How the separate proof works

The program was finished and had produced its counts before the repository's three verifier files were opened.

1. [F] Far away: if a half-space holds every charge, the field cannot vanish outside it. Checked in exact fractions.
2. [F] Near a charge: inside a small ball around each charge its own field beats the sum of the others. Checked in exact fractions.
3. [F] Everywhere else: the box is split into eight until each piece is ruled out by one of two Taylor tests, or lies inside a ball that holds one proven balance point.
4. [F] Each balance point: a contraction argument on a ball proves that exactly one exists there and that it is not degenerate. The index is read from the sign of one determinant, because the potential is harmonic.

The two derivative bounds the tests rest on, 2/r^3 for second derivatives of 1/r and 6/r^4 for third derivatives, were derived by hand and checked numerically.

[F] It differs from the repository's verifiers in the search for points, the test for existence, the far-field and near-charge arguments and the way the index is found. Both use the same ball-arithmetic library. Seven charges take 128,817 boxes here against 394,265 in the repository's verifier.

[F] The count of index-2 points minus index-1 points equals the number of charges minus one in every row. The program does not use that relation, so it is a separate check.

## Negative controls

[F] All run under `python3 -O` and all fail as they should: a claimed count of 43 for seven charges, one changed charge for five and for seven, one moved charge for six. Garbage hint boxes change nothing, because the proof never reads them.

## A fault in the repository's verifier

[F] `verify_arb.py` uses bare `assert` for its proof steps (lines 180, 190, 195, 201, 245). Under `python3 -O` those lines do not run. With one box duplicated in the four-charge certificate it then prints "VERIFIED ... exactly 10 zeros". With a wrong index it prints VERIFIED too.

[I] The published counts are not affected, because the checks run without `-O` and the separate proof agrees. The fix is to raise an error in place of each `assert`.

## What is published elsewhere

- [F] Five charges: at least 24 (Arathoon, Ball and Kvalheim, arXiv:2607.27197).
- [F] Six charges: no count above 25 was found in print. The 29 appears only in this repository.
- [F] Seven and nine charges: 44 and 64 follow from a formula in the same paper (at least 4 + 20m for m added pairs). No explicit configuration or exact count was found.
- [F] Eight charges: the best published count found is 25, numerical.

The search covered the arXiv listing and the full texts of the three papers closest to the problem. This is "no earlier report found".

## Where the counts lead

[F] Every known way to build a configuration gives a count that grows in a straight line with the number of charges, about 10 per charge. Maxwell's bound grows with the square.

| Charges | Best known count | Maxwell's bound |
|---|---|---|
| 5, 6, 7 | 24, 29, 44 | 16, 25, 36 |
| 8, 9 | 49, 64 | 49, 64 |
| 10 | 69 | 81 |
| 20 | 169 | 361 |
| 40 | 369 | 1521 |

[I] So with what is known today, the bound is beaten only for 5, 6 and 7 charges and met for 8 and 9. From 10 up, nobody has a configuration that reaches it. Joining far-apart groups cannot change that, because the count per charge of a joined group never exceeds the best single group.

[I] The disproof of the conjecture is therefore a small-number event so far. Whether the true maximum grows faster than a straight line is open. One route to test: find how many balance points a harmonic polynomial of degree d can have. If that grows faster than d squared, nested constructions might beat a straight line.

The nine-charge window is narrow. Changing the last charge by half a percent gives 52 or 56 in place of 64.

## Rerun

```
python3 -I -O checks/charges/indep_count.py <certificate or config .json> out.json     # needs python-flint and NumPy
python3 checks/charges/growth.py
```

Seven charges take about a minute and nine about three. Saved logs are in `checks/charges/out/`.

## Not verified

- The two derivative bounds are proved on paper, not by machine.
- The argument that joining groups cannot raise the growth rate is written, not formalised.
- The three- and four-charge open cases were not attacked here (see `maxwell-push.md`).

## Next steps

1. Replace the `assert` lines in the repository's verifier and run its negative controls under `-O`.
2. Add the eight- and nine-charge configurations to the repository as certificates.
3. Tell the authors of the July paper about the exact counts for 6 to 9 charges.
