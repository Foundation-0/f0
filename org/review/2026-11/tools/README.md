# Review tools

Scripts that produced the November 2026 review files live
here, so every rerun command in this folder works from the
repository alone. The org scan scripts stay homed in draft
40 under `scripts/org/scan/`. They are run from there, not
copied here.

- `o1_extras.py` (draft for O1): branch test merges, open-PR
  test merges and shared files, cross-repository copies.
- `o2_run.py`: mechanical verifier runs (documented,
  optimised, empty folder), with exit codes and hashes.

Each script states its inputs in its header. Outputs land
in this review folder, one file per run product.
