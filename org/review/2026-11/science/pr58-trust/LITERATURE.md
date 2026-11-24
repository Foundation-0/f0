# Literature check: four charges, eleven balance points (PR 58)

Searched on 2026-11-15. Scope: the "What is published" section of `threads/four-charges-eleven.md`, the arXiv number cited in `growth.md`, and the harmonic-polynomial claims in `flat-centres.md`.

Method. I fetched arXiv abstract pages and PDFs directly and pulled the text with `pdftotext`. Quotes from arXiv papers are copied from those PDFs. Some publisher pages were blocked (403); those items are marked. Working copies are in the session scratchpad, not in the repository.

Marks used below: [Q] quoted from the source, [I] my inference, not a statement in the source.

## Bottom line

- No report was found, anywhere, of four point charges with more than 9 equilibria for the Coulomb potential. No report was found of the regular-tetrahedron centre as a Milnor-number-11 or T(4,4,4) point.
- But the count 11 for four charges at a regular tetrahedron is already in print, in two places. The note does not mention either.
  1. Gabrielov, Novikov and Shapiro (2004 preprint, 2007 PLMS) say the regular tetrahedron has 11 effective Voronoi cells, which is more than 9, so "a stronger version of Maxwell's conjecture in R3 fails" for their potential with a large exponent. That potential is not Coulomb.
  2. Edelsbrunner, Fillmore and Oliveira (arXiv:2501.05315, PLMS 2026) say the local homology at the tetrahedron centre is "consistent with one minimum, four 1-saddles, and six 2-saddles co-located at the center", which is 11 points, and that the face structure suggests this reading.
- So the note's sentence "four is the smallest number of charges at which Maxwell's bound is known to fail" needs the words "for the Coulomb potential". The novelty of the Coulomb result itself is not contradicted by anything found.
- The note's description of arXiv:2501.05315 ("says only that it splits into three saddles") is incomplete. See (b1).

## (d) Findings that contradict or weaken the novelty claim

### d1. GNS: eleven critical points for four charges at a regular tetrahedron, for large exponent

Source: A. Gabrielov, D. Novikov, B. Shapiro, "Mystery of point charges", arXiv:math-ph/0409009 (v1, 3 Sep 2004); Proc. London Math. Soc. (3) 95 (2007) 443-472, doi:10.1112/plms/pdm012.
- https://arxiv.org/pdf/math-ph/0409009
- Preprint of the PLMS version: https://www.math.purdue.edu/~gabriea/maxwell.pdf
- Same remark in B. Shapiro's lecture slides: https://staff.math.su.se/shapiro/Mylectures/Maxwell/MaxwellLect.pdf

[Q] Purdue version, page 7: "However, already for a regular tetrahedron the number of effective cells is 11, which is greater than Maxwell's bound 9. Thus a stronger version of Maxwell's conjecture in R3 fails: the number of critical points of Vα can be bigger than (l − 1)2 for α sufficiently large."

[Q] Their potential is "Vα(x̄) = ζ1/ρ1^α + ... ", "where ρi = ri^2". So the Coulomb case is α = 1/2. Their Theorem 1.9 says "α = 1/2" is "the standard 3-dimensional Newton potential".

[Q] Theorem 1.6(a): "For any generic configuration of point charges of the same sign there exists α0 > 0 such that for any α ≥ α0 the critical points of the potential Vα(x̄) are in one-to-one correspondence with effective cells of positive codimension in the Voronoi diagram ... The Morse index of each critical point coincides with the dimension of the corresponding Voronoi cell."

[I] For the regular tetrahedron the effective cells are six planes (index 2), four lines (index 1) and one point (index 0). That gives 6 + 4 + 1 = 11 for large α. The PR's Coulomb configurations have 7 of index 2 and 4 of index 1. Same total, different split. A Coulomb potential cannot have an index-0 point, because it is harmonic.

