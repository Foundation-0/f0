"""Task 4: structure of the solutions as eps -> 0 along fixed rays s = 1 + eps u.
Saves all solution sets to structure_n{n}.npz.  Usage: python structure.py n ndir
"""
import sys, time
import numpy as np
from unit import make, load_generic, unit_dirs, solve_at_s, classify, HERE

n, ndir = int(sys.argv[1]), int(sys.argv[2])
L, N = make(n)
S0, P0 = load_generic(n)
U = unit_dirs(len(L.E), 5000, 1000 + n)          # same directions as the main run
EPSS = [1e-2, 1e-3, 1e-4, 1e-5, 1e-6]
out = {}
t0 = time.time()
for k in range(ndir):
    for eps in EPSS:
        s = 1.0 + eps * U[k]
        Z, P1 = solve_at_s(L, S0, P0, s, tol_rel=1e-7, rounds=8)
        c = classify(L, Z)
        out[f"Z_k{k}_e{eps:g}"] = Z
        out[f"P_k{k}_e{eps:g}"] = P1
        print(f"n={n} k={k} eps={eps:g} found={c['nfound']}/{N} conj_ok={c['conj_ok']} real={c['nreal']} "
              f"minsep={c['minsep']:.2e} maxabs={c['maxabs']:.2e} minIm_nonreal={c['min_imag_nonreal']} ({time.time()-t0:.0f}s)",
              flush=True)
np.savez(f"{HERE}/structure_n{n}.npz", **out)
