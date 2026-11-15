"""Lead's own proof of a sample of the recurrences, sharing no code with the thread's builder or verifier.
For each chosen entry: read the OEIS name and the claimed coefficients from the certificate, build a row-by-row
machine straight from the name (state = last row and the number of qualifying pairs so far, capped), compute a(n)
with exact integers, compare with the OEIS data terms, then check the recurrence residual is zero for D consecutive
n, where D is the dimension of this machine. By Cayley-Hamilton that proves it for every later n."""
import json, re, sys, itertools, glob, os
CERTS = sys.argv[1]
WORDS = {"zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10,"eleven":11,"twelve":12}
def parse(name):
    m = re.match(r"Number of\s+(n|\d+)\s*X\s*(n|\d+)\s+(binary|0\.\.(\d+)) arrays with some element plus some (.+?) adjacent neighbor totalling (\w+) (no more than once|not more than once|exactly once)\.?$", name)
    if not m: return None
    a, b, alpha, top, nb, tot, mode = m.groups()
    q = 2 if alpha == "binary" else int(top) + 1
    kinds = set()
    for w in re.split(r"[ ,]+", nb.replace(" or ", " ")):
        w = w.strip()
        if w == "horizontally": kinds.add("H")
        elif w == "vertically": kinds.add("V")
        elif w == "diagonally": kinds.add("D")
        elif w == "antidiagonally": kinds.add("A")
        elif w: return None
    if a == "n": k = int(b)                       # n rows, k columns
    else:                                         # k rows, n columns: transpose, which swaps H and V
        k = int(a); kinds = {{"H":"V","V":"H"}.get(x, x) for x in kinds}
    return dict(k=k, q=q, kinds=kinds, total=WORDS[tot], exact=(mode == "exactly once"))
def prove(cert):
    sp = parse(cert["name"])
    if sp is None: return "name not parsed"
    k, q, kinds, t, exact = sp["k"], sp["q"], sp["kinds"], sp["total"], sp["exact"]
    rows = list(itertools.product(range(q), repeat=k)); R = len(rows)
    h = [sum(1 for c in range(k-1) if "H" in kinds and r[c]+r[c+1] == t) for r in rows]
    def cross(a, b):
        s = 0
        for c in range(k):
            if "V" in kinds and a[c]+b[c] == t: s += 1
            if "D" in kinds and c+1 < k and a[c]+b[c+1] == t: s += 1
            if "A" in kinds and c-1 >= 0 and a[c]+b[c-1] == t: s += 1
        return s
    pre0 = [[] for _ in rows]; pre1 = [[] for _ in rows]
    for bi, b in enumerate(rows):
        if h[bi] > 1: continue
        for ai, a in enumerate(rows):
            x = h[bi] + cross(a, b)
            if x == 0: pre0[bi].append(ai)
            elif x == 1: pre1[bi].append(ai)
    c0 = [1 if h[i] == 0 else 0 for i in range(R)]; c1 = [1 if h[i] == 1 else 0 for i in range(R)]
    D = 2 * R
    coef = cert["recurrence"]["coefficients"]; d = len(coef)
    off = int(cert["offset"]); data = cert["data_terms"]
    need = d + D + 40
    seq = []
    for n in range(need):
        seq.append(sum(c1) if exact else sum(c0) + sum(c1))
        n0 = [sum(c0[a] for a in pre0[b]) for b in range(R)]
        n1 = [sum(c1[a] for a in pre0[b]) + sum(c0[a] for a in pre1[b]) for b in range(R)]
        c0, c1 = n0, n1
    if seq[:len(data)] != data: return f"DATA MISMATCH first terms {seq[:4]} vs {data[:4]}"
    res = [seq[i] - sum(coef[j] * seq[i-1-j] for j in range(d)) for i in range(d, len(seq))]
    # first index from which the residual stays zero through the end of what was computed
    last_bad = max((i for i, r in enumerate(res) if r != 0), default=-1)
    zeros = len(res) - (last_bad + 1)
    start_n = (last_bad + 1) + d + off
    if zeros < D: return f"NOT PROVED: only {zeros} consecutive zero residuals, need {D}"
    claimed = cert.get("proof", {}).get("start_n", cert.get("start_n"))
    return f"PROVED for all n >= {start_n} (machine dimension {D}, {zeros} consecutive zero residuals, {len(data)} OEIS terms matched, order {d})"
picked = {}
for p in sorted(glob.glob(os.path.join(CERTS, "A*.json"))):
    c = json.load(open(p)); sp = parse(c["name"])
    if sp is None: print("unparsed name:", c["oeis_id"], c["name"]); continue
    if sp["q"] ** sp["k"] > 260: continue
    key = (frozenset(sp["kinds"]), sp["q"], sp["exact"], c["name"].split()[2][0] == "n" or c["name"].split()[2] == "n")
    picked.setdefault(key, c)
print(f"{len(picked)} entries chosen, one per (neighbour set, alphabet, mode) among those with at most 260 row states")
bad = 0
for key, c in sorted(picked.items(), key=lambda kv: kv[1]["oeis_id"]):
    r = prove(c); print(c["oeis_id"], "|", c["name"][10:95], "|", r)
    if not r.startswith("PROVED"): bad += 1
print("failures:", bad)
sys.exit(1 if bad else 0)
