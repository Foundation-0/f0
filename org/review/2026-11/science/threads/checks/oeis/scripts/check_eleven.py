"""Task 2: are the eleven entries of finite-state-proofs still listed as empirical? Reads the live JSON cached in sources/
(each fetched with https://oeis.org/search?q=id:A......&fmt=json on 2026-11-15). Also compares the coefficients with the
repository's sources.json."""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec
cache = spec.load_cache()
repo = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'repos', 'finite-state-proofs', 'sources.json')))
want = {c['oeis_id']: (f['recurrence_coefficients'], c) for f in repo['families'] for c in f['claims']}
ok = True
for sid in sorted(want):
    a = int(sid[1:]); e = cache[a]
    lines = [x for x in e.get('formula', []) if 'mpirical' in x]
    r = spec.parse_recurrence(e.get('formula', []))
    same = bool(r) and r[0] == want[sid][0]
    data = [int(x) for x in e['data'].split(',')]
    same_data = data[:len(want[sid][1]['initial_terms'])] == want[sid][1]['initial_terms']
    print(sid, 'empirical-in-entry=%s' % bool(lines), 'coefficients==repo=%s' % same, 'initial terms==repo=%s' % same_data,
          'revision', e['revision'], 'last edit', e['time'])
    print('    ', lines[0][:100])
    ok &= bool(lines) and same and same_data
print('ALL ELEVEN STILL EMPIRICAL AND IDENTICAL TO sources.json' if ok else 'DIFFERENCE FOUND')
