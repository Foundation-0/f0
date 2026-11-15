"""Probe: how many of the 11 balance points at the tetrahedron's centre can be real?

Model: f = c3 xyz + c4 K4 + (linear) + (traceless quadratic) + (harmonic cubic other than xyz), the last three
small and random. f stays harmonic. For each perturbation, find the complex critical points near the origin by
Newton from many complex starts in a ball (exactly 11 are expected there), and count the real ones.
This is the polynomial model, not actual charges: it says what harmonic unfoldings allow, not what four charges
can realise."""
import numpy as np, sys
c3, c4 = 1.283001, -0.099789
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
# harmonic cubic basis (7): xyz, x^3-3xy^2, y^3-3yx^2, x^3-3xz^2, z^3-3zx^2, y^3-3yz^2, z^3-3zy^2  (the last 6 span, with xyz, all harmonic cubics up to one relation; fine for a probe)
def grad_hess(P, V):
    # P: parameters dict; V: (m,3) complex points -> gradient (m,3) and Hessian (m,3,3)
    x, y, z = V[:,0], V[:,1], V[:,2]
    l = P["l"]; Q = P["Q"]; a = P["a"]
    g = np.empty_like(V); H = np.empty((V.shape[0],3,3), dtype=complex)
    # c3 xyz
    g[:,0] = c3*y*z; g[:,1] = c3*x*z; g[:,2] = c3*x*y
    H[:] = 0
    H[:,0,1] = H[:,1,0] = c3*z; H[:,0,2] = H[:,2,0] = c3*y; H[:,1,2] = H[:,2,1] = c3*x
    # c4 K4
    g[:,0] += c4*(4*x**3 - 6*x*(y*y+z*z)); g[:,1] += c4*(4*y**3 - 6*y*(x*x+z*z)); g[:,2] += c4*(4*z**3 - 6*z*(x*x+y*y))
    H[:,0,0] += c4*(12*x*x - 6*(y*y+z*z)); H[:,1,1] += c4*(12*y*y - 6*(x*x+z*z)); H[:,2,2] += c4*(12*z*z - 6*(x*x+y*y))
    H[:,0,1] += -12*c4*x*y; H[:,1,0] += -12*c4*x*y; H[:,0,2] += -12*c4*x*z; H[:,2,0] += -12*c4*x*z; H[:,1,2] += -12*c4*y*z; H[:,2,1] += -12*c4*y*z
    # linear and quadratic
    g += l[None,:] + V @ Q.T
    H += Q[None,:,:]
    # cubic harmonic perturbations a[0..5]: u^3 - 3 u v^2 for (u,v) in pairs
    pairs = [(0,1),(1,0),(0,2),(2,0),(1,2),(2,1)]
    for k,(u,v) in enumerate(pairs):
        U, W = V[:,u], V[:,v]
        g[:,u] += a[k]*(3*U*U - 3*W*W); g[:,v] += a[k]*(-6*U*W)
        H[:,u,u] += a[k]*6*U; H[:,v,v] += a[k]*(-6*U); H[:,u,v] += a[k]*(-6*W); H[:,v,u] += a[k]*(-6*W)
    return g, H
def solve_near(P, rad, nstart=1500, iters=60):
    V = (rng.normal(size=(nstart,3)) + 1j*rng.normal(size=(nstart,3))) * rad * rng.uniform(0.02, 1.0, size=(nstart,1))
    for it in range(iters):
        g, H = grad_hess(P, V)
        try: d = np.linalg.solve(H, g[:,:,None])[:,:,0]
        except np.linalg.LinAlgError: d = np.einsum('mij,mj->mi', np.linalg.pinv(H), g)
        V = V - d
    g, H = grad_hess(P, V)
    ok = (np.linalg.norm(g, axis=1) < 1e-10*(1+np.linalg.norm(V,axis=1))) & (np.linalg.norm(V, axis=1) < rad)
    roots = []
    for v in V[ok]:
        if not any(np.linalg.norm(v - r) < 1e-7*rad for r in roots): roots.append(v)
    return roots
hist = {}; best = None
for trial in range(int(sys.argv[2]) if len(sys.argv) > 2 else 300):
    e = 10 ** rng.uniform(-3, -0.5)                      # overall size of the neighbourhood
    Qm = rng.normal(size=(3,3)); Qm = (Qm + Qm.T)/2; Qm -= np.eye(3)*np.trace(Qm)/3
    P = {"l": rng.normal(size=3) * e**3 * 10**rng.uniform(-1.5, 0.5), "Q": Qm * e * 10**rng.uniform(-1.5, 0.5), "a": rng.normal(size=6) * 10**rng.uniform(-2.5, -0.3)}
    roots = solve_near(P, rad=1.2)
    if len(roots) != 11: hist["not 11 found"] = hist.get("not 11 found", 0) + 1; continue
    nreal = sum(1 for r in roots if np.linalg.norm(r.imag) < 1e-8)
    hist[nreal] = hist.get(nreal, 0) + 1
    if best is None or nreal > best[0]: best = (nreal, {k: (v.tolist()) for k, v in P.items()}, [r.real.tolist() for r in roots if np.linalg.norm(r.imag) < 1e-8])
print("real balance points near the centre, over random harmonic perturbations:", dict(sorted(hist.items(), key=lambda kv: str(kv[0]))))
print("best:", best[0] if best else None)
if best and best[0] >= 9:
    import json; json.dump({"nreal": best[0], "params": best[1], "real_points": best[2]}, open(f"probe_best_{best[0]}.json", "w"))
