# F4: re-check of the 14 November findings

Science pass, 15 November 2026. Each finding from issue 42 (The problem, items 3 and 4, and Phase 3) was re-run on fresh clones at the pinned heads in `org/review/2026-11/tools/heads.tsv` on the H1 branch (draft PR 45). Gravity `main` is `8f96c4b`, which is after the 14 November merges.

Marks: **[F]** a fact read from a repository or a run, **[I]** an inference. "Lead" means the run was done in this pass by the lead reviewer. "Reader" means a reading agent ran it and the lead did not repeat it.

## Result

| # | Finding in issue 42 | Outcome on the pinned heads |
|---|---|---|
| 3a | Many checks are bare `assert`, which `python -O` skips | **Confirmed** |
| 3b | Some `--check` modes regenerate instead of comparing | **Confirmed** |
| 3c | Some tools exit 0 when given no input | **Confirmed** (reader run) |
| 3d | gravity `verify_all.py --check` overwrites the files it checks | **Confirmed** |
| 3e | vitruvian3d verifiers accept a corrupted certificate under `-O` | **Confirmed** |
| 3f | The scanner in proven-commons 9 misses a compiling proof of `False` | **Confirmed**, with a new counterexample |
| 4a | "PROVEN" and "VERIFIED" mean different things in different repositories | **Confirmed** |
| 4b | gravity's "PROVEN" Lean lemmas include `2 + 1 = 3` | **Confirmed**, with a qualification |
| 4c | exoplanets-frontier RUWE is exactly 1.0 for all 348 Platinum and Gold rows | **Confirmed** |
| 4d | 16 Zenodo records say "Researched and verified by" a list of models | **Confirmed**, and 9 of the 16 hold no result of their own |
| P3a | gravity page still shows withdrawn claims | **Confirmed in part** |
| P3b | 8 of 36 `SHA256SUMS` entries fail | **Overturned** on `main` |
| P3c | KiDS lens counts are not in the cited paper | **Confirmed**, and refined |
| P3d | gravity Pages site resembles fdn0.org | Not judged. This is a site question, not a science one |
| H1 | The L880 count passes an independent exact re-check | **Confirmed** by a second independent check |
| H2 | vitruvian3d's proofs are correct | Not judged in this pass |
| H3 | fractals 26 and 35 reproduce from independent code | Not judged in this pass (belongs to F5) |

## Evidence

### 3a, 3b, 3d: gravity check modes

- [F] `gravity@8f96c4b:verify_all.py:384` writes the certificate with no condition. The `--check` flag only changes what is printed afterwards (`:389`).
- [F] Lead run in a copy: one digit of `results/certificates.json` was changed, then `python3 verify_all.py --check` was run. Exit code 0, and the file was rewritten to its original bytes. The same happens under `python3 -O`.
- [F] `gravity@8f96c4b:wave10_covariant_jeans_unification.py:320-327` compares with four `assert` lines. Lead run: with `185.59` changed to `195.59` in the stored certificate, the bare run exits 1. Under `python3 -O` the same file prints `CHECK OK (byte-identical)` and exits 0.
- [F] The `emit_or_verify` function is byte-identical in the Wave 7, Wave 9 and Wave 10 scripts (`wave7...py:227`, `wave9...py:174`, `wave10...py:315`), so the three behave the same way.
- [F] H1 counts 245 bare asserts in gravity checker files (`checks-census.csv`). That count was not redone here.

### 3c: tools that pass on nothing

- [F] Reader run: `formal-claims-audit@bacf059:scripts/check_verdicts.py` passes on zero verdict files, bare and under `-O`.

### 3e: vitruvian3d

- [F] `vitruvian3d@7099f5c:research/passage_verify.py:64` is a bare `assert`.
- [F] Lead run in a copy: one digit of `research/passage_certificate.json` was changed. Bare run: exit 1. Under `python3 -O`: exit 0, and the conclusion line was printed as if the certificate were sound.
- [F] Reader run: `replay_all.py` and the transport `check.py` refuse to run under `-O`. About 40 other scripts use bare asserts.

### 3f: proven-commons 9

- [F] `checks/scanner_miss.lean` is eight lines. It hides `implemented_by` behind a `deprecated` attribute with a `since` argument, then proves `False` with `native_decide`.
- [F] Lead run: `lean` 4.35.0 compiles it with exit 0 and two deprecation warnings.
- [F] Lead run: `scan_lean_tokens` from `scripts/surface_audit.py` at the pull request head `9ff9c40` returns an empty list for that file. For the same definition without the `deprecated` attribute it returns `implemented_by`.
- [I] The existing review on that pull request describes the attribute window. This file shows the consequence end to end. `scripts/audit.py` on `main` would still catch it, because `native_decide` adds an axiom that `collectAxioms` reports.

### 4a, 4b: labels

- [F] `gravity@8f96c4b:CLAIMS.md:147` reads "Checks `2 + 1 = 3` and `2 * 1 = 2`" under the label `PROVEN (ARITHMETIC-LEMMA)`. The Lean statement is at `formal/Wave11MachianZeroEnergy.lean:31`.
- [F] Lead run: `lake build` succeeds on `8f96c4b`. All 32 theorems in `formal/*.lean` depend only on `propext`, `Classical.choice` and `Quot.sound`, or on no axiom. No `sorry`, no `axiom`.
- [I] The ledger defines the label as covering the arithmetic only (`CLAIMS.md:13`), so inside the ledger the label is accurate. The theorem names are physical (`c28_machian_induction_partition_unity`, `c30_cpt_pair_opposite_noether_charge`) while the statements are integer arithmetic. A reader who sees only the name and the word PROVEN is misled.
- [F] `gravity@8f96c4b:index.html:187` says "zero unearned PROVEN tags".
- [F] Meanings found for the same words: gravity PROVEN is Lean integer arithmetic. exoplanets-frontier VERIFIED is a pipeline output with a file hash. cfrp-strengthening VERIFIED is agreement with ten printed values inside a tolerance the author set. `glossary.md` lists them.

