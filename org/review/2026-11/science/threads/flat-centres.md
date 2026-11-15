# Thread: centres that are flat to high order

Follow-up to `four-charges-eleven.md`, 15 November 2026. Marks: **[F]** fact from a run, **[P]** a published result, **[I]** inference, **[C]** conjecture. Everything numerical here is uncertified. The thread is still being worked.

## The question

The four-charge result came from one point where the gradient and the Hessian both vanish. That point was worth 8 balance points. Can a point be flat to a higher order, and what would it be worth?

## An inversion rule

[F] Take charges q_i at sites a_i, at distances r_i from a point O. Reflect them in the unit sphere about O: charge m_i = q_i / r_i at b_i = a_i / r_i². Then the term of degree k in the Taylor series of the potential at O is the multipole of order k of the reflected charges. Dipole gives the gradient, quadrupole the Hessian, and so on.

The proof is the Legendre expansion: the degree-k term is the sum of q_i P_k(cos) |x|^k / r_i^(k+1), and q_i / r_i^(k+1) is m_i |b_i|^k. `checks/kflat/kelvin_check.py` confirms it for seven random charges to 12 digits, for k from 0 to 6.

So O is flat to order k, meaning every derivative of order 1 to k vanishes, exactly when the reflected charges have no multipole of order 1 to k.

[I] For four charges this is the closed form in `four-charges-eleven.md`, read another way. The reflected charges are n_i², which add to 1. Their centre of charge is at O and their inertia is the same in every direction.

## Regular solids

[P] Equal weights at the points of a spherical k-design have no multipole of order 1 to k about the centre. The regular solids are designs: the tetrahedron of order 2, the octahedron and cube of order 3, the icosahedron and dodecahedron of order 5.

[F] `checks/kflat/platonic.py` confirms the order for equal charges at the vertices, and counts the other balance points from 40,000 starts.

| Solid | Charges | Centre flat to order k | Most the centre can give, k³ | Other balance points | Maxwell's bound | Best known count |
|---|---|---|---|---|---|---|
| Tetrahedron | 4 | 2 | 8 (11 here, see below) | 0 | 9 | 11 |
| Octahedron | 6 | 3 | 27 | 0 | 25 | 29 |
| Cube | 8 | 3 | 27 | 12 | 49 | 49 |
| Icosahedron | 12 | 5 | 125 | 0 | 121 | 89 |
| Dodecahedron | 20 | 5 | 125 | 30 | 361 | 169 |

Near a centre that is flat to order k the potential starts with a harmonic form F of degree k + 1. Moving the charges adds harmonic terms of every lower degree. The balance points near the centre are the real critical points of F plus those terms. They solve three equations of degree k, so there are at most k³.

For the tetrahedron the cubic is degenerate, which is why the centre gives 11 and not 8.

[I] The row that stands out is the icosahedron. If most of its 125 could be made real, twelve charges would pass the best known count of 89. All 125 would pass Maxwell's bound of 121, which nothing known reaches from 10 charges up.

## How many can be real

This is the whole question, and it is open.

- [F] Order 2. All 8 can be real. This is proved in effect by the certified four-charge configurations.
- [F] Order 3, the octahedron. In 4,000 random choices of the lower terms the real count ran from 5 to 13 of 27. A climb that pulls complex pairs toward the real axis reached 17, with 11 of index 2 and 6 of index 1. That fits the local degree of 5.
- [F] Order 3, two scales. With only a cubic term added, the origin keeps 8 of the 27 and the other 19 sit further out. In three climbs at most 13 of those 19 were real. With 8 more from the inner cluster that points to about 21.
- [F] Order 5, the icosahedron. The solver used here fails on most samples at 125 roots. The 16 samples it solved had 11 to 15 real. That says nothing yet about the largest count.

[I] So the octahedron does not reach its record of 29 by this route, and probably not Maxwell's 25 either. The case that matters is the icosahedron, and it needs a better solver and a structured search. A worker is on it.

## Answered since

[F] `growth.md` answers the general question. A harmonic polynomial of degree d in three variables can have about d³/6 real critical points, by stacking levels at separated scales. That is enough for growth like n^(3/2), which that note argues in four steps and confirms with exact lower bounds for 9 and 21 charges. The icosahedron question below is still open.

## Why this could change the growth law

[P] Spherical k-designs exist with a number of points that grows like k².

[C] If a fixed share of the k³ critical points can be made real for every k, then n charges can have of order n^(3/2) balance points. Every construction known today grows like 10n.

[I] The conjecture turns on one number. Let M(d) be the most real critical points a harmonic polynomial of degree d in three variables can have. M(3) is 8.

[P] In two variables the answer is d - 1, far below the count of complex solutions, because a harmonic function there is the real part of an analytic one.

[I] If three variables behave like two, M(d) grows like d² and nothing is gained. If M(d) grows like d³, the growth law changes.

## Tests

1. The largest real count for the icosahedral form with lower harmonic terms. A count of 91 or more, realised by 12 charges and certified, would be a new record for twelve charges.
2. The largest real count for a harmonic quartic, with the octahedral leading form and with a general one.
3. Lower bounds for M(4), M(5) and M(6), and any argument for an upper bound.
4. A literature search for critical points of harmonic polynomials in three variables.
5. For the map from charge moves to lower harmonic terms, a check that it has full rank at the icosahedron.

## Rerun

```
python3 checks/kflat/kelvin_check.py
python3 checks/kflat/platonic.py
python3 checks/kflat/kflat_scan.py octahedron 4000 1
python3 checks/kflat/kflat_climb.py octahedron 12000 4
python3 checks/kflat/outer_scan.py octahedron 3000 6000 1
```

They need NumPy and mpmath. `polysys.py` is the solver they share. Saved output is in `checks/kflat/runs.out`.

## Not verified

- Every count in this note is numerical.
- The solver was tested only on systems with known roots, up to degree 5.
- That the octahedron and icosahedron have no balance point other than the centre is from random starts.
- The step from the polynomial model to actual charges was done only for order 2.
- No literature search was made for this note. The worker's search will be added.
