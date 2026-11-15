#!/usr/bin/env python3
"""Check that every backticked path in the two notes resolves to something real.

Rules:
- A token with no slash is a name or a pattern, not a path, and is skipped.
- Tokens ending in "/" or containing "*" are directories and globs, and are skipped,
  as are URLs, placeholders in angle brackets, provisional result IDs and git refs.
- A token that is a file in this folder or under tools/ resolves.
- `repo/rest` resolves if rest exists inside mirrors/repo.
- Any other slashed token resolves if the same relative path exists in some mirror,
  or if it names a branch in some mirror.
- heads.tsv, repos.tsv and mirrors/ are written by clone-all.sh, so they are allowed
  by name.
Prints the misses and exits 1 if there is any.
"""
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(TOOLS)
SOURCES = os.path.join(TOOLS, "sources")
DOCS = [os.path.join(BASE, "h1-method.md"), os.path.join(BASE, "numbers.md")]
OUT = BASE
MIRRORS = os.path.join(TOOLS, "mirrors")
repos = sorted(d for d in os.listdir(MIRRORS) if os.path.isdir(os.path.join(MIRRORS, d)))
GENERATED = {"heads.tsv", "repos.tsv", "mirrors/"}

branches = set()
for r in repos:
    out = subprocess.run(
        ["git", "-C", os.path.join(MIRRORS, r), "for-each-ref",
         "--format=%(refname:lstrip=3)", "refs/remotes/origin"],
        capture_output=True, text=True, check=False).stdout
    branches.update(line for line in out.split() if line and line != "HEAD")

misses = []
checked = 0
for doc in DOCS:
    if not os.path.exists(doc):
        continue  # each pull request carries one note
    text = open(doc).read()
    for tok in sorted(set(re.findall(r"`([^`\s]+)`", text))):
        if ("/" not in tok or tok.endswith("/") or "*" in tok or tok.startswith("-")
                or "<" in tok or ">" in tok or "://" in tok):
            continue
        if tok in GENERATED:
            continue
        if re.fullmatch(r"[^/]+/R-\d+", tok) or tok.startswith("origin/"):
            continue  # a provisional result ID or a remote ref, not a file
        checked += 1
        if os.path.exists(os.path.join(OUT, tok)):
            continue
        first, _, rest = tok.partition("/")
        if first in repos and os.path.exists(os.path.join(MIRRORS, first, rest)):
            continue
        if any(os.path.exists(os.path.join(MIRRORS, r, tok)) for r in repos):
            continue
        if tok in branches:
            continue
        misses.append((os.path.basename(doc), tok))

for doc, tok in misses:
    print("MISS", doc, tok)
print(f"checked {checked} path tokens, {len(misses)} miss(es)")
sys.exit(1 if misses else 0)
