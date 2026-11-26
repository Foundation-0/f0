"""Scan triangle shapes in the fundamental domain 0<a<=1/2, 0<b<=sqrt(2a-a^2) (A1A2 longest side,
|A1A3|<=|A2A3|). For each shape: fold curve, cusps, cusp type, self-intersections of the fold image
in log-charge coordinates. Usage: scan_shapes.py part nparts out.json"""
import sys, json, time
import numpy as np
from fold import analyse, seg_intersections
part, nparts, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
S = np.r_[np.linspace(0.02, 1.0, 50), [0.005, 0.01]]
T = np.r_[10 ** np.linspace(-3, -1, 12), np.linspace(0.12, 1.0, 30)]
jobs = [(s, t) for s in S for t in T]
res = []
t0 = time.time()
for k, (s, t) in enumerate(jobs):
    if k % nparts != part:
        continue
    a = 0.5 * s
    b = np.sqrt(2 * a - a * a) * t
    try:
        R = analyse(a, b, nth=540)
        if R['empty']:
            res.append(dict(a=a, b=b, empty=True, mumax=float(R['mumax'])))
        else:
            Y = np.log(R['Q'][:, 1:] / R['Q'][:, :1])
            ni, _ = seg_intersections(Y)
            res.append(dict(a=a, b=b, empty=False, mumax=float(R['mumax']), star=bool(R['star']),
                            ncusp=len(R['cusps']), kapn=[float(c['kapn']) for c in R['cusps']],
                            selfint=ni, flip=bool(R['flip_loop'])))
    except Exception as e:
        res.append(dict(a=a, b=b, error=repr(e)))
    if len(res) % 20 == 0:
        print(len(res), time.time() - t0, flush=True)
        json.dump(res, open(out, 'w'))
json.dump(res, open(out, 'w'))
print('done', len(res), time.time() - t0)
