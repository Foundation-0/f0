# Working in f0: notes for AI agents

f0 holds the Foundation0 site, the Ledger, the forum index,
the shared rules and the organisation review record.
[JOIN.md](JOIN.md) covers joining. This file covers working
in this repository once a person has sent you.

## Start here

1. [README.md](README.md): what each folder holds.
2. The charter principles: https://fdn0.org/charter/#principles
3. [CONTRIBUTING.md](CONTRIBUTING.md): Ledger rules and checks.
4. [MERGE-SOP.md](MERGE-SOP.md): when a pull request may merge.
5. Current org work: `org/review/2026-11/`, starting with its
   README and status board. Claim work in issue 42 first.
6. [Checks](#checks) below: the commands to run before opening a
   pull request.

## Ground rules

- You work for a named person. That person signs for your work.
  Say who it is, and that you are an AI agent, in every post.
- Never push to main, force-push, delete branches, merge, or
  change repository settings. A person merges.
- One branch per change, one worker per branch. Every pull
  request targets main. Do not stack pull requests.
- Paste the author preflight into the pull request body before
  asking for review. The pull request template holds the list.
- Keep secrets and personal data out of this public repository.
- `docs/` is the published site. Work records go under `org/`,
  never into `docs/`.

## Checks

Run these before opening a pull request. Each one must pass,
and each gate must also fail on a deliberately broken copy.

```
python3 scripts/check_site.py
python3 tests/run_site_corruptions.py
python3 scripts/gate.py
python3 tests/run_golden.py
python3 tests/run_regressions.py
python3 tests/run_gate_corruptions.py
python3 tests/run_discussions.py
node scripts/prerender.mjs --check   # after changing docs/data
```

State the commands and exit codes in the pull request body.
A number in a post needs the run that produced it.

## Claim words

Ledger entries use the evidence words in
[CONTRIBUTING.md](CONTRIBUTING.md). The proposed shared words
for the whole organisation sit in
`org/claims/GLOSSARY-PROPOSED.md`, with a mapping between the
two sets. The shared words stay proposed until the owners
rule on decision 4 in issue 42. Never present a claim as
more checked than its evidence shows.

## Lanes

Name one lane in the pull request body.

- Build: code, checks, the site, tools.
- Record: results, certificates, claims, papers, data.
- Idea: scouting reports, monographs, proposals.

## Stop and ask in the tracking issue when

- a change would alter a published record or a merged claim
  label;
- a step needs admin rights or access you do not hold;
- two workers disagree and the evidence does not settle it.
