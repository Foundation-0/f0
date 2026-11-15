"""Track the 1144 generic solutions to real edge lengths and count real ones.  Random near-unit sampling."""
import sys, time, json
import numpy as np
from monodromy import make, robust_solve

L, N = make("l2288")
d = np.load("l2288_generic.npz"); S0, P0 = d["Z"], d["P"]


def solve_real(lam, tol_rel=1e-6):
    P1, sc = L.real_params_from_lengths(lam)
    Z, good = robust_solve(L, S0, P0, P1, tol_rel=tol_rel)
    ms = L.min_sep(Z)[0]
    im = L.imag_norm(Z)
    return Z, P1, (N if good else -1), ms, int((im < 1e-8).sum()), im


if __name__ == "__main__":
    mode = sys.argv[1]; nsamp = int(sys.argv[2]); seed = int(sys.argv[3])
    rng = np.random.default_rng(seed)
    best = -1; res = []
    t0 = time.time()
    for k in range(nsamp):
        if mode == "unit":
            eps = float(sys.argv[4])
            lam = 1.0 + eps * rng.uniform(0, 1, size=19)
        elif mode == "shell":
            eps = float(sys.argv[4])
            lam = 1.0 + eps * rng.uniform(-1, 1, size=19)
        Z, P1, nok, ms, nr, im = solve_real(lam)
        res.append(dict(lam=lam.tolist(), ok=nok, minsep=ms, nreal=nr))
        flag = ""
        if nok == N and ms > 1e-7 and nr > best:
            best = nr; flag = " *"
            np.savez(f"best_{mode}_{seed}.npz", Z=Z, P=P1, lam=lam)
        print(f"{k} ok={nok} minsep={ms:.1e} real={2*nr}/2288{flag} ({time.time()-t0:.0f}s)", flush=True)
    json.dump(res, open(f"samples_{mode}_{seed}.json", "w"))
