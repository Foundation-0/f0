# Pull request 58: an independent check, a literature check, and answers to its review

15 November 2026. This folder sits beside `threads/` (pull request 58) and `pr58-addendum/` (pull request 60, the review record). It holds work that does not trust the threads' own programs. The same pull request also edits files in `threads/` to answer the review's blocking items. Marks: **[F]** fact from a run or a proof, **[P]** published, **[I]** inference, **[C]** conjecture.

## Check it yourself in one minute

With Python 3.8 or later and nothing else installed:

```
cd four
python3 -O check.py short_table.json certs/short_table.cert.json 11
```

`short_table.json` is the table printed in `threads/four-charges-eleven.md`, typed in. The program uses no floating point and no library outside Python's own. It prints the 11 balance points with their indices and ends `PROVED exactly 11 balance points`. Maxwell's bound for four charges is 9.

## What is here

| File | What it holds |
|---|---|
| `four/NOTE.md` | A proof that four charges have exactly 11 balance points, for all four certificates, by a checker written without reading the earlier ones. Its lemmas, controls, the adversarial review it received, and its limits. |
| `four/T444.md` | Why the routes in the thread stop at 11. The tetrahedron centre is Arnold's T(4,4,4), whose Milnor number is 11. The flat points form a ladder of types with multiplicities 8, 9, 10 and 11. A prediction made from the ladder, and a first test of it. |
| `LITERATURE.md` | What is published, with quotes and the queries run. Written because the review says "Literature and novelty claims were not checked in any thread." |
| `CHECKER-AUDIT.md` | Which checkers in `threads/checks/` raise on failure and have a saved run on corrupted input under `-O`. It answers review item 3. |

## Findings, most important first

1. **[F] The four-charge result holds under a separate proof.** All four certificates give exactly 11, with 7 of index 2 and 4 of index 1. The checker is one file, standard library only, with every real number enclosed in an integer interval. An untrusted search writes a certificate that the checker replays from a root box it computes itself. Eight configurations with other counts come out as the threads or `indep_count.py` say, including one placed 1.2e-17 from a fold. Twenty-six corrupted inputs are rejected.
2. **[F] An adversarial review of that checker found one unsound path, now closed.** An unquoted JSON number passed through a binary float on reading. A configuration 1.2e-17 past a fold was then checked as one on the other side, and proved 11 where the exact count is 9. The headline inputs were always quoted strings, so they do not change. The fix and both inputs are in the record.
3. **[P] The count 11 at the regular tetrahedron is already in print, though not for the Coulomb potential.** Gabrielov, Novikov and Shapiro (2007) note 11 effective cells for the regular tetrahedron, above 9, for their potential with a large exponent. A 2026 paper (arXiv:2501.05315) reads the degenerate centre as 11 co-located critical points, with a minimum, and does not realise them. The thread's note did not cite the first and described the second wrongly. Both are corrected in `threads/four-charges-eleven.md`. [F] No report of more than 9 for four Coulomb charges was found. The novelty claim stands as "no earlier report found", now with the closest prior statements named.
4. **[F] The multiplicity 11 is a theorem, not only a computation.** The centre is of type T(4,4,4) in Arnold's classification. A Groebner basis computation agrees. The thread's other multiplicities, 8 and 10, are the types P8 and T(3,4,4) of the same ladder. [I] The next type up, U12, with multiplicity 12, would open a route to 13. Searches find no flat four-charge point of that type.
5. **[F] A prediction from the ladder passes a first test on the thread's own data.** Near the nodal stratum, one far balance point should approach the flat point linearly in the distance to the stratum. Over the thread's 23 printed samples the log-log slope is 1.01 and the rank correlation 0.82.
6. **[F] The three-charge proof now has its derivations in the record.** `threads/checks/three/DERIVATIONS.md` writes out every lemma, and `derivations_check.py` checks 62 formulas and statements, failing as it should when a sign is flipped. Two sentences in `three-charges.md` claimed more than the certificate proves and are narrowed: the inverse map is one-to-one on the minima, not on every box, and boxes are shown not to hold minima for the same charges.
7. **[F] A rounding sentence was ambiguous.** "Rounding to four decimals leaves 9" holds for the unrounded source. Rounding the printed table again gives 7. The note now names its source.

## Changes to `threads/` in this pull request

| Review item | File | Change |
|---|---|---|
| Blocking 1 | `unit-point.md` | Gives the counts that `certray_868.json` holds at each eps. |
| Blocking 2 | `recurrences.md`, `square-law.md` | Labels aligned with `README.md`. PROVEN, defined only in an unmerged pull request, is dropped. The four entries with no separate verifier run are named. |
| Blocking 3 | `README.md`, `convergences.md` | The sentence that every checker raises and ran under `-O` now names the nine that the record supports, and points to `CHECKER-AUDIT.md`. |
| Blocking 4 | `three-charges.md`, `checks/three/` | Derivations written out and machine-checked; two over-claims narrowed. |
| Blocking 5 | `gravity.md`, `neutrino-like.md`, two programs | Stale paths fixed where the target exists. Both notes now say they cannot be re-run from this checkout and that the 9 eV end of the window rests on an output with no program. This item is answered in wording only. |
| Major items | `l2288.md`, `central-configurations.md`, `neutrino-like.md`, `fabric.md`, `growth.md`, `convergences.md` | Shared proof template named; equality qualified; corruption counts matched to the record; the 100 eV system named; a tag lowered to [I]; the growth constant's numerical basis stated. |
| Literature | `four-charges-eleven.md`, `README.md` | The two prior statements above cited; "for the Coulomb potential" added; the later checker and the T(4,4,4) identification cited. |

`threads/MANIFEST.sha256` is regenerated and verifies 1,445 of 1,445 files. Nothing else in `threads/` changes.

## For the owners

- [I] The most useful next step is still a check by a person outside the project. `four/check.py` is about 600 lines of plain Python, written so that a mathematician can read it against the four lemmas in `four/NOTE.md`.
- Whom to tell, if anyone, is yours to decide. [I] The literature check adds two groups to the authors of the July paper: Gabrielov, Novikov and Shapiro, whose 2007 remark is the closest prior statement, and Edelsbrunner, Fillmore and Oliveira, whose 2026 paper names the 11 at the tetrahedron. No one was contacted.
- Nothing here changes a claim label on a merged record.

## Limits

- [I] Every piece of work in this folder, like the threads and the review, was done by AI models of one family. A shared misunderstanding would pass all of it. The adversarial review caught a real fault, which shows the value of a second reader. It is not a substitute for an outside one.
- [F] The literature search was by web and arXiv search on one day. Two items were behind paywalls and are marked as not read in `LITERATURE.md`.
