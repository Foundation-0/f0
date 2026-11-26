"""Stage (m+1, m) when the G-invariant harmonics of degree m form a plane: scan the half circle of directions of B
(B and -B give the same points). Writes the best as a stage file (same format as stage_sym.py).
Usage: stage_circle.py <family> <m> <points> [previous stage json]"""
import numpy as np, sys, json
import stage, hmodel as hm, sym
fam, m, NPT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
solid, kind, ax = fam.split(":"); G = sym.subgroup(solid, kind, ax)
if len(sys.argv) > 4:
    prev = json.load(open(sys.argv[4])); Aterm = hm.harm(m + 1, np.array(prev["thB"])); chain = prev.get("chain", []) + [prev["real"]]
else:
    dF, Aterm = hm.leading(solid); chain = []
IB = sym.invariant_basis(m, G); assert IB.shape[0] == 2, IB.shape
best = None; line = []
for t in np.linspace(0, np.pi, NPT, endpoint=False):
    th = (np.cos(t) * IB[0] + np.sin(t) * IB[1]); r = None
    for sd in range(3):
        r = stage.count(Aterm, hm.harm(m, th), m, seed=sd)
        if r is not None: break
    line.append(None if r is None else r["real"])
    if r is not None and (best is None or (r["real"], -r["gap"]) > (best[0], -best[1])): best = (r["real"], r["gap"], t, th, r["idx"])
print(f"{fam} stage ({m+1},{m}) circle scan: counts along the half circle: {line}")
print(f"{fam} stage ({m+1},{m}): best real {best[0]} of {3*m*m-3*m+1} at t={best[2]:.4f}, index counts {best[4]}; previous stages {chain}")
tag = sys.argv[4].split('/')[-1].replace('.json','') if len(sys.argv) > 4 else 'top'
json.dump({"family": fam, "m": m, "thB": best[3].tolist(), "real": best[0], "idx": best[4], "chain": chain,
           "prev": sys.argv[4] if len(sys.argv) > 4 else None}, open(f"stcirc_{fam.replace(':','_')}_m{m}_{tag}.json", "w"))
