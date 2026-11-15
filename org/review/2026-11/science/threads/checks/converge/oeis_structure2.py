"""Q2 and Q3 for the recurrence structure.
Q2. 'exact' and 'atmost' entries of the same family: same polynomial?
Q3. Is the square root of the characteristic polynomial the minimal recurrence polynomial of the DEFECT-FREE count
    z(n) (arrays with no qualifying pair at all)? Checked with a separately written row machine for every entry
    with at most 260 row states: g = sqrt(P) must annihilate z for D consecutive n (D = number of rows, enough by
    Cayley-Hamilton), and no polynomial g / (one irreducible factor) may do so."""
import json, glob, sys, os, re, itertools, collections
from flint import fmpz_poly
sys.path.insert(0, sys.argv[2])
import spot_proof_lib as sp
certs = [json.load(open(p)) for p in sorted(glob.glob(os.path.join(sys.argv[1], "A*.json")))]
def charpoly(coef):
    d = len(coef); return fmpz_poly([-coef[d - 1 - i] for i in range(d)] + [1])
def split(P):
    _, fac = P.factor(); g = fmpz_poly([1]); extra = fmpz_poly([1])
    for f, m in fac:
        for _ in range(m // 2): g = g * f
        if m % 2: extra = extra * f
    return g, extra, fac
fam = collections.defaultdict(dict)
for c in certs:
    s = c["spec"]; fam[(s["orient"], s["k"], s["q"], s["nbrs"], s["total"])][s["mode"]] = c
both = [v for v in fam.values() if len(v) == 2]
same = sum(1 for v in both if charpoly(v["exact"]["recurrence"]["coefficients"]) == charpoly(v["atmost"]["recurrence"]["coefficients"]))
sameroot = sum(1 for v in both if split(charpoly(v["exact"]["recurrence"]["coefficients"]))[0] == split(charpoly(v["atmost"]["recurrence"]["coefficients"]))[0])
print(f"Q2. families with both modes proved: {len(both)} (of {len(fam)} families); identical polynomial: {same}; identical square-root part: {sameroot}")

def zero_defect_terms(spec, nterms):
    k, q, kinds, t = spec["k"], spec["q"], spec["kinds"], spec["total"]
    rows = [r for r in itertools.product(range(q), repeat=k) if not ("H" in kinds and any(r[c] + r[c + 1] == t for c in range(k - 1)))]
    def ok(a, b):
        for c in range(k):
            if "V" in kinds and a[c] + b[c] == t: return False
            if "D" in kinds and c + 1 < k and a[c] + b[c + 1] == t: return False
            if "A" in kinds and c - 1 >= 0 and a[c] + b[c - 1] == t: return False
        return True
    pre = [[ai for ai, a in enumerate(rows) if ok(a, b)] for b in rows]
    v = [1] * len(rows); out = []
    for _ in range(nterms):
        out.append(sum(v)); v = [sum(v[a] for a in pre[b]) for b in range(len(rows))]
    return out, len(rows)
def annihilates(g, z, need):
    co = [int(g[i]) for i in range(g.degree() + 1)]; d = g.degree()
    res = [sum(co[i] * z[n + i] for i in range(d + 1)) for n in range(len(z) - d)]
    lastbad = max((i for i, r in enumerate(res) if r != 0), default=-1)
    return len(res) - (lastbad + 1) >= need, lastbad + 1
tested = 0; ok_all = 0; minimal = 0; notes = []
for c in certs:
    spec = sp.parse(c["name"])
    if spec is None or spec["q"] ** spec["k"] > 260: continue
    P = charpoly(c["recurrence"]["coefficients"]); g, extra, fac = split(P)
    cands = {"g": g}
    if extra.degree() > 0: cands["g*extra"] = g * extra
    z, R0 = zero_defect_terms(spec, 2 * 260 + P.degree() + 20)
    tested += 1
    good = {name: annihilates(G, z, R0)[0] for name, G in cands.items()}
    if good.get("g"):
        ok_all += 1
        # minimality: remove one irreducible factor at a time
        smaller = False
        for f, m in fac:
            if m // 2 >= 1:
                q_, r_ = divmod(g, f)
                if annihilates(q_, z, R0)[0]: smaller = True
        if not smaller: minimal += 1
        else: notes.append((c["oeis_id"], "a proper divisor of sqrt(P) already annihilates the defect-free count"))
    else:
        notes.append((c["oeis_id"], f"sqrt(P) does not annihilate the defect-free count; with the extra factor: {good.get('g*extra')}; extra = {extra}"))
print(f"Q3. entries tested with a separate machine (row states <= 260): {tested}")
print(f"    sqrt(P) annihilates the defect-free count: {ok_all}; and is minimal for it: {minimal}")
for n in notes[:12]: print("    note:", n)
