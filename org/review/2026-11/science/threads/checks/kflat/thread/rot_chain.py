"""Fix h5 (a stage (6,5) hit for I6) and search the rotation R of the octahedron chain (K4 + h3 + h2 + h1, 27 real)
that maximises stage(h5, K4 o R^T) [of 37]. Then the icosahedron model I6 + h5 + r R.(octahedron chain) has
stage(6,5) + stage(5,4) + 27 real critical points for small separated scales (check with chain_assemble.py --rot).
Usage: rot_chain.py <stage file with thB (degree 5)> <samples> <climb iters> <seed>"""
import numpy as np, sys, json
import stage, hmodel as hm, sym
J = json.load(open(sys.argv[1])); NS, NIT, seed = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]); rng = np.random.default_rng(seed)
h5 = hm.harm(5, np.array(J["thB"] if "thB" in J else J["th5"]))
XS = rng.normal(size=(300, 3))
def rot_theta(j, theta, R):
    """harmonic coordinates of p(R^T x) where p has coordinates theta in degree j."""
    mons, B = hm.hbasis(j); E = np.array(mons); M = lambda Y: np.prod(Y[:, None, :] ** E[None], axis=2)
    vals = M(XS @ R) @ (B.T @ theta)          # p(R^T x) at x = XS  (row vector x R = R^T x)
    return np.linalg.lstsq(M(XS) @ B.T, vals, rcond=None)[0]
mons4, B4 = hm.hbasis(4); d4, K4 = hm.leading("octahedron"); E = np.zeros(len(mons4)); i4 = {m: i for i, m in enumerate(mons4)}
for m, c in zip(*K4): E[i4[m]] += c
thK4 = B4 @ E
def score(R):
    r = stage.count(h5, hm.harm(4, rot_theta(4, thK4, R)), 4, seed=int(rng.integers(1 << 30)))
    return None if r is None else ((r["real"], -r["gap"]), r["idx"])
def randrot():
    q = rng.normal(size=4); q /= np.linalg.norm(q); a, b, c, d = q
    return np.array([[a*a+b*b-c*c-d*d, 2*(b*c-a*d), 2*(b*d+a*c)], [2*(b*c+a*d), a*a-b*b+c*c-d*d, 2*(c*d-a*b)], [2*(b*d-a*c), 2*(c*d+a*b), a*a-b*b-c*c+d*d]])
hist = {}; best = None
for i in range(NS):
    R = randrot(); sc = score(R)
    if sc is None: continue
    hist[sc[0][0]] = hist.get(sc[0][0], 0) + 1
    if best is None or sc[0] > best[0][0]: best = (sc, R)
print(f"random rotations {NS}: stage (5,4) counts {dict(sorted(hist.items()))}", flush=True)
cur, R = best; step = 0.2
for it in range(NIT):
    w = step * rng.normal(size=3); K = np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])
    R2 = R @ sym.rotation(w / (np.linalg.norm(w) + 1e-300), np.linalg.norm(w)) if np.linalg.norm(w) > 0 else R
    sc = score(R2)
    if sc is not None and sc[0] >= cur[0]: R, cur = R2, sc; step = min(step * 1.2, 1.0)
    else: step = max(step * 0.95, 1e-3)
    if it % 20 == 0: print(f"  it {it}: stage (5,4) {cur[0][0]}/37 idx {cur[1]}", flush=True)
print(f"best stage (5,4) {cur[0][0]}/37 with h5 from {sys.argv[1]} (stage (6,5) {J.get('real')})")
json.dump({"th5": list(J["thB"] if "thB" in J else J["th5"]), "R": R.tolist(), "s54": cur[0][0], "s65": J.get("real")},
          open(f"rotchain_{sys.argv[1].split('/')[-1].replace('.json','')}_{seed}.json", "w"))
