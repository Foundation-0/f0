"""Two-scale design for the octahedron centre. With a harmonic cubic H3 added to the leading quartic F, the critical
points of F + H3 are the origin (8-fold) and 19 others at the scale of H3. This program counts how many of the 19 are
real, over random H3 and then by climbing. A tiny quadratic and linear term is added only to split the 8-fold origin
so that the solver sees 27 simple roots; roots within a small radius of the origin are not counted here.
Usage: outer_scan.py <octahedron|cube> <samples> <climb iterations> <seed>"""
import numpy as np, sys, json, itertools
import polysys as ps
which, NS, NIT, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); rng = np.random.default_rng(seed)
U = {"octahedron": np.array([(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)], float),
     "cube": np.array(list(itertools.product((-1, 1), repeat=3)), float)}[which]
U = U / np.linalg.norm(U[0]); S = ps.System(3); monsF, cF = ps.solid_term(U, 4); cF = cF / np.abs(cF).max()
m3, B3 = ps.harmonic_basis(3); m2, B2 = ps.harmonic_basis(2); m1, B1 = ps.harmonic_basis(1)
q2 = rng.normal(size=5) @ B2; l1 = rng.normal(size=3)
def outer(c3):
    c3 = c3 / np.linalg.norm(c3)
    co = ps.grad_coeffs(S, [(monsF, cF), (m3, c3 @ B3), (m2, 1e-4 * q2), (m1, 1e-8 * l1)])
    X = S.solve(co, rng)
    if X is None or not np.isfinite(X).all(): return None
    r = np.abs(X).max(1); out = X[r > 0.02]
    if len(out) != 19: return None
    im = np.abs(out.imag).max(1) / np.abs(out).max(1); real = im < 1e-7
    J = S.jac(co, out[real]).real
    return int(real.sum()), -float(np.sort(im[~real])[:2].sum()) if (~real).any() else 0.0, int((np.linalg.det(J) > 0).sum())
hist = {}; best = None
for s in range(NS):
    c3 = rng.normal(size=7); sc = outer(c3)
    if sc is None: continue
    hist[sc[0]] = hist.get(sc[0], 0) + 1
    if best is None or sc[:2] > best[0][:2]: best = (sc, c3 / np.linalg.norm(c3))
print(f"{which}: real among the 19 outer critical points, random cubic terms (count: samples): {dict(sorted(hist.items()))}")
cur, c3 = best; step = 0.2
for it in range(NIT):
    t = c3 + step * rng.normal(size=7); sc = outer(t)
    if sc is not None and sc[:2] >= cur[:2]:
        c3, cur = t / np.linalg.norm(t), sc; step = min(step * 1.1, 0.5)
    else: step = max(step * 0.97, 1e-5)
print(f"after climbing: {cur[0]} of 19 real, {cur[2]} with positive determinant; nearest complex pair {-cur[1]:.2e}")
json.dump({"c3": c3.tolist(), "outer_real": cur[0], "npos": cur[2]}, open(f"outer_{which}_{seed}.json", "w"))
