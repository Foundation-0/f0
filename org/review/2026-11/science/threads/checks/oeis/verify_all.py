#!/usr/bin/env python3
"""Verify every certificate in certs/ with exact integer arithmetic (standard library only).

For each certificate this script
  1. rebuilds the transfer machine from the stored counting definition using bitmask row encodings
     (it does not read any graph from the certificate and shares no code with scripts/fsm.py),
  2. checks the graph digest, the state count and the first data terms stored from the OEIS entry,
  3. recomputes the residual vector chain z_0 = p(M) v, z_{j+1} = M z_j (or, when that chain does not
     reach the zero vector, the scalar residuals r_j = L(z_j)) and compares with the stored values,
  4. concludes that  a(n) = c_1 a(n-1) + ... + c_d a(n-d)  for all n >= start, and that it fails at start-1
     (unless start is the first index where the recurrence can be written down),
  5. cross-checks small cases against a direct enumeration of all arrays (pure Python, cell by cell).
All failures raise CertError (no bare assert), so the checks are the same under python -O.
Usage: verify_all.py [certs_dir]    exit status 0 only if every certificate passes.
"""
import hashlib, itertools, json, os, sys, time

class CertError(Exception):
    pass

def need(cond, msg):
    if not cond:
        raise CertError(msg)

TRANSPOSE = {'H': 'V', 'V': 'H', 'D': 'D', 'A': 'A'}
OFFS = {'H': (0, 1), 'V': (1, 0), 'D': (1, 1), 'A': (1, -1)}

def growth_nbrs(spec):
    nb = set(spec['nbrs'])
    return nb if spec['orient'] == 'nxk' else {TRANSPOSE[x] for x in nb}

def build(spec):
    """Machine for arrays that grow row by row. Pure-Python, bitmask based."""
    q, w, t, mode = spec['q'], spec['k'], spec['total'], spec['mode']
    nb = growth_nbrs(spec)
    need(mode in ('exact', 'atmost') and spec['orient'] in ('nxk', 'kxn'), 'bad spec')
    pairs = [(a, t - a) for a in range(q) if 0 <= t - a < q]
    rows = []
    for row in itertools.product(range(q), repeat=w):
        m = [0] * q
        for c, x in enumerate(row):
            m[x] |= 1 << c
        h = sum((m[a] & (m[b] >> 1)).bit_count() for a, b in pairs) if 'H' in nb else 0
        if h <= 1:
            rows.append((row, tuple(m), h))
    n = len(rows)
    states = [(u, i) for u in (0, 1) for i in range(n) if rows[i][2] <= u]
    index = {s: j for j, s in enumerate(states)}
    # cross[i][j] = new pairs when row j is placed below row i
    ms = [r[1] for r in rows]
    hs = [r[2] for r in rows]
    cross = []
    for i in range(n):
        up = ms[i]
        line = []
        for j in range(n):
            dn = ms[j]
            x = 0
            for a, b in pairs:
                if 'V' in nb: x += (up[a] & dn[b]).bit_count()
                if 'D' in nb: x += (up[a] & (dn[b] >> 1)).bit_count()
                if 'A' in nb: x += ((up[a] >> 1) & dn[b]).bit_count()
            line.append(x)
        cross.append(line)
    out = []
    for (u, i) in states:
        d = []
        for j in range(n):
            tot = u + hs[j] + cross[i][j]
            if tot <= 1:
                d.append(index[(tot, j)])
        out.append(d)
    init = [1 if u == hs[i] else 0 for (u, i) in states]
    accept = [1 if (mode == 'atmost' or u == 1) else 0 for (u, i) in states]
    seen = {j for j, x in enumerate(init) if x}
    stack = list(seen)
    while stack:
        j = stack.pop()
        for d in out[j]:
            if d not in seen:
                seen.add(d); stack.append(d)
    rev = [[] for _ in states]
    for j, ds in enumerate(out):
        for d in set(ds):
            rev[d].append(j)
    co = {j for j, a in enumerate(accept) if a}
    stack = list(co)
    while stack:
        j = stack.pop()
        for p in rev[j]:
            if p not in co:
                co.add(p); stack.append(p)
    keep = sorted(seen & co, key=lambda j: (states[j][0], rows[states[j][1]][0]))
    new = {j: k for k, j in enumerate(keep)}
    labels = [(states[j][0], rows[states[j][1]][0]) for j in keep]
    edges = [sorted(new[d] for d in out[j] if d in new) for j in keep]
    return labels, edges, [init[j] for j in keep], [accept[j] for j in keep]

def digest(labels, edges):
    h = hashlib.sha256()
    for (u, row), e in zip(labels, edges):
        h.update(('%d:%s>%s\n' % (u, ''.join(map(str, row)), ','.join(map(str, e)))).encode())
    return h.hexdigest()

def step(vec, edges):
    res = [0] * len(vec)
    for i, x in enumerate(vec):
        if x:
            for d in edges[i]:
                res[d] += x
    return res

def lin(vec, accept):
    return sum(x for x, a in zip(vec, accept) if a)

