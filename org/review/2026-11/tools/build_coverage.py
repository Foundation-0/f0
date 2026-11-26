#!/usr/bin/env python3
"""Coverage table and the H1 method note."""
import collections
import csv
import os

TOOLS = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(TOOLS)
SOURCES = os.path.join(TOOLS, "sources")
OUT = BASE

inv = list(csv.DictReader(open(os.path.join(OUT, "inventory.csv"))))
claims = list(csv.DictReader(open(os.path.join(OUT, "claims-index.csv"))))
census = {r["repository"]: r for r in csv.DictReader(open(os.path.join(OUT, "checks-census.csv")))}
results = list(csv.DictReader(open(os.path.join(OUT, "results-index.csv"))))
results_by_repo = collections.Counter(r["repository"] for r in results)
heads = {}
for line in open(os.path.join(TOOLS, "heads.tsv")):
    name, branch, sha = line.rstrip("\n").split("\t")
    heads[name] = (branch, sha)

by_repo = collections.defaultdict(list)
for r in inv:
    by_repo[r["repository"]].append(r)
claims_by_repo = collections.Counter(r["repository"] for r in claims
                                     if r["kind"] == "claim")
kinds_by_repo = collections.defaultdict(collections.Counter)
for r in claims:
    kinds_by_repo[r["repository"]][r["kind"]] += 1

rows = []
for name in sorted(heads):
    rs = by_repo.get(name, [])
    tc = collections.Counter(r["type"] for r in rs)
    rows.append({
        "repository": name,
        "pinned_head": heads[name][1],
        "inventory_rows": len(rs),
        "claims": tc["claims"],
        "notes": tc["note"],
        "readmes": tc["readme"],
        "papers": tc["paper"],
        "monographs": tc["monograph"],
        "lean_files": tc["lean"],
        "verifiers": tc["verifier"],
        "certificates": tc["certificate"],
        "datasets": tc["dataset"],
        "zenodo": tc["zenodo"],
        "claim_ids": claims_by_repo.get(name, 0),
        "results_indexed": results_by_repo.get(name, 0),
    })
with open(os.path.join(OUT, "coverage.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print("repos", len(rows))
print("rows without any claim id:", [r["repository"] for r in rows if not r["claim_ids"]])
print("total claim ids:", sum(r["claim_ids"] for r in rows))
