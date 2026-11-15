"""Harmonic quintic with many real critical points: f = h5 + c * rho^4 g(x / rho), where g = K4 + h3 + h2 + h1 is the
octahedron model with 27 real critical points and h5 is a stage (5,4) hit against K4 (top5_*.json). Counts all 64
complex critical points by homotopy continuation and certifies the real ones with the arb Krawczyk test (the
polynomial is taken exactly from its double-precision coefficients).
Usage: quintic_chain.py <top5 json> <rho> [rho ...]"""
import numpy as np, sys, json
import htrack as ht, hmodel as hm, certify as cf
T = json.load(open(sys.argv[1])); h5 = hm.harm(5, np.array(T["thA"]))
solid, d4, K4, TH = hm.load_model("sym_octahedron_crot_3_2.json")
for rho in [float(a) for a in sys.argv[2:]]:
    terms = [h5, K4] + [(hm.harm(j, TH[j - 1])[0], rho ** (4 - j) * hm.harm(j, TH[j - 1])[1]) for j in (1, 2, 3)]
    C = hm.to_array(terms, 5); P = ht.Poly(C); X = ht.roots(P, 1)
    if X is None: print("rho", rho, "solver failed"); continue
    Xr, idx, pok = ht.real_roots(P, X)
    coeffs = {tuple(int(v) for v in m): cf.arb(float(C[m])) for m in zip(*np.nonzero(C))}
    D = np.linalg.norm(Xr[:, None] - Xr[None], axis=-1) + 1e300 * np.eye(len(Xr)); sep = D.min(1)
    ok = 0; nidx = {1: 0, 2: 0}
    for x0, s in zip(Xr, sep):
        inside, signs = cf.krawczyk(coeffs, x0, min(1e-9 * (1 + np.abs(x0).max()), s / 4))
        if inside and signs[2] != 0: ok += 1; nidx[2 if signs[2] > 0 else 1] += 1
    print(f"rho {rho}: real {len(Xr)} of {len(X)} (index {np.bincount(idx, minlength=4).tolist()}), pairing ok {pok}; certified {ok} {nidx}", flush=True)
    json.dump({"C": C.tolist(), "real": len(Xr), "certified": ok, "idx": nidx}, open(f"quintic_{ok}.json", "w"))
