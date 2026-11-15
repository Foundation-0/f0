# Overwrite and lost-work scans

These are the read-only scans behind the 14 November 2026 findings in `REPO-PROTECTION.md` and
Foundation-0/f0#42. They work on local mirrors and change nothing on GitHub.

## Run

```
scripts/org/scan/mirror_org.sh --org Foundation-0 --dir mirrors          # blobless mirrors with PR refs
scripts/org/scan/list_prs.sh   --org Foundation-0 --dir mirrors --out lists

export SCAN_EXCLUDE=project-asma                                          # optional, comma-separated
python3 -I scripts/org/scan/classify_commits.py mirrors commits.json
python3 -I scripts/org/scan/forensics.py        mirrors lists/merged.tsv forensics.json
python3 -I scripts/org/scan/stale_base.py       mirrors stale_base.json
python3 -I scripts/org/scan/lost_units.py       mirrors lost_units.json
python3 -I scripts/org/scan/unlanded.py         mirrors unlanded.json lists/closed_unmerged.tsv lists/open.tsv
```

Each script prints a summary and writes the full result as JSON. Every date they print is UTC.
Run a script with no arguments to see its usage. The first run on a large organisation
fetches many file contents on demand, so it is slow. Keep at most two transfers per repository running
at once.

## What each scan finds

| Script | Question | How |
|---|---|---|
| `classify_commits.py` | How did each commit reach the default branch? | Each first-parent commit is a PR merge, squash or rebase, a pushed PR head, a direct API commit, or a direct push. It matches subjects, `refs/pull/*` and author identity. |
| `forensics.py` | Is every merged PR's content still on the default branch? Did a commit delete lines that another commit added shortly before? | Lost merges: the PR head is an ancestor, a squash with `(#N)`, or patch-equivalent. Clobbers: `git blame` on every deleted line, flagging lines added by a different commit within 48 hours. Moved or reflowed lines are excluded. |
| `stale_base.py` | Did a commit write a file from an old copy and overwrite the edits in between? | For each changed file, the new version is compared with earlier versions. It flags commits whose result is closer to an older version than to the one they replaced. Delete-then-recreate counts as a rewrite. |
| `lost_units.py` | What named units existed on the default branch and are gone everywhere today? | It inventories Python defs and classes, Lean declarations, claim IDs, Markdown headings and whole files, and records the commit that removed each one and its message. |
| `unlanded.py` | Which branches and closed, unmerged PRs hold file versions that never reached the default branch? | It compares every blob ever on the default branch with each branch and PR head. |

## Reading the results

These are candidates, not verdicts. In the 14 November run, most large deletions were deliberate
rewrites, such as a regenerated table or a second draft. Before calling something lost, read the commit
and check that the content is not somewhere else today. `find_force_pushes.sh` (an owner) and
`find_lost_local.sh` (each agent machine) cover what these scans cannot see: commits removed by force
pushes, and work that was never pushed.
