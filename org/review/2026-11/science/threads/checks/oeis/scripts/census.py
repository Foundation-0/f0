import sys, json, time; sys.path.insert(0,'.')
import fsm, spec
c = spec.load_cache()
pool = []
for a, e in sorted(c.items()):
    s = spec.parse_name(e['name'])
    if not s: continue
    r = spec.parse_recurrence(e.get('formula', []))
    pool.append((a, s, r, e))
print(len(pool), 'parsed entries;', sum(1 for p in pool if p[2]), 'with a parsed Empirical recurrence')
res = []
for a, s, r, e in pool:
    if not r: continue
    if s['q'] ** s['k'] > 4500: res.append((a, 'SKIP size')); print(a, 'skip q^k', s['q'] ** s['k']); continue
    t = time.time()
    m = fsm.build(s)
    D = len(m['states']); nnz = sum(map(len, m['edges']))
    data = [int(x) for x in e['data'].split(',')]
    off = int(e['offset'].split(',')[0])
    T = fsm.terms(m, len(data)) if nnz * len(data) < 3e7 else None
    ok = None if T is None else (T == data)
    coef = r[0]; d = len(coef)
    # chain
    if nnz * (d + 40) > 6e7:
        print(a, s['q'], s['k'], s['nbrs'], s['orient'], 'D', D, 'nnz', nnz, 'order', d, 'TOO BIG'); continue
    v = m['init']; pw = [v]
    for _ in range(d): pw.append(fsm.advance(pw[-1], m['edges']))
    z = [pw[d][i] - sum(coef[l - 1] * pw[d - l][i] for l in range(1, d + 1)) for i in range(D)]
    chain = 0; scal = []
    while any(z) and chain < 80:
        scal.append(sum(x for x, ac in zip(z, m['accept']) if ac))
        z = fsm.advance(z, m['edges']); chain += 1
    zero = not any(z)
    last_nz = max([j for j, x in enumerate(scal) if x], default=-1)
    print(a, 'q%d k%d %s %s %s' % (s['q'], s['k'], s['nbrs'], s['orient'], s['mode']), 'D', D, 'nnz', nnz, 'ord', d, 'terms', len(data), 'match', ok,
          'chain->0', zero, 'm', chain, 'start', off + d + last_nz + 1, 'natural', off + d, round(time.time() - t, 1), flush=True)
