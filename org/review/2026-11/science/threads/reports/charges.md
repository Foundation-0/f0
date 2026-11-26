# Point charges: independent count and growth: full report

15 November 2026.

Short note for this thread: `../point-charges.md`.

S is the working folder of this thread. It is archived outside the repository. Paths that start with S/ point into it. Where a file was copied into the repository, its repository path is listed at the end.

---

**Result.** I wrote a separate program, `indep_count.py`. It reads only the sites and charges from each certificate. Using Arb ball arithmetic and exact rationals, it proves these counts of critical points in R^3 minus the sites, all non-degenerate, written as index-1/index-2 splits:
- C3: 4 (1/3)
- C4: 9 (3/6)
- C5: 24 (10/14)
- C6: 29 (12/17)
- C7: 44 (19/25)

All five match the certificates. m2−m1 = n−1 holds every time. I derived that relation myself (Poincaré–Hopf, plus trace H = 0 so there is no index 0 or 3). The program does not use it. Each of my zeros lies in exactly one certificate box with the same index. Box counts: 1,801 / 6,009 / 39,617 / 58,561 / 128,817. C7 takes 67 s, against 394,265 boxes for the repo's `verify_arb.py`.
**This is an independent check, not a reproduction.** I read `certify.py`, `ia.py` and `verify_arb.py` only after my counts existed. I had read NOTE.md's description of their method before writing mine.

**How the method differs** from the repo's (Krawczyk on boxes, interval enclosures, dominance test, Gershgorin indices, bisection):
- **Zeros:** found by my own Newton search, never from certificate boxes. Existence, uniqueness and non-degeneracy come from a contraction argument on balls, using bounds on the third derivative.
- **Index:** read from the sign of det H, since trace H = 0.
- **Far field:** a half-space lemma in exact rationals.
- **Near each charge:** a fixed exclusion ball per charge, checked in exact `Fraction` arithmetic.
- **Elsewhere:** two Taylor tests at box centres, using bounds I proved: ‖D²(1/r)‖ = 2/r³ and ‖D³(1/r)[v,·,·]‖ ≤ 6/r⁴.
- **Subdivision:** octree.
- **Shared:** only python-flint.

**Negative controls**, all under `python -O`, exit 2 on mismatch:
- C7 with count set to 43: proves 44, rejects.
- C5 with q5 = 441/131072: proves 6.
- C6 with one site moved: proves 5.
- C7 with q7 = 136000/2^60: proves 36.
- Garbage zero boxes: still proves 24, because the proof never reads them.

**Bug in the repo verifier.** `verify_arb.py` uses bare `assert` for every proof step (lines 180, 190, 195, 201, 245). Under `python -O` it printed "VERIFIED … exactly 10 zeros" for the C4 certificate with one zero box duplicated, and it silently accepts a wrong index. The committed counts are unaffected, because CI runs without `-O`. The fix is to replace each assert with a check that raises.

**Literature (goal 2i).** Best published counts, none of them exact:
- n=5: ≥24 (ABK).
- n=6: nothing above 25 found.
- n=7: ≥44, but only as ABK Prop 1 "k ≥ 4+20m" at m=2.
- n=8: 25, from EFO's square antiprism (numerical).
- n=9: ≥64 (ABK Prop 1, m=3).

The six-charge count of 29 appears nowhere outside the repo. I searched the arXiv API, the full texts of ABK, EFO and Duan, and the web.

**Growth (goal 2ii).** The known rules are:
- the ABK pair (+20 for 2 charges);
- adding one charge (+3 or +5);
- clustering, M(a+b−1) ≥ M(a)+M(b). This one is my argument. By Fekete's lemma, clustering cannot improve the asymptotic slope.

Taking the best of these, every construction is linear with slope 10 (10n−26 for odd n, 10n−31 for even n). It beats Maxwell only at n = 5, 6, 7, ties at n = 8, 9, and falls short for every n from 10 to 40.

**New counts at n=8 and n=9**, numerical search then certified by my program:
- n=8: C7 plus a charge 2^−86 at the centre has exactly **49** (21/28).
- n=9: C7 plus a third pair at ±2^−21(1,1,1) with charge 164272/2^100 (ABK's formula) has exactly **64** (28/36). The working window is narrow: ±0.5% gives 52 or 56.

The repo's own `verify_arb.py` also verified both from my zero boxes, so two programs agree. Both tie Maxwell's bound. Neither beats it. I found no earlier report of the explicit 49 or 64.

**Conjectures (goal 2iii).** A: let h(d) be the most real critical points a degree-d harmonic polynomial on R³ can have. If h(d) grows faster than d², then nested local jets built from about d² charges could give superlinear growth. B: M(n)/n stays bounded. I only ran random sampling for A (counts are small, but it does not measure the maximum), so it does not test A. Both are open.

**Not done.**
- The derivative-norm lemmas are proved by hand and checked numerically only.
- The clustering rule is a written argument, not a formal proof.

**Next steps.**
1. Replace the asserts in `verify_arb.py` and run the negative controls under `-O` in CI.
2. Add n8 and n9 as repo certificates.
3. Maximise h(d) for d = 3 to 10.

**Rerun** (in S/threads/charges, P = S/work/pc-venv/bin/python):
- `./run_all.sh`
- `./run_corrupt.sh`
- `$P -I -O indep_count.py configs/n9.json out/n9.json`

Files are in S/threads/charges/:
- indep_count.py
- check_lemmas.py
- compare_hints.py
- run_all.sh
- run_corrupt.sh
- make_corrupt.py
- corrupt/
- configs/ (n8.json, n9.json, and the repo-format copies)
- explore_n8_n9.py
- growth.py
- harmonic_crit.py
- to_repo_format.py
- repo_copy/ (unchanged copy of verify_arb.py)
- repo_O_test/
- sources/ (arXiv pages fetched and cached)
- out/ (all logs and JSON results)

## Where the named files are in the repository

Paths are relative to `org/review/2026-11/science/threads/`. Names that are not listed were not copied. `checks/STATE-NOTES.md` says why.

| Name in this report | Repository path |
|---|---|
| `check_lemmas.py` | `checks/charges/check_lemmas.py` |
| `compare_hints.py` | `checks/charges/state/compare_hints.py` |
| `configs/` | `checks/charges/configs/` (3 files) |
| `configs/n9.json` | `checks/charges/configs/n9.json` |
| `explore_n8_n9.py` | `checks/charges/explore_n8_n9.py` |
| `growth.py` | `checks/charges/growth.py` |
| `harmonic_crit.py` | `checks/charges/state/harmonic_crit.py` |
| `indep_count.py` | `checks/charges/indep_count.py` |
| `make_corrupt.py` | `checks/charges/make_corrupt.py` |
| `n8.json` | `checks/charges/configs/n8.json`, `checks/charges/state/out/n8.json` |
| `n9.json` | `checks/charges/configs/n9.json`, `checks/charges/state/out/n9.json` |
| `out/` | `checks/charges/out/` (13 files) |
| `out/n9.json` | `checks/charges/state/out/n9.json` |
| `run_all.sh` | `checks/charges/state/run_all.sh` |
| `run_corrupt.sh` | `checks/charges/state/run_corrupt.sh` |
| `to_repo_format.py` | `checks/charges/state/to_repo_format.py` |
