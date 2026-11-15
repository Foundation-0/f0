"""Scale the perturbation from the unit point by kappa (continuation by local moves), then push2.
Usage: python scale_push.py state.npz kappa tag seconds"""
import sys
import numpy as np
from push import local_move, analyse, p_to_P
import push2
state, kappa, tag, secs = sys.argv[1], float(sys.argv[2]), sys.argv[3], float(sys.argv[4])
d = np.load(state); Z, p = d["Z"], d["p"]
rng = np.random.default_rng(0)
k = 1.0
while k < kappa:
    k2 = min(k * 2, kappa)
    q = push2.PU + (k2 / k) * (p - push2.PU)
    Z, ok = local_move(Z, p, q, rng)
    if not ok:
        raise SystemExit("scaling move failed")
    p, k = q, k2
    print(f"[{tag}] scaled x{k}: real {2*int(analyse(Z)[2].sum())}", flush=True)
fn = f"scaled_{tag}.npz"; np.savez(fn, Z=Z, p=p, P=p_to_P(p))
push2.run(fn, tag, secs, k_target=30, beta=0.3)
