# W2 site inventory: method

Read on 15 November 2026 as ahrazzle by the first Haiku-seat run. The site is `f0/docs/` plus the root Markdown pages that W1 changes, and the organisation profile in `Foundation-0/.github`. Pinned heads: `Foundation-0/f0@6ea3a0b3d18fa1e7cf1845e3dc67220a35781948` and `Foundation-0/.github@81f83c38918382b4ca142b81debd3cc5ccf61d3a`. Nothing in `docs/` was changed.

`site-inventory.csv` has 3155 rows over 62 pages. One row is one statement on the site. The columns:

- `page` and `line`: where the statement sits.
- `kind`: `date`, `count`, `status`, `repository`, `link` or `member`.
- `statement`: the text as written, shortened to a snippet around the match.
- `what_is_true_now`: the state at the pinned heads or the 15 November read.
- `source`: the statement pinned as `repo@sha:path:line`.
- `now_source`: where the "true now" fact comes from, or the run that produced it.
- `mark`: `[F]` for a fact read from a repository or a run, `[I]` for an inference or a statement left for W3.
- `note`: why the row is there, and what W3 should do with it.

2495 rows are `[F]` and 660 are `[I]`. Nothing here judges a claim or a result.

## How rows were made

- **date** (786): a date in a page, or an `updated` or `generated_at` field in a data file. Each row says the date is still on the site at the pinned head and when the file was last committed.
- **count** (188): a number next to a countable noun in a page, or a recomputed record count in a data file. Research numbers are recorded, not checked. Fable re-checks them.
- **status** (478): a status word in a page, or a `status` field in `projects.json`. The "private preview" rows say that no public repository named Exo or Exo OS exists. "Founding member" rows carry W1's claim that four of the five never joined, marked `[I]` because no repository pin supports it.
- **repository** (193): every `github.com/owner/name` the site names. The now column says whether it is one of the 35 public repositories read on 15 November, a private repository named in the organisation profile, or a repository outside Foundation-0.
- **link** (1509): every `href`, `src` and URL in the pages, deduplicated by page and target. Internal targets resolve against the pinned checkout. 760 resolve and none is broken at this head.
  External targets were checked with `curl -sIL` on 15 November: 421 unique URLs, of which 403 returned 200, 9 returned 404, 4 returned 403, 2 returned 429 and 3 did not answer in time. Scanner junk (template fragments like `${...}`, stray backticks) is skipped and not counted.
  A bare host or API prefix is marked `[I]`, because the page appends a path when it renders.
- **member** (1): the founding-members wording in the organisation profile.

## What the inventory says

The four data dates stand as written: ledger 18 October, members and projects 19 October, writing 14 October, forum index 17 October. `docs/feed.json` was generated on 11 October and no newer feed exists at the pinned head.

The pinned page `docs/research/integer-multiplication/live/method.html` (line 126) records that the `update.yml` schedule has not run since 11 October and that the job is switched off in the repository's Actions settings, which a checkout cannot read, so the live tracker serves that feed.

`projects.json` has 28 entries, 16 of kind `repository`. A live read on 15 November finds 35 public repositories, or 34 if `.github` is left out. 19 of the 35 are not listed, or 18 of the 34. W3 adds them.

The organisation profile names three private repositories, medcode, ion-tracker and demo-repository, all of which return 404 to an anonymous request. It says the core team has admin rights on all repositories, and it refers to founding members. REPO-PROTECTION section 2 gives agents Write only. A cloud session cannot change that repository, so an owner does it.

## How to rerun

From a fresh clone of this branch:

```
python3 -O org/review/2026-11/tools/build_site_inventory.py              # exit 0, offline, same bytes
python3 org/review/2026-11/tools/build_site_inventory.py                 # exit 0, offline, same bytes
python3 org/review/2026-11/tools/build_site_inventory.py --refresh-sources  # network, refreshes site-sources.json
```

The default run reads `site-sources.json`, which freezes the repository list, file commit dates, link statuses and the organisation profile text at the 15 November read. It writes `site-inventory.csv` byte-identically each time. The refresh run uses `gh repo list`, `git log` and `curl`, and may change link statuses, so it is not the reproducibility check.

Deliberate failure on a copy of the checkout: removing `docs/data/projects.json` makes three internal link rows say "No file at docs/data/projects.json" (docs/index.html:258, docs/research/index.html:83, docs/research/machine-mathematics/index.html:324), and the row count drops from 3155 to 3133.

Removing `f0` from `site-sources.json:public_repos` flips 24 of the 25 `Foundation-0/f0` repository rows to "No public Foundation-0 repository by that name", while the 25th, the organisation-profile row, flips to "Private repository named in the organisation profile". Restoring the copy returns the recorded bytes.

## Limits

- Link statuses are a moment. A 403 or 429 is a rate limit, not a dead page. W3 rechecks before it acts.
- The large data files contribute a date row and a count row each. Their thousands of pull-request URLs are dataset records, not site navigation links.
- `docs/legacy-site/` is a frozen archive. Its rows are kept so W3 can see them, but W1 leaves the archive alone.
- The "what is true now" column does not decide what the site should say. It records what was true at the pinned heads so W3 and the owners can decide.
