# Laman count for the 10-vertex graph: full report

15 November 2026. Repository head pinned by the report: rigid-realizations at 298926c.

Short note for this thread: `../rigid-realizations.md`.

S is the working folder of this thread. It is archived outside the repository. Paths that start with S/ point into it. Where a file was copied into the repository, its repository path is listed at the end.

---

## Result

[F] The Laman number (complex realizations up to rotation and translation, reflections counted separately) is 880 for code 4778440734593 and 2288 for code 18120782205838348. Three separate programs agree: my code, the authors' C++ library lnumber (built from source with a patch, see below), and the repository's script.

[F] So the number of complex realizations of the 10-vertex graph is exactly 880. Together with the repository's existing proof of 880 distinct real realizations, "all realizations are real" follows, under two conditions. First, Theorem 4.7 of the paper must be right for a general edge labeling.
Second, the repository's lengths must be general enough that no complex solution is missed or double-counted (the repository's own box check shows 880 nonsingular real solutions, so the count of complex solutions for those lengths is at least 880, and the generic count is the upper bound only when the lengths are generic). [I] I did not check that second point. See "Not verified".

## 1. Recursion and convention as the paper states them

Source: arXiv:1701.05500 (abs page https://arxiv.org/abs/1701.05500, TeX from https://arxiv.org/e-print/1701.05500, cached in sources/). Title "The number of realizations of a Laman graph".

[F] Convention. Definition "equivalent realization": "there exists a direct Euclidean isometry sigma of R^2 such that rho_1 = sigma o rho_2", "a direct Euclidean isometry ... preserves distance and orientation". Complex version: A orthogonal with determinant 1. So realizations differing by a reflection are different.
Check: the paper's Figure 1 shows 4 realizations of K4 minus an edge, and my code gives 2 for the triangle and 4 for K4 minus an edge. Proposition "meaning_laman_number": Lam((G,G)) is the number of realizations for a general labeling up to direct complex isometries.

[F] Bigraph (G,H): two graphs (multi-edges, loops, several components allowed) with a bijection of edges. Pseudo-Laman: dim G + dim H = |E| + 1, dim = |V| - #components. Quotient G/E' contracts the edges in E' and keeps E minus E' (an edge that gets both ends in one class becomes a self-loop). Subtraction G\E' deletes E' and keeps only vertices that still have an edge.
^{M}B = (G/M, H\M), B^{N} = (G\N, H/N), each with biedges E minus M, E minus N.

[F] Theorem "laman_number" (Section 4, "A formula for the Laman number"), for pseudo-Laman B without self-loops and any fixed biedge e:

    Lam(B) = Lam(^{e}B) + Lam(B^{e}) + sum over (M,N) of Lam(^{M}B) * Lam(B^{N})

with M union N = E, M intersect N = {e}, |M| >= 2, |N| >= 2, and both ^{M}B and B^{N} pseudo-Laman. Base cases (Proposition "base_cases"): a self-loop in G or H gives 0. G and H each a single edge between two vertices gives 1. Lam(B) = 0 when f_B is not dominant (I use: dim sum below |E|+1 gives 0).

[I] Choices of mine: isolated vertices are dropped (they change neither dim nor the base case). The paper's text on timing says 880 takes 0.18 s in C++ and 1.7 s in Mathematica. my plain Python takes 2.4 s.

## 2. Validation against the paper

[F] Integer code convention. The paper TeX contains no integer codes (the figure lists edges by letters). The convention comes from the lnumber source (lnumber/src/lib.cpp, convert_to_edgelist and idx_flat): bit index i(i-1)/2 + j, least significant bit = bit 0, set if and only if edge {j,i} with 0 <= j < i exists.
The vertex count is inferred from the top set bit as the smallest n with n(n-1)/2 > top bit index. The code depends on the vertex labelling. Confirmed by decoding: both target codes decode to graphs that pass my brute-force Laman test (|E| = 2n-3 and every vertex subset of size k spans at most 2k-3 edges).

[F] Paper's maximal graphs (edge lists read from the TeX figure, validate_paper.log): n = 6..12 give 24, 56, 136, 344, 880, 2288, 6180, all matching the paper's table. Run time for n = 12: 52 s.
[F] Minimum graphs (Henneberg rule 1 only), n = 3..10: 2, 4, 8, 16, 32, 64, 128, 256 = 2^(n-2) (crosscheck.log). Triangle 2, K4 minus an edge 4, prism 24.
[F] 158 random Henneberg-built Laman graphs with n = 3..9: mine with a random choice of e, mine with e = 0, and lnumber agree on all (0 disagreements). This also shows the count does not depend on which e is fixed.
[F] Rejection test: removing an edge from the 10-vertex graph makes my code raise ValueError (dim sum above |E|+1, count undefined). Adding an edge or a K4-plus-pendant graph gives 0. These use no bare assert, so `python -O` gives the same output (crosscheck_O.log).

Note: the paper's drawn n=10 graph, in the letter order of the figure, has code 9502097324865 in my encoding, not 4778440734593. Codes differ by vertex labelling. Both give 880.

## 3. The two target graphs

[F] targets.log:
- 4778440734593: n = 10, 17 edges, Laman, mine 880 (2.5 s), lnumber 880.
  Decoded edges (0-based): (0,1) (1,4) (2,4) (3,4) (0,5) (2,5) (3,5) (1,6) (2,6) (1,7) (3,7) (0,8) (3,8) (7,8) (0,9) (2,9) (6,9).
- 18120782205838348: n = 11, 19 edges, Laman, mine 2288 (11.7 s), lnumber 2288.

[F] The certificate graph. l880_certificate.json (repo@298926c:rigid_realizations_l880_pr_bundle/results/l880-all-880-real/l880_certificate.json, keys "edges", "num_vertices": 10, "complex_realizations_SE2": 880) uses vertex labels 1..10. It is isomorphic to the decoded graph (networkx).
Vertex map, decoded 0-based label to certificate label: 0->9, 1->10, 2->8, 3->7, 4->5, 5->6, 6->1, 7->2, 8->3, 9->4. Mapping the 17 decoded edges gives exactly the 17 certificate edges. The graph has 4 automorphisms, so the map is not unique. The certificate graph itself passes the Laman test (after shifting labels by 1).

## 4. lnumber

[F] `S/work/pc-venv/bin/pip install lnumber` fails on this Mac: version 0.20, source build, `clang++: error: unsupported option '-fopenmp'` (pip_lnumber.log). Workaround [F]: I downloaded the sdist (lnumber-0.20.tar.gz from PyPI), compiled the two C++ files by hand with clang++ without OpenMP, with a shim for the old header tr1/unordered_set and an empty omp.h (source unchanged. it only used `#pragma omp`, which is then ignored, so it runs single-threaded).
Library: lnumber_src/build/lnumber_noomp.dylib, called through ctypes with the same entry point the Python wrapper uses (laman_number). It is therefore the authors' algorithm, built with a patch of the build, not the unmodified PyPI wheel. Results: 880 and 2288, plus agreement on 158 random graphs with n up to 9 (crosscheck.py). lnumber was not run on the paper's n = 6..12 drawn graphs.

## 5. The repository script (opened only after steps 1-4 were final)

File: repo@298926c:rigid_realizations_l880_pr_bundle/scripts/verify_capco_laman.py (not in scripts/ at top level). Copy, sha256 feb8a4252150db585375653d5cbd2e28921223253d433d9cd1471aa73b54969d, in repo_copy/.

[F] Same recursion: laman_bigraph (lines 209-323) takes the two single-edge terms (lines 250-261) and the sum over (M,N) with M = S plus e, N = complement plus e, S non-empty proper (lines 275-321), with loop checks, pseudo-Laman checks (dim sum = remaining biedges + 1) and the base case m == 1 giving 1 (lines 216-221). Contract and delete are the paper's quotient and subtraction (lines 99-157).
[F] Differences, none of which change the recursion: (a) it adds two shortcuts before pivoting, lines 228-240: a bridge common to G and H gives 0 (matches paper Lemma "two_bridges"), and a bridge in only one graph is deleted from both (matches Lemma "remove_edge"). Both lemmas are in the paper (TeX lines 1367 and 1407). (b) Pivot is the first biedge touching a repeated edge, else biedge 0.
(c) It memoises on a degree-sorted relabelling. (d) Its checks use `assert` in the `__main__` block (lines 349-359), which vanish under `python -O`. This only matters for the self-test. (e) Dead code and "Wait:" notes remain in comments and an empty function _canonicalize_graph (lines 15-22).
[F] Agreement (compare_repo.log): the repository's compute_c2 and my laman_number agree on all 80 graphs both computed: paper maximal graphs n = 6..11 (24, 56, 136, 344, 880, 2288), both target codes (880, 2288), and 72 random Laman graphs with n = 4..9. 0 disagreements. Its own run prints 2, 4, 24 and 880 (1.05 s).
[I] Docstring says "Proposition 2.10, Lemmas 2.18-2.19, and Theorem 4.7". The arXiv TeX numbers differ from those labels (the formula is Theorem "laman_number"). I did not check the published numbering.

## 6. Growth rate

[F] arXiv:1811.12800 (Bartzos, Emiris, Legersky, Tsigaridas. TeX from the e-print, sources/bel/maximal_real_arxiv.tex lines 1937-1962), section "Lower bounds". Theorem quoted: "Let G=(V_G,E_G) be a generically rigid graph, with a generically rigid subgraph H=(V_H,E_H). We construct a rigid graph using k copies of G, where all the copies have the subgraph H in common.
The new graph is rigid, has n = |V_H| + k(|V_G| - |V_H|) vertices, and the number of its real embeddings is at least 2^{(n-|V_H|) mod (|V_G|-|V_H|)} * r_d(H) * (r_d(G)/r_d(H))^{floor((n-|V_H|)/(|V_G|-|V_H|))}." They credit the "caterpillar, fan and generalized fan constructions" of their ref. GraKouTsiLower17. The triangle has r_2 = 2.
Corollary: "The maximum number of real embeddings on the plane among Laman graphs with n vertices is bounded from below by 2^{(n-3) mod 7} * 2 * 430^{floor((n-3)/7)}. The bound asymptotically behaves as 2.378^n."

So with H = triangle (3 vertices, r = 2) and G with 10 vertices and r real realizations: glue k copies along a common triangle, n = 3 + 7k, at least 2 (r/2)^k realizations, growth per vertex (r/2)^(1/7).

[F] Numbers (growth.log, mpmath, 30 digits): r = 860: 430^(1/7) = 2.3779887. r = 868: 434^(1/7) = 2.3811363. r = 880: 440^(1/7) = 2.3858113.
[F] The earlier note's formula (r/2)^(1/(n-3)) with n = 10 is the same as (r/2)^(1/7). Its figures 2.3780 (860) and 2.3858 (880) are correct to four decimals. Confirmed, no correction. The paper's own intro quotes 2.3811 for the 868 case, matching 434^(1/7). Using r^(1/7) without halving would give 2.6255, 2.6290, 2.6341, which is wrong because the triangle's own factor 2 is shared.
[F] The repository states the same: repo@298926c:rigid_realizations_l880_pr_bundle/paper/l880_all_880_real_realizations.tex:87 and :288 (440^(1/7) ~ 2.385811, 430^(1/7) ~ 2.377989, 434^(1/7) ~ 2.381136).
[I] The bound is a lower bound on the maximal number of real realizations of Laman graphs, per theorem: it needs r real realizations of one 10-vertex graph. It uses real count r, so r = 880 requires the 880-real result. "Asymptotically 2.3858^n" is the n-th root of the bound as n grows.

## Not verified
- That the repository's 17 lengths are generic for the complex count. The upper bound 880 is for general labelings. For special lengths the number of isolated complex solutions can only be lower or (if degenerate) infinite. The repository's box check gives 880 nonsingular real solutions, which with generic count 880 closes the count.
  [I] Nonsingularity at the 880 solutions gives that each is simple, so for these lengths there are at least 880 and at most 880 only if no solution is at infinity or degenerate. I did not check this step, which belongs to the real-certificate thread.
- I did not re-derive Theorem 4.7. I implemented it as published. The paper's own consistency check (all 118,051 Laman graphs up to 10 vertices against Groebner bases) supports it. My 158 + 80 comparisons against lnumber and the repository script test the implementation, not the theorem.
- Published numbering of the paper's results (SIAGA version).

## Rerun
```
cd S/threads/laman
PY=S/work/pc-venv/bin/python
$PY validate_paper.py 12      # paper maximal graphs 6..12
$PY targets.py                # two codes, lnumber, certificate isomorphism
$PY crosscheck.py             # 158 random graphs, min graphs, rejection tests; add -O to confirm
$PY compare_repo.py           # repository script vs mine
$PY growth.py
```
Build lnumber without OpenMP: see lnumber_src/ (commands in section 4). Shim files in lnumber_src/shim/.

## Files
laman_count.py (implementation), validate_paper.py, validate_paper_graphs.py, targets.py, crosscheck.py, crosscheck_gen.py, compare_repo.py, growth.py. Logs: validate_paper.log, targets.log, crosscheck.log, crosscheck_O.log, compare_repo.log, repo_script_run.log, growth.log, pip_lnumber.log. Sources: sources/ (abs.html, paper.tex, bel/).

Also kept from the hand-back file list: sources/ (the paper TeX, the abstract page and the Bartzos et al. TeX) and lnumber_src/ (the build and the header shim).

## Where the named files are in the repository

Paths are relative to `org/review/2026-11/science/threads/`. Names that are not listed were not copied. `checks/STATE-NOTES.md` says why.

| Name in this report | Repository path |
|---|---|
| `compare_repo.log` | `checks/laman/state/compare_repo.log` |
| `compare_repo.py` | `checks/laman/state/compare_repo.py` |
| `crosscheck.log` | `checks/laman/crosscheck.log` |
| `crosscheck.py` | `checks/laman/crosscheck.py` |
| `crosscheck_O.log` | `checks/laman/state/crosscheck_O.log` |
| `crosscheck_gen.py` | `checks/laman/state/crosscheck_gen.py` |
| `growth.log` | `checks/laman/growth.log` |
| `growth.py` | `checks/laman/growth.py` |
| `laman_count.py` | `checks/laman/laman_count.py` |
| `pip_lnumber.log` | `checks/laman/state/pip_lnumber.log` |
| `repo_script_run.log` | `checks/laman/state/repo_script_run.log` |
| `targets.log` | `checks/laman/targets.log` |
| `targets.py` | `checks/laman/targets.py` |
| `validate_paper.log` | `checks/laman/validate_paper.log` |
| `validate_paper.py` | `checks/laman/validate_paper.py` |
| `validate_paper_graphs.py` | `checks/laman/state/validate_paper_graphs.py` |
