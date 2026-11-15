"""Union of the classes found by several census runs for the same n.  Each representative is first polished by
Newton's method on the reduced system (float), then classes are merged only when I agrees to 1e-10 and every
sorted mutual distance to 1e-8.  Floating point only: the certificate decides distinctness.
Usage: python merge_census.py out.json run1.json run2.json ..."""
import sys, json
import numpy as np
from cert_arb import polish

out = sys.argv[1]; runs = [json.load(open(f)) for f in sys.argv[2:]]
n = runs[0]['n']
iu = np.triu_indices(n, 1)
classes = []
for f, d in zip(sys.argv[2:], runs):
    if d['n'] != n:
        raise SystemExit("different n")
    for c in d['classes']:
        q, k = polish(c['x'], n)
        I = float((q ** 2).sum()); dist = np.sort(np.sqrt(((q[:, None] - q[None]) ** 2).sum(-1))[iu])
        hit = next((e for e in classes if abs(e['I'] - I) < 1e-10 and np.max(np.abs(e['d'] - dist)) < 1e-8), None)
        if hit is None:
            classes.append({'I': I, 'd': dist, 'x': q.reshape(-1).tolist(), 'found_in': [f]})
        elif f not in hit['found_in']:
            hit['found_in'].append(f)
classes.sort(key=lambda e: e['I'])
for e in classes:
    print(f"P = {e['I'] ** 1.5:.10f}  found in {len(e['found_in'])} run(s): {', '.join(x.split('/')[-1] for x in e['found_in'])}")
print(f"n = {n}: {len(classes)} classes in the union of {len(runs)} runs")
json.dump({'n': n, 'merged_from': sys.argv[2:],
           'classes': [{'I': e['I'], 'P': e['I'] ** 1.5, 'x': e['x'], 'found_in': e['found_in']} for e in classes]},
          open(out, 'w'), indent=1)
