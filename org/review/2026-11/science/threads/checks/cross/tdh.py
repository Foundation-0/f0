"""Total-degree homotopy (gamma trick) for the equilibrium system: independent completeness check
of the monodromy count (numerical). Start system z_j^4 - 1 (every equation has degree 4).
Usage: python tdh.py mono_file.npz [chunk]"""
import sys, time, itertools
import numpy as np
from cross_lib import F_J, newton, merge

f = np.load(sys.argv[1])
P, q, Smono = f["P"], f["q"], f["S"]
n, D = q.shape[0], P.shape[1]
N = n + D
rng = np.random.default_rng(7)
gamma = np.exp(2j * np.pi * rng.random())
roots = np.exp(2j * np.pi * np.arange(4) / 4)
starts = np.array(list(itertools.product(roots, repeat=N)))
print(f"n={n} D={D}: {len(starts)} start paths", flush=True)


def H(Z, s):
    B = len(Z)
    F, J = F_J(Z, np.broadcast_to(P, (B, n, D)), np.broadcast_to(q, (B, n)), D)
    G = Z ** 4 - 1
    JG = np.zeros_like(J)
    idx = np.arange(N)
    JG[:, idx, idx] = 4 * Z ** 3
    s_ = s[:, None]
    Hv = (1 - s_) * gamma * G + s_ * F
    Hz = (1 - s_)[..., None] * gamma * JG + s_[..., None] * J
    Hs = F - gamma * G
    return Hv, Hz, Hs


def track(Z0, s_end=1.0, h0=0.01, hmin=1e-12, max_iter=200000):
    B = len(Z0)
    Z = Z0.astype(complex).copy()
    s = np.zeros(B)
    h = np.full(B, h0)
    done = np.zeros(B, bool)
    fail = np.zeros(B, bool)
    it = 0
    while True:
        act = ~(done | fail)
        if not act.any() or it > max_iter:
            break
        it += 1
        ia = np.where(act)[0]
        za, sa = Z[ia], s[ia]
        ha = np.minimum(h[ia], s_end - sa)
        _, J0, Hs0 = H(za, sa)
        try:
            v0 = -np.linalg.solve(J0, Hs0[..., None])[..., 0]
        except np.linalg.LinAlgError:
            v0 = np.zeros_like(za)
        z1 = za + ha[:, None] * v0
        s1 = sa + ha
        _, J1, Hs1 = H(z1, s1)
        try:
            v1 = -np.linalg.solve(J1, Hs1[..., None])[..., 0]
        except np.linalg.LinAlgError:
            v1 = v0
        zc = za + 0.5 * ha[:, None] * (v0 + v1)
        ok = np.ones(len(ia), bool)
        prev = None
        scale = 1.0 + np.max(np.abs(zc), axis=1)
        for c in range(3):
            Hc, Jc, _ = H(zc, s1)
            try:
                dz = np.linalg.solve(Jc, Hc[..., None])[..., 0]
            except np.linalg.LinAlgError:
                dz = np.full_like(zc, np.inf)
            nd = np.max(np.abs(dz), axis=1)
            nd = np.where(np.isfinite(nd), nd, np.inf)
            zc = zc - np.where(np.isfinite(dz), dz, 0)
            if prev is not None:
                ok &= (nd <= 0.5 * prev + 1e-14 * scale) | (nd < 1e-10 * scale)
            if c == 0:
                ok &= nd < 0.1 * scale
            prev = nd
        ok &= prev < 1e-8 * scale
        ok &= np.all(np.isfinite(zc), axis=1)
        acc, rej = ia[ok], ia[~ok]
        Z[acc] = zc[ok]
        s[acc] = s1[ok]
        h[acc] = np.minimum(h[acc] * 1.6, 0.05)
        h[rej] *= 0.5
        done |= s >= s_end - 1e-15
        fail[rej[h[rej] < hmin]] = True
        fail |= (np.max(np.abs(Z), axis=1) > 1e7) & ~done
    return Z, done & ~fail, s


t0 = time.time()
chunk = int(sys.argv[2]) if len(sys.argv) > 2 else 4096
found = np.zeros((0, N), complex)
nfin = 0
for c0 in range(0, len(starts), chunk):
    Z, ok, sfin = track(starts[c0:c0 + chunk], s_end=1.0)
    Zf = Z[ok]
    Zf, err = newton(Zf, np.broadcast_to(P, (len(Zf), n, D)), np.broadcast_to(q, (len(Zf), n)), D)
    good = (err < 1e-10) & (np.max(np.abs(Zf), axis=1) < 1e5)
    nfin += good.sum()
    found, _ = merge(found, Zf[good])
    print(f"chunk {c0}: reached end {ok.sum()}, finite good {good.sum()}, distinct so far {len(found)}, "
          f"s at failure: min {np.min(sfin[~ok]) if (~ok).any() else 1:.3f}, {time.time()-t0:.0f}s", flush=True)
both, added = merge(Smono, found)
print(f"RESULT: total-degree distinct finite solutions {len(found)}; monodromy {len(Smono)}; union {len(both)} "
      f"(TDH adds {len(both)-len(Smono)} not in monodromy set)")
np.savez(sys.argv[1].replace("mono_", "tdh_"), found=found)
