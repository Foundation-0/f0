"""Unit-point statistics (search code, not proof code).

Graphs: the maximal Laman graphs for n = 6..11 (codes from threads/laman/validate_paper.log for 6..9,
and the project codes for 10, 11, which are isomorphic to the log's codes; checked in NOTES.md).

Parameters: squared lengths s_e for all 2n-3 edges.  Near cell: s = 1 + eps * u, u uniform on the unit
sphere in the hyperplane orthogonal to (1,...,1) (the all-ones direction only rescales, which is a
similarity).  Far cell: lengths iid U[0.5, 1.5], kept if the pinned triangle exists.

A sample counts only if the tracker returns all N = c/2 distinct solutions AND the set is closed under
complex conjugation (an involution).  Real = fixed point of conjugation.
"""
import json, os, sys, time
import numpy as np
from scipy.spatial import cKDTree
from lam import Laman, decode
from monodromy import robust_solve, _distinct

HERE = os.path.dirname(os.path.abspath(__file__))
GR = {
    6: (29327, (1, 2, 3), 12),
    7: (1714767, (3, 4, 7), 28),
    8: (106235230, (2, 5, 7), 68),
    9: (22097893737, (1, 3, 8), 172),
    10: (4778440734593, (7, 2, 3), 440),
    11: (18120782205838348, (3, 9, 10), 1144),
}
GEN = {10: "l880_generic.npz", 11: "l2288_generic.npz"}


def make(n):
    code, tri, N = GR[n]
    return Laman(n, decode(n, code), tri), N


def load_generic(n):
    fn = os.path.join(HERE, GEN.get(n, f"g{n}_generic.npz"))
    d = np.load(fn)
    return d["Z"], d["P"]


def emb(Z):
    return np.concatenate([Z.real, Z.imag], axis=1)


def classify(L, Z):
    """returns dict: nfound, minsep, conj_ok, nreal, min_imag_nonreal, max_imag_real."""
    N = len(Z)
    if N < 2:
        return dict(nfound=N, minsep=0.0, conj_ok=False, nreal=0, min_imag_nonreal=None, max_imag_real=None)
    X = emb(Z)
    tr = cKDTree(X)
    d2, _ = tr.query(X, k=2)
    minsep = float(d2[:, 1].min())
    C = emb(L.conj_partner(Z))
    dc, ic = tr.query(C, k=1)
    scale = 1.0 + np.abs(X).max()
    match_tol = min(1e-7 * scale, 0.01 * minsep)
    conj_ok = bool((dc < match_tol).all() and (ic[ic] == np.arange(N)).all())
    im = L.imag_norm(Z)
    real = (ic == np.arange(N)) & (dc < match_tol)
    return dict(nfound=N, minsep=minsep, conj_ok=conj_ok, nreal=int(real.sum()),
                min_imag_nonreal=(float(im[~real].min()) if (~real).any() else None),
                max_imag_real=(float(im[real].max()) if real.any() else None),
                maxabs=float(np.abs(Z).max()))


def solve_at_s(L, S0, P0, s, tol_rel=1e-6, rounds=6, seed=5):
    lam = np.sqrt(s)
    P1, sc = L.real_params_from_lengths(lam)
    Z, good = robust_solve(L, S0, P0, P1, tol_rel=tol_rel, rounds=rounds, seed=seed)
    return Z, P1


def unit_dirs(m, K, seed):
    rng = np.random.default_rng(seed)
    U = rng.normal(size=(K, m))
    one = np.ones(m) / np.sqrt(m)
    U -= (U @ one)[:, None] * one[None, :]
    U /= np.linalg.norm(U, axis=1)[:, None]
    return U


def far_lengths(L, rng):
    while True:
        lam = rng.uniform(0.5, 1.5, size=len(L.E))
        a, b, c = (lam[i] for i in L.tri_edges)
        if a < b + c and b < a + c and c < a + b:
            return lam


class Saver:
    def __init__(self, n, tag):
        self.n, self.tag = n, tag
        self.data = {}
        os.makedirs(os.path.join(HERE, "samples"), exist_ok=True)

    def add(self, cell, rec):
        self.data.setdefault(cell, []).append(rec)
        fn = os.path.join(HERE, "samples", f"n{self.n}_{cell}_{self.tag}.json")
        tmp = fn + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self.data[cell], f)
        os.replace(tmp, fn)


EPS = [1.0, 0.3, 0.1, 0.03, 0.01, 0.003, 0.001]


def run(n, k0, k1, tag, eps_list=EPS, far_per_dir=1, dir_seed=None, far_seed=None, tmax=None):
    L, N = make(n)
    S0, P0 = load_generic(n)
    assert len(S0) == N
    m = len(L.E)
    U = unit_dirs(m, 5000, dir_seed if dir_seed is not None else 1000 + n)
    rng_far = np.random.default_rng(far_seed if far_seed is not None else 7000 + 13 * n + k0)
    sv = Saver(n, tag)
    t00 = time.time()
    for k in range(k0, k1):
        u = U[k]
        for eps in eps_list:
            s = 1.0 + eps * u
            if (s <= 0).any():
                continue
            t0 = time.time()
            Z, P1 = solve_at_s(L, S0, P0, s)
            rec = classify(L, Z)
            rec.update(k=k, eps=eps, ok=bool(rec["nfound"] == N and rec["conj_ok"]), N=N,
                       secs=round(time.time() - t0, 2), s=s.tolist())
            sv.add(f"e{eps:g}", rec)
            if rec["ok"] and rec["nreal"] == N:
                np.savez(os.path.join(HERE, "allreal", f"n{n}_e{eps:g}_k{k}.npz"), Z=Z, P=P1, s=s)
        for j in range(far_per_dir):
            lam = far_lengths(L, rng_far)
            t0 = time.time()
            Z, P1 = solve_at_s(L, S0, P0, lam ** 2)
            rec = classify(L, Z)
            rec.update(k=k, eps=None, ok=bool(rec["nfound"] == N and rec["conj_ok"]), N=N,
                       secs=round(time.time() - t0, 2), s=(lam ** 2).tolist())
            sv.add("far", rec)
            if rec["ok"] and rec["nreal"] == N:
                np.savez(os.path.join(HERE, "allreal", f"n{n}_far_k{k}_{j}.npz"), Z=Z, P=P1, s=lam ** 2)
        print(f"n={n} dir {k} done ({time.time()-t00:.0f}s)", flush=True)
        if tmax and time.time() - t00 > tmax:
            print("time limit reached", flush=True)
            break


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "allreal"), exist_ok=True)
    n, k0, k1, tag = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    tmax = float(sys.argv[5]) if len(sys.argv) > 5 else None
    run(n, k0, k1, tag, tmax=tmax)
