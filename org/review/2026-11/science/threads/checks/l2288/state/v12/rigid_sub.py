"""Rigid (Laman-tight) proper subgraphs of the 12-vertex graph: vertex sets with exactly 2k-3 induced edges."""
import json, itertools
g = json.load(open("graph12.json")); E = [tuple(e) for e in g["edges"]]; n = g["n"]
for k in range(3, n):
    hits = [S for S in itertools.combinations(range(1, n + 1), k) if sum(1 for u, v in E if u in S and v in S) == 2 * k - 3]
    print(k, len(hits), hits[:5])
