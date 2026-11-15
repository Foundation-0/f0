# Why the same patterns keep turning up

15 November 2026. The owner asked why more and more patterns emerge from these threads, and whether that points to a deeper framework in mathematics or in physics. This note gives the answer the evidence supports. Marks: **[F]** fact from this folder, **[P]** a published result, **[I]** inference, **[C]** conjecture.

## The short answer

[I] There is a common framework, and it is a known part of mathematics: the study of how many solutions of a system are real, and how they appear when a degenerate arrangement is disturbed. The threads were chosen with that shape and attacked with one method, so some of the repetition was put in by the choice. What was not put in is that the same four tools did the work every time.

[I] It reaches physics wherever a field is harmonic. It does not point to new physics, and nothing here is a step toward a single physical theory.

## Part of the pattern was put there

- [F] The threads were picked from one list because each had a result that a short program could re-check. That selects problems of one kind.
- [F] After the first record was found beside a degenerate arrangement, the later searches started there on purpose. Finding more records in the same place is partly a result of looking there.
- [I] So "records sit beside the most degenerate arrangement" is supported by four cases, of which two were found by acting on it. It is a working rule, not a law.

## The four tools that recur

### 1. An index count fixes the difference, never the total

| Problem | What is fixed |
|---|---|
| Balance points of n charges | index-2 minus index-1 = n - 1 |
| One level of the growth construction | saddles minus extrema = I - 1 |
| An axisymmetric harmonic polynomial | points on the axis + 2 circles = k |
| A flat point of four charges | local degree 0 |
| Central configurations of equal masses | an alternating sum equal to 1/56, -1/72, 1/90 |

[P] All are forms of one theorem, due to Poincaré and Hopf: the indices of the zeros of a vector field add up to a number fixed by the shape of the space.

[I] This is why every count in the folder comes with a built-in test, and why the open questions are all about totals. The theorem gives the difference for nothing and says nothing about the sum.

### 2. A degenerate point has a budget

[P] A point where several solutions coincide has a multiplicity. Disturbing it releases at most that many solutions.

- [F] The centre of the regular tetrahedron has multiplicity 11, and a disturbance makes all 11 real.
- [F] A flat point with a general cubic has multiplicity 8, and all 8 can be real.
- [F] The octahedron's quartic has multiplicity 27, and all 27 can be real.
- [F] For three charges no flat point exists, and every cusp sampled is of the kind that releases one minimum, not two. The count stays at 4.

[I] So the question "what is the largest count" turns into two smaller ones. What is the most degenerate point the system can reach? And can all of its budget be made real?

### 3. Separated scales turn a hard system into easy ones

[F] The growth construction stacks levels a factor of 100 apart. At each scale only two terms matter, and the count is a sum over levels.

[P] This is the method by which real curves with a chosen shape have been built since the 1980s, known as patchworking: pieces that are each simple are glued at separated scales. Tropical geometry is the theory of that limit.

[I] The difference here is that the coefficients are not free. A harmonic polynomial of degree d has about d² of them, and the system has about d³ solutions. That is why the stack reaches a sixth of the possible count and not all of it.

### 4. Flatness is a moment condition

[F] By the inversion rule in `flat-centres.md`, a point is flat to order k exactly when the reflected charges have no multipole of order 1 to k. Equal charges on a sphere do this exactly when they form a design.

[F] The reviewer's exploration note in pull request 60 saw the next step. The bound on how small a design can be, and the bound used in the code tables, are the same bound, due to Delsarte. So the limit on growth per flat point and the limit on codes come from one theory.

## Why low degrees reach the full count

[F] In each problem the number of numbers one can choose grows slowly and the number of solutions grows fast.

| Problem | Numbers to choose | Solutions | Most made real so far |
|---|---|---|---|
| Harmonic polynomial, degree 3 | 8 | 8 | 8 |
| Degree 4 | 15 | 27 | 27 |
| Degree 5 | 24 | 64 | 52 |
| Degree 6 | 35 | 125 | 83 |
| Rigid graph, 10 vertices | 17 | 880 | 880 |
| 11 vertices | 19 | 2,288 | 2,288 |
| 12 vertices | 21 | 6,180 | 3,904 |

[I] The clean results, 8 of 8, 27 of 27, all 2,288, are at the small end, where there is still room to steer every solution. The share falls as the size grows. Whether it falls because the searches are weaker or because the full count is out of reach is not known.

[C] So the tidy pattern "everything can be made real" is likely a feature of small cases. It should be expected to fail at some size in each problem. Finding where, and why, would say more than another record.

## Where this is already physics

- [P] The Hessian of a harmonic potential has zero trace, so a charge cannot rest in stable balance in a static field. This is Earnshaw's theorem. It is the reason every balance point here has index 1 or 2.
- [I] A trap for ions built from many poles is a field whose centre is flat to high order. The inversion rule says which arrangements of electrodes give which order.
- [P] The number of images made by a gravitational lens is the same counting problem in a plane. Its bound of 5n - 5 is proved and reached.
- [P] The bright lines of light in a cup or on the floor of a pool are classified by the same theory of disturbed degenerate points.
- [P] The balance points of bodies in orbit, and whether their number is finite, is one of the open problems Smale listed for this century.

[I] In each of these the mathematics is the same because the field obeys the same equation. That is a connection through a shared equation. It is not evidence of a hidden common cause.

## What a deeper framework would have to do

[C] It would predict a count before it is computed. Two candidates come out of this folder, and both can be tested.

1. **The budget rule.** The largest count is the multiplicity of the most degenerate point the system can reach, plus what the index count forces elsewhere. It gives 11 for four charges and 4 for three. Test: find the most degenerate point reachable with five charges and compare with the known 24.
2. **The room rule.** All solutions can be real while the numbers to choose keep pace with the solutions, and not beyond. Test: find where the share first drops below one for harmonic polynomials. Degree 5 is the first candidate.

[I] If either rule fails its test, that is worth as much as if it holds. A framework that survives is one that could have failed.

## Not verified

- The table of shares mixes proved counts (degrees 3 and 4, the rigid graphs) with search results (degrees 5 and 6).
- The published results are cited from memory of the standard literature and were not re-read for this note.
- The two rules are conjectures. Neither has been tested beyond the cases that suggested it.