What this does and does not do. It does not give more than 9 for the Coulomb potential. It does show that "four charges, 11 critical points, more than Maxwell's 9" has been in print since 2004 for a closely related family. It also gives a natural reading of the PR's 11 as the Coulomb version of the large-α Voronoi count. The note should cite it.

### d2. EFO: the tetrahedron centre is "consistent with" 11 co-located critical points

Source: H. Edelsbrunner, C. Fillmore, G. Oliveira, "Counting Equilibria of the Electrostatic Potential", arXiv:2501.05315 (v1 9 Jan 2025, v2 20 Mar 2025); Proc. London Math. Soc. (3) 132 (2026) e70163, doi:10.1112/plms.70163.
- https://arxiv.org/abs/2501.05315
- Published-version PDF on the first author's page: https://pub.ista.ac.at/~edels/Papers/2026-13-CountingEquilibria.pdf (same wording on this point)

[Q] Section 3.2: "the rank vector of the tetrahedron is (0, 0, 3, 0), which is consistent with three 2-saddles co-located at its center. It is also consistent with one minimum, four 1-saddles, and six 2-saddles co-located at the center, where the four 1-saddles cancel with the minimum and three of the 2-saddles. The latter choice is suggested by the face structure of the tetrahedron, which has one tetrahedron, four triangles, and six edges."

[Q] Section 3.4: the number 3 "is also a lower bound for the number of 1-saddles and 2-saddles the degenerate equilibrium unfolds into. For example, we get three 2-saddles near the center of the tetrahedron".

[Q] Same section: "Perturbing the vertices of the five Platonic solid thus increases the ratios to 3/4, ..." So their perturbed tetrahedron has 3 equilibria, not more.

What this does and does not do. EFO name 11 as a possible local structure but do not realise it, and a minimum is impossible for the Coulomb potential. They do not claim more than 9 for four charges. Their concluding sentence: [Q] "The main question of determining the maximum number of equilibria of an electrostatic potential defined by n point charges in R3 remains open."

### d3. What I looked for and did not find

- No paper, preprint, thesis, blog, talk or forum post reporting four point charges with more than 9 equilibria for the Coulomb potential.
- No statement that Maxwell's bound fails at n = 4 for the Coulomb potential.
- No identification of the tetrahedron centre as Milnor number 11 or as a T(4,4,4) singularity.
- The arXiv listing was searched by API up to submissions of 11 November 2026. The newest relevant items are from September 2026 (listed in Q1 below). None treats four charges in space.

## (a) Confirmed as the note states

### a1. arXiv:2607.27197

https://arxiv.org/abs/2607.27197 . P. Arathoon, G. Ball, M. D. Kvalheim, "The Maxwell Conjecture is False". [Q] "[v1] Wed, 29 Jul 2026 17:58:42 UTC". Primary class physics.class-ph.
- [Q] Abstract: "We exhibit a configuration of five point charges in Euclidean space whose electrostatic potential admits at least 24 critical points all of which are non-degenerate."
- [Q] Proposition 1: "For every m ≥ 0, there exists a configuration of 3 + 2m positive point charges whose potential has a finite number k ≥ 4 + 20m of critical points, all of which are non-degenerate."
- Four charges are not treated. The only configurations are 3 + 2m charges. The construction is an equilateral triangle plus axial pairs; [Q] "the central equilibrium bifurcates into a family of 21 equilibria."
- [Q] On small n: "it is not known even for n = 3 if 4 is the maximum number, except in the case of equal charges [7]."

### a2. arXiv:2607.28785

https://arxiv.org/abs/2607.28785 . A. Gabrielov, Dm. Novikov, T. Novikov, B. Shapiro, "From 12 to 6: Sharpening the Three-Charge Bound in Maxwell's Problem". [Q] "[v1] Thu, 30 Jul 2026 19:17:04 UTC".
- [Q] Theorem 1.1: "For every n ≥ 2 and every α > 0, a potential generated by three positive point charges in Rn has at most 6 nondegenerate equilibrium points."
- [Q] Section 6: "An improvement to m0 ≤ 1 would be equivalent to Maxwell's conjectured bound for three charges." This matches `three-charges.md`.
- Small qualifier: the bound is for nondegenerate points. `four-charges-eleven.md` drops the word; `three-charges.md` keeps it.

