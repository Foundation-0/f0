"""Compile push statistics from out/*.json (numerical)."""
import json, collections, glob


def best(r):
    return max(r.get('best_phys', 0), r.get('final_phys', 0) or 0)


for n in (3, 4):
    print(f"==== n = {n}")
    tot_starts = tot_iters = 0
    allbest = collections.Counter()
    for f in sorted(glob.glob(f'out/push_n{n}_*.json')) + sorted(glob.glob(f'out/push2_n{n}_*.json')):
        R = [r for r in json.load(open(f)) if 'best_phys' in r]
        c = collections.Counter(best(r) for r in R)
        it = sum(r['iters'] for r in R)
        tot_starts += len(R); tot_iters += it; allbest += c
        extra = ''
        if 'push2' in f:
            Ts = [r['nearest_T_min_at_best_count'] for r in R if r['best_phys'] == max(c)]
            extra = f", kicks {sum(r['kicks'] for r in R)}, min nearest-pair T at the top count {min(Ts):.2e}"
        print(f"{f}: starts {len(R)}, LP iterations {it}, best counts {dict(sorted(c.items()))}{extra}")
    print(f"TOTAL n={n}: pushes {tot_starts}, LP iterations {tot_iters}, best-count distribution {dict(sorted(allbest.items()))}")
