"""Climb the real count of one separated scale: non-zero critical points of A + B (A harmonic of degree m+1, B of degree m).
Usage: stage_climb.py <m> <iterations> <seed> <free|icosahedron|octahedron|fixedA:file.json> [start.json]
free: A and B both vary. icosahedron/octahedron: A is the Platonic leading form. fixedA:file: A taken from a previous
stage file (its B becomes this stage's A). Score: real count, then minus the two smallest relative imaginary parts."""
import numpy as np, sys, json, time
import stage, hmodel as hm
m, NIT, seed, mode = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
rng = np.random.default_rng(seed)
nA, nB = 2 * m + 3, 2 * m + 1
if mode in ("icosahedron", "octahedron"):
    d, Aterm = hm.leading(mode); assert d == m + 1; freeA = False
elif mode.startswith("fixedA:"):
    src = json.load(open(mode[7:])); Aterm = hm.harm(m + 1, np.array(src["thB"])); freeA = False
else: freeA = True
def terms(thA, thB):
    A = hm.harm(m + 1, thA) if freeA else Aterm
    return A, hm.harm(m, thB)
def score(thA, thB):
    r = stage.count(*terms(thA, thB), m, seed=int(rng.integers(1 << 30)))
    if r is None: return None
    return (r["real"], -r["gap"]), r
if len(sys.argv) > 5:
    st = json.load(open(sys.argv[5])); thA = np.array(st["thA"]); thB = np.array(st["thB"])
else:
    thA = rng.normal(size=nA); thB = rng.normal(size=nB)
thA /= np.linalg.norm(thA); thB /= np.linalg.norm(thB)
cur = None
while cur is None:
    cur = score(thA, thB)
    if cur is None: thA = rng.normal(size=nA); thA /= np.linalg.norm(thA); thB = rng.normal(size=nB); thB /= np.linalg.norm(thB)
best = (cur, thA.copy(), thB.copy()); step = 0.15; t0 = time.time(); fails = 0
total = 3 * m * m - 3 * m + 1
for it in range(NIT):
    a = thA + (step * rng.normal(size=nA) if freeA else 0); a /= np.linalg.norm(a)
    b = thB + step * rng.normal(size=nB); b /= np.linalg.norm(b)
    sc = score(a, b)
    if sc is None: fails += 1; step = max(step * 0.95, 1e-4); continue
    if sc[0] >= cur[0]:
        thA, thB, cur = a, b, sc; step = min(step * 1.15, 0.6)
        if sc[0] > best[0][0]: best = (sc, a.copy(), b.copy())
    else: step = max(step * 0.97, 1e-4)
    if it % 100 == 0: print(f"  it {it}: real {cur[0][0]}/{total} idx {cur[1]['idx']} gap {-cur[0][1]:.1e} step {step:.1e} fails {fails} {time.time()-t0:.0f}s", flush=True)
r = best[0][1]
print(f"stage m={m} mode {mode} seed {seed}: best real {r['real']} of {total}, index counts {r['idx']}")
json.dump({"m": m, "mode": mode, "thA": best[1].tolist(), "thB": best[2].tolist(), "real": r["real"], "idx": r["idx"]},
          open(f"stage_{m}_{mode.replace(':','_').replace('/','_')}_{seed}.json", "w"))
