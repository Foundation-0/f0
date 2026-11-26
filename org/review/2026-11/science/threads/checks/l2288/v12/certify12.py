"""Exact-arithmetic existence/uniqueness check for real realizations of a planar Laman framework,
edge-pinned frame (for graphs with no triangle).  Imports nothing from the repository or the search code.

Input JSON keys: num_vertices, edges (1-based), code (MSB/GKT integer code of this exact edge list),
  triangle: [A, B]  (the pinned edge; the key name is kept for layout compatibility),
  sq_lengths (rational strings, every edge, edge order), pinned {A: [0, 0], B: [b, 0]} with b > 0,
  free_vertices, box_radius_exp2 (r = 2^-k), center_scale_exp2 (centres = integers / 2^m), centers.
Claim for each centre c: F(x) = |p_a - p_b|^2 - s_e (one equation per edge other than AB) has exactly one zero
in the box |x - c|_inf <= r, and DF is nonsingular there.  Same argument as ../certify.py:
F(c + d) = F(c) + DF(c) d + Q(d), |Q_e| <= q_e r^2 (q = 8 both ends free, 2 one end pinned); rows of
DF(c + d) - DF(c) have abs sum <= w_e r (w = 16 or 4).  With N(x) = x - Y F(x), Y a rounded float inverse:
  |N(c + d) - c|_i <= |Y F(c)|_i + alpha_i r + r^2 sum_e |Y_ie| q_e,   kappa_i = alpha_i + r sum_e |Y_ie| w_e.
All inclusion bounds < r (self-map, Brouwer) and all kappa_i < 1 (contraction) give exactly one zero.
Counting: every realization modulo direct isometries has exactly one representative with A at the origin and
B on the positive x-axis (lambda_AB > 0), so distinct boxes are distinct classes.  Mirror images are separate
boxes here (nothing is doubled).  Disjointness is proved by sorting centres on one coordinate and comparing
only neighbours closer than 2r in that coordinate (all integer arithmetic).
Usage: python -I certify12.py cert.json   (exit status 0 only if everything passes)
"""
import json, sys, itertools
from fractions import Fraction as Fr
import numpy as np


def die(msg):
    print("FAIL:", msg)
    raise SystemExit(1)


