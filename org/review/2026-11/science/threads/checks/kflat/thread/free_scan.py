"""Real critical points of a general harmonic polynomial of degree d (leading form free): random scan then climb.
Optional symmetry: 'cNv' = invariant under the dihedral group C_Nv about the z axis (rotation by 2pi/N, mirror y -> -y).
Usage: free_scan.py <d> <samples> <climb iterations> <seed> [cNv]"""
import numpy as np, sys, json, time
import htrack as ht, hmodel as hm, sym
d, NS, NIT, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); rng = np.random.default_rng(seed)
symm = sys.argv[5] if len(sys.argv) > 5 else None
if symm:
    N = int(symm[1:-1]); G = sym.closure([sym.rotation((0, 0, 1), 2 * np.pi / N), np.diag([1., -1, 1])])
    ib = {j: sym.invariant_basis(j, G) for j in range(1, d + 1)}
else:
    ib = {j: np.eye(2 * j + 1) for j in range(1, d + 1)}
sizes = [ib[j].shape[0] for j in range(1, d + 1)]; NP = sum(sizes)
def poly(p):
    terms = []; o = 0
    for j in range(1, d + 1):
        n = sizes[j - 1]
        if n: terms.append(hm.harm(j, p[o:o + n] @ ib[j]))
        o += n
    return ht.Poly(hm.to_array(terms, d))
def score(p):
    P = poly(p); X = ht.roots(P, int(rng.integers(1 << 30)))
    if X is None: return None
    Xr, idx, pok = ht.real_roots(P, X)
    if not pok: return None
    im = np.linalg.norm(X.imag, axis=1) / (1 + np.linalg.norm(X.real, axis=1)); cx = np.sort(im[im > 1e-9])
    return (len(Xr), -float(cx[0]) if len(cx) else 0.0), np.bincount(idx, minlength=4).tolist()
def sample():
    p = [rng.normal(size=sizes[j - 1]) * (10 ** rng.uniform(-2.5, 0.5) if j < d else 1.0) for j in range(1, d + 1)]
    return np.concatenate(p)
hist = {}; best = None; fails = 0; t0 = time.time()
for s in range(NS):
    p = sample(); sc = score(p)
    if sc is None: fails += 1; continue
    hist[sc[0][0]] = hist.get(sc[0][0], 0) + 1
    if best is None or sc[0] > best[0][0]: best = (sc, p)
print(f"free degree {d} {symm or ''} (parameters {NP}): samples {NS}, failures {fails}; real counts {dict(sorted(hist.items()))}  {time.time()-t0:.0f}s", flush=True)
cur, p = best; step = 0.2
for it in range(NIT):
    q = p * (1 + step * rng.normal(size=NP)) + 0.02 * step * np.abs(p).mean() * rng.normal(size=NP)
    sc = score(q)
    if sc is not None and sc[0] >= cur[0]:
        p, cur = q, sc; step = min(step * 1.2, 0.8)
    else: step = max(step * 0.97, 1e-3)
    if it % 50 == 0: print(f"  it {it}: real {cur[0][0]} idx {cur[1]} nearest {-cur[0][1]:.1e} step {step:.1e}", flush=True)
print(f"free degree {d} {symm or ''}: best real {cur[0][0]} of {(d-1)**3}, index counts {cur[1]}")
json.dump({"d": d, "sym": symm, "p": p.tolist(), "real": cur[0][0], "idx": cur[1], "hist": hist}, open(f"free_{d}_{symm or 'none'}_{seed}.json", "w"))
