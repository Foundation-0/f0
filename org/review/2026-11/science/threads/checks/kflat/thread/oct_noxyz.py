"""Octahedron: the coefficient of xyz in T_3 cannot be moved to first order by moving six charges (rank 14 of 15).
Search the stage (4,3) over C3-invariant harmonic cubics with no xyz component (a circle of directions)."""
import numpy as np, json, stage, hmodel as hm, sym
G = sym.subgroup("octahedron", "crot", "3"); IB = sym.invariant_basis(3, G)
mons, B = hm.hbasis(3); xyz = np.zeros(len(mons)); xyz[mons.index((1, 1, 1))] = 1
w = B @ xyz                      # xyz in harmonic coordinates (xyz is harmonic)
c_xyz = IB @ w                   # its component in invariant coordinates
Q = np.linalg.svd(c_xyz[None])[2][1:]    # invariant directions orthogonal to xyz (2 x 3)
d, F = hm.leading("octahedron"); best = None
for t in np.linspace(0, np.pi, 361):
    c = np.cos(t) * Q[0] + np.sin(t) * Q[1]; th = c @ IB
    r = stage.count(F, hm.harm(3, th), 3)
    if r is None: continue
    if best is None or r["real"] > best[0]: best = (r["real"], t, th, r["idx"])
    if r["real"] >= 19: print("t", round(t, 4), r["real"], r["idx"], "xyz component", float(th @ w), flush=True)
print("best", best[0], best[3], "at t", best[1])
json.dump({"family": "octahedron:crot:3", "m": 3, "thB": best[2].tolist(), "real": best[0], "idx": best[3], "chain": [], "prev": None}, open("stsym_oct_noxyz.json", "w"))
