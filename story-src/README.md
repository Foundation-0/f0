# When the crowd gets a frontier model

A one-page site about what happened in `CrocSwap/integer-mult-bounds` in its first six days,
and what our own contributions in that space have been.

## Build

```sh
python3 -I story-src/build.py    # reads story-src/data.json, writes docs/story/index.html
```

Standard library only. `index.html` is self-contained: no fonts, scripts or assets to fetch,
so it can be served from anywhere or opened from disk.

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
  the 1-2-5 ladder closing above the data, direct label on the last value, hover tooltip on
  every mark. Palette is the validated default (`#2a78d6` light, `#3987e5` dark), which passes
  the lightness, chroma and contrast checks against both surfaces.
- Dark mode is selected, not an inverted flip: its own steps under both `prefers-color-scheme`
  and a `data-theme` stamp, so a future theme toggle wins over the OS setting either way.
- The copy states the result is conditional and not a runtime claim, because the repository
  does. Keep that paragraph if the page is edited.

## Where it lives

`docs/story/index.html`, served by this repo's Pages setup once this is on `main`:
https://aska-digital.github.io/frontier-math/story/
