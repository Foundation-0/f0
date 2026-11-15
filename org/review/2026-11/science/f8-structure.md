# F8: where the science says the work belongs

Science pass, 15 November 2026. These follow from `theories.md` and `ties.md`. Each is a proposal for the owners.

## Together

1. **One home for certified counting.** rigid-realizations, point-charges, certified-orbits and relative-equilibria use, or plan to use, the same proof method: a box around each solution, checked in exact or interval arithmetic. A shared checker that compares by default, refuses to run under `python -O` and raises errors would serve all four.

   The two that have results show the method works. The two that have not started would start from a tested tool.
2. **One claims register per repository, in one format.** 30 of 35 repositories have no claim IDs. A verdict cannot attach to a result that has no name. The gravity ledger is the best model in the organisation: it separates the physical statement from the arithmetic lemma and names its inputs.
3. **The acceleration-evolution thread in one place.** It lives in gravity only. Its companion notes are in open pull requests in three other repositories. Keep the equations and the test design in gravity and link to them.

## Apart

4. **The fact-check table out of the result indexes.** `notes/reports/fact-check.md` is a source check from October. It sits in 12 repositories and was indexed as 15 results in each. Keep one copy in f0 and mark the others as frozen copies, or remove them.
5. **gravity: data apart from scripts.** The 126-row table is typed into a script, and 38 rows are computed inside it. Move the published values to a data file with one source pin per row. Keep model-derived rows in a separate file that is never fitted as data.
6. **gravity: the page apart from the ledger.** The public page should be generated from `CLAIMS.md`, so that a limit added to a claim reaches the page.
7. **gfq-codes: known apart from new.** Split the 18 cells into the two base facts that are new against the table, the four that follow from them, and the twelve that are in or follow from Maruta's tables.
8. **Plans apart from results.** Nine published Zenodo records belong to repositories with no result. A plan can be public. It should not carry a version 1.0.0 record that says "verified".
9. **Index pages apart from research.** The project tables in physics0, math0 and astr0 quote other repositories, and two of the quotations are out of date. Generate their tables from each repository's own status line.

## Order of work the science suggests

1. Write an independent checker for point-charges. It is the next result that could reach VERIFIED.
2. Have a mathematician read the incentre-lattices elastic proof line by line. It is the candidate for a new theorem.
3. Rebuild the gravity table from sources and refit both parameters, as set out in `notes/gravity.md`.
4. Regenerate the exoplanets-frontier ledger from its current results files and re-run the Gaia step.
