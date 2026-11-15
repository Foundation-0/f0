# Three-charge thread: working notes

All code in this directory is new (does not import repo code).

## Sources read
- arXiv:2607.28785v1 (GNNS, "From 12 to 6"), full HTML text, cached sources/html_2607.28785.html, text_2607.28785.txt.
- arXiv:math-ph/0409009v1 (GNS 2007 "Mystery of point charges"), PDF, cached sources/gns_0409009.pdf/.txt.
- Not read: Tsai 2015 (Physica D 309, equal charges), Tsai 2011, Killian 2009 (not on arXiv).

## Lemmas (proved by hand, see final report for write-up)
L1 planarity; L2 planar Laplacian = sum q/r^3; L3 index count m - s = -2.
L4 (barycentric form of the inverse map). x critical for q  <=>  q_i/r_i^3 proportional to the barycentric
   coordinates beta_i(x).  So Z(x) = [beta_i r_i^3].
L5 (minimum criterion). With M = sum beta_i u_i u_i^T (trace 1): Hess = C(3M - I), C = sum q_i/r_i^3.
   x is a min iff det M > 2/9 iff |m(x)| < 1/3, where m(x) = sum beta_i exp(2 i theta_i), theta_i = arg(x - a_i).
L6 (isotropic point). m has winding -1 on the blown-up boundary of the triangle, so it has a zero x*.
L7 (local model, small charge near the saddle of a pair). F_L(X) = X1^2 - X2^2/2 + 1/|X| - L.X has at most one
   local min for every L with L1 != 0. Proof: critical points <-> roots c in (0,2) u (2,inf) of
   c^{2/3}[L1^2/(2-c)^2 + L2^2/(1+c)^2] = 1; the ratio R(c) = 2(1+c)^4/((2-c)^3(2c-1)) has a single critical
   point c = 5/7 on (1/2, 2), so at most 3 roots on (0,2) and minima only for c in [1/2,2].

## Necessary and sufficient structure (generic)
Maxwell <=> at every fold parameter the other critical points are two saddles.
A + type cusp (kappa > 0), any A4 point, or a transversal double fold forces m = 2 nearby.

## Runs
- scan_shapes.py (2 workers) -> out/scan_shapes_{0,1}.json  (fold curve, cusps, cusp type, self-intersections)
- cusp_scan.py 200 -> out/cusp_samples.npy: 4866 cusp points in psi coordinates, Kn max -0.3338, approached
  in the limit r1 -> 0 (small charge near the saddle of the other two = L7 regime).
- l8_model.py -> out/l8_model.png: two charges in a uniform field, deltoid image, simple.
- l7_check.py: Newton count = 1D root count, never 2 minima (400 random L).
- run_cert3.py equilateral (b in [0.8660254037844385, 0.8660254037844387]) -> out/c3_equi.json PROVED
  (2645 candidate boxes, 7343 leaves, 55.1M pair resolutions, 378 s).
- verify_arb3.py out/c3_equi (independent arb re-check of exclusion/coverage and every leaf; phase B sampled).
- Lesson: arb ball multiplication overestimates wide products; the verifier uses endpoint intervals built on arb.
- right isosceles and obtuse certificates stopped unfinished when the report was called for (no FAIL lines up to then).
