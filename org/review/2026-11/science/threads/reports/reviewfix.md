# Review fixes on seven branches: full report

15 November 2026.

Short note for this thread: `../README.md`.

S is the working folder of this thread. It is archived outside the repository. Paths that start with S/ point into it. Where a file was copied into the repository, its repository path is listed at the end.

---

All seven branches have one new local commit each. Nothing was pushed or posted, and the clone is on `main` with a clean tree. The item table below is condensed.

**Commits** (no trailer. The F4 commit was amended once before handing back, since it is still local)
- F1 (PR 52): 1e06f90
- F2 (PR 51): 3758334
- F3 (PR 53): e6b45ab
- F4 (PR 54): 9fe6671
- F6 (PR 55): d964b92
- F7 (PR 56): b37a660
- F8 (PR 57): 02cc9c3

**Files for you to publish** (all in S/threads/reviewfix/bodies/)
- Bodies: `pr51.md` to `pr57.md`. The originals I fetched are in S/threads/reviewfix/orig/.
- Comments: `taking.md`, `status.md`, `f7-comment.md`, `f8-comment.md`, `newground-comment.md`.
- The prose gate exits 0 in both modes on every changed markdown file, body and comment.
- `taking.md` ends with the fixed blockquote, which you did not ask for. I added it because it is this account's first comment on the thread. Drop it if the thread rule differs.

**Key checks**
- `g185_like_for_like.py` regenerates its `.out` byte for byte: 60.26 as compared, 256.53 like for like, best 54.00 at sigma_J = 200 and D = 4.0.
- The regenerated `verdicts.csv` differs from the old one only in these rows:
  - gravity C-08 (verdict, label judgment, plain language).
  - gravity C-21.
  - The 3 L880 rows.
  - The 30 gfq-codes result rows.
- Rerunning with the documented H1 fetch steps gives an identical file.
- L880 corruption runs under `python3 -O` all exit 1 with FAIL for: a changed edge length, a changed pinned coordinate, a replaced edge, a duplicated box, and a centre moved by 2^-12.
- The old "moving one centre" wording was loose. A tiny shift inside the box radius still passes, so the notes now say 2^-12.
- `scanner_miss.lean` compiles on Lean 4.35.0 with exit 0 and two deprecation warnings.

**Reviewer wrong or partly right**
- **PR 53 B3 (a_0 in fractals): wrong.**
  - The fractals README writes the symbol as a₀ (`README.md:289`, `:290`, `:296`) and `atom.js:6` writes a0. Only the literal text `a_0` is absent.
  - I kept the row, added those pins, and listed gravity's a_0 at `CLAIMS.md:18`.
- **PR 53 B2 (gfq-codes 15 not 18): partly right.** There are 15 certificate files holding 18 certificates. I wrote "15 certificate files covering 18 statements". `delsarte_independent.out` was regenerated to say so.
- **PR 52 "Correction 21 in closed issue 21": not found.**
  - Fractals issue 21 holds no such text.
  - Item 21 exists only in the `CORRECTIONS.md` of open fractals PRs 26 and 35 (one item) and PR 54 (a different one).
  - I scoped the claim to those files.

**Fixed as the reviews asked**
- **Attribution (all seven):** the sentence naming who wrote the body and the generated-with footer are gone from every body. The decision-2 sentence, the single blockquote and the co-author-trailer line are in.
- **PR 51 (F2):**
  - Merge-order and dependency stated.
  - C-08 verdict is CONTRADICTED, with the qualification kept in label judgment and plain language.
  - Hashes labelled and recomputed.
  - The `-O`, exact-arithmetic and NumPy/SciPy claims limited to the L880 and Delsarte checks. The Delsarte check needs only the standard library.
  - L880 plain language now says 880 real is checked and the complex count is the repository's own computation.
- **PR 52 (F1):**
  - Two results have separate-code checks, with point charges marked REPRODUCED and lines 9 and 143 aligned.
  - Both rod thresholds are stated, checked in `connectors_proof.md:27` and `:57`.
  - The heads.tsv path, the `acceleration-evolution/STATUS.md` path, and the 100 versus 82 datasets disagreement (`README.md:70` against `docs/validation_body.md:3`) are fixed.
- **PR 53 (F3):**
  - N1 to N11, apart from the a_0 point above.
  - Cited files for the three planet-candidate figures corrected.
  - Companion-notes line names fractals 51, physics0 15 and astr0 4.
- **PR 54 (F4):**
  - Rerun section stands alone (PR 51 path, working directory, heads.tsv source).
  - `scripts/check_verdicts.py` path.
  - The `emit_or_verify` mark is [F]: the function text is identical in Waves 7, 9 and 10.
- **PR 55 (F6):**
  - CLAIMED row added from PR 44 and decision 4, with nine words stated plainly.
  - VERIFIED example cites the real path and drops "three".
  - Pins `CLAIMS.md:25,30,44` plus `:49,53`, and the C-08 qualifier.
  - [F]/[I] marks on the examples.
  - The nhanes exception: 189 rows in 13 repositories.
- **PR 56 (F7):**
  - Gravity table is 39 rows not published (38 computed, 1 set by hand), fixed everywhere it appears.
  - project-asma (128 rows) is named in every not-judged list.
  - plate-eclipses is marked partly judged.
  - The "repository's computed complex count" wording.
  - MUSE-DARK III is named, with 79 galaxies at redshift 0.33 to 1.44.
- **PR 57 (F8):**
  - f0 holds no copy of `fact-check.md`, so the file now says to place the canonical copy there.
  - The two out-of-date index quotations are named: math0 `README.md:22` and physics0 `README.md:17`. physics0's point-charges row is incomplete, not out of date.
  - The two GF(7) base facts are named.
  - The checker is described as comparing stored certificates against a fresh recomputation.
  - Draft PRs 52 and 53 are named in the file header.

**Not changed:** the reviewers' own limits (Lean not built in their environment, GF(7) values not re-read). The commit trailers stay, because removing them needs a force-push. Each body says so.

All edits are under `org/review/2026-11/science/` on the seven review branches in the local f0 clone.
