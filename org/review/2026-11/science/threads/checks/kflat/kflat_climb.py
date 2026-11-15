"""Directed search for unfoldings of a k-flat centre with as many real balance points as possible.
State: coefficients of harmonic terms of degrees 1..k added to the leading form F. Score: number of real critical
points, then (as a tie-break) minus the sum of the imaginary parts of the non-real ones, so that a complex pair
is pulled toward the real axis. Random steps, accept if the score does not fall.
Usage: kflat_climb.py <octahedron|cube> <iterations> <seed> [start.json]"""
import numpy as np, sys, json, itertools
import polysys as ps
which, NIT, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); rng = np.random.default_rng(seed)
phi = (1 + 5 ** 0.5) / 2
U = {"octahedron": np.array([(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)], float),
     "cube": np.array(list(itertools.product((-1, 1), repeat=3)), float)}[which]
U = U / np.linalg.norm(U[0]); d = 4; k = 3
S = ps.System(k); monsF, cF = ps.solid_term(U, d); cF = cF / np.abs(cF).max()
bases = {j: ps.harmonic_basis(j) for j in range(1, d)}; dims = [bases[j][1].shape[0] for j in range(1, d)]
def score(theta):
    terms = [(monsF, cF)]; o = 0
    for j in range(1, d):
        mons, B = bases[j]; terms.append((mons, theta[o:o + dims[j - 1]] @ B)); o += dims[j - 1]
    co = ps.grad_coeffs(S, terms); X = S.solve(co, rng); nreal, npos = S.count_real(co, X)
    if nreal < 0: return None
    scale = np.abs(X).max(); im = np.abs(X.imag).max(1); cx = im[im > 1e-8 * scale]
    return nreal, -float(np.sort(cx)[:2].sum() / scale) if len(cx) else 0.0, npos
if len(sys.argv) > 4: theta = np.array(json.load(open(sys.argv[4]))["theta"])
else:
    theta = np.concatenate([rng.normal(size=dims[j - 1]) * 10 ** rng.uniform(-2, 0) for j in range(1, d)])
cur = None
while cur is None: cur = score(theta); theta = theta if cur else np.concatenate([rng.normal(size=n) * 0.3 for n in dims])
best = (cur, theta.copy()); step = 0.1
for it in range(NIT):
    t2 = theta * (1 + step * rng.normal(size=theta.shape)) + step * 0.01 * np.abs(theta).mean() * rng.normal(size=theta.shape)
    sc = score(t2)
    if sc is not None and (sc[0], sc[1]) >= (cur[0], cur[1]):
        theta, cur = t2, sc; step = min(step * 1.1, 0.5)
        if (cur[0], cur[1]) > (best[0][0], best[0][1]): best = (cur, theta.copy())
    else: step = max(step * 0.98, 1e-4)
    if it % 2000 == 0: print(f"  iteration {it}: real {cur[0]} (positive determinant {cur[2]}), nearest complex pair {-cur[1]:.2e}, step {step:.1e}", flush=True)
print(f"{which} seed {seed}: best real count {best[0][0]} of {k ** 3}, positive determinant {best[0][2]}")
json.dump({"theta": best[1].tolist(), "real": best[0][0], "npos": best[0][2]}, open(f"climb_{which}_{seed}.json", "w"))
