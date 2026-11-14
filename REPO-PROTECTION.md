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
- **One confirmed overwrite.** In `gravity`, commit `e855db6b4` (11 Nov, 19:19 UTC) rewrote
  `wave4_unified_field_solver.py` starting from the 10:52 version. It erased the 11:04 refactor
  (`fcef36e23`): 104 lines, still missing today. This one was mostly cosmetic. The mechanism is not.
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

## How to apply

An organisation owner runs, with the GitHub CLI logged in as themselves:

```
scripts/org/apply_rulesets.sh            # dry run: prints what it would do
scripts/org/apply_rulesets.sh --apply    # creates or updates the rulesets
scripts/org/apply_rulesets.sh --verify   # lists the rules now in force on each default branch
```

The script tries organisation-level rulesets first, which also cover repositories created later. If the
plan doesn't offer them, it adds the same rulesets to each repository one by one. Re-running it updates
the rulesets rather than duplicating them. Private repositories may need a paid plan for rulesets; the
script lists any it could not protect. To roll back, set `"enforcement": "disabled"` in the JSON files
and run `--apply` again.

Then make the account changes in section 2 by hand, in the organisation's People and Settings pages.

Expect friction for a few days. Agents that push to `main` will get "GH013: Repository rule
violations"; they need to open a pull request instead. Workflows that push to `main` (for example
`f0`'s `update.yml`, now disabled) will need to open pull requests too.