### a3. The 2022 planar paper

The note does not name it. It is: T.-L. Lee and Y.-L. Tsai, "Nine equilibrium points of four point charges on the plane", Applied Mathematics Letters 132 (2022) 108207, doi:10.1016/j.aml.2022.108207 (Crossref record, online 26 May 2022). Publisher page: https://www.sciencedirect.com/science/article/abs/pii/S0893965922001719 (returned 403 to me).
- Confirmed through a citing paper: V. Zolotov, arXiv:2307.00312, https://arxiv.org/pdf/2307.00312 . [Q] "T.-L. Lee and Y.-L. Tsai [15] give an example with 9 equilibrium points for d = 2, m = 1, and n = 4 which is the claimed upper bound of the Maxwell conjecture."
- Abstract wording, seen only as a search-engine snippet of the publisher page, not opened by me: "We find a specific configuration for four point charges on the plane and show, with charge values in a small region, there are nine equilibrium points on the same plane." A second snippet says three equal charges sit at an equilateral triangle, a fourth charge sits at the centre, and the ratio can be "as small as 3/1000". Treat these two snippets as unverified.
- So the note is right: nine, planar, meets the bound.

### a4. arXiv:2609.09637 (cited in growth.md)

https://arxiv.org/abs/2609.09637 . X. Duan, "Counterexamples to GNS Conjecture 1.8". [Q] "[v1] Wed, 9 Sep 2026 02:54:51 UTC".
- [Q] Abstract: "For the Coulomb potential, a generic rational configuration of 24 unit charges in R3 has at least 18 nondegenerate critical points of Morse index one but exactly 14 effective Voronoi one-cells."
- It is about the GNS Voronoi conjecture, not about counts for small n or growth rates. I found no statement of growth faster than linear in it, in arXiv:2607.27197, or in arXiv:2501.05315. This agrees with `growth.md`. The only growth statements are linear: ABK [Q] "an asymptotic critical point to charge ratio of 10"; EFO Result 2, ratio above 25/7.

### a5. 2(d^2 - d + 1) for homogeneous harmonic polynomials on the sphere

- K. Kozhasov, arXiv:1707.04005 (SIAM J. Appl. Algebra Geom. 2018), https://arxiv.org/abs/1707.04005 . [Q] "In [9] Gichev constructed for any d ≥ 1 a homogeneous harmonic polynomial of degree d in 3 variables having 2md,3 = 2(d2 − d + 1) critical points on the sphere S2." His Theorem 1 says this is [Q] "the maximum possible finite number of critical points", attained [Q] "among traceless tensors (harmonic polynomials)".
- V. M. Gichev, arXiv:0705.2547, https://arxiv.org/abs/0705.2547 . He proves only an upper bound 2n^2 for degree n and writes [Q] "I know no example of a spherical harmonic with a greater (finite) number of critical points." The sharp upper bound comes via Kozhasov's Lemma 1, which he credits to Cartwright and Sturmfels.
- So `flat-centres.md` is right that the count is published. Note it counts critical points on the sphere, not in R^3.

### a6. Non-homogeneous harmonic polynomials in three variables

As `flat-centres.md` says, I found no result on the maximum number of real critical points of a non-homogeneous harmonic polynomial in three variables. See Q5.

## (b) Found, but differs from the note

### b1. arXiv:2501.05315 says more than "three saddles"

The note says the paper "treats the centre of the regular tetrahedron as degenerate and says only that it splits into three saddles." The first half is right. The second half is not. The paper:
- gives the local homology rank vector (0, 0, 3, 0);
- says this is consistent with three 2-saddles, and also with one minimum, four 1-saddles and six 2-saddles, 11 in all, and prefers the second reading from the face structure (quote in d2);
- calls 3 a lower bound for the unfolding, not the answer.

