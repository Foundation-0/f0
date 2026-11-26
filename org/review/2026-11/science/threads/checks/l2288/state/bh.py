"""Basin hopping on top of push2: random kick of the perturbation direction, short climb, keep if better.
Usage: python bh.py start.npz tag total_seconds climb_seconds kick seed"""
import sys, time
import numpy as np
from push import L, N, analyse, local_move, full_solve, p_to_P, lengths
import push2

start, tag, total, climb, kick, seed = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6])
rng = np.random.default_rng(seed)
d = np.load(start)
Zb, pb = d["Z"], d["p"]
nb = int(analyse(Zb)[2].sum())
print(f"[{tag}] base {2*nb}", flush=True)
t0 = time.time(); hop = 0
while time.time() - t0 < total:
    hop += 1
    eps = np.abs(pb - push2.PU).max()
    q = pb + kick * eps * rng.uniform(-1, 1, len(pb))
    Zq, ok = local_move(Zb, pb, q, rng)
    if not ok:
        Zq, okf = full_solve(q, rng)
        if not okf.all():
            print(f"[{tag}] hop {hop}: kick solve failed", flush=True); continue
    nq = int(analyse(Zq)[2].sum())
    fn = f"bh_{tag}_tmp.npz"; np.savez(fn, Z=Zq, p=q, P=p_to_P(q))
    best = push2.run(fn, f"{tag}.h{hop}", climb, k_target=30, beta=0.3, seed=hop)
    print(f"[{tag}] hop {hop} ({time.time()-t0:.0f}s): kicked {2*nq} -> climbed {2*best[0]} (base {2*nb})", flush=True)
    if best[0] > nb:
        nb, Zb, pb = best[0], best[1], best[2]
        np.savez(f"bh_{tag}_best.npz", Z=Zb, p=pb, P=p_to_P(pb), lam=lengths(pb), nreal=nb)
        print(f"[{tag}] NEW BEST {2*nb}", flush=True)
print(f"[{tag}] done best {2*nb}", flush=True)
