"""Assemble a separated-scale model from a chain of stage files (stage_sym.py output, the last file of the chain links
back through "prev") and count the real critical points of the full model for several scale ratios r: the stage
(j+1, j) roots sit at radius ~ r^(k-j). Writes a model json usable by certify_model.py / realise_k.py.
Usage: assemble.py <last stage json> <r> [r ...]"""
import numpy as np, sys, json
import htrack as ht, hmodel as hm
files = [sys.argv[1]]
while json.load(open(files[-1])).get("prev"): files.append(json.load(open(files[-1]))["prev"])
stages = [json.load(open(f)) for f in files][::-1]           # m = k, k-1, ...
fam = stages[0]["family"]; solid = fam.split(":")[0]; d, F = hm.leading(solid); k = d - 1
TH = {s["m"]: np.array(s["thB"]) for s in stages}
print("stages:", [(s["m"], s["real"]) for s in stages], " sum of stage counts", sum(s["real"] for s in stages))
for r in [float(a) for a in sys.argv[2:]]:
    # radius of stage (j+1, j) is rho_j = r^(k-j); coefficient s_j with s_{j+1} rho_j^{j} ~ s_j rho_j^{j-1}
    s = {k: 1.0}
    for j in range(k - 1, 0, -1): s[j] = s[j + 1] * r ** (k - j)
    th = [s[j] * TH[j] if j in TH else np.zeros(2 * j + 1) for j in range(1, d)]
    P = ht.Poly(hm.model(F, d, th)); X = ht.roots(P, 3)
    if X is None: print(f"r {r}: solver failed"); continue
    Xr, idx, pok = ht.real_roots(P, X)
    print(f"r {r}: real {len(Xr)} of {len(X)}, index counts {np.bincount(idx, minlength=4).tolist()}, pairing ok {pok}; radii of real roots from {np.linalg.norm(Xr,axis=1).min():.1e} to {np.linalg.norm(Xr,axis=1).max():.1e}", flush=True)
    json.dump({"family": fam, "solid": solid, "r": r, "theta": [t.tolist() for t in th], "real": len(Xr)},
              open(f"model_{solid}_{fam.replace(':','_')}_r{r}.json", "w"))
