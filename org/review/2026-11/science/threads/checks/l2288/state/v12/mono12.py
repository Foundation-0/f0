"""Monodromy for the maximal 12-vertex Laman graph in the edge-pinned frame (A=1 at 0, B=2 at 1).
Usage: python mono12.py out.npz [seed]"""
import sys, time, json, os
import numpy as np
from lam12 import EdgeFrame

HERE = os.path.dirname(os.path.abspath(__file__))
G = json.load(open(os.path.join(HERE, "graph12.json")))
N = 6180


def make():
    return EdgeFrame(G["n"], G["edges"], (1, 2)), N


def dedup_merge(S, Znew, tol=1e-6):
    R = np.concatenate([S.real, S.imag], axis=1)
    key = R @ np.linspace(1, 2, R.shape[1])
    order = np.argsort(key); ks = key[order]
    add = []
    for z in Znew:
        r = np.concatenate([z.real, z.imag]); k = r @ np.linspace(1, 2, len(r))
        lo, hi = np.searchsorted(ks, k - 1e-4), np.searchsorted(ks, k + 1e-4)
        if hi > lo and np.abs(S[order[lo:hi]] - z).max(axis=1).min() < tol:
            continue
        if any(np.abs(a - z).max() < tol for a in add):
            continue
        add.append(z)
    return np.vstack([S] + [np.array(add)]) if add else S


if __name__ == "__main__":
    out = sys.argv[1]; seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    L, _ = make(); rng = np.random.default_rng(seed)
    Z = (rng.normal(size=2 * L.f) + 1j * rng.normal(size=2 * L.f))[None, :]
    P0 = L.F(Z, np.zeros(L.m, complex))[0]
    S = Z.copy(); t0 = time.time(); stale = 0
    for loop in range(400):
        sc = np.abs(P0).mean()
        P1 = P0 + (rng.normal(size=L.nP) + 1j * rng.normal(size=L.nP)) * sc
        P2 = P0 + (rng.normal(size=L.nP) + 1j * rng.normal(size=L.nP)) * sc
        Z1, ok, _ = L.track(S, P0, P1); Z1 = Z1[ok]
        Z2, ok, _ = L.track(Z1, P1, P2); Z2 = Z2[ok]
        Z3, ok, _ = L.track(Z2, P2, P0); Z3 = Z3[ok]
        before = len(S)
        S = dedup_merge(S, Z3)
        print(f"loop {loop}: kept {len(Z3)}/{before}, total {len(S)} / {N} ({time.time()-t0:.0f}s)", flush=True)
        stale = stale + 1 if len(S) == before else 0
        if len(S) >= N and stale >= 3:
            break
        if stale >= 15:
            break
        if loop % 5 == 0:
            np.savez(out, Z=S, P=P0)
    S, err = L.newton(S, P0)
    print(f"final {len(S)}, max residual {err.max():.1e}, min sep {L.min_sep(S)[0]:.2e}", flush=True)
    np.savez(out, Z=S, P=P0)
