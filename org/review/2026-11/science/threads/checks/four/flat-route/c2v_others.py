"""Balance points of the symmetric flat configurations n = (a, a, b, b) other than the flat point itself.
The flat point here has multiplicity 10 (11 at the regular tetrahedron). If its local degree is d, the other
balance points have index-2 minus index-1 equal to 3 - d."""
import numpy as np
from flat_param import flat_config, field
rng = np.random.default_rng(0)
print("   a       b     | others: index-2, index-1 | distances from the flat point (in units of the largest site distance)")
for a in np.concatenate([np.linspace(0.03, 0.47, 23), np.linspace(0.48, 0.52, 9), np.linspace(0.53, 0.70, 18)]):
    b = np.sqrt(0.5 - a * a); A, q, _ = flat_config(np.array([a, a, b, b])); R = np.linalg.norm(A, axis=1).max()
    X = rng.normal(size=(6000, 3)); X *= (R * rng.uniform(0, 1, size=(6000, 1)) ** (1 / 3)) / np.linalg.norm(X, axis=1)[:, None]
    X[:2000] *= 10 ** rng.uniform(-3, 0, size=(2000, 1))
    with np.errstate(all='ignore'):
        for it in range(120):
            g, H = field(X, A, q)
            d = np.einsum('mab,mb->ma', np.linalg.pinv(H, rcond=1e-12), g)
            st = np.linalg.norm(d, axis=1); d *= np.minimum(1.0, 0.05 * R / np.maximum(st, 1e-300))[:, None]
            X = X - d
        g, H = field(X, A, q)
    w = np.linalg.eigvalsh(np.where(np.isfinite(H), H, 0.0))
    ok = np.isfinite(X).all(1) & (np.linalg.norm(g, axis=1) < 1e-11 * q.sum() / R**2) & (np.linalg.norm(X, axis=1) < R) & (np.abs(w).min(1) > 1e-6 * np.abs(w).max(1))
    pts = []
    for x, ww in zip(X[ok], w[ok]):
        if np.linalg.norm(x) < 2e-3 * R: continue
        if all(np.linalg.norm(x - p[0]) > 1e-7 * R for p in pts): pts.append((x, int((ww < 0).sum())))
    m2 = sum(1 for p in pts if p[1] == 2); m1 = sum(1 for p in pts if p[1] == 1)
    print("  %.4f  %.4f |  %d, %d   (so local degree of the flat point = %d) | %s" % (a, b, m2, m1, 3 - (m2 - m1), np.array2string(np.sort([np.linalg.norm(p[0]) / R for p in pts]), precision=4)))
