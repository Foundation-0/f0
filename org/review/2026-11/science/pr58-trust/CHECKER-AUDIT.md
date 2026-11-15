# Checker audit for pull request 58

15 November 2026. This audit answers blocking item 3 of the review of pull request 58. `threads/README.md` said that every checker written in this pass raises an error instead of using `assert`, and was run under `python3 -O` against corrupted input. `threads/convergences.md` said the same. This file lists what the record supports, program by program.

## How it was done

- Every `.py` and `.sh` file under `threads/checks/` was searched for `raise`, `SystemExit`, `sys.exit`, `assert` and printed verdict words. There are 333 such files, 288 outside the `state/` copies.
- For each program below, the failure path was read: what it does when a check fails.
- The saved outputs, the thread notes and the reports under `threads/reports/` were searched for runs on corrupted input, and for whether those runs used `-O`.
- Nothing was re-run for this audit. Runs made only during the review are noted at the end. They are not part of this pull request.

Columns:

- **Raises on failure.** Yes if a failed check raises an exception or exits with a nonzero status, without `assert`. Partly if some failures still exit 0.
- **Corrupted-input run in the record.** Whether a run on corrupted or false input is saved or stated in this pull request, and whether it used `-O`.
- **Evidence.** Paths are relative to `threads/checks/` unless they start with `threads/`.

## Table

