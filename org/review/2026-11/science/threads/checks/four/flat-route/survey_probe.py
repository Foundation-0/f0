import numpy as np, sys
from flat_param import flat_config, field
rng = np.random.default_rng(int(sys.argv[1]))
for s in range(int(sys.argv[2])):
    n = np.abs(rng.normal(size=4)); n /= np.linalg.norm(n)
    if n.min() < 0.03: continue
    A, q, _ = flat_config(n); R = np.linalg.norm(A, axis=1).max()
    X = rng.normal(size=(3000, 3)); X *= (R * rng.uniform(0, 1, size=(3000, 1)) ** (1 / 3)) / np.linalg.norm(X, axis=1)[:, None]
    X[:1500] *= 10 ** rng.uniform(-2.5, 0, size=(1500, 1))
    with np.errstate(all='ignore'):
        for it in range(150):
            g, H = field(X, A, q)
            d = np.einsum('mab,mb->ma', np.linalg.pinv(H, rcond=1e-12), g)
            st = np.linalg.norm(d, axis=1); d *= np.minimum(1.0, 0.03 * R / np.maximum(st, 1e-300))[:, None]; X = X - d
        g, H = field(X, A, q)
    w = np.linalg.eigvalsh(np.where(np.isfinite(H), H, 0.0))
    ok = np.isfinite(X).all(1) & (np.linalg.norm(g, axis=1) < 1e-11 * q.sum() / R**2) & (np.linalg.norm(X, axis=1) < R)
    pts = []
    for x, ww in zip(X[ok], w[ok]):
        if all(np.linalg.norm(x - p[0]) > 1e-6 * R for p in pts): pts.append((x, int((ww < 0).sum()), np.abs(ww).min() / np.abs(ww).max()))
    far = [p for p in pts if np.linalg.norm(p[0]) > 2e-3 * R]
    print("n", np.round(np.sort(n), 3), "| far points (radius/R, index, eigen ratio):", [(round(float(np.linalg.norm(p[0]) / R), 4), p[1], float("%.1e" % p[2])) for p in sorted(far, key=lambda p: np.linalg.norm(p[0]))], flush=True)
