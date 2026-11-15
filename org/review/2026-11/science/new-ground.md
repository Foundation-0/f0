# New ground, promising advances, and threads worth pulling

Science pass, 15 November 2026. This ranks the work in the public repositories by how far it goes beyond the published record and how close it is to something others could use. It builds on `verdicts.csv`, `theories.md` and `ties.md`, which are on draft PRs 51, 52 and 53. Paths written `checks/...` and `notes/...` are in `org/review/2026-11/science/` on PR 51.

Marks: **[F]** a fact read from a repository, a run or a source, **[I]** an inference. Literature checks were web searches and page reads on 15 November. A search can miss prior work, so "no earlier report found" is not proof of priority.

| Tier | Meaning |
|---|---|
| **New ground** | Goes beyond the published record and holds under a check |
| **Promising** | Passes its own checks and is one named step from the tier above |
| **Thread** | An idea with a concrete next test, not yet a result |

## New ground

### 1. Every realization of the 10-vertex rigid graph can be real (rigid-realizations)

- [F] The published record for this graph is 860 real realizations verified and 868 found numerically (Bartzos, Emiris, Legersky and Tsigaridas, arXiv:1811.12800). The repository gives bar lengths with 880 real realizations. Its own count of complex realizations is also 880.
- [F] A separate exact check written for this review confirms the 880 (`checks/l880_independent.py`).
- [I] If the repository's computed complex count of 880 is taken as given, this settles the maximum number of real realizations for 10 vertices. The published growth rate for real realizations, 2.3780 per vertex, comes from 430^(1/7). The same construction with 440 gives 2.3858.
- **Who would care.** People who count realizations of rigid graphs, in rigidity theory, computational algebraic geometry and robot kinematics.
- **Before it goes out.** A second implementation of the complex count. A human read of the paper. A note that the search that found the lengths cannot be replayed from the repository.

### 2. Exact counts of balance points for 4 to 7 charges (point-charges)

- [F] Maxwell's bound was disproved in July 2026 by a five-charge example with at least 24 balance points (Arathoon, Ball and Kvalheim, arXiv:2607.27197).
- [F] The repository proves the count for that example is exactly 24. It gives a six-charge arrangement with exactly 29, above the bound of 25, a seven-charge one with exactly 44, and a four-charge one that reaches the bound of 9.
- [F] The repository's second verifier returns all five counts on a fresh clone. A search found the six-charge count nowhere else.
- [F] The field is moving. Four related preprints appeared between July and September 2026 (arXiv:2607.28785, 2609.00336, 2609.03965, 2609.09637), and a public project has an open item to formalise the conjecture in Lean.
- **Who would care.** The authors above and the groups working on the three-charge case.
- **Before it goes out.** An independent checker, which would move it from REPRODUCED to VERIFIED. For seven charges only one of the two verifiers finishes.
- [I] This is the most time-sensitive item in the organisation. Others are likely to compute the same counts.

### 3. Proofs of eleven counting formulas (finite-state-proofs)

- [F] The eleven recurrences are listed in the OEIS as "Empirical", meaning fitted and unproved. A268881 still reads that way.
- [F] The repository proves them with exact integer certificates that two programs check.
- [I] Small, but clean and easy to hand over: a comment on each OEIS entry with a link to the certificate.
- **Before it goes out.** A human read of the short argument that links the counting problem to the transfer matrix.

## Promising

### 4. Two new limits on codes over GF(7) (gfq-codes)

- [F] No [55,10,40] code and no [74,10,56] code exists over GF(7). Both are verified here, and both improve the bound shown at codetables.de. Four more bounds follow from them.
- [I] The twelve GF(9) bounds showed that the online table can lag behind the literature. The same may be true for GF(7), so a literature check comes before any claim of priority.
- **Next step.** Check the two base facts against the literature, then send them to the table's maintainer. The repository says nothing has been submitted.

### 5. Elastic constants of the incentre lattice in any dimension (incentre-lattices)

- [F] For ideal unit springs the repository states C11/C12 = (n-1)^2, zero shear moduli, and a Poisson ratio of 1/(n^2 - n - 1) along a cube axis. Its finite checks pass for n = 2 to 8.
- [F] The repository itself says the framework is prior art and calls this result its strongest candidate for something new, with priority unresolved.
- **Who would care.** Rigidity theory and the design of mechanical metamaterials.
- **Next step.** A line-by-line read of the written proof by a mathematician, and a search of the mechanics literature for the formula. Then a comparison with measured elastic constants of the hexaborides, which have this structure.

