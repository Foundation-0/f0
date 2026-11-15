"""Local size of the all-real cone around a found all-real direction u (from climb_n{n}_e{eps}.json).
v = normalize(u + theta * g), g Gaussian projected orthogonal to ones and u, normalised; theta ~ angle.
Usage: python conesize.py n eps nper  -> conesize_n{n}.json"""
import sys, json
import numpy as np
from unit import make, load_generic, solve_at_s, classify, HERE

n, eps, nper = int(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
L, N = make(n)
S0, P0 = load_generic(n)
m = len(L.E); one = np.ones(m) / np.sqrt(m)
u = np.array(json.load(open(sys.argv[4] if len(sys.argv) > 4 else f"{HERE}/climb_n{n}_e{eps:g}.json"))["traj"][-1]["u"])
rng = np.random.default_rng(11)
out = dict(n=n, eps=eps, rows=[])
for th in (0.02, 0.05, 0.1, 0.2, 0.4):
    k = ok = 0
    for _ in range(nper):
        g = rng.normal(size=m); g -= (g @ one) * one; g -= (g @ u) * u; g /= np.linalg.norm(g)
        v = np.cos(th) * u + np.sin(th) * g
        Z, P1 = solve_at_s(L, S0, P0, 1 + eps * v)
        r = classify(L, Z)
        if r["nfound"] == N and r["conj_ok"]:
            ok += 1; k += r["nreal"] == N
    out["rows"].append(dict(theta=th, ok=ok, allreal=k))
    print(f"n={n} theta={th}: all-real {k}/{ok}", flush=True)
json.dump(out, open(f"{HERE}/conesize_n{n}.json", "w"), indent=1)
