import json, numpy as np
from collections import Counter
R = json.load(open('out/scan_shapes_0.json')) + json.load(open('out/scan_shapes_1.json'))
ok = [r for r in R if 'error' not in r and not r['empty']]
lines = []
lines.append('shapes scanned: %d (errors %d, empty R_min %d)' % (len(R), sum('error' in r for r in R), sum(r.get('empty', False) for r in R)))
lines.append('(cusps, self-intersections of fold image) counts: %s' % sorted(Counter((r['ncusp'], r['selfint']) for r in ok).items()))
lines.append('star-shaped flag false (ray sampling artefact on thin shapes): %d' % sum(not r['star'] for r in ok))
kn = np.array([max(r['kapn']) for r in ok])
lines.append('max normalised cusp coefficient over all shapes: %.6f (all cusps of the minus type iff < 0)' % kn.max())
lines.append('min over shapes of max |m| margin: mumax min %.6f' % min(r['mumax'] for r in ok))
b = np.array([r['b'] for r in ok]); a = np.array([r['a'] for r in ok])
lines.append('a range [%.4g, %.4g], b range [%.3g, %.3g]' % (a.min(), a.max(), b.min(), b.max()))
open('out/scan_shapes_summary.txt', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