| Program | What it checks | Raises on failure | Corrupted-input run in the record | Evidence |
|---|---|---|---|---|
| `charges/indep_count.py` | exact count of balance points | Yes. Exit 2 on a count mismatch, exit 3 on a proof failure | Yes, under `-O`. Five inputs. Four are rejected. The fifth changes only hint boxes the proof never reads, and passes as it should | `charges/state/run_corrupt.sh`, `charges/out/corrupt_final.log`, `four/controls/` |
| `charges/check_lemmas.py` | the two derivative bounds, by sampling | No. Print only. Its docstring says "not proofs" | No | none |
| `four/verify/lower_bound_check.py` | lower bound for four charges, ball arithmetic | Yes (`CheckFailure`) | One false claim, "prove 12", rejected. `-O` not recorded | `four/verify/lower_bound_check_control.out` |
| `four/verify/width.py` | width of the 11-point region, numerical | No. Print only | No | `four/verify/width.out` |
| `verify_arb.py` of the point-charges repository. Not written in this pass and not in this checkout | exact count | No. Its checks are `assert` statements at the pinned head | One changed charge, rejected. Run without `-O` | `four/controls/ctrl_repo_charge1.log`, `threads/four-charges-eleven.md` line 58 |
| `l2288/certify.py` | the 2,288 certificate, exact rationals | Yes (`SystemExit`) | Yes, with and without `-O`. Five kinds, plus an unchanged control that passes | `l2288/test_certify_corrupt.py`, `l2288/state/corrupt_tests_2288_dec6.out` and the other `corrupt_tests*.out` |
| `l2288/certify_arb.py` | the 2,288 certificate, ball arithmetic | Yes (`SystemExit`) | No. Only clean runs are saved | `l2288/state/certify_arb_2288_dec6.out` |
| `l2288/l2288_independent.py` | the 2,288 certificate, third checker | Yes (`SystemExit`) | Stated only. `threads/l2288.md` line 15 says five kinds are rejected, also under `-O`. No output is saved | `l2288/l2288_independent.out` (clean run) |
| `l2288/edge_frame_independent.py` | the 12-vertex certificate | Yes (`SystemExit`) | No | `l2288/edge_frame_independent.out` (clean run) |
| `l2288/v12/certify12.py` | the 12-vertex certificate, exact | Yes (`SystemExit`) | No. The harness `l2288/v12/test_corrupt12.py` has no saved output | none |
| `l2288/v12/certify12_arb.py` | the 12-vertex certificate, ball arithmetic | Yes (`SystemExit`) | No | none |
| `l2288/graph_check.py` | graph structure | No. Print only | No | `l2288/graph_check.out` |
| `laman/laman_count.py` | complex count by the published recursion | No. It prints the count. It raises only when the count is undefined | Yes, with and without `-O`. Three graphs that are not minimally rigid, run through `crosscheck.py` | `laman/crosscheck.log`, `laman/state/crosscheck_O.log` |
| `laman/crosscheck.py` | three implementations against each other | No. It prints DISAGREE and exits 0. It needs the `lnumber` library, which is not in this checkout | It is the harness for the row above | `laman/crosscheck.log` |
| `laman/validate_paper.py` | the paper's largest counts | No. It prints OK or MISMATCH | No | `laman/validate_paper.log` |
| `unit/check_point.py`, `unit/certray.py`, `unit/rayprofile.py`, `unit/conesize.py` | real counts near equal lengths, numerical | No. Print only | No | `unit/*.json` |
| `codes/verify_certs.py` | code certificates, recurrence form | Yes (`SystemExit`) | Yes. Five kinds, all rejected. `-O` not recorded for these runs | `codes/corrupt_results.out`, `threads/reports/codes.md` line 20 |
| `codes/verify_binomial.py` | code certificates, binomial-sum form | Partly. It raises on sign, distance and size, and never checks the declared size bound | Yes. Four of five kinds rejected. A wrong declared size bound is accepted. `-O` not recorded | `codes/corrupt_results.out` |
| `codes/verify_codes.py` | the lead's bookkeeping check | Yes (`SystemExit`) | No. It loads `delsarte_independent.py` from draft PR 51, which is not in this checkout | `codes/verify_codes.out` |
| `oeis/verify_all.py` | the 211 recurrence certificates | Yes (`CertError`, exit 1) | Yes, with and without `-O`. 105 of 105 rejected | `oeis/test_corrupt.py`, `oeis/state/test_corrupt.log` |
| `oeis/spot_proof.py` | third proof of 46 entries | Partly. Exit 1 if an entry is not proved. Exit 0 when no entry is chosen. It never compares the starting index | No | `oeis/spot_proof.out` |
| `oeis/scripts/lemma_check.py` | the window lemma on random systems | Yes (`SystemExit`) | No | `oeis/state/lemma_check.log` |
| `oeis/scripts/check_eleven.py` | OEIS status of the eleven controls | No. Print only | No | `oeis/state/check_eleven.log` |
| `square/verify.py` | the 238 square-law proofs | Yes (`Reject`, exit 1) | Yes, with and without `-O`. 73 of 73 rejected | `square/test_corrupt.log`, `square/test_corrupt_O.log` |
| `square/test_theory.py` | the symmetry and the decomposition | No. It uses `assert`, so `-O` removes the checks | No | none |
| `converge/oeis_structure.py` | factors the polynomials | No. Print only | No | none |
| `cc/verify_rational.py` | central configurations, exact rationals | Yes (`SystemExit`, REJECT) | Yes, with and without `-O`. Seven kinds | `cc/corrupt_tests.out`, `cc/state/corrupt_tests.sh` |
| `cc/cert_arb.py` | central configurations, ball arithmetic | Yes (`SystemExit`, FAIL) | Yes, under `-O`. One kind, a moved centre | `cc/corrupt_tests.out` |
| `cc/spot_cc.py` | equation residuals, numerical | No. Print only | No | none |
| `cc/compare_lit.py` | match to published tables | No. Print only | No | `cc/compare_n*.out` |
| `incentre/elastic_indep.py` | elastic constants, exact | Yes (`SystemExit`, exit 1) | Yes, under `-O`. A target changed by 1% | `incentre/out_corrupt.txt`, `threads/reports/incentre.md` line 38 |
| `incentre/fold_indep.py` | the fold, exact | Yes (`SystemExit` through `elastic_indep.check`) | Yes. A flipped sign (`--corrupt`). `-O` not recorded | `incentre/out_fold_corrupt.txt` |
| `growth/verify/levels_check.py` | one-level count, numerical | Yes since commit a61e289. At cbfa5a6 it had no raise and exited 0 on a mismatch | No. `threads/growth.md` runs it without `-O` | `growth/verify/levels_check.out` |
| `growth/verify/stack_check.py` | stacked levels, exact | Yes (`SystemExit`) | No | `growth/verify/stack*.out` |
| `growth/verify/lower_bound_hp.py` | lower bounds of 26 and 87 | Yes (`CheckFailure`) | No | `growth/verify/demo_d5_n9.lower.out`, `growth/verify/demo_d8_n21.lower.out` |
| `growth/verify/dump_taylor_points.py`, `growth/thread/check_taylor.py`, `growth/thread/validate.py` | points near the flat point, numerical | No. Print only | No | none |
| `kflat/verify/quartic27_check.py` | the quartic with 27 real critical points, exact | Yes (`CheckFailure`) | No | `kflat/verify/quartic27_full.out`, `kflat/verify/quartic27_short.out` |
| `kflat/kelvin_check.py` | the inversion rule, numerical | No. It prints both sides | No | `kflat/kelvin_check.out` |
| `kflat/thread/certify.py` | critical points of the model, ball arithmetic | No. It prints a count | No. Its controls are in `kflat/thread/negcontrol.py`, with no saved output | none |
| `geometry/wall_graph.py` | wall tracing | No. It prints the number of failures | No | none |
| `three/verify_arb3.py` | re-check of the three-charge certificate | Yes (exit 2) | Yes, under `-O`. Three kinds | `three/run_corrupt.sh`, `three/out/corrupt_equi.log` |
| `three/run_cert3.py` | primary three-charge certificate | Partly. Exit 1 only when phase A fails. Otherwise it prints NOT PROVED and exits 0 | No | none |
| `three/verify_pairs_arb3.py` | sampled pair check | No. It prints SOME UNRESOLVED and exits 0 | No | none |
| `three/l7_check.py` | lemma L7, numerical | No. Print only | No | none |
| `accel/check_transcription.py` | the hand-typed table | Yes (exit 1) | Yes. Three edits rejected. `-O` not recorded | `accel/outputs/corruption_tests.txt` |
| `accel/repro_repo_numbers.py` | the repository's numbers | Yes (exit 1) | Yes, under `-O`. One changed value | `accel/outputs/corruption_tests.txt`, `threads/reports/accel.md` line 55 |
| `gravity/t0_checks.py` | model sanity, and two corrupted data tables | Yes (`SystemExit`) | It is a harness. It runs `t6` and `t3` on corrupted tables under `-O` and raises if they miss it. The guard in `t6` only prints. It reads `sources/`, which is not in this checkout | `gravity/t0_checks.out` |
| `neutrino/check_numbers.py`, `neutrino/n3_efe_check.py`, `fabric/fabric_numbers.py` | arithmetic and formula checks | No. Print only | No | the `.out` beside each |
| `converge/codes_stats.py`, `converge/unified_check.py` | statistics and a fit | No. Print only | No | none |

