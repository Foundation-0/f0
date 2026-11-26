"""Structure of L2288 and its relation to L880 (Henneberg I / II)."""
import itertools, networkx as nx
def decode(n, code):
    # MSB-lexicographic bit order; laman/laman_count.py decodes the same code LSB first (isomorphic graph).
    pairs = list(itertools.combinations(range(1, n+1), 2)); m = len(pairs)
    return [pairs[k] for k in range(m) if (code >> (m-1-k)) & 1]
E11 = decode(11, 18120782205838348)
E10 = decode(10, 4778440734593)
print("L2288 edges", len(E11), E11)
print("L880 edges", len(E10), E10)
G = nx.Graph(E11); H = nx.Graph(E10)
print("deg L2288", dict(G.degree())); print("deg L880", dict(H.degree()))
print("L2288 triangles", [c for c in nx.enumerate_all_cliques(G) if len(c)==3])
# H1: remove degree-2 vertex
for v in G:
    if G.degree(v) == 2:
        K = G.copy(); K.remove_node(v); print("H1 removal", v, nx.is_isomorphic(K, H))
    if G.degree(v) == 3:
        nb = list(G[v])
        for a, b in itertools.combinations(nb, 2):
            if G.has_edge(a, b): continue
            K = G.copy(); K.remove_node(v); K.add_edge(a, b)
            if nx.is_isomorphic(K, H):
                print(f"H2 reverse: remove {v} (nbrs {nb}), add edge {a,b} -> L880")
# does L2288 contain L880 as a subgraph on 10 vertices with 17 edges (i.e. vertex deletion keeps 17 edges)?
for v in G:
    K = G.copy(); K.remove_node(v)
    if K.number_of_edges() == 17: print("vertex", v, "deletion leaves 17 edges; iso to L880:", nx.is_isomorphic(K, H))
print("H2 reductions of L2288 (remove deg-3 v, add non-edge among its nbrs):")
seen = []
for v in G:
    if G.degree(v) == 3:
        nb = sorted(G[v])
        for a, b in itertools.combinations(nb, 2):
            if G.has_edge(a, b): continue
            K = G.copy(); K.remove_node(v); K.add_edge(a, b)
            cls = next((i for i, S in enumerate(seen) if nx.is_isomorphic(S, K)), None)
            if cls is None: seen.append(K); cls = len(seen)-1
            print(f"  remove {v} nbrs {nb} add {(a,b)} -> class {cls}, deg seq {sorted(d for _,d in K.degree())}")
