#!/usr/bin/env python3
"""check_lean.py - the proof-level check for AnchoredConservationQuotient.lean.

acq_kernel.audit_lean4_init_module is a source lint. This script does what a
lint cannot: it compiles the file with the installed `lean`, then asks Lean
which axioms every public theorem depends on. It fails if compilation fails, if
no theorem is found, or if any theorem depends on an axiom outside the standard
three (propext, Classical.choice, Quot.sound). `sorryAx` is therefore caught
wherever it comes from, including through imports.

Usage: python3 check_lean.py [path/to/file.lean]
Needs `lean` on PATH (CI pins toolchain v4.35.0).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from typing import List

ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}
NAMESPACE = "Foundation0.ACQ"


def public_theorems(source: str) -> List[str]:
    return re.findall(r"^theorem\s+([A-Za-z_][A-Za-z0-9_']*)", source, flags=re.M)


def run_lean(path: str) -> subprocess.CompletedProcess:
    return subprocess.run(["lean", path], capture_output=True, text=True, check=False)


def check(path: str) -> List[str]:
    """Return a list of failures. Empty means the file compiles and uses only standard axioms."""
    with open(path, encoding="utf-8") as fh:
        source = fh.read()
    failures: List[str] = []
    plain = run_lean(path)
    if plain.returncode != 0:
        failures.append(f"lean exited {plain.returncode}: {plain.stdout}{plain.stderr}")
        return failures
    names = public_theorems(source)
    if not names:
        return ["no public theorems found"]
    probe = source + "\n" + "".join(f"#print axioms {NAMESPACE}.{n}\n" for n in names)
    with tempfile.TemporaryDirectory() as tmp:
        probe_path = os.path.join(tmp, "Probe.lean")
        with open(probe_path, "w", encoding="utf-8") as fh:
            fh.write(probe)
        res = run_lean(probe_path)
    if res.returncode != 0:
        return [f"axiom probe exited {res.returncode}: {res.stdout}{res.stderr}"]
    text = res.stdout
    seen = 0
    for n in names:
        full = f"{NAMESPACE}.{n}"
        m = re.search(rf"'{re.escape(full)}' (does not depend on any axioms|depends on axioms: \[([^\]]*)\])", text)
        if not m:
            failures.append(f"no axiom report for {full}")
            continue
        seen += 1
        axioms = {a.strip() for a in (m.group(2) or "").split(",") if a.strip()}
        extra = axioms - ALLOWED_AXIOMS
        if extra:
            failures.append(f"{full} depends on {sorted(extra)}")
    if seen != len(names):
        failures.append(f"checked {seen} of {len(names)} theorems")
    return failures


def main(argv: List[str]) -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    path = argv[1] if len(argv) > 1 else os.path.join(here, "AnchoredConservationQuotient.lean")
    failures = check(path)
    if failures:
        for line in failures:
            print(f"LEAN_CHECK_FAILED | {line}", file=sys.stderr)
        return 1
    print(f"LEAN_CHECK_OK | {len(public_theorems(open(path, encoding='utf-8').read()))} theorems, standard axioms only")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
