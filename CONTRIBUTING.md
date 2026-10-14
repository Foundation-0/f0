# Contributing to Foundation0

Foundation0 is a public record. The most useful contribution is a correction: a wrong date, an
overstated claim, a dead link, a critique we missed. Open an issue with the source, or a pull request.

## Add or correct a ledger entry

The ledger lives in [`docs/data/ledger.json`](docs/data/ledger.json); its rules are in
[`docs/data/ledger.schema.json`](docs/data/ledger.schema.json). One entry per advance, sorted by date.

An entry belongs here when digital intelligence caused or contributed to a real advance in science,
mathematics, technology or human capability, and the advance has a concrete, checkable outcome.
Product launches, benchmark scores and business news do not count.

Fill every field. The three that need judgment:

**`ai_role`**: how much of the work the machine did.
- `instrument`: AI is a tool inside a study people designed (a model forecasts weather; a classifier
  finds planets in telescope data).
- `collaborator`: AI proposes key ideas, candidates or constructions that people then select, prove
  or test.
- `originator`: AI produces the result essentially end to end, and people check it.

**`evidence`**: the strongest check the result has passed.
- `formally-verified`: a machine-checked proof (Lean, Coq, Isabelle).
- `peer-reviewed`: a journal or conference paper.
- `independently-replicated`: someone else reproduced it.
- `deployed`: in real operational use (a cleared medical device, an operational forecast).
- `preprint`: public but not yet reviewed.
- `claimed`: an announcement or repository only.

**`contested`**: `true` when a credible source disputes the result or its framing. Say who and why in
`contested_note`, with the source among `sources`.

Sources: one to four, primary first (the paper, the preprint, the official post, the repository),
`https://` only. Write the summary in plain words, with the key number. No hype.

`foundation0: true` marks work by a founding member, or work a founding member contributed to. Set
`page` when the site has a page about it.

## Check before you open a pull request

```
python3 scripts/check_site.py     # ledger schema, data files, links, page metadata
python3 scripts/gate.py           # the kappa-race feed
python3 tests/run_golden.py && python3 tests/run_regressions.py && python3 tests/run_gate_corruptions.py
python3 -m http.server -d docs 8000
```

`python3 scripts/check_site.py --external` also checks that every source URL answers.

## Pages and design

Pages are plain HTML, CSS and JavaScript in `docs/`, with no build step and no third-party scripts.
The shared design system is in `docs/assets/` and described in
[`docs/assets/README.md`](docs/assets/README.md). Every figure must work with the keyboard, in both
themes, with motion off, and at 360 px wide.
