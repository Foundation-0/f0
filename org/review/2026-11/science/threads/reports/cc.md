# Central configurations of 8, 9 and 10 equal masses: full report

15 November 2026.

Short note for this thread: `../central-configurations.md`.

S is the working folder of this thread. It is archived outside the repository. Paths that start with S/ point into it. Where a file was copied into the repository, its repository path is listed at the end.

---

## Summary

For 8 equal masses in the plane I proved that at least 20 classes of central configurations exist. For 9 equal masses I proved at least 42. Classes are counted up to rotation, scaling, reflection and relabelling. Each class is proved to exist, to be unique in its box and to be non-degenerate. The classes are proved pairwise distinct.

Two programs that share no code check every certificate. One uses Arb ball arithmetic and the other exact rational arithmetic. Both also prove each class's Morse index and its exact symmetry group. With those, the certified lists satisfy the Morse (Euler characteristic) identity exactly. Their Morse counts match Hampton's conjectured Morse polynomials for N = 8 and N = 9, term by term.

As an extra, n = 10 gives at least 67 classes, and the Morse identity holds exactly there too. Completeness is not proved for any n ≥ 8. I did not attempt it, because I estimate it at about 30 to 55 CPU-years with the published method.

All files are in `S/threads/cc/`.

**Failures and limits:**
- One n = 10 census crashed on a NaN bug. I fixed it and reran.
- For n = 10, random starts (about 1.1 million) never found the regular decagon. Only a probe started near the regular polygon found it. So a census that stops finding new classes can still miss a real class.
- A few certification steps, each a few seconds long, ran beside two censuses. That briefly broke the 2-process limit.

---

# Full report

## Central configurations of 8 and 9 equal masses: what the box method delivers

Thread `cc`, 15 November 2026. Wall clock 00:39 to 02:07 (88 minutes of the 2 hour box).

### 1. Literature

The convention is classes up to translation, rotation, scaling, reflection and relabelling. Moczurad and Zgliczyński call this their "second criterion" (`sources/mz2019_v3.txt` line 147).

| n | rigorous complete list | numerical lists |
|---|---|---|
| 5, 6, 7 | 5, 9, 14 (Moczurad and Zgliczyński 2019) | Ferrario 2002: same |
| 8 | none | Ferrario 20, Doicu, Zhao, Doicu (DZD) 2022: 20 |
| 9 | none | Ferrario 42; DZD 42 |
| 10 | none | Ferrario 64 (fails his own Morse check), DZD 67 |
| 11, 12 | none | DZD 114, 191 |

- [F] **Moczurad and Zgliczyński**, arXiv:1812.07279v3 (CMDA 131, 2019).
  - Their Table 4 gives 5, 9, 14 classes for n = 5, 6, 7. The n = 7 run took 8.5e6 CPU-seconds.
  - On n = 8 they write: "we were not able to obtain a rigorous listing of CCs for n = 8" (lines 164 to 166).
  - Line 169 says that existence and local uniqueness of every listed CC with n ≥ 8 was easy for them.
  - Their Theorem 2 lists only CCs with no symmetry: 2 for n = 8, 3 for n = 9, 11 for n = 10.
- [F] **Ferrario**, arXiv:math/0204198v1 (2002), numerical tables. I parsed 20, 42 and 64 entries for n = 8, 9, 10. For n = 10 he writes that "there is a missing term +3" (`ferrario.txt` line 501).
- [F] **DZD**, arXiv:2010.15358v2 (CMDA 134(3), 2022).
  - Their Table 1 gives 20, 42, 67, 114, 191 classes for n = 8 to 12.
  - They state there is "no guarantee that the list is complete" (line 1156).
  - They report that Moczurad and Zgliczyński tested existence for every listed CC up to n = 12 (line 1104). I found no published certificates for those tests.
  - For n = 10 they say 11 of the 67 have no axis of symmetry (line 1222).
- [F] **Hampton**, arXiv:1810.13011v2, Conjecture 5 gives Morse polynomials for N = 7, 8, 9. He suspects that Ferrario's 26th 9-body entry has isotropy 1, not 1/2 (line 1107).
- [F] **Moczurad and Zgliczyński 2026**, arXiv:2601.01165, still cites complete planar lists only for n ≤ 7. They call DZD "possibly complete" (lines 107 and 111).
- **Search done:** an arXiv API title search ("central configurations" with "equal" in the abstract, 49 hits up to 2026-11-04), four recent abstracts, and three web searches. Cached in `sources/`. No complete n = 8 list was found, and no public certificates for n ≥ 8.

