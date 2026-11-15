# Thread: the complex count behind "all 880 are real"

Follow-up to the science pass, 15 November 2026. Pinned head `rigid-realizations@298926c`. Marks: **[F]** fact, **[I]** inference.

## Question

The repository proves 880 real realizations of a 10-vertex rigid graph. Calling that "all of them" needs a second number: the count of complex realizations must also be 880. Until now only the repository's own script had computed it.

## Result

| Graph | Integer code | Our recursion | Authors' library | Repository script |
|---|---|---|---|---|
| 10 vertices | 4778440734593 | 880 | 880 | 880 |
| 11 vertices | 18120782205838348 | 2288 | 2288 | 2288 |

[F] Three implementations agree on both graphs. Verdict for the complex count: **VERIFIED**.

## What was done

- [F] `checks/laman/laman_count.py` implements the recursion of Capco, Gallet, Grasegger, Koutschan, Lubbes and Schicho (arXiv:1701.05500) in plain Python with exact integers. It was written from the paper before the repository script was opened.
- [F] It reproduces the paper's maximal counts for 6 to 12 vertices: 24, 56, 136, 344, 880, 2288 and 6180. It gives 2^(n-2) for graphs built by the simplest step alone, for 3 to 10 vertices.
- [F] The authors' C++ library `lnumber` was built from its published source without OpenMP and called on the same graphs. It agrees with our code on 158 random rigid graphs.
- [F] The repository script (`rigid_realizations_l880_pr_bundle/scripts/verify_capco_laman.py:209-323`) implements the same recursion with two shortcuts. It agrees with ours on all 80 graphs both computed.
- [F] The edge list in the 880 certificate is the same graph as the decoded integer code, under the vertex map 0 to 9, 1 to 10, 2 to 8, 3 to 7, 4 to 5, 5 to 6, 6 to 1, 7 to 2, 8 to 3, 9 to 4.
- [F] The counting convention is the paper's: realizations up to rotation and translation, with a mirror image counted separately. The triangle counts 2.

## What "all are real" now rests on

1. [F] 880 real realizations exist at the certified edge lengths, each alone in its box (`checks/l880_independent.py` on draft PR 51, 440 boxes and their mirrors).
2. [F] A generic choice of edge lengths gives exactly 880 complex realizations (this note).
3. [I] At any particular edge lengths, the number of isolated complex solutions cannot exceed the generic count. This is the parameter continuation theorem of Morgan and Sommese (1989). So at the certified lengths no further isolated complex realization exists.

Step 3 is a cited theorem, not a computation made here. The recursion itself was implemented as published and not re-derived.

## Growth rate

[F] Bartzos, Emiris, Legersky and Tsigaridas (arXiv:1811.12800) glue copies of a graph along a shared subgraph. Gluing a 10-vertex graph with r real realizations along a triangle gives growth of (r/2)^(1/7) per vertex.

| r | Source | Growth per vertex |
|---|---|---|
| 860 | published, verified | 2.37799 |
| 868 | published, numerical | 2.38114 |
| 880 | this repository, verified | 2.38581 |

## Rerun

```
python3 checks/laman/validate_paper.py 12      # needs the paper's TeX source saved as sources/paper.tex
python3 checks/laman/laman_count.py 4778440734593 18120782205838348
python3 checks/laman/crosscheck.py             # needs the hand-built lnumber library
```

`targets.py` and `crosscheck.py` expect a clone of the repository and the built library at the paths set in their first lines. Saved outputs are the `.log` files beside them.

## Not verified

- The published theorem behind the recursion.
- The `lnumber` build is the authors' source with OpenMP removed, not the stock package.

## Next step

Answer the repository's open request for a blind re-check of the 880 certificate with this note and the checker on draft PR 51. The 11-vertex graph is the open target (see `l2288.md`).
