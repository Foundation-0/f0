"""Stage (6,5) with B = the top5 quintic (see stage_topfree.py; sed-derived copy). Stage (5,4) with B = K4 (octahedral quartic) fixed and A a harmonic quintic in the invariant space of a subgroup
of Oh (or all quintics with 'all'). With the octahedron chain K4 + h3 + h2 + h1 (27 real, certified) inside, a
quintic A with s real points in this stage gives a harmonic quintic polynomial with s + 27 real critical points.
Usage: stage_topfree.py <octahedron:kind:axis | all> <samples> <climb iters> <seed>"""
import numpy as np, sys, json, time
import stage, hmodel as hm, sym
fam, NS, NIT, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); rng = np.random.default_rng(seed)
m = 5; Bterm = hm.harm(5, np.array(json.load(open("top5_octahedron_crot_3_1.json"))["thA"]))
if fam == "all": IB = np.eye(13)
else:
    s, k, a = fam.split(":"); IB = sym.invariant_basis(6, sym.subgroup(s, k, a))
nb = IB.shape[0]; total = 61
print(f"stage (6,5) with B = top5 quintic, A in {fam}: {nb} dims", flush=True)
def score(c):
    c = c / np.linalg.norm(c); r = stage.count(hm.harm(6, c @ IB), Bterm, m, seed=int(rng.integers(1 << 30)))
    if r is None: return None
    return (r["real"], -r["gap"]), r["idx"]
hist = {}; best = None; fails = 0
for s_ in range(NS):
    c = rng.normal(size=nb); sc = score(c)
    if sc is None: fails += 1; continue
    hist[sc[0][0]] = hist.get(sc[0][0], 0) + 1
    if best is None or sc[0] > best[0][0]: best = (sc, c / np.linalg.norm(c))
print(f"  random {NS}, failures {fails}: {dict(sorted(hist.items()))}", flush=True)
cur, c = best; step = 0.2
for it in range(NIT):
    q = c + step * rng.normal(size=nb); q /= np.linalg.norm(q); sc = score(q)
    if sc is not None and sc[0] >= cur[0]: c, cur = q, sc; step = min(step * 1.2, 0.8)
    else: step = max(step * 0.95, 1e-3)
    if it % 25 == 0: print(f"  it {it}: real {cur[0][0]}/{total} idx {cur[1]} nearest {-cur[0][1]:.1e}", flush=True)
print(f"stage (6,5) B=top5, A in {fam}: best real {cur[0][0]} of {total}, idx {cur[1]}")
json.dump({"fam": fam, "thA": (c @ IB).tolist(), "real": cur[0][0], "idx": cur[1]}, open(f"top6_{fam.replace(':','_')}_{seed}.json", "w"))
