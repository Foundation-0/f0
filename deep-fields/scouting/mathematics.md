# Scouting report: overlooked long tails in mathematics and theoretical computer science

*Written by an AI research agent (Claude) for Foundation0 on 18 Oct 2026.*

**How it was checked:** the agent scraped codetables.de and read the maintainers' own pages. Treat every figure as
a lead and re-check it before you rely on it.

**Follow-up:** the [math0 leads](https://github.com/Foundation-0/math0) hold the 18 Oct snapshot of open codetables.de
entries.

## Main finding

The idea that discoveries sit where nobody bothered to look still holds, but many people now share it. Between July
and October 2026, dozens of people, many apparently using AI agents, swept the famous record tables. The places
still quiet are:

- tables where checking a result needs heavier algebra (minimum distance over GF(q), quantum code distance);
- the proof and upper-bound side of tables, as opposed to new constructions;
- lists of open problems buried in handbooks and surveys.

## Already crowded: do not start here

| Area | Evidence of the sweep |
|---|---|
| Friedman's Packing Center | Many pages updated 18 Oct 2026. The hexagons-in-circles page credits at least 7 different finders in 2026 ([index](https://erich-friedman.github.io/packing/)). |
| Comellas degree/diameter table | Changed on 18 Oct 2026. At least 15 named contributors July–Oct 2026, plus a single-author paper using ChatGPT ([2606.15860](https://arxiv.org/abs/2606.15860)). [Table](https://web.mat.upc.edu/francesc.comellas/delta-d/table_degree_diameter.html) |
| Brouwer's code tables | About 12 contributors sent constant-weight codes Aug–Oct 2026. Rosin's CPro1 tool added 24 ([2603.00174](https://arxiv.org/abs/2603.00174)); Echols found 124 ([2608.13906](https://arxiv.org/abs/2608.13906)). [Andw](https://www.win.tue.nl/~aeb/codes/Andw.html) |
| Kéri covering codes | Marosi made 83 improvements in Aug 2026, "the first since 2011" ([2608.19872](https://arxiv.org/abs/2608.19872)). He also contributes to the Comellas table, so people are moving from table to table. |
| Sorting networks | Five improvements on 13 Oct 2026 ([list](https://bertdobbelaere.github.io/sorting_networks_extended.html)). |
| Classical Ramsey numbers | AlphaEvolve raised 9 bounds ([2603.09172](https://arxiv.org/abs/2603.09172)); an integer-programming paper raised 25 R(3,n) bounds ([2608.18769](https://arxiv.org/abs/2608.18769)). |
| Cages | 11 records by Exoo, Goedgebeur et al. ([2511.07247](https://arxiv.org/abs/2511.07247)). |
| Covering designs | The La Jolla Covering Repository was frozen on 1 Mar 2026; a [successor site](https://dmgordon.org/covering-designs/) is active. CPro1 failed on these. |
| Covering arrays | Colbourn's table now requires an ASU sign-in. CPro1 failed on these. |
| Erdős problems | A DeepMind proof agent resolved 9 of 353 ([2605.22763](https://arxiv.org/abs/2605.22763)). The [formal-conjectures](https://github.com/google-deepmind/formal-conjectures) repository has 873 Erdős files, 236 OEIS files and 57 Written-on-the-Wall II files. |
| Busy Beaver | BB(2,4) is settled. BB(6) has 1,064 machines still unresolved and an active community writing Rocq proofs. |
| Kissing numbers | AlphaEvolve, PackingStar ([2511.13391](https://arxiv.org/abs/2511.13391)), Echols. |
| Polynomial and matrix multiplication | Kauers' group ([2502.06264](https://arxiv.org/abs/2502.06264), [2603.07280](https://arxiv.org/abs/2603.07280)). |

## Ranked shortlist

### 1. Linear codes over GF(3), GF(4), GF(5), GF(7), GF(8) and GF(9) on codetables.de, both bounds

1. **What is overlooked.** Grassl's tables are the standard reference ([BKLC](https://www.codetables.de/BKLC/index.html)).
   AI attention goes to the binary table. The non-binary fields, and the upper-bound side generally, get little.
   Checking a result needs a minimum-distance computation over GF(q), a higher bar than for constant-weight codes.
2. **Size (scraped 18 Oct 2026).**
   - Open entries (lower bound below upper bound): GF(2) 25,859; GF(3) 25,684; GF(4) 29,374; GF(5) 7,056;
     GF(7) 4,071; GF(8) 7,202; GF(9) 7,265.
   - About 19,000 non-binary entries are marked "constructions missing".
   - In a random sample of 210 entries, 77% were last changed in 2001–2009 and 4% in 2025–26.
   - The maintainer calls GF(7) upper bounds for n > 50 "rather weak". There are 3,296 open entries there, with a
     median gap of 9, against 3 for n ≤ 50.
3. **Certificate.** A generator matrix, whose minimum distance anyone can recompute. Upper bounds can be certified by
   an exact rational LP dual. Submissions go to codes@codetables.de; Grassl is active.
4. **Prior and ongoing AI attacks.**
   - EPFL (Viazovska, Abbe): binary only ([2609.37056](https://arxiv.org/abs/2609.37056)).
   - He and Kasprzyk, machine learning on toric codes ([2512.13370](https://arxiv.org/abs/2512.13370)).
   - **Main competitor:** the maintainer's own sweep of quasi-cyclic index-2 codes, credited as "GrasslOzkaya".
   - An exhaustive constacyclic search over q ≤ 9 once improved 71 entries.
5. **Pilot.**
   - (a) An open-source minimum-distance verifier over GF(q) (Brouwer–Zimmermann), validated against the generator
     matrices stored on the table's pages.
   - (b) Search outside the index-2 sweep: quasi-twisted codes of index 3–4, constacyclic shifts, and one-column
     extensions of record codes.
   - (c) An exact Delsarte LP bound for GF(7) codes with n = 51–100.
   - **First success:** one code that beats the table, checked by two independent programs.
6. **Risk.** Each record is minor. Most gaps come from weak upper bounds, so the open count (80,652 in the non-binary fields when re-counted on 18 Oct; first estimated at about
   79,000) overstates what can be improved. Grassl's own sweep may get there first.

### 2. OEIS "Empirical" recurrences by R. H. Hardin: a proof sweep

1. **What is overlooked.** About 16,180 entries carry empirical formulas from counting arrays under local rules
   ([search](https://oeis.org/search?q=Empirical+author%3AHardin)). For a fixed width these can be proved
   mechanically with transfer matrices.
2. **Size.** 16,180 entries. Only 16 mention "proved", 107 "confirmed" and 128 Howroyd.
3. **Certificate.** A transfer matrix T with start and end vectors u and v. If T has dimension D, a claimed
   recurrence of order r that holds on the first D + r terms holds for every term.
4. **Prior work.** Dougherty-Bliss and Kauers proved one family ([2309.00487](https://arxiv.org/abs/2309.00487)).
   DeepMind's agent proved 44 of 492 OEIS conjectures. No systematic sweep of Hardin's entries turned up.
5. **Pilot.** Pick one Hardin family and prove or refute every column recurrence. **First success:** 100 or more
   proved, plus any counterexamples.
6. **Risk.** Low significance per entry. The OEIS's AI policy, approved 29 Aug 2026, bans bulk or serial automated
   submissions without prior permission ([policy](https://oeis.org/wiki/Use_of_AI_for_OEIS_Submissions)). Publish
   the proofs on Zenodo first, then ask the editors.

### 3. Open existence questions in combinatorial designs: the Handbook lists and Gordon's circulant weighing matrices

1. **What is overlooked.** Rosin's CPro1 solved open Handbook instances in 7 of 16 design types
   ([2501.17725](https://arxiv.org/abs/2501.17725)). Nine types failed, and most chapters were never tried.
2. **Size.**
   - CPro1 lists 2–16 open instances per design type ([repo](https://github.com/Constructive-Codes/CPro1)).
   - Gordon's circulant weighing matrix dataset v1.3 (24 Apr 2026) has 2,773 open cases with n ≤ 1000 and k ≤ 19²
     ([page](https://dmgordon.org/circulant-weighing-matrices/), [Zenodo](https://doi.org/10.5281/zenodo.10775927)).
     That includes 28 in Strassler's classic range and 270 with n ≤ 300.
3. **Certificate.** The design itself, or the first row of the matrix, checked instantly.
4. **Note.** Tan proved 8 cases impossible in Aug 2026 ([2608.18468](https://arxiv.org/abs/2608.18468)); exclude them.
5. **Pilot.** Add circulant weighing matrices as a CPro1 design type, using the open list as instances. Run for
   48–72 h.

### 4. Small Ramsey numbers outside the classical R(s,t) table

- **Size.** Radziszowski's survey, revision #18 (24 Apr 2026), has many tables beyond classical R(s,t): K_k − e,
  books, wheels, cycles, C4 versus stars, and 3-colour lower bounds ([pdf](https://cs.rit.edu/~spr/ElJC/ejcram18.pdf)).
- **Attention so far.** AI attacks targeted only classical R(s,t) and R(3,n).
- **Certificate.** A colouring.
- **Odds.** Higher prestige, lower chance of success within days.

### 5. Qubit stabilizer codes on codetables.de

- **Size.** 29,459 of 33,152 entries are open for n ≤ 256, 1,361 of them with n ≤ 64. Another 15,011 are marked
  "constructions missing" ([table](https://www.codetables.de/QECC/index.html)).
- **Competition.** Topical, and competitive.

### 6. Graffiti and Written-on-the-Wall conjectures (lower priority)

- **Size.** About 1,000 conjectures. Several were refuted in 2025–26.
- **Formalised.** 57 of the Written-on-the-Wall II conjectures are now in formal-conjectures.
- **Status.** No maintained list of which ones remain open.

## Practical advice

- Contact maintainers before submitting in bulk: Grassl, Gordon, Radziszowski, and the OEIS editors.
- Build reusable exact checkers and certificate formats first.
- Move fast. The degree/diameter table went from quiet to about 15 contributors in roughly three months.
- One unconfirmed lead: the [subspace-codes table](http://subspacecodes.uni-bayreuth.de/news/) has no news since 2017.
