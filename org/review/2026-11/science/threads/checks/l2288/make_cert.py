"""Build a certificate JSON for certify.py from a search state (npz with p).
Rounds the parameters to rationals, re-solves the full system there (search code), refines each real
solution exactly (quasi-Newton in Fractions), and writes integer box centres.
Usage: python make_cert.py state.npz out.json [den_exp10]
"""
import sys, json
from fractions import Fraction as Fr
import numpy as np
from monodromy import make, robust_solve
from push import p_to_P, P_to_p, S0, P0

L, N = make("l2288")


def rational_params(p, den=10 ** 9):
    if den == 0:  # use the binary64 values exactly (dyadic rationals)
        return Fr(float(p[0])), Fr(float(p[1])), [Fr(float(v)) for v in p[2:]]
    xc = Fr(round(p[0] * den), den); yc = Fr(round(p[1] * den), den)
    s_rem = [Fr(round(v * den), den) for v in p[2:]]
    return xc, yc, s_rem


def main(state, out, den_exp=9):
    d = np.load(state)
    p = d["p"]
    xc, yc, s_rem = rational_params(p, 10 ** den_exp if den_exp > 0 else 0)
    pf = np.array([float(xc), float(yc)] + [float(v) for v in s_rem])
    from push import local_move
    if np.array_equal(pf, p):
        Z, good = d["Z"].copy(), True
    else:
        Z, good = local_move(d["Z"], p, pf, np.random.default_rng(1))
    good = good and len(Z) == N and L.min_sep(Z)[0] > 1e-8
    if not good:
        Z, good = robust_solve(L, S0, P0, p_to_P(pf))
    if not good:
        raise SystemExit("full solve at rational point incomplete")
    ms = L.min_sep(Z)[0]
    im = L.imag_norm(Z)
    real = im < 1e-8
    print(f"rational point: {len(Z)} solutions, min sep {ms:.2e}, real {int(real.sum())} -> {2*int(real.sum())} realizations")
    f = L.f
    X = (0.5 * (Z[real, :f] + Z[real, f:])).real
    Y = (-0.5j * (Z[real, :f] - Z[real, f:])).real
    # exact system data
    A, B, C = L.tri
    pin = {A: (Fr(0), Fr(0)), B: (Fr(1), Fr(0)), C: (xc, yc)}
    sq = [None] * len(L.E)
    for k, ei in enumerate(L.rem):
        sq[ei] = s_rem[k]
    for ei in L.tri_edges:
        u, v = L.E[ei]
        sq[ei] = (pin[u][0] - pin[v][0]) ** 2 + (pin[u][1] - pin[v][1]) ** 2
    free = L.free
    idx = {v: j for j, v in enumerate(free)}
    M = L.m

    def FJ(z):
        P = dict(pin)
        for v in free:
            P[v] = (z[2 * idx[v]], z[2 * idx[v] + 1])
        F = []; J = np.zeros((M, M))
        for row, ei in enumerate(L.rem):
            u, v = L.E[ei]
            dx = P[u][0] - P[v][0]; dy = P[u][1] - P[v][1]
            F.append(dx * dx + dy * dy - sq[ei])
            for vert, sg in ((u, 1), (v, -1)):
                if vert in idx:
                    J[row, 2 * idx[vert]] = 2 * sg * float(dx); J[row, 2 * idx[vert] + 1] = 2 * sg * float(dy)
        return F, J

    m_c = 64
    centers = []
    worst = 0.0
    for i in range(len(X)):
        z = []
        for v in free:
            z += [X[i, idx[v]], Y[i, idx[v]]]
        z = [Fr(float(t)) for t in z]
        for it in range(4):
            F, J = FJ(z)
            Yi = np.linalg.inv(J)
            dz = Yi @ np.array([float(t) for t in F])
            # exact-ish step: use Fraction product with rounded inverse for accuracy beyond float
            Yq = [[Fr(int(round(Yi[a, b] * 2 ** 52)), 2 ** 52) for b in range(M)] for a in range(M)]
            step = [sum(Yq[a][b] * F[b] for b in range(M)) for a in range(M)]
            z = [z[a] - step[a] for a in range(M)]
            z = [Fr(round(t * 2 ** 80), 2 ** 80) for t in z]
        F, J = FJ(z)
        worst = max(worst, max(abs(float(t)) for t in F))
        centers.append([int(round(t * 2 ** m_c)) for t in z])
    print(f"refined {len(centers)} centres, worst exact residual {worst:.2e}")
    cert = dict(
        num_vertices=L.n, edges=[list(e) for e in L.E], code=18120782205838348,
        triangle=list(L.tri), sq_lengths=[str(x) for x in sq],
        pinned={str(k): [str(v[0]), str(v[1])] for k, v in pin.items()},
        free_vertices=free, box_radius_exp2=36, center_scale_exp2=m_c, Y_exp2=40, centers=centers,
        note="squared edge lengths are exact rationals; edge lengths are their positive square roots; scale fixed by lambda_{3,9}=1")
    json.dump(cert, open(out, "w"))
    print("wrote", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 9)
