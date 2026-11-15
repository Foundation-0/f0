"""Monodromy solve at a generic complex parameter point, then a trace test.
Usage: python monodromy.py {l880|l2288} out.npz
"""
import sys, time
import numpy as np
from lam import Laman, decode

GRAPHS = {
    "l880": (10, 4778440734593, (7, 2, 3), 440),
    "l2288": (11, 18120782205838348, (3, 9, 10), 1144),
}


def make(name):
    n, code, tri, N = GRAPHS[name]
    return Laman(n, decode(n, code), tri), N


def random_seed(L, rng):
    f = L.f
    Z = (rng.normal(size=2 * f) + 1j * rng.normal(size=2 * f))[None, :]
    uC = rng.normal() + 1j * rng.normal(); wC = rng.normal() + 1j * rng.normal()
    P = np.zeros(L.nP, complex); P[0], P[1] = uC, wC
    P[2:] = 0
    P[2:] = L.F(Z, P)[0]  # makes F(Z, P) = 0
    return Z, P


def run(name, out, seed=1, max_loops=200, stall=12):
    L, N = make(name)
    rng = np.random.default_rng(seed)
    Z, P0 = random_seed(L, rng)
    S = Z.copy()
    t0 = time.time(); stale = 0
    for loop in range(max_loops):
        P1 = P0 + (rng.normal(size=L.nP) + 1j * rng.normal(size=L.nP)) * np.abs(P0).mean()
        P2 = P0 + (rng.normal(size=L.nP) + 1j * rng.normal(size=L.nP)) * np.abs(P0).mean()
        Z1, ok1, _ = L.track(S, P0, P1); Z1 = Z1[ok1]
        Z2, ok2, _ = L.track(Z1, P1, P2); Z2 = Z2[ok2]
        Z3, ok3, _ = L.track(Z2, P2, P0); Z3 = Z3[ok3]
        before = len(S)
        for z in Z3:
            if np.abs(S - z).max(axis=1).min() > 1e-6:
                S = np.vstack([S, z[None]])
        print(f"loop {loop}: kept {len(Z3)}/{before}, total {len(S)} / {N}  ({time.time()-t0:.1f}s)", flush=True)
        stale = stale + 1 if len(S) == before else 0
        if len(S) >= N and stale >= 3:
            break
        if stale >= stall:
            break
    S, err = L.newton(S, P0)
    ms, _ = L.min_sep(S)
    print(f"final {len(S)} solutions, max residual {err.max():.2e}, min separation {ms:.3e}")
    np.savez(out, Z=S, P=P0)
    return L, S, P0


def trace_test(L, S, P0, rng):
    """Linear trace test along a pencil P(t) = P0 + t * v.  Track to t = +-eps and check the sum of
    solutions is affine in t (second difference near 0)."""
    v = (rng.normal(size=L.nP) + 1j * rng.normal(size=L.nP)) * 0.05
    sums = []
    for t in (-1.0, 1.0):
        Zt, ok, _ = L.track(S, P0, P0 + t * v)
        if not ok.all():
            return None
        sums.append(Zt.sum(axis=0))
    s0 = S.sum(axis=0)
    second = sums[0] + sums[1] - 2 * s0
    scale = np.abs(sums[1] - sums[0]).max()
    return np.abs(second).max(), scale


if __name__ == "__main__":
    name, out = sys.argv[1], sys.argv[2]
    L, S, P0 = run(name, out)
    # note: a pencil trace test in these parameters is not affine even for complete sets (checked on L880),
    # so completeness rests on saturation plus agreement with the known c_2 / 2.


def dup_indices(Z, tol=1e-8):
    D = np.abs(Z[:, None, :] - Z[None, :, :]).max(axis=2)
    np.fill_diagonal(D, np.inf)
    return np.where(D.min(axis=1) < tol)[0]


def robust_solve(L, S0, P0, P1, tol_rel=1e-6, rounds=6, seed=5, N=None):
    """Collect the distinct converged endpoints of several homotopies from (S0, P0) to P1
    (straight, then random complex detours) until len(S0) distinct solutions are found.
    Endpoints of different homotopies may be permuted, so only the union of endpoint SETS is used."""
    N = N or len(S0)
    rng = np.random.default_rng(seed)
    Z, ok, _ = L.track(S0, P0, P1, tol_rel=tol_rel, hmin=1e-14, max_iter=30000)
    sol = _distinct(Z[ok])
    for _ in range(rounds):
        if len(sol) >= N:
            break
        G = 0.3j * np.abs(P1 - P0) * rng.uniform(-1, 1, size=L.nP)
        Zb, okb, _ = L.track(S0, P0, P1, G=G, tol_rel=tol_rel, hmin=1e-15, max_iter=60000)
        sol = _distinct(np.vstack([sol, Zb[okb]]))
    return sol, len(sol) == N


def _distinct(Z, tol=1e-9):
    if len(Z) == 0:
        return Z
    key = np.round((Z @ np.linspace(1, 2, Z.shape[1])).real, 7)
    order = np.argsort(key)
    Z = Z[order]
    keep = [0]
    for i in range(1, len(Z)):
        # compare to recent kept rows with nearby keys
        j = len(keep) - 1
        dup = False
        while j >= 0 and abs(key[order[i]] - key[order[keep[j]]]) < 1e-5:
            if np.abs(Z[i] - Z[keep[j]]).max() < tol:
                dup = True; break
            j -= 1
        if not dup:
            keep.append(i)
    return Z[keep]
