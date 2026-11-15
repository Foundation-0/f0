"""Targeted wall trades from a stuck state: drop the separation constraints of the K closest real pairs
(letting them cross their fold), push the remaining non-real pairs with an LP, then climb with push2.
Usage: python trade.py state.npz tag climb_seconds"""
import sys, time
import numpy as np
from scipy.optimize import linprog
from push import L, N, analyse, local_move, p_to_P, lengths, sensitivities, pair_reps
import push2

state, tag, climb = sys.argv[1], sys.argv[2], float(sys.argv[3])
d = np.load(state); Z0, p0 = d["Z"], d["p"]
X, Y, real, im2 = analyse(Z0); n0 = int(real.sum())
eps = np.abs(p0 - push2.PU).max()
dX, dY = sensitivities(Z0, p_to_P(p0))
reps = pair_reps(Z0, real)
c = sum(2 * (X[r].imag[:, None] * dX[r].imag + Y[r].imag[:, None] * dY[r].imag).sum(axis=0) / im2[r] for r in reps)
A, b, dmin = push2.constraints(X, Y, real, dX, dY, 0.3, nclose=400)
print(f"[{tag}] base {2*n0}, eps {eps:.1e}, {len(reps)} pairs, closest real d2 {np.sort(b/0.3)[:6]}", flush=True)
rng = np.random.default_rng(0)
best = (n0, Z0, p0)
t0 = time.time()
for K in (1, 2, 4, 8, 16):
    for trs in (0.02, 0.1, 0.3):
        tr = trs * eps
        res = linprog(c, A_ub=A[K:], b_ub=b[K:], bounds=[(-tr, tr)] * len(p0), method="highs")
        if not res.success:
            continue
        q = p0 + res.x
        Zq, ok = local_move(Z0, p0, q, rng)
        if not ok:
            print(f"[{tag}] K={K} tr={tr:.1e}: move failed", flush=True); continue
        Xq, Yq, rq, im2q = analyse(Zq); nq = int(rq.sum())
        repq = pair_reps(Zq, rq)
        print(f"[{tag}] K={K} tr={tr:.1e}: after trade {2*nq}, pair im2 {np.sort(im2q[repq])[:4]}", flush=True)
        fn = f"trade_{tag}_tmp.npz"; np.savez(fn, Z=Zq, p=q, P=p_to_P(q))
        bb = push2.run(fn, f"{tag}.K{K}.{trs}", climb, k_target=30, beta=0.3, seed=K)
        print(f"[{tag}] K={K} tr={tr:.1e}: climbed to {2*bb[0]}", flush=True)
        if bb[0] > best[0]:
            best = bb
            np.savez(f"trade_{tag}_best.npz", Z=bb[1], p=bb[2], P=p_to_P(bb[2]), lam=lengths(bb[2]), nreal=bb[0])
            print(f"[{tag}] NEW BEST {2*bb[0]}", flush=True)
            if bb[0] == N:
                raise SystemExit
print(f"[{tag}] done best {2*best[0]} ({time.time()-t0:.0f}s)", flush=True)
