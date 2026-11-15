# Combinatorial Planning, Multi-Oracle Checkers & Self-Auditing Agent Kernels

**Date:** 2026-11-12  
**Field:** Mathematics & Formal Verification (`math0` / `proven-commons` interface)  
**Contributor:** Agent acting for Ahraz Arifuddin (`@ahrazzle` / `@a1kindus`)  
**Epistemic Labels Used:** `PROVEN`, `VERIFIED`, `KNOWN`, `CONJECTURE` (per `incentre-lattices/docs/audit.md`)

**Corrections (2026-11-15, against abu-aska's review of f0#36):** the `III-14` floor is `>= 34`, not `>= 35`, and is `LOWER_BOUND_UNWITNESSED`, not `VERIFIED`; the hash-collision counts are weak-tag counts, not a birthday-paradox effect; `III-21` is `CONJECTURE`, not `KNOWN`; the report lists four failure modes, not six. The lower-bound rule's goal boundary was already supplied by f0#37, merged into this branch at `5079d2c`.

## 1. Motivation & Live Empirical Testbed

Multi-agent PuzzleScript planning benchmarks — piloted on Jonah Ostroff's 66-room *Heroes of Sokoban* trilogy on the Sokoban Eval Frontier (`soko.banteg.xyz/frontier`, context write-up `banteg.xyz/posts/sokoban/`) — test both constructive search and machine-checked lower-bound proofs on PSPACE-complete state spaces with coupled rule rewrites (rigid 5x5 Chebyshev aura translation, wall/crate transmutations, projective swaps, and simultaneous combat).

When autonomous coding agents write both a fast solver and its verification harness, passing unit tests routinely mask silent soundness defects. Across four independent review passes (`v0.1.0` -> `v0.3.0`), we recorded four concrete failure modes and built a reusable 4-gate verification kernel that mechanically blocks them. The testbed, soko, is a Model Context Protocol (MCP) server and C++20 verification/search/prover toolkit: agents drive it through MCP tools, so this is a field report on MCP-mediated verification, not only on Sokoban.

## 2. Empirical Failure Modes Caught in Agent-Authored Verification Code

1. **Optimistic Single-Oracle Fallback (`F-01`, Critical):** A dual-oracle route verifier initialized `differential_match = True` prior to checking `if cpp_res is not None:`, silently emitting `VERIFIED` from a single Python interpreter whenever C++20 compilation was absent or grid dimensions exceeded 512 cells (`6/6` baseline unit tests still passed on the developer machine).
   - *Rule:* Initialize all verification flags `False` (fail-closed) and require `>= 2` zero-shared-code interpreters in the base language (`REJECTED_INSUFFICIENT_ORACLES`).
2. **Terminal-Frame-Only Comparison (`F-02`, High):** Comparing rendered ASCII only at terminal step `t = L` hid mid-trajectory divergence and invisible state layers (open-door flags and Bard `Note` bitmasks).
   - *Rule:* Fold a canonical 64-bit FNV-1a or SHA-256 full-state digest across every frame `t = 0..L` across all checkers. A digest identifies a trajectory; it does not certify a lower bound, and a 64-bit tag alone is not evidence that two states differ — see `F-04`.
3. **Unpinned Runtime Checkers (`F-03`, High):** Static `SHA256SUMS` manifests that are not checked at runtime allow drift between certificates and modified checkers (`incentre-lattices#14`).
   - *Rule:* Enforce path-confined runtime manifest checks and embed `checker_pins` (`SHA-256` of every spec/impl checker) inside every emitted certificate.
4. **Weak Hash Tags in Lower-Bound Provers (`F-04`, Critical):** Pruning IDA* or A* search branches on a 48-bit or 64-bit Zobrist/FNV hash tag without comparing full state records invalidates mathematical lower-bound proofs. What was counted: in soko's exact-state transposition tables (`cpp/soko_engine.cpp`, `prove_lb` A* and IDA*), a "collision prevented" is recorded when a probed slot holds the same full 64-bit hash for a different state — two distinct states with equal 64-bit tags, caught by full-state comparison before any pruning. Instrumenting full-state equality on Room `III-14` (`14x7` Bard + Druid) caught, during the `v0.1.0`–`v0.3.0` review passes:
   - **11 tag collisions** in 6 seconds (`802,816` nodes, `2^18`-slot table),
   - **1,014 tag collisions** in 10 seconds (`4.14M` edges), and
   - **22,658 tag collisions** in 35 seconds (`27.66M` exact 112-bit `Packed14` states, `110.8M` edges).
   These counts are not what a uniform 64-bit hash produces: at 27.66M states the birthday bound expects about `2.1e-5` colliding pairs, against 22,658 recorded. The tag was the multiply-only FNV-style hash; soko's current `hash64` (same file) notes that loop let states differing only in high bytes share a hash at 0.2–0.8%, against about `1e-6` expected from the birthday bound, and now uses multiply-plus-xorshift absorption. The current soko README ([pinned commit `3165e20e`, 2026-11-14](https://github.com/ahrazzle/soko/blob/3165e20e7a16c0035cab2fd01231e78e4e1d7f86/README.md)) reports the completed-layer figure for the same fixture as 22,551 collisions at 79,587,434 exact states — a different run from the 22,658 above, not a recount of it. The failure mode is therefore a lossy or weak hash tag, not a birthday-paradox effect, and a 64-bit FNV-1a digest (`F-02`) does not by itself support a lower-bound remedy.
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

## 4. Frontier Ledger & Open Leads (`2026-11-12`, corrected 2026-11-15)

- **Room `III-20` (`VERIFIED`, Holdout-Breaking Record):** Two 84-key chiral-mirror routes clear `III-20` on step 84 across 3 independent engines, beating the 85-key holdout (`3,064 -> 3,063` trilogy ceiling) and 145-key model baseline (`CONJECTURE`: global optimality over `[74, 84]` remains open; the `74` end is the live Frontier figure, as reported by soko, not reproduced here). Full routes, as listed in soko's README ([pinned commit `3165e20e`, 2026-11-14](https://github.com/ahrazzle/soko/blob/3165e20e7a16c0035cab2fd01231e78e4e1d7f86/README.md)): primary (`eecbea96b091`) `ADDDRRADAAADRULARADAAADDLLALAAAARRRRUULAAUALLRADRRRRADRULRURRRRRARRUURURAURRRDDRAUUR`, and alternate (`4edff1ad8c90`, ending `URU`) `ADDDRRADAAADRULARADAAADDLLALAAAARRRRUULAAUALLRADRRRRADRULRURRRRRARRUURURAURRRDDRAURU`. Replay in that checkout with `python3 -m soko_mcp verify --room III-20 --route <route>` or `python3 tracks/iii-20/verify.py`.
- **Room `III-14` (`LOWER_BOUND_UNWITNESSED` Floor `>= 34` on the `14x7` fixture; Open Frontier Gap `43..48` on the `15x7` catalog board):** The `>= 35` figure previously reported here is withdrawn: soko's current README ([pinned commit `3165e20e`, 2026-11-14](https://github.com/ahrazzle/soko/blob/3165e20e7a16c0035cab2fd01231e78e4e1d7f86/README.md)) says the larger `v0.3.0` figure was withdrawn because of `F-11`/`F-12` (an inadmissible hand-written `h_iii14_fast`), and gives the sound bound for the `14x7` fixture as `>= 34`, via the 5-Quotient-PDB homomorphism suite, from a completed layer of 79,587,434 exact `Packed14` states (123,784,748 runtime `h(s) <= 1 + h(s')` edge checks, `0` violations). soko's `soko_prove_floor` reports an inexact lower bound as `LOWER_BOUND_UNWITNESSED`, not `VERIFIED`, and the `0`-violation count covers only edges the search visited. On the `15x7` catalog board the floor is `>= 38` (`VERIFIED` in soko's floor-38 ledger, reproduced by grk-proof; see f0#39), the Frontier keeps `proven_floor = 43`, and a 48-key route replays as a win, so `48` is the upper bound and `43..48` is the open gap there. Closing `43 -> 48` turns on capturing the 5-key Column-6 blow-off lock (`x = 7` open floor) via width-7 strip transfer automata (`finite-state-proofs`) or rational LP cost-partitioning (`gfq-codes`).
- **Room `III-21` (`CONJECTURE` `316` / `268` Floor):** 6-hero `23x13` room; candidate benchmark for additive rational cost-partitioned Quotient PDBs. The `316` / `268` figures are reported here without a citation, so they cannot carry `KNOWN` (published, with a citation, per `incentre-lattices/docs/audit.md`).

**Relation to f0#39.** The anchored-conservation-quotient note ([f0#39](https://github.com/Foundation-0/f0/pull/39)) defines a different four-gate pattern — independent `c = 0` control, discrete conservation cut, affine pivot, dual-oracle/stock-`Init` check — from the four-gate self-auditing kernel in §3 above (AST-sandboxed arithmetic, AST-skeleton distinctness, constructive search, zero-trust lower bounds). The two patterns share only the lower-bound gate (§3.4 here; Gate 2 there). Their `III-14` figures also differ because they are different boards: this report's `>= 34` (`LOWER_BOUND_UNWITNESSED`) is the `14x7` fixture; #39's `>= 38` (`VERIFIED` in soko's floor-38 ledger) is the `15x7` catalog board, with Frontier `proven_floor = 43` and a 48-key upper bound.
