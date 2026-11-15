# Note: exoplanets-frontier

Pinned head `exoplanets-frontier@3bc0163`. Marks: **[F]** fact, **[I]** inference. Nothing here was re-run against the survey archives, which needs network downloads.

| Claim | Lead check | Reader finding |
|---|---|---|
| C-01 | [F] `results/blind_verification_s106_s107.csv` has 39 rows. 22 are CONFIRMED_ON_SCHEDULE, from 18 distinct stars. The lowest passing signal-to-noise is 3.05, and the rule is `snr >= 3.0` (`vetter.py:121`) | 9 rows are inconclusive, 5 marginal, 2 in a data gap, 1 a timing offset |
| C-02 | not checked | 33 rows in the audit file against 24 in the claim. The quoted "MES = 369.8" is the `err_ppm` column |
| C-03 | [F] Quoted hash `6c2a1823`. The file hashes to `2c6d4454` | |
| C-04 | [F] Quoted hash `a81f7b1c`. The file hashes to `50640b01` | Period and timing values in the claim differ from the file |
| C-05 | not checked | The 14.35 day signal is in no results file |
| C-06 | [F] Quoted hash `7f735d0b`. The file hashes to `a73e65e1` | Offsets differ. The file's verdict for the named star is ON_TARGET_UNRESOLVED_NEIGHBOR |
| C-07 | [F] Quoted hash matches the file | |
| C-08 | [F] `results/platinum_followup_targets.csv`: 348 rows, `ruwe` is 1.0 in every row, `nss` is 0 in every row. `blend_gaia.py:24,37,42` set those defaults | The coolest of the 348 is at 327 K. The claim names 426 K and 453 K |

[I] The results files were regenerated on 13 November after the ledger was written. The ledger and the files now describe different runs. Regenerating the ledger from the files would remove most of these mismatches. The RUWE default and the 3 sigma pass rule would remain.

[I] The count of candidates the work starts from is given as 665, 3,543 and 2,421 in different files. The base catalogue comes from an outside project that is not included, so none of the three can be checked from the repository.
