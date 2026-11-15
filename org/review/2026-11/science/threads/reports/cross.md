# Rigid-realizations engine on three and four charges: full report

15 November 2026. Repository head pinned by the report: point-charges at a2fd159 and rigid-realizations at 298926c.

Short note for this thread: `../maxwell-push.md`.

S is the working folder of this thread. It is archived outside the repository. Paths that start with S/ point into it. Where a file was copied into the repository, its repository path is listed at the end.

---

# Cross thread: the rigid-realizations push engine applied to Maxwell's point-charge problem, n = 3 and n = 4

Date 15 November 2026, about 01:00 to 02:15 CST. Everything numerical is labelled numerical.
`[F]` = read at a pinned place or produced by a run here. `[I]` = my inference.

Pinned sources (read only):
- point-charges @ a2fd159bccb24d2922a127ad83f28b9f44e2ceba (NOTE.md, results/SUMMARY.md, verify_arb.py).
- rigid-realizations @ 298926c5e7a03683bb83165931ac38a94260166f (rigid_realizations_l880_pr_bundle/scripts/discovery/{l880_lib.py, lp_push_880.py, monodromy_l880.py}. Notes/l880-880-and-868-diagnostics.md).

The rigid-realizations engine is specific to its graph (edge tables, isotropic coordinates of a pinned triangle). I did not import it.
I rewrote its three ideas for this system: monodromy loops in complex parameter space, sensitivities dZ/dtheta of every solution from the implicit function theorem, and a trust-region linear program that moves the parameters to shrink the imaginary part of a chosen conjugate pair while linearised constraints keep the existing real solutions apart.
Tracking between real parameter points goes along a complex arc (as in `fast_move_adaptive`), so fold crossings do not stall the tracker.

## 1. The polynomial system

Unknowns x in C^D and t_i = 1/r_i (i = 1..n). Parameters: sites p_i and charges q_i.

    F_i = t_i^2 |x - p_i|^2 - 1 = 0          (n equations)
    G   = sum_i q_i t_i^3 (x - p_i) = 0       (D equations, equal to -grad V with V = sum q_i / r_i)

[F] (by construction) Using t_i = 1/r_i instead of r_i with cleared denominators removes the spurious r_i = 0 components: F_i forces t_i != 0 on every solution. Every equation has degree 4.

Sign symmetry. [F] If (x, t) solves the system for charges q, then (x, eps t) solves it for charges (eps_i q_i), eps_i = +-1. So, for fixed |q|, one complex solution set holds the equilibria of every sign pattern of the charges. For fixed q the only symmetry of the solution set is the global flip (x, t) -> (x, -t), which acts freely.
A real solution (x real, t real) is an equilibrium of the charges (sign(t_i) q_i). Physical equilibria (all charges positive) are the real solutions with all t_i > 0. Each appears twice, as (x, t) and (x, -t).

Planarity for n = 3. [F] (elementary proof) Put the sites in the plane z = 0. Then dV/dz = -z sum_i q_i / r_i^3, which is non-zero when z != 0 and all q_i > 0. So every equilibrium of three positive charges lies in their plane, and the n = 3 problem is planar (D = 2). The same statement is in point-charges NOTE.md section 1.
For mixed signs this argument fails, but the in-plane system still contains all in-plane equilibria of every sign pattern.

Code: `cross_lib.py` (system, Jacobian, parameter derivatives, batched adaptive predictor-corrector tracker).

## 2. Complex solution counts (numerical)

| case | variables | generic complex solutions (x, t) | distinct x | method |
|---|---|---|---|---|
| n = 3, planar (D = 2) | 5 | **68** | 34 | monodromy, 4 independent seeds (1,2,3,4): 68 each, stable for 10 to 15 loops, total-degree homotopy (1,024 paths, gamma trick) finds exactly the same 68 and nothing else |
| n = 4, space (D = 3) | 7 | **420** | 210 | monodromy, 3 independent seeds: 420 each, total-degree homotopy (16,384 paths) finds exactly the same 420 and nothing else |

