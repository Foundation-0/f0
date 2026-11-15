"""Generic complex solution set for the maximal graph on n vertices by monodromy (search code).
Safeguard: saturation (no new solution in `stall` consecutive loops after reaching N) and the count must equal
c/2 from the Laman-number recursion (threads/laman/validate_paper.log).
Usage: python gen.py n
"""
import sys, time
import numpy as np
from unit import make, HERE, classify
from monodromy import random_seed

n = int(sys.argv[1])
L, N = make(n)
rng = np.random.default_rng(100 + n)
Z, P0 = random_seed(L, rng)
S = Z.copy(); stale = 0; t0 = time.time()
for loop in range(400):
    P1 = P0 + (rng.normal(size=L.nP) + 1j * rng.normal(size=L.nP)) * np.abs(P0).mean()
    P2 = P0 + (rng.normal(size=L.nP) + 1j * rng.normal(size=L.nP)) * np.abs(P0).mean()
    Z1, ok1, _ = L.track(S, P0, P1, tol_rel=1e-6); Z1 = Z1[ok1]
    Z2, ok2, _ = L.track(Z1, P1, P2, tol_rel=1e-6); Z2 = Z2[ok2]
    Z3, ok3, _ = L.track(Z2, P2, P0, tol_rel=1e-6); Z3 = Z3[ok3]
    before = len(S)
    for z in Z3:
        if np.abs(S - z).max(axis=1).min() > 1e-6:
            S = np.vstack([S, z[None]])
    stale = stale + 1 if len(S) == before else 0
    print(f"loop {loop}: total {len(S)}/{N} ({time.time()-t0:.1f}s)", flush=True)
    if len(S) > N:
        print("MORE THAN N: error"); break
    if len(S) == N and stale >= 10:
        break
S, err = L.newton(S, P0)
c = classify(L, S)
print(f"final {len(S)} (expected {N}), max residual {err.max():.2e}, minsep {c['minsep']:.3e}")
if len(S) == N:
    np.savez(f"{HERE}/g{n}_generic.npz", Z=S, P=P0)
