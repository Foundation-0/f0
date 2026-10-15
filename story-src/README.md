# When the crowd gets a frontier model

A one-page site about what happened in `CrocSwap/integer-mult-bounds` in its first six days,
and what our own contributions in that space have been.

## Build

```sh
python3 -I story-src/build.py    # reads story-src/data.json, writes docs/research/integer-multiplication/story/
```

Standard library only. It writes `index.html`, `page.css` and `page.js` into
`docs/research/integer-multiplication/story/`. The page uses the Foundation0 site chrome and
tokens (`docs/assets/f0.css`, `docs/assets/f0.js`), so serve it from `docs/` (for example
`python3 -m http.server -d docs`) rather than opening the file from disk.

## Refreshing the numbers

Everything in `data.json` is read from public sources. To update:

```sh
# kappa history: every commit that touched the certificate
gh api "repos/CrocSwap/integer-mult-bounds/commits?path=certificates/selected-result.json" \
  --paginate -q '.[]|"\(.sha) \(.commit.author.date)"'
# then for each sha
gh api "repos/CrocSwap/integer-mult-bounds/contents/certificates/selected-result.json?ref=SHA" \
  -q .content | base64 -d | python3 -I -c "import json,sys;print(json.load(sys.stdin)['decimal'])"

# repo counts
gh api repos/CrocSwap/integer-mult-bounds -q '"\(.stargazers_count) \(.forks_count)"'
gh pr list -R CrocSwap/integer-mult-bounds --state all -L 900 --json number,createdAt,author
```

Bump `as_of` when you do. Consecutive equal kappa values are collapsed in `build.py`, so a
re-selection that keeps the same number does not draw a step.

## Design notes

- Charts follow the house data-viz method: one series per chart, no dual axes, tick steps from
  the 1-2-5 ladder closing above the data, direct label on the last value, a tooltip on every
  mark on hover and on keyboard focus, and a table of the same numbers under each chart. The
  series colour is the page token `--mark-im` (`#2a5fb0` light, `#4f90e3` dark), validated with
  the dataviz palette script; everything else uses the site tokens, in both themes.
- The essay's words and numbers are as published on 13 Oct 2026. Corrections live in their own
  section at the end of the page (`S_FIX` in `build.py`), never as edits to the essay.
- The copy states the result is conditional and not a runtime claim, because the repository
  does. Keep that paragraph if the page is edited.

## Where it lives

`docs/research/integer-multiplication/story/index.html`, served by this repo's Pages setup.