### 4c: RUWE

- [F] Lead run: `exoplanets-frontier@3bc0163:results/platinum_followup_targets.csv` has 348 rows. The `ruwe` column holds the single value `1.0`. The `nss` column holds the single value `0`.
- [F] `blend_gaia.py:24` substitutes `1.0` when the Gaia value is missing. Lines 37 and 42 set `1.0` on the fallback paths.
- [I] Real RUWE values for 348 stars would not all be exactly 1.0. The Gaia binary-star check did not run on these rows, so "clean" in claim C-08 is not supported by this file.

### 4d: Zenodo records

- [F] H2 lists 16 published v1.0.0 records with the line "Researched and verified by different model families".
- [F] Six of those repositories say "Status: not started" at the pinned head: certified-orbits (`README.md:20`), covering-min-modulus (`:19`), formal-claims-audit (`:17`), relative-equilibria (`:22`), lost-eclipses (`:19`), wwssn-microseisms (`:16`). gaia-dr4 says "preparing. No results yet." (`:39`).
- [F] Reader finding: ductricity and thermal-capture hold text only, with no code, data or computation.
- [I] In 9 of the 16 records there is no result for "verified" to refer to. Decision 5 in issue 42 covers the wording. This adds that the word is empty for those nine whatever wording is chosen.

### P3a: the gravity page

- [F] The numbers were corrected. `index.html:224` now shows 384.82, 200.08, 121.72 and 127.16 Myr, and the superseded 122.79 and 109.04 no longer appear.
- [F] The framing was not. `index.html:223` says the pair branches arise by "Bifurcating from unbroken w = −1 de Sitter symmetry". `CLAIMS.md:156` says the algebra "does not derive their production from `u = 0`".
- [F] `index.html:224` says the scale "traps 99.997% of condensate". `CLAIMS.md:173` says the value "is an assigned trapping prescription, not a capture solution".
- [F] `index.html:179` says the condensate "unifies" rotation curves, lensing, cluster cores and black hole assembly. `README.md:8` says the repository "is **not** a derivation of a new fundamental theory".

### P3b: checksums

- [F] Lead run: `SHA256SUMS` on `8f96c4b` has 39 entries. All 39 match the files. The 14 November count of 8 failures in 36 was made on a head before the merge.

### P3c: KiDS lens counts

- [F] `gravity@8f96c4b:CLAIMS.md:48` gives "52,553 + 43,727 + 22,950 + 9,797 = 129,027 isolated lenses in Mistele et al. 2024 ... Sec. II & Table 2".
- [F] The paper (arXiv:2406.09685, HTML version read on 15 November) says "the four mass bins contain [24297, 17183, 22083, 11570] LTG lenses", and gives 1795, 5439, 14220 and 32440 for the ETG lenses. None of 52,553, 43,727, 22,950, 9,797 or 129,027 appears in its text. Table 2 lists masses and velocities, not lens counts.
- [I] The paper's eight counts sum to 129,027, so the total can be derived from it. Per bin the paper gives 26,092, 22,622, 36,303 and 44,010, which rise with mass. The ledger's four numbers fall with mass. They are not the paper's.
- [F] The four velocity bins in `wave9_scale_convergence_audit.py:30-33` do match the paper's Table 2 ("All", R < 1000 kpc). The four KiDS rows in `wave7_group_cluster_threshold_audit.py:37-40` do not match any row set in Table 2.

### H1: L880

- [F] `checks/l880_independent.py` uses only the edge list, the 17 rational lengths, the pinned triangle and the 440 box centres. It builds its own preconditioners and uses no code from the repository.
- [F] Lead run on `rigid-realizations@298926c`: all 440 boxes pass in exact rational arithmetic, the boxes are pairwise disjoint, and corrupted inputs are rejected under `python3 -O`: one edge length changed, one coordinate of a pinned vertex changed, one edge of the list replaced, one box duplicated, and one centre moved by 2^-12 each exit 1 with a FAIL message. The program raises errors and has no `assert`. Output in `checks/l880_independent.out`.

## How to rerun

The four check programs are on draft PR 51 (branch `review/F2`), in `org/review/2026-11/science/checks/`. This branch holds only this file. Check out `review/F2`, or copy that directory, and run the commands from `org/review/2026-11/science/`. The clone directories are the pinned heads in `org/review/2026-11/tools/heads.tsv`, which is on the H1 branch (draft PR 45).

```
python3 -I checks/l880_independent.py <rigid-realizations>/rigid_realizations_l880_pr_bundle/results/l880-all-880-real/l880_certificate.json
python3 -I checks/delsarte_independent.py <gfq-codes>
python3 -I checks/g185_independent.py <gravity>
lean +leanprover/lean4:v4.35.0 checks/scanner_miss.lean
```

The Lean file has no imports, so the `lean` command also runs from any other directory with the file's path. `l880_independent.py` needs NumPy. `delsarte_independent.py` uses only the Python standard library. `g185_independent.py` needs NumPy and SciPy.
