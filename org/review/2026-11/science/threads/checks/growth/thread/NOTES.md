# growth thread notes (deep/growth)

## Tools
- finder.py: multi-scale finder (seeds per charge at own scale, pairs, triples, random); float Newton, scale-free acceptance
  (Newton step < 1e-9 x distance to nearest site); high-precision (arb, 212 bits) refinement when charges span > 1e6 or
  spacings > 1e4; dedup relative to distance to nearest site; Morse checks M1 (m2-m1=n-1) and M2 (traced wall loops = m1;
  capture radius = dominance radius).
- validate.py -> out/validate.txt: [F] 4, 9, 24, 29, 44, 49, 64 for the seven certified configs, M1 and M2 pass on all.
  Earlier versions failed on n7-n9 (acceptance relative to total field; float noise in nested clusters); both Morse checks
  caught every failure.
- harm.py: harmonic polynomials, total-degree homotopy for grad P = 0.
- level.py, level2d.py: one level of a hierarchical unfolding (A deg p + B deg p-1).
- flatsolve.py: positive charges flat to order d-1 at the origin (jets 1..d-1 vanish).

## Results so far
- [F] Platonic shells of equal charges (out/shapes.txt): tetra 3 (+centre 4), octa 5 (all from the degenerate centre,
  local degree +5), cube 12 edge walls + 5 from the centre = 17, ico 11 (all from the centre, local degree +11),
  dodeca 30 edge walls + 13 from centre = 43. No face points on any Platonic solid (agrees with EFO's remark that
  Platonic/Catalan polyhedra have no 1-saddles). Idea 3 (edges + faces - 1) FAILS: 3,5,17,11,43 vs 5V-11 etc.
- [F] Centre insertion (idea 2): cube + small centre charge = 32 (+20 = 8 vertex + 12 edge directions) as predicted;
  icosahedron + centre = 12 only (H6_ico > 0 only at the 12 vertices; edge saddles are negative); dodecahedron + centre
  = 80 = 30 + 50 (20 + 30). So idea 2 is right for the cube, wrong in sign for the icosahedron (the 42 is not there;
  the dual dodecahedron gets 50).
- [F] R(d) hill-climb (perturbing a flat point of degree d): d=3 8/8 real; d=4 up to 19/27 (random and octahedral
  top); d=5 26/64. Hill-climbing is weak.
- [F] Level lemma: crossed zonal harmonics A = Z_p about z, B = Z_{p-1} about x: real nonzero critical points of A+B
  = I_p - 1 exactly for p = 3..14 (out/level_crossed.txt), I_p = number of crossings on RP^2 of the two nodal
  families (pairs of Legendre zeros a, b with a^2+b^2<1) ~ p^2/2. Euler count on RP^2: V=I, E=2I, F=I+1, each face with
  2m alternating arcs forces m-1 saddles (rotation index 1-m), sum = I-1.
- [I] Hierarchy: P = sum_k c_k A_k with alternating axes and c_{k-1}/c_k << 1: R(d) >= sum_{k=2}^{d-1} (I_k - 1) ~ d^3/6.
- [I] Realization: a spherical t-design with t >= 2(d-1) and equal charges is flat to order t; changing charges only is
  linear in the jet and the evaluation matrix has full row rank (design orthogonality), so any small jet is realized with
  positive charges. Designs exist with N = O(t^2) points (Bondarenko-Radchenko-Viazovska 2013). Hence M(n) >= c n^{3/2}.
- Literature checked (cached texts in threads/charges/sources): ABK 2607.27197 (ratio 10, Prop 1), EFO 2501.05315
  (ratio 25/7, polyhedra), 2609.09637. No superlinear lower bound stated.

## Hierarchy and real-charge demo (later)
- [F] hier.py, s=0.01 (out/hier_s0.01.txt): P = sum_{k=1}^{d} c_k Z_k (axes alternating z, x; level radii 0.01^j):
  real critical points 6, 13, 24, 41, 66, 97, 136, 185 for d = 3..10 = predicted sum_{p=2}^{d} (I_p - 1) exactly;
  all non-degenerate (min |eig|/max >= 0.09). s=0.03 loses 2-4 at d>=7 (levels too close).
- [F] level_crossed_homotopy.txt: total-degree homotopy (separate method) gives the same real counts I_p - 1, p=3..9.
- [F] flat points (nflat.py): positive charges flat to order d-1 found at n=6 (d=4), n=9 (d=5), n=21 (d=8), jet
  Jacobian full rank (15, 24, 63). Not found at n=5 (d=4), n=8 (d=5, 150 tries), n=10 (d=6), n=19, 20 (d=8).
  So n_flat(d) ~ (d^2-1)/3 in practice.
