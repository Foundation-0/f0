# Thread: four charges with eleven balance points

Follow-up to `point-charges.md`, `maxwell-push.md` and `relational-geometry.md`, 15 November 2026. Pinned head `point-charges@a2fd159`. Marks: **[F]** fact from a run, **[P]** a published result, **[I]** inference, **[C]** conjecture.

## Result

[F] Four positive point charges can have exactly 11 balance points, all non-degenerate: 7 of index 2 and 4 of index 1. Maxwell's bound for four charges is 9.

[F] Two configurations were built, by two different methods and two separately written sets of programs. For each one, two exact programs prove the count is exactly 11, and a third program proves it is at least 11.

Status: VERIFIED in the sense this review uses, meaning separately written programs accept it. Nobody outside the project has checked it.

## The two configurations

| | Jet route | Flat route |
|---|---|---|
| File | `checks/four/jet-route/n4_eleven_b12.json` | `checks/four/verify/n4_eleven_flat.json` |
| Charges | 1, 0.851, 0.864, 0.838 | 1, 0.280, 0.267, 0.263 |
| Shape | a tetrahedron about 0.05 from the regular one | one large charge at 0.846 from the flat point, three small ones at 0.49 |
| Balance points | 8 within 0.001 of the design point, 3 at 0.011 to 0.018 | 8 within 0.0026 of the flat point, 3 at 0.027 to 0.030 |
| Coordinates | 12-digit decimals | 14-digit decimals |

`n4_eleven_a.json` is the jet-route configuration to 25 digits. It passes the same programs.

## Checks

| Program | What it proves | Jet route | Flat route |
|---|---|---|---|
| `indep_count.py`, run with `-O` | exactly N, by covering the whole region with boxes that hold no zero | 11, from 36,897 boxes | 11, from 33,873 boxes |
| the repository's `verify_arb.py` | exactly N | VERIFIED 11 | VERIFIED 11 |
| `lower_bound_check.py`, new | at least N | 11 | 11 |

- `indep_count.py` reads only the sites and the charges. It is the third checker from `point-charges.md`.
- `verify_arb.py` is the repository's own verifier at the pinned head. It was run without `-O`, because at that head its checks are `assert` statements.
- `lower_bound_check.py` was written for this result without reading the other two. It finds its own candidates, then proves one zero in each small cube with the Krawczyk test in ball arithmetic, and fixes the index from the sign of the determinant.

[F] Controls, all of which fail as they should:

- Claiming 13 on the jet-route configuration gives a mismatch.
- The jet-route recipe with a linear term of -1e-10 in place of -3e-10 gives 9.
- One charge of the jet-route configuration multiplied by 1.000001 gives 5.
- The repository verifier fed the 11 boxes with one charge changed fails its test.
- `lower_bound_check.py` asked to prove 12 stops with an error.

## How narrow it is

[F] Both configurations are needles. `checks/four/verify/width.py` multiplies every coordinate and charge by a random factor and counts again, numerically.

| Relative change | Flat route, 12 trials | Jet route, 12 trials |
|---|---|---|
| 1e-8 | 11 in all 12 | 11 in 1 |
| 1e-7 | 11 in all 12 | 11 in 2 |
| 1e-6 | 11 in 7 | 11 in none |
| 1e-5 | 11 in 2 | 11 in none |
| 1e-4 and above | 11 in none | 11 in none |

[I] This is why random search never found it. In the repository's sample of 25,108 random four-charge configurations, 25,054 have the least possible count of 3.

## How it was found

### The starting point

[F] At the centre of a regular tetrahedron of equal charges the potential is 4/√3 + (20√3/27) xyz - (14√3/243) K4 + higher terms, with K4 = x⁴ + y⁴ + z⁴ - 3(x²y² + y²z² + z²x²). The linear and quadratic terms vanish.

[F] That centre is a balance point of multiplicity exactly 11. The dimension count that gives the multiplicity runs 7, 10, 11, 11 and stays there, for the true series and not only for a truncation. `checks/four/jet-route/milnor.py` computes it.

[F] Numerically the centre is the only balance point of the regular tetrahedron, from 20,000 starts. So 11 is the most this one point could give, and the question was whether all 11 can be made real at once.

### Jet route

The program `jetsolve.py` solves 16 equations for the sites and charges that give a chosen gradient, Hessian and cubic part at the origin. The values that work are a gradient of -3e-10 in each coordinate, a Hessian with diagonal 2e-6, 2e-6 and -4e-6, and cubic coefficients of 1.0e-3, 1.2e-3 and 0.8e-3.

[I] Along each axis the reduced equation has three roots at well-separated scales. Two more points sit near the centre. Three axes times three, plus two, is 11. A first try with a different Hessian gave 7, as the reality condition for the outer pair predicts.

### Flat route

Call a point *flat* when both the gradient and the whole Hessian of the potential vanish there. That is 8 conditions.

[F] **Closed form.** Every four-charge configuration with a flat point at the origin comes from a unit vector n in four dimensions with all entries positive. Put t = n / √(1 - n²) entry by entry. Then site i lies at distance t_i from the origin, sites i and j have dot product -t_i² t_j², and charge i is t_i³ / (1 + t_i²). Rotation and overall scale are free. The regular tetrahedron is n = (1, 1, 1, 1)/2.

