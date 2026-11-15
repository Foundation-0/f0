# The square law for strip counts

Follow-up to `recurrences.md`, 15 November 2026. Pinned head `finite-state-proofs@9eeb3da`. Marks: **[F]** fact, **[I]** inference.

## What was noticed

The 211 recurrences proved in `recurrences.md` count grids of fixed width in which a neighbouring pair with a given sum occurs exactly once, or at most once. Their characteristic polynomials were factored over the integers (`checks/converge/oeis_structure.py`).

- [F] 209 of the 211 are perfect squares. The other two, A268888 and A268997, are a square times (x + 1). No factor occurs more than twice.
- [F] In all 88 families where both conditions are proved, "exactly once" and "at most once" have the same polynomial.
- [F] For all 170 entries small enough to test with a separate machine, the square root g is the minimal recurrence of the count with no such pair at all. In the two exceptions that minimal recurrence is g (x + 1).

So the recurrence for "one pair" is the square of the recurrence for "no pair". The rest of this note states that as a theorem, proves it, and uses it.

## Setting

Fix the width, the alphabet, the target sum and the kinds of neighbour. Rows are added one at a time.

- Omega0 is the set of rows with no pair inside the row. Omega1 is the set with exactly one.
- `cnt(a, b)` is the number of pairs created between row a and the row b placed after it.
- A is the 0/1 matrix on Omega0 with `A[a][b] = 1` when `cnt(a, b) = 0`. B1 is the same with `cnt(a, b) = 1`.
- C goes from Omega0 to Omega1 and D from Omega1 to Omega0, each with no pair created.
- z(n) counts grids of n rows with no pair. e(n) counts grids with exactly one. The OEIS sequence is e(n), or z(n) + e(n).
- Write 1 for the all-ones vector, `R_r = A^r 1` and `L_p = 1^T A^p`. Then `z(n) = 1^T A^(n-1) 1`.

## Theorem

Let m be a monic integer polynomial of degree D with `m(A) 1 = 0`. Let `m*(x) = x^D m(1/x)` and `Q = (m*)^2`. Put N = 2D + 2 if Omega1 is not empty, and N = 2D + 1 if it is empty. Then for every n at least N, the sequences z, e and z + e all satisfy the recurrence whose coefficients are those of Q.

If `m = x^s h` with h(0) not zero, the recurrence has characteristic polynomial h squared. The factor x^s does not change the recurrence. It does raise N.

## Proof

**A symmetry.** Reversing a row left to right keeps the pairs inside it. Turning two stacked rows through 180 degrees shows `cnt(a, b) = cnt(rev b, rev a)`, for every kind of neighbour. So the transpose of A is A with rows and columns reversed, and `m(A) 1 = 0` holds exactly when `1^T m(A) = 0`. One hypothesis is enough.

**One side.** Let `R(x)` be the series with coefficients `R_r`. The coefficient of x^j in `m*(x) R(x)` is `A^(j-D) m(A) 1` for j at least D, which is zero. So `m* R = N_R`, a polynomial of degree at most D - 1. The same holds on the left: `m* L = N_L`.

**Where the single pair can be.** A grid with exactly one pair falls into exactly one of five cases.

1. The pair is between rows i and i + 1. Summed over i this is the sum over p + r = n - 2 of `L_p B1 R_r`.
2. The pair is inside a middle row. This is the sum over p + r = n - 3 of `L_p C D R_r`.
3. The pair is inside the first row: `u A^(n-2) 1`, with u the row vector `1^T D` taken over Omega1.
4. The pair is inside the last row: `1^T A^(n-2) c`, with c the vector `C 1` taken over Omega1.
5. One row only: the size of Omega1.

**The series.** A sum over p + r fixed is a product of series. So with E(x) the series of e(n),

`E = x^2 L B1 R + x^3 L C D R + x^2 u R + x^2 L c + |Omega1| x`.

Multiply by `(m*)^2` and use the previous step:

`(m*)^2 E = x^2 N_L B1 N_R + x^3 N_L C D N_R + x^2 (u N_R) m* + x^2 (N_L c) m* + |Omega1| x (m*)^2`.

**Degrees.** The five terms have degree at most 2D, 2D + 1, 2D + 1, 2D + 1 and 2D + 1. If Omega1 is empty only the first remains. The coefficient of x^n on the left is the recurrence applied to e at n. It vanishes once n exceeds the degree of the right side. That gives N.

**The pair-free count.** Its series is `x 1^T R`, so `Q Z = x (1^T N_R) m*`, of degree at most 2D. So z obeys the recurrence from 2D + 1 on, and so does z + e from N on. This ends the proof.

