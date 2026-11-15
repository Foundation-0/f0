"""Statistics of the code-table improvements: which entries are now settled exactly, how the gap shrinks,
and where in the (rate, relative distance) plane the improvements sit."""
import csv, sys, collections, math
rows = list(csv.DictReader(open(sys.argv[1])))
for r in rows:
    for k in ("q", "n", "k", "lower", "table_upper", "new_upper", "table_self_closure_upper"): r[k] = int(r[k])
out = []
for q in (7, 8, 9):
    R = [r for r in rows if r["q"] == q]
    real = [r for r in R if r["new_upper"] < r["table_self_closure_upper"]]      # beyond the table's own consistency
    settled = [r for r in real if r["new_upper"] == r["lower"]]
    gap_before = collections.Counter(r["table_self_closure_upper"] - r["lower"] for r in real)
    gap_after = collections.Counter(r["new_upper"] - r["lower"] for r in real)
    drop = collections.Counter(r["table_self_closure_upper"] - r["new_upper"] for r in real)
    print(f"\nGF({q}): improved beyond the table's own consistency: {len(real)}; now settled exactly (upper = lower): {len(settled)}")
    print("  gap before:", dict(sorted(gap_before.items())))
    print("  gap after :", dict(sorted(gap_after.items())))
    print("  size of the drop in the upper bound:", dict(sorted(drop.items())))
    for r in settled: out.append(r)
    # where: rate k/n and relative distance d/n
    rates = sorted(r["k"] / r["n"] for r in real); n_ = sorted(r["n"] for r in real)
    qt = lambda a, p: a[int(p * (len(a) - 1))]
    print(f"  rate k/n: min {rates[0]:.3f}, quartiles {qt(rates,.25):.3f} {qt(rates,.5):.3f} {qt(rates,.75):.3f}, max {rates[-1]:.3f};  length n: min {n_[0]}, median {qt(n_,.5)}, max {n_[-1]}")
    base = [r for r in R if r["kind"] == "base"]
    print("  base entries by dimension k:", dict(sorted(collections.Counter(r["k"] for r in base).items())))
    # relative gap closure
    tot_before = sum(r["table_self_closure_upper"] - r["lower"] for r in real); tot_after = sum(r["new_upper"] - r["lower"] for r in real)
    print(f"  total gap over improved entries: {tot_before} -> {tot_after} ({100*(tot_before-tot_after)/tot_before:.1f}% closed)")
w = csv.writer(open("settled_cells.csv", "w", newline=""))
w.writerow(["q", "n", "k", "optimal_distance", "table_upper_before", "kind"])
for r in sorted(out, key=lambda r: (r["q"], r["n"], r["k"])): w.writerow([r["q"], r["n"], r["k"], r["lower"], r["table_upper"], r["kind"]])
print(f"\nsettled entries written: {len(out)}")
for r in sorted(out, key=lambda r: (r["q"], r["n"], r["k"]))[:40]: print(f"  GF({r['q']}) [{r['n']},{r['k']}]: d = {r['lower']} (table said {r['lower']}-{r['table_upper']})")
