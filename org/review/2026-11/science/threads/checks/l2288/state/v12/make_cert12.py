"""Certificate JSON for certify12.py from a search state (npz with Z, p).  Rounds squared lengths to den_exp
decimals (0 = exact binary64 values), moves the solution set there by local tracking (search code), checks it
is complete (6180 distinct), refines each real solution exactly and writes integer centres.
Usage: python make_cert12.py state.npz out.json [den_exp]"""
import sys, json
from fractions import Fraction as Fr
import numpy as np
import push12 as P

L, N = P.L, P.N


def main(state, out, den_exp=6):
    d = np.load(state); Z, p = d["Z"], d["p"]
    if den_exp > 0:
        s_rem = [Fr(round(v * 10 ** den_exp), 10 ** den_exp) for v in p]
    else:
        s_rem = [Fr(float(v)) for v in p]
    pf = np.array([float(x) for x in s_rem])
    if not np.array_equal(pf, p):
        Z, ok = P.local_move(Z, p, pf, np.random.default_rng(1))
        if not ok:
            raise SystemExit("move to rational point failed")
    if len(Z) != N or P.L.min_sep(Z)[0] <= 1e-8:
        raise SystemExit("solution set incomplete")
    X, Y, real, im2 = P.analyse(Z)
    print(f"rational point: {len(Z)} solutions, min sep {L.min_sep(Z)[0]:.2e}, real {int(real.sum())}", flush=True)
    f = L.f; A, B = L.tri
    pin = {A: (Fr(0), Fr(0)), B: (Fr(1), Fr(0))}
    sq = [None] * len(L.E)
    for k, ei in enumerate(L.rem):
        sq[ei] = s_rem[k]
    sq[L.tri_edges[0]] = Fr(1)
    free = L.free; idx = {v: j for j, v in enumerate(free)}; M = L.m

    def FJ(z):
        Pp = dict(pin)
        for v in free:
            Pp[v] = (z[2 * idx[v]], z[2 * idx[v] + 1])
        F = []; J = np.zeros((M, M))
        for row, ei in enumerate(L.rem):
            u, v = L.E[ei]; dx = Pp[u][0] - Pp[v][0]; dy = Pp[u][1] - Pp[v][1]
            F.append(dx * dx + dy * dy - sq[ei])
            for vert, sg in ((u, 1), (v, -1)):
                if vert in idx:
                    J[row, 2 * idx[vert]] = 2 * sg * float(dx); J[row, 2 * idx[vert] + 1] = 2 * sg * float(dy)
        return F, J

    m_c = 64; centers = []; worst = 0.0
    Xr, Yr = X[real].real, Y[real].real
    for i in range(len(Xr)):
        z = []
        for v in free:
            z += [Fr(float(Xr[i, idx[v]])), Fr(float(Yr[i, idx[v]]))]
        for it in range(4):
            F, J = FJ(z)
            Yi = np.linalg.inv(J)
            Yq = [[Fr(int(round(Yi[a, b] * 2 ** 52)), 2 ** 52) for b in range(M)] for a in range(M)]
            z = [z[a] - sum(Yq[a][b] * F[b] for b in range(M)) for a in range(M)]
            z = [Fr(round(t * 2 ** 80), 2 ** 80) for t in z]
        F, _ = FJ(z); worst = max(worst, max(abs(float(t)) for t in F))
        centers.append([int(round(t * 2 ** m_c)) for t in z])
    print(f"refined {len(centers)} centres, worst exact residual {worst:.2e}", flush=True)
    import itertools
    pairs = list(itertools.combinations(range(1, L.n + 1), 2)); es = set(map(frozenset, L.E))
    code = sum(1 << (len(pairs) - 1 - i) for i, pp in enumerate(pairs) if frozenset(pp) in es)
    cert = dict(num_vertices=L.n, edges=[list(e) for e in L.E], code=code, triangle=[A, B],
                sq_lengths=[str(x) for x in sq], pinned={str(k): [str(v[0]), str(v[1])] for k, v in pin.items()},
                free_vertices=free, box_radius_exp2=36, center_scale_exp2=m_c, Y_exp2=40, centers=centers,
                note="edge-pinned frame (graph has no triangle); 'triangle' holds the pinned edge [A, B]; "
                     "squared lengths exact, lengths are their positive square roots, lambda_AB = 1")
    json.dump(cert, open(out, "w"))
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 6)
