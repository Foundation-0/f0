"""Icosahedron chain through the octahedron: f = I6 + h5 + [K4 + h3 + h2 + h1] at three separated scales.
The inner bracket is the certified 27-real octahedron model (C3-invariant about (1,1,1), as is I6 restricted to that
axis). h5 runs over the C3-invariant harmonic quintics (3 dims). Score = stage(I6, h5) [of 61] + stage(h5, K4) [of 37];
the full model then has score + 27 real critical points when the scales are separated enough.
Usage: chain_c3.py <samples> <climb iters> <seed> [group family, default icosahedron:crot:3]"""
import numpy as np, sys, json, time
import stage, hmodel as hm, sym
NS, NIT, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); rng = np.random.default_rng(seed)
fam = sys.argv[4] if len(sys.argv) > 4 else "icosahedron:crot:3"
s, k, a = fam.split(":"); IB = sym.invariant_basis(5, sym.subgroup(s, k, a))
# keep only directions also invariant under the octahedral C3 about (1,1,1) (same axis, same rotation): automatic for crot:3
d6, I6 = hm.leading("icosahedron"); d4, K4 = hm.leading("octahedron")
nb = IB.shape[0]
def score(c):
    c = c / np.linalg.norm(c); h5 = hm.harm(5, c @ IB)
    r1 = stage.count(I6, h5, 5, seed=int(rng.integers(1 << 30)))
    if r1 is None: return None
    r2 = stage.count(h5, K4, 4, seed=int(rng.integers(1 << 30)))
    if r2 is None: return None
    return (r1["real"] + r2["real"], -(r1["gap"] + r2["gap"])), (r1["real"], r2["real"], r1["idx"], r2["idx"])
hist = {}; best = None; t0 = time.time()
for i in range(NS):
    c = rng.normal(size=nb); sc = score(c)
    if sc is None: continue
    hist[sc[1][:2]] = hist.get(sc[1][:2], 0) + 1
    if best is None or sc[0] > best[0][0]: best = (sc, c / np.linalg.norm(c))
print(f"{fam}: random {NS}: (stage 65, stage 54) counts {dict(sorted(hist.items()))} {time.time()-t0:.0f}s", flush=True)
cur, c = best; step = 0.2
for it in range(NIT):
    q = c + step * rng.normal(size=nb); q /= np.linalg.norm(q); sc = score(q)
    if sc is not None and sc[0] >= cur[0]: c, cur = q, sc; step = min(step * 1.2, 0.8)
    else: step = max(step * 0.95, 1e-3)
    if it % 20 == 0: print(f"  it {it}: stages {cur[1][:2]} sum {cur[0][0]} -> model {cur[0][0] + 27}", flush=True)
print(f"best: stage (6,5) {cur[1][0]}/61 idx {cur[1][2]}, stage (5,4) {cur[1][1]}/37 idx {cur[1][3]}; with the 27 inner: {cur[0][0] + 27} of 125")
json.dump({"family": fam, "c": c.tolist(), "th5": (c @ IB).tolist(), "s65": cur[1][0], "s54": cur[1][1]}, open(f"chain_{fam.replace(':','_')}_{seed}.json", "w"))
