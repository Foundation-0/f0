"""Random scan, then climb, inside a symmetric family (see sym.py). Counts all (d-1)^3 critical points of the model.
Usage: sym_scan.py <family e.g. icosahedron:stab:5> <samples> <climb iterations> <seed>"""
import numpy as np, sys, json, time
import htrack as ht, hmodel as hm, sym
fam, NS, NIT, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); rng = np.random.default_rng(seed)
d, F, ib, order = sym.family(fam)
sizes = [ib[j].shape[0] for j in range(1, d)]; NP = sum(sizes)
def thetas(p):
    out = []; o = 0
    for j in range(1, d):
        n = sizes[j - 1]; out.append(p[o:o + n] @ ib[j] if n else np.zeros(2 * j + 1)); o += n
    return out
def score(p):
    P = ht.Poly(hm.model(F, d, thetas(p))); X = ht.roots(P, int(rng.integers(1 << 30)))
    if X is None: return None
    Xr, idx, pok = ht.real_roots(P, X)
    if not pok: return None
    im = np.linalg.norm(X.imag, axis=1) / (1 + np.linalg.norm(X.real, axis=1)); cx = np.sort(im[im > 1e-9])
    return (len(Xr), -float(cx[0]) if len(cx) else 0.0), np.bincount(idx, minlength=4).tolist()
def sample():
    p = []
    for j in range(1, d):
        n = sizes[j - 1]; p.append(rng.normal(size=n) * 10 ** rng.uniform(-2.5, 0.5))
    return np.concatenate(p)
hist = {}; best = None; fails = 0; t0 = time.time()
for s in range(NS):
    p = sample(); sc = score(p)
    if sc is None: fails += 1; continue
    hist[sc[0][0]] = hist.get(sc[0][0], 0) + 1
    if best is None or sc[0] > best[0][0]: best = (sc, p)
print(f"{fam} (group order {order}, free parameters {NP}): random samples {NS}, failures {fails}; real counts {dict(sorted(hist.items()))}  {time.time()-t0:.0f}s", flush=True)
cur, p = best; step = 0.2
for it in range(NIT):
    q = p * (1 + step * rng.normal(size=NP)) + 0.02 * step * np.abs(p).mean() * rng.normal(size=NP)
    sc = score(q)
    if sc is not None and sc[0] >= cur[0]:
        p, cur = q, sc; step = min(step * 1.2, 0.8)
    else: step = max(step * 0.97, 1e-3)
    if it % 50 == 0: print(f"  it {it}: real {cur[0][0]} idx {cur[1]} nearest {-cur[0][1]:.1e} step {step:.1e}", flush=True)
print(f"{fam}: best real {cur[0][0]} of {(d-1)**3}, index counts {cur[1]}")
json.dump({"family": fam, "p": p.tolist(), "real": cur[0][0], "idx": cur[1], "hist": hist}, open(f"sym_{fam.replace(':','_')}_{seed}.json", "w"))
