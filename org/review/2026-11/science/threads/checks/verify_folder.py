#!/usr/bin/env python3
"""One command for a reviewer: three quick checks of this folder as a whole.

  1. Every file listed in MANIFEST.sha256 is present with that checksum. (It does not test that the list is complete.)
  2. The claims ledger: listed sentences are still in their notes and the data files still support them.
  3. The checker scan: no listed checking program relies on a bare assert, and each can stop with an error.
It does not re-run the proofs. For those see the Rerun section of each note, and checks/check_all.py for the
gravity, acceleration and neutrino programs.
Usage: python3 checks/verify_folder.py      (exit status 0 only if all three pass)"""
import hashlib, os, subprocess, sys
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.normpath(os.path.join(here, ".."))
bad = 0
# 1. manifest
listed = {}
for line in open(os.path.join(root, "MANIFEST.sha256"), encoding="utf-8"):
    if line.strip():
        h, rel = line.rstrip("\n").split("  ", 1); listed[rel] = h
missing = wrong = 0
for rel, h in listed.items():
    p = os.path.join(root, rel)
    if not os.path.isfile(p): missing += 1; print("missing:", rel); continue
    if hashlib.sha256(open(p, "rb").read()).hexdigest() != h: wrong += 1; print("checksum differs:", rel)
print(f"manifest: {len(listed)} files listed, {missing} missing, {wrong} with a different checksum")
bad += missing + wrong
# 2 and 3
for name, script in (("claims ledger", "claims/check_claims.py"), ("checker scan", "claims/scan_checkers.py")):
    r = subprocess.run([sys.executable, os.path.join(here, script)], capture_output=True, text=True)
    last = (r.stdout.strip().splitlines() or [""])[-1]
    print(f"{name}: {last}" + ("" if r.returncode == 0 else f"   FAILED (exit {r.returncode})"))
    if r.returncode != 0:
        bad += 1
        for l in r.stdout.splitlines():
            if l.startswith("FAIL"): print("   ", l)
if bad: raise SystemExit(1)
print("all three checks pass")
