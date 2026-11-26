"""
Numerical census of planar central configurations of n equal unit masses.

Equations (masses 1, lambda = 1):   F_i(q) = sum_{j != i} (q_i - q_j)/r_ij^3 - q_i = 0,  i = 1..n.
Summing over i gives sum_i q_i = 0, so the centre of mass is forced to 0; lambda = 1 fixes the scale.
The only remaining continuous symmetry is rotation, so solutions come in circles; we use a batched
Levenberg-Marquardt iteration on the full 2n x 2n system (it tolerates the 1-dim rotation kernel).

Classes are identified up to rotation, reflection and relabelling by the invariant
(I, sorted list of the n(n-1)/2 mutual distances), where I = sum |q_i|^2 (= U, since lambda = 1).

Usage: python census.py n seconds seed out.json
Floating point only.  This finds candidates; nothing here is a proof.
"""
import sys, time, json, os
import numpy as np

MODE = os.environ.get("MODE", "lm")        # "lm" (Levenberg-Marquardt) or "newton" (pseudo-inverse Newton, step halving)
STARTS = os.environ.get("STARTS", "mix")
TIGHT = os.environ.get("TIGHT", "0") == "1"    # polish every solution with 4 Newton steps, then merge only to 1e-10 in I, 1e-8 in distances
TOL_I, TOL_D = (1e-10, 1e-8) if TIGHT else (1e-7, 1e-6)   # "mix" (disc/square/gauss) or "cluster" (bodies grouped near 2-4 random centres)

n = int(sys.argv[1]); TLIM = float(sys.argv[2]); seed = int(sys.argv[3]); OUT = sys.argv[4]
rng = np.random.default_rng(seed)
iu = np.triu_indices(n, 1)


def FJ(X):
    """X: (B, n, 2).  Returns F (B, 2n) and J (B, 2n, 2n)."""
    B = X.shape[0]
    D = X[:, :, None, :] - X[:, None, :, :]            # q_i - q_j
    r2 = (D ** 2).sum(-1)
    r2[:, np.arange(n), np.arange(n)] = 1.0
    r3i = r2 ** -1.5; r5i = r2 ** -2.5
    r3i[:, np.arange(n), np.arange(n)] = 0.0; r5i[:, np.arange(n), np.arange(n)] = 0.0
    F = (D * r3i[..., None]).sum(2) - X                  # (B, n, 2)
    # block (i,j), j != i: d F_i / d q_j = -(r^-3 I - 3 r^-5 D D^T)
    eye = np.eye(2)
    blk = r3i[..., None, None] * eye - 3 * r5i[..., None, None] * D[..., :, None] * D[..., None, :]
    Jb = -blk                                            # (B, n, n, 2, 2) off-diagonal blocks
    diag = blk.sum(2) - eye                              # d F_i / d q_i
    Jb[:, np.arange(n), np.arange(n)] = diag
    J = Jb.transpose(0, 1, 3, 2, 4).reshape(B, 2 * n, 2 * n)
    return F.reshape(B, 2 * n), J


def mindist(X):
    D = X[:, :, None, :] - X[:, None, :, :]
    r2 = (D ** 2).sum(-1)
    r2[:, np.arange(n), np.arange(n)] = np.inf
    return np.sqrt(r2.min(axis=(1, 2)))


def solve_batch(X, iters=120):
    B = X.shape[0]
    mu = np.full(B, 1e-2)
    F, J = FJ(X); nf = np.linalg.norm(F, axis=1)
    I2 = np.eye(2 * n)
    for it in range(iters):
        A = J @ J + mu[:, None, None] * I2           # J symmetric, so J^T J = J J
        g = np.einsum('bij,bj->bi', J, F)
        try:
            d = -np.linalg.solve(A, g[..., None])[..., 0]
        except np.linalg.LinAlgError:
            d = np.zeros_like(g)
        Xn = X + d.reshape(B, n, 2)
        with np.errstate(all='ignore'):
            Fn, Jn = FJ(Xn)
        nfn = np.linalg.norm(Fn, axis=1)
        ok = np.isfinite(nfn) & (nfn < nf)
        X[ok] = Xn[ok]; F[ok] = Fn[ok]; J[ok] = Jn[ok]; nf[ok] = nfn[ok]
        mu = np.where(ok, np.maximum(mu / 3, 1e-12), mu * 4)
        if it > 20 and np.all((nf < 1e-13) | (mu > 1e8)):
            break
    return X, nf


def solve_batch_newton(X, iters=80):
    B = X.shape[0]
    F, J = FJ(X); nf = np.linalg.norm(F, axis=1)
    for it in range(iters):
        d = -np.einsum('bij,bj->bi', np.linalg.pinv(J, rcond=1e-10), F)
        t = np.ones(B); done = np.zeros(B, bool)
        for _ in range(12):
            Xn = X + (t[:, None] * d).reshape(B, n, 2)
            with np.errstate(all='ignore'):
                Fn, Jn = FJ(Xn)
            nfn = np.linalg.norm(Fn, axis=1)
            ok = (~done) & np.isfinite(nfn) & (nfn < nf)
            X[ok] = Xn[ok]; F[ok] = Fn[ok]; J[ok] = Jn[ok]; nf[ok] = nfn[ok]
            done |= ok
            t = np.where(done, t, t / 2)
        if np.all((nf < 1e-13) | (~done)):
            break
    return X, nf


