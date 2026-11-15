# Note: incentre-lattices

Pinned head `incentre-lattices@2d374ff`. Marks: **[F]** fact, **[I]** inference.

## What was run

- [F] Lead run: `make verify` on a fresh copy exits 0, reports 15 checksums OK, and leaves the tree clean.
- [F] Reader run: every verifier also passes under `python3 -O`. None relies on a bare assert. They fail through `tools/certlib.py`.
- [F] Reader run: a one-digit change in a certificate is caught by the hash check and by `build_certificates.py --check`, not by the verifier that reads it. A path coordinate moved by 0.001 is rejected by the locked checker.
- [F] Reader run: `formal/Arithmetic.lean` compiles and its four theorems use no axiom. They are counting arithmetic and say nothing about rigidity, as the repository states.

## How the 86 indexed rows were judged

- 23 rows are not claims: 5 negative controls labelled "must be rejected" and 18 rows of the internal review ledger.
- The other 63 rows, and claim H1, are REPRODUCED. They are nine results, each stated in up to four files (README, a copy of the README table, `docs/status.md`, `docs/audit.md` and the PROOF file).
- [I] "Must be rejected" does not mean a result was refuted. It marks inputs that a verifier is built to refuse.

## The nine results and what stands behind each

| Result | Label in the repository | What this pass can say |
|---|---|---|
| Elastic constants in n dimensions | PROVEN for n at least 3, VERIFIED for n = 2 to 8 | Finite check REPRODUCED. The step from C11 and C12 to the Poisson ratio was checked by hand. The written proof was not checked line by line |
| Radius ratio under H1 or H2 | PROVEN, VERIFIED on 20 polytopes | Finite check REPRODUCED, in floating point. Which polytopes satisfy H1 or H2 is open |
| CaB6 packing maximum | PROVEN upper bound and attainment | REPRODUCED. Reader finding: the exact all-pairs check behind the attainment step is not in the repository |
| 2D fold | KNOWN linkage, corollaries PROVEN | REPRODUCED. Reader finding: the first-contact claim is numerical only |
| 3D fold, cubic | VERIFIED | REPRODUCED |
| Fold to close packing | VERIFIED, sampled | REPRODUCED. A sampled path is evidence of a motion, not a proof |
| Exact fold end states | PROVEN, integer arithmetic | REPRODUCED |
| Fold at m = 1 | VERIFIED, sampled | REPRODUCED |
| Continuous fold to fcc | PROVEN, written argument and exact certificate | REPRODUCED. The written argument was not checked line by line |

## Prior art, as the repository states it

[F] Reader finding: the README says the bridged cross-polytope family is prior art (Borcea and Streinu 2021), that the counts in n dimensions are "likely routine", and that the unit-spring elastic result is the "strongest remaining candidate" for something new, with priority "unresolved". One research note still says "No prior reference found".

## What is not there

[F] No material constants, no stiffness in physical units and no carbon fibre data. The elastic result is for ideal unit springs, and its stiffness tensor has zero shear moduli. [I] A claim about a real material would need a separate model. The new repository fibral-rigidity is outside the pinned set and was not read.
