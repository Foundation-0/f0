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

## After changing `docs/data`, run the prerender

Pages draw their lists, cards and counts from `docs/data/*.json` in the browser, and each of those parts
also carries a static copy in the HTML so the page reads without JavaScript. After changing anything in
`docs/data` (or a page script that renders from it), run:

```
node scripts/prerender.mjs
```

It serves `docs/` locally, opens every page that has `<!--prerender:NAME-->` markers in headless Chromium
with the network to GitHub blocked, and writes what each page's own script rendered back between its
markers. Commit the changed `docs/**/*.html` with the data. It needs Playwright
(`npm i --no-save playwright@1.56.1 && npx playwright install chromium`; set `PRERENDER_CHROMIUM=playwright`
to use that browser). `node scripts/prerender.mjs --check` only reports whether any page is out of date.
On `main`, the `prerender` workflow does the same and commits the result.

After a change to `docs/data/ledger.json`, also refresh the share image, which shows every milestone and their
count: `node scripts/og/shoot.mjs` writes `docs/assets/og.png` (1200×630) from the ledger. Look at it before you
commit it.

To make a new data-rendered part prerendered, put the two markers as the only content of the element the
page script writes into, for example `<ol id="members-list"><!--prerender:members--><!--/prerender:members--></ol>`,
and run the script. The full rules are at the top of [`scripts/prerender.mjs`](scripts/prerender.mjs).

## Check before you open a pull request

```
python3 scripts/check_site.py     # ledger schema, data files, links, page metadata
python3 scripts/gate.py           # the kappa-race feed
python3 tests/run_golden.py && python3 tests/run_regressions.py && python3 tests/run_gate_corruptions.py
node scripts/prerender.mjs --check   # the no-JavaScript copies match the data
python3 -m http.server -d docs 8000
```

`python3 scripts/check_site.py --external` also checks that every source URL answers.

## Pages and design

Pages are plain HTML, CSS and JavaScript in `docs/`, with no build step and no third-party scripts.
The shared design system is in `docs/assets/` and described in
[`docs/assets/README.md`](docs/assets/README.md). Every figure must work with the keyboard, in both
themes, with motion off, and at 360 px wide.
