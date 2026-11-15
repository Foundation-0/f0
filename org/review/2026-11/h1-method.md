# H1 inventory, claims index and checks census

Foundation-0 public repositories, read on 15 November 2026. Every fact here is read from a fresh clone at the head named in the table below. Nothing in these files judges a claim.

## Scope and pinned heads

35 public repositories, cloned from their default branch. Private repositories are out of scope as the issue says. Size: 883 research files in `inventory.csv`.

| repository | head |
|---|---|
| .github | 81f83c38918382b4ca142b81debd3cc5ccf61d3a |
| astr0 | 67cafe2defc44d5a4e17815fc7329f65eeef45eb |
| certified-orbits | 51f69833cd64ff3c1bc65c429566714fa2c9c17e |
| cfrp-strengthening | 3f68cccf19556574b7652311be1b0dc0daa93144 |
| cosmic-denoising | a00e2b5b827e0f4c9c5f0c01cba609fa523a9811 |
| covering-min-modulus | e8ecf1b53e337b9267831779c3760bd8dfe0feaa |
| discussi0n | 5accdb70fa770609e17504a5930823cda7ba7ed3 |
| ductricity | 0a178a01209b6b583408a861b2476e2308e1f053 |
| exoplanets-frontier | 3bc0163bc04547628072aa5b281eda282347e3d1 |
| f0 | 6ea3a0b3d18fa1e7cf1845e3dc67220a35781948 |
| finite-state-proofs | 9eeb3da2cdd6ba6b100ac24d23b32c369c0db8ec |
| formal-claims-audit | bacf05953c10bf5105fa1209a127392d395e2f92 |
| fractals | 48b923bd25dbcfef7fa8e8399d4144592145f0ef |
| gaia-dr4 | 0110e1cea41631bd91ab4d7ec32e0c5199262381 |
| gfq-codes | 9200a06be239d6cc70ec94ed82f681e75b9bc718 |
| gravity | 8f96c4b240f985c3e3e1b81f64c3e91a5534d4f2 |
| incentre-lattices | 2d374fff2a59cc9331566733043a4bb25c1040bf |
| lost-eclipses | f9989df2be02cc13331d6c74b89f0225f28fd8e4 |
| math0 | e649250ca32249affe52873a45d22e8bd5562624 |
| nhanes-bioimpedance | efb3395b70e32ae96779a73454b2333b7e86c4d1 |
| overdue-data | cc50b3c15751519311350b3e20645cea031219f5 |
| physics0 | 913468f093f82d869dc58b404039ea0a416cfb80 |
| plate-eclipses | c0b7b0b6260f67d1a6964465bd3164283d1c73f7 |
| plate-novae | 9183100ec8778009982add1c09d7efb6c190117b |
| point-charges | a2fd159bccb24d2922a127ad83f28b9f44e2ceba |
| project-asma | 48178217a88066212ec798a7e8031e6fc652493e |
| proven-commons | 903c1858be856776de21675cf5c4e26fb9eebcdf |
| relative-equilibria | bf1e1cedeb42848f67fbd014a295e100137e6a6d |
| rigid-realizations | 298926c5e7a03683bb83165931ac38a94260166f |
| rism-anon | c345b5b4de85d1b4763e6219b5020204ac975645 |
| st0a | 7cb5b9a24b935603cfedb7e214b01d6cf54b04da |
| thermal-capture | 5fa678e94d2e6b1ace56d2cc7e4e0b0eae0a91af |
| virtual-human | 6b10b458704e36cd592552ab8165d55ce5fe64ec |
| vitruvian3d | 7099f5cb317e77d6e675d798397e2351f7c42ad2 |
| wwssn-microseisms | 2bb4f58460a3e99a377d92242c1b8ce097978f2e |

## What counts as a research file

`inventory.csv` has one row per research file, with its type, blob hash, size, and the last commit that touched it. The types and the rule for each:

| type | rows |
|---|---|
| claims | 7 |
| paper | 9 |
| monograph | 8 |
| note | 323 |
| readme | 97 |
| lean | 16 |
| verifier | 159 |
| certificate | 86 |
| dataset | 158 |
| zenodo | 20 |

