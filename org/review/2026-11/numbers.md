# H2 numbers for the decisions

Read on 15 November 2026, as ahrazzle, against the GitHub API and the Zenodo API. Counts cover the 35 public repositories only.

## The problem, item 5, refreshed

| measure | issue_14_nov | now |
|---|---|---|
| open pull requests | 164 across 29 repos | 166 across 29 repos |
| open PRs opened before 1 November | 115 | 115 |
| open issues | 121 | 122 across 24 repos |
| branches not merged into the default branch | 13 | 204 (159 are the head of an open PR, 45 have no open PR) |

Open PRs by account: ahrazzle 127, orda-aska 25, zero-aska 6, abu-aska 4, mithrax-exo 4.

Open issues by account: zero-aska 72, ahrazzle 24, orda-aska 23, abu-aska 2, mithrax-exo 1.

The 14 November figure of 164 PRs is now 166, and the account totals moved by two for ahrazzle, which is the two review PRs opened on 15 November. The issue count moved from 121 to 122. The per-repository lists are in `open-prs.csv` and `open-issues.csv`.

### Branches

204 branch heads are not reachable from the default branch of their repository. 159 of them are the head of an open pull request, so they are not stranded work in the sense of the issue. 45 have no open pull request. 18 of those were touched on or after 1 November. `branches.csv` gives each one, its head, its last author and its state.

The 13 branches named in Phase 2 were checked one by one. All 13 still exist and none is merged into `main`:

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

gfq-codes `axiom/delsarte-sweep` also still exists and is unmerged. The issue says it landed through #15 to #17 and can be deleted after a check.

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

Where the repository licence and the `.zenodo.json` licence differ, both are listed in `licences.csv`. Three cases:

- cfrp-strengthening is MIT in the file and MIT in Zenodo.
- ductricity and thermal-capture are Apache-2.0 with a CC BY 4.0 documentation file and say cc-by-4.0 in Zenodo.
- nhanes-bioimpedance and point-charges carry an extra `LICENSE-CC-BY-4.0` for text.

## How to rerun

```
gh search prs --owner Foundation-0 --state open --limit 400 \
  --json number,createdAt,author,repository,isDraft,title > out/h2/open-prs.json
gh api 'search/issues?q=is:issue+is:open+org:Foundation-0&per_page=100' --paginate \
  > out/h2/open-issues.json
python3 build_h2.py        # writes the five CSVs
python3 build_branches.py  # adds the open-PR or stranded state to branches.csv
python3 make_docs.py       # writes numbers.md from those CSVs
```

The scripts are not in this folder. They are held by the author and can be attached to the pull request on request.

The counts move with every PR and issue. They were taken once, on 15 November, and the file lists let a later run be compared.

