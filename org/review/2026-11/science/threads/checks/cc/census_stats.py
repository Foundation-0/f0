"""Summarise census runs: starts, converged runs, classes, hit counts, and what the run can and cannot rule out.
Usage: python census_stats.py run1.json [run2.json ...]   (runs for the same n are compared by P = I^1.5)"""
import sys, json, math

for f in sys.argv[1:]:
    d = json.load(open(f))
    hits = sorted(c['hits'] for c in d['classes'])
    N = d['starts']; conv = d['converged']
    last = max(c['first_found_at_start'] for c in d['classes'])
    single = sum(1 for h in hits if h == 1)
    # a class whose basin catches a fraction p of starts is missed by all N starts with probability (1-p)^N;
    # p95: the share for which that probability is 5 %
    p95 = -math.log(0.05) / N
    print(f"{f}: n={d['n']} mode={d.get('mode','lm')} starts={d.get('start_distribution','mix')} N={N} converged={conv} "
          f"({conv/N:.1%}) classes={len(hits)} last new class at start {last} ({last/N:.2%} of the run); "
          f"smallest hit share {hits[0]/conv:.2e}; classes seen once {single}; "
          f"a class with basin share > {p95:.1e} would have been missed with probability < 5%")
if len(sys.argv) > 2:
    sets = []
    for f in sys.argv[1:]:
        d = json.load(open(f))
        sets.append(sorted(round(c['P'], 6) for c in d['classes']))
    allP = sorted(set(sum(sets, [])))
    print("union of classes over runs:", len(allP), "; identical lists:", all(s == sets[0] for s in sets))
