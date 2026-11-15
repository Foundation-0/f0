import sys, json, os, csv; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
rows = json.load(open(os.path.join(ROOT, 'summary.json')))
cache = spec.load_cache()
DN = {'H': 'horizontal', 'V': 'vertical', 'D': 'diagonal', 'A': 'antidiagonal'}
def define(s):
    shape = 'n X %d' % s['k'] if s['orient'] == 'nxk' else '%d X n' % s['k']
    alpha = 'binary' if s['q'] == 2 else '0..%d' % (s['q'] - 1)
    mode = 'exactly one' if s['mode'] == 'exact' else 'at most one'
    nb = '/'.join(DN[x] for x in 'HVDA' if x in s['nbrs'])
    return '%s %s arrays, %s adjacent pair (%s) with sum %d' % (shape, alpha, mode, nb, s['total'])
out = ['| A-number | definition (one line) | order | states | terms matched | start n | stated start | proof file | status |', '|---|---|---:|---:|---:|---:|---:|---|---|']
cs = [['oeis_id', 'definition', 'recurrence_order', 'states', 'oeis_terms_matched', 'proved_from_n', 'stated_start_in_oeis', 'natural_first_n', 'proof_kind', 'brute_force_sizes_numpy', 'proof_file', 'in_finite_state_proofs', 'status']]
skipped = []
for r in sorted(rows, key=lambda r: r['id']):
    if r['status'] != 'proved':
        skipped.append(r); continue
    a = 'A%06d' % r['id']
    st = r['stated'] if r['stated'] is not None else '-'
    status = 'proved all n>=%d%s' % (r['start'], ' (control: already in repo)' if r['already'] else '')
    out.append('| %s | %s | %d | %d | %d | %d | %s | certs/%s.json | %s |' % (a, define(r['spec']), r['order'], r['states'], r['terms'], r['start'], st, a, status))
    cs.append([a, define(r['spec']), r['order'], r['states'], r['terms'], r['start'], '' if r['stated'] is None else r['stated'], r['natural'], r['kind'], r['brute_n'], 'certs/%s.json' % a, r['already'], status])
open(os.path.join(ROOT, 'table.md'), 'w').write('\n'.join(out) + '\n')
csv.writer(open(os.path.join(ROOT, 'table.csv'), 'w', newline='')).writerows(cs)
print(len(out) - 2, 'proved rows;', len(skipped), 'skipped for cost')
for r in skipped: print(' skipped A%06d %s %s' % (r['id'], define(r['spec']), r['status']))
# accounting over the whole cached pool
tot = parsed = withrec = 0; norec = []; unparsed = []; tables = 0
for a, e in sorted(cache.items()):
    if 'neighbor totalling' not in e['name']: continue
    tot += 1
    if e['name'].startswith('T(n,k)') : tables += 1; continue
    s = spec.parse_name(e['name'])
    if not s:
        unparsed.append((a, e['name'][:100])); continue
    parsed += 1
    r = spec.recurrence_for(a, e)
    if r: withrec += 1
    else: norec.append((a, e.get('formula'), (e['data'].count(',') + 1)))
print('pool: %d entries with "neighbor totalling"; %d tables T(n,k); %d parsed strip/single-width entries; %d with Empirical recurrence parsed; %d without' % (tot, tables, parsed, withrec, len(norec)))
print('unparsed (n X n diagonal etc.):', len(unparsed))
for a, f, n in norec: print('  no parsed recurrence A%06d terms=%d formula=%s' % (a, n, (f or ['none'])[0][:90]))
# tightness of stated start
pr = [r for r in rows if r['status'] == 'proved']
tight = sum(1 for r in pr if r['stated'] is not None and r['stated'] == r['start'])
loose = [(r['id'], r['stated'], r['start']) for r in pr if r['stated'] is not None and r['stated'] > r['start']]
print('stated start == proved minimal start:', tight, '; stated later than necessary:', loose)
print('stated absent:', sum(1 for r in pr if r['stated'] is None), ' of which start==natural:', sum(1 for r in pr if r['stated'] is None and r['start'] == r['natural']))
print('proved', len(pr), 'new (not in repo):', sum(1 for r in pr if not r['already']))
from collections import Counter
print('proof kinds', Counter(r['kind'] for r in pr))
print('families (q, nbrs, mode):', len(set((r['spec']['q'], r['spec']['nbrs'], r['spec']['total'], r['spec']['mode']) for r in pr)))
print('order range', min(r['order'] for r in pr), max(r['order'] for r in pr), 'states range', min(r['states'] for r in pr), max(r['states'] for r in pr))
print('terms in OEIS data: min', min(r['terms'] for r in pr), 'cases with terms <= order:', [r['id'] for r in pr if r['terms'] <= r['order']][:50], sum(1 for r in pr if r['terms'] <= r['order']))
print('start - natural distribution', Counter(r['start'] - r['natural'] for r in pr))
