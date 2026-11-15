"""Is the 12-vertex graph a Henneberg I or II extension of L2288?"""
import json, itertools, networkx as nx
import sys; sys.path.insert(0, '..')
from lam import decode
g = json.load(open("graph12.json")); G = nx.Graph([tuple(e) for e in g["edges"]])
H = nx.Graph(decode(11, 18120782205838348))
print("min degree", min(d for _, d in G.degree()))
hits = []
for v in G:
    if G.degree(v) == 3:
        nb = sorted(G[v])
        for a, b in itertools.combinations(nb, 2):
            if G.has_edge(a, b): continue
            K = G.copy(); K.remove_node(v); K.add_edge(a, b)
            if nx.is_isomorphic(K, H): hits.append((v, nb, (a, b)))
print("H2 reductions to L2288:", hits)
