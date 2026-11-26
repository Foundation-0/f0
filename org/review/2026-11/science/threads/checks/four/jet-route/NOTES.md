# Four charges: notes (deep/four)

## Result
[F] A configuration of four positive charges with exactly 11 balance points, all non-degenerate (index 1: 4, index 2: 7).
Certificate: n4_eleven_b12.json (12-digit rationals). Also n4_eleven_a.json (25 digits), same structure.
- indep_count.py (python -I -O): count=11, index1=4, index2=7, 36,897 boxes, 14 s. Log n4_eleven_b12.indep.log.
- repository verify_arb.py (run WITHOUT -O so its asserts are active), fed boxes from to_repo_format.py:
  "VERIFIED n4_eleven_b12: exactly 11 zeros ... index 1: 4, index 2: 7". Log n4_eleven_b12.repo.log.
Maxwell's bound for n=4 is 9, so if both programs are right this disproves it for four charges.

## Controls
[F] claim 13 on the true config: indep MISMATCH (exit 2). Charge 1 times (1+1e-6): indep count 5 (MISMATCH).
Linear term -1e-10 in place of -3e-10 (same recipe): indep count 9, agreeing with my finder's 9.
Repository verifier on the 11 boxes with charge 1 corrupted: Krawczyk assertion fails.

## Task A
[F] Taylor at centre (taylor_tet.out): V = 4/sqrt3 + (20 sqrt3/27) xyz - (14 sqrt3/243) K4 + 0 (deg 5) + (4 sqrt3/729) K6 + ...
[F] milnor.py: dim Q[x]/(J + m^k) = 7,10,11,11,11,... for the 6-jet; stabilises at k=5->6, so by Nakayama m^5 is in J and
mu = 11 exactly for the true analytic germ (J_true + m^k = J_6jet + m^k for k<=6).
[I] The germ is T_{4,4,4} (Kouchnirenko: Newton number 11; face polynomials non-degenerate).
[F numerical only] 20,000-start Newton finds no balance point other than the centre; so local degree is +3. Not proved.

## Task B: how the 11 was built
Solve for a configuration with prescribed 3-jet at the origin (jetsolve.py, 16 equations, mpmath Newton from the tetrahedron):
grad = (-3e-10)(1,1,1); Hessian diag (2e-6, 2e-6, -4e-6), off-diag 0; cubic T2 parts nu=(1.0,1.2,0.8)e-3;
cubic T1 parts 0 (rotation gauge); xyz coefficient as at the tetrahedron; q0 = 1.
Normal-form picture (T444 = xyz + a sum x_i^4, here a = c4 < 0): along axis i the reduced equation is
4 c4 x^3 + 6 nu_i x^2 + H_ii x + lam_i + lam_j lam_k/(c3 x^2) = 0, giving per axis an outer root (-1.5 nu_i/c4),
a small root (-H_ii/(6 nu_i)), an intermediate root (-lam_i/H_ii), plus two central points (need lam_x lam_y lam_z < 0).
Reality: 36 nu_i^2 - 16 c4 H_ii > 0 (only binds when H_ii < 0). Scale window H^2/c3 << lam << H^2/(6 nu).
3 axes x 3 + 2 = 11. Radii found: 2.7e-5 (x2), 6.6e-5, 1.1e-4 (x2), 3.8e-4, 4.4e-4, 9.9e-4, 1.1e-2, 1.5e-2, 1.8e-2.
[F] jac_check.py: Jacobian of the jet map at the tetrahedron has three small singular values (0.0102, 0.0102, 0.0056)
against >=0.43 for the rest: the T2 block (grad, Hessian off-diagonal, cubic nu) is ill-conditioned, so nu ~ 1e-3
needs site moves ~ 0.05. The config sits ~0.05 from the regular tetrahedron, charges 1, 0.851, 0.864, 0.838.
[F] First attempt (H_zz = -2e-5 with nu_z = 8e-4) gave 7: the z outer pair was complex, as the reality condition predicts.
[F] C3v two-parameter family (vertex 0 radius and charge): only 3 and 5 seen; [I] C3v cannot set the E part of the Hessian.

## Task D: walls
[F numerical] walls2.py (RK4, step 2% of distance to nearest balance point or charge): all 6 pairs share a wall and
pair 0-3 shares two. Same result with steps 0.5% and smaller start offset, and for both certificates.
[F] The older wall_graph.py reports a self-loop 0-0 in place of the second 0-3 wall. [I] artefact: its first step
(1e-3 x distance to nearest charge, ~1.7e-3) is larger than the inner cluster (1e-5 .. 1e-3).

## Not done (stopped on discovery, as briefed)
Task C (flat family survey) and the proof that the regular tetrahedron has only the centre. Max achievable count near
other flat points (U12-type cubics x^3-3xy^2, mu=12) not explored.
