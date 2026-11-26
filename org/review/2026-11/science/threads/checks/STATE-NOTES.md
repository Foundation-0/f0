# State kept so that a result can be resumed or re-derived

15 November 2026. For each thread, the small files that a person needs to resume a search or re-derive a result were copied into `checks/<thread>/state/`. They are in addition to the programs and outputs already in `checks/<thread>/`. The whole set adds about 11.6 MB.

In text files, the absolute path of the working folder was replaced by the letter S. So the hashes of those copies differ from the archive copies. The `.npz` files are unchanged. The full archive stays outside the repository.

## What was copied

| Thread | Files | Bytes | What |
|---|---|---|---|
| l2288 | 89 | 7,067,083 | The saved solution states for the 2,288 point (`state_2288.npz`, `state_2288_b.npz`, `state_2288_c.npz`), the generic start (`l2288_generic.npz`), the L880 generic start, the last and best states of the final climb (`push2_DF1_last.npz`, `push2_DF1_best.npz`), the milestone snapshots, every certificate file for the intermediate counts, all logs, the search scripts that were not yet in the repository, the step logs, and the small files of the 12-vertex work. |
| cc | 67 | 767,432 | The merged census files for n = 8, 9 and 10 (`census_out/merged_n*.json`), every single-run census file with its log, the probe runs, the certificate test files, the chain logs and scripts, the corrupted test inputs and the verification and comparison outputs. |
| codes | 15 | 576,228 | The scan results `scan7.json`, `scan8.json`, `scan9.json` and their logs, the uncertified float candidates, the corrupted test certificates and the check outputs. |
| charges | 44 | 342,908 | All result files and logs from `out/`, the corrupted test inputs, the repository-format configs, the rerun scripts and the outputs of the repository verifier run under `python -O`. |
| cross | 66 | 2,497,318 | All of `out/`: the logs, the JSON results, the start files and the resumable `.npz` state that each push and each monodromy run writes. |
| laman | 9 | 8,217 | The remaining logs, the scripts that were not yet in the repository, and the header shim used to build the library without OpenMP. |
| oeis | 13 | 185,739 | The build, harvest, scan, census, verification and corruption-test logs, and the summary file. |
| incentre | 8 | 4,782 | The remaining output files and the reproduction logs of the repository verifiers. |
| accel | 1 | 6,803 | The second reading of the transcribed table (`rc100_xcheck.csv`) and its difference list. |
| gravity2 | 16 | 98,607 | The scripts and outputs that were not yet in the repository. |

## What was skipped, and why

Nothing was skipped without a reason below. No single file over 3 MB was found among the working files.

- **All threads, outside sources.** Pages, PDFs, tables and e-print archives downloaded from outside are not copied. `SOURCES.md` lists each with its size and sha256.
- **laman.** `lnumber_src/` holds the downloaded library archive, two Windows binaries, a compiled macOS library and the unpacked sources. These are a download and a build product. `repo_copy/verify_capco_laman.py` is a copy of a file from another repository. Its sha256 is in the report.
- **codes.** `table.json` (416 KB) is the parsed form of the downloaded tables. `parse.py` rebuilds it from the cached pages.
- **incentre.** `repro/repo/` is a full copy of another repository, used to rerun its verifiers. It is large and not ours. Its logs were kept.
- **accel.** `xcheck/*.png` are six zoomed page images made from the paper PDF, used in the second reading. The `tmp_corrupt/` folder is scratch and was marked for deletion in the report.
- **gravity2.** The `unified/` folder is not described in the thread report. It holds a table and scripts of another analysis, and was left out until its source is clear.
- **l2288.** About 64 further `.npz` files (18.8 MB, about 295 KB each) are intermediate search states: the best and last state of each run, the scaled starts, the multistart starts and the temporary files. The `v12/` folder holds work on a 12-vertex graph that the l2288 report does not describe. Its scripts, logs and the largest certificate (`cert12_3892.json`) were copied under `state/v12/`.
  Its 37 `.npz` states (73 MB) and one other certificate were left out for size. The final states and the certificates are kept, so the result can be rerun. A search can restart from `l2288_generic.npz` with `push2.py`.
- **cc.** `handback_draft.txt` is a draft of the final message and `chain.done` and `chain2.done` are empty markers.
- **reviewfix.** The draft pull request bodies and comments in `bodies/` and `orig/` are not copied. They are text for posting on GitHub. The seven changes themselves are commits on the review branches. The raw log file is not copied either.
- **Python caches** (`__pycache__`) and the cached copy of the virtual environment are never copied.

Two empty log files that backed no claim were removed after the team review: one in the central-configuration census output and one in the lattice reproduction logs. The counts above reflect that.
