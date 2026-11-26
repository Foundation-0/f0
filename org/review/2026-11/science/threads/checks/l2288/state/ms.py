"""Multi-start: random near-unit perturbation direction, full solve, then push2 for a fixed time.
Usage: python ms.py seed n_starts seconds_each eps mode(pos|sym)"""
import sys, time, json
import numpy as np
from push import L, N, full_solve, analyse, p_to_P, lengths
import push2

seed, n, secs, eps, mode = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
rng = np.random.default_rng(seed)
out = []
for k in range(n):
    delta = rng.uniform(0, 1, 18) if mode == "pos" else rng.uniform(-1, 1, 18)
    p = push2.PU + eps * delta
    Z, ok = full_solve(p)
    if not ok.all():
        print(f"[ms{seed}.{k}] start solve incomplete, skip", flush=True); continue
    nr0 = int(analyse(Z)[2].sum())
    fn = f"ms_{seed}_{k}_start.npz"; np.savez(fn, Z=Z, p=p, P=p_to_P(p))
    best = push2.run(fn, f"ms{seed}.{k}", secs, k_target=30, beta=0.3, seed=k)
    out.append(dict(k=k, start=2 * nr0, best=2 * best[0], delta=delta.tolist()))
    json.dump(out, open(f"ms_{seed}_summary.json", "w"))
    print(f"[ms{seed}.{k}] start {2*nr0} -> best {2*best[0]}", flush=True)