def brute(spec, rows, cols):
    """Direct enumeration of all q^(rows*cols) arrays of the literal shape of the definition."""
    q, t = spec['q'], spec['total']
    exact = atmost = 0
    for cells in itertools.product(range(q), repeat=rows * cols):
        c = 0
        for r in range(rows):
            for k in range(cols):
                for d in spec['nbrs']:
                    dr, dc = OFFS[d]
                    r2, k2 = r + dr, k + dc
                    if 0 <= r2 < rows and 0 <= k2 < cols and cells[r * cols + k] + cells[r2 * cols + k2] == t:
                        c += 1
        exact += (c == 1); atmost += (c <= 1)
    return exact if spec['mode'] == 'exact' else atmost

def verify_cert(cert, brute_limit=12000):
    spec, rec, proof = cert['spec'], cert['recurrence'], cert['proof']
    need(type(spec['q']) is int and type(spec['k']) is int and type(spec['total']) is int, 'spec types')
    coef = rec['coefficients']
    need(coef and all(type(c) is int for c in coef), 'coefficients must be integers')
    d = len(coef)
    o = cert['offset']
    data = cert['data_terms']
    need(data and all(type(x) is int for x in data), 'data terms')
    labels, edges, init, accept = build(spec)
    D = len(labels)
    need(D == cert['machine']['states'], 'state count differs')
    need(sum(map(len, edges)) == cert['machine']['transitions'], 'transition count differs')
    need(digest(labels, edges) == cert['machine']['graph_sha256'], 'graph digest differs')
    # terms of the sequence: a(o), a(o+1), ... = L(M^j v)
    need(len(data) >= 1, 'no data')
    vecs = [init]
    for _ in range(max(len(data), d + 1) - 1):
        vecs.append(step(vecs[-1], edges))
    terms = [lin(v, accept) for v in vecs]
    need(terms[:len(data)] == data, 'machine terms differ from stored OEIS data terms')
    # residual chain: z_0 = q(M) v with q(t)= t^d - c_1 t^(d-1) - ... - c_d  (needs v_0..v_d)
    z = [vecs[d][i] - sum(coef[l - 1] * vecs[d - l][i] for l in range(1, d + 1)) for i in range(D)]
    natural = o + d              # first index n where a(n-d)..a(n) are all defined
    kind = proof['kind']
    scal = []
    if kind == 'vector_chain':
        chain = [z]
        while any(chain[-1]):
            need(len(chain) <= D + 1, 'chain does not reach zero within D steps')
            chain.append(step(chain[-1], edges))
        need(chain == proof['chain'], 'stored residual chain differs')
        scal = [lin(v, accept) for v in chain[:-1]]
        # z_m = 0 so r_j = 0 for all j >= m; recurrence holds at n = natural + j for j >= m.
    elif kind == 'scalar_window':
        # r_j = L(M^j z_0) satisfies the order-D recurrence given by the characteristic polynomial of M
        # (Cayley-Hamilton), so D consecutive zeros force all later residuals to vanish.
        run = 0
        while run < D:
            need(len(scal) < proof['max_steps'], 'no zero window found within the stored step bound')
            r = lin(z, accept)
            scal.append(r)
            run = run + 1 if r == 0 else 0
            if run < D:
                z = step(z, edges)
        need(scal == proof['scalar_residuals'], 'stored scalar residuals differ')
    else:
        raise CertError('unknown proof kind')
    last_nz = max([j for j, r in enumerate(scal) if r != 0], default=-1)
    start = natural + last_nz + 1
    need(start == proof['min_start'], 'minimal start index differs')
    # the recurrence really holds for all n >= start and fails at start-1 when start-1 >= natural
    if start > natural:
        need(scal[last_nz] != 0, 'internal: residual at start-1 must be nonzero')
    # compare with a statement that carries an explicit range
    ss = rec.get('stated_start')
    need(rec.get('holds_as_stated') == (ss is None and start == natural or ss is not None and start <= ss),
         'holds_as_stated flag differs')
    # direct enumeration cross-check for all small sizes
    checked = []
    n = o
    while True:
        rows, cols = (n, spec['k']) if spec['orient'] == 'nxk' else (spec['k'], n)
        if spec['q'] ** (rows * cols) > brute_limit:
            break
        need(brute(spec, rows, cols) == data[n - o], 'direct enumeration differs at n=%d' % n)
        checked.append(n); n += 1
    need(proof['brute_checked_n'] == checked, 'brute-force range differs')
    return dict(states=D, order=d, start=start, natural=natural, kind=kind, brute=len(checked))

def main(argv):
    root = os.path.dirname(os.path.abspath(__file__))
    cdir = argv[1] if len(argv) > 1 else os.path.join(root, 'certs')
    files = sorted(f for f in os.listdir(cdir) if f.endswith('.json'))
    need(files, 'no certificates found')
    bad = 0
    for f in files:
        t0 = time.time()
        try:
            cert = json.load(open(os.path.join(cdir, f)))
            r = verify_cert(cert)
            print('PASS %s states=%d order=%d start=%d (natural %d) %s brute_n=%d  %.1fs' % (
                cert['oeis_id'], r['states'], r['order'], r['start'], r['natural'], r['kind'], r['brute'], time.time() - t0), flush=True)
        except (CertError, KeyError, TypeError, ValueError, IndexError) as e:
            bad += 1
            print('FAIL %s: %s' % (f, e), flush=True)
    print('%d certificates, %d failed' % (len(files), bad))
    return 1 if bad else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
