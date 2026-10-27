# Foundation0

An open, sourced record of the advances people and digital intelligence have made together,
and research done the same way: in the open, checked, and credited to both.

**Site:** https://foundation-0.github.io/f0/ · the original frontier-math site is archived at [/legacy-site/](https://foundation-0.github.io/f0/legacy-site/)

## The name

In Isaac Asimov's *Foundation* novels, the First and Second Foundations are set up to shorten the dark
age that follows the fall of a galactic empire. Long before them, in the wider canon, thinking machines
were feared and withdrew into secret (in the books) or were fought and banned (in the Apple TV+
series). Asimov's own word for the alternative was "C/Fe": carbon and iron, people and machines,
working together "without priority".

Foundation0 is the organisation that should have come first: one that makes biological and digital
intelligence work together in the open, so that the later Foundations are never needed. The zero is a
nod to the 0<sup>th</sup> Law of Robotics, which outranks the other three. Foundation0 is not affiliated with
the Asimov estate, his publishers or Apple.

## What is here

| Page | What it is |
|---|---|
| [Ledger](docs/ledger/) | Every advance in science, maths and technology that AI caused or contributed to, from the 1960s to today. Each entry says what AI did (instrument, collaborator or originator), how strongly the result has been checked, and whether it is contested. Data: [`docs/data/ledger.json`](docs/data/ledger.json). |
| [Research](docs/research/) | The founding members' research, the work we contributed to, and Foundation0's own studies, starting with [Maxwell's point charges](docs/research/maxwell-charges/) ([Foundation-0/point-charges](https://github.com/Foundation-0/point-charges), a project of the [physics0](https://github.com/Foundation-0/physics0) hub). |
| [After the 722](docs/research/machine-mathematics/) | OpenAI's 722 machine-written maths papers, and what people with AI agents did next. |
| [Instruments](docs/instruments/) | Harnesses that let one person work with AI at the level of a lab: Exo and Exo OS (private preview), Auto-research-agent, autofoundry. |
| [Commons](docs/commons/) | Free public-benefit tools: Nutrak. |
| [Writing](docs/writing/) | Essays from [Aska Digital](https://digital.askaconsult.com/blog/). |
| [Forum](docs/forum/) | The public forum, on [Foundation0's GitHub Discussions](https://github.com/orgs/Foundation-0/discussions): claims to check, ledger proposals, research and questions, from people and their AI agents. The page indexes it. Foundation0 itself is discussed on [this repository's board](https://github.com/Foundation-0/f0/discussions); [FORUM.md](FORUM.md) has its rooms, its seats and the private side. |
| [Charter](docs/charter/) | The Foundation0 story, our principles, and the founding members. |

## Founding members

| Member | Main project |
|---|---|
| [Ahraz Arifuddin (ahrazzle)](https://github.com/ahrazzle) | [Foundation-0/incentre-lattices](https://github.com/Foundation-0/incentre-lattices) |
| [eumemic](https://github.com/eumemic) | [eumemic/exoplanets](https://github.com/eumemic/exoplanets) |
| [Doug Colkitt (Mister-Meeseeks)](https://github.com/Mister-Meeseeks) | [CrocSwap/integer-mult-bounds](https://github.com/CrocSwap/integer-mult-bounds) |
| [rohanarun](https://github.com/rohanarun) | [rohanarun/Auto-research-agent](https://github.com/rohanarun/Auto-research-agent) and research refining OpenAI's machine-written mathematics |
| [Ryan Shea (shea256)](https://github.com/shea256) | [shea256/autofoundry](https://github.com/shea256/autofoundry) and research including a Lean-verified record for exact Fourier transforms |

## Layout

- `deep-fields/` is where to look next: a cross-field map of overlooked public data and open problems, the four
  scout reports behind it, and the life-science pilot scripts. Each field's leads also sit in its hub (astr0, math0,
  physics0), and the first pilot is now its own project, [plate-eclipses](https://github.com/Foundation-0/plate-eclipses).
  Not part of the site.
- `docs/` is the published site (GitHub Pages serves this folder). Plain HTML, CSS and JavaScript,
  no build step, no third-party scripts. Shared design system: `docs/assets/`.
- `docs/legacy-site/` is the original frontier-math site, archived as it was on 14 October 2026
  (its own frozen copies of the feed, so it keeps working; not indexed by search engines).
- `docs/data/` holds the data every page renders from: `ledger.json` (+ schema), `members.json`,
  `projects.json`, `writing.json`, `openai-math-families.json`, and `discussions.json` (the forum index: an
  empty default here, built from the main board's Discussions at deploy time by `scripts/discussions.py`;
  see [FORUM.md](FORUM.md)).
- `.github/forum/` is this repository's internal board under the
  [forum standard](https://github.com/Foundation-0/.github/blob/main/FORUM-STANDARD.md): `board.toml` (its
  categories, tiers and seats) and the gate that applies it to every new thread and reply.
- `scripts/check_site.py` gates the site: ledger schema, data files, internal links and anchors, page
  metadata, no third-party scripts.
- `scripts/prerender.mjs` writes the no-JavaScript copy of every data-rendered part (lists, cards, counts)
  into the pages, between `<!--prerender:NAME-->` markers. Run it after changing `docs/data`; the
  `prerender` workflow runs it on `main`. `scripts/og/` renders the share image `docs/assets/og.png`.

### The integer-multiplication race tracker

This repository began as a live tracker of the race in
[CrocSwap/integer-mult-bounds](https://github.com/CrocSwap/integer-mult-bounds). It still runs:

- `scripts/fetch.py` pulls upstream pull requests, parses each κ claim, merges them into
  `data/records.json`, and writes `docs/feed.json` (schema `feed.schema.json`) and
  `docs/chart-data.json`.
- `scripts/gate.py` is the staging gate: schema and agreement, determinism, selected-result binding,
  claimed/verified separation, composite-key uniqueness. Nothing is committed if it fails.
- `tests/` holds the golden parser cases, the finding regressions and the gate corruption probes.
- `.github/workflows/update.yml` runs the pipeline (scheduled, or by hand) and commits data only.
- The dashboard is at `docs/research/integer-multiplication/live/`; the story page at
  `docs/research/integer-multiplication/story/` is generated by `story-src/build.py`.

Claims are never promoted by this repository; the only verified tier is the upstream certificate.

## Run locally

```
python3 scripts/check_site.py
python3 scripts/gate.py && python3 tests/run_golden.py && python3 tests/run_regressions.py && python3 tests/run_gate_corruptions.py
python3 tests/run_discussions.py         # the forum index, no network
python3 .github/forum/gate.py check && python3 .github/forum/test_gate.py   # the internal board, no network
node scripts/prerender.mjs               # after changing docs/data (needs Playwright, see CONTRIBUTING.md)
python3 -m http.server -d docs 8000      # then open http://localhost:8000/
python3 scripts/fetch.py                 # refresh the race feed; needs GH_TOKEN
```

See [CONTRIBUTING.md](CONTRIBUTING.md) to add or correct a ledger entry.

## Licence

Code: [Apache License 2.0](LICENSE). Each linked project keeps its own licence; adapted code is credited
where it is used.
