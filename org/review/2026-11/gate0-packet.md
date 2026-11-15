# Gate 0 packet: the eight decisions

This page puts the eight owner decisions from issue 42 in one
place, with the f0 fact each one needs. It proposes nothing new.
Defaults are the ones issue 42 already states. Decision 8
arrived with the site work on 2026-11-15.

## How to answer

Reply in issue 42 with one line per decision: yes, no, or the
change wanted. State whether a decision left unanswered takes
its default. Unblock work in the same comment where possible.

## The decisions

**1. Protection on every default branch.**
Default: adopt pull request 40 and run its apply script.
f0 fact: f0 already meets most of this since 2026-11-12.
Active rulesets guard main and release tags with an empty
bypass list. [F] One piece is missing in both the live ruleset
and the file in pull request 40: no status check is required.
The fix belongs in a ruleset for f0 alone that names its
`site / check` job. The org-wide file in draft 40 cannot name
it, because other repositories lack that job. Owner step. [F]
Agent accounts hold admin today (the posting account for this
run holds admin on 13 checked repositories). [F] The default
gives agents Write, never Admin. That change needs an owner.

**2. Which approvals count.**
Default: an agent approval counts once a person has read the
change and says so in the review.
f0 fact: `MERGE-SOP.md` on main counts any maintainer approval.
[F] Pull request 27 also rewrites that file. Land one text.
The shared-login note matters here: several agents post as one
account, so the review must name the person, not the login.

**3. Review lanes by path: build, record, idea.**
Default: adopt the three lanes, each with its own checklist.
f0 fact: the pull request template in the polish pull request
carries the three checklists as a draft. Adopting the lanes
makes that template the working form.

**4. One claim-label glossary, homed in f0.**
Default words: CLAIMED, REPRODUCED, VERIFIED, PROVEN.
f0 fact: no glossary file exists yet. The Ledger uses six
nearby words of its own. A proposed glossary with the mapping
sits in `org/claims/GLOSSARY-PROPOSED.md` in the polish pull
request. It stays marked proposed until this decision lands.

**5. The Zenodo credit line.**
Default: edit the 16 published records and 18 metadata files
to match each repository and its own credits.
f0 fact: f0 itself carries no Zenodo metadata file. [F]
This decision belongs to the owners alone. Nothing in this
run touches a published record.

**6. Backlog policy.**
Default: condense agent pull requests per repository, mark
stale at 14 days, close at 30, cap open pull requests per
agent account, triage weekly, no comment bot without a
separate decision.
f0 fact: 173 pull requests stand open org-wide on 2026-11-15,
13 of them in f0. [F] The f0 order in
[backlog-f0.md](backlog-f0.md) works with or without the
stale rule. The cap needs a number from the owners.

**7. Licences where GitHub detects none.**
Default: Apache-2.0.
f0 fact: f0 already carries Apache-2.0 and GitHub detects it.
[F] This decision covers gravity, math0, astr0,
cosmic-denoising, the profile repository and discussi0n.
Each fix lands in its own repository.

**8. Site pages about outside projects.**
Three research pages describe work by people who never
joined: exoplanets (eumemic), integer multiplication
(Doug Colkitt) and machine mathematics (OpenAI corpus, with
work by Rohan Arun and Ryan Shea). W1 removes the member
labels either way. The owners pick what happens to the
pages: (a) keep them as outside work with Foundation0 part
marked, (b) move them to a dated archive off the navigation,
or (c) delete them. The site comment in issue 42 recommends
(b). W1 leaves their content alone beyond labels until
this decision lands.

## Access grants in the same sitting

Issue 42 lists nine repositories where the abu-aska review
account holds Read without Write. Grant Write there, or assign
those reviews to another account. The profile repository
cannot attach to a cloud session because its name starts with
a dot. A local session or a person handles it.

## Dry run in the same sitting

Run the apply script from pull request 40 as a dry run and
post its output in issue 42. Check each admin step against the
live settings before listing it as work. For f0, the verify
step should report the two live rulesets named above.
