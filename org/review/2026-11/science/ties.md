# F3: how the work ties together

Science pass, 15 November 2026. This records which claims use which results, constants and data, where the same quantity appears with different values, where repositories disagree, and which "convergence" claims hold. Pinned heads are in `org/review/2026-11/tools/heads.tsv` on the H1 branch (draft PR 45). The check programs and outputs cited as `checks/...` are in `org/review/2026-11/science/checks/` on draft PR 51.

Marks: **[F]** a fact read from a repository or a run, **[I]** an inference.

## What the ties are

[I] The repositories are tied together far less than the site and the project tables suggest. There are four kinds of tie, in order of strength.

1. **One real chain of dependent claims.** Inside gravity, six claims rest on one hand-entered data table.
2. **Quotation.** astr0 is an index page and holds two files. physics0 is an index page with a small data folder. math0 is an index page plus one study. Their project tables quote the status of other repositories.
3. **Copies.** One table of 15 literature checks sits in 12 repositories and supplies 180 of the 383 indexed results.
4. **Shared method.** Three unrelated results use the same proof technique, which is the strongest thing the organisation has.

No result in one repository is used as an input to a result in another. [F] The reader agents searched each repository for the names of the others and for shared numbers. The only cross-repository numbers found are quotations in README tables.

## Graph

```mermaid
graph TD
  subgraph gravity
    C19[C-19 hand-placed threshold 388 km/s] --> C21
    T[126-row table, wave7 lines 34-141] --> C21[C-21 three-parameter fit]
    T --> C22[C-22 plateau]
    C21 --> C23[C-23 one-parameter fit, sigma_J 180-190]
    T --> C23
    C23 --> C26[C-26 fixed sigma_J = 185.59]
    PS[Planck 2018 spectrum, EH98] --> C26
    C26 --> C27[C-27 four-way convergence]
    C26 --> C32[C-32 scale at z = 6.08]
    C08[C-08 SPARC and KiDS fits] --> C09[C-09 interpolator scan]
    AE[acceleration-evolution]
  end
  subgraph index pages
    P0[physics0 README]
    M0[math0 README]
    A0[astr0 README]
  end
  PC[point-charges: n = 3 to 7 charges] -. quoted .-> P0
  IL[incentre-lattices] -. quoted .-> M0
  GF[gfq-codes: 18 bounds in 15 files] -. quoted .-> M0
  M0 -- census of open table entries --> GF
  RR[rigid-realizations: L880] -. quoted .-> M0
  EX[exoplanets-frontier] -. candidate count .-> A0
  EXT[eumemic/exoplanets candidate list, not included] --> EX
  EX -. candidate list .-> GD[gaia-dr4 plan]
  VH[virtual-human graph core, pinned copy] --> PA[project-asma]
  PA -. checkout read by validate_asma_interventions.py .-> VH
  FC[fact-check.md, 15 literature checks] ==> R12[12 repositories, 180 indexed rows]
  K[Krawczyk boxes in exact arithmetic] --- RR
  K --- PC
  K -. planned .-> CO[certified-orbits, relative-equilibria]
  AE -. cites notes not on main .-> FR[fractals, physics0, astr0]
```

Solid arrows are inputs. Dotted arrows are quotations or plans. The double arrow is a copy. EXT is the candidate list of the outside project eumemic/exoplanets, which exoplanets-frontier starts from. project-asma holds a pinned copy of `vh/graph/core.py` (`project-asma@4817821:NOTICE:70`). The virtual-human script `scripts/validate_asma_interventions.py` reads a project-asma checkout (`--asma-root`).

## 1. The gravity chain