def sample_cluster(B):
    R = (n / 8.0) ** (1 / 3) * 1.4 * rng.uniform(0.5, 1.6, size=(B, 1, 1))
    X = np.empty((B, n, 2))
    for b in range(B):
        kc = rng.integers(2, 5)
        cen = rng.uniform(-1, 1, (kc, 2))
        lab = rng.integers(0, kc, n)
        X[b] = cen[lab] + rng.normal(0, rng.uniform(0.02, 0.3), (n, 2))
    X -= X.mean(1, keepdims=True)
    return X * R


def sample_decagon(B):
    """Regular n-gon of the right size, randomly perturbed (probes classes close to the regular polygon)."""
    t = 2 * np.pi * np.arange(n) / n
    rho = (0.25 * sum(1 / np.sin(np.pi * k / n) for k in range(1, n))) ** (1 / 3)
    base = rho * np.stack([np.cos(t), np.sin(t)], -1)
    X = base[None] + rng.normal(0, 1, (B, 1, 1)) * rng.uniform(0.001, 0.08) * rng.normal(0, 1, (B, n, 2))
    return X - X.mean(1, keepdims=True)


def sample(B):
    """A mixture of start distributions, scaled around the size of a normalised CC."""
    R = (n / 8.0) ** (1 / 3) * 1.4 * rng.uniform(0.5, 1.6, size=(B, 1, 1))
    kind = rng.integers(0, 3, size=B)
    X = np.empty((B, n, 2))
    # uniform in disc
    t = rng.uniform(0, 2 * np.pi, (B, n)); rr = np.sqrt(rng.uniform(0, 1, (B, n)))
    disc = np.stack([rr * np.cos(t), rr * np.sin(t)], -1)
    sq = rng.uniform(-1, 1, (B, n, 2))
    ga = rng.normal(0, 0.5, (B, n, 2))
    X[kind == 0] = disc[kind == 0]; X[kind == 1] = sq[kind == 1]; X[kind == 2] = ga[kind == 2]
    X -= X.mean(1, keepdims=True)
    return X * R


def invariant(x):
    q = x.reshape(n, 2)
    q = q - q.mean(0)
    I = float((q ** 2).sum())
    d = np.sort(np.sqrt(((q[:, None] - q[None]) ** 2).sum(-1))[iu])
    return I, d


classes = []   # dicts: I, d, x, hits, first
starts = 0; conv = 0; t0 = time.time(); last_new = 0
log = open(OUT + '.log', 'w')
while time.time() - t0 < TLIM:
    B = 3000
    X0 = sample_cluster(B) if STARTS == 'cluster' else (sample_decagon(B) if STARTS == 'decagon' else sample(B))
    X, nf = solve_batch_newton(X0) if MODE == 'newton' else solve_batch(X0)
    starts += B
    if TIGHT:
        sel = np.isfinite(nf) & (nf < 1e-8)          # polish only runs that converged
        Xs = X[sel]
        for _ in range(4):
            with np.errstate(all='ignore'):
                F_, J_ = FJ(Xs)
                Xs = Xs - np.einsum('bij,bj->bi', np.linalg.pinv(J_, rcond=1e-12), F_).reshape(Xs.shape)
        with np.errstate(all='ignore'):
            nfs = np.linalg.norm(FJ(Xs)[0], axis=1)
        X[sel] = Xs; nf[sel] = nfs
    md = mindist(X)
    good = (nf < 1e-11) & (md > 1e-3)
    for b in np.nonzero(good)[0]:
        x = X[b].reshape(-1)
        I, d = invariant(x)
        hit = None
        for c in classes:
            if abs(c['I'] - I) < TOL_I and np.max(np.abs(c['d'] - d)) < TOL_D:
                hit = c; break
        conv += 1
        if hit is None:
            classes.append({'I': I, 'd': d, 'x': x.copy(), 'hits': 1, 'first': starts})
            last_new = starts
            log.write(f"{time.time()-t0:8.1f}s starts={starts} NEW class #{len(classes)} I={I:.10f} P=I^1.5={I**1.5:.8f}\n"); log.flush()
        else:
            hit['hits'] += 1
    log.write(f"{time.time()-t0:8.1f}s starts={starts} converged={conv} classes={len(classes)} last_new_at={last_new}\n"); log.flush()

classes.sort(key=lambda c: c['I'])
json.dump({'n': n, 'mode': MODE, 'start_distribution': STARTS, 'tight': TIGHT, 'starts': starts, 'converged': conv, 'seconds': time.time() - t0, 'seed': seed,
           'classes': [{'I': c['I'], 'P': c['I'] ** 1.5, 'x': c['x'].tolist(), 'hits': c['hits'], 'first_found_at_start': c['first']}
                       for c in classes]}, open(OUT, 'w'), indent=1)
log.write("done\n"); log.close()
