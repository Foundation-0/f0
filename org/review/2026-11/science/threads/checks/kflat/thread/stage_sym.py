"""Separated scales with symmetry. Stage (m+1, m): A is fixed (the Platonic leading form, or the B of a previous stage),
B runs over the directions of the G-invariant harmonics of degree m. Counts the real non-zero critical points of A + B
(of 3m^2-3m+1). Random directions, then a climb.
Usage: stage_sym.py <group family e.g. icosahedron:crot:3> <m> <samples> <climb iters> <seed> [previous stage json]"""
import numpy as np, sys, json, time
import stage, hmodel as hm, sym
fam, m, NS, NIT, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
rng = np.random.default_rng(seed)
solid, kind, ax = fam.split(":"); G = sym.subgroup(solid, kind, ax)
if len(sys.argv) > 6:
    prev = json.load(open(sys.argv[6])); Aterm = hm.harm(m + 1, np.array(prev["thB"])); chain = prev.get("chain", []) + [prev["real"]]
else:
    dF, Aterm = hm.leading(solid); assert dF == m + 1; chain = []
IB = sym.invariant_basis(m, G); nb = IB.shape[0]; total = 3 * m * m - 3 * m + 1
print(f"{fam} stage ({m+1},{m}): invariant harmonics of degree {m}: {nb}; non-zero critical points {total}", flush=True)
def score(c):
    c = c / np.linalg.norm(c); r = stage.count(Aterm, hm.harm(m, c @ IB), m, seed=int(rng.integers(1 << 30)))
    if r is None: return None
    return (r["real"], -r["gap"]), r["idx"]
hist = {}; best = None; fails = 0; t0 = time.time()
for s in range(NS):
    c = rng.normal(size=nb); sc = score(c)
    if sc is None: fails += 1; continue
    hist[sc[0][0]] = hist.get(sc[0][0], 0) + 1
    if best is None or sc[0] > best[0][0]: best = (sc, c / np.linalg.norm(c))
print(f"  random directions {NS}, failures {fails}: real counts {dict(sorted(hist.items()))}  {time.time()-t0:.0f}s", flush=True)
cur, c = best; step = 0.2
for it in range(NIT):
    q = c + step * rng.normal(size=nb); q /= np.linalg.norm(q); sc = score(q)
    if sc is not None and sc[0] >= cur[0]:
        c, cur = q, sc; step = min(step * 1.2, 0.8)
    else: step = max(step * 0.95, 1e-4)
    if it % 25 == 0: print(f"  it {it}: real {cur[0][0]}/{total} idx {cur[1]} nearest {-cur[0][1]:.1e} step {step:.1e}", flush=True)
print(f"{fam} stage ({m+1},{m}): best real {cur[0][0]} of {total}, index counts {cur[1]}; previous stages {chain}")
out = {"family": fam, "m": m, "thB": (c @ IB).tolist(), "cB": c.tolist(), "real": cur[0][0], "idx": cur[1], "chain": chain,
       "prev": sys.argv[6] if len(sys.argv) > 6 else None}
json.dump(out, open(f"stsym_{fam.replace(':','_')}_m{m}_{seed}.json", "w"))
