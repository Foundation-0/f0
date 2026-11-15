#!/usr/bin/env python3
"""Corrupt certificates in memory and confirm verify_all.verify_cert rejects every corruption.
Run both as `python3 test_corrupt.py` and `python3 -O test_corrupt.py` (no bare assert is used)."""
import copy, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import verify_all as V

SAMPLES = ['A268881', 'A268887', 'A268636', 'A268763', 'A269007', 'A268623']   # vector chains and scalar windows

def mutations(c):
    k = c['proof']['kind']
    def m(name, f):
        d = copy.deepcopy(c); f(d); return name, d
    yield m('coefficient+1', lambda d: d['recurrence']['coefficients'].__setitem__(0, d['recurrence']['coefficients'][0] + 1))
    yield m('last coefficient+1', lambda d: d['recurrence']['coefficients'].__setitem__(-1, d['recurrence']['coefficients'][-1] + 1))
    yield m('drop last coefficient', lambda d: d['recurrence']['coefficients'].pop())
    yield m('data term+1', lambda d: d['data_terms'].__setitem__(2, d['data_terms'][2] + 1))
    yield m('last data term+1', lambda d: d['data_terms'].__setitem__(-1, d['data_terms'][-1] + 1))
    yield m('min_start-1', lambda d: d['proof'].__setitem__('min_start', d['proof']['min_start'] - 1))
    yield m('min_start+1', lambda d: d['proof'].__setitem__('min_start', d['proof']['min_start'] + 1))
    yield m('graph digest', lambda d: d['machine'].__setitem__('graph_sha256', '0' * 64))
    yield m('state count', lambda d: d['machine'].__setitem__('states', d['machine']['states'] + 1))
    yield m('total changed', lambda d: d['spec'].__setitem__('total', d['spec']['total'] ^ 1))
    yield m('neighbour dropped', lambda d: d['spec'].__setitem__('nbrs', d['spec']['nbrs'][1:]))
    yield m('mode flipped', lambda d: d['spec'].__setitem__('mode', 'atmost' if d['spec']['mode'] == 'exact' else 'exact'))
    # for neighbour sets closed under transposition (e.g. HV) the two orientations define the same sequence
    if V.growth_nbrs(dict(c['spec'], orient='nxk')) != V.growth_nbrs(dict(c['spec'], orient='kxn')):
      yield m('orientation flipped', lambda d: d['spec'].__setitem__('orient', 'kxn' if d['spec']['orient'] == 'nxk' else 'nxk'))
    yield m('stated_start lowered flag', lambda d: d['recurrence'].__setitem__('holds_as_stated', not d['recurrence']['holds_as_stated']))
    yield m('brute range', lambda d: d['proof']['brute_checked_n'].append(99))
    yield m('kind swapped', lambda d: d['proof'].__setitem__('kind', 'scalar_window' if k == 'vector_chain' else 'vector_chain'))
    if k == 'vector_chain':
        def tweak(d):
            d['proof']['chain'][0][0] += 1
        yield m('chain entry+1', tweak)
        yield m('chain truncated', lambda d: d['proof']['chain'].pop())
    else:
        yield m('residual+1', lambda d: d['proof']['scalar_residuals'].__setitem__(0, d['proof']['scalar_residuals'][0] + 1))
        yield m('max_steps too small', lambda d: d['proof'].__setitem__('max_steps', 3))

def main():
    cdir = os.path.join(HERE, 'certs')
    total = rejected = 0
    for sid in SAMPLES:
        c = json.load(open(os.path.join(cdir, sid + '.json')))
        V.verify_cert(c)                      # the genuine certificate must pass
        for name, d in mutations(c):
            total += 1
            try:
                V.verify_cert(d)
            except (V.CertError, KeyError, TypeError, ValueError, IndexError) as e:
                rejected += 1
            else:
                print('NOT REJECTED:', sid, name)
    print('python -O' if sys.flags.optimize else 'python', ': rejected %d of %d corrupted certificates' % (rejected, total))
    return 0 if rejected == total else 1
if __name__ == '__main__':
    sys.exit(main())
