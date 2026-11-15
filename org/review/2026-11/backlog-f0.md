# f0 backlog triage

State read 2026-11-15 against main `6ea3a0b`. Lanes follow
decision 3 in issue 42: build, record, idea. The lane here is a
routing hint for review, not a verdict on the content. [I]

Coverage: all 13 open pull requests inventoried from the
GitHub API, each with head, base, merge-tree result and check
state. Review state for every row in this run: triaged, not
reviewed. No finding was posted to any pull request here.
Heads move, so recheck a head before acting on its row.

## The 13 open pull requests

| PR | Lane | Review | Checks | Blocks on |
|---|---|---|---|---|
| 40 protection proposal | build | required | green | owner decisions 1, 2 |
| 35 prerender at deploy | build | changes asked | none shown | rework, then 30 order |
| 30 Playwright pin | build | changes asked | green | rebase: conflicts with main |
| 27 collaboration guidance | build | none yet | green | overlaps 40 on merge rules |
| 41 Single Thread essay | idea | changes asked | green | science review (F5) |
| 39 conservation quotients | idea + build | changes asked | green | science review, adds a workflow |
| 36 planning field report | idea | changes asked | green | lands before 37 |
| 37 goal boundary (draft) | idea | approved | green | stacked on 36, retarget |
| 28 tissue scouting report | idea | changes asked | green | science review (F5) |
| 20 funding roadmap (draft) | idea | changes asked | green | owner call on scope |
| 11 Witness Map page | record | changes asked | green | tied to issue 10 |
| 7 Discord hub | build | changes asked | green | tied to issue 12 |
| 6 incentre mark | build | changes asked | green | tied to issue 12 |

Facts behind the table: heads, merge state and file counts sit
in [overlap-f0.md](overlap-f0.md). Review states and check
states come from the GitHub API on 2026-11-15. [F]

## Suggested order

This order clears the build fixes that the new rulesets need,
then the stacked pair, then the idea work that waits on science
review. Each step merges to main before the next opens for
review. No step here merges by itself: a person merges. [I]

1. **Decide Gate 0, then land 40.** Nothing else in Phase 1 can
   move without it. While landing it, add the missing required
   check (gap G1 in [f0-audit.md](f0-audit.md)) so a red site
   check blocks a merge.
2. **Land one prerender path: 35 or 30, not both at once.**
   They edit the same three files. 35 removes the direct push
   to main that the ruleset rejects (gap G2). 30 pins the
   browser tooling and conflicts with main today, so its author
   rebases first either way. Pick 35 first, then rebase 30 on
   the result and keep only the pinning that still applies.
3. **Unstack 36 and 37.** Review and land 36. Retarget 37 to
   main, re-run its preflight, and review the one-file change
   on its own. Never delete the 36 branch while 37 points at it.
4. **Fold 27 into the 40 outcome.** 27 rewrites `MERGE-SOP.md`
   and adds collaboration guidance. Decision 2 rewrites the
   same file. Land one text, not two. The smaller path: close
   27 once its still-wanted parts sit in the decision 2 update,
   with the replacement named in the closing pull request.
5. **Science reviews for 41, 39 and 28** under the verdict
   standard in issue 42. 39 also adds a workflow file, so it
   needs a build-lane pass on that file beside the science pass.
6. **Owner calls clear the rest:** 20 (scope), 11 (issue 10),
   7 and 6 (issue 12). Park them with the `needs decision`
   label until the call lands, so the queue reads true.

## Open issues

| Issue | What it waits for |
|---|---|
| 42 this cleanup | Gate 0 answers |
| 38 research pattern | feeds F1 and F2 method |
| 22 org profile README | admin step in another repository |
| 12 forum, logo, Discord, merge rules | owner decisions, gates PRs 7, 6 |
| 10 Witness Map thread | owner decision, gates PR 11 |

## What stays out

No pull request here gets a scientific verdict in this run.
No pull request gets closed, merged or retargeted here.
Authors keep their branches. Each suggested step names the
person or package that carries it out.