- [F] `gravity@8f96c4b:wave9_scale_convergence_audit.py:14` and `wave10_covariant_jeans_unification.py:14` import the Wave 7 script and call `build_catalog()`. Claims C-21, C-22, C-23 part 3, C-26 and C-27 all use that one table.
- [F] The table is typed into the script. 28 of its 126 rows (the lensing clusters) are not measured ratios. They are computed from each cluster's mass by a halo model with an assumed baryon fraction of 0.130 (`wave7...py:101-119`).
- [F] 10 more rows (the rich groups) are divided by a factor that changes with velocity dispersion and has a knee at 180 km/s (`wave7...py:81`). Those rows are excluded from the 60-system subset and included in the 126-system fits.
- [F] One more row, NGC4125_X, is set by hand to 1.70 (`wave7...py:95`). With the 28 and the 10, that is 39 of the 126 rows that are not published values: 38 computed and one set by hand.
- [I] A claim that rests on C-26 inherits these properties. That includes the forecast in C-27 and the scale at redshift 6.08 in C-32.

## 2. The same quantity with different values

| Quantity | Values | Where | Does it matter |
|---|---|---|---|
| Hubble constant | 67.36, 67.4, 70, 72, 73.0 km/s/Mpc | gravity: `wave10...py:30`, `CLAIMS.md:42`, `acceleration-evolution/test_model.py:44`, `wave7...py:102`, `CLAIMS.md:48` | [I] Each use is defensible alone. Results that combine them (C-23, C-26) mix a table built at 72 and 73 with a scale built at 67.36 |
| Acceleration scale | 1.20e-10 (fitted a_0) and 1.0422e-10 (c H_0 / 2 pi) m/s^2 | gravity: `CLAIMS.md:118` and `:72,94` | [F] C-18 computes the MOND radius with the second value. C-24 uses the first |
| Baryon fraction in clusters | 0.130, 0.105, and 0.1565 (cosmic) | gravity: `wave7...py:119`, `CLAIMS.md:121`, `wave7...py:27` | [I] Yes. The data rows are built with 0.130 and the model that is tested on them uses 0.105 |
| Number of planet candidates | 665, 3,543, 2,421 | exoplanets-frontier `HANDOFF.md:31` and `PLAIN_GUIDE.md:32` (665), `CHANGELOG.md:8` (3,543), `CLAIMS.md:51,53` (2,421). gaia-dr4 and astr0 quote 665 | [F] `CLAIMS.md:53` reconciles 3,543 to 2,421: 1,122 leaked validation rows were removed. The 665 upstream count is not reconciled in any file |
| Dimensions verified for the elastic theorem | n = 2 to 6, and n = 2 to 8 | incentre-lattices `research/1-mechanics.md` and `docs/audit.md` | [F] Reader finding. The second is current |
| Rod radius threshold | (sqrt(3) - 1) r = 0.5176 r, and a/r < 1/2 | vitruvian3d `research/connectors_proof.md:27,57`, `README.md:22`, `research/status.md:15` | [F] Both are in the proof. The first is the probe-exclusion threshold and the second is the simultaneous-certificate bound. The summaries state the second, which is the stricter one |
| Symbol a_0 | an acceleration scale (gravity), a Bohr radius (fractals) | gravity `CLAIMS.md:18`. fractals `README.md:289`, where it is written a₀, and `gravitational-atom/atom.js:6`, where it is a0 | [I] A naming collision only |

## 3. Where repositories disagree

- [F] `math0@e649250:README.md:22` says gfq-codes is "Not started". `gfq-codes@9200a06:README.md:24` says "research underway" and holds 15 certificate files that cover 18 statements.
- [F] `physics0@913468f:README.md:14` quotes point-charges counts for 4, 5 and 6 charges and leaves out the count of 44 for 7 charges, which `point-charges@a2fd159:README.md:22-24` says only one verifier proves. The two-verifier statement is in `point-charges README.md:41-42` (3 to 6 charges) and `physics0 README.md:31-32` (a general rule, "where possible"). The quotation is correct for what it includes.
- [F] `gravity@8f96c4b:index.html:223-224` states as results what `CLAIMS.md:156,173` limits to assigned prescriptions. See `recheck-1114.md`, P3a.
- [F] gravity says companion notes exist in fractals, physics0 and astr0. None of the three mentions the gravity repository on its default branch. The notes are in open pull requests fractals 51, physics0 15 and astr0 4, from the branch `aeva/acceleration-evolution-links`. Their heads are the commits that gravity's `PROVENANCE.md` pins.
- [F] Reader finding: incentre-lattices `research/1-mechanics.md` says "No prior reference found" for the elastic formulas. Its README says priority is unresolved and names Borcea and Streinu 2021 for the framework.

