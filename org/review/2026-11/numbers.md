# H2 numbers for the decisions

Read on 15 November 2026 at 01:25 UTC, as ahrazzle, against the GitHub API and the Zenodo API. Counts cover the 35 public repositories only.

The snapshot is taken before this pull request and its H1 sibling existed, so neither branch nor either pull request is counted here. A later read will show two more branches and two more open pull requests. Repeat the method below and expect the numbers to move.

## The problem, item 5, refreshed

| measure | issue_14_nov | now |
|---|---|---|
| open pull requests | 164 across 29 repos | 166 across 29 repos |
| open PRs opened before 1 November | 115 | 115 |
| open issues | 121 | 122 across 24 repos |
| branch heads not reachable from the default branch | not counted | 204 (159 are the head of an open PR, 45 have no open PR; 7 of the 45 are already on the default branch in content) |
| Phase 2 branches holding work not on `main` | 13 | 13, all still present |

Open PRs by account: ahrazzle 127, orda-aska 25, zero-aska 6, abu-aska 4, mithrax-exo 4.

Open issues by account: zero-aska 72, ahrazzle 24, orda-aska 23, abu-aska 2, mithrax-exo 1.

The 14 November figure of 164 PRs is now 166, and the account totals moved by two for ahrazzle, which is the two review PRs opened on 15 November. The issue count moved from 121 to 122. The per-repository lists are in `open-prs.csv` and `open-issues.csv`.

### Branches

204 branch heads are not reachable from the default branch of their repository. 159 of them are the head of an open pull request, so they are not stranded work in the sense of the issue. 45 have no open pull request. 18 of those were touched on or after 1 November.

7 of the 45 have their content on the default branch already, so merging them would change nothing. The test is `git merge-tree --write-tree <default> <head>`: it prints the default branch's own tree. `branches.csv` gives each branch, its head, its last author, its state and the `content_on_default` column.

| repository | branch |
|---|---|
| cfrp-strengthening | claude/zealous-mendel-s7z7hk |
| incentre-lattices | fold-dof-wording |
| incentre-lattices | fold-search-step-bound |
| project-asma | smith/asma-occurrence-inventory-87 |
| virtual-human | auto/E-deterministic-subgraph |
| virtual-human | docs/asma-research-foundation-20261105 |
| virtual-human | helix/ovarian-parameter-ledger-fe7d |

The 13 branches named in Phase 2 were checked one by one. All 13 still exist, none is merged into `main`, and none of them passes the `content_on_default` test:

| repository | branch | state |
|---|---|---|
| gaia-dr4 | prep/gaia-dr4-tasks | present, unmerged |
| incentre-lattices | gpt-forge/distributed-folding | present, unmerged |
| incentre-lattices | codex/focused-fcc-paper | present, unmerged |
| incentre-lattices | prior-art-sources | present, unmerged |
| proven-commons | claude/brave-knuth-x3bkfi | present, unmerged |
| proven-commons | sync/upstream | present, unmerged |
| exoplanets-frontier | orda-aska-patch-1 | present, unmerged |
| .github | org-pr-template | present, unmerged |
| virtual-human | auto/E-sbml-import | present, unmerged |
| virtual-human | claude/admiring-cori-0qyybb | present, unmerged |
| virtual-human | port/asma-verification-tooling-20261113 | present, unmerged |
| f0 | claude/beautiful-sagan-ssa4lh | present, unmerged |
| f0 | claude/affectionate-ride-rezj73 | present, unmerged |

gfq-codes `axiom/delsarte-sweep` also still exists and is unmerged. It fails the `content_on_default` test as well, because `main` has edited the same files since. Its tip differs from `main` in 15 files. The issue says it landed through #15 to #17 and can be deleted after a check.

## Decision 5: the Zenodo credit line

The exact line in every place it appears:

> Researched and verified by different model families across Gemini, Claude, Grok, OpenAI, and Muse

- 20 `.zenodo.json` files exist. 18 carry the line. The two that do not are `incentre-lattices/.zenodo.json` and `project-asma/.zenodo.json`. Both have their own description, and both belong to repositories with no v1.0.0 deposit. The issue body's figure of 18 matches the files that carry the line.
- 16 published records carry the line. All are version v1.0.0, published 11 November 2026, and each record's description is byte-identical to the repository's `.zenodo.json` description. Editing the file alone does not change the published record. Each record has to be edited in Zenodo by a person with access to the account. `zenodo-credits.csv` lists every file and every record with the credit text it carries, so the edit can be checked against it.

