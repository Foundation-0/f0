"""The maximal 12-vertex Laman graph from S/threads/laman/validate_paper.log (LSB code 1514126886600097825):
decode, relabel 1-based, report triangles, MSB (GKT) code of the 1-based list, structure vs L2288."""
import itertools, json, sys
import networkx as nx
LSB = 1514126886600097825
def decode_lsb(code):
    top = code.bit_length() - 1; n = 2
    while n * (n - 1) // 2 <= top: n += 1
    return n, [(j, i) for i in range(1, n) for j in range(i) if (code >> (i * (i - 1) // 2 + j)) & 1]
n, e0 = decode_lsb(LSB)
E = sorted(tuple(sorted((a + 1, b + 1))) for a, b in e0)
pairs = list(itertools.combinations(range(1, n + 1), 2)); es = set(map(frozenset, E))
msb = sum(1 << (len(pairs) - 1 - i) for i, p in enumerate(pairs) if frozenset(p) in es)
G = nx.Graph(E)
print("n", n, "edges", len(E), E)
print("MSB code of 1-based list", msb)
print("degrees", sorted(dict(G.degree()).items()))
print("triangles", [c for c in nx.enumerate_all_cliques(G) if len(c) == 3])
json.dump(dict(n=n, edges=E, lsb_code=LSB, msb_code=msb), open("graph12.json", "w"))
