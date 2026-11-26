"""Analyse structure_n{n}.npz: limit points of the solutions as eps -> 0 along fixed rays.
Usage: python struct_an.py n
"""
import sys, json, itertools
from collections import Counter
import numpy as np
from scipy.spatial import cKDTree
from scipy.sparse.csgraph import connected_components
from scipy.sparse import coo_matrix
from unit import make, classify, emb, HERE

n = int(sys.argv[1])
L, N = make(n)
d = np.load(f"{HERE}/structure_n{n}.npz")
ks = sorted({int(k.split("_")[1][1:]) for k in d.files if k.startswith("Z_")})
EPS = [1e-2, 1e-3, 1e-4, 1e-5, 1e-6]
adj = {frozenset(e) for e in L.E}
verts = L.free + list(L.tri)          # column order of L.full
pairs = [(i, j) for i, j in itertools.combinations(range(len(verts)), 2)]
nonadj = [(i, j) for i, j in pairs if frozenset((verts[i], verts[j])) not in adj]


def coords(Z, P):
    U, W = L.full(Z, P)
    return (U + W) / 2, (U - W) / 2j          # complex x, y per vertex


def clusters(Z, tol):
    X = emb(Z)
    tr = cKDTree(X)
    pr = np.array(sorted(tr.query_pairs(tol)))
    if len(pr) == 0:
        return len(Z), Counter({1: len(Z)})
    A = coo_matrix((np.ones(len(pr)), (pr[:, 0], pr[:, 1])), shape=(len(Z), len(Z)))
    nc, lab = connected_components(A, directed=False)
    return nc, Counter(Counter(lab).values())


res = dict(n=n, N=N, rays={})
lims = {}
for k in ks:
    r = {}
    for eps in EPS:
        Z = d[f"Z_k{k}_e{eps:g}"]
        c = classify(L, Z)
        r[f"{eps:g}"] = dict(found=c["nfound"], conj_ok=c["conj_ok"], nreal=c["nreal"], minsep=c["minsep"], maxabs=c["maxabs"])
    valid = [e for e in EPS if r[f"{e:g}"]["found"] == N and r[f"{e:g}"]["conj_ok"]]
    el = min(valid); ep = min(e for e in valid if e > el)
    r["limit_eps_used"] = el
    Z6, P6 = d[f"Z_k{k}_e{el:g}"], d[f"P_k{k}_e{el:g}"]
    Z5 = d[f"Z_k{k}_e{ep:g}"]
    lims[k] = Z6
    # movement between eps=1e-5 and 1e-6 (nearest neighbour)
    mv, _ = cKDTree(emb(Z5)).query(emb(Z6))
    r["move_prev_to_limit"] = dict(median=float(np.median(mv)), max=float(mv.max()))
    for tol in (1e-4, 1e-3, 1e-2):
        nc, mult = clusters(Z6, tol)
        r[f"clusters_tol{tol:g}"] = dict(n=nc, multiplicities=dict(sorted(mult.items())))
    # coincident vertices in the limit
    x, y = coords(Z6, P6)
    nco = np.zeros(len(Z6), int)
    for i, j in nonadj:
        dd = np.sqrt(np.abs(x[:, i] - x[:, j]) ** 2 + np.abs(y[:, i] - y[:, j]) ** 2)
        nco += dd < 1e-2
    cl = classify(L, Z6)
    C = emb(L.conj_partner(Z6)); tr = cKDTree(emb(Z6)); dc, ic = tr.query(C)
    real = (ic == np.arange(len(Z6))) & (dc < 1e-7 * (1 + np.abs(Z6).max()))
    r["limit_with_coincidence"] = int((nco > 0).sum())
    r["limit_with_coincidence_real"] = int(((nco > 0) & real).sum())
    r["limit_no_coincidence_nonreal"] = int(((nco == 0) & ~real).sum())
    # lattice check for real solutions: distance of each vertex to the triangular lattice a + b*omega
    om = np.array([0.5, np.sqrt(3) / 2])
    xr, yr = x[real].real, y[real].real
    bb = yr / om[1]; aa = xr - bb * om[0]
    ra, rb = np.round(aa), np.round(bb)
    best = np.full(xr.shape, np.inf)
    for da in (-1, 0, 1):
        for db in (-1, 0, 1):
            px = (ra + da) + (rb + db) * om[0]; py = (rb + db) * om[1]
            best = np.minimum(best, np.hypot(xr - px, yr - py))
    onlat = (best < 1e-3).all(axis=1)
    r["real_limits_all_vertices_on_lattice"] = int(onlat.sum())
    r["nreal_at_1e-6"] = int(real.sum())
    res["rays"][k] = r
# direction independence: limit points common to all rays
if len(ks) > 1:
    base = lims[ks[0]]
    common = np.ones(len(base), bool)
    for k in ks[1:]:
        dd, _ = cKDTree(emb(lims[k])).query(emb(base))
        common &= dd < 1e-3
    C = emb(L.conj_partner(base)); tr = cKDTree(emb(base)); dc, ic = tr.query(C)
    real = (ic == np.arange(len(base))) & (dc < 1e-7 * (1 + np.abs(base).max()))
    res["common_limits_all_rays"] = dict(count=int(common.sum()), real=int((common & real).sum()),
                                         nonreal=int((common & ~real).sum()))
print(json.dumps(res, indent=1))
json.dump(res, open(f"{HERE}/structure_n{n}.json", "w"), indent=1)