- **claims**: a claims register (`CLAIMS.md`, `registries/claims-ledger.json`, `CLAIM_MAP.json`, `notes/reports/ai-claims.md`).
- **paper**: files under `papers/` or `paper/`, `manuscript.md`, and `.tex` sources outside `docs/`.
- **monograph**: files under `monographs/`, excluding figures and checksums.
- **note**: Markdown or text research writing, including every `PROOF.md` and `THEOREM.md`.
- **readme**: a `README.md`. Kept apart because most repositories state their result there.
- **lean**: `*.lean`, except the build file `lakefile.lean`.
- **verifier**: a script whose name marks it as a checker (`verify`, `check`, `audit`, `probe`, `replay`, `recompute`, `validate`, `independent`, `attest`, `confirm`, `gate`, `vet`, `equivalence`), excluding `test_*` files.
- **certificate**: `SHA256SUMS`, `commitment/ROOT`, and files with `certificate` or `.cert.json` in the name.
- **dataset**: data and results files under `data/`, `results/`, `inputs/`, `snapshot/`, `registries/` and the crystal-structure `cod/` folder.
- **zenodo**: every `.zenodo.json`.

Not inventoried: figures, site HTML, CSS and JavaScript, CI workflows, licences, `AGENTS.md` and `CLAUDE.md`, tests, and library code that is not a checker. The rules are mechanical, so a few edge cases are debatable. `coverage.csv` shows the counts per repository, so a gap is easy to see.

## Claims index

`claims-index.csv` has 192 rows: 173 claims, 10 method entries and 9 review dispositions.

- gravity: 33 claims (`C-01` to `C-33`) from `CLAIMS.md`, 10 methods (`M-01` to `M-10`) from `METHODS_AND_PLAYBOOK.md`, and 9 disposition rows (`D01` to `D09`) from `research/update-d144448-review/CLAIM_MAP.json`. Each D row names the claim it reviews in the `xref` column.
- exoplanets-frontier: 8 claims (`C-01` to `C-08`) from `CLAIMS.md`.
- project-asma: 128 claims, 118 from `registries/claims-ledger.json` and 10 (`A1` to `A5`, `B1`, `C1` to `C3`) from `docs/cdr2-hla-ii-evidence-map-2026-11-06.md`, found by the scan.
- incentre-lattices: 1 claim (`H1`) from `docs/audit.md`, found by the scan.
- rigid-realizations: 3 claims (`L344`, `L880`, `G160`) from `README.md`, found by the scan.

The `scope` column carries the decision: `in` for gravity, exoplanets-frontier, incentre-lattices and rigid-realizations, 64 rows in all, and `reference` for project-asma, 128 rows. F2 can filter on the column instead of the repository name.

The label column repeats the label as written, with Markdown backticks removed and nothing else changed. Where a claim carries two labels, both are kept. The text column keeps the claim wording verbatim, backticks included. Only the label column strips them.

**30 of the 35 public repositories define no claim ID at all.** They state results in a `README.md`, a `PROOF.md`, or named result folders, without IDs to cite. The exceptions are gravity, exoplanets-frontier, project-asma, incentre-lattices and rigid-realizations. A scan of every Markdown and JSON file for an ID pattern followed by a label found no other register. The 30:

`.github`, `astr0`, `certified-orbits`, `cfrp-strengthening`, `cosmic-denoising`, `covering-min-modulus`, `discussi0n`, `ductricity`, `f0`, `finite-state-proofs`, `formal-claims-audit`, `fractals`, `gaia-dr4`, `gfq-codes`, `lost-eclipses`, `math0`, `nhanes-bioimpedance`, `overdue-data`, `physics0`, `plate-eclipses`, `plate-novae`, `point-charges`, `proven-commons`, `relative-equilibria`, `rism-anon`, `st0a`, `thermal-capture`, `virtual-human`, `vitruvian3d`, `wwssn-microseisms`.

This matters for decision 4 and for F2: a glossary cannot be applied to claims that have no identifier to carry a label. The next section indexes their stated results. The repositories that do use IDs use three different label vocabularies:

| repository | labels |
|---|---|
| gravity | COMPUTED (known framework or model scan), EMPIRICAL-FIT, KNOWN-LITERATURE-VALUE, CONJECTURE, and PROVEN (ARITHMETIC-LEMMA) on the Lean lemmas |
| exoplanets-frontier | VERIFIED, FALSIFIED, CONJECTURE, KNOWN |
| project-asma | VERIFIED, KNOWN, CONJECTURE |
| incentre-lattices | CLAIMED |
| rigid-realizations | KNOWN, CLAIMED |

## Results without a claim ID

`results-index.csv` has 383 rows from 24 repositories. The columns match `claims-index.csv`. The ID is provisional, `<repository>/R-<n>`, numbered in file and line order within each repository. 340 rows carry a label. Labels and text have Markdown emphasis, backticks and heading marks removed and whitespace collapsed. Nothing else changes.

Two repositories in this index also carry a few claim IDs of their own (incentre-lattices `H1`, rigid-realizations `L344`, `L880`, `G160`). Their stated results are indexed here all the same, since the IDs cover only a handful of rows.

Three sources, all mechanical:

