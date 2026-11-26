# The checking programs of this folder

Written by `scan_checkers.py` from the source of each program. A bare `assert` is removed by `python3 -O`, so a checker must not rely on one. The last column names the saved output of a test that feeds the program corrupted input, where there is one.

| Program | What it checks | Bare assert | Can stop with an error | Corruption test in the folder |
|---|---|---|---|---|
| `checks/charges/indep_count.py` | exact count of balance points | none | yes | `checks/charges/out/corrupt_final.log` |
| `checks/charges/repo_verifier/verify_arb.py` | exact count, the repository's verifier in corrected form | none | yes | none saved |
| `checks/four/verify/lower_bound_check.py` | lower bound on balance points | none | yes | `checks/four/verify/lower_bound_check_control.out` |
| `checks/growth/verify/lower_bound_hp.py` | lower bound on balance points, many scales | none | yes | none saved |
| `checks/growth/verify/stack_check.py` | real critical points of stacked levels | none | yes | none saved |
| `checks/growth/verify/levels_check.py` | one-level counts, numerical | none | yes | none saved |
| `checks/kflat/verify/quartic27_check.py` | 27 real critical points of a quartic | none | yes | none saved |
| `checks/l2288/l2288_independent.py` | 2,288 real realizations, exact rationals | none | yes | `checks/l2288/test_certify_corrupt.py` |
| `checks/l2288/certify.py` | 2,288 real realizations, exact rationals | none | yes | `checks/l2288/test_certify_corrupt.py` |
| `checks/l2288/certify_arb.py` | 2,288 real realizations, ball arithmetic | none | yes | none saved |
| `checks/l2288/edge_frame_independent.py` | 3,904 real realizations at 12 vertices | none | yes | `checks/l2288/v12/test_corrupt12.py` |
| `checks/codes/verify_certs.py` | code-bound certificates | none | yes | `checks/codes/corrupt_results.out` |
| `checks/codes/verify_binomial.py` | code-bound certificates, second formula | none | yes | `checks/codes/corrupt_results.out` |
| `checks/oeis/verify_all.py` | recurrence certificates | none | yes | `checks/oeis/test_corrupt.py` |
| `checks/oeis/spot_proof.py` | 46 recurrences, third program | none | yes | none saved |
| `checks/square/verify.py` | square-law proofs | none | yes | `checks/square/test_corrupt_O.log` |
| `checks/incentre/elastic_indep.py` | elastic constants, exact | none | yes | `checks/incentre/out_corrupt.txt` |
| `checks/incentre/fold_indep.py` | the fold, exact | none | yes | `checks/incentre/out_fold_corrupt.txt` |
| `checks/cc/verify_rational.py` | central configurations, exact rationals | none | yes | `checks/cc/corrupt_tests.out` |
| `checks/cc/cert_arb.py` | central configurations, ball arithmetic | none | yes | `checks/cc/corrupt_tests.out` |
| `checks/three/verify_arb3.py` | equilateral three-charge certificate | none | yes | `checks/three/out/corrupt_equi.log` |
| `checks/claims/check_claims.py` | sentences against data | none | yes | `checks/claims/control.out` |

22 programs. 22 have no bare assert, 22 can stop with an error, 15 have a corruption test saved in this folder.
