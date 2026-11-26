"""Harmonic sextic with many real critical points (question D, free leading form):
f = A6 + h5 + r K4 + r rho h3 + r rho^2 h2 + r rho^3 h1, with h5 from top5_*.json (stage (5,4) against K4),
A6 from top6_*.json (stage (6,5) against h5) and (K4, h1..h3) the 27-real octahedron model. Real critical points are
seeded from the three scales, refined by Newton and certified by the arb Krawczyk test on the exact float polynomial.
Usage: sextic_chain.py <top6 json> <r> <rho> [<r> <rho> ...]"""
import numpy as np, sys, json
import htrack as ht, hmodel as hm, certify as cf, stage
A6 = hm.harm(6, np.array(json.load(open(sys.argv[1]))["thA"]))
h5 = hm.harm(5, np.array(json.load(open("top5_octahedron_crot_3_1.json"))["thA"]))
solid, d4, K4, TH = hm.load_model("sym_octahedron_crot_3_2.json")
a = [float(x) for x in sys.argv[2:]]
for r, rho in zip(a[::2], a[1::2]):
    terms = [A6, h5, (K4[0], r * K4[1])] + [(hm.harm(j, TH[j - 1])[0], r * rho ** (4 - j) * hm.harm(j, TH[j - 1])[1]) for j in (1, 2, 3)]
    C = hm.to_array(terms, 6); P = ht.Poly(C)
    Y1 = stage.outer_roots(A6, h5, 5)[0]; Y2 = r * stage.outer_roots(h5, K4, 4)[0]
    Y3 = rho * r * 0 + rho * ht.roots(ht.Poly(hm.model(K4, 4, TH)), 1)
    cand = np.vstack([Y1, Y2, Y3]); cand = cand[np.abs(cand.imag).max(1) < 1e-6 * np.abs(cand).max(1)].real
    for it in range(30):
        g, H = P.gh(cand.astype(complex)); cand = cand - np.linalg.solve(H.real, g.real[..., None])[..., 0]
    g, H = P.gh(cand.astype(complex)); good = np.linalg.norm(np.linalg.solve(H.real, g.real[..., None])[..., 0], axis=1) < 1e-12 * np.linalg.norm(cand, axis=1)
    Xr = cand[good]; keep = []
    for i, x in enumerate(Xr):
        if all(np.linalg.norm(x - Xr[j]) > 1e-6 * np.linalg.norm(x) for j in keep): keep.append(i)
    Xr = Xr[keep]
    coeffs = {tuple(int(v) for v in m): cf.arb(float(C[m])) for m in zip(*np.nonzero(C))}
    D = np.linalg.norm(Xr[:, None] - Xr[None], axis=-1) + 1e300 * np.eye(len(Xr)); sep = D.min(1)
    ok = 0; nidx = {1: 0, 2: 0}
    for x0, s in zip(Xr, sep):
        inside, signs = cf.krawczyk(coeffs, x0, min(1e-7 * np.abs(x0).max(), s / 4))
        if inside and signs[2] != 0: ok += 1; nidx[2 if signs[2] > 0 else 1] += 1
    print(f"r {r} rho {rho}: candidates {len(cand)}, distinct converged {len(Xr)}, CERTIFIED {ok} {nidx}", flush=True)
    json.dump({"C": C.tolist(), "certified": ok, "idx": nidx}, open(f"sextic_{ok}.json", "w"))