The note should quote this and should cite the published version (PLMS 132 (2026) e70163).

### b2. GNS is missing from the note

The note's "What is published" list does not cite "Mystery of point charges", although `three-charges.md` cites it for the bound of 12. Its tetrahedron remark (d1) is the closest published statement to the PR's result.

Numbering caution. In arXiv v1 and the Purdue preprint the Voronoi conjecture is "Conjecture 1.7" and the line conjecture is "Conjecture 1.8". Later papers (EFO, GNNS 2026, Duan) call them 1.8 and 1.9, following the PLMS version.

### b3. Relevant 2026 papers the notes do not cite

These were in the team's `SOURCES.md` download list but are not used in the four-charge note.
- A. Enciso, D. Peralta-Salas, arXiv:2609.03965, https://arxiv.org/abs/2609.03965 , [Q] "[v1] Thu, 3 Sep 2026". Proves finiteness for charges of one sign. [Q] "the Coulomb field has at most 2^(N−4)(N − 1)(9N^2 + 9N + 10) equilibria in the region where S(x) ... does not vanish. Of course, for charges of one sign, S is nonzero everywhere." [I] For N = 4 this is 570. It is the best explicit upper bound for four positive charges that I found.
- G. Oliveira, arXiv:2609.00336, https://arxiv.org/abs/2609.00336 (31 Aug 2026), and X. Duan, arXiv:2608.28376 (28 Aug 2026): both prove the GNS line conjecture, at most 2n − 1 critical points on a line. Not about four charges in space.

## (c) Could not find or could not access

