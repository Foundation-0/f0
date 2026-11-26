"""Directed climb for the full model f = F + h_{d-1} + ... + h_1 (all critical points via homotopy continuation).
Each iteration picks a non-real root pair close to the real axis and moves the parameters along the gradient that shrinks
its imaginary part (implicit function: dx/dtheta = -Hess^{-1} grad(phi_theta)); line search over step lengths; a step is
accepted if the real count does not fall and the target pair gets closer to the axis (or turns real). Random steps
are mixed in when the pull stalls.
Usage: full_pull.py <octahedron|icosahedron|cube|free4|free5|free6> <iterations> <seed> [start.json]"""
import numpy as np, sys, json, time
import htrack as ht, hmodel as hm
which, NIT, seed = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); rng = np.random.default_rng(seed)
if which.startswith("free"):
    d = int(which[4:]); Fterm = None; freeF = True
else:
    d, Fterm = hm.leading(which); freeF = False
degs = list(range(1, d)) + ([d] if freeF else [])
nd = {j: 2 * j + 1 for j in degs}
basis = []   # dense arrays of each basis harmonic polynomial
for j in degs:
    mons, B = hm.hbasis(j)
    for row in B: basis.append(hm.to_array([(mons, row)], d))
basis = np.array(basis); NP = len(basis)
C0 = hm.to_array([Fterm], d) if not freeF else np.zeros((d + 1,) * 3)
def poly(th): return ht.Poly(C0 + np.tensordot(th, basis, 1))
Gb = np.array([ht.Poly(b).G for b in basis])   # gradients of basis polys
def evalgrad_basis(X):
    k = np.arange(d + 1); px, py, pz = [X[:, v][:, None] ** k[None] for v in range(3)]
    return np.einsum('piabc,ka,kb,kc->kpi', Gb, px, py, pz)   # [K, NP, 3]
def solve(th):
    P = poly(th); X = ht.roots(P, int(rng.integers(1 << 30)))
    if X is None: return None
    Xr, idx, pok = ht.real_roots(P, X)
    if not pok: return None
    nreal = len(Xr); cx = np.where(np.abs(X.imag).max(1) > 1e-9 * (1 + np.abs(X).max(1)))[0]
    im = np.linalg.norm(X.imag, axis=1) / (1 + np.linalg.norm(X.real, axis=1))
    return dict(real=nreal, idx=np.bincount(idx, minlength=4).tolist(), X=X, P=P, cx=cx[np.argsort(im[cx])], im=im)
def key(s, tgt=None):
    return (s["real"], -(s["im"][s["cx"][0]] if len(s["cx"]) else 0.0))
if len(sys.argv) > 4:
    th = np.array(json.load(open(sys.argv[4]))["theta"])
else:
    th = rng.normal(size=NP) * 0.3
    if freeF: th[-nd[d]:] = rng.normal(size=nd[d])
cur = None
while cur is None:
    cur = solve(th)
    if cur is None: th = th + 0.05 * rng.normal(size=NP)
best = (cur["real"], th.copy(), cur["idx"]); t0 = time.time(); stall = 0; total = (d - 1) ** 3
for it in range(NIT):
    X, P = cur["X"], cur["P"]
    improved = False
    if len(cur["cx"]) and stall < 6:
        # target: one of the nearest pairs (randomised when stalled)
        tgt = cur["cx"][min(int(rng.integers(0, 1 + stall)), len(cur["cx"]) - 1)]
        x = X[tgt:tgt + 1]; g, H = P.gh(x)
        dB = evalgrad_basis(x)[0]            # [NP, 3]
        dx = -np.linalg.solve(H[0], dB.T).T     # [NP, 3] complex
        im = x[0].imag; grad = 2 * (im[None, :] * dx.imag).sum(1)
        if freeF: grad[-nd[d]:] *= 0.3
        gn = np.linalg.norm(grad)
        if gn > 0:
            dirn = -grad / gn; s0 = np.linalg.norm(im) ** 2 / gn   # Newton-like length to zero
            for fac in (2.0, 1.2, 0.8, 0.4, 0.15, 0.05):
                t2 = th + fac * s0 * dirn; s2 = solve(t2)
                if s2 is None: continue
                if s2["real"] > cur["real"] or (s2["real"] == cur["real"] and key(s2) > key(cur)):
                    th, cur = t2, s2; improved = True; break
    if not improved:
        sc = 0.02 * (1 + stall) * np.abs(th).mean()
        t2 = th + sc * rng.normal(size=NP); s2 = solve(t2)
        if s2 is not None and (s2["real"] > cur["real"] or (s2["real"] == cur["real"] and key(s2) >= key(cur))):
            th, cur = t2, s2; improved = True
    stall = 0 if improved else min(stall + 1, 12)
    if cur["real"] > best[0]: best = (cur["real"], th.copy(), cur["idx"])
    if it % 20 == 0:
        print(f"  it {it}: real {cur['real']}/{total} idx {cur['idx']} nearest {cur['im'][cur['cx'][0]] if len(cur['cx']) else 0:.1e} stall {stall} {time.time()-t0:.0f}s", flush=True)
        json.dump({"which": which, "theta": best[1].tolist(), "real": best[0], "idx": best[2]}, open(f"pull_{which}_{seed}.json", "w"))
print(f"{which} seed {seed}: best real {best[0]} of {total}, index counts {best[2]}")
json.dump({"which": which, "theta": best[1].tolist(), "real": best[0], "idx": best[2]}, open(f"pull_{which}_{seed}.json", "w"))