### 2. Equations and normalisation

All masses are 1. Each body satisfies F_i = Σ_{j≠i} (q_i − q_j)/r_ij³ − q_i = 0, which sets λ = 1 and so fixes the scale.

- [F] Summing the equations forces Σ q_i = 0, which removes translation.
- Rotation is removed by putting the body farthest from the origin, body k, on the positive x-axis. So y_k = 0 and y_k is not an unknown.
- The identity Σ_i q_i × F_i = 0 holds for every configuration. With y_k = 0 it gives x_k F_{k,y} = −Σ_{i≠k} q_i × F_i. So if x_k > 0 and every other equation holds, F_{k,y} = 0 follows, and that equation can be dropped.
- That leaves a square system: 2n − 1 equations in 2n − 1 unknowns (15 for n = 8). Its zeros with x_k > 0 are exactly the CCs with body k on the positive x-axis. Its Jacobian is invertible exactly when the CC is non-degenerate.
- The invariant used to tell classes apart is I = Σ|q_i|². With λ = 1, I equals U, and Moeckel's potential is P = U·√I = I^1.5.

### 3. Numerical census (floating point. Finds candidates only)

`census.py` runs batched Levenberg-Marquardt from random starts. The starts mix a disc, a square and Gaussian clouds. There are three variants:
- pseudo-inverse Newton started from clustered bodies (`MODE=newton STARTS=cluster`);
- "tight" runs that polish every solution and merge two solutions only when I agrees to 1e-10 and the sorted distances agree to 1e-8 (`TIGHT=1`).
- a probe started near the regular polygon (`STARTS=decagon`).

`merge_census.py` takes the union of all runs.

| n | runs and starts | classes in each run | last new class |
|---|---|---|---|
| 8 | LM 2.56M, Newton+cluster 168k, tight 948k, polygon probe 144k | 20, 20, 20, probe adds none | within the first 3000 starts in every run |
| 9 | LM 2.53M, Newton+cluster 126k, tight 681k, polygon probe 108k | 42, 42, 42, probe adds none | within the first 3000 starts |
| 10 | LM 801k, tight 300k, polygon probe 30k | 66, 66, probe adds the regular decagon | |

- [F] For n = 8 and 9, the least-hit class still took 0.6% and 0.2% of converged starts. A class whose basin takes a share p of starts is missed by N starts with probability (1 − p)^N. So a class with basin share above about 1e-6 would have been missed with probability under 5%.
- [F] **Caution:** for n = 10, random starts never found the regular decagon (Morse index 7), but the probe near the polygon found it. A tiny basin defeats this estimate, so the census is evidence, not proof.

### 4. Certification

**Krawczyk test.**
- The box centre x0 lies on the 2^-50 grid. The box is X = x0 + [−h, h] with h = 2^-30. C is a dyadic approximate inverse of the Jacobian at x0.
- The test requires K(X) = x0 − C·G(x0) + (I − C·DG(X))(X − x0) to lie strictly inside X. Then X holds exactly one zero, and every matrix in DG(X) is invertible (Krawczyk 1969, Moore 1977).
- I also ran the test on boxes of radius 2^-12, 2^-14 and so on, and report the largest box that passes as the uniqueness radius.
- [F] Uniqueness radii:
  - n = 8: 2^-12 for 16 classes, 2^-14 for 3, 2^-16 for 1.
  - n = 9: 2^-12 to 2^-16.
  - n = 10: down to 2^-22, for the near-degenerate classes close to the decagon.

**Bounds, and why they hold.** DG(X) has to enclose the Jacobian at every point of X. The Jacobian blocks are r^-3·I − 3·r^-5·d·dᵀ. The only non-polynomial step is r^-1, computed from r² ∈ [a, b].
- `cert_arb.py` uses Arb's rsqrt, which rounds outward rigorously. If the ball for r² touches 0, the result is not finite and the test fails rather than passing by accident.
- `verify_rational.py` encloses r^-1 in [1/√b, 1/√a], because t^(-1/2) is decreasing. The square roots come from integer square roots: isqrt(⌊t·4^120⌋)/2^120 ≤ √t ≤ (isqrt(⌈t·4^120⌉) + 1)/2^120. Every product is rounded outward to the 2^-120 grid, and sums are exact. It also checks x_k > 0 on the whole box.

