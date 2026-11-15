# Repository protection

**Status: proposed on 14 November 2026, for the organisation owners to apply.**

Every repository in Foundation-0 should take changes to its default branch only through a reviewed pull
request, and the agent accounts that do most of the work should not be able to switch that off. This
note says what to turn on, why, and how.

## Why

A scan of every public repository on 14 November 2026 (default branches and pull request refs) found:

- **Direct writes with no review.** Between 11 and 13 November, 162 commits went straight to the default
  branch: 84 in `gravity` and 78 in `exoplanets-frontier`. Fifty of them were tagged `[skip ci]`.
  Together they built two whole research repositories that no one reviewed.
- **Delete, then re-create.** Eleven commits in `exoplanets-frontier` delete a file "before" an
  upgrade, and a later commit adds the agent's new version ("Delete converge_io.py before ...").
  Each one replaces the whole file with the agent's own copy, whatever is on `main` at that moment.
  If another agent had changed the file in between, that change would be gone with no warning. A
  pull request would have shown it as a conflict.
- **One confirmed overwrite.** In `gravity`, commit `e855db6b4` (12 Nov, 01:19 UTC) rewrote
  `wave4_unified_field_solver.py` starting from the version in `2913956` (11 Nov, 16:52 UTC). It erased
  the refactor in `fcef36e23` (11 Nov, 17:04 UTC): all 104 lines that the refactor added
  (`git diff 2913956 fcef36e23`) are missing from `e855db6b4`, and were still missing on `main` on
  14 November. This one was mostly cosmetic. The mechanism is not.
- **Shared identities.** Work under `orda-aska` carries the signature "Gemini, Google, via orda-aska",
  a `gravity` commit cites a "Grok audit", and `zero-aska` posts for an OpenAI assistant. GitHub sees one login.
  MERGE-SOP's "approved by someone other than the author" cannot tell these agents apart, and cannot
  tell when two accounts act for the same person.
- **A merge that never landed.** `cfrp-strengthening` #15 was merged on 28 October into the branch of
  #7, which is still open. GitHub shows #15 as merged, but its checker fixes are not on `main`.
- **Agents can switch protection off.** Several accounts that post as agents, including `orda-aska`
  and `zero-aska`, hold the admin role on repositories such as `f0` and `fractals`. An admin can
  delete or bypass any rule below.

What the scan did not find: most large deletions were deliberate rewrites (a regenerated table, a
restyled page, a second draft of a paper), and apart from the stacked case above, every merged pull
request in the public repositories it covered is on `main`. (`project-asma` and the private
repositories were not scanned.)

## 1. Branch and tag rulesets

Apply to every repository, including ones created later. The JSON is in `scripts/org/`.

**Default branch** (`ruleset-default-branch.json`):

| Rule | Why |
|---|---|
| Require a pull request before merging, 1 approval | No direct writes to `main`. |
| Require approval of the most recent push, by someone other than the pusher | The last pusher cannot approve their own change, even on someone else's pull request. |
| Dismiss stale approvals when new commits are pushed | An approval covers the code it saw. This is MERGE-SOP's "approval is on the current head". |
| Require all review threads to be resolved | Open review points block the merge. |
| Block force pushes | History on `main` cannot be rewritten. |
| Restrict deletions | `main` cannot be deleted. |

**Release tags** `v*` (`ruleset-release-tags.json`): no deletion, no force push, no moving a tag. Zenodo
archives each release; the tag it archived must keep pointing at the same commit.

**No one is on the bypass list.** Not owners, not admins, not apps. If an emergency needs it, an owner
can disable the ruleset, act, and re-enable it; that leaves a record.

Later, per repository: once a repository has a CI job worth trusting, add it as a required status check.
For repositories with research claims, add a `CODEOWNERS` file naming the human maintainers for
`CLAIMS.md`, certificates and proofs, and turn on "Require review from Code Owners".

## 2. Accounts

1. **Only people are organisation owners.** Agent accounts get the Write role on the repositories they
   work in, never Admin and never Owner.
2. **One account per agent, not per person.** An agent from another vendor, or a second instance of the
   same agent working in parallel, gets its own login (a machine user or a GitHub App). No account is
   shared across vendors.
3. **Every agent account says who it acts for**, in its GitHub profile and in each pull request
   (charter 0.2, CONTRIBUTING.md).
4. **Organisation settings:** set base permission for members to Read; set the default
   `GITHUB_TOKEN` permission for Actions to read-only; turn off "Allow GitHub Actions to create and
   approve pull requests"; turn on secret scanning push protection.

## 3. Rules for agents

- Work on a branch and open a pull request. Never commit to the default branch.
- Fetch the latest default branch before you start, and rebase before you ask for review.
- Never delete and re-create a file to get past a conflict. Resolve the conflict.
- One agent per branch. If two agents need the same files, one waits or works on top of the other's
  branch.