def main(path):
    d = json.load(open(path))
    n = d["num_vertices"]; E = [tuple(e) for e in d["edges"]]
    s = [Fr(x) for x in d["sq_lengths"]]
    pin = {int(k): (Fr(v[0]), Fr(v[1])) for k, v in d["pinned"].items()}
    free = list(d["free_vertices"])
    k_r = d["box_radius_exp2"]; m_c = d["center_scale_exp2"]; p_y = d.get("Y_exp2", 40)
    r = Fr(1, 2 ** k_r)
    if len(E) != 2 * n - 3 or len(set(map(frozenset, E))) != len(E) or len(s) != len(E):
        die("edge count")
    for k in range(2, n + 1):
        for S_ in itertools.combinations(range(1, n + 1), k):
            st = set(S_)
            if sum(1 for u, v in E if u in st and v in st) > 2 * k - 3:
                die(f"Laman condition fails on {S_}")
    pairs = list(itertools.combinations(range(1, n + 1), 2)); es = set(map(frozenset, E))
    code = sum(1 << (len(pairs) - 1 - i) for i, p in enumerate(pairs) if frozenset(p) in es)
    lsb = sum(1 << ((max(u, v) - 1) * (max(u, v) - 2) // 2 + min(u, v) - 1) for u, v in E)
    if code != d["code"]:
        die("graph code mismatch")
    print(f"graph: {n} vertices, {len(E)} edges, Laman on all subsets, MSB code {code}, LSB code of this labelling {lsb}")
    A, B = d["triangle"][:2]
    if len(pin) != 2 or sorted(pin) != sorted((A, B)) or sorted(free + list(pin)) != list(range(1, n + 1)):
        die("vertex partition")
    if pin[A] != (0, 0) or pin[B][1] != 0 or not pin[B][0] > 0:
        die("frame normalisation")
    ab = [i for i, (u, v) in enumerate(E) if u in pin and v in pin]
    if len(ab) != 1 or pin[B][0] ** 2 != s[ab[0]]:
        die("pinned edge")
    if any(not x > 0 for x in s):
        die("non-positive squared length")
    rem = [i for i in range(len(E)) if i != ab[0]]
    if len(rem) != 2 * len(free):
        die("equation count")
    idx = {v: j for j, v in enumerate(free)}
    print(f"frame: v{A} at origin, v{B} on positive x-axis; {len(rem)} equations in {2*len(free)} unknowns")
    M = len(rem); SC = 2 ** m_c; SY = 2 ** p_y
    wq = [(16, 8) if (E[ei][0] in idx and E[ei][1] in idx) else (4, 2) for ei in rem]
    worst_k = Fr(0); worst_in = Fr(0)
    C_ = d["centers"]
    for bi, cint in enumerate(C_):
        if len(cint) != M:
            die("centre length")
        P = dict(pin)
        for v in free:
            P[v] = (Fr(int(cint[2 * idx[v]]), SC), Fr(int(cint[2 * idx[v] + 1]), SC))
        Fv = []; J = [[Fr(0)] * M for _ in range(M)]
        for row, ei in enumerate(rem):
            u, v = E[ei]
            dx = P[u][0] - P[v][0]; dy = P[u][1] - P[v][1]
            Fv.append(dx * dx + dy * dy - s[ei])
            for vert, sg in ((u, 1), (v, -1)):
                if vert in idx:
                    J[row][2 * idx[vert]] = 2 * sg * dx; J[row][2 * idx[vert] + 1] = 2 * sg * dy
        Yf = np.linalg.inv(np.array([[float(x) for x in rw] for rw in J]))
        Y = [[Fr(int(round(Yf[i][j] * SY)), SY) for j in range(M)] for i in range(M)]
        for i in range(M):
            YJ = [sum(Y[i][k] * J[k][j] for k in range(M)) for j in range(M)]
            alpha = sum(abs((1 if i == j else 0) - YJ[j]) for j in range(M))
            kap = alpha + r * sum(abs(Y[i][k]) * wq[k][0] for k in range(M))
            rho = abs(sum(Y[i][k] * Fv[k] for k in range(M))) + alpha * r + r * r * sum(abs(Y[i][k]) * wq[k][1] for k in range(M))
            if not kap < 1:
                die(f"box {bi}: contraction bound {float(kap)}")
            if not rho < r:
                die(f"box {bi}: inclusion bound {float(rho / r)}")
            worst_k = max(worst_k, kap); worst_in = max(worst_in, rho / r)
    print(f"{len(C_)} boxes: each holds exactly one real solution with nonsingular Jacobian "
          f"(worst contraction {float(worst_k):.3e}, worst inclusion ratio {float(worst_in):.3e})")
    if 2 * SC % 2 ** k_r:
        die("radius not on centre grid")
    two_r = 2 * SC // 2 ** k_r
    Ci = [[int(x) for x in c] for c in C_]
    order = sorted(range(len(Ci)), key=lambda i: Ci[i][0])
    mn = None
    for a in range(len(order)):
        i = order[a]
        for b2 in range(a + 1, len(order)):
            j = order[b2]
            if Ci[j][0] - Ci[i][0] > two_r:
                break  # every later centre is farther than 2r in coordinate 0
            sep = max(abs(x - y) for x, y in zip(Ci[i], Ci[j]))
            if sep <= two_r:
                die(f"boxes {i} and {j} overlap")
            mn = sep if mn is None else min(mn, sep)
    print(f"pairwise disjoint (sorted sweep on coordinate 0; {'no pair' if mn is None else 'closest checked pair ' + format(mn / SC, '.3g')} within 2r = {float(2 * r):.3e} in that coordinate)")
    print(f"RESULT: {len(C_)} distinct real realizations modulo direct isometries")


if __name__ == "__main__":
    main(sys.argv[1])
