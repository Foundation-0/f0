"""Realise a k-flat model (Platonic leading form F plus harmonic terms h_1..h_k) by actual positive charges.
Unknowns: sites (3n) and charges (n) near the Platonic solid with unit charges. Conditions: the harmonic coordinates of
the Taylor terms T_j of the potential at the origin, j = 1..k, equal lam * eps^(k+1-j) * theta_j (lam: largest
coefficient of the unnormalised F, so that T_{k+1} = lam * F_normalised). Then near the origin
V = V0 + lam eps^(k+1) [model](x/eps) + O(eps) relative, and the balance points near the origin are eps times the
model's critical points. Newton with least-norm steps; then all balance points are counted numerically.
Usage: realise_k.py <model json from sym_scan.py> <eps> [eps ...]"""
import numpy as np, sys, json
from numpy.polynomial import legendre as Lg
import hmodel as hm, sym, htrack as ht
J = json.load(open(sys.argv[1])); epss = [float(a) for a in sys.argv[2:]]
solid, d, F, TH = hm.load_model(sys.argv[1]); fam = solid + "_" + sys.argv[1].split("/")[-1].replace(".json", ""); k = d - 1
U0 = hm.SOLIDS[solid] / np.linalg.norm(hm.SOLIDS[solid][0]); N = len(U0)
mons_F, cF = __import__("polysys").solid_term(U0, d); lam = np.abs(cF).max()
rng = np.random.default_rng(3)
XS = rng.normal(size=(400, 3)); XS /= np.linalg.norm(XS, axis=1)[:, None]
fit = {}
for j in range(1, d + 1):
    mons, B = hm.hbasis(j); E = np.array(mons); M = np.prod(XS[:, None, :] ** E[None], axis=2) @ B.T
    fit[j] = np.linalg.pinv(M)
def taylor(u, upto):
    A = u[:3 * N].reshape(N, 3); q = u[3 * N:]; r = np.linalg.norm(A, axis=1); ah = A / r[:, None]
    out = []
    for j in range(1, upto + 1):
        vals = (q[None, :] / r[None, :] ** (j + 1) * Lg.legval(XS @ ah.T, [0] * j + [1])).sum(1)   # |x| = 1
        out.append(fit[j] @ vals)
    return out
def cond(u): return np.concatenate(taylor(u, k))
def jac(u, h=1e-6):
    Jm = np.empty((sum(2 * j + 1 for j in range(1, d)), 4 * N))
    for i in range(4 * N):
        e = np.zeros(4 * N); e[i] = h; Jm[:, i] = (cond(u + e) - cond(u - e)) / (2 * h)
    return Jm
u0 = np.concatenate([U0.ravel(), np.ones(N)])
J0 = jac(u0); sv = np.linalg.svd(J0, compute_uv=False)
print(f"{solid}: Jacobian of (sites, charges) -> harmonic Taylor coefficients of degrees 1..{k}: shape {J0.shape}, rank {(sv > 1e-9 * sv[0]).sum()}, smallest singular value {sv[-1]:.2e}")
def field(X, A, q):
    D = X[:, None, :] - A[None]; r2 = (D * D).sum(-1); r = np.sqrt(r2)
    g = -(q[None, :, None] * D / (r2 * r)[..., None]).sum(1)
    H = (q[None, :, None, None] * (3 * D[..., :, None] * D[..., None, :] - r2[..., None, None] * np.eye(3)) / (r2 * r2 * r)[..., None, None]).sum(1)
    return g, H
# model roots
Ctot = hm.model(F, d, TH); P = ht.Poly(Ctot); X = ht.roots(P, 5); Xr, idx, pok = ht.real_roots(P, X)
print(f"model: {len(Xr)} real critical points of {len(X)}, radius of the farthest {np.abs(Xr).max():.3f}")
results = []
for eps in epss:
    target = np.concatenate([lam * eps ** (k + 1 - j) * TH[j - 1] for j in range(1, d)])
    u = u0.copy()
    for it in range(40):
        c = cond(u) - target
        if np.linalg.norm(c) < 1e-14 * lam: break
        u = u - np.linalg.lstsq(jac(u), c, rcond=None)[0]
    err = np.linalg.norm(cond(u) - target)
    A = u[:3 * N].reshape(N, 3); q = u[3 * N:]
    # Newton from the scaled model roots and from random starts in the ball of radius 1
    X0 = np.vstack([eps * Xr, rng.normal(size=(6000, 3)) * 0.5, eps * rng.normal(size=(6000, 3)) * np.abs(Xr).max()])
    Y = X0.copy()
    with np.errstate(all="ignore"):
        for itn in range(300):
            g, H = field(Y, A, q); dY = np.linalg.solve(H, g[..., None])[..., 0]
            cap = np.maximum(0.05 * np.linalg.norm(Y, axis=1), 0.02 * eps)
            s = np.linalg.norm(dY, axis=1); dY *= np.minimum(1.0, cap / np.maximum(s, 1e-300))[:, None]
            Y = Y - dY
        g, H = field(Y, A, q); last = np.linalg.norm(np.linalg.solve(H, g[..., None])[..., 0], axis=1)
    ok = np.isfinite(Y).all(1) & (last < 1e-7 * eps) & (np.linalg.norm(Y, axis=1) < 2)
    pts = []
    for y, h in zip(Y[ok], H[ok]):
        if any(np.linalg.norm(y - z[0]) < 1e-4 * eps for z in pts): continue
        w = np.linalg.eigvalsh(h); pts.append((y, int((w < 0).sum()), float(np.abs(w).min() / np.abs(w).max())))
    near = sum(1 for z in pts if np.linalg.norm(z[0]) < 3 * eps * np.abs(Xr).max())
    m = np.bincount([z[1] for z in pts], minlength=4)
    from_model = sum(1 for i in range(len(Xr)) if ok[i] and np.linalg.norm(Y[i] - eps * Xr[i]) < 0.1 * eps * (1 + np.linalg.norm(Xr[i])))
    print(f"eps {eps}: residual {err:.1e}, charges in [{q.min():.4f}, {q.max():.4f}], site moves up to {np.abs(A - U0).max():.2e}; "
          f"balance points {len(pts)} (index counts {m.tolist()}), near the centre {near}; model seeds kept {from_model}/{len(Xr)}; smallest eigenvalue ratio {min(z[2] for z in pts):.1e}", flush=True)
    results.append(dict(eps=eps, sites=A.tolist(), charges=q.tolist(), total=len(pts), near=near, idx=m.tolist(), points=[z[0].tolist() for z in pts]))
json.dump(dict(model=sys.argv[1], results=results), open(f"realise_{solid}_{fam.replace(':','_')}.json", "w"))
