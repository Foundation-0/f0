"""
Independent check of the rigid-realizations L880 claim.
Uses from the repository ONLY: the edge list, the 17 rational edge lengths, the pinned triangle and
the 440 box centres.  It does NOT use the repository's preconditioner matrices or any of its code.
For each centre it builds its own preconditioner (float inverse of the exact Jacobian, rounded to
dyadic rationals) and then proves, in exact rational arithmetic, that the box of radius 2^-26
contains exactly one real solution with nonsingular Jacobian.

Argument.  F is quadratic: F(c+d) = F(c) + DF(c) d + Q(d), with Q_k(d) = |d_u - d_v|^2.
N(z) = z - Y F(z).  On the box |d|_inf <= r:
  |N(c+d) - c|_i <= |Y F(c)|_i + alpha_i r + r^2 sum_k |Y_ik| q_k,  q_k = 8 (both ends free) or 2
  ||I - Y DF(z)||_row_i <= kappa_i = alpha_i + r sum_k |Y_ik| w_k,   w_k = 16 or 4
If the first is < r, N maps the box into its interior (a fixed point exists, Brouwer).
If kappa < 1, Y and DF(z) are invertible on the box and N is a contraction (the zero is unique).
Failures raise SystemExit.  Usage: python3 -I l880_independent.py <certificate.json>
"""
import json, sys, itertools
from fractions import Fraction as Fr
import numpy as np

d = json.load(open(sys.argv[1]))
E = [tuple(e) for e in d["edges"]]; n = d["num_vertices"]
lam = [Fr(s) for s in d["edge_lengths"]]
pin = {int(k): (Fr(v[0]), Fr(v[1])) for k, v in d["pinned_vertices"].items()}
free = d["free_vertices"]; rem = d["remaining_edge_indices"]
r = Fr(1, 2 ** d["box_radius_exp2"]); cs = 2 ** d["center_scale_exp2"]
def die(m): raise SystemExit("FAIL: " + m)

# --- the graph ---
if len(E) != 2 * n - 3 or len(set(map(frozenset, E))) != len(E): die("edge count")
for k in range(2, n + 1):
    for S_ in itertools.combinations(range(1, n + 1), k):
        s = set(S_)
        if sum(1 for u, v in E if u in s and v in s) > 2 * k - 3: die(f"not Laman on {S_}")
pairs = list(itertools.combinations(range(1, n + 1), 2)); es = set(map(frozenset, E))
code = sum(1 << (len(pairs) - 1 - i) for i, p in enumerate(pairs) if frozenset(p) in es)
print("graph: 10 vertices, 17 edges, Laman (all vertex subsets checked); integer encoding", code)

# --- the pinned triangle satisfies its three edge equations exactly ---
sq = lambda a, b: (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
pinned_edges = [i for i in range(len(E)) if i not in rem]
for i in pinned_edges:
    u, v = E[i]
    if sq(pin[u], pin[v]) != lam[i] ** 2: die(f"pinned edge {E[i]} length")
if sorted(set(sum((list(E[i]) for i in pinned_edges), []))) != sorted(pin): die("pinned set")
(a, b, c3) = (pin[7], pin[2], pin[3])
if not (a == (0, 0) and b[1] == 0 and b[0] > 0 and c3[1] > 0): die("frame normalisation")
if sorted(free + list(pin)) != list(range(1, n + 1)) or len(rem) != 2 * len(free): die("unknown count")
print("frame: v7 at origin, v2 on the positive x-axis, v3 above it; pinned edges exact;", len(rem), "equations,", 2 * len(free), "unknowns")

idx = {v: i for i, v in enumerate(free)}
def check_box(cnum):
    z = [Fr(x, cs) for x in cnum]
    P = dict(pin); P.update({v: (z[2 * idx[v]], z[2 * idx[v] + 1]) for v in free})
    m = len(rem); F = []; J = [[Fr(0)] * m for _ in range(m)]; w = []; q = []
    for k, ei in enumerate(rem):
        u, v = E[ei]; dx = P[u][0] - P[v][0]; dy = P[u][1] - P[v][1]
        F.append(dx * dx + dy * dy - lam[ei] ** 2)
        nf = 0
        for vert, sgn in ((u, 1), (v, -1)):
            if vert in idx:
                J[k][2 * idx[vert]] = 2 * sgn * dx; J[k][2 * idx[vert] + 1] = 2 * sgn * dy; nf += 1
        w.append(16 if nf == 2 else 4); q.append(8 if nf == 2 else 2)
    Yf = np.linalg.inv(np.array([[float(x) for x in row] for row in J]))
    Y = [[Fr(int(round(Yf[i][j] * 2 ** 30)), 2 ** 30) for j in range(m)] for i in range(m)]
    worst_k = Fr(0); worst_in = Fr(0)
    for i in range(m):
        alpha = sum(abs((1 if i == j else 0) - sum(Y[i][k] * J[k][j] for k in range(m))) for j in range(m))
        kappa = alpha + r * sum(abs(Y[i][k]) * w[k] for k in range(m))
        rho = abs(sum(Y[i][k] * F[k] for k in range(m))) + alpha * r + r * r * sum(abs(Y[i][k]) * q[k] for k in range(m))
        if not kappa < 1: die("contraction bound")
        if not rho < r: die("inclusion bound")
        worst_k = max(worst_k, kappa); worst_in = max(worst_in, rho / r)
    return worst_k, worst_in

C = d["centers_num"]; wk = Fr(0); wi = Fr(0)
for cnum in C:
    k_, i_ = check_box(cnum); wk = max(wk, k_); wi = max(wi, i_)
print(f"{len(C)} boxes: each holds exactly one real nonsingular solution (worst contraction bound {float(wk):.3e}, worst inclusion ratio {float(wi):.3e})")

# --- the boxes are pairwise disjoint ---
two_r = 2 * cs // 2 ** d["box_radius_exp2"]; arr = np.array(C, dtype=object); mn = None
for i in range(len(C)):
    for j in range(i + 1, len(C)):
        sep = max(abs(x - y) for x, y in zip(C[i], C[j]))
        if sep <= two_r: die(f"boxes {i},{j} overlap")
        mn = sep if mn is None else min(mn, sep)
print(f"pairwise disjoint: min centre separation {mn / cs:.6f} against 2r = {float(2 * r):.3e}")
print(f"RESULT: {len(C)} distinct real nonsingular realizations with v3 above the axis; mirror images give {2 * len(C)} classes modulo direct isometries")
