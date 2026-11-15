"""How many of the k^3 balance points of an unfolded k-flat centre can be real?
The centre of equal charges on an octahedron (k = 3) or icosahedron (k = 5) has potential F + higher terms with F a
harmonic form of degree k + 1. Moving the charges adds harmonic terms of every lower degree. This program adds random
harmonic terms of degrees 1..k to F and counts the real critical points (out of k^3) of the resulting polynomial.
Usage: kflat_scan.py <octahedron|icosahedron|cube> <samples> <seed>"""
import numpy as np, sys, json, itertools
import polysys as ps
which, NS, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); rng = np.random.default_rng(seed)
phi = (1 + 5 ** 0.5) / 2
U = {"octahedron": np.array([(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)], float),
     "cube": np.array(list(itertools.product((-1, 1), repeat=3)), float),
     "icosahedron": np.array([p for s1 in (-1,1) for s2 in (-1,1) for p in ((0, s1, s2*phi), (s1, s2*phi, 0), (s2*phi, 0, s1))], float)}[which]
U = U / np.linalg.norm(U[0]); d = 4 if which != "icosahedron" else 6; k = d - 1
S = ps.System(k); monsF, cF = ps.solid_term(U, d); cF = cF / np.abs(cF).max()
bases = {j: ps.harmonic_basis(j) for j in range(1, d)}
hist = {}; best = (0, None); fail = 0
for s in range(NS):
    terms = [(monsF, cF)]; eps = []
    for j in range(1, d):
        mons, B = bases[j]; c = rng.normal(size=B.shape[0]); c /= np.linalg.norm(c)
        e = 10 ** rng.uniform(-2, 0.5); eps.append(e); terms.append((mons, (c @ B) * e))
    co = ps.grad_coeffs(S, terms); X = S.solve(co, rng); nreal, npos = S.count_real(co, X)
    if nreal < 0: fail += 1; continue
    hist[nreal] = hist.get(nreal, 0) + 1
    if nreal > best[0]: best = (nreal, dict(eps=eps, co=co.tolist(), npos=npos))
print(f"{which}: leading form of degree {d}, at most {k ** 3} critical points; samples {NS}, solver failures {fail}")
print("real critical points (count: samples):", dict(sorted(hist.items())))
print("best:", best[0], "with", best[1]["npos"] if best[1] else None, "of positive determinant")
json.dump(best[1] | {"real": best[0]}, open(f"kflat_scan_{which}_{seed}.json", "w"))