[F] Logs: `out/mono_n4_s1.log`, `out/tdh_n4.log`. The n = 3 lines are reproduced in section 7. All final solutions have residual below 5e-14 and minimum pairwise separation above 0.1.
[I] The two methods are independent (different homotopies, different start points), so the counts 68 and 420 are solid numerically. They are not proved. A proof would need, for example, an exact Groebner basis at one rational parameter point (no Singular or Macaulay2 here) or a certified homotopy.

Split under the sign symmetry. [F] Each monodromy run started from one solution and its global flip and reached all 68 (or 420), so the monodromy group together with the flip acts transitively: over C there is one irreducible family, and "physical" and "mixed-sign" equilibria are not algebraically separated. The split exists only at real parameters:

- n = 3 (3,000 random real configurations, `out/summary_sample_n3.txt`, plus 412 push configurations): real x per configuration 8 or 10 of 34. Physical 2 or 4. Each of the three mixed classes (++-, +-+, -++) has exactly 2 real equilibria in every configuration sampled. The rest (24 or 26 x) are non-real.
- n = 4 (500 random real configurations, `out/summary_sample_n4.txt`): real x 24, 26 or 28 of 210. Physical 3 (499) or 5 (1). Each of the seven mixed classes has 3 (3,491 cases) or 5 (9 cases) real equilibria. At the repository's 9-configuration C_4: physical 9, class +++- 5, the other six mixed classes 3 each, total 32 real x of 210.

