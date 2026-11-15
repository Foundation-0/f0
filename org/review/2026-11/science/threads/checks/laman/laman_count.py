"""Independent implementation of the Laman-number recursion of
Capco, Gallet, Grasegger, Koutschan, Lubbes, Schicho (arXiv:1701.05500), Theorem
"theorem:laman_number" (eq. "equation:laman_number") with base cases of
Proposition "proposition:base_cases".  Plain Python, exact integers.

A bigraph is a list of biedges; biedge i = (g_edge, h_edge), each a pair of
vertex labels (ints).  Isolated vertices are dropped (they change neither
dim nor components-minus-vertices).  Convention: the Laman number of (G,G) counts
complex realizations up to DIRECT complex isometries (rotation+translation),
so a reflection is a different realization.

Recursion, for pseudo-Laman B=(G,H) without self-loops, fixed biedge e:
  L(B) = L(^{e}B) + L(B^{e}) + sum_{(M,N)} L(^{M}B) * L(B^{N})
  ^{M}B = (G/M, H\\M),  B^{N} = (G\\N, H/N), biedges E\\M resp. E\\N
  M u N = E, M n N = {e}, |M|>=2, |N|>=2, both quotients pseudo-Laman.
Base: self-loop in G or H -> 0.  One biedge, both sides a single edge -> 1.
pseudo-Laman: dim G + dim H = |E| + 1, dim = |V| - #components.
"""
import sys
from functools import lru_cache

sys.setrecursionlimit(10000)


def _dim(edges):
    """dim of a graph given as list of vertex pairs (isolated vertices ignored)."""
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        parent.setdefault(a, a)
        parent.setdefault(b, b)
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    nv = len(parent)
    comps = len({find(x) for x in parent})
    return nv - comps


def _quotient(edges, idx_contract):
    """Graph G/M: contract the edges with indices in idx_contract (a set), return the
    list of remaining edges (indices not in idx_contract) renamed to classes, or None
    if one of them becomes a self-loop."""
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for i in idx_contract:
        a, b = edges[i]
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    out = []
    for i, (a, b) in enumerate(edges):
        if i in idx_contract:
            continue
        ra, rb = find(a), find(b)
        if ra == rb:
            return None
        out.append((ra, rb) if ra < rb else (rb, ra))
    return out


def _normalize(g, h):
    """Rename vertices canonically-enough for memoisation (exact key, not an
    isomorphism-complete canonical form)."""
    order = sorted(range(len(g)), key=lambda i: (g[i], h[i]))
    g = [g[i] for i in order]
    h = [h[i] for i in order]
    mg, mh = {}, {}
    G, H = [], []
    for (a, b), (c, d) in zip(g, h):
        for x in (a, b):
            mg.setdefault(x, len(mg))
        for x in (c, d):
            mh.setdefault(x, len(mh))
        G.append(tuple(sorted((mg[a], mg[b]))))
        H.append(tuple(sorted((mh[c], mh[d]))))
    return tuple(G), tuple(H)


STATS = {"calls": 0, "dim_greater": 0}


def laman_number_bigraph(G, H, ebar=0, _memo=None):
    memo = {} if _memo is None else _memo
    return _lam(tuple(map(tuple, G)), tuple(map(tuple, H)), ebar, memo)


def _lam(G, H, ebar, memo):
    # self-loops
    if any(a == b for a, b in G) or any(a == b for a, b in H):
        return 0
    k = len(G)
    if k == 0:
        return 0
    dsum = _dim(G) + _dim(H)
    if dsum < k + 1:
        return 0            # f_B not dominant
    if dsum > k + 1:
        STATS["dim_greater"] += 1
        raise ValueError("dim G + dim H > |E|+1: Laman number would be infinite/undefined")
    if k == 1:
        return 1
    key = (G, H)
    if key in memo:
        return memo[key]
    STATS["calls"] += 1
    ebar = ebar % k
    others = [i for i in range(k) if i != ebar]
    total = 0

    def sub(g, h, idxs, side):
        # side 'L': (G/M, H\M);  side 'R': (G\N, H/N); idxs = contracted/removed set
        if side == "L":
            qg = _quotient(g, idxs)
            if qg is None:
                return None
            qh = [h[i] for i in range(k) if i not in idxs]
        else:
            qh = _quotient(h, idxs)
            if qh is None:
                return None
            qg = [g[i] for i in range(k) if i not in idxs]
        return qg, qh

    # first two terms: M = {ebar} resp N = {ebar}
    for side in ("L", "R"):
        r = sub(G, H, {ebar}, side)
        if r is None:
            continue
        qg, qh = r
        if _dim(qg) + _dim(qh) != k:   # pseudo-Laman needs dsum = (k-1)+1
            continue
        total += _lam(*_normalize(qg, qh), 0, memo)
    # pairs (M,N): M = {ebar} u S, N = {ebar} u (others \ S), S nonempty proper
    m = len(others)
    for mask in range(1, (1 << m) - 1):
        S = {others[j] for j in range(m) if (mask >> j) & 1}
        T = {others[j] for j in range(m) if not (mask >> j) & 1}
        M = S | {ebar}
        N = T | {ebar}
        left = sub(G, H, M, "L")
        if left is None:
            continue
        lg, lh = left
        if _dim(lg) + _dim(lh) != len(lg) + 1:
            continue
        right = sub(G, H, N, "R")
        if right is None:
            continue
        rg, rh = right
        if _dim(rg) + _dim(rh) != len(rg) + 1:
            continue
        a = _lam(*_normalize(lg, lh), 0, memo)
        if a == 0:
            continue
        b = _lam(*_normalize(rg, rh), 0, memo)
        total += a * b
    memo[key] = total
    return total


def laman_number(edges, ebar=0):
    """Laman number of the graph with the given edge list: the bigraph (G,G)."""
    E = [tuple(sorted(e)) for e in edges]
    return laman_number_bigraph(E, E, ebar)


# ---------- graph codes -------------
def decode(code):
    """Integer code -> (n, edge list).  Bit index i*(i-1)//2 + j (LSB = bit 0) set
    <=> edge {j,i} with 0<=j<i.  Vertex count n = smallest n with n(n-1)/2 > top bit
    index (the same inference lnumber makes)."""
    top = code.bit_length() - 1
    n = 2
    while n * (n - 1) // 2 <= top:
        n += 1
    edges = []
    for i in range(1, n):
        for j in range(i):
            if (code >> (i * (i - 1) // 2 + j)) & 1:
                edges.append((j, i))
    return n, edges


def encode(edges):
    c = 0
    for a, b in edges:
        i, j = max(a, b), min(a, b)
        c |= 1 << (i * (i - 1) // 2 + j)
    return c


def is_laman(n, edges):
    """Direct definition: |E| = 2n-3 and every vertex subset spans <= 2|V'|-3 edges
    (|V'|>=2).  Brute force over subsets; fine for n <= 12."""
    if len(set(map(frozenset, edges))) != len(edges) or any(a == b for a, b in edges):
        return False
    if len(edges) != 2 * n - 3:
        return False
    adj = [0] * n
    for a, b in edges:
        adj[a] |= 1 << b
        adj[b] |= 1 << a
    for S in range(1, 1 << n):
        k = bin(S).count("1")
        if k < 2:
            continue
        cnt = 0
        for v in range(n):
            if (S >> v) & 1:
                cnt += bin(adj[v] & S).count("1")
        if cnt // 2 > 2 * k - 3:
            return False
    return True


if __name__ == "__main__":
    for c in sys.argv[1:]:
        n, e = decode(int(c))
        print(c, n, e, is_laman(n, e), laman_number(e))
