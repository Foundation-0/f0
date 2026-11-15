#!/usr/bin/env python3
"""Check sentences in the notes against the data files they rest on.

The team review of this folder found that no proved result failed, and that most defects were sentences that said
more than the files beside them. A result had a second program checking it. A sentence had nobody. This program is
the second check for sentences: each entry of claims.json names a note, a piece of text that must appear in it, and
a test on a data file in this folder. If the text is gone from the note, or the data no longer supports it, the
program stops with a non-zero exit status.

Kinds of test:
  json    {"file", "path": [keys or indexes], "equals"}        a value in a JSON file
  jsonrow {"file", "rows": [keys to the list], "where": {key: value}, "field", "equals"}   a field of the one matching row
  line    {"file", "contains"}                                  a line of a text file contains this text
  count   {"file", "pattern", "equals"}                         number of lines of a text file that contain a pattern
  files   {"glob", "equals"}                                    number of files matching a pattern
  csvrows {"file", "equals"}                                    number of data rows of a CSV file (header not counted)
Usage: check_claims.py [folder]      (the folder that holds the notes; default: two levels above this file)"""
import json, sys, os, glob
here = os.path.dirname(os.path.abspath(__file__))
root = sys.argv[1] if len(sys.argv) > 1 else os.path.normpath(os.path.join(here, "..", ".."))
claims = json.load(open(os.path.join(here, "claims.json")))
bad = 0
def fail(c, why):
    global bad
    bad += 1; print(f"FAIL  {c['note']}: \"{c['text'][:70]}\"  ->  {why}")
for c in claims:
    note = os.path.join(root, c["note"])
    if not os.path.isfile(note): fail(c, "note not found"); continue
    if c["text"] not in open(note, encoding="utf-8").read(): fail(c, "the text is no longer in the note"); continue
    t = c["test"]; kind = t["kind"]
    try:
        if kind == "json":
            v = json.load(open(os.path.join(root, t["file"])))
            for k in t["path"]: v = v[k]
            if v != t["equals"]: fail(c, f"{t['file']} gives {v!r}, the note needs {t['equals']!r}"); continue
        elif kind == "jsonrow":
            rows = json.load(open(os.path.join(root, t["file"])))
            for k in t.get("rows", []): rows = rows[k]
            hit = [r for r in rows if all(abs(r[k] - v) <= 1e-9 * max(1.0, abs(v)) if isinstance(v, float) else r[k] == v for k, v in t["where"].items())]
            if len(hit) != 1: fail(c, f"{len(hit)} rows of {t['file']} match {t['where']}"); continue
            if hit[0][t["field"]] != t["equals"]: fail(c, f"{t['file']} gives {hit[0][t['field']]!r}, the note needs {t['equals']!r}"); continue
        elif kind == "line":
            if not any(t["contains"] in l for l in open(os.path.join(root, t["file"]), encoding="utf-8", errors="replace")): fail(c, f"no line of {t['file']} contains \"{t['contains']}\""); continue
        elif kind == "count":
            n = sum(1 for l in open(os.path.join(root, t["file"]), encoding="utf-8", errors="replace") if t["pattern"] in l)
            if n != t["equals"]: fail(c, f"{n} lines of {t['file']} contain \"{t['pattern']}\", the note needs {t['equals']}"); continue
        elif kind == "files":
            n = len(glob.glob(os.path.join(root, t["glob"])))
            if n != t["equals"]: fail(c, f"{n} files match {t['glob']}, the note needs {t['equals']}"); continue
        elif kind == "csvrows":
            n = sum(1 for l in open(os.path.join(root, t["file"]), encoding="utf-8") if l.strip()) - 1
            if n != t["equals"]: fail(c, f"{t['file']} has {n} rows, the note needs {t['equals']}"); continue
        else:
            fail(c, f"unknown kind of test {kind}"); continue
    except (OSError, KeyError, IndexError, ValueError, TypeError) as e:
        fail(c, f"could not run the test: {type(e).__name__}: {e}"); continue
    print(f"ok    {c['note']}: \"{c['text'][:70]}\"")
print(f"{len(claims) - bad} of {len(claims)} claims hold")
if bad or not claims: raise SystemExit(1)
