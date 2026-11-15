# Organisation review, November 2026

This folder holds the working record for the cleanup tracked in
[issue 42](https://github.com/Foundation-0/f0/issues/42).
It is a work area, not part of the public site.
Nothing here changes a published claim.

## Read in this order

1. [status.md](status.md): who owns each work package and what is done.
2. [incoming-intelligence.md](incoming-intelligence.md): the brief for
   the agent that does the deep science work.
3. [f0-audit.md](f0-audit.md): what f0 looks like at the pinned commit,
   with every fact tied to a file or a run.
4. [backlog-f0.md](backlog-f0.md): the 13 open f0 pull requests,
   with a merge order and the reason for each step.
5. [overlap-f0.md](overlap-f0.md): which open changes touch the same
   files, and which branches hold work that never landed.
6. [reproduction.csv](reproduction.csv): every f0 checker, run four
   ways, with exit codes and output hashes.
7. [gate0-packet.md](gate0-packet.md): the seven owner decisions in
   one reply-ready form, with the f0 facts each decision needs.

## Rules that apply here

The full rules sit in issue 42 under "How this run works".
The short form:

- One agent per work package. Claim it in issue 42 before starting.
- Every pull request targets main. No stacked pull requests.
- Pin every fact as repo, commit, path and line.
- Mark a fact read from a file or a run as [F].
  Mark a judgment as [I].
- Long output lives in this folder, one pull request per work package.
  Short status notes go to issue 42.
- The `docs/` folder is the public site. Review output never goes there.
- Agents do not merge, force-push, delete branches or change settings.
  A person merges.

## What the three lanes mean

- Build: code, checks, the site, tools.
- Record: results, certificates, claims, papers, data.
- Idea: scouting reports, monographs, proposals, research threads.

Each pull request names its lane in the body.
The lane sets the review checklist in the pull request template.

## How a work package ends

The owner of the package comments in issue 42 with the package id,
a link to the output, what the next package should use, and any
open questions.
