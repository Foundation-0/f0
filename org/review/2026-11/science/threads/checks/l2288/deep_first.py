"""Drive the deepest non-real pairs to the real axis first, ignoring the real count, then climb with push2.
Path indices are kept by local tracking, so a targeted solution keeps its index.
Usage: python deep_first.py state.npz tag n_deep phase1_seconds climb_seconds"""
import sys, time
import numpy as np
from scipy.optimize import linprog
from push import L, N, analyse, local_move, p_to_P, lengths, sensitivities, pair_reps
import push2

state, tag, nd, t1, t2 = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
d = np.load(state); Z, p = d["Z"], d["p"]
X, Y, real, im2 = analyse(Z)
reps = pair_reps(Z, real)
tg = list(reps[np.argsort(im2[reps])[::-1][:nd]])
print(f"[{tag}] start real {2*int(real.sum())}, targets im2 {im2[tg]}", flush=True)
rng = np.random.default_rng(0)
tau = 0.05; t0 = time.time()
while time.time() - t0 < t1:
    X, Y, real, im2 = analyse(Z)
    live = [r for r in tg if not real[r]]
    if not live:
        print(f"[{tag}] all targets real, count {2*int(real.sum())}", flush=True); break
    eps = np.abs(p - push2.PU).max()
    dX, dY = sensitivities(Z, p_to_P(p))
    c = sum(2 * (X[r].imag[:, None] * dX[r].imag + Y[r].imag[:, None] * dY[r].imag).sum(axis=0) / im2[r] for r in live)
    tr = tau * eps
    res = linprog(c, bounds=[(-tr, tr)] * len(p), method="highs")
    q = p + res.x
    Zq, ok = local_move(Z, p, q, rng)
    if ok:
        Xq, Yq, rq, im2q = analyse(Zq)
        newobj = sum(np.log(max(im2q[r], 1e-30)) for r in live)
        oldobj = sum(np.log(im2[r]) for r in live)
        if newobj < oldobj or any(rq[r] for r in live):
            Z, p = Zq, q; tau = min(tau * 1.5, 0.5)
            print(f"[{tag}] ({time.time()-t0:.0f}s) target im2 {np.round(im2q[live], 4)}, real {2*int(rq.sum())}, eps {np.abs(q-push2.PU).max():.1e}", flush=True)
            continue
    tau *= 0.5
    if tau < 1e-5:
        print(f"[{tag}] phase 1 stuck", flush=True); break
fn = f"deep_{tag}_mid.npz"; np.savez(fn, Z=Z, p=p, P=p_to_P(p))
push2.run(fn, tag, t2, k_target=30, beta=0.3, mono=True)
