# O2 verifier runs: method and headline results

Scope: the 159 `type=verifier` rows in H1 `inventory.csv`
(draft 45), run 2026-11-15 in fresh clones at the heads
pinned in `h1-method.md`. Mechanical runs only. Nothing
here judges whether a claim is true. That is F2 work.

## How to rerun

```
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python numpy scipy sympy pandas matplotlib pyarrow mpmath
.venv/bin/python org/review/2026-11/tools/o2_run.py --inventory inventory.csv --repos repos --out reproduction-org.csv --timeout 120 --python .venv/bin/python
```

Setup, run from a checkout of this branch with `inventory.csv`
and `repos/` at its root: copy `inventory.csv` (the H1 verifier
list) from draft 45, and build `repos/<name>` with draft 45's
`clone-all.sh` so each clone sits at the head pinned in its
`h1-method.md`. The runner is `org/review/2026-11/tools/o2_run.py`
in this folder; it records the interpreter and paths exactly as
invoked (the `command` column is verbatim) and absolutizes them
only to execute. The committed `command` column was rewritten
after the run, on 26 November 2026, from the absolute
interpreter path the first runner recorded to the as-invoked
`.venv/bin/python` (and, in empty-cwd rows, the clone-relative
script path); no row was re-run and no other column changed.
Environment for the recorded run: CPython 3.12
venv with the packages above, macOS. Across all modes the CSV
records DEP-MISSING with the module astropy (3 rows), flint (3)
or jax (3), plus `vh` (24) and `pilot001_first_run` (6), which
are the repositories' own packages, not missing third-party
dependencies.

## Modes and classes

Per Python verifier (154): documented (`python <file>`, no
arguments, repo root), optimised (`python -O`), empty-cwd
(same file from an empty folder). After each root run the
runner records whether the tree changed, then restores it.
Corrupted-input probes need per-verifier knowledge, so all
159 rows record MANUAL for F2. Five files are not Python
(3 R, 1 mjs, 1 C) and record NOT-RUN.

Classes: PASS0 (exit 0), FAILNZ (nonzero), NEEDS-ARGS
(argparse exit 2), DEP-MISSING, TIMEOUT (120s), NOT-RUN.
A bare run is a blunt instrument. FAILNZ here means the
bare command failed, not that the claim fails. Causes need
a per-verifier read, which belongs to F2.

## Headline counts, documented mode

| Class | Verifiers |
|---|---|
| PASS0 | 119 |
| FAILNZ | 12 |
| NEEDS-ARGS | 9 |
| DEP-MISSING | 13 |
| TIMEOUT | 1 |
| NOT-RUN | 5 |

Full rows sit in `reproduction-org.csv`: exit code,
seconds, output hash, assert count, dirtied flag. [F] An
empty output hash means the run printed nothing (24 PASS0
and 3 TIMEOUT rows).

Per repository (PASS0 of total, documented): [F]

| Repo | Pass | Repo | Pass |
|---|---|---|---|
| cfrp-strengthening | 1/1 | math0 | 6/7 |
| exoplanets-frontier | 1/3 | nhanes-bioimpedance | 2/5 |
| f0 | 3/3 | point-charges | 0/2 |
| finite-state-proofs | 2/2 | project-asma | 35/44 |
| formal-claims-audit | 1/1 | proven-commons | 0/2 |
| fractals | 1/2 | rigid-realizations | 5/5 |
| gfq-codes | 14/16 | virtual-human | 1/10 |
| gravity | 22/25 | vitruvian3d | 14/16 |
| incentre-lattices | 11/15 | | |

project-asma rows ran mechanically like the rest. Its
claims stay reference scope per rule 8 in issue 42.

## Signals worth F2 time first

**40 verifiers pass under `-O` while carrying bare
asserts.** [F] Under `-O` Python drops asserts, so any
check that lives only in an assert cannot fail there.
The heaviest: math0 cubic-frames verify (30 asserts),
gravity wave11-12 check (21), gravity value-assessment
check (20). The CSV `asserts` column ranks them all.
Whether each assert guards a claim needs reading. [I]

**28 verifiers write files on a bare run** (43 mode
rows across all modes; a 29th, gravity wave11-12
`check.py`, dirties only under `-O`), mostly gravity
research probes and two exoplanets-frontier vetters. [F]
A check that rewrites
its inputs cannot double as a compare step. The
`dirtied_tree` column names them.

**One timeout:** incentre-lattices
`results/fold-close-packing/verify.py` exceeds 120s in
every mode. [F] Long exact checks need a stated budget,
not a shorter leash here.

**Spot-checked failures, mechanical causes only:**

- proven-commons `scripts/audit.py` needs `lake update`
  before it can audit. Setup step, not a verdict.
- incentre `chk_independent.py` reads `sys.argv[1]` and
  dies without it. Read its FAILNZ row as needs-args.
- virtual-human verifiers import the repo package `vh`.
  They need the repo root on the path, then arguments
  such as `--asma-root`. The 9 DEP-MISSING rows there
  record the bare invocation, not broken code.
- gravity wave11-12 `check.py` asserts file hashes
  against a pinned older head and fails on
  `CHANGELOG.md`. Pin drift since its review snapshot.
- nhanes-bioimpedance pilot verify recomputes values
  that differ from its certificate past the stated
  tolerance in this environment (for example fc_khz p99:
  the recorded run got 469.40258675 against cert
  469.40138875, tol 3e-06; the got value is
  environment-specific and moved on a rerun). [F]
  Environment or data drift can explain this. F2 to read.
- exoplanets-frontier `cool_vet.py` fails to parse on
  main, as O1 and issue 42 already record (R2).

## Limits

- No-arguments runs only. Verifiers whose documented form
  takes flags such as `--check` were not rerun in that
  form. NEEDS-ARGS and argv failures mark the gap.
- No corrupted-input mode in this pass. All MANUAL.
- One environment only. A second interpreter or pinned
  dependency set per repository could move several rows.
- Output text is hashed, not stored. Rerun a row to read
  its words. Numbers stated by verifiers were not compared
  against claims here. F2 owns that comparison.