**Distinctness.** [F] The enclosures of I over the certified zeros are pairwise disjoint. The closest n = 8 pair is P = 63.18080 and P = 63.18157, which differ by about 8e-4. The enclosure widths are about 1e-12.

**Morse index.**
- [I] The Morse index of U on the shape space equals the number of positive eigenvalues of the reduced Jacobian. The reason: −J_F is the Hessian of U + I/2. The scaling and translation directions are positive and orthogonal to the shape space. Rotation is the kernel. And deleting y_k keeps the inertia, because the rotation vector has component x_k ≠ 0 there.
- Arb program: a float eigenvector congruence, then Gershgorin discs.
- Rational program: exact LDLᵀ inertia of M0 ± tI, then Weyl's inequality.

**Symmetry order s.**
- Permutations that do not preserve every |q_i|² and r_ij² enclosure are excluded.
- For each surviving permutation, and with or without reflection, the image is re-rotated so that body k is on the positive x-axis. If it lands in the box, uniqueness proves it is a symmetry. If it misses the tight enclosure, it is not one. Any undecided case is a failure.
- This proves s exactly, including s = 1 (no symmetry).

**Results.** Both programs accept all of the following, and both agree under `python -O`.

| n | classes certified | no symmetry (s = 1) | labelled count (up to rotation, mirror images counted separately) | Σ(−1)^h·2/s vs (−1)^n/(n(n−1)) |
|---|---|---|---|---|
| 8 | 20 | 2 | 676,080 | 1/56 = 1/56 |
| 9 | 42 | 3 | 13,905,360 | −1/72 = −1/72 |
| 10 | 67 | 12 | 246,556,800 | 1/90 = 1/90 |

- [F] Morse counts for n = 8 by index: 5760, 40320, 161280, 216720, 151200, 80640, 20160. This equals Hampton's 720(8 + 56t + 224t² + 301t³ + 210t⁴ + 112t⁵ + 28t⁶).
- [F] Morse counts for n = 9 equal 5040(81 + 216t + 384t² + 732t³ + 746t⁴ + 396t⁵ + 168t⁶ + 36t⁷).
- [F] Every n = 8 class agrees with Ferrario's table in P (to 8 decimals), Morse index and isotropy (isotropy = s/2).
- For n = 9, all agree except Ferrario's 26th entry (P = 89.80039). We prove s = 2, so its isotropy is 1, which confirms Hampton's suspicion.
- For n = 10:
  - Ferrario's "regular decagon" (P = 122.14138716, isotropy 10) is really a configuration with s = 4.
  - The true decagon, P = 122.14139026 with s = 20, is missing from his table, as are P = 122.14138733 (s = 4) and P = 119.28941199 (s = 1).
  - [F] We certify 12 classes with no symmetry for n = 10. DZD write 11, and the Moczurad and Zgliczyński appendix lists 11 (it lacks P = 119.28941).
  - [I] DZD's count of 11 is probably a slip.

**Corrupted inputs** (`corrupt_tests.sh` and `corrupt_tests.out`). [F] All 15 checks are rejected, also under `-O`. The corruptions were:
- a centre moved by 2^-12 (in the Arb run and in the certificate).
- a duplicated class;
- the wrong pinned body;
- a uniqueness radius of 2^-6;
- a wrong Morse index;
- a wrong symmetry order;
- a wrong labelled count.

### 5. Completeness

- [F] What is proved: at least 20 classes for n = 8, at least 42 for n = 9 and at least 67 for n = 10. All of them are non-degenerate, with proved Morse indices and symmetry orders. No completeness is proved.
- [I] The identity Σ(−1)^h·2/s cannot detect a missing pair of classes whose terms cancel. But every certified class is non-degenerate, and the counts already equal Hampton's polynomial. So Hampton's Conjecture 5 for N = 8 holds if and only if the list of 20 is complete, because any further CC would add a positive term to one coefficient. The same holds for N = 9 and the list of 42.
- **Cost of the published box method for n = 8:**
  - The reduced system has 13 unknowns, with ordering constraints that cut the domain by about n!.
  - The a priori bounds come from Moczurad and Zgliczyński's Theorems 6, 7 and 11.
  - Their box counters grow by about ×69, ×135 and ×85 per added body (3.9e4, 2.7e6, 3.7e8, then about 3.1e10 test calls at n = 7). CPU time grows by about ×200 per body.
  - [I] So n = 8 needs about 3e12 to 6e12 boxes and 0.85e9 to 1.7e9 CPU-seconds, which is 27 to 54 CPU-years in their C++ code. That is not credible on 2 Python processes in 2 hours, so I did not attempt it.
