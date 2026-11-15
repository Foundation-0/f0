import json, time, ctypes, itertools, random, sys
import networkx as nx
from laman_count import *
R = '../../repos/rigid-realizations/'
cert = json.load(open(R + 'rigid_realizations_l880_pr_bundle/results/l880-all-880-real/l880_certificate.json'))
lib = ctypes.CDLL('lnumber_src/build/lnumber_noomp.dylib')
lib.laman_number.argtypes = [ctypes.c_char_p]
lib.laman_number.restype = ctypes.c_size_t
def ln(code): return lib.laman_number(str(code).encode())

for code in (4778440734593, 18120782205838348):
    n, e = decode(code)
    t = time.time()
    mine = laman_number(e); dt = time.time() - t
    print('code', code, 'n', n, 'edges', len(e), 'laman', is_laman(n, e), 'mine', mine, '%.1fs' % dt, 'lnumber', ln(code), flush=True)
    print('  edges', e)

n, e = decode(4778440734593)
ce = [tuple(x) for x in cert['edges']]
print('cert edges', ce, 'n', cert['num_vertices'], 'cert code', encode(ce))
G1 = nx.Graph(e); G2 = nx.Graph(ce)
gm = nx.isomorphism.GraphMatcher(G1, G2)
print('isomorphic:', gm.is_isomorphic())
m = gm.mapping
print('decoded vertex -> certificate vertex:', dict(sorted(m.items())))
img = sorted(tuple(sorted((m[a], m[b]))) for a, b in e)
print('mapped decoded edges == certificate edges:', img == sorted(tuple(sorted(x)) for x in ce))
print('number of automorphisms of the graph:', sum(1 for _ in nx.isomorphism.GraphMatcher(G1, G1).isomorphisms_iter()))
print('cert certificate graph name:', cert['graph'], 'cert complex count:', cert['complex_realizations_SE2'])
print('certificate vertices are 1-based; cert graph Laman (shifted to 0-based):', is_laman(10, [(a-1,b-1) for a,b in ce]))