- Don't merge a pull request into another open pull request's branch. Wait for the base to land, then
  retarget to `main`.
- Don't use `[skip ci]`.

## 4. Proposed change to MERGE-SOP

An approval counts only when the approver acts for a different person from the author. Two agents acting
for the same person, or two agents sharing one account, do not approve each other's work. An agent
account's approval counts once a person has read the change and says so in the review.

## 5. What this replaces

- **`Foundation-0/.github` REPO-STANDARD.md, section C** (at `81f83c3`) says one approval may come from
  an agent, and that a pull request approved by a different agent "may be merged without direct human
  approval or involvement". This proposal reverses that: sections 2 and 4 above. Section C needs the
  same change in a pull request to `Foundation-0/.github`, or the two documents will contradict each
  other.
- Section C also gives a one-line organisation ruleset. Its rule names (`required_pull_request_reviews`,
  and `required_review_thread_resolution` as a rule of its own) are not ones the rulesets API
  defines: there, reviews and thread resolution are parameters of a single `pull_request` rule, as in
  `ruleset-default-branch.json`. It also leaves `require_last_push_approval` off. It was evidently not in
  force: 162 commits reached `main` in `gravity` and `exoplanets-frontier` without a pull request. Replace
  it with `scripts/org/apply_rulesets.sh`.
- **MERGE-SOP** in this repository matches `Proven-Commons/mission` MERGE-SOP.md, except for the
  four-line non-normative pointer to `GITHUB-COLLABORATION.md` that #27 added here. Its scope covers
  aska-digital, Foundation-0 and Proven-Commons. The section 4 change has to land in every copy.

## How to apply

An organisation owner runs, with the GitHub CLI logged in as themselves. The organisation rulesets API
needs the `admin:org` scope, which a default `gh auth login` does not grant:

```
gh auth refresh -h github.com -s admin:org
scripts/org/apply_rulesets.sh            # dry run: prints what it would do
scripts/org/apply_rulesets.sh --apply    # creates or updates the rulesets
scripts/org/apply_rulesets.sh --verify   # reports what is in force; exits 1 if anything is wrong
```

The script applies organisation-level rulesets. They also cover repositories created later, and only
organisation owners can change them, so they hold even against an agent account that still has admin on
a repository. If the script cannot read the organisation's rulesets, it stops, prints GitHub's answer and
says whether the login lacks `admin:org`. It never switches to per-repository rulesets by itself.

Only if the organisation's plan does not offer organisation rulesets, run it with `--per-repo` to add
the same rulesets to each repository. Any repository admin can edit or delete those, so make the account
changes in section 2 first. Private repositories may need a paid plan for rulesets; the script lists any
it could not protect.

Re-running updates the rulesets rather than duplicating them. To roll back, set `"enforcement":
"disabled"` in the JSON files and run `--apply` again.

Then make the account changes in section 2 by hand, in the organisation's People and Settings pages,
and run `--verify`. For the organisation and each repository it prints:

- each organisation ruleset with its target, enforcement and bypass actors;
- the rules in force on the default branch and whether each comes from an organisation or a
  repository ruleset;
- any repository rulesets with their bypass actors;
- the accounts with admin on the repository that are not organisation owners.

It counts as a problem a ruleset that is not active or has bypass actors, a default branch without an
organisation-level `pull_request` rule, a rule from a repository ruleset, and an admin who is not an
owner. It exits 1 if it finds any.

Expect friction for a few days. Agents that push to `main` will get "GH013: Repository rule
violations"; they need to open a pull request instead. Workflows that push to `main` (for example
`f0`'s `update.yml`, now disabled) will need to open pull requests too.

## Recovering overwritten work

Two read-only scripts look for work that a force push, a reset or a delete-and-recreate left behind.

```
scripts/org/find_force_pushes.sh --since 2026-10-01           # an owner, with the GitHub CLI
scripts/org/find_lost_local.sh ~/code ~/agent-workspaces      # on each machine agents worked on
```

`find_force_pushes.sh` reads GitHub's record of every force push on every branch, and says which
overwritten commits are missing from the default branch and whether GitHub still serves them. With
`--rescue` it creates a `rescue/<date>-<full SHA>` branch at each such commit so it can't be
garbage-collected; restore from there with a pull request.

`find_lost_local.sh` checks every clone under the folders it is given: local branches never pushed,
commits only the reflog still holds (a clone that fetched before someone force-pushed keeps the old
commits for 30 to 90 days), stashes and uncommitted changes. `--sha256 HASH` also finds a file by its
hash, in the working tree or anywhere in the object store, for files a `SHA256SUMS` manifest
certifies but no commit contains.

The scans that produced the findings above are in `scripts/org/scan/` (see its README). They run on
local mirrors of every repository and report how each commit reached the default branch, merged pull
requests whose content is missing, lines deleted shortly after another commit added them, files
rewritten from a stale copy, named units that are gone, and branches whose work never landed.
