"""Refutation test for 'no all-real direction at small eps': random-walk hill climb over directions u
(unit, orthogonal to ones) at fixed eps, maximising the number of real solutions.
Usage: python climb.py n eps seconds seed
Starts from the best ray in the saved samples at that eps.  Writes climb_n{n}_e{eps}.json (trajectory)."""
import sys, json, glob, time, os
import numpy as np
from unit import make, load_generic, solve_at_s, classify, HERE

n, eps, secs, seed = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
L, N = make(n)
S0, P0 = load_generic(n)
m = len(L.E)
one = np.ones(m) / np.sqrt(m)
R = []
for f in glob.glob(f"{HERE}/samples/n{n}_e{eps:g}_w*.json"):
    R += [r for r in json.load(open(f)) if r["ok"]]
best = max(R, key=lambda r: r["nreal"])
u = (np.array(best["s"]) - 1) / eps
u -= (u @ one) * one; u /= np.linalg.norm(u)
cur = best["nreal"]
rng = np.random.default_rng(seed)
traj = [dict(it=0, nreal=cur, u=u.tolist())]
t0 = time.time(); it = 0; sig = 0.3
while time.time() - t0 < secs and cur < N:
    it += 1
    v = u + sig * rng.normal(size=m)
    v -= (v @ one) * one; v /= np.linalg.norm(v)
    Z, P1 = solve_at_s(L, S0, P0, 1 + eps * v)
    c = classify(L, Z)
    if c["nfound"] == N and c["conj_ok"] and c["nreal"] >= cur:
        if c["nreal"] > cur:
            print(f"it {it}: {2*cur} -> {2*c['nreal']} / {2*N} (sig {sig:.3f}, {time.time()-t0:.0f}s)", flush=True)
        u, cur = v, c["nreal"]
        traj.append(dict(it=it, nreal=cur, u=u.tolist()))
        if cur == N:
            np.savez(f"{HERE}/allreal/climb_n{n}_e{eps:g}.npz", Z=Z, P=P1, s=1 + eps * v)
    else:
        sig = max(sig * 0.97, 0.02)
    if it % 50 == 0:
        sig = 0.3   # restart step size
json.dump(dict(n=n, eps=eps, start=2 * best["nreal"], final=2 * cur, N=2 * N, iters=it, traj=traj),
          open(f"{HERE}/climb_n{n}_e{eps:g}.json", "w"))
print(f"final {2*cur}/{2*N} after {it} iterations")
