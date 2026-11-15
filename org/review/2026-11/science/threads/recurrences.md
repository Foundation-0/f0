# Thread: how far the recurrence proofs go

Follow-up to the science pass, 15 November 2026. Pinned head `finite-state-proofs@9eeb3da`. Marks: **[F]** fact, **[I]** inference.

## Question

The repository proves eleven recurrences that the OEIS lists only as "Empirical". The method looked general. How many more entries does it prove, and what stops it?

## Result

[F] 211 recurrences are now proved for every n from a stated starting index. 200 are new. The other 11 are the repository's own, redone as controls. None of the 211 listed recurrences turned out to be false.

| | |
|---|---|
| Entries proved | 211, in the range A268622 to A270054 |
| Families | 34: alphabets of 2 to 7 values, four kinds of neighbour, strip widths 1 to 7, both orientations |
| Recurrence order | 2 to 68 |
| States in the machine | 7 to 2,048 |
| Still marked "Empirical" at the OEIS on 15 November 2026 | yes, for each of the eleven controls |

The full list is `checks/oeis/table.md`. Each entry has a certificate in `checks/oeis/certs/`.

## The counting problem

[F] Each sequence counts grids of fixed width, with entries from a small alphabet, in which a neighbouring pair adding up to a given total occurs exactly once, or at most once. One reading of the OEIS wording fits every data term of all 211 entries: unordered neighbouring pairs, each counted once.

## Why a finite check proves it for every n

Rows are added one at a time. A state is the last row together with the number of counted pairs so far. That gives a matrix M of size D, and the count is a(n) = u M^(n-1) v.

[F] For a claimed recurrence, write r(n) for the amount by which it fails at n. Then r(n) is itself of the form u M^m w. By the Cayley-Hamilton theorem such a sequence obeys a recurrence of order D. So if r(n) is zero for D consecutive n, it is zero for every later n.

[F] So the recurrence holds from n = s onward exactly when it holds for the D values s to s+D-1. The terms printed at the OEIS, 11 to 31 per entry, are never enough for that. The terms come from the machine. The printed terms only confirm that the definition was read correctly.

## How it was checked

- [F] `checks/oeis/verify_all.py` rebuilds every machine from the definition and checks all 211 certificates in exact integers, in about 25 seconds, with and without `-O`. It rejects 105 of 105 corrupted certificates.
- [F] A brute-force count that shares no code with the machine builder matches the machines and the OEIS data for small n.
- [F] A third program, written for this review without reading the other two (`checks/oeis/spot_proof.py`), builds its own machine straight from the OEIS wording. It proves 46 of the entries, one from each combination of neighbour kind, alphabet, condition and orientation. All 46 give the same starting index as the certificates.

Verdict: **VERIFIED** for the 46 above, which have a third proof. REPRODUCED for the other 165. These are the labels in `README.md`. A later study (`square-law.md`) proved all 211 again by a different argument with separately written code, and the starting index agrees in all 211.

## Findings on the way

1. [F] In 121 entries the OEIS states a range such as "for n>7". In every one, that range equals the proved starting index.
2. [F] In 61 entries the recurrence has more terms than the OEIS prints. The printed data cannot test those at all.
3. [F] The repository's own test is stricter than it needs to be. Eight true recurrences fail it and need the weaker test above: A268627, A268636, A268748, A268763, A268771, A268778, A268909 and A268976.

## Update: the skipped entries are proved

[F] The 27 entries left unproved here are now proved in `square-law.md`. That note also explains why every one of these recurrences has an even order: each is the square of the recurrence for grids with no such pair. The limits listed below applied to the first method only.

## What stops the method

- [F] The number of states grows by about 1.7 times per extra column for two values, and much faster for larger alphabets. 27 entries of this family were left unproved for that reason. The largest has 24,192 states.
- [F] Square grids and two-parameter tables have no fixed width, so the method does not apply to them.
- [I] The candidate list is one family of definitions. Other families by the same contributor are also finite-state, and each needs its own parser. Thousands of entries are likely within reach.

## Rerun

```
python3 -O checks/oeis/verify_all.py          # all 211 certificates
python3 -O checks/oeis/test_corrupt.py        # corrupted certificates are rejected
python3 -I checks/oeis/spot_proof.py checks/oeis/certs
```

The verifier needs only the standard library. The builder in `checks/oeis/scripts/` needs NumPy.

## Not verified

- The match between grids and paths through the machine is argued, not machine-checked.
- Whether any of these recurrences has been proved elsewhere. No literature search was made.
- Whether the listed orders are the smallest possible.

## Next steps

1. A person reads the argument above, then the proofs can be offered to the OEIS as comments. Draft wording is in `checks/oeis/comments_draft.md`. Nothing was sent.
2. Merge states that behave alike, with a checked condition, to reach the 27 skipped entries.
3. Write parsers for the neighbouring families.
