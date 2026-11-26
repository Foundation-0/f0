"""Recompute the code-table counts quoted in the exploration note of pull request 60 from this folder's files.
Usage (from the threads folder): python3 checks/review-meta/pr60-rerun/code_counts.py"""
import csv, collections, json
rows = list(csv.DictReader(open("checks/codes/improved_cells.csv")))
c = collections.Counter(int(r["table_upper"]) - int(r["new_upper"]) for r in rows)
print("improved cells:", len(rows), " by size of the improvement:", dict(sorted(c.items())))
J = json.load(open("checks/codes/summary.json"))
print("table cells that the table's own closure rules already improve:", {q: J[q]["table_cells_stale_vs_own_closure"] for q in ("7", "8", "9")})
