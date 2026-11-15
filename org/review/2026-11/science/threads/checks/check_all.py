#!/usr/bin/env python3
"""Re-run the gravity, acceleration, neutrino and fabric programs in a temporary copy and compare every result with the saved file.

From the checks folder:
    python3 gravity/fetch_sources.py    # once: downloads the published tables (they are not stored in the repository)
    python3 check_all.py                # all but the 6-minute acceleration fit
    python3 check_all.py --full         # also the acceleration fit
    python3 -O check_all.py             # the same, with the programs run under -O
Needs numpy and scipy (python-flint for one job). The committed files are never written.
Without gravity/sources the jobs that read published tables are SKIPPED and the exit status is 3.
Every comparison is an explicit test, so -O does not weaken it.
Exit status: 0 all compared files identical, 1 a difference or a failed run, 3 jobs skipped.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time

HERE = pathlib.Path(__file__).resolve().parent   # the checks folder
OPT = ["-O"] if sys.flags.optimize else []
FULL = "--full" in sys.argv
TABLE = "../gravity/unified/unified_table.csv"
REPO = "../gravity/unified/repo_copy"

# name, directory, script, args, compare [(kind, file)], needs sources, only with --full
# kind "stdout": the program's output equals the file. kind "file": the file the program writes equals the committed one.
JOBS = [
    ("gravity t0 sanity and corruption checks", "gravity", "t0_checks.py", [], [("stdout", "t0_checks.out")], True, False),
    ("gravity t1 SPARC galaxies", "gravity", "t1_sparc_threshold.py", [], [("stdout", "t1_sparc_threshold.out")], True, False),
    ("gravity t1b SPARC by baryonic mass", "gravity", "t1b_sparc_by_mass.py", [], [("stdout", "t1b_sparc_by_mass.out")], True, False),
    ("gravity t2 giant spirals", "gravity", "t2_massive_spirals.py", [], [("stdout", "t2_massive_spirals.out")], True, False),
    ("gravity t3 early-type galaxies", "gravity", "t3_atlas3d.py", [], [("stdout", "t3_atlas3d.out")], True, False),
    ("gravity t4 cluster tables from TeX", "gravity", "t4_data.py", [], [("file", "t4_systems.json")], True, False),
    ("gravity t4 groups and clusters", "gravity", "t4_clusters.py", [], [("file", "t4_clusters.out")], True, False),
    ("gravity t5 speed-mass line break", "gravity", "t5_btfr_break.py", [], [("file", "t5_btfr_break.out")], True, False),
    ("gravity t6 high-redshift galaxies", "gravity", "t6_highz_fdm.py", [], [("file", "t6_highz_fdm.out")], True, False),
    ("gravity separate collapse scale and 60-system test", "gravity", "g185_independent.py", ["unified/repo_copy"], [("stdout", "g185_independent.out")], True, False),
    ("gravity like-for-like grid", "gravity", "g185_like_for_like.py", [], [("stdout", "g185_like_for_like.out")], True, False),
    ("unified table", "gravity/unified", "build_table.py", [], [("file", "unified_table.csv"), ("stdout", "build_table.out")], True, False),
    ("unified fits and onset", "gravity/unified", "part2b.py", [], [("file", "part2b.out")], True, False),
    ("unified fits, extra checks", "gravity/unified", "part2c.py", [], [("file", "part2c.out")], True, False),
    ("unified variable ranking", "gravity/unified", "rank_variables.py", [], [], True, False),
    ("unified variable ranking, summary", "gravity/unified", "summarize_rank.py", [], [("file", "summarize_rank.out")], True, False),
    ("four-speed coincidence audit", "gravity/unified", "coincidence_audit.py", [], [("file", "coincidence_audit.out")], True, False),
    ("unified fit, separate code", "converge", "unified_check.py", [TABLE], [("stdout", "unified_check.out")], False, False),
    ("unified fit, circularity", "converge", "unified_circularity.py", [TABLE], [("stdout", "unified_circularity.out")], False, False),
    ("unified fit, baryon-only law", "converge", "unified_baryon_law.py", [TABLE], [("stdout", "unified_baryon_law.out")], False, False),
    ("accel theory numbers", "accel", "theory_numbers.py", [], [("stdout", "outputs/theory_numbers.txt")], False, False),
    ("accel published summaries", "accel", "muse_summary.py", [], [("stdout", "outputs/muse_summary.txt")], False, False),
    ("accel repository numbers", "accel", "repro_repo_numbers.py", [], [("stdout", "outputs/repro_repo_numbers.txt")], False, False),
    ("accel KMOS3D bound", "accel", "ubler_bound.py", ["../gravity/sources/from_accel/ubler2017_vizier.tsv", "ubler_bound.json"],
     [("stdout", "outputs/ubler_bound.txt"), ("file", "outputs/ubler_bound.json")], True, False),
    ("accel transcription check", "accel", "check_transcription.py", ["data/rc100_table3.csv"], [], False, False),
    ("accel 100-galaxy fit (about 6 minutes)", "accel", "rc100_fit.py", ["data/rc100_table3.csv", "outputs/rc100_fit.json"],
     [("stdout", "outputs/rc100_fit.txt"), ("file", "outputs/rc100_fit.json")], False, True),
    ("neutrino bounds", "neutrino", "n1_bounds.py", [TABLE], [("stdout", "n1_bounds.out")], False, False),
    ("neutrino bias scan", "neutrino", "n2_bias_scan.py", [TABLE], [("stdout", "n2_bias_scan.out")], False, False),
    ("neutrino external field in physical units", "neutrino", "n3_efe_check.py", [TABLE], [("stdout", "n3_efe_check.out")], False, False),
    ("neutrino mass and population window", "neutrino", "n4_window.py", [TABLE], [("file", "n4_window.out")], False, False),
    ("neutrino arithmetic checks", "neutrino", "check_numbers.py", [], [("stdout", "check_numbers.out")], False, False),
    ("halo model 1", "neutrino/model", "m1_requirements.py", [], [("file", "m1_requirements.out"), ("file", "m1_requirements.csv")], True, False),
    ("halo model 2 (writes m2_combos.json)", "neutrino/model", "m2_radial.py", [], [("file", "m2_radial.out")], True, False),
    ("halo model 3", "neutrino/model", "m3_fermion_halo.py", [], [("file", "m3_fermion_halo.out")], True, False),
    ("halo model 3b", "neutrino/model", "m3b_decompose.py", [], [("file", "m3b_decompose.out")], True, False),
    ("halo model 5", "neutrino/model", "m5_galaxies.py", [], [("file", "m5_galaxies.out")], False, False),
    ("halo model 5b", "neutrino/model", "m5b_lensing_mmax.py", [], [("file", "m5b_lensing_mmax.out")], False, False),
    ("woven hypothesis numbers", "fabric", "fabric_numbers.py", [], [("stdout", "fabric_numbers.out")], False, False),
]

# The program must fail on the changed input: name, directory, script, file to change, old text, new text, args
CORRUPT = [
    ("a changed speed error in the transcribed table", "accel", "check_transcription.py", "data/rc100_table3.csv", ",286,57,30,7,8.66", ",236,57,30,7,8.66", ["data/rc100_table3.csv"]),
    ("a changed error in the transcribed table", "accel", "check_transcription.py", "data/rc100_table3.csv", ",6.49,1.48,0.53,0.09", ",6.49,1.48,0.35,0.09", ["data/rc100_table3.csv"]),
    ("a changed mass in the transcribed table", "accel", "check_transcription.py", "data/rc100_table3.csv", ",9.15,0.52,7.61,1.31", ",9.15,0.52,4.61,1.31", ["data/rc100_table3.csv"]),
    ("a repository number changed by 5e-12 relative", "accel", "repro_repo_numbers.py", "repro_repo_numbers.py", "2.1575391880369907", "2.157539188046991", []),
]


def fail(msg):
    raise SystemExit("CHECK FAILED: " + msg)


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def main():
    have_src = (HERE / "gravity" / "sources" / "sparc" / "SPARC_Lelli2016c.mrt").is_file() and (HERE / "gravity" / "unified" / "repo_copy").is_dir()
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="checks-"))
    try:
        work = tmp / "checks"
        for sub in ("gravity", "accel", "neutrino", "fabric", "converge"):
            shutil.copytree(HERE / sub, work / sub, ignore=shutil.ignore_patterns("__pycache__"))
        skipped, bad, done = [], [], 0
        for name, d, script, args, compare, src, slow in JOBS:
            if slow and not FULL:
                skipped.append(name + " (--full)"); continue
            if src and not have_src:
                skipped.append(name + " (needs gravity/sources)"); continue
            cwd = work / d
            t0 = time.time()
            r = run([sys.executable, *OPT, script, *args], cwd)
            if r.returncode != 0:
                bad.append(name); print(f"FAIL  {name}: exit {r.returncode}\n{r.stderr[-300:]}"); continue
            ok = True
            for kind, rel in compare:
                got = r.stdout.encode() if kind == "stdout" else (cwd / rel).read_bytes()
                want = (HERE / d / rel).read_bytes()
                if got != want:
                    ok = False; print(f"DIFF  {name}: {rel} differs from the saved file")
            if ok:
                done += 1; print(f"OK    {name} ({time.time() - t0:.0f} s)")
            else:
                bad.append(name)
        for name, d, script, rel, old, new, args in CORRUPT:
            f = work / d / rel
            text = f.read_text()
            if old not in text:
                fail(f"corruption test text not found: {name}")
            f.write_text(text.replace(old, new, 1))
            r = run([sys.executable, *OPT, script, *args], work / d)
            f.write_text(text)
            if r.returncode == 0:
                bad.append("corruption accepted: " + name); print(f"FAIL  corruption accepted: {name}")
            else:
                done += 1; print(f"OK    rejected {name}")
        print(f"\n{done} passed, {len(bad)} failed, {len(skipped)} skipped")
        for s in skipped:
            print("SKIPPED", s)
        if bad:
            fail("; ".join(bad))
        return 3 if any("gravity/sources" in s for s in skipped) else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
