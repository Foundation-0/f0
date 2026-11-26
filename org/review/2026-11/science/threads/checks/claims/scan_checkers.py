#!/usr/bin/env python3
"""List the checking programs of this folder and test two things about each one from its source:
that it has no bare `assert` (which `python3 -O` removes), and that it can stop with an error
(a `raise`, or a call that exits with a status). It also tests that the saved output of each program's
corruption test is in the folder. The result is written to checkers.md beside this file.

The team review found that a sentence saying "every checker raises an error and was run under -O on corrupted
input" was wider than the evidence. This table replaces that sentence. A program not listed here is not claimed
as a checker: counts, scans and traces only compute and print.
Usage: scan_checkers.py   (exits with status 1 if a listed checker has a bare assert, cannot stop with an
error, or a listed evidence file is missing)"""
import ast, os, sys
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.normpath(os.path.join(here, "..", ".."))
# program, what it checks, saved corruption test ("" when there is none)
CHECKERS = [
 ("checks/charges/indep_count.py", "exact count of balance points", "checks/charges/out/corrupt_final.log"),
 ("checks/charges/repo_verifier/verify_arb.py", "exact count, the repository's verifier in corrected form", ""),
 ("checks/four/verify/lower_bound_check.py", "lower bound on balance points", "checks/four/verify/lower_bound_check_control.out"),
 ("checks/growth/verify/lower_bound_hp.py", "lower bound on balance points, many scales", ""),
 ("checks/growth/verify/stack_check.py", "real critical points of stacked levels", ""),
 ("checks/growth/verify/levels_check.py", "one-level counts, numerical", ""),
 ("checks/kflat/verify/quartic27_check.py", "27 real critical points of a quartic", ""),
 ("checks/l2288/l2288_independent.py", "2,288 real realizations, exact rationals", "checks/l2288/test_certify_corrupt.py"),
 ("checks/l2288/certify.py", "2,288 real realizations, exact rationals", "checks/l2288/test_certify_corrupt.py"),
 ("checks/l2288/certify_arb.py", "2,288 real realizations, ball arithmetic", ""),
 ("checks/l2288/edge_frame_independent.py", "3,904 real realizations at 12 vertices", "checks/l2288/v12/test_corrupt12.py"),
 ("checks/codes/verify_certs.py", "code-bound certificates", "checks/codes/corrupt_results.out"),
 ("checks/codes/verify_binomial.py", "code-bound certificates, second formula", "checks/codes/corrupt_results.out"),
 ("checks/oeis/verify_all.py", "recurrence certificates", "checks/oeis/test_corrupt.py"),
 ("checks/oeis/spot_proof.py", "46 recurrences, third program", ""),
 ("checks/square/verify.py", "square-law proofs", "checks/square/test_corrupt_O.log"),
 ("checks/incentre/elastic_indep.py", "elastic constants, exact", "checks/incentre/out_corrupt.txt"),
 ("checks/incentre/fold_indep.py", "the fold, exact", "checks/incentre/out_fold_corrupt.txt"),
 ("checks/cc/verify_rational.py", "central configurations, exact rationals", "checks/cc/corrupt_tests.out"),
 ("checks/cc/cert_arb.py", "central configurations, ball arithmetic", "checks/cc/corrupt_tests.out"),
 ("checks/three/verify_arb3.py", "equilateral three-charge certificate", "checks/three/out/corrupt_equi.log"),
 ("checks/claims/check_claims.py", "sentences against data", "checks/claims/control.out"),
]
def facts(path, seen=None):
    """bare asserts and the ability to stop with an error, in the program and in the modules it imports
    from its own folder (a checker often keeps its `check` helper in a sibling file)."""
    seen = seen if seen is not None else set()
    if path in seen: return 0, False
    seen.add(path)
    tree = ast.parse(open(path, encoding="utf-8").read())
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    stops = any(isinstance(n, ast.Raise) for n in ast.walk(tree)) or any(
        isinstance(n, ast.Call) and getattr(n.func, "attr", getattr(n.func, "id", "")) in ("exit", "SystemExit") for n in ast.walk(tree))
    names = [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names] + [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module]
    for name in names:
        sib = os.path.join(os.path.dirname(path), name.split(".")[0] + ".py")
        if os.path.isfile(sib):
            a, st = facts(sib, seen); n_assert += a; stops = stops or st
    return n_assert, stops
rows = []; bad = 0
for prog, what, ev in CHECKERS:
    p = os.path.join(root, prog)
    if not os.path.isfile(p): rows.append((prog, what, "MISSING", "", ev)); bad += 1; continue
    n_assert, stops = facts(p)
    ev_ok = (ev == "") or os.path.isfile(os.path.join(root, ev))
    if n_assert or not stops or not ev_ok: bad += 1
    rows.append((prog, what, "none" if n_assert == 0 else f"{n_assert} FOUND", "yes" if stops else "NO", (ev if ev_ok else ev + " MISSING") if ev else "none saved"))
out = ["# The checking programs of this folder", "",
       "Written by `scan_checkers.py` from the source of each program. A bare `assert` is removed by `python3 -O`, so a checker must not rely on one. The last column names the saved output of a test that feeds the program corrupted input, where there is one.", "",
       "| Program | What it checks | Bare assert | Can stop with an error | Corruption test in the folder |", "|---|---|---|---|---|"]
out += [f"| `{a}` | {b} | {c} | {d} | {('`' + e + '`') if e not in ('none saved',) and 'MISSING' not in e else e} |" for a, b, c, d, e in rows]
n_ev = sum(1 for r in rows if r[4] != "none saved" and "MISSING" not in r[4])
out += ["", f"{len(rows)} programs. {sum(1 for r in rows if r[2] == 'none')} have no bare assert, {sum(1 for r in rows if r[3] == 'yes')} can stop with an error, {n_ev} have a corruption test saved in this folder.", ""]
open(os.path.join(here, "checkers.md"), "w").write("\n".join(out))
print(out[-2])
if bad: raise SystemExit(f"{bad} listed programs fail the scan")