- Lee and Tsai 2022, full text and abstract page: ScienceDirect and ResearchGate returned 403. Confirmed only through Zolotov's citation and search snippets.
- A. Yu. Uteshev, M. V. Yashina, "On Maxwell's Conjecture for Coulomb Potential Generated by Point Charges", LNCS 9570 (Transactions on Computational Science XXVII), 2016, pp. 68-80, doi:10.1007/978-3-662-50412-3_5. Paywalled; Springer and the SPbU portal blocked me. Search summaries say it treats K = 3 and K = 4 positive charges. A 2026 Stockholm thesis describes it as [Q] "For configurations of three and four positive point charges fixed in the plane, they develop an analytical approach to finding the set of critical points" (https://kurser.math.su.se/pluginfile.php/16103/mod_folder/content/0/2026/2026-K24-Einar-Sn%C3%A4ll.pdf). No sign of a count above 9, but I did not read it.
- K. Killian, "A remark on Maxwell's conjecture for planar charges", Complex Var. Elliptic Equ. 54 (2009) 1073-1078, and his 2008 USF thesis (https://digitalcommons.usf.edu/etd/333). Not read. Cited elsewhere as a planar upper bound only.
- Y.-L. Tsai, Physica D 309 (2015) 86-98, doi:10.1016/j.physd.2015.07.007, and Nonlinearity 24 (2011) 3299-3321. Not read. Cited by ABK and GNNS for three equal charges.
- R. M. de J. Nunes, "Morse Theory and the Maxwell conjecture on point charges", MSc thesis, University of Lisbon, 2025. Only the abstract page was readable (https://researchportal.ulisboa.pt/en/studentTheses/morse-theory-and-the-maxwell-conjecture-on-point-charges/). It mentions no four-charge count.
- "Maxwell's Conjecture on four collinear points" (Huang and Nguyen), known only second-hand from the Stockholm thesis, which calls the text "inaccessible". It concerns mixed-sign collinear charges.
- No MathOverflow thread on the topic was found.
- Citation-graph tools hit rate limits (Semantic Scholar 429; OpenAlex daily budget). So I could not list every paper citing arXiv:2607.27197. A full forward-citation check is still open.

## Answers by question

### Q1. Do the cited arXiv papers exist as described?

Yes for all four arXiv numbers. Details and mismatches are in a1, a2, a4 and b1. The 2022 paper exists (a3). The only real mismatch is b1.

### Q2. Any earlier report of more than 9 for four charges, or of Maxwell failing at n = 4?

- For the Coulomb potential: none found (d3).
- For the related potential with a large exponent: yes, GNS 2004/2007, 11 at the regular tetrahedron (d1).
- Is n = 4 stated as open? No source says "n = 4 is open" in those words. Closest statements:
  - ABK (July 2026), quoted in a1: not known even for n = 3.
  - EFO (2026), quoted in d2: the maximum "remains open".
  - GNNS (July 2026): [Q] "In view of a recent counterexample [1] the question of finding new conjectures/results for the maximal number of points of equilibrium for configurations of point charges has resurfaced anew."
  - E. Snäll, Stockholm BSc thesis 2026 (link in c), random search: [Q] "Configurations for N = 4. No configurations with more than five critical points. 750 configurations." This fits the PR's remark that random search does not find 11.
  - MathWorld "Maxwell Conjecture", last updated 14 Nov 2026, lists only the five-charge counterexample: https://mathworld.wolfram.com/MaxwellConjecture.html

### Q3. Tetrahedron centre as Milnor number 11 or T(4,4,4)?

- Not found in any source.
- Known: EFO call the centre degenerate with rank vector (0, 0, 3, 0) and suggest 11 co-located points (d2). GNS give 11 for large α (d1).
- Background for the T(4,4,4) reading: F. Gauss, C. Hertling, arXiv:1511.08660, https://arxiv.org/abs/1511.08660 . [Q] "The 1-parameter families of the hyperbolic singularities of type Tpqr (p, q, r ∈ N≥2, p ≥ q ≥ r, κ := 1/p + 1/q + 1/r < 1) have as surface singularities the normal forms [AGV1] x^p + y^q + z^r + t · xyz". [Q] "A singularity of type Tpqr has Milnor number µ = p + q + r − 1". [I] So T(4,4,4) has µ = 11, which agrees with the PR's computed multiplicity. Whether the actual germ c·xyz − c'·K4 + ... is right-equivalent to T(4,4,4) is not checked here.

### Q4. Best known counts and proved upper bounds

Best known counts (Coulomb, positive charges):
- 5 charges: at least 24, proved (ABK, a1).
- 6 charges: no explicit count found in print. EFO's octahedron gives 5 after perturbation. I found no source for the "25 in print" figure in `point-charges.md`.
- 7 charges: at least 44, from ABK Proposition 1 with m = 2. This is a formula, not an explicit configuration.
- 8 charges, for reference: 25 (EFO square antiprism, ratio 25/8, numerical with partial proofs).

Proved upper bounds, three charges:
- 12 nondegenerate (GNS 2007, Theorem 1.5(b)). [Q] "For l = 3 one has a significantly improved upper bound N3(n, α) ≤ 12."
- 6 nondegenerate (GNNS 2026, a2).
- 4 for three equal charges (Tsai 2015, as cited by ABK and GNNS). [Q] GNNS: "For three equal charges, the bound 4 is known [7]."

Proved upper bounds, four charges. I found no bound specific to n = 4. The general formulas give these values [I, my arithmetic]:
- GNS 2007, nondegenerate: [Q] "Nl(n, α) ≤ 4^(l^2)(3l)^(2l)". For l = 4 this is about 1.8 × 10^18.
- Zolotov 2023, isolated points: [Q] "V has at most (m + 4)(2m + 7)^(d+n) isolated critical points". For m = 1, d = 3, n = 4 this is 5 · 9^7 = 23,914,845.
- EFO 2026, with one charge in generic position: [Q] "the number of isolated critical points of V is at most 2n × (3n − 2)^3". For n = 4 this is 8000.
- Enciso and Peralta-Salas 2026, all equilibria, one sign, no genericity needed: 570 (b3).

### Q5. Real critical points of a non-homogeneous harmonic polynomial of degree d in three variables

- No published maximum found.
- The trivial bound is Bezout's (d − 1)^3 for isolated points. [I]
- For all cubics, not only harmonic ones, 8 real critical points is the maximum and occurs. V. A. Vassiliev, arXiv:2404.17891, https://arxiv.org/abs/2404.17891 . [Q] "strictly Morse polynomials R^3 → R^1 of degree three with the maximal possible number (eight) of real critical points".
- The homogeneous, on-the-sphere count 2(d^2 − d + 1) is published (a5).
- Searches for harmonic polynomials returned mostly the different problem of zeros of complex harmonic polynomials (Wilmshurst-type valence). The claims in `flat-centres.md` (27 for d = 4) and `growth.md` (order d^3/6) have no published counterpart that I found. That supports novelty but is not proof.

## Minor cautions about secondary sources

- Ghosh, Goldberg, Hollender, arXiv:2512.03249 (ITCS 2026) misstate Maxwell's bound as [Q] "(n − 1)(n − 2)". Do not cite it for the bound.
- The Lisbon MSc abstract says three positive charges have at most four equilibria. The 2026 primary sources say this is known only for equal charges.
- Several search-engine summaries garbled facts, for example "a general upper bound ... only obtained in 2013". Nothing in this memo relies on a summary unless marked as a snippet.

## Queries run on 2026-11-15

Note on names. The brief asked for no personal names in queries but also suggested author-name phrasings. I used published authors' names from the literature in some queries, as marked [author name]. I used no names, emails or identifiers of the team, the organisation or the repository.

Web search (mode in brackets):
1. Maxwell conjecture four point charges equilibrium points [standard]
2. four point charges more than nine equilibrium points counterexample Maxwell [standard]
3. "Maxwell's conjecture" "four charges" equilibria [standard]
4. nine equilibrium points four point charges plane 2022 [standard]
5. "point charges" "Maxwell" equilibria arXiv 2022 four charges square nine critical points [extended]
6. Killian Maxwell's problem point charges in the plane equilibria bound [standard] [author name]
7. "Nine equilibrium points of four point charges on the plane" abstract [standard]
8. regular tetrahedron four equal charges center degenerate critical point Milnor number [standard]
9. T_{4,4,4} singularity xyz + quartic Milnor number 11 harmonic potential tetrahedral symmetry [standard]
10. mathoverflow Maxwell conjecture point charges number of equilibria [standard]
11. Gabrielov Novikov Shapiro "Mystery of point charges" four charges bound open [standard] [author name]
12. "Maxwell conjecture is false" five charges 24 critical points four charges open [extended]
13. Maxwell point charge conjecture disproved 2026 blog AI five charges [standard]
14. "four point charges" "11 equilibria" OR "eleven equilibria" OR "eleven critical points" [standard]
15. Uteshev Yashina "On Maxwell's conjecture for Coulomb potential generated by point charges" [standard] [author name]
16. Ya-Lun Tsai equilibrium points point charges Maxwell conjecture four charges three dimensions [standard] [author name]
17. maximum number of real critical points harmonic polynomial three variables degree d [standard]
18. critical points of spherical harmonics on the sphere maximum number 2(d^2-d+1) [standard]
19. Uteshev Yashina Coulomb potential stationary points K=4 positive charges Maxwell conjecture abstract [extended] [author name]
20. Lee Tsai 2022 Applied Mathematics Letters four point charges plane nine equilibrium points Maxwell conjecture charge values region [extended] [author name]
21. "T_{p,q,r}" singularity normal form x^p + y^q + z^r + a xyz Milnor number p+q+r-1 [standard]
22. electrostatic potential Platonic solid charges center degenerate equilibrium unfolding Milnor number singularity type [extended]
23. "tetrahedron" "point charges" "degenerate" critical point "xyz" Taylor expansion potential center [standard]
24. number of critical points of harmonic polynomials in R^3 upper bound non-homogeneous real critical points gradient zeros [extended]
25. harmonic polynomial three variables all critical points real (d-1)^3 Bezout bound attained [extended]
26. "harmonic polynomials" "critical points" maximal number real R^3 Maxwell problem multipole [standard]
27. Yifei Wang "Equilibrium Points of Potential Fields Produced by Positive Point Charges" thesis [standard] [author name]
28. Ricardo Nunes "Morse theory and the Maxwell conjecture on point charges" thesis 2025 [standard] [author name]
29. "Maxwell's conjecture on four collinear points" Huang Nguyen [standard] [author name]
30. zeros of the gravitational field of four point masses number of equilibrium points Newtonian potential three dimensions [extended]
31. "Maxwell" conjecture "regular tetrahedron" charges "effective" Voronoi cells 11 critical points [standard]
32. Maxwell conjecture four charges open problem smallest counterexample n=4 point charges 2026 [extended]
33. T444 hyperbolic singularity tetrahedral symmetry xyz + x^4 + y^4 + z^4 deformation real critical points [extended]
34. equal charges vertices regular tetrahedron equilibrium points of electric field centre degenerate how many equilibria [standard]
35. "four charges" Maxwell bound exceeded Riesz potential large exponent tetrahedron Voronoi effective cells critical points [extended]
36. critical points Coulomb potential four positive charges tetrahedron numerical maximum equilibria found [standard]
37. site:mathoverflow.net point charges equilibrium points Maxwell [standard]
38. "point charges" "balance points" OR "neutral points" four charges more than nine three dimensions [standard]
39. "Maxwell" "point charges" "n = 4" equilibria conjecture holds OR fails four charges 2025 2026 preprint [extended]
40. "there are nine equilibrium points on the same plane" [standard]

arXiv API (export.arxiv.org/api/query, newest first):
1. abs:"point charges" AND (abs:equilibrium OR abs:equilibria OR abs:"critical points")
2. abs:Maxwell AND abs:conjecture AND abs:charges
3. (abs:Coulomb OR abs:electrostatic OR abs:Newtonian) AND (abs:"critical points" OR abs:equilibria) AND abs:charges
4. abs:Maxwell AND abs:"point charges"
5. abs:"Maxwell problem" OR abs:"Maxwell's problem" OR ti:"point charges"
6. abs:Maxwell AND (abs:equilibria OR abs:"equilibrium points")
7. (abs:"Coulomb potential" OR abs:"electrostatic potential" OR abs:"Newtonian potential") AND abs:"critical points"
8. abs:"electric field" AND (abs:zeros OR abs:zeroes) AND abs:charges
9. abs:"harmonic polynomial" AND abs:"critical points" (no hits since 2024)

Bibliographic lookups:
- Crossref: "Nine equilibrium points of four point charges on the plane"; DOI 10.1007/978-3-662-50412-3_5; "Mystery of point charges Gabrielov Novikov Shapiro"; "Counting equilibria of the electrostatic potential Edelsbrunner"; "Maxwell conjecture three point charges equal magnitudes Tsai".
- Semantic Scholar: DOI 10.1016/j.aml.2022.108207 with citations (two citing papers: arXiv:2307.00312, arXiv:2512.03249); DOI 10.1007/978-3-662-50412-3_5; arXiv:2607.27197 citations (rate-limited, no result).
- OpenAlex: DOI 10.1016/j.aml.2022.108207; DOI 10.1007/978-3-662-50412-3_5; works citing GNS (rate-limited, no result).

Pages and PDFs read in full or in part: arXiv 2607.27197, 2607.28785, 2501.05315, 2609.09637, 2609.03965, 2609.00336, 2608.28376 (abstract), 2609.12817 (abstract), 2512.03249, 2307.00312, math-ph/0409009, 2106.11416 (abstract), 1404.7198 (abstract), 1707.04005, 0705.2547, 1511.08660, 2404.17891 (abstract), 2312.07754, 1503.05295; the Purdue GNS preprint; the ISTA EFO PDF; Shapiro's lecture slides; the 2026 Stockholm thesis; MathWorld; the alphaXiv page for 2607.27197 (no comments posted).
