# Thread: how real a rigid graph is near equal edge lengths

Follow-up to `l2288.md`, 15 November 2026. Pinned head `rigid-realizations@298926c`. Marks: **[F]** fact from a run, **[I]** inference, **[C]** conjecture. Every count in this note is numerical. Nothing here is certified.

## Question

The graph with all 2,288 realizations real was found with every edge length within 0.8% of 1. Is that an accident of the search, or do realizations become real near the point where all lengths are equal? Nobody appears to have measured it.

The hypothesis was written down before looking: near the all-equal point the share of real realizations is much higher than far from it, and the chance that a random direction gives all of them real does not shrink to zero as the graph grows.

## Result

The first half holds strongly. The second half is false as stated, and what replaces it is more useful.

### Realizations are far more often real near equal lengths

[F] For the largest graph on 6 to 11 vertices, edge lengths were drawn in two ways: close to the all-equal point (squared lengths 1 + eps u, with u a random direction and eps from 0.001 to 1), and far from it (each length uniform between 0.5 and 1.5). There were 12,307 samples and the solver returned the full set of solutions in every one.

| Vertices | Complex realizations | Mean real share, near (eps = 0.001) | Mean real share, far |
|---|---|---|---|
| 6 | 24 | 0.90 | 0.52 |
| 7 | 56 | 0.82 | 0.38 |
| 8 | 136 | 0.80 | 0.27 |
| 9 | 344 | 0.79 | 0.18 |
| 10 | 880 | 0.73 | 0.14 |
| 11 | 2,288 | 0.68 | 0.10 |

[F] The difference is significant in every graph (Mann-Whitney p between 1e-32 and 1e-121). The real count falls as eps grows, and on 90 to 99% of rays it never rises.

### A random direction is almost never all real

[F] The share of random directions with every realization real is 0.395 for 6 vertices and 0.090 for 7. For 8, 9, 10 and 11 vertices it is zero in every sample: 0 of 300, 0 of 124, 0 of 220 and 0 of 93.

### But all-real directions exist, and the record is one of them

- [F] For 8, 9 and 10 vertices a directed climb found directions u whose whole ray is all real, at every eps tested from 0.001 down to 0.00001. For 10 vertices there are at least two, 126 degrees apart.
- [F] The certified 880 point lies on such a ray. Along its direction the count is 880 of 880 at every eps from its own 0.033 down to 0.00001.
- [F] Along the direction of the published lengths (Bartzos and co-authors) the count is 868 at its own eps of 0.0019 and at every smaller eps tested (0.001, 0.0001 and 0.00001). At larger eps it is lower: 860 at 0.003 and 856 at 0.01 (`checks/unit/certray_868.json`).
- [F] The all-real cone is open and thin. For 8 vertices, 27 of 30 directions tilted by 0.02 radians stay all real, and 3 of 30 at 0.4. For 10 vertices it is 8 of 20 at 0.02 and none at 0.1.
- [F] For 11 vertices the certified direction gives 2,288 at eps of 0.001 to 0.01 and 2,284 at 0.0001. Whether a ray exists that is all real all the way in is open.

[I] So the record counts are a property of a direction at the all-equal point, not of a distance from it. The published search and the repository's search were both near that point. They differ in direction.

A correction to the premise of this thread: the published lengths are closer to the all-equal point than the 880 lengths are (eps of 0.0019 against 0.033), not farther.

## What the solutions do as lengths approach equality

[F] Along a ray the solutions do not pile up. All of them tend to distinct limits. They split into two kinds.

| Vertices | Fixed part | Moving part | Real share of the moving part |
|---|---|---|---|
| 6 | 16 | 8 | 0.69 |
| 7 | 24 | 32 | 0.68 |
| 8 | 44 | 92 | 0.70 |
| 9 | 92 | 252 | 0.71 |
| 10 | 168 | 712 | 0.67 |
| 11 | 312 | 1,976 | 0.62 |

- [F] The fixed part has the same limits on every ray. These are all real, and every vertex lies on the triangular lattice.
- [F] The moving part has limits that depend on the direction. Its real share is close to two thirds for every graph.
- [F] No limit was found that is both non-real and the same on every ray. So nothing seen forbids an all-real direction.

[I] A share near two thirds is what independent random real quadratics would give. A quadratic with independent standard normal coefficients has real roots with probability 0.65. So each moving pair behaves roughly as if a random real quadratic decided whether it is real. The counts of non-real pairs fit that for up to 8 vertices and are more spread out for 10 and 11.

[F] One statement in the repository's paper does not hold in these runs. It says every vertex of a unit-length realization of the 10-vertex graph lies on the triangular lattice. Only 84 of about 300 real limits per ray do.

## Conjecture

[C] For the largest rigid graph on each number of vertices there is a non-empty open cone of directions at the all-equal point along which every complex realization is real for all small enough perturbations. The cone's share of all directions tends to zero as the graph grows.

[I] If this holds, the largest real count equals the complex count for these graphs, and the search for a record reduces to finding one direction.

The cheapest test: for 11 vertices, climb at eps of 0.0001 from the certified direction with the trust-region method of the repository. Then do the same for the 12-vertex graph, where 588 solutions run off to infinity near equal lengths and may forbid it. A refutation needs a certified non-real limit that is the same on every ray.

## Rerun

Programs and data are in `checks/unit/`. `unit.py` draws the samples, `analyse.py` produces `analysis.txt`, `structure.py` and `struct_an.py` the limits, `conesize.py` the width of the cone. `allreal_lengths.json` holds the all-real lengths found for 8, 9 and 10 vertices, uncertified.

## Not verified

- Nothing is certified. The solver's separation between real and non-real solutions is more than six orders of magnitude, and no sample was rejected.
- Below eps of 0.001 the solver becomes unreliable for the largest graphs.
- The limits come from three rays per graph.
- The reviewer re-ran a fresh slice of 60 directions for 6 vertices: mean real share 0.88 near and 0.51 far, with 19 of 60 all real. That agrees with the full sample. The larger graphs were not re-run.
- No literature search was made.
