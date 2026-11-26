#!/usr/bin/env python3
"""Check the W2 deliverable: paths, pins, columns and marks.

    python3 tools/check_site_inventory.py

Exit 0 when every backticked path in site-method.md resolves, every source pin
in site-inventory.csv names a file that exists at the pinned head with the
pinned line inside it, and the CSV uses the declared columns, kinds and marks.
The .github pin is checked by path only (profile/README.md): that repository
is not in this checkout, so its head cannot be read here.
"""
import csv
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEW = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(os.path.dirname(REVIEW)))

COLUMNS = ["page", "line", "kind", "statement", "what_is_true_now", "source",
           "now_source", "mark", "note"]
KINDS = {"date", "count", "status", "repository", "link", "member"}
MARKS = {"[F]", "[I]"}
SKIP = {"Foundation-0/.github", "Foundation-0/f0", "github.com/owner/name"}

misses = []
method = open(os.path.join(REVIEW, "site-method.md")).read()
for tok in sorted(set(re.findall(r"`([^`\s]+)`", method))):
    if ("/" not in tok or tok.endswith("/") or "@" in tok or "://" in tok
            or "<" in tok or tok in SKIP):
        continue
    if not os.path.exists(os.path.join(REPO, tok)):
        misses.append(("method path", tok))

# Line counts at the pinned heads, one git read per unique (sha, path).
# A pin is verified only when the file exists at that sha and the pinned
# line is inside it; a missing file or a line past the end is a miss.
_line_counts = {}


def line_count(sha, path):
    if (sha, path) not in _line_counts:
        out = subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (sha, path)],
                             capture_output=True)
        if out.returncode != 0:
            _line_counts[(sha, path)] = None
        else:
            # Lines, not newlines: a file with no trailing newline has one
            # more line than newline (a minified one-line file has 0).
            data = out.stdout
            _line_counts[(sha, path)] = (data.count(b"\n")
                                         + (1 if data and not data.endswith(b"\n")
                                            else 0))
    return _line_counts[(sha, path)]

rows = list(csv.DictReader(open(os.path.join(REVIEW, "site-inventory.csv"))))
if list(rows[0].keys()) != COLUMNS:
    misses.append(("columns", list(rows[0].keys())))
for r in rows:
    if r["kind"] not in KINDS:
        misses.append(("kind", r["kind"]))
    if r["mark"] not in MARKS:
        misses.append(("mark", r["mark"]))
    m = re.match(r"^([^@]+)@([0-9a-f]+):([^:]+):(\d+)$", r["source"])
    if not m:
        misses.append(("bad pin", r["source"]))
        continue
    repo, sha, path, line = m.groups()
    if repo == "Foundation-0/f0":
        total = line_count(sha, path)
        if total is None:
            misses.append(("missing file at pinned head", path))
        elif int(line) > total:
            misses.append(("line past end at pinned head",
                           "%s:%s" % (path, line)))
    if repo == "Foundation-0/.github" and path != "profile/README.md":
        misses.append(("missing profile", path))

for kind, val in misses[:20]:
    print("MISS", kind, val)
print("checked %d rows and the method note: %d miss(es)" % (len(rows), len(misses)))
sys.exit(1 if misses else 0)
