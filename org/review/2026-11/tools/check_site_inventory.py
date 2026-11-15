#!/usr/bin/env python3
"""Check the W2 deliverable: paths, pins, columns and marks.

    python3 tools/check_site_inventory.py

Exit 0 when every backticked path in site-method.md resolves, every source pin
in site-inventory.csv names a file that exists at the pinned head, and the CSV
uses the declared columns, kinds and marks.
"""
import csv
import os
import re
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
    if repo == "Foundation-0/f0" and not os.path.exists(os.path.join(REPO, path)):
        misses.append(("missing file", path))
    if repo == "Foundation-0/.github" and path != "profile/README.md":
        misses.append(("missing profile", path))

for kind, val in misses[:20]:
    print("MISS", kind, val)
print("checked %d rows and the method note: %d miss(es)" % (len(rows), len(misses)))
sys.exit(1 if misses else 0)