[F] (proof, Poincare-Hopf) In the plane, the gradient of V has index +1 around each site and +1 around a large circle when the total charge is non-zero. So the indices of the critical points sum to 1 - 3 = -2, and every sign class with non-zero total charge has at least 2 real equilibria.
In space the same argument gives index sum (#positive - #negative - 1) for positive total charge, so each mixed class of four charges has at least 1. The n = 3 samples sit exactly at this minimum.

What bound follows. Parameter continuation (Morgan and Sommese, see Sommese and Wampler, *The Numerical Solution of Systems of Polynomials*, 2005, ch. 7) says the number of isolated complex solutions at any parameter value, counted with multiplicity, is at most the generic count. A non-degenerate physical equilibrium gives two non-singular solutions (x, +-t). Hence, if the generic counts were proved:

- n = 3: at most 34 equilibria in the plane over all sign patterns. Subtracting 2 forced real equilibria in each of the three mixed classes (generic case) leaves at most 28 physical.
  This is weaker than Gabrielov, Novikov and Shapiro's 12 (arXiv:math-ph/0409009, abstract: the bound "is 12 for three charges", obtained from fewnomial theory) and much weaker than the 6 of Gabrielov, Novikov, Novikov and Shapiro (arXiv:2607.28785, "from 12 to 6"). [I] So the complex count gives nothing new for n = 3.
- n = 4: at most 210 equilibria over all sign patterns, so at most 210 physical (203 after subtracting one forced equilibrium per mixed class in the generic case). Enciso and Peralta-Salas (arXiv:2609.03965) give 2^{N-4}(N-1)(9N^2+9N+10), which is 570 at N = 4 (my arithmetic), in the region where their auxiliary function does not vanish.
  [I] 210 would improve 570, but only after the count 420 is proved, and it is still far from 9. I have not read their paper beyond the abstract, so I do not claim the two bounds count exactly the same objects.

## 3. The push (numerical)

Normalised real parameters: n = 3: p1 = (0,0), p2 = (1,0), p3 = (a,b), q = (1, e^l2, e^l3) (4 parameters). n = 4: p1 = 0, p2 = (1,0,0), p3 = (a,b,0), p4 = (c,d,e), q = (1, e^l2, e^l3, e^l4) (8 parameters). Writing charges as exponentials keeps them positive. Box: positions within [-3,4], b >= 0.02, log-charges within [-12,12] (n = 3) or [-16,16] (n = 4).

Target. For a non-real solution z, T(z) = |Im z|^2 + sum_i min(Re t_i, 0)^2: the squared distance from the real all-positive region. A conjugate pair can become two physical equilibria only by passing T = 0 (a fold into the physical class).
Each step: compute dZ/dtheta for all solutions, choose a target pair among the nearest three, solve an LP that decreases T(target) linearly within a trust region, subject to linearised constraints that the squared distance between any two physical solutions shrinks by at most 35% (this is the rigid-realizations separation constraint) and (push.py only) that no physical t_i grows more than 30% per step.
Track all solutions to the new point along a complex arc and accept if the physical count did not drop and the target moved closer.

- `push.py`: the direct transcription, stops after 3 rejected LPs.
- `push2.py`: one tracked target, persistent adaptive trust region, and up to 4 to 8 random kicks from the best configuration when the trust region collapses (basin hopping).

Sanity checks. [F] The engine reproduces the repository's counts: equilateral triangle with equal charges gives 4 physical. Triangle plus centre charge 2^-10 (C_4) gives 9. From a perturbed C_4 start at 5 it climbed 5 -> 7 -> 9 (`push_n4_centre.json`, start 4), so it can bring pairs in when they are there.

## 4. Results of the push (numerical)

No configuration with more than 4 equilibria for n = 3 or more than 9 for n = 4 was found. Task 4 (exact check of a find) was therefore not triggered, and nothing was sent to a verifier.

Totals (`out/summary_all.txt`):

| | pushes | LP iterations | best count reached (number of pushes) |
|---|---|---|---|
| n = 3 | 311 (21 from the equilateral triangle or near it, 30 from count-4 end points, 260 random) | 46,063 | 4: 197, 2: 114 |
| n = 4 | 130 (10 from perturbed C_4, 20 from count-9 or count-7 end points, 100 random) | 16,495 | 9: 17, 7: 23, 5: 56, 3: 34 |

Plus 3,000 random n = 3 configurations (counts 2: 2,994, 4: 1) and 500 random n = 4 configurations (3: 499, 5: 1), tracked with all complex solutions.

[F] The engine does climb: one random n = 4 start went from 3 to 9 (`push_n4_rand.json` start 14), and a perturbed C_4 start went 5 -> 7 -> 9. For n = 3, 197 of 311 pushes reached 4 and none went further.

### 4.1 n = 3: what stops the push

- [F] At every count-4 end point of stage 1 (155 pushes), the nearest non-real pair to the physical region has exactly one negative Re t_i. It sits in a mixed-sign orthant: if it turned real it would be an equilibrium of two positive charges and one negative charge, not a new physical equilibrium.
- [F] Over 344 count-4 configurations visited by the pushes (`out/orthant_n3.log`), 333 have no non-real pair with all Re t_i > 0 at all. The other 11 have one such pair, and it is farther than the three nearest pairs (its T is above 2.4).
- [F] Distance reached. The smallest T of any non-real pair at count 4, over all pushes and trajectories, was 0.30 (stage 2, random starts) and 0.51 (stage 2 from count-4 points). In stage 1 the final nearest T was 1.02 to 1.97. For comparison, the pair that turns 2 into 4 is routinely pushed to T = 0 (a fold), and stage-1 count-2 end points had nearest T down to 0.067 with all Re t_i > 0.
- [F] Stops: LP trust region collapses (stage 1: 131 of 220. The rest hit the iteration cap). Parameters stayed inside the box (one push of 220 touched b = 0.02, a flat triangle). Charges stayed between e^-12 and e^12.
- [F] Real structure in the plane at every n = 3 configuration sampled: 2 or 4 physical equilibria and exactly 2 in each mixed class, which is the Poincare-Hopf minimum.

[I] Reading. For three charges the complex solutions that could supply a fifth and sixth physical equilibrium live, near the count-4 region, in the orthants that belong to a negative charge. The push can bring them toward the real plane, but they land as mixed-sign equilibria. This is consistent with Maxwell's bound 4 and with the proved bound 6 (GNNS). It is evidence, not proof.

### 4.2 n = 4: what stops the push

- [F] Two families reached 9. (a) Triangle plus a small charge near its centre (the repository's C_4 design, charge ratio about e^-7.5 to e^-8.3, the small charge slightly off the plane).
  (b) A genuinely three-dimensional configuration found from a random start: theta = (0.3727, 0.8209, 0.1982, 0.3166, 1.6152, 0.6414, 0.1853, 2.1157), i.e. sites (0,0,0), (1,0,0), (0.373, 0.821, 0), (0.198, 0.317, 1.615) and charges 1, 1.90, 1.20, 8.30, with all nine equilibria inside a ball of radius about 0.05 around (0.40, 0.28, 0.28). Family (b) is numerical and not certified.
  It may be new as a 9-configuration of a different design, but I did not search for it in the literature.
- [F] Both families are thin: perturbing (b) by 0.003 in positions or (a) by 0.03 drops the count to 3, 5 or 7 (`push2_n4_c.log`, `push_n4_centre.log`).
- [F] At count 9 there remain 1 or 2 non-real pairs with all Re t_i > 0 (26 configurations, `out/orthant_n4.log`), and one of them is close: T = 8.2e-3 in family (a) (near the small charge, t_4 about 26) and T = 2.3e-4 in family (b). So for n = 4, unlike n = 3, a positive-orthant pair does come close.
- [F] But it cannot be brought in without losing two others. `diag.py` follows -grad T without constraints. Family (a): two of the nine physical equilibria are 1e-4 apart, and a step of 1e-4 merges them (count 9 -> 7) while the target T barely changes (0.00824 -> 0.00822). Family (b): a step of 1e-4 makes the target pair real, but the count goes 9 -> 7, so two other pairs annihilated in the same step.
  The LP push, which forbids those collisions, stalls there. In family (a) it lowered T from about 0.045 to 0.0082 in 28 accepted steps and then every further LP step was rejected. Two runs with different random arcs ended at the same point. Over the stage-2 runs from six count-9 points (1,500 LP iterations) no count above 9 appeared.
- [F] Stops in stage 1: trust-region collapse or iteration cap. No parameter at the box boundary in any of the 50 stage-1 pushes.

[I] Reading. Near the best configurations the ninth, tenth and eleventh real equilibria sit in fold-wall trades: the nearest physical candidate pair can only cross into the real region where another physical pair leaves. In family (a) this matches the repository's local model ("at most 4 near one small charge, or 6 for an axially symmetric background", point-charges NOTE.md section 3).
In family (b) all nine equilibria cluster near one point, which suggests an organizing degenerate critical point. Either way the evidence agrees with Maxwell's bound 9 for four charges. It is evidence, not proof.

### 4.3 Counts of positive-orthant pairs (numerical, descriptive)

For each configuration let k be the number of non-real conjugate pairs with all Re t_i > 0 (one representative per pair and its global flip).

| n | physical count : observed k |
|---|---|
| 3 | 2 : 1 or 2 , 4 : 0 (333 of 344) or 1 |
| 4 | 3 : 4 to 11 , 5 : 3 to 9 , 7 : 2 to 5 , 9 : 1 or 2 |

[I] In all these data, physical + 2k is at least 4 (n = 3) and at least 11 (n = 4). I do not know whether this means anything. Re t_i > 0 is not preserved along complex paths, so k is not a count with an obvious algebraic meaning.

## 5. What is not verified

- The complex counts 68 and 420 are numerical (two independent homotopy methods agree). No proof.
- All physical counts in this thread come from floating-point tracking with a fixed tolerance (|Im| below 1e-9 relative). They were cross-checked against the repository only at C_3 (4) and C_4 (9). The family (b) 9-configuration is not certified.
- The "fold trade" explanation rests on two diagnosed configurations plus the failure of 1,500 constrained LP steps. It is not a theorem.
- I read only the abstracts of GNS 2007, GNNS 2026 and Enciso and Peralta-Salas 2026.
- The rigid-realizations engine was re-implemented, not reused. A bug in my code could hide a better configuration. The engine did reproduce 4 and 9 and climbed to them from random starts.

## 6. Next concrete steps

1. Prove the generic counts 68 and 420 (exact Groebner basis at a random rational parameter point, or certified homotopy). For n = 4 this would give at most 210 equilibria for four charges of any signs, against 570 from Enciso and Peralta-Salas, if their bound counts the same objects (check their paper).
2. Certify the family (b) nine-equilibrium configuration with `verify_arb.py` after rounding to rationals, and look for its organizing centre: a configuration with a critical point where the Hessian of V vanishes (3 + 5 conditions on 8 parameters plus the point). The unfolding of that cubic germ bounds what can cluster there.
3. For n = 3, turn the orthant observation into a statement: show that at a configuration with 4 equilibria no complex equilibrium has all Re t_i > 0, or find the 11 exceptions' structure.

## 7. Files and rerun commands

All in this directory. Python `S/work/pc-venv/bin/python`. `run_all.sh` lists every run in order (about 1 hour on 2 cores).

- `cross_lib.py`: system, Jacobian, parameter derivatives, batched adaptive tracker.
- `monodromy.py n D seed [stall]`: monodromy count. Logs: `out/mono_n3.log`, `out/mono_n4_s1.log`.
- `tdh.py file.npz [chunk]`: total-degree homotopy check. Logs: `out/tdh_n3.log`, `out/tdh_n4.log`.
- `sample.py`: random real configurations. Output `out/sample_n3.json`, `out/sample_n4.json`, summaries `out/summary_sample_n3.txt`, `out/summary_sample_n4.txt`.
- `push.py`: stage-1 LP push. Output `out/push_n3_tri.json`, `out/push_n3_rand.json`, `out/push_n4_centre.json`, `out/push_n4_rand.json`, logs `out/push_n3.log`, `out/push_n4.log`, summaries `out/summary_push_n3.txt`, `out/summary_push_n4.txt`.
- `push2.py`: stage-2 push with tracked target and kicks. Start files `out/starts_*.json` (written by short inline snippets from stage-1 output. They are saved, so reruns use them directly). Output `out/push2_*.json`, logs `out/push2_*.log`.
- `orthant.py`: positive-orthant pair counts. `out/orthant_n3.log`, `out/orthant_n4.log` and the matching json. Inputs `out/thetas_n3_all.json`, `out/thetas_n4_all.json`.
- `diag.py`: unconstrained line search at a stalled point. `out/diag_n4b2.txt`, `out/diag_n4c0.txt`.
- `summarize.py` -> `out/summary_all.txt`.
- `sources/literature.txt`: abstracts consulted.

Resumable state: every push writes its json after each start. `out/mono_*.npz` hold the base complex solutions that every other script starts from.

## Timing

The final hand-back gave the stop time as about 02:05, roughly 70 minutes into the two-hour budget.

## Where the named files are in the repository

Paths are relative to `org/review/2026-11/science/threads/`. Names that are not listed were not copied. `checks/STATE-NOTES.md` says why.

| Name in this report | Repository path |
|---|---|
| `cross_lib.py` | `checks/cross/cross_lib.py` |
| `diag.py` | `checks/cross/diag.py` |
| `monodromy.py` | `checks/cross/monodromy.py` |
| `orthant.py` | `checks/cross/orthant.py` |
| `out/diag_n4b2.txt` | `checks/cross/state/out/diag_n4b2.txt` |
| `out/diag_n4c0.txt` | `checks/cross/state/out/diag_n4c0.txt` |
| `out/mono_*.npz` | 7 files in `checks/cross/state/out/` |
| `out/mono_n3.log` | `checks/cross/state/out/mono_n3.log` |
| `out/mono_n4_s1.log` | `checks/cross/state/out/mono_n4_s1.log` |
| `out/orthant_n3.log` | `checks/cross/state/out/orthant_n3.log` |
| `out/orthant_n4.log` | `checks/cross/state/out/orthant_n4.log` |
| `out/push2_*.json` | `checks/cross/state/out/push2_n3_four.json`, `checks/cross/state/out/push2_n3_rand2.json`, `checks/cross/state/out/push2_n4_a.json`, `checks/cross/state/out/push2_n4_b.json`, `checks/cross/state/out/push2_n4_c.json`, `checks/cross/state/out/push2_n4_rand2.json` |
| `out/push2_*.log` | `checks/cross/state/out/push2_n3.log`, `checks/cross/state/out/push2_n3_rand2.log`, `checks/cross/state/out/push2_n4_a.log`, `checks/cross/state/out/push2_n4_b.log`, `checks/cross/state/out/push2_n4_c.log`, `checks/cross/state/out/push2_n4_rand2.log` |
| `out/push_n3.log` | `checks/cross/state/out/push_n3.log` |
| `out/push_n3_rand.json` | `checks/cross/state/out/push_n3_rand.json` |
| `out/push_n3_tri.json` | `checks/cross/state/out/push_n3_tri.json` |
| `out/push_n4.log` | `checks/cross/state/out/push_n4.log` |
| `out/push_n4_centre.json` | `checks/cross/state/out/push_n4_centre.json` |
| `out/push_n4_rand.json` | `checks/cross/state/out/push_n4_rand.json` |
| `out/sample_n3.json` | `checks/cross/state/out/sample_n3.json` |
| `out/sample_n4.json` | `checks/cross/state/out/sample_n4.json` |
| `out/starts_*.json` | `checks/cross/state/out/starts_n3_four.json`, `checks/cross/state/out/starts_n3_rand2.json`, `checks/cross/state/out/starts_n4_a.json`, `checks/cross/state/out/starts_n4_b.json`, `checks/cross/state/out/starts_n4_c.json`, `checks/cross/state/out/starts_n4_rand2.json` |
| `out/summary_all.txt` | `checks/cross/out/summary_all.txt` |
| `out/summary_push_n3.txt` | `checks/cross/state/out/summary_push_n3.txt` |
| `out/summary_push_n4.txt` | `checks/cross/state/out/summary_push_n4.txt` |
| `out/summary_sample_n3.txt` | `checks/cross/state/out/summary_sample_n3.txt` |
| `out/summary_sample_n4.txt` | `checks/cross/state/out/summary_sample_n4.txt` |
| `out/tdh_n3.log` | `checks/cross/state/out/tdh_n3.log` |
| `out/tdh_n4.log` | `checks/cross/state/out/tdh_n4.log` |
| `out/thetas_n3_all.json` | `checks/cross/state/out/thetas_n3_all.json` |
| `out/thetas_n4_all.json` | `checks/cross/state/out/thetas_n4_all.json` |
| `push.py` | `checks/cross/push.py` |
| `push2.py` | `checks/cross/push2.py` |
| `push2_n4_c.log` | `checks/cross/state/out/push2_n4_c.log` |
| `push_n4_centre.json` | `checks/cross/state/out/push_n4_centre.json` |
| `push_n4_rand.json` | `checks/cross/state/out/push_n4_rand.json` |
| `run_all.sh` | `checks/cross/state/run_all.sh` |
| `sample.py` | `checks/cross/sample.py` |
| `summarize.py` | `checks/cross/summarize.py` |
| `tdh.py` | `checks/cross/tdh.py` |
