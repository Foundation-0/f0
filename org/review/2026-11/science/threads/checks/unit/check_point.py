"""Numerical sanity check of a saved all-real point (not a proof).
Re-solves at the saved s from a FRESH generic start (new monodromy run with a different seed), then reports:
count, conjugation closure, max |Im|, max residual, min smallest singular value of the Jacobian, min separation.
Usage: python check_point.py n file.npz seed"""
import sys, time
import numpy as np
from unit import make, solve_at_s, classify, HERE
from monodromy import random_seed

n, fn, seed = int(sys.argv[1]), sys.argv[2], int(sys.argv[3])
L, N = make(n)
d = np.load(fn); s = d["s"]
rng = np.random.default_rng(seed)
Z, P0 = random_seed(L, rng)
S = Z.copy(); stale = 0
while True:
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
    if len(S) == N and stale >= 8:
        break
    if len(S) > N:
        raise SystemExit("too many")
print(f"fresh generic set: {len(S)}/{N}")
Z, P1 = solve_at_s(L, S, P0, s, tol_rel=1e-7, rounds=8, seed=seed)
c = classify(L, Z)
Fv, Jz, _, _ = L.FJ(Z, P1)
sv = np.linalg.svd(Jz, compute_uv=False)
print(f"found {c['nfound']}/{N}, conj_ok {c['conj_ok']}, real {2*c['nreal']}/{2*N}, minsep {c['minsep']:.3e}, "
      f"max imag {L.imag_norm(Z).max():.2e}, max residual {np.abs(Fv).max():.2e}, min sigma_min {sv[:, -1].min():.3e}")
