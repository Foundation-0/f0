"""Lead's own check of the code-bounds scan: (1) every certificate through the checker written for the
science pass (three-term recurrence, exact Fractions); (2) each improved cell's bookkeeping; (3) live table values
for a sample of base cells."""
import json, sys, csv, random, re, time, urllib.request
from fractions import Fraction
CHECKER, CODES = sys.argv[1], sys.argv[2]   # path to checks/delsarte_independent.py (draft PR 51), and this folder
src = open(CHECKER).read().split("\nrows = []")[0]
ns = {}; exec(src, ns)
check = ns["check"]
tot = 0; excl = {}
for q in (7, 8, 9):
    certs = json.load(open(f"{CODES}/certs/gf{q}_certs.json"))["certificates"]
    for c in certs:
        if c["q"] != q: raise SystemExit("q mismatch")
        r = check(c)   # raises SystemExit on any failure
        excl[(q, c["n"], c["k"])] = min(excl.get((q, c["n"], c["k"]), 10**9), c["excluded_distance"])
        tot += 1
    print(f"q={q}: {len(certs)} certificates pass my checker")
print("total", tot)
# bookkeeping: for base cells, the direct certificate must exclude d = new_upper + 1 (or lower)
rows = list(csv.DictReader(open(f"{CODES}/improved_cells.csv")))
bad = 0; base = [r for r in rows if r["kind"] == "base"]
for r in base:
    key = (int(r["q"]), int(r["n"]), int(r["k"]))
    if key not in excl or excl[key] > int(r["new_upper"]) + 1: bad += 1
    if int(r["new_upper"]) >= int(r["table_upper"]) or int(r["new_upper"]) < int(r["lower"]): bad += 1
print(f"base cells: {len(base)}; bookkeeping failures: {bad}")
print("improved cells by q:", {q: sum(1 for r in rows if r['q'] == str(q)) for q in (7, 8, 9)})
print("new_upper below table lower anywhere:", sum(1 for r in rows if int(r['new_upper']) < int(r['lower'])))
# live spot check
random.seed(20261115)
sample = random.sample(base, 9)
for r in sample:
    url = f"http://www.codetables.de/BKLC/BKLC.php?q={r['q']}&n={r['n']}&k={r['k']}"
    html = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-script"}), timeout=40).read().decode("latin-1")
    txt = re.sub(r"<[^>]+>", " ", html); txt = re.sub(r"\s+", " ", txt)
    m = re.search(r"lower bound:\s*(\d+)\s*upper bound:\s*(\d+)", txt)
    print(f"q={r['q']} n={r['n']} k={r['k']}: csv lower/upper {r['lower']}/{r['table_upper']} -> new {r['new_upper']} | live:", m.groups() if m else txt[:160])
    time.sleep(1.2)
