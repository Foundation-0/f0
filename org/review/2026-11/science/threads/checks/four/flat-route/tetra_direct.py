"""Direct search with actual charges: four positive charges close to a regular tetrahedron with equal charges.
For each random small perturbation of the positions and charges, find the balance points of the true potential
near the centre by Newton from many real starts, classify by index, and accept the count only if
index-2 minus index-1 equals 3 (the Morse relation for four charges). Reports the distribution of counts."""
import numpy as np, sys, json
rng = np.random.default_rng(int(sys.argv[1])); NT = int(sys.argv[2]); SC = (float(sys.argv[3]), float(sys.argv[4]))
A0 = np.array([(1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1)], float); Q0 = np.ones(4)
def gh(X, A, Q):
    D = X[:,None,:] - A[None,:,:]; r2 = (D*D).sum(-1); r = np.sqrt(r2)
    g = -(Q[None,:,None] * D / (r2*r)[:,:,None]).sum(1)
    H = (Q[None,:,None,None] * (3*D[:,:,:,None]*D[:,:,None,:] - r2[:,:,None,None]*np.eye(3)[None,None]) / (r2*r2*r)[:,:,None,None]).sum(1)
    return g, H
def count(A, Q, nstart=600, rad=0.9):
    X = rng.normal(size=(nstart,3)); X = X / np.linalg.norm(X,axis=1)[:,None] * rad * rng.uniform(0,1,size=(nstart,1))**(1/3)
    for it in range(80):
        g, H = gh(X, A, Q)
        try: d = np.linalg.solve(H, g[:,:,None])[:,:,0]
        except np.linalg.LinAlgError: return None
        step = np.linalg.norm(d, axis=1); d *= np.minimum(1.0, 0.3/np.maximum(step,1e-300))[:,None]
        X = X - d
    g, H = gh(X, A, Q)
    ok = (np.linalg.norm(g,axis=1) < 1e-11) & (np.linalg.norm(X,axis=1) < 1.4)
    pts = []; idx = []
    for x, h in zip(X[ok], H[ok]):
        if any(np.linalg.norm(x-p) < 1e-7 for p in pts): continue
        w = np.linalg.eigvalsh(h)
        if np.min(np.abs(w)) < 1e-9: return None
        pts.append(x); idx.append(int((w < 0).sum()))
    m1 = idx.count(1); m2 = idx.count(2)
    return (len(pts), m1, m2, pts)
hist = {}; best = None
for t in range(NT):
    e = 10 ** rng.uniform(*SC)
    A = A0 + e * rng.normal(size=(4,3)); Q = Q0 * np.exp(e * rng.normal(size=4) * rng.uniform(0.3, 3))
    c = count(A, Q)
    if c is None or c[2] - c[1] != 3: hist["rejected"] = hist.get("rejected",0)+1; continue
    hist[c[0]] = hist.get(c[0],0)+1
    if best is None or c[0] > best[0]: best = (c[0], e, A.tolist(), Q.tolist(), c[1], c[2])
print(f"seed {sys.argv[1]} scale 10^[{SC[0]},{SC[1]}]:", dict(sorted(hist.items(), key=lambda kv: str(kv[0]))), "| best", best[0], "at e =", round(best[1],5), "index split", best[4], best[5])
json.dump({"count": best[0], "e": best[1], "sites": best[2], "charges": best[3]}, open(f"direct_best_seed{sys.argv[1]}.json","w"))
