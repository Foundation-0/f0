"""
Independent exact check of a certificate of real realizations in the EDGE frame (two pinned vertices).
Variant of l2288_independent.py for graphs with no triangle: one edge is pinned, so mirror images are separate
solutions and each must have its own box.

Written by the reviewer, from the checker used for the 10-vertex result in the science pass. It uses from the
certificate ONLY: the edge list, the 19 rational squared edge lengths, the pinned triangle and the 1,144 box
centres. Its code is separate from the two checkers written by the search, but it follows the same proof
template as l2288_independent.py, so it is a second arithmetic route, not a different method.

For each centre it builds its own preconditioner (float inverse of the exact Jacobian, rounded to dyadic
rationals) and proves in exact rational arithmetic that the box of the stated radius holds exactly one real
solution with nonsingular Jacobian.

Argument. F is quadratic: F(c+d) = F(c) + DF(c) d + Q(d), with Q_k(d) = |d_u - d_v|^2.
N(z) = z - Y F(z). On the box |d|_inf <= r:
  |N(c+d) - c|_i <= |Y F(c)|_i + alpha_i r + r^2 sum_k |Y_ik| q_k,  q_k = 8 (both ends free) or 2
  ||I - Y DF(z)||_row_i <= kappa_i = alpha_i + r sum_k |Y_ik| w_k,   w_k = 16 or 4
If the first is < r, N maps the box into its interior (a fixed point exists, Brouwer).
If kappa < 1, Y and DF(z) are invertible on the box and N is a contraction (the zero is unique).
Failures raise SystemExit, so the check behaves the same under python -O.
Usage: python3 -I l2288_independent.py <certificate.json> [expected integer code] [expected number of realizations]
"""
import json, sys, itertools
from fractions import Fraction as Fr
import numpy as np

d = json.load(open(sys.argv[1]))
E = [tuple(e) for e in d["edges"]]; n = d["num_vertices"]
lam2 = [Fr(s) for s in d["sq_lengths"]]
pin = {int(k): (Fr(v[0]), Fr(v[1])) for k, v in d["pinned"].items()}
free = d["free_vertices"]; tri = d["triangle"]
r = Fr(1, 2 ** d["box_radius_exp2"]); cs = 2 ** d["center_scale_exp2"]
def die(m): raise SystemExit("FAIL: " + m)

# --- the graph ---
if len(E) != 2 * n - 3 or len(set(map(frozenset, E))) != len(E) or len(lam2) != len(E): die("edge count")
if any(not (1 <= u <= n and 1 <= v <= n and u != v) for u, v in E): die("edge endpoints")
if any(not l > 0 for l in lam2): die("squared length not positive")
for k in range(2, n + 1):
    for S_ in itertools.combinations(range(1, n + 1), k):
        s = set(S_)
        if sum(1 for u, v in E if u in s and v in s) > 2 * k - 3: die(f"not Laman on {S_}")
