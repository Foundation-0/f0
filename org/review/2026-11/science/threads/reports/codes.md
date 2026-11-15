# Code-bound tables: full report

15 November 2026. Repository head pinned by the report: gfq-codes at 9200a06.

Short note for this thread: `../codes.md`.

S is the working folder of this thread. It is archived outside the repository. Paths that start with S/ point into it. Where a file was copied into the repository, its repository path is listed at the end.

---

RESULT (code-bounds thread, 15 November 2026). All files are in S/threads/codes/.

(A) Literature. [F] The codetables.de cell page says: "Upper bounds are taken from the tables of Andries E. Brouwer, with the exception of codes over GF(7) with n>50. For most of these codes, the upper bounds are rather weak. Upper bounds for codes over GF(7) with small dimension have been provided by Rumen Daskalov." It does not name LP. Brouwer's bound server is discontinued.
His page points to codetables.de. Maruta's site (mars39.lomo.jp) covers q=7,8,9 only for k=4. A Daskalov table cited in Metodieva 2004 is for k<=7. The base cells have k>=8. No earlier report of [55,10,40]_7 or [74,10,56]_7 found, from about 10 web queries. I could not read Daskalov-Metodieva 2007 (ResearchGate 403), Daskalov-Gulliver 2001, or the Magma handbook (401).
The repo says the 2007 list has 34 LP exclusions and neither triple. I did not confirm that. "No earlier report found" is the most I can say.

Repo scope [F]. gfq-codes@9200a06 PROOF.md says GF(7) was swept for 51<=n<=60, k<=12 (81 open cells tested at the displayed upper d, 4 hits). [74,10] came from a separate sweep whose range is not stated. GF(9) only n 31..37. q=8 never scanned. notes/scouting.md just says "Status: Not started".

(B) Scan. [F] I downloaded whole tables (3 requests, plus 4 cell pages): q=7 n<=100, q=8 and 9 n<=130. I ran a column-scaled dual LP (HiGHS) on every gap cell at d = displayed upper bound, lowering d while it still excludes. Every certificate is verified with exact Fractions by two scripts that use different Krawtchouk formulas (recurrence, and binomial sum), under `python3 -I -O`. Both pass all certificates.
Corrupted certificates (negative coefficient, smaller d, smaller k, halved coefficient) are rejected by both. A wrong declared size_bound is rejected only by verify_certs.py. The repo's 18 certificates also pass my checker.

Propagation rules (upper bound u(n,k), closure to a fixed point):
- u(n,k) <= u(n-1,k)+1 (puncture)
- u(n,k) <= u(n-1,k-1) (shorten)
- u(n,k) <= u(n,k-1) (subcode)
- u(n,k) <= u(n+1,k) (zero-pad)

| q | gap cells | direct certs | improved cells | base | derived | improved beyond table's own closure |
|---|---|---|---|---|---|---|
| 7 | 4071 | 88 | 94 | 12 | 82 | 94 |
| 8 | 7202 | 737 | 1408 | 62 | 1346 | 1408 |
| 9 | 7265 | 694 | 1377 | 48 | 1329 | 916 |

For q=9, 531 table cells are not closed under the table's own propagation. They are not LP wins, and the last column removes them. These counts are "at least": the float solver found no usable dual for 2464 / 5132 / 5277 gap cells. Another 48 / 55 / 58 float candidates failed the exact check (numerical artefacts, listed in certs/gf*_uncertified.json).

Repo cross-check [F]. All six repo GF(7) cells appear with the same new bounds: 55,10 and 74,10 as base. 56,10, 56,11, 57,11 and 75,11 as derived. All twelve GF(9) cells appear (31,4 base, 11 derived).

New q=7 base cells (n,k: table upper to new upper): 56,12: 39 to 38. 66,23: 38 to 37. 92,8: 73 to 72. 93,13: 69 to 68. 94,16: 67 to 66. 95,18: 66 to 65. 98,8: 78 to 77. 98,11: 75 to 74. 99,13: 74 to 73. 100,16: 72 to 71. Plus 55,10 and 74,10.

Discrepancy [F]. Cells 56,12 (lower 33, upper 39) and 57,12 (lower 34, upper 40) lie inside the repo's stated sweep range, and the live pages confirm those values. Both have exact LP certificates (ratio f(0)/(a_0 q^k) = 0.957 and 0.691). The repo did not list them. Reason unknown.

Not verified: the 2007 and 2001 texts. Completeness of the scan. Any literature check of the GF(8) and GF(9) improvements. The LP theorem was not formalised.

Draft note (not sent, passes the prose check): draft_note_to_maintainer.md. Sender line left blank.

Next steps (not done): exact or high-precision LP to rescue the failed cells. Strengthened LP for linear codes (divisibility, integrality). The same scan for q=2..5. Obtain the Daskalov texts. Ask why the repo sweep missed 56,12 and 57,12.

Files in S/threads/codes/:
- improved_cells.csv (every improved cell: q, n, k, lower, table upper, new upper, base or derived, certificate)
- base_cells.csv (122 base cells)
- certs/gf7_certs.json, certs/gf8_certs.json, certs/gf9_certs.json, plus certs/gf*_uncertified.json
- summary.json
- verify_all.out, corrupt_results.out, repo_check.out
- scan{7,8,9}.json and scan{7,8,9}.log
- table.json, sources/ (cached tables and cell pages)
- scripts: parse.py, scan2.py, build_certs.py, analyze.py, verify_certs.py, verify_binomial.py, corrupt/ (corrupted test certificates)

Rerun, from S/threads/codes with PY=S/work/pc-venv/bin/python:
- `$PY parse.py`
- `$PY scan2.py 7` (then 8, 9)
- `$PY build_certs.py 7` (then 8, 9)
- `$PY analyze.py`
- `$PY -I -O verify_certs.py certs/gf7_certs.json` and `$PY -I -O verify_binomial.py certs/gf7_certs.json` (same for gf8 and gf9)

## Where the named files are in the repository

Paths are relative to `org/review/2026-11/science/threads/`. Names that are not listed were not copied. `checks/STATE-NOTES.md` says why.

| Name in this report | Repository path |
|---|---|
| `analyze.py` | `checks/codes/analyze.py` |
| `base_cells.csv` | `checks/codes/base_cells.csv` |
| `build_certs.py` | `checks/codes/build_certs.py` |
| `certs/gf*_uncertified.json` | `checks/codes/state/certs/gf7_uncertified.json`, `checks/codes/state/certs/gf8_uncertified.json`, `checks/codes/state/certs/gf9_uncertified.json` |
| `certs/gf7_certs.json` | `checks/codes/certs/gf7_certs.json` |
| `certs/gf8_certs.json` | `checks/codes/certs/gf8_certs.json` |
| `certs/gf9_certs.json` | `checks/codes/certs/gf9_certs.json` |
| `corrupt_results.out` | `checks/codes/corrupt_results.out` |
| `improved_cells.csv` | `checks/codes/improved_cells.csv` |
| `parse.py` | `checks/codes/parse.py` |
| `repo_check.out` | `checks/codes/state/repo_check.out` |
| `scan2.py` | `checks/codes/scan2.py` |
| `summary.json` | `checks/codes/summary.json` |
| `verify_all.out` | `checks/codes/verify_all.out` |
| `verify_binomial.py` | `checks/codes/verify_binomial.py` |
| `verify_certs.py` | `checks/codes/verify_certs.py` |
