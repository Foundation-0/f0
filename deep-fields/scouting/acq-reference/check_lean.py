#!/usr/bin/env python3
"""check_lean.py - the proof-level check for AnchoredConservationQuotient.lean.

acq_kernel.audit_lean4_init_module is a source lint. This script does what a
lint cannot: it compiles the file with the installed `lean`, then asks Lean
which axioms every theorem depends on. It fails if compilation fails, if
no theorem is found, or if any theorem depends on an axiom outside the standard
three (propext, Classical.choice, Quot.sound). `sorryAx` is therefore caught
wherever it comes from, including through imports.

Discovery is fail-closed. `public_theorems` finds every theorem declaration
form Lean accepts in this file: indented theorems, `private` / `protected` /
`noncomputable` theorems, attribute-prefixed theorems (`@[simp] theorem`,
including attributes on their own line), and `lemma`. `unparsed_theorem_tokens`
then scans the comment- and string-stripped source for any remaining
`theorem` / `lemma` keyword; one means a declaration form this checker does
not understand, and `check` fails rather than auditing only the theorems it
did find. Anonymous `example` blocks are out of scope by design: they are not
named, so a `sorry` inside one cannot leak into a named theorem's axioms.
Declaration forms introduced by `syntax` / `macro` are likewise out of scope
here; the Gate 4 source lint flags those tokens.

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


def _strip_lean_comments_and_strings(source: str) -> str:
    """Remove Lean comments and blank string literals, preserving newlines.

    Block comments nest (`/- ... -/`); line comments run to end of line.
    Char literals such as `'"'` are consumed as a unit so the quote cannot
    start a phantom string that swallows real code from the scan.
    """
    out: List[str] = []
    i, n, depth = 0, len(source), 0
    while i < n:
        if depth > 0:
            if source[i:i + 2] == "/-":
                depth += 1
                i += 2
            elif source[i:i + 2] == "-/":
                depth -= 1
                i += 2
            else:
                if source[i] == "\n":
                    out.append("\n")
                i += 1
        else:
            if source[i:i + 2] == "/-":
                depth = 1
                i += 2
            elif source[i:i + 2] == "--":
                while i < n and source[i] != "\n":
                    i += 1
            elif source[i] == "'" and not (i > 0 and (source[i - 1].isalnum() or source[i - 1] in "_'")):
                m = re.match(r"'(?:\\[^'\n]*|[^'\\\n])'", source[i:])
                if m:
                    out.append("'C'")
                    i += m.end()
                else:
                    out.append(source[i])
                    i += 1
            elif source[i] == '"':
                out.append('"S"')
                i += 1
                while i < n and source[i] != '"':
                    if source[i] == "\\" and i + 1 < n:
                        i += 2
                    else:
                        if source[i] == "\n":
                            out.append("\n")
                        i += 1
                if i < n:
                    i += 1
            else:
                out.append(source[i])
                i += 1
    return "".join(out)


# A theorem declaration: optional leading whitespace, any number of attribute
# groups (each possibly on its own line), optional modifiers, then `theorem`
# or `lemma` and the name. The `\s*` after each attribute group covers the
# newline when the attribute sits on its own line above the declaration.
_DECL_RE = re.compile(
    r"^[ \t]*(?:@\[[^\]]*\]\s*)*"
    r"(?:(?:private|protected|noncomputable)\s+)*"
    r"(?:theorem|lemma)\s+([A-Za-z_][A-Za-z0-9_']*)",
    re.M,
)


def public_theorems(source: str) -> List[str]:
    """Names of every theorem declaration in `source`, in file order."""
    cleaned = _strip_lean_comments_and_strings(source)
    return _DECL_RE.findall(cleaned)


def unparsed_theorem_tokens(source: str) -> List[str]:
    """`theorem` / `lemma` keywords not part of a found declaration.

    Returns one `"line N: <text>"` entry per leftover keyword. Anything here
    is a declaration form this checker does not understand, so `check` must
    fail rather than silently audit only the theorems it did find.
    """
    cleaned = _strip_lean_comments_and_strings(source)
    blanked = _DECL_RE.sub(lambda m: "\n" * m.group(0).count("\n"), cleaned)
    lines = blanked.splitlines()
    found: List[str] = []
    for m in re.finditer(r"\b(?:theorem|lemma)\b", blanked):
        lineno = blanked.count("\n", 0, m.start()) + 1
        text = lines[lineno - 1].strip() if 0 < lineno <= len(lines) else ""
        found.append(f"line {lineno}: {text}")
    return found


def run_lean(path: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(["lean", path], capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return subprocess.CompletedProcess(args=["lean", path], returncode=127, stdout="", stderr="lean not found on PATH")


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
    unparsed = unparsed_theorem_tokens(source)
    if unparsed:
        failures.append(
            "unparsed theorem/lemma declaration(s) the checker does not understand; "
            "audit is not fail-closed: " + "; ".join(unparsed)
        )
        return failures
    if not names:
        return ["no theorems found"]
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
