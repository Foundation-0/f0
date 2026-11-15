"""Try to find a better-conditioned all-real point: scale the 2288 perturbation by kappa, re-push (mono).
Usage: python robust_2288.py kappa tag seconds"""
import sys
import numpy as np
from push import local_move, analyse, p_to_P
import push2
kappa, tag, secs = float(sys.argv[1]), sys.argv[2], float(sys.argv[3])
d = np.load(sys.argv[4] if len(sys.argv) > 4 else "state_2288.npz"); Z, p = d["Z"], d["p"]
rng = np.random.default_rng(0); k = 1.0
while k < kappa:
    k2 = min(k * 2, kappa); q = push2.PU + (k2 / k) * (p - push2.PU)
    Z, ok = local_move(Z, p, q, rng)
    if not ok:
        raise SystemExit("scale move failed")
    p, k = q, k2
fn = f"robust_{tag}_start.npz"; np.savez(fn, Z=Z, p=p, P=p_to_P(p))
push2.run(fn, tag, secs, k_target=30, beta=0.3, mono=True)