- **result-table**, 308 rows: the body rows of a table whose header has a subject column and a status column. The subject column is the first header that begins with `result`, `statement`, `theorem`, `claim`, `contribution`, `question`, `track`, `area`, `proposition`, `lemma` or `evidence`, in that order. The label comes from a `label`, `status` or `verdict` column. A project index (`Project | Question | Status`) keeps the question as the text and the status as the label.
- **proof-title** and **proof-statement**, 34 rows each: every `PROOF.md` and `THEOREM.md` gives two rows. The first is the title, taken from the first heading or the first bold line. The second is the first paragraph of the statement, or the paragraph after the title when the file has no statement heading. The statement row names the title row in `xref`.
- **result-line**, 7 rows: a line that begins `Theorem`, `Proposition`, `Lemma`, `Conjecture` or `Result` in a file typed paper, monograph or note, outside a code fence and at least 25 characters long.

8 repositories give no row: `.github`, `cosmic-denoising`, `discussi0n`, `ductricity`, `fractals`, `proven-commons`, `st0a`, `thermal-capture`. None of them has a result table, a `PROOF.md` or `THEOREM.md`, or a theorem line at this head, so any result they state is written in prose. Fable's F1 covers prose.

Rows that record a plan rather than a result are kept and labelled as written, for example `Not started.` in `astr0`, `physics0` and `math0`. The rule copies and does not judge, and F2 decides what to do with them.

`coverage.csv` carries a `results_indexed` column, so a repository with no row is visible in the same table as the claim count. The `scope` column is `in` on every row: these are results in repositories the issue puts in scope, and a result indexed here cannot be outside it.

## Checks census

`checks-census.csv` counts, per repository:

- **bare assert**: statement-level `assert` lines inside verifier files, counted separately for Python and for other languages.
- **check mode**: verifier files that implement a `--check` flag, and separately those that implement `--write`.
- **skip ci**: commits on the default branch whose subject contains `[skip ci]`, all time and since 7 November.
- **Lean**: `sorry` occurrences and `axiom` declarations, after removing comments.

| what | count |
|---|---|
| verifier files | 159 |
| bare `assert` in Python verifiers | 482 |
| bare `assert` in verifiers in other languages | 0 |
| verifier files with a `--check` mode | 20 |
| verifier files with a `--write` mode | 8 |
| `[skip ci]` commits, all time | 50 |
| `[skip ci]` commits since 7 November | 50 |
| Lean files | 16 |
| `sorry` | 0 |
| `axiom` | 0 |

All 50 `[skip ci]` commits are in exoplanets-frontier. gravity has none at this head. No Lean file at these heads contains `sorry` or declares an `axiom`. Matches in comments are excluded, and the two Lean modules that mention them say "zero sorry, zero axiom".

### Difference from the 14 November scan

The issue gives 107 bare asserts in gravity, 96 in vitruvian3d, 7 in incentre-lattices, 6 in point-charges and 4 in rigid-realizations. This census gives 245, 155, 9, 5 and 4.

The gap is scope. This count covers every file whose name marks it as a checker, and the 14 November scan's file list is not recorded. The file-by-file counts are in the `assert_files` column so the two can be reconciled. The comparison is a number to refresh, not a finding about either scan.

## How to rerun

```
bash tools/clone-all.sh          # clones the 35 repositories into tools/mirrors,
                                 # writes tools/heads.tsv
python3 tools/build_h1.py        # writes inventory.csv, claims-index.csv,
                                 # checks-census.csv
python3 tools/build_results.py   # writes results-index.csv from inventory.csv
python3 tools/build_coverage.py  # writes coverage.csv
python3 tools/make_docs.py --h1  # writes this note
```

The scripts are in `tools/`. `tools/mirrors/` holds the clones and `tools/.gitignore` keeps them out of the commit. `clone-all.sh` is the only step that needs the network.

Three runs on 15 November produced byte-identical copies of every file here: two plain runs and one under `python3 -O`. The scripts contain no `assert`, so an optimised run cannot skip a check.

Three mutation tests on copies of the clones, each discarded afterwards:

- Deleting the `gaia-dr4` row, `astr0/R-4`, from the project table in `astr0/README.md` removed exactly one row (the rows after it renumber, so `R-5` is the ID that vanishes) and left 382
- Deleting the `C-10` line from `gravity/CLAIMS.md` removed exactly that row, 192 to 191
- Adding one `assert` to `gravity/verify_all.py` raised gravity's count from 245 to 246

## Limits

- The head is a moment. Counts will move as PRs merge.
- The classification is by name and path, not by reading each file, so a checker with an unusual name is missed and library code that happens to be named `check_*` is included. The lists are in the CSV so the error is visible.
- No network fetch is involved. The repository clones are the only input, and `heads.tsv` records the commit each file was read at.