## What running it corrected

- [F] The first guess was that g itself kills the vector 1. That is false in 67 of the 211 entries. What kills it is `x^s g` with s from 0 to 6: s = 0 in 144 entries, 1 in 45, 2 in 10, 3 in 4, 4 in 6 and 6 in 2. Some rows cannot be continued for long without creating a pair, and the vector 1 has a part on them.
- [F] The index N is sharp. In 111 of the 211 entries the recurrence fails at N - 1 and holds from N.
- [F] The two (x + 1) entries need one extra line. The theorem gives the recurrence for P (x + 1). Its residual at n is r(n) + r(n-1), where r is the residual of the listed P. So r(n) = -r(n-1) from N on, and the single checked value r(N) = 0 makes r vanish from N - 1 on.

## The cheap proof

For each entry: take the integer square root g of the listed polynomial, find the smallest s with `A^s g(A) 1 = 0`, compute the count up to N, and check the recurrence on that window. With the theorem this proves the recurrence for every n from its starting index.

- [F] `A^s g(A) 1 = 0` is an identity between integers. It is checked modulo enough primes below 2^31 that their product exceeds twice a proved bound on the entries. The bound is the sum of `|g_i| rho^(i+s)`, with rho the largest row or column sum of A.
- [F] The machine applies A one column at a time and never stores it. The largest case has 279,936 rows.
- [F] The window of counts is recovered exactly from residues by the Chinese remainder theorem, with a proved bound on its size.

## Results

| | |
|---|---|
| Entries of the first pass proved again | 211 of 211, same starting index in every one |
| Entries the first pass skipped for cost | 27 of 27 proved |
| Verifier passes, all 238 | 238 of 238, 236 dense and 2 tensor |
| New entries proved in all | 227, with the 11 controls 238 |
| Starting index against the OEIS, for the 27 | equal to the stated start in all 27 |
| Corrupted inputs rejected | 73 of 73, also under `python3 -O` |

- [F] Every one of the 27 skipped recurrences is a perfect square. None needed the (x + 1) factor.
- [F] An entry the first method abandoned at 158 million transitions takes 1.4 seconds.
- [F] The verifier was re-run for this review on the 211 entries under `python3 -O`. All pass.

Verdict: **VERIFIED** for the 46 entries that `checks/oeis/spot_proof.py` proves again, written apart from the rest. **REPRODUCED** for the other 192. These are the other 165 of the 211, and the 27 added here. The 27 are proved by the square-law theorem and checked by the thread's verifier. The label is REPRODUCED and not VERIFIED because the dense verifier and the prover share a parser and were written in the same pass.

Four of the 27 need a closer note.

- A269765 and A270057 were first checked only through the prover's tensor engine. The dense verifier now also passes both.
- A269766 and A269900 are too large for the dense form here. The verifier checked them through the prover's tensor engine, which the verifier shares with the prover. A269766 was run through the verifier later than the rest.

The other 234 passed the dense verifier. The engine used for each entry is in the `verifier_engine` column of `checks/square/table.csv`, and the full output is `checks/square/verify_all.log`.

## How far the law goes

- [F] For grids with exactly j pairs, the same counting on 12 narrow strips gives the power j + 1 of g for j up to 3, in 48 of 48 cases.
- [I] The proof above covers j = 1 only. For j of 2 or more the middle factors act on other subspaces, and a proof needs the minimal polynomial of A there.

## Is it known?

[I] That one marked defect squares the denominator of a transfer-matrix count is a standard kind of fact, and a specialist will not be surprised by it. No statement of it for these OEIS entries was found, and the entries list their recurrences one by one without noting that they are squares. No literature search was made beyond that.

## Rerun

```
cd checks/square
python3 verify.py proofs/A2*.json          # all 238; the largest entry alone takes about 8 minutes
SQUARE_DENSE_MAX=60000 python3 verify.py proofs/A270057.json   # force the dense engine on a larger entry
python3 -O test_corrupt.py
python3 ../converge/oeis_structure.py ../oeis/certs
```

The prover needs NumPy. Per-entry data are in `checks/square/table.csv`.

## Not verified

- The tie between each OEIS name and its machine rests on matching the printed terms, 7 to 19 per entry, and on brute force for small cases.
- The law for two or more pairs.
- Whether each recurrence has the smallest possible order.

## Next steps

1. Prove the law for j pairs.
2. Apply the method to the neighbouring families of entries, where the first pass had no parser.
3. Offer the theorem with the proofs to the OEIS, after a person has read it.
