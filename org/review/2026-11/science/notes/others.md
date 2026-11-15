# Note: the other judged repositories

Marks: **[F]** fact, **[I]** inference. Pinned heads are in `org/review/2026-11/tools/heads.tsv` on the H1 branch (draft PR 45). This note cites `theories.md`, which arrives with draft PR 52.

## gfq-codes

- [F] `checks/delsarte_independent.py` checks all 18 certificates, held in 15 certificate files, with integer arithmetic and a three-term recurrence for the Krawtchouk polynomials, which neither of the repository's two checkers uses. It uses only the Python standard library. All pass. It raises an error instead of using `assert`. Run under `python3 -O` with one coefficient changed by 1, it exits 1 with "f positive on [d,n]".
- [I] The theorem applied is Delsarte's: if f is a combination of Krawtchouk polynomials with a_0 positive, the other coefficients non-negative, and f at most zero on d to n, then a code of minimum distance d has at most f(0)/a_0 words.
- [F] codetables.de on 15 November: GF(7) [55,10] upper bound 40, [56,10] 41, [56,11] 40, [57,11] 41, [74,10] 56, [75,11] 56. Each certificate lowers its bound by one. GF(9) [31,4] upper bound 26 and [32,4] 27, each "by the Griesmer bound".
- [F] Maruta's table of n_9(4,d): n_9(4,26) = 32 and n_9(4,27) = 33. So no [31,4,26] and no [32,4,27] code over GF(9) exists, and that was known.
- [I] The ten GF(9) cells with dimension 5 to 9 follow from those two. If an [n,k,d] code exists, so does an [n-1,k-1,d] code.
- [I] All six GF(7) cells improve the online table. They rest on two base facts, no [55,10,40] code and no [74,10,56] code. The other four follow by puncturing or shortening. The GF(9) cells correct the online table and are not new.

## point-charges

- [F] Lead run in an isolated environment with the repository's requirements: `verify_arb.py certificates/*.json` exits 0 and reports exactly 4, 9, 24, 29 and 44 non-degenerate equilibria for 3 to 7 charges. The check for 7 charges covers 394,265 boxes.
- [F] The repository says the five-charge configuration comes from a counterexample published in July 2026, and that the three and four charge cases are open.
- [F] Reader finding: the Lean file holds definitions only. For 7 charges only one of the two verifiers finishes.
- [F] REPRODUCED here means a run of the repository's own verifier. No check with separate code exists yet, so the separate-code check is still to come. Of the results judged here, only the 880 realizations and the 18 code bounds have one.

## finite-state-proofs

[F] Reader run: `verify.py` and `verify_independent.py` both pass with exact integers, also under `-O`, and reject a changed coefficient and a changed initial term. [I] The proof depends on a prose argument that the counting problem equals the transfer-matrix model. That argument is short and awaits human review.

## cfrp-strengthening

[F] Reader run: the checker matches ten printed values, and `verify.py` rejects five corruptions in both modes. The worked example the values come from is not in the repository. The repository discloses that the beam fails one code section by a hand calculation.

## plate-eclipses

[F] Reader re-fit of the stored eclipse times gives a period of 4343.28 +/- 1.06 days against the stated 4343.3 +/- 1.1. Two of the timing errors are assumed.

## Not yet judged

math0 (integer multiplication study), nhanes-bioimpedance, virtual-human, vitruvian3d, plate-novae, overdue-data, rism-anon, two rows in f0, and two of the three plate-eclipses rows (the third, the period re-fit, is judged above). project-asma has 128 claim rows in the H1 claims index. None was judged and verdicts.csv holds no row for them. The reader agents' notes on each are summarised in `theories.md`.
