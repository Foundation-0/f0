# Overlap map for f0 (O1, f0 slice)

Method: for each open pull request, `git merge-tree --write-tree
origin/main <head>` at main `6ea3a0b`, plus the changed-file list
against main. Run 2026-11-15. [F]

## Merge state of the 13 open pull requests

| PR | Head | Merge with main | Files |
|---|---|---|---|
| 41 | f20ef73 | clean | 4 |
| 40 | 9f98863 | clean | 14 |
| 39 | 66359b2 | clean | 7 |
| 37 | 8dd1380 | clean, wrong base | 1 |
| 36 | f6d4212 | clean | 1 |
| 35 | 22b6f89 | clean | 4 |
| 30 | 930ca51 | conflicts | 10 |
| 28 | 0b2471c | clean | 15 |
| 27 | 72ab53d | clean | 2 |
| 20 | 16b4473 | clean | 5 |
| 11 | d27fe69 | clean | 4 |
| 7 | 7b5d3c7 | clean | 2 |
| 6 | 0397b84 | clean | 31 |

Pull request 37 targeted the branch of pull request 36, not main.
That breaks the no-stacks rule in issue 42. Deleting the base
branch would close 37. It was folded into 36 first instead: 37
merged into 36's branch on 2026-11-15, so no retarget is needed.

## Files touched by more than one open pull request

| File | Pull requests | Risk |
|---|---|---|
| `.github/workflows/prerender.yml` | 35, 30 | second one rebases |
| `.github/workflows/pages.yml` | 35, 30 | second one rebases |
| `scripts/prerender.mjs` | 35, 30 | check both edits |
| `deep-fields/scouting/combinatorial-planning-verified-bar.md` | 36, 37 | same report, two layers |

No other file repeats across the 13. The scouting reports in
28, 39 and 41 each add new folders and collide with nothing. [F]

## Branches beside main

| Branch | State | Last commit | Suggested step |
|---|---|---|---|
| claude/dazzling-shannon-yi2pt1-2 | merged | 2026-10-19 | delete after owner confirms |
| claude/f0-forum | merged | 2026-10-19 | delete after owner confirms |
| claude/relaxed-faraday-qghpbi | merged | 2026-10-18 | delete after owner confirms |
| claude/sleepy-pasteur-k5knht | merged | 2026-10-18 | delete after owner confirms |
| foundation0 | merged | 2026-10-15 | delete after owner confirms |
| foundation0-logo | merged | 2026-10-15 | delete after owner confirms |
| claude/beautiful-sagan-ssa4lh | 1 commit, superseded | 2026-10-19 | delete, per issue 42 |
| claude/affectionate-ride-rezj73 | 2 commits, forum proposal | 2026-10-27 | keep until issue 12 is decided |

The other 13 branches each carry one open pull request. [F]
Merged means the branch tip is an ancestor of main, checked with
`git merge-base --is-ancestor`. [F] Deleting stays an owner step
in this run. Before any delete, retarget dependent pull requests:
only 37 depends on another branch, and that branch (36) is live. [F]

## Overwrites inside f0

No force-push or lost-commit candidate was found in f0 itself.
The scan covered all branch tips against main on 2026-11-15.
Every merged pull request head reaches main. [F]

The org-wide overwrite scan (O1 in full) needs the scripts in
pull request 40 at `9f98863` under `scripts/org/scan/`. They are
not on main yet. Until 40 lands, run them from that branch in a
separate clone. Do not copy them into this folder: one home per
tool. [I]

## Recovery queue outside f0 (O3 checks)

Issue 42 orders the stranded branches across the org, gaia-dr4
first, before the archive outage on 2026-11-25. Those restores
belong in their own repositories, one pull request each against
main, opened by an account with Write there.

This run checked the two most urgent branches from fresh clones
on 2026-11-15 and opened neither. The reasons differ.

**gaia-dr4 `prep/gaia-dr4-tasks` at `5a53b3a`.** It still merges
clean with main `0110e1c`: 138 files, 20,036 lines added. [F]
But six steward pull requests (9 to 14) are already open in that
repository. Pull request 10 (`steward/task-2-preparation`)
shares 25 of its 30 files with the prep branch. [F] Opening the
prep branch whole would put two versions of the same work in
review at once. The next step sits with the gaia-dr4 authors:
pick the prep branch or the task slices, then open one path
with a full preflight. The 2026-11-25 deadline makes this the
first call in the queue. [I]

**exoplanets-frontier `orda-aska-patch-1` at `35a77f7`.** It
merges clean with main `3bc0163`. [F] On main, `cool_vet.py`
fails to parse: `python3 -m py_compile` exits 1 with an
unterminated string at line 2. On the branch it exits 0. [F]
The branch does more than fix the parse. It also changes the
target count from 14 to 10 in the function, the call and the
report headings. [F] `cool_vet.py` diff, main to `35a77f7`.
That count change alters which candidates get vetted, so the
restore needs a record-lane review that names both changes.
It must not land as a plain syntax fix. [I]

Access for both restores is in place: the posting account holds
admin on gaia-dr4, exoplanets-frontier, proven-commons and
incentre-lattices. [F] Each restore still needs its own
preflight in its own repository before review is requested.
The f0 rows above show the shape to copy.
