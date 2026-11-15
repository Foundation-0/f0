"""Build one certificate per sequence into ../certs/ and a summary table. Uses fsm.py (numpy builder)
and brute.py (independent numpy enumeration for larger small cases)."""
import sys, os, json, hashlib, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fsm, spec, brute
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CERTS = os.path.join(ROOT, 'certs'); os.makedirs(CERTS, exist_ok=True)
SKIP_BIG = {269095, 269107}       # q=4, width 6: 3564 states, 1.3M transitions; skipped for verifier runtime only
ALREADY = {268881,268882,268883,268884,268885,268989,268990,268991,268992,268993,268994}  # in finite-state-proofs

def digest(m):
    h = hashlib.sha256()
    for (u, row), e in zip(m['states'], m['edges']):
        h.update(('%d:%s>%s\n' % (u, ''.join(map(str, row)), ','.join(map(str, sorted(e))))).encode())
    return h.hexdigest()

def prove(m, coef, o):
    D = len(m['states']); d = len(coef); E = m['edges']; A = m['accept']
    pw = [m['init']]
    for _ in range(d): pw.append(fsm.advance(pw[-1], E))
    z = [pw[d][i] - sum(coef[l - 1] * pw[d - l][i] for l in range(1, d + 1)) for i in range(D)]
    lin = lambda v: sum(x for x, a in zip(v, A) if a)
    chain = [z]; scal = []; run = 0
    cap = 4 * D + 200
    t_start = time.time()
    while True:
        if not any(z):
            kind = 'vector_chain'; break
        r = lin(z); scal.append(r); run = run + 1 if r == 0 else 0
        if run >= D: kind = 'scalar_window'; break
        if len(scal) > cap or time.time() - t_start > 400: return None
        z = fsm.advance(z, E); chain.append(z)
    if kind == 'vector_chain':
        last_nz = max([j for j, r in enumerate(scal) if r], default=-1)
        return dict(kind=kind, chain=chain, min_start=o + d + last_nz + 1, scal=scal)
    last_nz = max([j for j, r in enumerate(scal) if r], default=-1)
    return dict(kind=kind, scalar_residuals=scal, max_steps=cap, min_start=o + d + last_nz + 1, scal=scal)

def main():
    cache = spec.load_cache()
    rows = []
    for a, e in sorted(cache.items()):
        s = spec.parse_name(e['name'])
        if not s: continue
        r = spec.recurrence_for(a, e)
        if not r or a in SKIP_BIG: continue
        out = os.path.join(CERTS, 'A%06d.json' % a)
        t0 = time.time()
        coef, line, stated, origin = r
        data = [int(x) for x in e['data'].split(',')]
        o = int(e['offset'].split(',')[0])
        if s['q'] ** s['k'] > 20000:
            rows.append(dict(id=a, spec=s, order=len(coef), status='skipped: cost (q^k=%d rows)' % s['q'] ** s['k'])); print(a, 'skip rows'); continue
        m = fsm.build(s)
        nnz = sum(map(len, m['edges']))
        if len(m['states']) > 2100 or nnz > 500000:
            rows.append(dict(id=a, spec=s, order=len(coef), states=len(m['states']), status='skipped: cost (%d states, %d transitions)' % (len(m['states']), nnz))); print(a, 'skip cost', len(m['states']), nnz); continue
        T = fsm.terms(m, max(len(data), len(coef) + 1))
        if T[:len(data)] != data:
            rows.append(dict(id=a, status='DATA MISMATCH')); print(a, 'DATA MISMATCH'); continue
        p = prove(m, coef, o)
        if p is None:
            rows.append(dict(id=a, status='no proof found within bound')); print(a, 'no proof'); continue
        natural = o + len(coef)
        holds = (stated is None and p['min_start'] == natural) or (stated is not None and p['min_start'] <= stated)
        # brute: numpy enumeration up to 2^22 boards, literal orientation; plus the same sizes the verifier reuses
        bt = brute.literal_terms(s, 22 if s['q'] == 2 else 22)
        bmatch = bt == data[:len(bt)]
        # verifier's pure-python brute range
        vb = []; n = o
        while s['q'] ** ((n if s['orient'] == 'nxk' else s['k']) * (s['k'] if s['orient'] == 'nxk' else n)) <= 12000:
            vb.append(n); n += 1
        proof = {k: v for k, v in p.items() if k != 'scal'}
        proof['brute_checked_n'] = vb
        cert = dict(
            oeis_id='A%06d' % a, name=e['name'], offset=o,
            source=dict(url='https://oeis.org/A%06d' % a, oeis_revision=e.get('revision'), oeis_time=e.get('time'),
                        entry_sha256=hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest(),
                        fetched='2026-11-15', note='JSON from https://oeis.org/search?q=id:A%06d&fmt=json' % a),
            spec=s, data_terms=data,
            recurrence=dict(coefficients=coef, source_line=line, source_origin=origin, stated_start=stated, holds_as_stated=holds),
            machine=dict(states=len(m['states']), transitions=sum(map(len, m['edges'])), graph_sha256=digest(m)),
            proof=proof)
        json.dump(cert, open(out, 'w'))
        rows.append(dict(id=a, spec=s, order=len(coef), states=len(m['states']), terms=len(data), kind=p['kind'],
                         start=p['min_start'], natural=natural, stated=stated, holds=holds,
                         brute_n=len(bt), brute_ok=bmatch, already=a in ALREADY, status='proved' if bmatch else 'BRUTE MISMATCH'))
        print(a, rows[-1]['status'], p['kind'], 'D', len(m['states']), 'start', p['min_start'], 'natural', natural, 'stated', stated,
              'brute', len(bt), bmatch, round(time.time() - t0, 1), flush=True)
    json.dump(rows, open(os.path.join(ROOT, 'summary.json'), 'w'), indent=1)
main()
