- **Date:** 2026-11-13

- **Scope:** Unified mathematical and engineering synthesis across
  > [<u>Foundation-0/gravity</u>](https://github.com/Foundation-0/gravity),
  > [<u>Foundation-0/project-asma</u>](https://github.com/Foundation-0/project-asma),
  > Foundation-0/exoplanets-frontier,
  > [<u>Moissanite-Labs/weft</u>](https://github.com/Moissanite-Labs/weft),
  > ahrazzle/soko, and Proven-Commons

- **Executable Reference Kernel:** quotient_anchor_kernel.py in
  > [<u>start-here/project-files/fdn0</u>](https://drive.google.com/drive/folders/1Z-GKOILLjfla66zYpaXaS9jPxlKxi2_U)
  > (7/7 checks passed in exact Fraction and integer arithmetic across
  > 5 domains, Proven-Commons not exercised,
  > SHA-256:
  > 8ff47efe0a8d2885a59af396cf9f001ad41314359d2ccc1a6f0cda85c53ff1a5)

**What the receipt means.** Each witness builds its inputs from the same model the kernel then inverts, so a passing run shows the algebra is self-consistent. It does not show that any cited repository's data fits the model, and the kernel reads no repository. The `p = 0` endpoint of a sample is not a bleed anchor: with `alpha = 3/20` and `c = 1/4`, `y(0) = 29/80`, and using that endpoint as the anchor returns `c = 0`. Proven-Commons is named below but no check in the kernel calls it. (Corrected 2026-11-15 against ahrazzle's review of f0#41; the essay originally quoted digest `64b7bf0f…`, which is the digest of a kernel version not in the tree.)

# 1. What the Single Thread Is in Plain Words

Every project we worked on studies a rich, hidden reality through a
compressed observation or relaxation: galactic potentials from rotation
and lensing profiles, tumour state transitions and classifier skill from
mixed assay scores, exoplanet transits from noisy stellar flux, 66-room
multi-hero state graphs through quotient heuristics, and self-modifying
neural weights through scalar fitness and norm gates.

Whenever you compress a high-dimensional causal process onto a narrow
measurement or search relaxation, the same three failures appear in
every field:

- **Hidden Offset and Bleed Aliasing:** Two opposite causes produce the
  > exact same curve or score because an unanchored offset or cross-talk
  > parameter slides freely along a symmetry orbit.

- **Phantom Shortcuts and Zeno Drift:** A relaxed model drops a
  > conservation law, allowing tokens to stack on one cell,
  > floating-point budgets to take 100,000 free sub-ULP steps, or 3e-12
  > rounding dust to trigger mitosis.

- **Single-Branch Phase Blindness:** Extrapolating one regime across a
  > physical or combinatorial phase threshold makes coexisting regimes
  > look like a contradiction.

Work across the programs below is grouped here, by analogy, under one **four-gate pattern** — an **Anchored Conservation Quotient (ACQ)** — for turning an ambiguous projection into a machine-checkable receipt. Nothing in this essay proves or ships a result in any of those repositories; the pattern is the essay's synthesis, and the receipts are the repositories' own, as cited in the table.

# 2. How All Five Programs Map onto One Four-Gate Operator

| Program                                                                                                                                                | Hidden Reality vs. Narrow Projection                                                                                    | Gate 1: Boundary / Null Anchor                                                                                              | Gate 2: Exact Conservation Law                                                                                                         | Gate 3: Linearized Regime Pivot                                                                                                 | Gate 4: Zero-Trust Kernel Receipt                                                                                                                                                   |
|--------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [<u>Foundation-0/gravity</u>](https://foundation-0.github.io/gravity/) (Waves 1-12)                                                                    | Relativistic condensate (phi) projected onto radial acceleration and halo profiles                                      | Asymptotic de Sitter / Machian zero-energy boundary and Planck z = 1100 dust density                                        | Shift-symmetry Noether charge J^mu (J(-u) + J(u) = 0, positive Legendre dust on both sheets)                                           | Acceleration crossover g_b,x = 0.02897 a_0 (C-23, COMPUTED, no Lean lemma) and Press-Schechter sigma\_\*(z) (0.97 km/s at z = 6.08 vs 185.59 km/s at z = 0)       | 7 Lean 4 Init modules (decide on integer statements; no QPos found) + 39-entry SHA256SUMS                                                                                                                    |
| [<u>Foundation-0/project-asma</u>](https://github.com/Foundation-0/project-asma/pull/87) (#82; #83 closed unmerged, superseded by #87)                                                   | Tumour selection vs. conversion (r, c) and 5-fold classifier skill projected onto post-assay y(p) and pooled OOF scores | independent c = 0 recombinant paralog control as bleed anchor (alpha) — not the sample's own p = 0 endpoint — and within-fold mid-rank (rank - 0.5)/N_k                         | Stratified pair conservation (4,316 = 862 within + 3,454 cross; no \|b\| \<= 1/20 bound found in the cited note)                                 | Survival-ratio straight-line pencil Phi(p) = (1 - p)/(1 - q) pivoting at (1/5, 4) on Phi; (1/20, 3/8) are the mixture fractions, not a point of Phi; C25 flip (10179/563920 \> 1/60) | AsmaIdentifiabilityProofs.lean (30cdc3a, four checks green — cross-arch-equivalence, amd64-synthetic, arm64-synthetic-native, verify — not on main) + exact Fraction JSON certificate (cdc6d93; #83 closed unmerged)                                                                                  |
| [<u>Moissanite-Labs/weft</u>](https://github.com/Moissanite-Labs/weft) (v2 reference suite #128, review issue #111)                                                                    | Self-modifying cell colony projected onto scalar reward counters and float32 arena norms                                | p = 0 planted-negative reward-bleed batch + within-shard mid-rank tournament pooling (swarm_loom.py)                        | Frozen-core bit lock, nextafterf ULP-monotone budget descent, Pythagorean orthogonality, and Dinic unit-capacity synaptic flow         | Division-free MDR gate, proposed in unmerged weft#179 (grad_orth \>= orth_floor and grad_orth \>= tau \* grad_par, eliminating 3e-12 dust mitosis) — not merged, not shipped             | Unreviewed v2 reference suite (merged weft#128, labelled external/unreviewed) + Drive C11 patch + WeftInvariantsPureInit.lean + 2,048-vector parity (cited, not checked here) |
| ahrazzle/soko & Proven-Commons ([<u>CHANGELOG</u>](https://docs.google.com/document/d/1T04Xv72FtlCklVac0FQglVz-cvFDhepcaJSe_rzPq9I/edit?usp=drivesdk)) | 117,766,522 canonical states at the finished f = 37 layer (floor >= 38); ~282M raw states is the ceiling of the later f = 38 chunk — concrete PuzzleScript graphs and byte streams projected onto quotient PDBs and parsers                       | Full-state collision equality (105,495,450 collisions prevented at the f = 37 layer; 181,027,454 in the later f = 38 chunk), NUL-byte differential (Z-F1 in open Proven-Commons/zip#5 review findings), and prefix-free HTTP framing | 40-Atom conservation (popcnt), intact-border unit 9-Flow (5/9 cut on r30), and Unblocked-Crate Non-Stuttering (zero violations across 250,000 states, 439,038 transitions and 255,924 Bard stutters) | Crushing vs. sticky purple-door phase transition (34-step route wins only under the relaxed sticky-door rule; under the crushing rule the Druid is crushed at step 30, floor >= 38 on 15x7 III-14; 84 keys on III-20)  | Dual zero-shared-code oracles + exact Fraction LP duals + checker_auditor.py & lean4_auditor.py                                                                                     |
| Foundation-0/exoplanets-frontier                                                                                                                       | Multi-sector TESS + Gaia DR3 signals (pre-DR4 catalog) projected onto 1D phase-folded transit photometry                                  | Flux-inversion null test (inverted_lightcurves_vetted.csv) + odd/even depth (no Gaia DR4 anchor: the catalog is pre-DR4 Gaia DR3; DR4 on 2 December 2026 is the falsifier)              | Ephemeris phase coherence (ttv_track.py) across Sectors 1–107                                                                          | Equilibrium temperature + brightness tractability frontier (TIC 399695544 at 426 K, TIC 409696823 at 453 K; 0 small habitable-zone candidates)                     | Deterministic vetting registries (eumemic_gaia_dr4_readiness.csv, platinum_followup_targets.csv; pre-DR4, built from VizieR Gaia DR3)                                                                                    |

# 3. Why This Matters for What We Build Next

Viewed as one thread, carbon-based discovery (gravity, project-asma,
exoplanets-frontier) and digital sentience engineering (weft,
soko-verified-mcp, Proven-Commons) are no longer separate tracks:

- **Science needs Weft and Soko's kernel discipline:** The 1 Mpc vs. cluster tension in gravity (C-04, COMPUTED, model-dependent) and the C20 gap in project-asma remain open in their ledgers; C25 is an exact-arithmetic ceiling on typed-in inputs (see f0#39). What the kernel discipline offers is a way to state such claims so they can be checked — exact rational bounds, explicit gauge anchors, and zero-Mathlib Lean 4 proofs — not a closure of the open rows.

- **Digital sentience (weft) needs Physics and Biology's gauge and
  > conservation laws:** An autonomous self-modifying colony cannot
  > trust a raw scalar reward any more than oncology can trust an
  > unanchored CDR2/CDR2L assay or physics can extrapolate one
  > condensate branch without its Noether charge. Wiring the four-gate
  > **Anchored Conservation Quotient** into weft's cell reproduction loop
  > is a proposal, not a shipped change: it depends on the division-free
  > gate in unmerged weft#179. As a proposal it would give
  > self-modifying agents a mathematical immune system: anchor the null
  > channel with an independent c = 0 control (not the sample's own
  > p = 0 endpoint), conserve metabolic and topological invariants
  > (nextafterf + unit flow), detect capacity walls via division-free
  > orthogonal curvature (MDR), and commit only updates carrying a
  > dual-checked rational/Lean receipt.