es = set(map(frozenset, E))
# integer code in the convention of the authors' library: bit i(i-1)/2 + j is the edge {j, i}, j < i, 0-based
def code_of(perm):
    c = 0
    for u, v in E:
        a, b = sorted((perm[u], perm[v])); c |= 1 << (b * (b - 1) // 2 + a)
    return c
print(f"graph: {n} vertices, {len(E)} edges, Laman (all vertex subsets checked)")

# --- the pinned triangle satisfies its three edge equations exactly ---
sq = lambda a, b: (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
if sorted(pin) != sorted(tri): die("pinned set is not the triangle")
tri_edges = [i for i, (u, v) in enumerate(E) if u in pin and v in pin]
if len(pin) != 2 or len(tri_edges) != 1: die("the pinned vertices are not one edge of the graph")
for i in tri_edges:
    u, v = E[i]
    if sq(pin[u], pin[v]) != lam2[i]: die(f"pinned edge {E[i]} length")
a, b = pin[tri[0]], pin[tri[1]]
if not (a == (0, 0) and b[1] == 0 and b[0] > 0): die("frame normalisation")
rem = [i for i in range(len(E)) if i not in tri_edges]
if sorted(free + list(pin)) != list(range(1, n + 1)) or len(rem) != 2 * len(free): die("unknown count")
print(f"frame: v{tri[0]} at origin, v{tri[1]} on the positive x-axis; pinned edge exact;", len(rem), "equations,", 2 * len(free), "unknowns")

idx = {v: i for i, v in enumerate(free)}
YS = 2 ** 44
def check_box(cnum):
    if len(cnum) != 2 * len(free): die("centre length")
    z = [Fr(int(x), cs) for x in cnum]
    P = dict(pin); P.update({v: (z[2 * idx[v]], z[2 * idx[v] + 1]) for v in free})
    m = len(rem); F = []; J = [[Fr(0)] * m for _ in range(m)]; w = []; q = []
    for k, ei in enumerate(rem):
        u, v = E[ei]; dx = P[u][0] - P[v][0]; dy = P[u][1] - P[v][1]
        F.append(dx * dx + dy * dy - lam2[ei])
        nf = 0
        for vert, sgn in ((u, 1), (v, -1)):
            if vert in idx:
                J[k][2 * idx[vert]] = 2 * sgn * dx; J[k][2 * idx[vert] + 1] = 2 * sgn * dy; nf += 1
        if nf == 0: die("equation with no free vertex")
        w.append(16 if nf == 2 else 4); q.append(8 if nf == 2 else 2)
    Yf = np.linalg.inv(np.array([[float(x) for x in row] for row in J]))
    Y = [[Fr(int(round(float(Yf[i][j]) * YS)), YS) for j in range(m)] for i in range(m)]
    worst_k = Fr(0); worst_in = Fr(0)
    for i in range(m):
        alpha = sum(abs((1 if i == j else 0) - sum(Y[i][k] * J[k][j] for k in range(m))) for j in range(m))
        kappa = alpha + r * sum(abs(Y[i][k]) * w[k] for k in range(m))
        rho = abs(sum(Y[i][k] * F[k] for k in range(m))) + alpha * r + r * r * sum(abs(Y[i][k]) * q[k] for k in range(m))
        if not kappa < 1: die(f"contraction bound ({float(kappa):.3e})")
        if not rho < r: die(f"inclusion bound (ratio {float(rho / r):.3e})")
        worst_k = max(worst_k, kappa); worst_in = max(worst_in, rho / r)
    return worst_k, worst_in

C = [[int(x) for x in c] for c in d["centers"]]; wk = Fr(0); wi = Fr(0)
for t, cnum in enumerate(C):
    k_, i_ = check_box(cnum); wk = max(wk, k_); wi = max(wi, i_)
print(f"{len(C)} boxes: each holds exactly one real nonsingular solution (worst contraction bound {float(wk):.3e}, worst inclusion ratio {float(wi):.3e})")

# --- the boxes are pairwise disjoint ---
two_r = 2 * cs // 2 ** d["box_radius_exp2"]; mn = None
order_ = sorted(range(len(C)), key=lambda i: C[i][0])
for ii in range(len(order_)):
    ci = C[order_[ii]]
    for jj in range(ii + 1, len(order_)):
        cj = C[order_[jj]]
        if cj[0] - ci[0] > two_r and (mn is not None and cj[0] - ci[0] >= mn): break
        sep = max(abs(x - y) for x, y in zip(ci, cj))
        if sep <= two_r: die(f"boxes {order_[ii]},{order_[jj]} overlap")
        if mn is None or sep < mn: mn = sep
print(f"pairwise disjoint: min centre separation {mn / cs:.3e} against 2r = {float(2 * r):.3e}")
print(f"RESULT: {len(C)} distinct real nonsingular realizations modulo direct isometries (mirror images are among them)")

# --- optional: the graph is the one with the expected integer code, up to relabelling ---
if len(sys.argv) > 2:
    target = int(sys.argv[2]); tn = n
    tE = set()
    for i in range(tn):
        for j in range(i):
            if (target >> (i * (i - 1) // 2 + j)) & 1: tE.add(frozenset((j, i)))
    if len(tE) != len(E): die("target code has a different number of edges")
    # search for an isomorphism by degree-refined backtracking
    adjC = {v: set() for v in range(1, n + 1)}
    for u, v in E: adjC[u].add(v); adjC[v].add(u)
    adjT = {v: set() for v in range(tn)}
    for e in tE:
        u, v = tuple(e); adjT[u].add(v); adjT[v].add(u)
    order = sorted(adjC, key=lambda v: -len(adjC[v]))
    def extend(m):
        if len(m) == n: return m
        v = order[len(m)]
        for t in range(tn):
            if t in m.values() or len(adjT[t]) != len(adjC[v]): continue
            if all((m[u] in adjT[t]) == (u in adjC[v]) for u in m):
                m[v] = t
                res = extend(m)
                if res: return res
                del m[v]
        return None
    iso = extend({})
    if not iso or code_of(iso) != target: die("graph is not the target code up to relabelling")
    print(f"graph matches integer code {target} under the vertex map {iso}")

# --- optional: the number of realizations equals the expected complex count ---
if len(sys.argv) > 3:
    if len(C) != int(sys.argv[3]): die(f"{len(C)} realizations certified, {sys.argv[3]} expected")
    print(f"count matches the expected {sys.argv[3]}")
