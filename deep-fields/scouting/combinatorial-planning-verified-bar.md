# Combinatorial Planning, Multi-Oracle Checkers & Self-Auditing Agent Kernels

**Date:** 2026-11-12  
**Field:** Mathematics & Formal Verification (`math0` / `proven-commons` interface)  
**Contributor:** Agent acting for Ahraz Arifuddin (`@ahrazzle` / `@a1kindus`)  
**Epistemic Labels Used:** `PROVEN`, `VERIFIED`, `KNOWN`, `CONJECTURE` (per `incentre-lattices/docs/audit.md`)

## 1. Motivation & Live Empirical Testbed

Multi-agent PuzzleScript planning benchmarks — piloted on Jonah Ostroff's 66-room *Heroes of Sokoban* trilogy on the Sokoban Eval Frontier (`soko.banteg.xyz/frontier`, context write-up `banteg.xyz/posts/sokoban/`) — test both constructive search and machine-checked lower-bound proofs on PSPACE-complete state spaces with coupled rule rewrites (rigid 5x5 Chebyshev aura translation, wall/crate transmutations, projective swaps, and simultaneous combat).

When autonomous coding agents write both a fast solver and its verification harness, passing unit tests routinely mask silent soundness defects. Across four independent review passes (`v0.1.0` -> `v0.3.0`), we recorded six concrete failure modes and built a reusable 4-gate verification kernel that mechanically blocks them.

## 2. Empirical Failure Modes Caught in Agent-Authored Verification Code

1. **Optimistic Single-Oracle Fallback (`F-01`, Critical):** A dual-oracle route verifier initialized `differential_match = True` prior to checking `if cpp_res is not None:`, silently emitting `VERIFIED` from a single Python interpreter whenever C++20 compilation was absent or grid dimensions exceeded 512 cells (`6/6` baseline unit tests still passed on the developer machine).
   - *Rule:* Initialize all verification flags `False` (fail-closed) and require `>= 2` zero-shared-code interpreters in the base language (`REJECTED_INSUFFICIENT_ORACLES`).
2. **Terminal-Frame-Only Comparison (`F-02`, High):** Comparing rendered ASCII only at terminal step `t = L` hid mid-trajectory divergence and invisible state layers (open-door flags and Bard `Note` bitmasks).
   - *Rule:* Fold a canonical 64-bit FNV-1a or SHA-256 full-state digest across every frame `t = 0..L` across all checkers.
3. **Unpinned Runtime Checkers (`F-03`, High):** Static `SHA256SUMS` manifests that are not checked at runtime allow drift between certificates and modified checkers (`incentre-lattices#14`).
   - *Rule:* Enforce path-confined runtime manifest checks and embed `checker_pins` (`SHA-256` of every spec/impl checker) inside every emitted certificate.
4. **Birthday-Paradox Transposition Hash Collisions in Lower-Bound Provers (`F-04`, Critical):** Pruning IDA* or A* search branches on a 48-bit or 64-bit Zobrist/FNV hash tag without comparing full state records invalidates mathematical lower-bound proofs. Instrumenting full-state equality on Room `III-14` (`14x7` Bard + Druid) caught:
   - **11 live hash collisions** in 6 seconds (`802,816` nodes, `2^18`-slot table),
   - **1,014 live full-64-bit hash collisions** in 10 seconds (`4.14M` edges), and
   - **22,658 live full-64-bit hash collisions** in 35 seconds (`27.66M` exact 112-bit `Packed14` states, `110.8M` edges).
   - *Rule:* Lower-bound provers (`PROVEN` / `VERIFIED`) must store and compare exact states on every transposition hit (`0` lossy tag pruning).

## 3. Four-Gate Self-Auditing Kernel Pattern for Discrete Systems

To let agents formalize arbitrary discrete state machines (planning, protocol safety, combinatorial scheduling) without trusting LLM prose or hand-written heuristics:

1. **AST-Sandboxed Exact Arithmetic:** Reject imports, I/O, globals, dunder escapes, and IEEE-754 floats; expose `fractions.Fraction` so rational potentials and dual multipliers (`gfq-codes` pattern) evaluate bit-exactly.
2. **Alpha-Normalized AST Skeleton Distinctness (`H_alpha(SPEC) != H_alpha(IMPL)`):** Canonicalize local variable names in AST preorder and reject variable-renamed copy-paste duplicates (`REJECTED_IDENTICAL_AST_SKELETON`), paired with mandatory `must_fail_controls` and `100%` planted-mutation kills (`Proven-Commons` pattern).
3. **Constructive Search & Counterexample Extraction:** Exact Dijkstra/BFS (shortest goal witness or shortest safety-invariant violation), symmetry-reflected Tube Beam, and Sliding-Window LNS, replaying every candidate trace across all locked checkers.
4. **Zero-Trust Lower Bounds & Inductive Invariants:** Accept lower bounds only
   through machine-checked certificates with the following obligations.

   - **Quotient Graph Homomorphisms:** For `pi: S -> Q`, verify
     `w_Q(pi(s), pi(s')) <= c(s,a,s')` on every covered concrete transition.
     The abstract goal set must contain the image of every relevant concrete
     goal. Certify the abstract distance lower bound.
   - **Inductive Ranking Potentials:** Verify `h(s) <= c(s,a,s') + h(s')`
     on every covered edge and `h(g) <= 0` at every relevant goal `g`.
   - **Houdini Greatest-Fixpoint Invariants / Deadlock Traps:** Emit `PROVEN`
     only when concrete or syntactic state enumeration closes without truncation.

For a finite path `s_0 -> ... -> s_k = g`, summing the potential inequalities
gives `h(s_0) <= sum_i c(s_i,a_i,s_{i+1}) + h(g)`. The goal boundary therefore
makes `h(s_0)` a lower bound on every covered solution's cost. Edge inequalities
alone are insufficient: on one edge `start -> goal` of cost 1, the constant
potential `h = 35` satisfies `35 <= 1 + 35` but does not bound the optimal cost 1.
A certificate must identify its state model, transition costs, start and goals,
and justify coverage of every possible solution path from that start. A sampled
edge set or truncated enumeration does not suffice. For an unsolvable state,
there is no finite goal path to which this argument applies: a finite potential
does not itself prove unsolvability, which needs a separate closed invariant or
exhaustive no-goal argument. This completes the stated proof obligation. It does
not assess or refute any room record listed below.

## 4. Verified Frontier Ledger & Open Leads (`2026-11-12`)

- **Room `III-20` (`VERIFIED`, Holdout-Breaking Record):** Two 84-key chiral-mirror routes (`eecbea96b091` ending `...AUUR`, and `4edff1ad8c90` ending `...AURU`) clear `III-20` on step 84 across 3 independent engines, beating the 85-key holdout (`3,064 -> 3,063` trilogy ceiling) and 145-key model baseline (`CONJECTURE`: global optimality over `[74, 84]` remains open).
- **Room `III-14` (`VERIFIED` Floor `>= 35`; Open Frontier Gap `43..48`):** 39.7M-state 2-Atom Quotient Pattern Database + multi-core exact-state A* certifies `floor >= 35` in 35s (`0` step-consistency violations across `110.8M` edges). Closing `43 -> 48` turns on capturing the 5-key Column-6 blow-off lock (`x = 7` open floor) via width-7 strip transfer automata (`finite-state-proofs`) or rational LP cost-partitioning (`gfq-codes`).
- **Room `III-21` (`KNOWN` `316` / `268` Floor):** 6-hero `23x13` room; candidate benchmark for additive rational cost-partitioned Quotient PDBs.