- **Levers that could change this:**
  - analytic exclusion of clustered regions, where most of their boxes die.
  - larger Krawczyk boxes, since uniqueness holds here at radius 2^-12, far larger than their bias.
  - using reflection symmetry in the search itself.

### 6. What is new, and what a specialist would ask

Existence of the 20 and 42 known classes is not new. Moczurad and Zgliczyński said it was easy, and DZD report that they tested it.

What is new, as far as I found:
- Public certificates that two independent programs check, one of them in exact rational arithmetic.
- Proved Morse indices and exact symmetry orders for every class at n = 8, 9 and 10. This turns the Morse-identity check on these lists into a theorem about the lists, and shows that Hampton's N = 8 and N = 9 conjectures are equivalent to completeness of the lists.
- Settling Ferrario's n = 9 isotropy question (s = 2).
- Correcting the n = 10 picture: the decagon is a separate class, and there are 12 classes with no symmetry rather than 11. The class at P = 119.28941 has a first rigorous existence proof here.

"No earlier report found" is the strongest claim for each of these.

A specialist would ask first: "Is the list complete? 'At least 20' was already believed." Then: "How exactly did you compute the Morse index and isotropy?"

### Files (S/threads/cc/)

| file | content |
|---|---|
| `census.py`, `merge_census.py`, `census_stats.py` | numerical census and summaries |
| `cert_arb.py` | Arb certifier |
| `verify_rational.py` | independent exact-rational verifier |
| `compare_lit.py` | comparison with Ferrario's tables |
| `cert_n{8,9,10}.json` | certificates |
| `cert_*.out`, `verify_*.out`, `verify_*_O.out`, `compare_*.out`, `merge_*.out` | outputs |
| `census_out/` | runs and logs |
| `corrupt_tests.sh`, `corrupt_tests.out`, `corrupt/` | corruption tests |
| `run_all.sh` | rerun everything |
| `sources/` | cached PDFs, text and arXiv XML |

Python is `S/work/pc-venv/bin/python` (python-flint 0.9.0). Rerun everything with `sh run_all.sh`: censuses take about 2.5 hours at 2 processes, and certification takes minutes.

### Not verified

- Completeness for any n ≥ 8.
- The Morse-index reduction argument is my own derivation [I]. It reproduces Ferrario and Hampton for n = 3 to 9.
- The Krawczyk theorem and Weyl's inequality are used as published, not re-proved.
- Literature counts come from text extracted from the PDFs. I spot-checked all of n = 8.

### Next concrete step

Run a polygon-seeded probe and a homotopy-style candidate search for n = 8 and 9, aimed at classes with tiny basins. Then decide whether to build a fast (C or numpy-vectorised) exclusion search for n = 8 restricted to the near-polygon region, where the n = 10 census failed.

## Where the named files are in the repository

Paths are relative to `org/review/2026-11/science/threads/`. Names that are not listed were not copied. `checks/STATE-NOTES.md` says why.

| Name in this report | Repository path |
|---|---|
| `census.py` | `checks/cc/census.py` |
| `census_stats.py` | `checks/cc/census_stats.py` |
| `cert_*.out` | `checks/cc/state/cert_n10.out`, `checks/cc/state/cert_n8.out`, `checks/cc/state/cert_n9.out` |
| `cert_arb.py` | `checks/cc/cert_arb.py` |
| `compare_*.out` | `checks/cc/compare_n10.out`, `checks/cc/compare_n8.out`, `checks/cc/compare_n9.out` |
| `compare_lit.py` | `checks/cc/compare_lit.py` |
| `corrupt_tests.out` | `checks/cc/corrupt_tests.out` |
| `corrupt_tests.sh` | `checks/cc/state/corrupt_tests.sh` |
| `merge_*.out` | `checks/cc/state/merge_n10.out`, `checks/cc/state/merge_n8.out`, `checks/cc/state/merge_n9.out` |
| `merge_census.py` | `checks/cc/merge_census.py` |
| `run_all.sh` | `checks/cc/state/run_all.sh` |
| `verify_*.out` | `checks/cc/verify_n10_O.out`, `checks/cc/verify_n8_O.out`, `checks/cc/verify_n9_O.out` |
| `verify_*_O.out` | `checks/cc/verify_n10_O.out`, `checks/cc/verify_n8_O.out`, `checks/cc/verify_n9_O.out` |
| `verify_rational.py` | `checks/cc/verify_rational.py` |
