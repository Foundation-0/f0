# Pull request 58: an independent check, a literature check, and answers to its review

15 November 2026. This folder sits beside `threads/` (pull request 58) and `pr58-addendum/` (pull request 60, the review record). It holds work that does not trust the threads' own programs. The author of pull request 58 answered the review's items in their own commits; this pull request changes only two notes in `threads/`, to add what the literature check found. Marks: **[F]** fact from a run or a proof, **[P]** published, **[I]** inference, **[C]** conjecture.

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

## Findings, most important first

1. **[F] The four-charge result holds under a separate proof.** All four certificates give exactly 11, with 7 of index 2 and 4 of index 1. The checker is one file, standard library only, with every real number enclosed in an integer interval. An untrusted search writes a certificate that the checker replays from a root box it computes itself. Eight configurations with other counts come out as the threads or `indep_count.py` say, including one placed 1.2e-17 from a fold. Twenty-six corrupted inputs are rejected.
2. **[F] An adversarial review of that checker found one unsound path, now closed.** An unquoted JSON number passed through a binary float on reading. A configuration 1.2e-17 past a fold was then checked as one on the other side, and proved 11 where the exact count is 9. The headline inputs were always quoted strings, so they do not change. The fix and both inputs are in the record.
3. **[P] The count 11 at the regular tetrahedron is already in print, though not for the Coulomb potential.** Gabrielov, Novikov and Shapiro (2007) note 11 effective cells for the regular tetrahedron, above 9, for their potential with a large exponent. A 2026 paper (arXiv:2501.05315) reads the degenerate centre as 11 co-located critical points, with a minimum, and does not realise them. The thread's note did not cite the first and described the second wrongly. Both are corrected in `threads/four-charges-eleven.md`. [F] No report of more than 9 for four Coulomb charges was found. The novelty claim stands as "no earlier report found", now with the closest prior statements named.
4. **[F] The multiplicity 11 is a theorem, not only a computation.** The centre is of type T(4,4,4) in Arnold's classification. A Groebner basis computation agrees. The thread's other multiplicities, 8 and 10, are the types P8 and T(3,4,4) of the same ladder. [I] The next type up, U12, with multiplicity 12, would open a route to 13. Searches find no flat four-charge point of that type.
5. **[F] A prediction from the ladder passes a first test on the thread's own data.** Near the nodal stratum, one far balance point should approach the flat point linearly in the distance to the stratum. Over the thread's 23 printed samples the log-log slope is 1.01 and the rank correlation 0.82.
6. **[F] Two separate write-ups of the three-charge lemmas found the same two over-claims.** The author of pull request 58 and a separate agent for this pull request each wrote out the derivations behind `three-charges.md`. Both found that the inverse map is one-to-one only on the minima, not on every box, and that the pair step shows no two minima share charges, not that no two boxes do. The author's corrected note and `checks/three/DERIVATIONS.md` are the ones kept; the second write-up is not added.
7. **[F] A rounding sentence was ambiguous.** "Rounding to four decimals leaves 9" holds for the unrounded source. Rounding the printed table again gives 7. The note now names its source.

## Changes to `threads/` in this pull request

The author of pull request 58 answered every blocking and major item of the review in their own commits, so this pull request no longer carries fixes for them. It changes two notes, and the manifest:

| File | Change |
|---|---|
| `four-charges-eleven.md` | Cites the 2007 remark of 11 at the tetrahedron and describes arXiv:2501.05315 as it reads. Adds "for the Coulomb potential" to the novelty sentences, and the 570 bound of arXiv:2609.03965, read from its Theorem 1.1. Names the source of the rounding sentence. Lists the later checker and the T(4,4,4) identification. |
| `README.md` | One sentence on the two prior statements, beside the novelty claim. |
| `MANIFEST.sha256` | The two checksums. `checks/verify_folder.py` passes: 1,481 files, 193 of 193 ledger claims, 22 checkers. |

## For the owners

- [I] The most useful next step is still a check by a person outside the project. `four/check.py` is about 600 lines of plain Python, written so that a mathematician can read it against the four lemmas in `four/NOTE.md`.
- Whom to tell, if anyone, is yours to decide. [I] The literature check adds two groups to the authors of the July paper: Gabrielov, Novikov and Shapiro, whose 2007 remark is the closest prior statement, and Edelsbrunner, Fillmore and Oliveira, whose 2026 paper names the 11 at the tetrahedron. No one was contacted.
- Nothing here changes a claim label on a merged record.

## Limits

- [I] Every piece of work in this folder, like the threads and the review, was done by AI models of one family. A shared misunderstanding would pass all of it. The adversarial review caught a real fault, which shows the value of a second reader. It is not a substitute for an outside one.
- [F] The literature search was by web and arXiv search on one day. Two items were behind paywalls and are marked as not read in `LITERATURE.md`.
