"""Order-d^3 lower bound for real critical points of harmonic polynomials (question D), Morse-Bott construction.
f0 = cos x cos y cosh(sqrt2 z) is harmonic and has a lattice of vertical critical LINES {cos x = cos y = 0}
(transversally a non-degenerate saddle). Adding eps*g with g = cos(w z) cosh(w x) (harmonic) breaks each line into the
critical points of g on it, at z = k pi / w. So in a box of side 2R there are about (2R/pi)^2 (2wR/pi) critical points.
Harmonic polynomials of degree d: write f = Re sum_j a_j exp(w_j . x) with null vectors w_j (w.w = 0) and truncate each
exponential series at degree d; each (w.x)^n is harmonic, so P_d is a harmonic polynomial of degree d.
This program counts the real non-degenerate critical points of P_d inside the box by Newton from a grid of starts.
Usage: cubic_growth.py R eps omega d1 d2 ..."""
import numpy as np, sys, math
R, eps, om = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]); ds = [int(a) for a in sys.argv[4:]]
s2 = math.sqrt(2)
W = [np.array([1j, sy, sz * s2]) for sy in (1j, -1j) for sz in (1, -1)]; A = [0.25] * 4
W += [np.array([sx * om, 0, 1j * om]) for sx in (1, -1)]; A += [eps / 2] * 2
W = np.array(W); A = np.array(A, complex)
def T(s, n):     # truncated exponential series sum_{k<=n} s^k/k!, n may be inf
    if n == math.inf: return np.exp(s)
    out = np.zeros_like(s); term = np.ones_like(s)
    for k in range(n + 1):
        out = out + term; term = term * s / (k + 1)
    return out
def gh(X, d):
    S = X.astype(complex) @ W.T            # [K, J]
    g1 = T(S, d - 1) * A; g2 = T(S, d - 2) * A
    G = np.einsum('kj,ji->ki', g1, W).real
    H = np.einsum('kj,ji,jl->kil', g2, W, W).real
    return G, H
def crit(d, h=0.35):
    g1 = np.arange(-R, R + 1e-9, h); X = np.array(np.meshgrid(g1, g1, g1, indexing='ij')).reshape(3, -1).T
    X = X + 0.01 * np.random.default_rng(0).normal(size=X.shape)
    for it in range(40):
        G, H = gh(X, d)
        try: dx = np.linalg.solve(H, G[..., None])[..., 0]
        except np.linalg.LinAlgError: dx = np.linalg.lstsq(H[0], G[0], rcond=None)[0][None]
        st = np.linalg.norm(dx, axis=1); dx *= np.minimum(1, 0.3 / np.maximum(st, 1e-300))[:, None]; X = X - dx
    G, H = gh(X, d); ev = np.linalg.eigvalsh(H)
    sc = np.abs(ev).max(1)
    ok = np.isfinite(X).all(1) & (np.abs(X).max(1) < R) & (np.linalg.norm(G, axis=1) < 1e-10 * (1 + sc)) & (np.abs(ev).min(1) > 1e-7 * sc)
    pts = []; idx = []
    for x, e in zip(X[ok], ev[ok]):
        if all(np.linalg.norm(x - p) > 1e-6 for p in pts): pts.append(x); idx.append(int((e < 0).sum()))
    return np.array(pts), np.bincount(idx, minlength=4)
def persist(P0, d):
    X = P0.copy()
    for it in range(30):
        G, H = gh(X, d); X = X - np.linalg.solve(H, G[..., None])[..., 0]
    G, H = gh(X, d); ev = np.linalg.eigvalsh(H); sc = np.abs(ev).max(1)
    ok = (np.linalg.norm(X - P0, axis=1) < 0.05) & (np.linalg.norm(G, axis=1) < 1e-9 * (1 + sc)) & (np.abs(ev).min(1) > 1e-6 * sc)
    D = np.linalg.norm(X[:, None] - X[None], axis=-1) + 1e9 * np.eye(len(X))
    return int(ok.sum()), bool(D.min() > 1e-4)
P0, I = crit(math.inf, 0.25)
print(f"analytic f0+eps*g (eps {eps}, omega {om}) in box |x|<{R}: {len(P0)} critical points, index counts {I.tolist()}")
for d in ds:
    n, dist = persist(P0, d)
    print(f"  degree {d}: {n} of {len(P0)} persist as distinct non-degenerate real critical points of the harmonic polynomial (distinct {dist}); n/d^3 = {n/d**3:.4f}", flush=True)
