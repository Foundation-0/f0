# Lattice elasticity and the fold: full report

15 November 2026. Repository head pinned by the report: commit 2d374ff of the lattice repository.

Short note for this thread: `../incentre-lattices.md`.

S is the working folder of this thread. It is archived outside the repository. Paths that start with S/ point into it. Where a file was copied into the repository, its repository path is listed at the end.

---

**Result.** The elastic theorem is correct. My own exact code, which shares nothing with the repository, gives C11/C12 = (n-1)^2, C44 = 0 and nu_100 = 1/(n^2-n-1) for every n from 2 to 9, with no mismatch [F]. The written proof is complete apart from two unstated assumptions: no pre-stress, and the standard definition of relaxed elastic constants. There is one wording error.
"Every shear modulus is 0" is true only for n = 2 [F]:
- C44 is 0 for all n.
- C' = (C11-C12)/2 = 2(n-2)/(n 2^n) is positive for n ≥ 3 (1/12 at n = 3). So for n ≥ 3 the lattice resists tetragonal shear.

The cab-to-fcc motion is proved on my reading. A separate exact check of my own confirms it [F].

**The brief does not match this commit.** At 2d374ff there is no THEOREM.md, no research/connectors_proof.md and no research/status.md [F]. Neither rod threshold appears either. The 3,248-quartic certificate is in results/fold-continuous-fcc/, not in autoresearch-fold/.

My scripts and their outputs are in S/threads/incentre/.

**Definition.** The joints are ±c e_i in each cell of 2Z^n, with c = 2-√2. Bars join touching balls: the edges of each cross-polytope plus one bridge per axis. Each bar is a unit central spring with no angular stiffness. Constants are in Voigt notation, after the joints relax.
- n = 2 is the 4.8.8 truncated square tiling.
- n = 3 is the cab net (the CaB6 boron net).
- It is not kagome, pyrochlore, A_n* or D_n.

**Proof, step by step.** Lemma 1, equation (*), the block split, parts (a) and (b), and the minimisation in (c) all follow. I re-derived each step.

**First principles.** There is no contradiction with the Cauchy relation C12 = C44.
- Before relaxation the constants satisfy C12 = C44 exactly in every n [F].
- The crystal is centrosymmetric, but no joint is a centre of inversion. So the joints relax: rotations of each cross-polytope remove C44, and C12 drops (n = 3: from 0.0858 to 1/18).
- The relaxed tensor has rank n: 3 easy modes in 3D (Milton and Cherkaev's "trimode", not pentamode), and only bulk stiffness in 2D.
- Coordination is 2n-1, one below the isostatic 2n. At q = 0 there are n(n+1)/2 zero modes and n(n-1)/2 self-stresses (n = 2..9) [F].

**Independent computation (elastic_indep.py).** It finds the bars by a distance search and computes in exact Q(√2) arithmetic.
- n = 3..9 gives C11/C12 = 4, 9, 16, 25, 36, 49, 64 and nu = 1/5, 1/11, 1/19, 1/29, 1/41, 1/55, 1/71.
- The relaxed constants are the same at t = 3/10, 1/3 and 3/4.
- A 1% corrupted target exits 1 under `python -O`.
- The repo's own verifier also passes (reproduction only).

**Novelty.** No earlier report found of C11/C12 = (n-1)^2 or nu_100 = 1/(n^2-n-1). The closest source is Borcea and Streinu 2021, Section 7 (open PDF read). It describes the same bar graph in any dimension but gives no spring constants. The derivation is short, so a specialist may call it a worked example. I did not read the full texts of Goodwin 2006 or Milton's book.

**The fold.**
- The motif is fixed and the lattice moves: L(s) = dI + tC. Each bridge keeps length √2 and swings 90° from its axis to an octahedron-edge direction.
- All 15 bars and the shape of each octahedron are kept, and no balls overlap.
- The end state is fcc: determinant 12, six cosets of D3, 12 contacts per ball. Density rises strictly.
- What the quartics certify: for 3,248 pairs of a lattice translation and a motif difference, the squared distance minus 2 has nonnegative Bernstein coefficients over the whole parameter interval, so no two balls overlap. A written bound covers translations farther away.
- Reproduction: both repo verifiers pass and the certificate regenerates identical. The sampled-path checker accepts the 501-sample curve and the stored 793-state hcp path.
- Independent check (fold_indep.py):
  - It covers 6,516 pairs (a larger box of translations), with no subdivision needed.
  - It bounds the far translations by a different argument: L·L^T − I is positive semidefinite, certified by its principal minors.
  - It proves exactly that the density increases strictly.
  - Flipping the sign of C keeps every bar but overlaps, and exits 1.
- Comparison: the Bain path and layer slides move bare packings with no bonds. ReO3 reaches hcp by tilting corner-sharing octahedra. Teshima and Matsumoto 2012 deform bare sphere packings from simple cubic to fcc (title only read). Borcea and Streinu sketch a fold of the same graph with bars twice the edge and no packing.
- New, as far as found: an explicit, rational, one-parameter motion of the equal-bar framework that keeps every bar and avoids overlap from the open cubic state to fcc, with an exact certificate over the whole interval.

**For a human.** Check first that the relaxation step in (c) is the right definition of the constants, then fix the wording to "C44 = 0, C' > 0".

How to state it: "For the bridged cross-polytope lattice in R^n with unit springs and no pre-stress, C44 = 0, C11/C12 = (n-1)^2 and nu_100 = 1/(n^2-n-1), whatever the ratio of bridge to edge."

**Not verified.** Generic-q mode counts. my code stops at n ≤ 9. The full papers listed above. The 793- and 1,193-state paths are sampled, not proved continuous.

**Files** (all in S/threads/incentre/):
- elastic_indep.py
- fold_indep.py
- out_c.txt, out_t1_3.txt, out_t3_10.txt, out_t3_4.txt, out_corrupt.txt
- out_fold.txt, out_fold_corrupt.txt
- repro/*.log
- sources/bs2021_wb.pdf and .txt (Borcea and Streinu, cached)
- sources/crossref_S1087659612010154.txt (Teshima and Matsumoto metadata)

Rerun: `$P -I elastic_indep.py --nmax 9` (about 5 minutes) and `$P -I fold_indep.py` (about 2 seconds), with $P = S/work/pc-venv/bin/python.

## Where the named files are in the repository

Paths are relative to `org/review/2026-11/science/threads/`. Names that are not listed were not copied. `checks/STATE-NOTES.md` says why.

| Name in this report | Repository path |
|---|---|
| `elastic_indep.py` | `checks/incentre/elastic_indep.py` |
| `fold_indep.py` | `checks/incentre/fold_indep.py` |
| `out_c.txt` | `checks/incentre/out_c.txt` |
| `out_corrupt.txt` | `checks/incentre/out_corrupt.txt` |
| `out_fold.txt` | `checks/incentre/out_fold.txt` |
| `out_fold_corrupt.txt` | `checks/incentre/out_fold_corrupt.txt` |
| `out_t1_3.txt` | `checks/incentre/state/out_t1_3.txt` |
| `out_t3_10.txt` | `checks/incentre/state/out_t3_10.txt` |
| `out_t3_4.txt` | `checks/incentre/state/out_t3_4.txt` |
| `repro/*.log` | `checks/incentre/state/repro/autoresearch_verify_best.log`, `checks/incentre/state/repro/autoresearch_verify_continuous.log`, `checks/incentre/state/repro/fold_continuous_independent.log`, `checks/incentre/state/repro/fold_continuous_verify.log`, `checks/incentre/state/repro/rigidity_verify.log` |