The derivation is in the header of `checks/four/flat-route/flat_param.py`. The same program checks it on random n: gradient and Hessian come out below 1e-13.

[I] In other words, reflect the four sites in a sphere about the flat point. The four images form a tetrahedron whose four altitudes meet at the flat point.

**What a flat point is worth.** Near a flat point the potential starts with a harmonic cubic C. Moving the charges slightly adds a linear term l and a quadratic term with a traceless matrix Q. The balance points near the flat point are then the real solutions of grad C(x) + Qx + l = 0. These are three quadrics, so there are at most 8 solutions.

[I] The equation keeps its form when x, Q and l are scaled by s, s and s². So if the cubic model has 8 real solutions, the true potential has them too once the scale is small enough.

[F] All 8 can be real. `cubic_scan2.py` draws flat configurations and pairs (Q, l) at random and solves for all 8 roots.

| Where n is drawn | Samples | With all 8 real |
|---|---|---|
| near the regular tetrahedron, spread 0.05 | 200,000 | 2,197 |
| spread 0.15 | 200,000 | 641 |
| the whole flat family | 200,000 | 139 |

[I] **The rest of the configuration.** The gradient of a cubic is a quadratic map. Its local algebra has graded pieces of size 1, 3, 3, 1 and pairs degree k with degree 3 - k, so its signature is 0. The local degree of a flat point is therefore 0. The other balance points must then satisfy index-2 minus index-1 = 3 on their own, so there are at least 3 of them.

[F] So an all-real unfolding of one flat point gives at least 8 + 3 = 11. `realise.py` turns a hit of the cubic model into an actual configuration by Newton steps on the 8 conditions. The first hit tried gave 11 at three scales. In the certified one, 4 points of each index lie near the flat point and 3 of index 2 lie further out.

## Walls

[F] In both configurations all six pairs of charges share a wall, and one pair shares two. That is seven walls, and 2 × 7 - 3 = 11. The trace is numerical. It held when the step was cut from 2% to 0.5%.

[F] `relational-geometry.md` said, before this was found, that beating 9 needs seven walls: keep the doubled wall of the second family and gain its missing one. Both configurations do exactly that.

[F] The older tracer `wall_graph.py` reports a wall from one charge back to itself here. Its first step is larger than the inner cluster. `walls2.py` scales its step to the distance from the nearest balance point and does not have this fault.

## What is published

- [P] arXiv:2607.27197, 29 July 2026: five charges with at least 24 balance points, and 3 + 2m charges with at least 4 + 20m. It does not treat four charges.
- [P] arXiv:2607.28785: three positive charges have at most 6.
- [P] A 2022 paper gives nine balance points for four charges in a plane, which meets the bound.
- [P] arXiv:2501.05315 treats the centre of the regular tetrahedron as degenerate and says only that it splits into three saddles.

[F] Searches on 15 November 2026 found no report of more than 9 for four charges, and none of the multiplicity 11. That is "no earlier report found". It is not proof that the result is new.

[I] If the result holds, four is the smallest number of charges at which Maxwell's bound is known to fail. For three charges the bound is 4 and the proved limit is 6.

## Not verified

- Nothing here shows that 11 is the largest count for four charges.
- The two derivative bounds that `indep_count.py` relies on are proved by hand, not by machine.
- That the regular tetrahedron has only one balance point is numerical.
- The degree argument is a sketch. The certified counts do not depend on it.
- The wall traces and the width table are numerical.
- The published papers were read from their abstracts and cached texts. No author was contacted.

## Open

1. A flat configuration with five or more other balance points would give 13 by the same unfolding. `survey_flat.py` counts them across the flat family.
2. Flat points whose cubic is itself degenerate have multiplicity above 8.
3. A sturdier example, one that survives changes of 1e-3, would be easier for others to check.
4. For more charges, one flat point is worth 8 balance points where a plain one is worth 1. Whether that raises the growth per charge is untested.

## Rerun

From `checks/four/`, with python-flint and NumPy installed. The first two commands need `indep_count.py` from `checks/charges/` and the repository's `verify_arb.py` at the pinned head.

```
python3 -O ../charges/indep_count.py verify/n4_eleven_flat.json out.json
python3 verify_arb.py verify/n4_eleven_flat.repo.json
python3 -O verify/lower_bound_check.py verify/n4_eleven_flat.json 11
python3 -O verify/lower_bound_check.py jet-route/n4_eleven_b12.json 11
python3 flat-route/flat_param.py
python3 flat-route/cubic_scan2.py 1 200000 0.05
python3 flat-route/realise.py flat-route/cubic_scan2_hits_1_0.05.json 4
```

Saved outputs sit beside each program. SHA-256 of the three certificates:

```
2cd7745142e187f545a56881e7ee5a5037651c0b79271b90c9ab16bae1b448d5  verify/n4_eleven_flat.json
e15e6c97b985a1b7a6d3d3c0de86a62c7fbc9c7c02396828164b6773970fd3c3  jet-route/n4_eleven_b12.json
e58ab31a00f824d086caafe4d0665b2dd0d98c22205ef932e6b7dd952399c469  jet-route/n4_eleven_a.json
```
