"""Corrupt one input at a time; the verifier must raise Reject every time and must still accept the clean certificate.
Run as `python test_corrupt.py` and `python -O test_corrupt.py` (asserts are stripped under -O: the verifier uses none)."""
import json, copy, sys
sys.path.insert(0, '.')
from verify import verify, Reject, is_prime
def composite_near(p):
    n = p - 2
    while is_prime(n) or n % 2 == 0: n -= 1
    return n
ids = ['A268906', 'A268888', 'A269763', 'A268635', 'A269279']
total = rejected = 0; clean = 0
print("python -O active:", not __debug__)
for aid in ids:
    c0 = json.load(open('proofs/%s.json' % aid))
    verify(copy.deepcopy(c0)); clean += 1
    muts = {}
    def add(label, f):
        c = copy.deepcopy(c0)
        try: f(c); muts[label] = c
        except Exception: pass
    add('coefficient +1', lambda c: c['coefficients'].__setitem__(0, c['coefficients'][0] + 1))
    add('last coefficient +1', lambda c: c['coefficients'].__setitem__(-1, c['coefficients'][-1] + 1))
    import re
    def chg(c):
        w = re.search(r'totalling (\w+)', c['name']).group(1)
        new = {'two': 'three', 'three': 'two', 'four': 'five', 'five': 'four', 'six': 'five'}[w]
        c['name'] = c['name'].replace('totalling ' + w, 'totalling ' + new)
    add('name: total changed', chg)
    add('name: exactly <-> at most', lambda c: c.__setitem__('name', c['name'].replace('exactly once', 'no more than once') if 'exactly' in c['name'] else c['name'].replace('no more than once', 'exactly once')))
    add('hypothesis prime made composite', lambda c: c['primes_hypothesis'].__setitem__(0, composite_near(c['primes_hypothesis'][0])))
    add('window prime made composite', lambda c: c['primes_window'].__setitem__(0, composite_near(c['primes_window'][0])))
    add('window primes dropped to one', lambda c: c.__setitem__('primes_window', c['primes_window'][:1]) if len(c['primes_window']) > 1 else 1 / 0)
    add('hypothesis primes dropped', lambda c: c.__setitem__('primes_hypothesis', c['primes_hypothesis'][:1]) if len(c['primes_hypothesis']) > 1 else 1 / 0)
    add('start + 1', lambda c: c.__setitem__('start', c['start'] + 1))
    add('start - 1', lambda c: c.__setitem__('start', c['start'] - 1))
    add('nilpotency s - 1', lambda c: c.__setitem__('nilpotency_s', c['nilpotency_s'] - 1) if c['nilpotency_s'] > 0 else 1 / 0)
    add('nilpotency s + 1', lambda c: c.__setitem__('nilpotency_s', c['nilpotency_s'] + 1))
    add('sqrt poly constant term', lambda c: c['sqrt_poly'].__setitem__(0, c['sqrt_poly'][0] + 1))
    add('theorem index - 1', lambda c: c.__setitem__('theorem_index', c['theorem_index'] - 1))
    add('data term', lambda c: c['data_terms'].__setitem__(2, c['data_terms'][2] + 1))
    add('format tag', lambda c: c.__setitem__('format', 'x'))
    for label, c in muts.items():
        total += 1
        try:
            verify(c); print("ACCEPTED (bad)", aid, label)
        except Reject as e:
            rejected += 1
        except Exception as e:
            rejected += 1; print("  (non-Reject exception counted as rejection)", aid, label, repr(e)[:80])
print("clean certificates accepted:", clean, "/", len(ids), "; corrupted inputs rejected:", rejected, "/", total)
sys.exit(0 if rejected == total and clean == len(ids) else 1)
