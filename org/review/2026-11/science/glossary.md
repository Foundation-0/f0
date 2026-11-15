# F6: claim labels, with one example each

Science pass, 15 November 2026. These are the definitions used in `verdicts.csv`. They follow the evidence standard in issue 50. Each example is from a repository at its pinned head in `tools/heads.tsv`.

A claim gets three separate judgments: the **statement**, the **evidence** offered, and the **label** it carries. A true statement can carry a label that says too much.

## The labels

| Label | What it requires | Example from this review |
|---|---|---|
| **PROVEN** | A Lean proof that depends only on `propext`, `Classical.choice` and `Quot.sound`, with a statement that matches the claim. Or a written proof that a reviewer has checked line by line. | `gravity@8f96c4b:formal/Wave10JeansDerivation.lean:33` proves `315 * 1101^3 > 1000 * 200 * 2090000`. It builds and uses no axiom. The claim it carries is that inequality and nothing more. |
| **VERIFIED** | Exact or interval arithmetic, re-run from a fresh clone at a pinned commit, recomputed with code the reviewer wrote, and still failing under `python3 -O` and on corrupted input. | rigid-realizations L880. `checks/l880_independent.py` proves in rational arithmetic that each of the 440 boxes holds one real solution, and it rejects three corrupted inputs. |
| **REPRODUCED** | The repository's own code gives the stated numbers from a fresh clone. The command and the output hash are recorded. | point-charges. `verify_arb.py certificates/*.json` on `a2fd159` reports exactly 4, 9, 24, 29 and 44 equilibria. |
| **KNOWN** | True and already published. The citation is quoted exactly. Say so where the repository presents it as new. | gfq-codes, the GF(9) cells. Maruta's table gives n_9(4,26) = 32, so no [31,4,26] code over GF(9) exists. The repository reports it as a new bound against codetables.de. |
| **OPEN** | Plausible, but the evidence does not establish it. The reason is given. This is the default and is not a criticism. | exoplanets-frontier C-07. The results file and its hash agree at the pinned head. The multi-sector re-run needs survey downloads and was not done. |
| **OVERSTATED** | The label or the wording claims more than the evidence shows. The verdict says what the evidence does show. | gravity C-27. Four speeds near 185 km/s are called independently defined. One is linear in a chosen overdensity, one scales with a chosen mass, and one moves from 153 to 216 km/s with the halo convention. |
| **CONTRADICTED** | A reproducible counterexample, a computation that fails from a fresh clone, or an exact quote from a primary source. It is attached. | gravity C-08, the lens counts. The four counts given per bin are not in the cited paper, which gives different counts per bin. |
| **NOT CHECKABLE** | Data or code is missing. The verdict says what and where. | exoplanets-frontier C-05. The 14.35 day signal appears in no results file at the pinned head. |

Two more values appear in the `status` column of `verdicts.csv`. They are not verdicts.

| Status | Meaning | Example |
|---|---|---|
| **not a claim** | The indexed row is not a result of that repository. | `notes/reports/fact-check.md`, a table of 15 literature checks copied into 12 repositories. It supplies 180 of the 383 indexed rows. |
| **not yet judged** | In scope, but this pass did not reach it. | math0, the integer multiplication study. |

## How the repositories use the same words today

| Repository | Word | What it means there | Pin |
|---|---|---|---|
| gravity | `PROVEN (ARITHMETIC-LEMMA)` | A Lean check of a literal integer or rational statement. The ledger says it is never applied to a physical reading. | `gravity@8f96c4b:CLAIMS.md:13` |
| incentre-lattices | PROVEN | A written proof with review by AI agents only. | `incentre-lattices@2d374ff:results/rigidity-nd/PROOF.md` |
| incentre-lattices | VERIFIED | A finite computation, in floating point for some rows and exact for others. | `incentre-lattices@2d374ff:docs/audit.md` |
| exoplanets-frontier | VERIFIED | A pipeline output file, cited with a hash prefix. Three of the five prefixes do not match the files. | `exoplanets-frontier@3bc0163:CLAIMS.md:24,29,43` |
| cfrp-strengthening | VERIFIED | The checker agrees with ten printed values from a worked example, inside tolerances the author set. | `cfrp-strengthening@3f68ccc:README.md` |
| rigid-realizations | CLAIMED | A computer-assisted certificate that awaits an independent check. | `rigid-realizations@298926c:README.md:20` |
| 12 repositories | CONFIRMED | A quoted fact was found at its cited source. It says nothing about the host repository. | `notes/reports/fact-check.md` |

## What the science says about decision 4

Decision 4 in issue 42 proposes four terms: CLAIMED, REPRODUCED, VERIFIED and PROVEN. This pass supports that set with three additions.

1. KNOWN is needed. Several results are correct and already in the literature. Without the word, a correct result reads as a new one.
2. A label should name its object. gravity's `PROVEN (ARITHMETIC-LEMMA)` does this well. A bare PROVEN next to a physical name does not.
3. CONFIRMED should be kept for source checks only, and kept out of result tables.
