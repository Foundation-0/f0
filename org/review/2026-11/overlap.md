# Overlaps and overwrites, organisation scan (O1)

Scope: all 35 public Foundation-0 repositories, mirrored
2026-11-15. Default-branch heads match the H1 pins in
`h1-method.md` unless a repository moved that day. Facts from
runs carry [F]. Judgments carry [I]. Candidates here are not
verdicts: read the commit before calling work lost.

## How this was run

Mirrors and PR lists come from the scripts on draft 40 at
`9f98863` (`scripts/org/scan/`), run from a local copy.
They stay homed there. This folder commits only the extra
tool this run added, `tools/o1_extras.py`, plus outputs.

```
bash scan/mirror_org.sh --org Foundation-0 --dir mirrors
bash scan/list_prs.sh --org Foundation-0 --dir mirrors --out lists
python3 -I scan/classify_commits.py mirrors o1-commits.json
python3 -I scan/unlanded.py mirrors o1-unlanded.json lists/closed_unmerged.tsv lists/open.tsv
python3 -I scan/lost_units.py mirrors o1-lost-units.json
python3 -I scan/stale_base.py mirrors o1-stale-base.json
python3 -I scan/forensics.py mirrors lists/merged.tsv forensics-full.json
python3 tools/o1_extras.py --mirrors mirrors --lists lists --inventory inventory.csv --h2-branches branches.csv --out .
```

The lost-units and stale-base scans complete this set,
with forensics beside them. Their sections below carry
their own run lines and limits. Force pushes and never-pushed work stay out of
reach here by design. Owners and operators cover those with
`find_force_pushes.sh` and `find_lost_local.sh` in draft 40.

## How commits reached the default branch

Across 520 first-parent commits on default branches: [F]

| Route | Commits |
|---|---|
| PR merge | 197 |
| PR squash | 73 |
| Direct API commit | 188 |
| Direct push | 59 |
| Direct merge | 3 |

So 250 of 520 (48 percent) landed with no pull request. [F]
Two repositories hold most of it: gravity 85 direct of 98,
and exoplanets-frontier 79 direct of 79, with no PR merge in
its history at all. [F]

The issue body counts 162 direct commits from 11 to 13
November (84 gravity, 78 exoplanets-frontier, 50 of them
tagged skip ci). This rerun finds 164 in that window: 84 in
gravity, 79 in exoplanets-frontier, 1 in vitruvian3d, and
the same 50 skip-ci subjects, all in exoplanets-frontier.
[F] The 14 November count stands, off by one exoplanet
commit and one vitruvian3d commit outside its two-repo
scope. Full rows sit in `o1-commits.json`.

f0 itself: 25 first-parent commits, 7 direct, all before
the November window. Its detail sits in `overlap-f0.md`. [F]

## Superseded pull requests: gravity set checked

The plan asks whether each change in a superseded PR reached
its replacement. For gravity 8, 9, 11, 12, 13 and 15, replaced
by 21 and 23 to 27 on 14 November, every superseded head is
an ancestor of current main, and no file version from those
heads is missing from main history. [F] Method: the blob
test in `unlanded.py`, rerun per head against all blobs that
ever sat on main. Nothing to recover in that set. Later
edits on main can still have overwritten lines in place.
The stale-base and forensics sections cover that risk.

Org-wide, 17 PRs stand closed and unmerged. Eight carry file
versions that never reached main: [F]

| Closed PR | Files | Lines | Note |
|---|---|---|---|
| project-asma 73 | 3 | 17,808 | three docx reports |
| incentre-lattices 99 | 8 | 7,876 | same work as branch in R3 |
| incentre-lattices 29 | 8 | 3,121 | continuous-fcc paper draft |
| project-asma 18 | 11 | 2,195 | pilot-001 contracts |
| project-asma 33 | 7 | 641 | repo-standard scaffold |
| project-asma 83 | 2 | 445 | Lean proofs, certificates |
| project-asma 50 | 3 | 410 | first-run runner |
| exoplanets-frontier 7 | 1 | 115 | cool_vet.py, same head as R2 |

Recovery for any of these, if wanted: open a fresh PR from
`refs/pull/<n>/head` in its repository, or cherry-pick with
authorship kept. Whether each was dropped on purpose needs
its author or an owner, per row. This scan does not decide.

## Open pull requests: merge state and shared files