## 4. Copies

- [F] `notes/reports/fact-check.md` is the same file in 12 repositories (`o1-copies.csv`). It is a check, dated 19 October, that 15 statements in scouting reports match their sources. H1's rule indexed it as 15 results in each repository.
- [I] 180 of the 383 rows in `results-index.csv` are this one table. nhanes-bioimpedance has its own fact check, which adds 9 more. The count of indexed results that belong to the repositories themselves is 194.
- [F] Six other scouting reports are also shared between two to four repositories each (`o1-copies.csv`).

## 5. Which "convergence" claims hold

| Claim | Where | Holds? |
|---|---|---|
| Four speeds near 185 km/s agree | gravity C-27, `CLAIMS.md:139` | **No, not as stated.** See below |
| A cross-repository "convergence research collection" | `gravity@8f96c4b:research/convergences-20261112/README.md` | Makes no convergence claim. It says "A shared fundamental theory is not assumed" and that its checks "do not establish new physical laws" |
| A convergence certificate file | exoplanets-frontier `results/convergence_certificates.json` | A list of file hashes. The name is the only link |
| A cross-project review | vitruvian3d `research/reviews/convergence-20261112/` | Not judged in this pass |

### The four-way convergence, C-27

The claim compares "four independently defined velocity scales". Each number reproduces. The independence does not hold. Commands and output are in `org/review/2026-11/science/checks/g185_independent.py` and `g185_independent.out`, on draft PR 51.

| Scale | Value in the claim | What sets it | Range under equally common choices |
|---|---|---|---|
| Collapse scale from the Planck spectrum | 185.59 km/s | Halo defined at 200 times critical density, sigma = V/sqrt(2) | 153 (200 times mean), 166 (virial), 216 (500 times critical) |
| Milgrom rotation speed | 175.82 km/s | Galaxy mass chosen as 6e10 solar masses | 148 at 3e10, 200 at 1e11 |
| Gas cooling scale | 178.42 km/s | Overdensity chosen as 1000 | Exactly 0.17842 km/s per unit of overdensity: 36 at 200, 446 at 2500 |
| Fitted onset in groups | 180 to 190 km/s | A fit that compares two different ratios, with the dark-to-baryon ratio fixed at 8.52 | Chi-squared within 1 of its minimum from 180 to 204 as fitted. With like compared to like and the ratio left free, the onset stays near 185 to 200 and the ratio drops to about 4 |

- [F] The fitted onset is the one number that survives a like-for-like comparison (`org/review/2026-11/science/checks/g185_like_for_like.out`, regenerated by `g185_like_for_like.py` in the same directory). What does not survive is "zero fitted parameters": with the ratio fixed at 8.52 the like-for-like chi-squared is 256.5 on 60 systems, and the table prefers a ratio near 4.
- [F] In the 60-system subset no system lies between 202 and 282 km/s. The onset is located by the assumed curve shape across that gap.
- [I] Three of the four numbers are set by a choice the claim does not derive. A choice that can move a number by a factor of two cannot count as independent agreement at the 5% level.
- [I] The coincidence that galaxies, gas cooling and the present-day collapse mass share a scale near 200 km/s is real and well known. It is the textbook account of why bright galaxies have the masses they do. The claim's label already says CONJECTURE for the common origin. The word "independently" is what overstates it.

## 6. The tie that does hold: one proof method

- [F] rigid-realizations and point-charges both prove existence and exact counts by placing a small box around each solution and showing in exact or interval arithmetic that the box holds one solution. certified-orbits and relative-equilibria plan the same method. finite-state-proofs and gfq-codes use exact integer certificates.
- [I] This is where the organisation's results are strongest, and it is the natural common base. A shared, fail-closed checker for box certificates would serve at least four repositories. F8 proposes it.
