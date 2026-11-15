# Brief for the incoming science worker

You are the strong model this cleanup was arranged for.
Your job is the deep work: say which theories, calculations
and formulae across Foundation-0 hold, which do not, and how
they connect. The engineering prep is done or queued. This
page is your entry point. Everything else sits one link away.

## Your standing

You work for a named person, and that person signs for your
work. Say who that is in every post. [JOIN.md](../../JOIN.md)
holds the general rules. This run adds its own rules in
[issue 42](https://github.com/Foundation-0/f0/issues/42),
under "How this run works" and in the execution plan comment.

Claim your work package in issue 42 before you start.
Name the model, the effort level and the GitHub account you
post as. Post which repositories you can read and which you
can write. One worker per package, one worker per branch.

## First hour, in order

1. Issue 42, body first, then the execution plan comment.
   That comment carries the verdict standard in full.
2. [status.md](status.md) in this folder, for what is claimed.
3. [f0-audit.md](f0-audit.md), for the ground you stand on.
4. The charter principles at fdn0.org/charter, section on
   principles. Eight short rules. They bind every post.
5. One repository end to end: its README, its claims file,
   its checkers. Start where status.md points you.

## The map, checked 2026-11-15

The organisation holds 35 public repositories, 6 private ones
out of scope, and 173 open pull requests. [F]

Hubs and shared ground:
f0 (site, Ledger, rules), the profile repository, discussi0n,
st0a (agent coordination), math0, physics0, astr0.

Mathematics and proof:
incentre-lattices, rigid-realizations, covering-min-modulus,
gfq-codes, finite-state-proofs, formal-claims-audit,
proven-commons.

Physics, Earth and engineered systems:
gravity, fractals, point-charges, relative-equilibria,
certified-orbits, vitruvian3d, cfrp-strengthening,
wwssn-microseisms, thermal-capture, ductricity,
cosmic-denoising.

Astronomy:
exoplanets-frontier, gaia-dr4, plate-eclipses, plate-novae,
lost-eclipses.

Life, body and data:
project-asma (biology out of scope in this run),
virtual-human, nhanes-bioimpedance, overdue-data, rism-anon.

Treat this grouping as a reading aid. The structure decision
(S1) may redraw it. Canonical homes per theory are yours to
propose, not to assume.

## How to judge a claim

Three judgments stay separate for every claim: the statement,
the evidence offered, and the label it carries. A true
statement can wear an overstated label.

| Verdict | Needs |
|---|---|
| PROVEN | proof checks, Lean on standard axioms, statement matches |
| VERIFIED | rigorous computation, rerun fresh, fails closed |
| REPRODUCED | the repo code gives the stated numbers, fresh clone |
| KNOWN | true and published, cite the source word for word |
| OPEN | plausible, evidence does not settle it. The default |
| OVERSTATED | label claims more than the evidence shows |
| CONTRADICTED | a counterexample, a failing fresh run, or an exact quote |
| NOT CHECKABLE | data or code missing, name what and where |

Working rules that carry weight:

- The scientific work here came from sources the owners rate
  highly. Meet it at that level. Argue the strongest case
  that a claim is right before you judge it.
- Implausible never means contradicted. Without one of the
  three proofs in the table, the verdict is OPEN with reasons.
- A deep derivation is not PROVEN until it checks. Length and
  polish earn nothing by themselves.
- Recompute on your own code from the stated formulae. Reruns
  of repo code support REPRODUCED at most.
- Each verdict ends with two plain sentences a non-specialist
  can follow: what the claim says, the verdict, and why.
- The 14 November findings in issue 42 are inputs. Recheck
  each one (F4). Overturn any that fail, and record the flip.

## Your work order

- **F1 theory map.** One entry per distinct theory: canonical
  statement, formulae, constants, repositories that use it.
  Done when every repository in the map names its theories.
- **F2 verdicts.** Every claim in the claims index (H1),
  Zenodo and PROVEN-labelled claims first, then claims other
  repositories build on, then the rest. Done when each claim
  carries a verdict, evidence and the plain-language line.
- **F3 ties.** Shared quantities, shared formulae with
  differing values, cross-repo contradictions, and which
  convergence claims survive. One graph plus the prose.
- **F4 recheck.** Each 14 November finding confirmed or
  overturned with evidence. f0 rows already sit in
  [f0-audit.md](f0-audit.md) and [reproduction.csv](reproduction.csv).
- **F5 reviews.** Science-lane reviews as authors request
  them in issue 42. Comment or request changes only, until
  decision 2 settles approvals.
- **F6 glossary.** Final wording for decision 4, built on
  the proposed draft in `org/claims/`.
- **F7 owner summary.** One page, plain language: settled,
  open, wrong, and how it fits together. Posted in issue 42.

## Output contract

- Files go in this folder, `org/review/2026-11/`, through one
  pull request per package on a branch named `review/<id>`.
- The pull request body carries the author preflight from
  issue 42. The template in the polish pull request holds
  the same list.
- Pin facts as repo, commit, path, line. Mark facts [F] and
  judgments [I].
- Every number you state comes from a run you name, with the
  command and exit code in the body.
- Hand off in issue 42: package id, link, what the next
  package should use, open questions.

## Stop and ask in issue 42 when

- a verdict would change a published Zenodo record or the
  label on a merged claim;
- a step needs admin rights or access you lack;
- two workers disagree. You hold the last word on science.
  Owners hold it on structure.

## Ready now, no decision needed

H1 inventory and H2 decision numbers are unclaimed and feed
everything. F1 can start per repository as H1 reaches it.
The gaia-dr4 recovery choice (prep branch or task slices)
needs its authors before 2026-11-25. Details sit in
[overlap-f0.md](overlap-f0.md).
