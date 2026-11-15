"""Reproduce the single-pair LP move from the stuck 2280 state (push2_DF1_last.npz) that reaches 2288."""
import numpy as np, sys
from scipy.optimize import linprog
from push2 import *
d = np.load("push2_DF1_last.npz"); Z = d["Z"]; p = d["p"]
X, Y, real, im2 = analyse(Z); reps = pair_reps(Z, real)
dX, dY = sensitivities(Z, p_to_P(p))
A, b, dmin = constraints(X, Y, real, dX, dY, 0.3, nclose=400)
rng = np.random.default_rng(0)
results = []
for r in reps:
    g = 2 * (X[r].imag[:, None] * dX[r].imag + Y[r].imag[:, None] * dY[r].imag).sum(axis=0)
    for K in (0, 1):
        for tr in (1e-7, 3e-7, 1e-6, 2e-6):
            res = linprog(g, A_ub=A[K:], b_ub=b[K:], bounds=[(-tr, tr)] * len(p), method="highs")
            if not res.success:
                continue
            q = p + res.x
            Zq, ok = local_move(Z, p, q, rng)
            if not ok:
                continue
            Xq, Yq, rq, im2q = analyse(Zq)
            n = int(rq.sum())
            if n == N:
                sv = np.array([np.linalg.svd(j, compute_uv=False)[-1] for j in L.FJ(Zq, p_to_P(q))[1]])
                ms = L.min_sep(Zq)[0]
                print(f"pair {r} K {K} tr {tr:.0e}: ALL {2*n} real, min sep {ms:.2e}, min sigma {sv.min():.2e}, max imag {L.imag_norm(Zq).max():.1e}")
                results.append((sv.min(), ms, Zq, q))
best = max(results, key=lambda t: (t[0], t[1]))
np.savez("state_2288.npz", Z=best[2], p=best[3], P=p_to_P(best[3]), lam=lengths(best[3]), nreal=N)
print("saved state_2288.npz with min sigma", best[0], "min sep", best[1])
