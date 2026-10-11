# frontier-math

Tracking the frontier of mathematical progress, one race at a time.

**Live dashboard:** https://aska-digital.github.io/frontier-math/

## v1: integer multiplication κ race

Upstream: [CrocSwap/integer-mult-bounds](https://github.com/CrocSwap/integer-mult-bounds).
Every open pull request that states a κ claim is parsed, keyed by (PR, head SHA), and plotted
against the last human-verified result from the upstream `certificates/selected-result.json`.
Claims are never promoted by this repo; the only verified tier is the upstream certificate.

- `docs/` is the published site: `index.html` (chart + sourced table), `method.html`
  (tier definitions), `feed.json` (machine-readable, schema in `feed.schema.json`),
  `chart-data.json` (plot view).
- `scripts/fetch.py` pulls upstream PRs, parses κ, merges into `data/records.json`, emits the views.
- `scripts/gate.py` is the staging gate: schema + agreement, determinism, selected-result
  binding, claimed/verified separation, composite-key uniqueness. Nothing is committed if it fails.
- `tests/` holds the golden parser cases and the gate corruption probes.
- `.github/workflows/update.yml` runs the pipeline every 15 minutes and commits data only.

Quarantined records (no construction claim, fraction/decimal mismatch, superseded head) stay in
the feed under `quarantined` and are not plotted.

## Run locally

```
python3 scripts/fetch.py        # needs GH_TOKEN for the upstream API
python3 scripts/gate.py
python3 tests/run_golden.py
python3 -m http.server -d docs 8000
```
