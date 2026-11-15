# F7: summary for the owners

Science pass on the Foundation-0 public repositories, 15 November 2026. All 35 were read from fresh copies at fixed commits. The full record is in `org/review/2026-11/science/`.

## What is established

Three results hold up when checked with programs written separately for this review, or with the repository's own second checker.

1. **A rigid framework with 880 real shapes** (rigid-realizations). A 10-joint framework can be assembled in 880 ways for the bar lengths given, which is every way the algebra allows. The best published figure is 860. A separate exact check confirms all 880.
2. **18 limits on error-correcting codes** (gfq-codes). All 18 are correct. Six improve a standard online table. Twelve are in, or follow directly from, another published table.
3. **Balance points of electric charges** (point-charges). The repository's checker confirms exact counts of 4, 9, 24, 29 and 44 for three to seven charges. Three of these exceed the limit Maxwell proposed in 1873. A separate check is the next step.

Two more pass their own checks and await a line-by-line reading of the written proofs: the elastic constants of the incentre lattice in any dimension, and eleven counting formulas in finite-state-proofs.

## What is open

- **Is the 880 result new?** No earlier report was found. A search cannot prove there is none.
- **The incentre lattice proofs.** The computer checks pass for dimensions 2 to 8. The general proofs have been read only by AI agents.
- **vitruvian3d, math0, nhanes-bioimpedance, virtual-human** and four small data pilots were not judged in this pass.
- **Nine published Zenodo records hold no result yet.** Their repositories say "not started" or hold text only.

## What is wrong

- **gravity, the 185 km/s agreement.** Four speeds near 185 km/s are presented as independent. Three of them depend on a choice made in the script and can move by tens of percent. The fit behind the fourth compares two different quantities. Compared like with like, a threshold near 185 to 200 km/s still fits the table, but only if a second number is fitted too. "Zero free parameters" does not hold.
- **gravity, the data table.** 38 of its 126 rows are computed by the script, not taken from published measurements. Four lens counts cited to a paper are not in that paper.
- **gravity, the public page** still states as results what the claims ledger limits to assumptions.
- **exoplanets-frontier.** Three of five file fingerprints quoted in the claims do not match the files. The 22 "confirmed candidates" are 22 detections from 18 stars at a low bar. The 348 "clean" targets all carry a placeholder where a Gaia measurement should be.
- **Checks that cannot fail.** Several verifiers pass a corrupted file when Python runs in optimised mode, and one rewrites the file it is meant to check. The 14 November findings on this were confirmed. One was overturned: all 39 gravity checksums now match.

## How it fits together

The repositories are separate bodies of work. No result in one is used as an input in another. physics0 and astr0 are index pages that quote the others, and math0 is an index page plus one study. Nearly half of the indexed results, 180 of 383, are one table of literature checks copied into 12 repositories.

There is no single theory here yet, and gravity's own ledger says it is not one. What the strongest results share is a method: put a small box around each solution and prove in exact arithmetic that the box holds one solution. That method is sound, and it is where this organisation's work is ahead of the published record.

## What needs an owner's call

35 verdicts would change the label on a merged claim or touch a published Zenodo record: 6 in gravity, 5 in exoplanets-frontier, and the 12 GF(9) cells in gfq-codes (24 indexed rows). They are marked in `verdicts.csv`. Nothing has been changed in any research repository.
