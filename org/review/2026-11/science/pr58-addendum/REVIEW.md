# Review record for pull request 58

> Frozen record. This file is the audit of pull request 58 as it stood at a61e289 (15 November 2026). It is kept as written and is not updated for later commits on `review/F7-threads`; whether those commits close each item is for the re-review of pull request 58 to record.

15 November 2026. Review of the F7 threads pull request at head cbfa5a6. One later commit, a61e289, arrived during the review. The lead reviewer re-ran its changed programs. Item 3 below is updated for that commit. The other items are unchanged by it.

Verdict: request changes. Five blocking items are listed below. The synthesis in findings.json lists six [BLOCK] entries: review passes 2 and 9 each filed the recurrence-label finding, and this page merges the two into item 2. All five are labelling, wording, or missing files. No proved result that was re-run failed to reproduce.

The complete machine record sits in findings.json beside this file. It holds every finding, evidence line, and open item from twelve review passes, word for word. This page is the readable form of that record.

## How the review ran

Ten passes covered one thread each. One pass then tried to break the surviving claims with fresh corrupted inputs. One pass merged the results. The lead reviewer also re-ran the charge and growth checkers alone, in the point-charges repository.

Every exact checker that was re-run reproduced its claimed output. Box counts and zero centres match the saved outputs. Corrupted inputs are rejected under python3 -O, with the exceptions named below.

## Blocking items

1. unit-point.md line 38 gives 868 at every tested eps. The data file certray_868.json in this pull request gives 856 at eps 0.01 and 860 at eps 0.003. The sentence is false against the shipped data.

2. The recurrence verdicts disagree inside the pull request. README.md gives VERIFIED for 46 and REPRODUCED for the rest. recurrences.md line 41 gives VERIFIED for all 211. square-law.md line 86 adds 27 PROVEN. PROVEN is defined only in pull request 55, which is not merged.

3. README.md line 90 says every checker in this pass raises an error and ran under -O on corrupted input. At cbfa5a6 levels_check.py had no raise and exited 0 on a mismatch.

Commit a61e289 fixes that program and adds stack_check.py. The lead reviewer ran stack_check.py under -O. It proves 41 points at D=6 in exact arithmetic and raises on failure.

The sentence in README.md still covers print-only programs such as laman_count.py. verify_arb.py also ran without -O, by the note's own account. The universal wording remains wider than the evidence.

4. three-charges.md line 21 says the structural lemmas are proved by hand in checks/three/NOTES.md. That file holds one-line statements. A reviewer rebuilt the missing derivations and found them sound. The derivations are not in the record, so the proof is not self-contained as archived.

5. The gravity and neutrino programs cannot be re-run from this checkout. They read a sources tree that STATE-NOTES.md excludes. Some paths predate a folder move. n4_window.out has no program. It is the only support for the 9 eV end of the fermion window.

## Major items, grouped

Missing files: REPORT.md, cited for the derivative bounds in indep_count.py, is absent. Two reviewers derived the bounds again. Both constants are correct. The input certificates for three to seven charges are also absent. A reviewer rebuilt them from corrupted copies and matched the saved outputs exactly.

External checkers: one exact program for the four-charge result lives in the point-charges repository. The lead reviewer ran its corrected form from point-charges pull request 22. All three configurations pass under -O. The claim inside this pull request still rests on one in-tree exact program until that file is copied in.

Independence wording: two of the three exact checkers for 2,288 share one proof template and its constants. The ball-arithmetic checker is the separate method. All three 880 programs implement one published recursion. The code finder filters its output with the first checker, so that pass proves nothing alone.

One recurrence: proofs hold 238 files and the verifier log holds 237 passes. The missing entry is A269766. Three more entries were checked only by the prover's own engine. spot_proof.py can also exit 0 on empty input, and it never asserts the starting index its note claims.

Fermion window: two of its three numbers come from the same 51 clusters the third is tested on. The per-system correlation in the saved test output is near zero and is never quoted. One system reaches the 100 eV search ceiling in three of four correction sets and is never named.

Growth constant: the exponent argument is labelled a sketch, and that label fits. The constant 0.87 in growth.md line 44 and the crossing near 160 charges rest on a flat family that is solved numerically, not proved. The exact lower bounds of 26 and 87 have their own programs.

Wording counts: central-configurations.md line 23 says both programs reject 15 kinds of corrupted input. The count is seven kinds for one program and one kind for the other, across 15 run lines. reports/cc.md states this correctly.

## Minor items

indep_count.py rejects every coplanar configuration, including two charges with one balance point. A count stored as text gives a self-contradictory mismatch line. Both faults reject input. Neither accepts a false claim.

The remaining minor items are single numbers or labels in convergences.md, flat-centres.md, relational-geometry.md, and the thread reports. Each one is listed with its location in findings.json.

## What reproduced

Four charges: exactly 11, three configurations, positive charges. Counts for three to nine charges: 4, 9, 24, 29, 44, 49, 64. Growth lower bounds: 26 and 87. A harmonic quartic: all 27 critical points real.

Rigid graphs: 2,288 real realizations exist. Generic counts 880 and 2,288 reproduce. Codes: 1,519 certificates pass two exact formulas. Improvements beyond the tables' own closure total 2,418.

Recurrences: 211 pass two programs, 46 pass a third. Central configurations: at least 20, 42, and 67 classes, with completeness not claimed. Lattice elasticity and the fold hold in dimensions 2 to 9.

Gravity: the transcription check passes. Six table programs reproduce byte for byte. The negative verdicts in the thread notes match the outputs.

Hygiene: the manifest verifies 1,437 of 1,437 files. Nothing outside the threads folder changes. No secrets or personal paths appear. The prose check passes on all 24 top-level notes.

## Merge order

Pull requests 51, 55, and 56 hold two cited checkers, the verdict words, and the thread list. File overlap with this pull request is zero. Land those three first so no citation points outside the tree.

## Not re-run

External items stayed external: the two checkers on pull request 51, the authors' lnumber program, the published gravity tables, the live code tables, and the OEIS source text. Literature and novelty claims were not checked in any thread.

The full pair step of verify_arb3.py and the full rc100 fit were sampled, not run whole. A269766 was not verifier-run by any reviewer. Each sampling limit is recorded per pass in findings.json.
