import random, ctypes, sys
from laman_count import *
lib = ctypes.CDLL('lnumber_src/build/lnumber_noomp.dylib')
lib.laman_number.argtypes = [ctypes.c_char_p]; lib.laman_number.restype = ctypes.c_size_t
def ln(c): return lib.laman_number(str(c).encode())
def henneberg(n, rng):
    E = {(0, 1)}; k = 2
    while k < n:
        V = list(range(k))
        if rng.random() < 0.5 or len(E) < 2:
            u, v = rng.sample(V, 2); E |= {(min(u, k), max(u, k)), (min(v, k), max(v, k))}
        else:
            u, v = rng.choice(sorted(E)); w = rng.choice([x for x in V if x not in (u, v)])
            E.discard((u, v)); E |= {(u, k), (v, k), (w, k)}
        k += 1
    return sorted(E)
rng = random.Random(1)
bad = 0; cnt = 0
for n in range(3, 10):
    for _ in range(25 if n < 9 else 8):
        e = henneberg(n, rng)
        if not is_laman(n, e): print('generator produced non-Laman', e); bad += 1; continue
        a = laman_number(e, ebar=rng.randrange(len(e)))
        b = ln(encode(e)); c = laman_number(e, ebar=0)
        cnt += 1
        if not (a == b == c): print('DISAGREE', n, e, a, b, c); bad += 1
print('random Laman graphs compared (mine with random ebar, mine ebar=0, lnumber):', cnt, 'disagreements:', bad)
# minimum 2^(n-2) on Henneberg-1-only graphs (path-like fan): triangle chain
for n in range(3, 11):
    e = [(0, 1)] + [(i, j) for j in range(2, n) for i in (j-2, j-1)]
    print('H1-only graph n=%d: mine %d, 2^(n-2)=%d' % (n, laman_number(e), 2**(n-2)))
# corruption: remove one edge -> not Laman (flexible), add a chord -> overbraced
n, e = decode(4778440734593)
e1 = e[:-1]
try: print('minus an edge ->', laman_number(e1))
except Exception as ex: print('minus an edge -> raises', type(ex).__name__, ex)
e2 = e + [(5, 9)]
try: print('plus an edge ->', laman_number(e2))
except Exception as ex: print('plus an edge -> raises', type(ex).__name__, ex)
# non-Laman with 2n-3 edges: K4 + pendant-ish (n=5: K4 has 6 edges =2*4-2 > 2*4-3)
e3 = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3),(3,4)]
print('K4 plus pendant (7 edges, n=5, not Laman):', end=' ')
try: print(laman_number(e3))
except Exception as ex: print('raises', type(ex).__name__, ex)
