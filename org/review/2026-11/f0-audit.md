# f0 audit at 6ea3a0b

Scope: this repository only, at main
`6ea3a0b3d18fa1e7cf1845e3dc67220a35781948` (2026-11-11), read on
2026-11-15 from a fresh clone. Org-wide counts in this file are
point-in-time reads from that day; they move during a working day,
so a fresh read on a later date will differ. [F] marks a fact read
from a file, a run or the GitHub API. [I] marks a judgment.

## What f0 is

f0 holds the public site at fdn0.org, the Ledger of advances with
their check status, the forum index, the shared rules, and the
integer-multiplication race tracker. [F] `README.md:3`

The site is plain HTML, CSS and JavaScript in `docs/`, served by
GitHub Pages with no build step and no third-party scripts.
[F] `README.md:53`

## What passes

All six documented checks pass from the fresh clone. [F]

| Command | Exit | Last line |
|---|---|---|
| `python3 scripts/check_site.py` | 0 | site gate: all checks pass |
| `python3 scripts/gate.py` | 0 | records=348 claimed=348 quarantined=25 |
| `python3 tests/run_golden.py` | 0 | all 4 golden cases pass |
| `python3 tests/run_regressions.py` | 0 | all regressions pass |
| `python3 tests/run_gate_corruptions.py` | 0 | 4 corruptions blocked |
| `python3 tests/run_discussions.py` | 0 | all forum checks pass |

The same checks fail when they should. [F]

- A ledger entry with a false evidence tier makes
  `check_site.py` exit 1.
- `gate.py --root` on an empty folder exits 1.
- Four corrupted feed copies each exit nonzero in
  `tests/run_gate_corruptions.py`.
- Under `python3 -O` the four main checks still pass on good
  input, because they raise errors instead of using bare asserts.
  The whole repository holds 2 bare asserts, both in
  `tests/run_discussions.py`. [F]

Full rows with output hashes sit in [reproduction.csv](reproduction.csv).
A hash is sha256 of the command's raw stdout, first 16 hex; stderr is
excluded. One row carries no hash: the forum-index check prints a random
tmpdir in its stdout, so its output has no stable hash.
f0 is a sound pattern for the shared checker in Phase 4 of issue 42. [I]

## Protection, live state

Issue 42 says no ruleset is in force. For f0 that no longer holds. [F]

- Ruleset "Protect main" (id 27178056) is active on the default
  branch since 2026-11-12 US Central time (created
  2026-11-13T05:11:06Z). It needs one approval, approval of the
  latest push by someone else, resolved review threads, and it
  blocks deletion and force pushes. The bypass list is empty. [F]
- Ruleset "Protect release tags" (id 27178077) is active. [F]
- Classic branch protection is also on for main, with admin
  enforcement. [F]
- Required status checks are empty in both layers. A pull request
  with a red site check can merge on one approval. [F]

Two gaps follow from that state.

**G1. The site check is not required.** The ruleset JSON in
pull request 40 has the same gap: it lists no required check.
[F] `scripts/org/ruleset-default-branch.json` at `9f98863`.
The fix is one rule that names the `site / check` job. It needs
an owner to apply it, so this run only records it. [I]

**G2. One workflow still pushes to main.** `prerender.yml`
commits baked pages and pushes on every data change to main.
[F] `.github/workflows/prerender.yml:54`
The ruleset rejects direct pushes, so that step now fails or
silently stops updating pages. Pull request 35 moves the baking
to deploy time and pull request 30 reworks the same workflows.
[F] `update.yml`, the other direct-push workflow, is already
disabled by hand. [F]

## Entry points for a new worker

**G3. There is no machine entry point.** The repository root has
no `AGENTS.md`. [F] `JOIN.md` speaks to an agent sent by a person
and ends with draft posts. It never names the review rules, the
evidence standard or the output folder for this run. A powerful
worker that lands here cold must rebuild the map from scratch. [I]

**G4. The org map is stale.** `docs/data/projects.json` carries
the date 2026-10-19 and 16 project repositories. [F]
The organisation has 35 public repositories on 2026-11-15. [F]
Nineteen public repositories have no link in that file, among
them gravity, proven-commons, virtual-human, vitruvian3d,
exoplanets-frontier, finite-state-proofs and the three field
hubs. [F] The project table in `JOIN.md:36` has the same gap. [F]
The Ledger data carries the date 2026-10-18 with 343 milestones. [F]

**G5. There is no claims file or glossary in f0.** Decision 4 in
issue 42 puts the shared claim words in this repository. No such
file exists at this commit. [F] The Ledger uses its own evidence
words in `CONTRIBUTING.md:26` (claimed, preprint, peer-reviewed,
independently-replicated, deployed, formally-verified). [F]
Those words overlap the proposed org words without matching
them, and no mapping is written down. [I]

**G6. Review paperwork lives only in the issue.** The author
preflight, the three lanes and the verdict words exist in issue
42 alone. The repository has discussion templates but no issue
template, no pull request template and no CODEOWNERS file. [F]
`MERGE-SOP.md` predates decision 2: it counts any maintainer
approval and says nothing about a person reading the change
or lanes. It does pin approval to the current head
(`MERGE-SOP.md:19,28,39`), so the head rule is not the gap.
[F] `MERGE-SOP.md:14`

## Backlog shape

f0 has 13 open pull requests and 5 open issues. [F]
One pull request (30) conflicts with main. One (37) stacks on
another open branch. Ten carry a changes-requested review.
The detail sits in [backlog-f0.md](backlog-f0.md). [F]

Twenty-one remote branches exist beside main. Six are already
merged and were never deleted. Two more hold the superseded and
the waiting work that issue 42 names. The branch table sits in
[overlap-f0.md](overlap-f0.md). [F]

Org-wide, open pull requests total 173 on 2026-11-15.
f0 still holds 13 of them. [F]

## What this run changes

Two draft pull requests, both against main, both for an owner
to judge:

1. This folder: the audit, the triage, the overlap map, the
   reproduction rows, the decision form and the brief for the
   science worker.
2. The entry polish: `AGENTS.md`, a pull request template with
   the preflight and lanes, a proposed glossary with the Ledger
   mapping, an empty claims registry with its column rules, a
   refreshed project table in `JOIN.md`, and a kept test that
   proves the site gate fails on corrupted data.

## What this run does not change

No merges. No branch deletions. No closes. No settings, ruleset
or licence edits. No site pages. No verdict on any scientific
claim. Every such step is written down as a recommendation with
its evidence, for an owner or the package owner to carry out.