167 open PRs were test-merged against their default branch
on 2026-11-15 (`o1-pr-merge.csv`). 133 merge clean and 34
conflict. [F] The conflicts concentrate:

- incentre-lattices: 24 of its open PRs conflict. Its
  October pile shares bookkeeping files: 21 open PRs touch
  `docs/review-ledger.md`, and 15 each touch
  `certificates/SHA256SUMS`, `certificates/selected-results.json`,
  `commitment/ROOT` and `commitment/SHA256SUMS`. [F]
- One each in cfrp-strengthening (7), exoplanets-frontier
  (6), f0 (30) and fractals (12). Three in math0 (1, 3, 4)
  and three in project-asma (65, 77, 78). [F]

88 files are touched by more than one open PR, across 14
repositories (`o1-pr-overlaps.csv`). Beyond incentre, the
widest is fractals `README.md` in 8 PRs. [F] For S1 and the
backlog work, incentre-lattices is the condensation case:
its PRs cannot land in any order without rebasing the
shared certificate and ledger files each time. One
condensed PR per the backlog policy fits it best. [I]

## Branches: classified

296 non-default branches were test-merged
(`o1-branches.csv`). Three classes matter. [F]

**Already on the default branch (97).** Most have zero
commits ahead: merged branches never deleted. Seven carry
commits ahead whose content is already on default, which
confirms the seven named in the H2 check on issue 42:
cfrp-strengthening `claude/zealous-mendel-s7z7hk`,
incentre-lattices `fold-dof-wording` and
`fold-search-step-bound`, project-asma
`smith/asma-occurrence-inventory-87`, and virtual-human
`auto/E-deterministic-subgraph`,
`docs/asma-research-foundation-20261105` and
`helix/ovarian-parameter-ledger-fe7d`. [F] Deleting any of
the 97 loses nothing. Deletion stays an owner step, after
retargeting dependents.

**Unlanded work, merges clean.** Among branches with no
open PR in the H2 map, these add content and merge clean:
the Phase 2 rows R2, R3, R6, R7 and R8 in `status.md`, plus
gaia-dr4 `prep/gaia-dr4-tasks` (R1, still blocked on the
prep-or-slices choice). Their next steps sit in the
recovery queue. Two rows in the scan, f0 `review/H1` and
`review/H2`, gained PRs 45 and 46 after the H2 map was
drawn. Read them as open work, not stranded. [F]

**Unlanded work, conflicts.** The rest need hand work
before any restore: 17 branches in incentre-lattices from
12 to 13 October (the `codex/` and `fix/` families, plus
`prior-art-sources`, R5), gfq-codes `axiom/delsarte-sweep`
(landed in substance, per issue 42, but main edited the
same files since, so the test merge conflicts), the three
virtual-human branches in R9 (all conflict, so R9 restores
need conflict work, not plain PRs), and a tail in
project-asma whose biology stays out of scope here. [F]
Full rows with ahead counts and dates sit in the CSV.

189 branch or closed-PR refs carry file versions that
never reached a default branch (`o1-unlanded.json`). [F]
Most are ordinary open work. The largest by lines is math0
`claude/math-capabilities-showcase-961iya` behind open PR
math0 1, which conflicts: 656 files. Its size makes it the
first stranded-work call outside the Phase 2 list. [I]

## Copies across repositories

Within H1 research files, 7 identical blobs sit in more
than one repository (`o1-copies.csv`). All are the October
scouting reports under `notes/reports/`, copied into new
repositories at creation. [F] 21 paths exist in more than
one repository with different blobs (`o1-samepath.csv`).
Most are expected per-repo files (README, .zenodo.json).
The ones that can drift in substance are the same scouting
reports: `notes/scouting-2026-10-19.md` differs across four
repositories, and `notes/reports/` files match in some
repositories and differ in others. [F] For S1: give the
scouting reports one home and link, or accept per-repo
copies as frozen snapshots and say so in each. [I]
Near-identical text beyond shared paths was not scanned.
That limit is recorded here, not filled with a guess.

## Lost units: named things gone from every branch

`lost_units.py` ran 14m36s over the mirrors. It finds 128
named units (Python defs, Lean declarations, claim IDs,
Markdown headings, whole files) that sat on a default
branch once and exist nowhere today (`o1-lost-units.json`).
54 carry a removing message that names a removal, rename or
refactor. 74 do not: 61 headings and 13 Python defs. [F]