### 6. An exactly certified continuous motion between two crystal packings (incentre-lattices)

- [F] The repository gives a continuous motion from the cab framework to the fcc packing, with an exact certificate over 3,248 polynomials. Its checks pass. The proof has not been read line by line.
- [I] Not yet judged for novelty. It is listed because an exact certificate for a continuous motion is uncommon.

## Threads worth pulling

### 7. Point the box method at two open targets

- [F] certified-orbits and relative-equilibria are plans. Each names a published source: 10,059 numerical three-body orbits (arXiv:2508.08568), and a paper that could not obtain a rigorous list of equilibrium shapes for eight equal masses (arXiv:1812.07279).
- [I] The method that verified the 880 realizations and counted the balance points is the method these plans call for. The organisation has shown it can carry it out. A rigorous list for eight masses would be a new result.

### 8. Prove empirical OEIS recurrences in bulk

- [I] The eleven proved formulas come from one contributor's family of strip-counting sequences, and that family is large. The transfer-matrix certificate is mechanical. A run over the family would show how many fall to it. The number is not known, so sample first.

### 9. gravity: a threshold with a testable redshift dependence

- [F] Compared like with like, the gravity data table is described well by extra mass that switches on above about 185 to 200 km/s, with a dark-to-baryon ratio near 4 (`checks/g185_like_for_like.out`).
- [I] This is a compact description of something known: modified gravity fits galaxies and falls short in groups and clusters. It is not new physics as it stands.
- [F] Claim C-27 states a prediction. If the threshold follows the cosmic collapse scale, it falls to 114 km/s at redshift 0.5 and 70 km/s at redshift 1. If it is a constant of nature, it does not move.
- [I] A sample of galaxy groups with lensing masses at redshift 0.5 would separate the two. So would systems between 200 and 280 km/s today, where the table has none. This is the one place where the gravity work makes a prediction that could fail.
- **Before any of that.** Rebuild the table from published sources and fit both parameters (`notes/gravity.md`).

### 10. Does the acceleration scale follow the expansion rate?

- [F] `gravity/acceleration-evolution` sets out a test of a_0(z) = A E(z)^q and says the fit to raw data has not been done.
- [F] Reader finding, not re-checked by the lead: over the redshift range of the 2026 MUSE-DARK III sample (Ciocan and co-authors, 79 galaxies, redshift 0.33 to 1.44, named as the primary source in `gravity/acceleration-evolution/evidence.json`), a scale that follows the expansion rate grows by a factor of 1.92. The survey's two fitted curves grow by 1.93 and 2.16.
- [I] That agreement is suggestive and no more. Published fits at high redshift are contested, and the comparison uses fitted curves, not data. The protocol in the folder is the right next step.

### 11. Auditing what a formal proof states

- [F] formal-claims-audit asks whether the Lean statement behind a claimed result says what its paper says. It has not started.
- [F] This pass shows why it matters. A proposed token scanner passed a file that proves `False` (`checks/scanner_miss.lean`), and gravity's Lean lemmas carry physical names over integer arithmetic.
- [I] Several outside groups now publish machine-checked results from AI systems. A careful, public audit of statement against claim would be used.

## Where there is no new ground yet

| Work | Why |
|---|---|
| gravity as a theory | Its ledger says it is not one. The central agreement is overstated |
| The twelve GF(9) code bounds | Correct, and already in Maruta's tables |
| exoplanets-frontier | The ledger and the result files disagree. No candidate is established |
| covering-min-modulus, certified-orbits, relative-equilibria, lost-eclipses, gaia-dr4, wwssn-microseisms | Plans |
| fractals | States that it claims no new result |
| thermal-capture, ductricity | Essays without a computation |

Not judged in this pass: vitruvian3d, the math0 integer multiplication study, nhanes-bioimpedance, virtual-human and project-asma (128 claim rows in the H1 claims index). Of four small data pilots, plate-novae, overdue-data and rism-anon were not judged, and plate-eclipses was judged in part.

## What this says about direction

[I] The work that holds is exact mathematics with machine-checked certificates. None of it is yet a step toward a unified physical theory. Thread 9 is the nearest thing to a physical prediction, and it needs its data rebuilt first.

[I] The fastest route to results others will cite is items 2, 1 and 3, in that order: an independent checker for the charge counts, a second count for the rigid graph, and a short note to the OEIS.
