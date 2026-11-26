# What was taken from each source and what went back

15 November 2026. The owner's rule for this work: a source we learn from must gain from it too. This file lists, for every Foundation-0 repository the review read closely, what the review took and what it returned. Everything returned is a draft pull request on a branch named `symbiosis/2026-11-review`, or an issue where no code change was right. Nothing was merged, no claim label was changed, and nothing was sent outside the organisation.

## Returned as draft pull requests

| Repository | Taken | Returned | Link |
|---|---|---|---|
| rigid-realizations | the L880 certificate, the counting code, the search method | a certificate for the 11-vertex graph with at least 2,288 real realizations, its full complex count, a 12-vertex result, a second count program, a standard-library re-check of L880 | [pull 21](https://github.com/Foundation-0/rigid-realizations/pull/21) |
| point-charges | the certified counts, the repository verifier, the open four-charge question | three certified four-charge configurations with 11 balance points, the growth argument with its two proved lower bounds, a fix for the verifier under `python -O`, certificates for eight and nine charges, a second family with 9, three further checkers | [pull 22](https://github.com/Foundation-0/point-charges/pull/22) |
| gravity | the threshold model, its certificates, the acceleration-evolution folder | data tests of the 185 km/s claims on a table of 763 rows, a fix for two check modes that passed when they should fail, proposals for six ledger entries | [pull 28](https://github.com/Foundation-0/gravity/pull/28) |
| gfq-codes | the method of excluding codes by a classical bound | the bound run over every open entry of three reference tables, 1,519 certificates, 2,418 improved entries | [pull 19](https://github.com/Foundation-0/gfq-codes/pull/19) |
| finite-state-proofs | the zero-vector method and eleven proved recurrences | 238 proved recurrences, the square law with a full proof, two corrections to the method | [pull 5](https://github.com/Foundation-0/finite-state-proofs/pull/5) |
| incentre-lattices | the elastic theorem and the fold | two exact checks written separately, and a correction: one shear modulus is zero, not both | [pull 102](https://github.com/Foundation-0/incentre-lattices/pull/102) |
| relative-equilibria | the proved lists to 7 bodies and the open question for 8 to 10 | existence certificates for 20, 42 and 67 classes, with the equations written out | [pull 16](https://github.com/Foundation-0/relative-equilibria/pull/16) |
| vitruvian3d | the passage certificate and its verifier | a fix so the verifier rejects a corrupted certificate under `python -O`, with a test | [pull 12](https://github.com/Foundation-0/vitruvian3d/pull/12) |
| physics0 | the index of physics repositories | two rows brought up to date | draft pull request in physics0, numbered as the gfq-codes one |
| math0 | the index of mathematics repositories | one row brought up to date | [pull 14](https://github.com/Foundation-0/math0/pull/14) |

## Returned as issues or comments

| Repository | Taken | Returned | Link |
|---|---|---|---|
| formal-claims-audit | the verdict check | a question for the owners about a check that passes on an empty folder | [issue 18](https://github.com/Foundation-0/formal-claims-audit/issues/18) |
| exoplanets-frontier | the claims ledger and result files | three places where the ledger and the files disagree | issue in exoplanets-frontier, numbered as the vitruvian3d pull request |
| proven-commons | the proof scanner in an open pull request | an eight-line file that proves a false statement and passes the scanner, posted as a review comment on that pull request | pull 9 of that repository |

Earlier in the day the review also posted its findings as comments on the open issues it had drawn on: issues 4 and 20 of rigid-realizations, issues 2 to 5 of point-charges, issue 5 of gfq-codes, issue 6 of gravity and issue 6 of relative-equilibria. It opened three new issues: 21 in point-charges, 101 in incentre-lattices and 4 in finite-state-proofs.

## Read, with nothing to return

- astr0: the index matched its repositories. The owners may want to refresh one count.
- The other repositories read in the science pass are covered by the verdict table in the parent folder. Where a verdict found a fault, the pull requests for work packages F1 to F8 carry it.

## Sources outside the organisation

Public tables, catalogues and papers were read and are listed in `SOURCES.md` with the date and a checksum of each copy. Nothing has been sent to their maintainers. The owner said others will handle that. Three items are ready for them:

- The code tables: 2,418 entries where a classical bound is tighter than the listed one, with certificates.
- The survey of rigid graphs: a growth constant of 2.4116 against the 2.378 it quotes.
- The authors of the five-charge counterexample: four charges with 11 balance points.

For relative-equilibria, issue 6 says a group in Kraków should be told before any count is published. No new count is claimed here, and that step stays with the owners.

## What each side gained

- The sources gained checks that do not share code with their own, fixes for three verifiers that passed corrupted input under `python -O` (the saved run in this folder is the point-charges one), one corrected statement, and results that extend their own.
- The review gained its starting points. Every new result in this folder began from a method or a certificate in one of these repositories.