The scan re-derives the one confirmed overwrite in issue
42 from scratch. Four defs added by the refactor
`fcef36e23` in gravity `wave4_unified_field_solver.py`
(`solve_bvp`, `solve_tridiag`, `check_c09`, `check_c10`)
were removed by `e855db6b4` eight hours later, with no
removal word in its message. [F] Classification: confirmed
overwrite, same as the issue body. Recovery, if R10 is
wanted: `git show fcef36e23:wave4_unified_field_solver.py`
in gravity carries the refactor, and reapplying it is one
PR against main.

The other unexplained losses concentrate in gravity (50,
mostly headings removed by four claim-reconciliation
commits on 12 November) and exoplanets-frontier (6 headings
when the Phase 3 report replaced the Phase 2 one in
`926675167`). [F] Classification: deliberate rewrite
candidates. Each removing commit rewrites the record it
touches, of the kind the scan README warns about. No lost
Lean declaration or claim ID appears in the output at all.
Read the four gravity commits before S1 treats any heading
loss as final. [I]

## Stale-base writes: one in the whole organisation

`stale_base.py` ran 7m44s. It flags exactly one commit org
wide (`o1-stale-base.json`): gravity `e855db6b4` writing
`wave4_unified_field_solver.py` from the older `2913956d8`
version (similarity 0.56) over the refactor it replaced
(0.12), with 104 lines still missing today. [F] That is
the same overwrite the lost-units scan and the issue body
name. Three methods agree on one event, and no second
stale-base write exists in any default-branch history
scanned. Classification: confirmed overwrite, one only.

## Forensics: lost merges and fast deletions

Results sit in `o1-forensics.json`, with clobber lines
aggregated per commit. Rerunning `forensics.py` gives
full line detail.

**Lost merges: 2 of 285 merged PRs.** [F]

- cfrp-strengthening 15 merged into the branch of PR 7
  (`checker-issue-4`), not into main. None of its 7 files
  matches main today. This is R11 in the recovery queue:
  land 7, or retarget the fixes to main. Confirmed.
- incentre-lattices 28 (continuous cab-to-fcc motion)
  squash commit `98d5aec` sits only on branch
  `codex/complete-result-commitments`. Main carries the
  same title as `abeb94b` under PR 33. 6 of its 17 files
  match main today. Classification: re-landed in evolved
  form, candidate only. A tree diff of `98d5aec` against
  `abeb94b` settles whether anything unique remains.

**Fast deletions (clobbers): 9,029 line records in 238
commits** that deleted lines another commit added within
48 hours. [F] The bulk is the delete-then-recreate working
style the issue describes: 26 commits in
exoplanets-frontier hold 4,891 records, many titled Delete
or Remove before an upgrade, and one data purge
(`4059fc1e4`) holds 3,602. Merge commits that resolve
overlaps add more. The only clobber already classed as an
overwrite is `e855db6b4` above. The rest read as churn
inside fast-moving repositories, not losses. [I] Any S1
move out of gravity or exoplanets-frontier should still
diff against the branch tips in `o1-unlanded.json` first.

One queue correction falls out of this scan: proven-commons
PR 7 from branch `claude/brave-knuth-x3bkfi` merged on
28 October. The branch then gained two sync-fix commits
(`6fac26b`, `fa8792e`). R6 is a restore of those two
commits only, not of the whole branch. [F]

## What S1 gets from O1

- One confirmed overwrite in the org, with its recovery
  commit named. No second stale-base write exists.
- Direct-to-main work is now counted per repository.
  exoplanets-frontier has no PR history to preserve.
  Its structure call can treat main as the only record.
- incentre-lattices cannot land its queue file by file.
  21 PRs share one ledger file. Condense first, then move.
- 97 branches carry nothing new. Deleting them is safe
  once dependents are retargeted. 40 branches carry
  unlanded work with no open PR: the recovery queue plus
  the incentre October family and math0 PR 1.
- Scouting reports live as copies in many repositories,
  already drifting. Pick one home or freeze the copies.
- Not covered here, by design: force-push losses (owner
  script in draft 40), never-pushed local work (operator
  script), near-identical files beyond shared paths, and
  superseded-PR fidelity outside the gravity set beyond
  the blob test in `o1-unlanded.json`.