| repository | doi | creators |
|---|---|---|
| certified-orbits | 10.5281/zenodo.24146098 | Arifuddin, Ahraz |
| cfrp-strengthening | 10.5281/zenodo.24146384 | Arifuddin, Shahid |
| covering-min-modulus | 10.5281/zenodo.24146105 | Arifuddin, Ahraz |
| ductricity | 10.5281/zenodo.24146368 | Arifuddin, Ahraz |
| formal-claims-audit | 10.5281/zenodo.24146108 | Arifuddin, Ahraz |
| gaia-dr4 | 10.5281/zenodo.24146126 | Arifuddin, Ahraz |
| gfq-codes | 10.5281/zenodo.24146084 | Arifuddin, Ahraz |
| lost-eclipses | 10.5281/zenodo.24146360 | Arifuddin, Ahraz |
| nhanes-bioimpedance | 10.5281/zenodo.24146382 | Arifuddin, Ahraz |
| overdue-data | 10.5281/zenodo.24146139 | Arifuddin, Ahraz |
| plate-novae | 10.5281/zenodo.24146118 | Arifuddin, Ahraz |
| point-charges | 10.5281/zenodo.24146380 | Arifuddin, Ahraz |
| relative-equilibria | 10.5281/zenodo.24146088 | Arifuddin, Ahraz |
| rism-anon | 10.5281/zenodo.24146136 | Arifuddin, Ahraz |
| thermal-capture | 10.5281/zenodo.24146372 | Arifuddin, Ahraz |
| wwssn-microseisms | 10.5281/zenodo.24146116 | Arifuddin, Ahraz |

Five more published records carry research from these repositories but no repository deposit:

| doi | what | credit |
|---|---|---|
| 10.5281/zenodo.23322080 | incentre-lattices paper, v1.0.0 | none |
| 10.5281/zenodo.23340326 | same paper, v2.0.0 | none |
| 10.5281/zenodo.23841188 | same paper, v3.0.0 | none |
| 10.5281/zenodo.24145786 | rigid-realizations L880 paper, v1 | a different wording: "Researched & verified by models across Gemini, Claude, Grok, OpenAI, and Muse families" |
| 10.5281/zenodo.23322079 | the same incentre-lattices paper, v1.0.0. This DOI now resolves to the v3 record | none on the v3 record |

The line is character-for-character identical in all 16 records and in the 18 files that carry it. The L880 paper's variant is the one different string that the decision meets.

## Decision 7: licences

Repositories with no licence file and no licence GitHub detects: 7.

- `.github`
- `astr0`
- `cosmic-denoising`
- `discussi0n`
- `finite-state-proofs`
- `gravity`
- `math0`

Licence files GitHub reads as NOASSERTION: `cfrp-strengthening`, `incentre-lattices`, `project-asma`. The file is present but is a split licence or a modified text, so GitHub cannot name it.

Detected licences other than Apache-2.0: `exoplanets-frontier` (MIT), `virtual-human` (MIT), `vitruvian3d` (MIT).

Only ductricity and thermal-capture differ: Apache-2.0 for the code with a CC BY 4.0 file for the documentation, and cc-by-4.0 in Zenodo. nhanes-bioimpedance and point-charges carry an extra `LICENSE-CC-BY-4.0` for text. cfrp-strengthening says MIT in Zenodo and has a licence file that GitHub reads as NOASSERTION. `licences.csv` lists all of them.

## How to rerun

```
bash tools/clone-all.sh          # clones the 35 repositories, writes heads.tsv
gh search prs --owner Foundation-0 --state open --limit 400 \
  --json number,createdAt,author,repository,isDraft,title \
  > tools/sources/open-prs.json
gh api 'search/issues?q=is:issue+is:open+org:Foundation-0&per_page=100' \
  --paginate > tools/sources/open-issues-items.json
python3 tools/build_h2.py        # writes open-prs.csv, open-issues.csv,
                                 # licences.csv, zenodo-credits.csv
python3 tools/build_branches.py  # writes branches.csv with open-PR or stranded,
                                 # and content_on_default
python3 tools/make_docs.py --h2  # writes this note
```

The scripts are in `tools/`. The API answers are frozen in `tools/sources/`, taken on 15 November, and the scripts read those, so a rerun needs no network and reproduces the same rows. The clones are needed for `content_on_default`, which runs `git merge-tree` in each repository.

`open-prs.json` and `open-issues-items.json` are the two searches above. `zenodo.json` is `https://zenodo.org/api/records?q=keywords:foundation0&size=25` and `z-<id>.json` is one record each. `unmerged-branches.csv` is the branch list at 01:25 UTC, `pr-heads.json` maps each open pull request to its branch, and `repo-list.json` is `gh repo list` for the 35 repositories.

The one command that fetches is `python3 tools/build_h2.py --live`. It refreshes the branch list for an audit trail and feeds no CSV.

A branch is matched to a pull request by name, not by commit. `f0` `review/o1-o2-f0` gained a commit after the snapshot, so its head no longer matches the recorded one, while the pull request is open and counted.

Two runs produced byte-identical files, and a run under `python3 -O` matched them. One mutation test on a copy of `gaia-dr4`: pointing `origin/main` at the head of `prep/gaia-dr4-tasks` flipped that branch's `content_on_default` from `no` to `yes`, and changed no other row.

The counts move with every PR and issue. They were taken once, on 15 November, and the file lists let a later run be compared.

