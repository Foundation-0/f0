# Review tools

This folder carries the extra tool the O1 run added,
`o1_extras.py`, plus its outputs. Its limits, so a rerun knows
where the inputs come from:

- The five org scan commands in `../overlap.md` run from the
  scripts homed on draft 40 (pull 40) under
  `scripts/org/scan/`; they are not copied into this
  repository.
- `o1_extras.py` takes `--inventory inventory.csv` from the
  `review/H1` branch (pull 45) and `--h2-branches
  branches.csv` from the `review/H2` branch (pull 46).
  Neither file is on this branch, so its rerun command does
  not work from this folder alone.

- `o1_extras.py` (draft for O1): branch test merges, open-PR
  test merges and shared files, cross-repository copies. It
  states its inputs in its header. Outputs land in this
  review folder, one file per run product.

`o2_run.py`, the O2 mechanical verifier, is not on this
branch; it lands with pull 49. This branch carries this
`tools/README.md`.
