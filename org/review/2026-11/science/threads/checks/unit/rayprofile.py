"""Real count along the ray s = 1 + eps u for the final direction of a climb.
Usage: python rayprofile.py n eps_of_climb   -> rayprofile_n{n}.json"""
import sys, json
import numpy as np
from unit import make, load_generic, solve_at_s, classify, HERE

n, ec = int(sys.argv[1]), float(sys.argv[2])
L, N = make(n)
S0, P0 = load_generic(n)
c = json.load(open(sys.argv[3] if len(sys.argv) > 3 else f"{HERE}/climb_n{n}_e{ec:g}.json"))
u = np.array(c["traj"][-1]["u"])
out = dict(n=n, climb_eps=ec, u=u.tolist(), profile=[])
for eps in [0.3, 0.1, 0.05, 0.03, 0.01, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5]:
    s = 1 + eps * u
    if (s <= 0).any():
        continue
    Z, P1 = solve_at_s(L, S0, P0, s, tol_rel=1e-7, rounds=8)
    r = classify(L, Z)
    ok = r["nfound"] == N and r["conj_ok"]
    out["profile"].append(dict(eps=eps, ok=bool(ok), real_full=2 * r["nreal"], N_full=2 * N, minsep=r["minsep"],
                               min_imag_nonreal=r["min_imag_nonreal"]))
    print(f"n={n} eps={eps:g} ok={ok} real={2*r['nreal']}/{2*N} minsep={r['minsep']:.2e} minIm={r['min_imag_nonreal']}", flush=True)
json.dump(out, open(f"{HERE}/rayprofile_n{n}.json", "w"), indent=1)
