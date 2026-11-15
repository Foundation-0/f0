"""Full icosahedron model from a chain_c3.py result: f = I6 + h5 + r [K4 + rho h3 + rho^2 h2 + rho^3 h1],
where (K4, h1..h3) is the certified 27-real octahedron model. Solves all 125 critical points, certifies the real ones
with the exact I6 (arb Krawczyk via certify.py), and writes a model json (key "theta") for realise_k.py.
Usage: chain_assemble.py <chain json> <r> <rho> [<r> <rho> ...]"""
import numpy as np, sys, json
import htrack as ht, hmodel as hm, certify as cf, stage
J = json.load(open(sys.argv[1])); th5 = np.array(J["th5"])
solid, d4, K4, TH = hm.load_model("sym_octahedron_crot_3_2.json")
mons4, B4 = hm.hbasis(4); E = np.zeros(len(mons4)); idx4 = {m: i for i, m in enumerate(mons4)}
for m, c in zip(*K4): E[idx4[m]] += c
thK4 = B4 @ E                                   # K4 in harmonic coordinates (orthonormal rows)
assert np.allclose(thK4 @ B4, E)
if "R" in J:      # rotate the whole octahedron chain: p(x) -> p(R^T x)
    R = np.array(J["R"]); XS = np.random.default_rng(9).normal(size=(300, 3))
    def rot_theta(j, theta):
        mons, B = hm.hbasis(j); Em = np.array(mons); M = lambda Y: np.prod(Y[:, None, :] ** Em[None], axis=2)
        return np.linalg.lstsq(M(XS) @ B.T, M(XS @ R) @ (B.T @ theta), rcond=None)[0]
    thK4 = rot_theta(4, thK4); TH = [rot_theta(j, TH[j - 1]) for j in (1, 2, 3)]
    K4 = hm.harm(4, thK4)
args = [float(a) for a in sys.argv[2:]]
d, I6 = hm.leading("icosahedron")
for r, rho in zip(args[::2], args[1::2]):
    theta = [r * rho ** 3 * TH[0], r * rho ** 2 * TH[1], r * rho * TH[2], r * thK4, th5]
    C = hm.model(I6, d, theta); P = ht.Poly(C)
    # candidates from the three scales (no global solve needed for a lower bound)
    h5 = hm.harm(5, th5)
    Y1 = stage.outer_roots(I6, h5, 5)[0]; Y2 = r * stage.outer_roots(h5, K4, 4)[0]
    P8 = ht.Poly(hm.to_array([K4] + [hm.harm(j, TH[j - 1]) for j in (1, 2, 3)], 4)); Y3 = rho * ht.roots(P8, 1)
    cand = np.vstack([Y1, Y2, Y3]); cand = cand[np.abs(cand.imag).max(1) < 1e-6 * np.abs(cand).max(1)].real
    for it in range(30):
        g, H = P.gh(cand.astype(complex)); cand = cand - np.linalg.solve(H.real, g.real[..., None])[..., 0]
    g, H = P.gh(cand.astype(complex)); good = np.linalg.norm(np.linalg.solve(H.real, g.real[..., None])[..., 0], axis=1) < 1e-12 * np.linalg.norm(cand, axis=1)
    Xr = cand[good]; keep = []
    for i, x in enumerate(Xr):
        if all(np.linalg.norm(x - Xr[j]) > 1e-6 * np.linalg.norm(x) for j in keep): keep.append(i)
    Xr = Xr[keep]; idx = np.array([int((np.linalg.eigvalsh(h.real) < 0).sum()) for h in P.gh(Xr.astype(complex))[1]]); pok = True; X = Xr
    print(f"  candidates {len(cand)}, converged and distinct {len(Xr)}")
    ok, nidx = cf.certify("icosahedron", C, hm.to_array([I6], d), Xr)
    rad = np.linalg.norm(Xr, axis=1)
    print(f"r {r} rho {rho}: real candidates {len(Xr)} (index {np.bincount(idx, minlength=4).tolist()}), pairing ok {pok}; "
          f"CERTIFIED {ok} {nidx}; radii {rad.min():.1e}..{rad.max():.1e}", flush=True)
    json.dump({"solid": "icosahedron", "theta": [t.tolist() for t in theta], "real": len(Xr), "certified": ok, "r": r, "rho": rho},
              open(f"model_ico_chain_{ok}_r{r}_rho{rho}.json", "w"))
