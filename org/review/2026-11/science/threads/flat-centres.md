# Thread: centres that are flat to high order

Follow-up to `four-charges-eleven.md`, 15 November 2026. Marks: **[F]** fact from a run, **[P]** a published result, **[I]** inference, **[C]** conjecture. Counts are numerical unless marked proved.

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

For the tetrahedron the cubic term is xyz, whose gradient vanishes along all three axes. So the cubic alone does not isolate the centre, and the quartic term adds one point along each axis: 8 + 3 = 11.

[I] The row that stands out is the icosahedron. If most of its 125 could be made real, twelve charges would pass the best known count of 89. All 125 would pass Maxwell's bound of 121, which nothing known reaches from 10 charges up.

## How many can be real

### A quartic with all 27 real

[F] A harmonic polynomial of degree 4 in three variables can have 27 real critical points, the most three cubic equations allow. Write K4 = x⁴ + y⁴ + z⁴ - 3(x²y² + y²z² + z²x²) and take

```
f = K4/3 - 0.00008 (x + y + z) + 0.0019 (xy + yz + zx) + 3.7 xyz
    + 0.046 [x³ + y³ + z³ - (3/2)(x²y + x²z + y²x + y²z + z²x + z²y)]
    - 0.045 [x²y + y²z + z²x - xy² - yz² - zx²]
```

- [F] Every term is harmonic, and the leading term is the octahedron's. The lower terms are unchanged by the turn that sends x to y to z.
- [F] `checks/kflat/verify/quartic27_check.py`, written for this review, proves 27 real and simple critical points for these coefficients, with 16 of one index and 11 of the other. It finds its own candidates and encloses each in a cube by a ball-arithmetic test. The check that f is harmonic is exact.
- [F] The thread found the model with nine-digit coefficients and certified it with its own interval prover. The two-digit version above is a rounding of it, and it still passes.
- [F] The points sit at three distances: 8 within 0.031 of the origin, 3 near 0.09 and 16 between 2.2 and 2.7. The 8 come from the cubic part and the other 19 from the quartic.

So the earlier climbs, which stalled at 17, were stuck. With the cubic that also has all 8 real, both degrees so far reach the full count.

### Higher degree, in the polynomial model

| Degree | Most the equations allow | Real critical points reached | Leading form |
|---|---|---|---|
| 3 | 8 | 8, proved | the cubic at a flat point of four charges |
| 4 | 27 | 27, proved | the octahedron's quartic |
| 5 | 64 | 52, certified by the thread | free |
| 6 | 125 | 83, certified by the thread | free |
| 6 | 125 | 77, certified by the thread | the icosahedron's sextic |

- [F] The counts for degrees 5 and 6 come from the thread's interval prover. The reviewer did not re-prove them.
- [F] With the icosahedron's leading form, the outer scale gave at most 31 of its 61 points in every family tried. That caps designs built on it near 95.
- [C] All (d - 1)³ critical points can be real for every degree d. It holds for d = 3 and 4.

### In actual charges

- [F] Twelve charges near an icosahedron were not built. The model count of 77 is below the 89 already known for twelve charges, and the scales in that model differ by factors near 1e-8.
- [F] At the icosahedron, moving the 12 charges reaches all 35 lower harmonic terms: the map has full rank.
- [F] At the octahedron it does not. Moving the six charges reaches 14 of the 15 lower terms. The xyz part of the cubic does not move at first order, and the quartic above needs it.
- [F] A test that carried a 51-point model over to charges in ordinary precision lost points at every scale tried. It needs extended precision.

[I] So neither solid gives a record. The octahedron could give at most 27, below the 29 known for six charges. The icosahedron's own leading form is a poor one. A different twelve-charge configuration with a centre flat to order 5 might do better, since a free sextic already reaches 83.

## Answered since

[F] `growth.md` answers the general question. A harmonic polynomial of degree d in three variables can have about d³/6 real critical points, by stacking levels at separated scales. That is enough for growth like n^(3/2), which that note argues in four steps and confirms with exact lower bounds for 9 and 21 charges. A separate construction in that thread, built from exponentials, also gives order d³.

## Why this could change the growth law

[P] Spherical k-designs exist with a number of points that grows like k².

[C] If a fixed share of the k³ critical points can be made real for every k, then n charges can have of order n^(3/2) balance points. Every construction known today grows like 10n.

[I] The conjecture turns on one number. Let M(d) be the most real critical points a harmonic polynomial of degree d in three variables can have. M(3) is 8.

[P] In two variables the answer is d - 1, far below the count of complex solutions, because a harmonic function there is the real part of an analytic one.

[I] If three variables behave like two, M(d) grows like d² and nothing is gained. If M(d) grows like d³, the growth law changes.

## Tests

1. A twelve-charge configuration, not the icosahedron, whose centre is flat to order 5 and whose leading form lets more than 89 of the 125 be real.
2. A pair of levels of degrees 5 and 4 with all 37 outer points real. That would give 64 real critical points at degree 5.
3. An upper bound of any kind below (d - 1)³. None is known here.
4. Carrying a model with moderate scale ratios over to charges in extended precision.

## Rerun

```
python3 checks/kflat/kelvin_check.py
python3 checks/kflat/platonic.py
python3 checks/kflat/kflat_scan.py octahedron 4000 1
python3 checks/kflat/kflat_climb.py octahedron 12000 4
python3 checks/kflat/outer_scan.py octahedron 3000 6000 1
python3 -O checks/kflat/verify/quartic27_check.py -0.00008 0.0019 3.7 0.046 -0.045
```

They need NumPy, mpmath and python-flint. `polysys.py` is the solver the first runs share. Saved output is in `checks/kflat/runs.out` and `checks/kflat/verify/`. The thread's programs and its certified models are in `checks/kflat/thread/`.

## Not verified

- The counts for degrees 5 and 6 rest on the thread's prover alone.
- That the octahedron and icosahedron have no balance point other than the centre is from random starts.
- The step from the polynomial model to actual charges was done only for order 2, and in the growth thread for stacked levels.
- The thread's literature search found no result on the largest number of real critical points of a harmonic polynomial in three variables that is not homogeneous. For the homogeneous case on the sphere a count of 2(d² - d + 1) is published. That is not proof the quartic is new.
