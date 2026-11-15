"""Structure of the 211 proved recurrences. For each, factor the characteristic polynomial over the integers.
Questions asked before looking:
  Q1. Is every characteristic polynomial a perfect square, or a square times a small extra factor?
  Q2. Do the 'exactly once' and 'at most once' entries of the same family share the same polynomial?
  Q3. Is the square root the characteristic polynomial of the count with NO such pair (the defect-free strip)?
"""
import json, glob, sys, collections, os
from flint import fmpz_poly
certs = {}
for p in sorted(glob.glob(os.path.join(sys.argv[1], "A*.json"))):
    c = json.load(open(p)); certs[c["oeis_id"]] = c
def charpoly(coef):
    d = len(coef)
    # x^d - c1 x^(d-1) - ... - cd ; fmpz_poly takes coefficients from the constant term up
    return fmpz_poly([-coef[d - 1 - i] for i in range(d)] + [1])
stats = collections.Counter(); fam = collections.defaultdict(dict); rows = []
for a, c in certs.items():
    P = charpoly(c["recurrence"]["coefficients"])
    cst, fac = P.factor()
    mults = sorted(m for _, m in fac)
    even = all(m % 2 == 0 for m in mults)
    sqdeg = sum(f.degree() * (m // 2) for f, m in fac)             # degree of the largest square-root part
    rest = sum(f.degree() * (m % 2) for f, m in fac)                # degree left outside the square
    odd = [(f, m) for f, m in fac if m % 2]
    sp = c["spec"]; key = (sp["orient"], sp["k"], sp["q"], sp["nbrs"], sp["total"])
    fam[key][sp["mode"]] = (a, P, fac)
    stats["perfect square" if even else ("square times extra" if sqdeg > 0 else "no square part")] += 1
    rows.append((a, sp["mode"], P.degree(), sqdeg, rest, max(mults), [(f.degree(), m) for f, m in fac]))
print("Q1. characteristic polynomials:", dict(stats), "of", len(certs))
print("    degree outside the square part:", dict(sorted(collections.Counter(r[4] for r in rows).items())))
print("    largest multiplicity of any factor:", dict(sorted(collections.Counter(r[5] for r in rows).items())))
by_mode = collections.defaultdict(collections.Counter)
for r in rows: by_mode[r[1]]["perfect square" if r[4] == 0 else f"extra degree {r[4]}"] += 1
for m, cnt in by_mode.items(): print(f"    mode {m}: {dict(cnt)}")
print("    examples of the extra factor (first 8 with one):")
k = 0
for a, c in certs.items():
    P = charpoly(c["recurrence"]["coefficients"]); _, fac = P.factor()
    odd = [f for f, m in fac if m % 2]
    if odd and k < 8:
        k += 1; print("     ", a, c["spec"]["mode"], "extra factor(s):", [str(f) for f in odd][:3])
both = [(k_, v) for k_, v in fam.items() if "exactly" in v and "atmost" in v]
same = sum(1 for _, v in both if v["exactly"][1] == v["atmost"][1])
print(f"\nQ2. families with both modes proved: {len(both)}; identical polynomial in both modes: {same}")
diff = [(k_, v) for k_, v in both if v["exactly"][1] != v["atmost"][1]]
def sqroot(fac):
    R = fmpz_poly([1])
    for f, m in fac:
        for _ in range(m // 2): R = R * f
    return R
same_root = sum(1 for _, v in diff if sqroot(v["exactly"][2]) == sqroot(v["atmost"][2]))
print(f"    of the {len(diff)} that differ, same square-root part: {same_root}")
for k_, v in diff[:6]:
    e, a_ = v["exactly"], v["atmost"]
    print("     ", k_, "| exactly", e[0], "deg", e[1].degree(), "| atmost", a_[0], "deg", a_[1].degree(), "| atmost/exactly-root extra:", [str(f) for f, m in a_[2] if m % 2][:2])
json.dump({a: {"mode": m, "degree": d, "square_root_degree": s, "outside_square": r_, "factors": f} for a, m, d, s, r_, _, f in rows}, open("oeis_structure.json", "w"), indent=0)