Copies under `state/` are not listed again. They are `l2288/state/v12/certify12.py`, `l2288/state/v12/certify12_arb.py`, `gravity2/state/t0_checks.py` and the older `charges/state/out/indep_count_v1.py`. The other programs under `checks/` search, build, fit or plot. They give no verdict on a claim, so they are not counted as checkers.

## Summary

The table covers 57 programs: 56 under `threads/checks/` and the external `verify_arb.py`.

| Raises on failure | Programs |
|---|---|
| Yes | 25 |
| Partly | 3 |
| No, print only or `assert` | 29 |

| Corrupted-input run in the record | Programs |
|---|---|
| Yes, under `-O` | 10 |
| Yes, `-O` not recorded | 5 |
| Yes, without `-O` (`verify_arb.py`) | 1 |
| Stated in a note, no saved output (`l2288_independent.py`) | 1 |
| The harness of such a run, under `-O` (`crosscheck.py`, `t0_checks.py`) | 2 |
| None | 38 |

- 9 programs both raise on failure and have a saved run under `-O` against corrupted input: `indep_count.py`, `certify.py`, `verify_all.py`, `square/verify.py`, `verify_rational.py`, `cert_arb.py`, `elastic_indep.py`, `verify_arb3.py` and `repro_repo_numbers.py`. The tenth run under `-O` is of `laman_count.py`, which only prints.
- 10 programs raise on failure but have no corrupted-input run in the record. They are `certify_arb.py`, `edge_frame_independent.py`, `certify12.py`, `certify12_arb.py`, `verify_codes.py`, `lemma_check.py`, `levels_check.py`, `stack_check.py`, `lower_bound_hp.py` and `quartic27_check.py`.
- So the sentence "every checker raises an error and was run under `-O` against corrupted input" is wider than the record. `threads/README.md` and `threads/convergences.md` now name the nine and say the rest do not meet it.

## Runs made during the review, not in this pull request

The review record (`pr58-addendum/findings.json` on its own branch) reports more runs. A reviewer rejected five corruptions of the 2,288 certificate with `l2288_independent.py`, also under `-O`. A reviewer ran a negative control of `quartic27_check.py`. The lead reviewer ran `stack_check.py` under `-O` on clean input. None of these outputs is saved in this pull request, so the table above does not count them.