- [F] demo_flat.py on configs/flat_d5_n9.json: jet realized exactly (error 5e-43) with levels Z4(z) 0.42, Z3(x) 4.2e-4,
  Z2(z) 2.1e-8, x 5.2e-14 -> configs/demo_d5_n9.json (60-digit rationals). finder: 26 balance points (9 index-1,
  17 index-2), M1 and M2 pass. Near the flat point: 1 point at 2.8e-6 (level 2), 5 at 2e-5..7e-5 (level 3), 7 at
  1.5e-3..3.8e-3 (level 4): exactly 1, 5, 7 as predicted.
- [I] Level lemma proof sketch: real nonzero critical points of A+B <-> critical points on RP^2 of
  phi = (p-1) log|A| - p log|B| (Euler: grad A || grad B with x = t w). phi -> -inf on Z_A, +inf on Z_B. Each face of
  the arrangement Z_A u Z_B with 2m alternating arcs has rotation index 1-m. Euler on RP^2 (V=I, E=2I, F=I+1) gives
  sum (m_F - 1) = I - 1.
- zonal/sectoral pairs reach p(p-1)-1 (Bezout-full crossings) at p=7,9 but with points spread over radii 1e-7..1e7:
  too fragile for use (out/level_zs_small.txt, partial).

## More results
- [F] Task D cluster insertions at an O_h flat point (out/insert_cluster.txt, lam scan 1e-3..1e2, 26 values):
  cube outer + small octahedron 30 (5/charge), + small cube 32 (4/charge); octahedron outer + small octahedron 6,
  + small cube 56 (7/charge). All repeatable in principle (origin stays O_h flat). None reaches 10/charge.
- [F] Families (out/families_a.txt): random clusters, equal or unequal charges (1e-3..1), n = 5..30: always n-1 (a tree),
  one exception 6 at n=5. Chains n-1. Rings n+1 (one loop), ring + 1e-3 centre n+1.
- [F] Real-charge demos: n=12 (flat_d6_n12 + levels Z5..Z1): Taylor check finds 24 = 1+5+7+11 points in |x|<0.01;
  n=21 (flat_d8_n21 + levels Z7..Z1): 62 in |x|<0.01 with default seeds (expected 66 = 1+5+7+11+17+25 counting the
  top level, which straddles 0.01); rerun with more seeds pending.
- [F] check_taylor.py (separate from finder.py) reproduces the 13 points of demo_d5_n9 near the flat point to 9 digits.
- n_flat(d) found: 6, 9, 12, 16, 21 for d = 4..8 (= ceil((d^2-1)/3) for d >= 6).
- [F] I_p (crossings of P_p and P_{p-1} zero circles on RP^2) = floor(p^2/2) + 2[p = 3 mod 4] for all 2 <= p <= 400
  (out/Ip_growth.txt). S(D) = sum_{p=2}^{D} (I_p - 1): 24, 185, 1421, 169101 at D = 5, 10, 20, 100; S/D^3 -> 1/6.
- [F] finder controls (out/finder_controls.txt): n5 true 24; q5 -> 441/131072 gives 6; -> 641/131072 gives 10.
- [F] lattices: sc-2 17, bcc-2 8, fcc-2 15, sc-3 26, bcc-3 34, fcc-3 62 = n-1 except tiny blocks: slope 1.
- d8 demo with sigma 1/20: per-level counts 1,5,6,10,16,24 (one short from level 4 up) = level separation too small,
  as in the pure polynomial at s=0.03. Rerun with sigma 1/100 in out/demo_d8_n21_s100.txt.
- [F] demo_d8_n21_s100 (21 charges, flat to order 7, levels Z7..Z1 with radius ratio 1/100): Taylor check (degree 18,
  |x| < 0.06) finds level groups 1, 5, 7, 11, 17, 25 (= 66, exactly as predicted) plus 21 at the top level: 87 points.
- [F] demo_d6_n12 (12 charges): 24 in the four lower levels (as predicted) + 12 at the top level = 36 within 0.06.
- [F] nested shells: octa in octa n=12: 11 or 13; cube in cube n=16: 25. Trees or near-trees.
- indep_count on demo_d5_n9 did not finish (stopped by me); flat points need many small boxes for the
  second-order exclusion tests.
