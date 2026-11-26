"""Exact-arithmetic existence/uniqueness check for real realizations of a planar Laman framework.

Written for this thread; it imports nothing from the repository and nothing from the search code.
Input JSON:
  num_vertices, edges (1-based pairs), code (GKT integer encoding, checked),
  sq_lengths: rational squared edge lengths (strings) for every edge, in edge order,
  pinned: {vertex: [x, y]} rational coordinates of the three triangle vertices,
  free_vertices: order of the unknowns (x_v, y_v) per free vertex,
  box_radius_exp2: r = 2^-k,  center_scale_exp2: centres are integers / 2^m,
  centers: list of integer vectors (length 2 * #free),
  Y_exp2: preconditioner entries are integers / 2^p (built here from a float inverse; not read from input).
Claim checked for each centre c:  F(x) = |p_a - p_b|^2 - s_e  (one equation per non-triangle edge) has
exactly one zero in the box |x - c|_inf <= r, and DF is nonsingular on that box.
Argument (F quadratic, so exact Taylor):  F(c + d) = F(c) + DF(c) d + Q(d), |Q_e(d)| <= q_e r^2 with
q_e = 8 if both ends are free, 2 if one end is pinned.  Entries of DF(c + d) - DF(c) are 2 (d_a - d_b),
so each row of that difference has absolute sum <= w_e r with w_e = 16 (both free) or 4 (one free).
With N(x) = x - Y F(x):
  |N(c + d) - c|_i <= |Y F(c)|_i + alpha_i r + r^2 sum_e |Y_ie| q_e     (alpha_i = row i abs sum of I - Y DF(c))
  row i abs sum of I - Y DF(x) <= kappa_i = alpha_i + r sum_e |Y_ie| w_e  for every x in the box.
If every bound in the first line is < r, N maps the box into itself (Brouwer gives a fixed point).
If every kappa_i < 1, Y DF(c) is invertible (so Y is), N is a contraction on the box, the fixed point is
unique, and fixed points of N are exactly zeros of F.  All comparisons are exact rational arithmetic.
Realizations are counted modulo direct isometries: the frame (pinned triangle vertex A at the origin,
B on the positive x-axis) is unique for any realization, so distinct boxes give distinct classes, and
since pinned C has y > 0, each box's mirror image (C below the axis) is a further distinct class.
Usage: python -I certify.py cert.json     (exit status 0 only if everything passes)
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
    k_r = d["box_radius_exp2"]; m_c = d["center_scale_exp2"]; p_y = d["Y_exp2"]
    r = Fr(1, 2 ** k_r)

    # graph: Laman count condition on every vertex subset, and the stated integer code
    if len(E) != 2 * n - 3 or len(set(map(frozenset, E))) != len(E):
        die("edge count or repeated edge")
    for k in range(2, n + 1):
        for S_ in itertools.combinations(range(1, n + 1), k):
            st = set(S_)
            if sum(1 for u, v in E if u in st and v in st) > 2 * k - 3:
                die(f"Laman condition fails on {S_}")
    pairs = list(itertools.combinations(range(1, n + 1), 2)); es = set(map(frozenset, E))
    code = sum(1 << (len(pairs) - 1 - i) for i, p in enumerate(pairs) if frozenset(p) in es)
    if code != d["code"]:
        die("graph code mismatch")
    print(f"graph: {n} vertices, {len(E)} edges, Laman on all subsets, code {code}")

    # frame
    if sorted(free + list(pin)) != list(range(1, n + 1)) or len(pin) != 3:
        die("vertex partition")
    A, B, C = d["triangle"]
    if pin[A] != (0, 0) or pin[B][1] != 0 or not pin[B][0] > 0 or not pin[C][1] > 0:
        die("frame normalisation")
    tri = [i for i, (u, v) in enumerate(E) if u in pin and v in pin]
    if len(tri) != 3:
        die("pinned triangle edges")
    for i in tri:
        u, v = E[i]
        if (pin[u][0] - pin[v][0]) ** 2 + (pin[u][1] - pin[v][1]) ** 2 != s[i]:
            die(f"pinned edge {E[i]} squared length")
    if any(not x > 0 for x in s):
        die("non-positive squared length")
    rem = [i for i in range(len(E)) if i not in tri]
    if len(rem) != 2 * len(free):
        die("equation count")
    idx = {v: j for j, v in enumerate(free)}
    print(f"frame: v{A} at origin, v{B} on positive x-axis, v{C} above it; {len(rem)} equations in {2*len(free)} unknowns")

    M = len(rem); SC = 2 ** m_c; SY = 2 ** p_y
    # pinned coordinates scaled by SC must be exact for integer arithmetic; keep them as Fractions
    wq = []
    for ei in rem:
        u, v = E[ei]; nf = (u in idx) + (v in idx)
        if nf == 0:
            die("edge between pinned vertices outside triangle")
        wq.append((16, 8) if nf == 2 else (4, 2))

    def coords(cint):
        P = dict(pin)
        for v in free:
            P[v] = (Fr(cint[2 * idx[v]], SC), Fr(cint[2 * idx[v] + 1], SC))
        return P

    worst_k = Fr(0); worst_in = Fr(0)
    C_ = d["centers"]
    for bi, cint in enumerate(C_):
        if len(cint) != M:
            die("centre length")
        P = coords(cint)
        Fv = []; J = [[Fr(0)] * M for _ in range(M)]
        for row, ei in enumerate(rem):
            u, v = E[ei]
            dx = P[u][0] - P[v][0]; dy = P[u][1] - P[v][1]
            Fv.append(dx * dx + dy * dy - s[ei])
            for vert, sg in ((u, 1), (v, -1)):
                if vert in idx:
                    J[row][2 * idx[vert]] = 2 * sg * dx
                    J[row][2 * idx[vert] + 1] = 2 * sg * dy
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

    # pairwise disjointness (exact integers): L_inf centre distance > 2r
    Ci = np.array(C_, dtype=object)
    two_r = 2 * SC // 2 ** k_r
    if 2 * SC % 2 ** k_r:
        die("radius not on centre grid")
    A_ = np.array(C_, dtype=np.float64)
    mn = None
    for i in range(len(C_)):
        # exact check against all later centres
        for j in range(i + 1, len(C_)):
            sep = max(abs(a - b) for a, b in zip(C_[i], C_[j]))
            if sep <= two_r:
                die(f"boxes {i} and {j} overlap")
            mn = sep if mn is None else min(mn, sep)
    print(f"pairwise disjoint: min L_inf centre separation {mn / SC:.6g} > 2r = {float(2 * r):.3e}")
    print(f"RESULT: {len(C_)} distinct real realizations with v{C} above the axis; with mirror images "
          f"{2 * len(C_)} real realizations modulo direct isometries")


if __name__ == "__main__":
    main(sys.argv[1])
