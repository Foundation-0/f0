"""Builder: row-by-row transfer machine for 'count arrays with exactly/at most one adjacent pair
summing to t' on a strip of fixed width. Uses numpy digit arrays (the certificate verifier uses a
different, bitmask-based construction; brute.py shares no code with either)."""
import itertools
import numpy as np

TRANSPOSE = {'H': 'V', 'V': 'H', 'D': 'D', 'A': 'A'}

def machine_nbrs(spec):
    """Neighbour set in the growth direction. For 'k X n' (k rows fixed, columns grow) we transpose."""
    if spec['orient'] == 'nxk':
        return set(spec['nbrs'])
    return {TRANSPOSE[d] for d in spec['nbrs']}

def build(spec, cap=1):
    """Return dict(states=[(used,row_tuple)], edges=[[dest,...]] (with multiplicity), init=[int], accept=[0/1]).
    States are reachable from some first row and can reach an accepting state; sorted by (used,row)."""
    q, w, t = spec['q'], spec['k'], spec['total']
    nb = machine_nbrs(spec)
    rows = np.array(list(itertools.product(range(q), repeat=w)), dtype=np.int16).reshape(-1, w)
    if 'H' in nb and w > 1:
        hin = ((rows[:, :-1] + rows[:, 1:]) == t).sum(axis=1)
    else:
        hin = np.zeros(len(rows), dtype=np.int64)
    ok = np.nonzero(hin <= cap)[0]            # rows that can occur at all
    R = rows[ok]; hin = hin[ok]; n = len(R)
    cross = np.zeros((n, n), dtype=np.int16)  # cross[r,s] = new pairs when s is placed under r
    if 'V' in nb:
        cross += ((R[:, None, :] + R[None, :, :]) == t).sum(axis=2).astype(np.int16)
    if 'D' in nb and w > 1:
        cross += ((R[:, None, :-1] + R[None, :, 1:]) == t).sum(axis=2).astype(np.int16)
    if 'A' in nb and w > 1:
        cross += ((R[:, None, 1:] + R[None, :, :-1]) == t).sum(axis=2).astype(np.int16)
    # state (used,row index); full graph first
    S = [(u, i) for u in range(cap + 1) for i in range(n) if hin[i] <= u]
    idx = {s: j for j, s in enumerate(S)}
    out = []
    for (u, i) in S:
        dests = []
        add = cross[i] + hin                   # pairs added by each next row
        for s in np.nonzero(u + add <= cap)[0]:
            dests.append(idx[(u + int(add[s]), int(s))])
        out.append(dests)
    init = [1 if u == hin[i] else 0 for (u, i) in S]
    accept = [1 if (spec['mode'] == 'atmost' or u == cap) else 0 for (u, i) in S]
    # reachable from initial
    seen = {j for j, x in enumerate(init) if x}; stack = list(seen)
    while stack:
        j = stack.pop()
        for d in out[j]:
            if d not in seen: seen.add(d); stack.append(d)
    # co-reachable to accepting
    rev = [[] for _ in S]
    for j, ds in enumerate(out):
        for d in set(ds): rev[d].append(j)
    co = {j for j, a in enumerate(accept) if a}; stack = list(co)
    while stack:
        j = stack.pop()
        for p in rev[j]:
            if p not in co: co.add(p); stack.append(p)
    keep = sorted(seen & co, key=lambda j: (S[j][0], tuple(R[S[j][1]])))
    new = {j: k for k, j in enumerate(keep)}
    states = [(S[j][0], tuple(int(x) for x in R[S[j][1]])) for j in keep]
    edges = [[new[d] for d in out[j] if d in new] for j in keep]
    return dict(states=states, edges=edges, init=[init[j] for j in keep], accept=[accept[j] for j in keep])

def advance(vec, edges):
    res = [0] * len(vec)
    for i, x in enumerate(vec):
        if x:
            for d in edges[i]: res[d] += x
    return res

def terms(m, count):
    v = m['init']; out = []
    for _ in range(count):
        out.append(sum(x for x, a in zip(v, m['accept']) if a))
        v = advance(v, m['edges'])
    return out
