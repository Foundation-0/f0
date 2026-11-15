"""Climb with a continuous tie-breaker: maximise score = nreal - sum over non-real half-solutions of
min(1, imag_norm / tau).  Pushes conjugate pairs toward the real locus.  Fixed eps.
Saves the trajectory every improvement.  Usage: python climb2.py n eps seconds seed"""
import sys, json, glob, time
import numpy as np
from unit import make, load_generic, solve_at_s, classify, HERE

n, eps, secs, seed = int(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
L, N = make(n)
S0, P0 = load_generic(n)
m = len(L.E); one = np.ones(m) / np.sqrt(m)
TAU = float(sys.argv[5]) if len(sys.argv) > 5 else 0.05
START = sys.argv[6] if len(sys.argv) > 6 else None
TAG = sys.argv[7] if len(sys.argv) > 7 else ""


def evaluate(v):
    Z, P1 = solve_at_s(L, S0, P0, 1 + eps * v)
    c = classify(L, Z)
    if not (c["nfound"] == N and c["conj_ok"]):
        return None, None, None, None
    im = L.imag_norm(Z)
    nonreal = np.sort(im)[c["nreal"]:] if c["nreal"] < N else np.array([])
    score = c["nreal"] - np.minimum(1, nonreal / TAU).sum() / 2
    return score, c["nreal"], Z, P1


R = []
for f in glob.glob(f"{HERE}/samples/n{n}_e{eps:g}_w*.json"):
    R += [r for r in json.load(open(f)) if r["ok"]]
if R:
    best = max(R, key=lambda r: r["nreal"])
    u = (np.array(best["s"]) - 1) / eps
    u -= (u @ one) * one; u /= np.linalg.norm(u)
if START:
    u = np.array(json.load(open(START))["traj"][-1]["u"])
cur, nr, Z, P1 = evaluate(u)
rng = np.random.default_rng(seed)
traj = [dict(it=0, nreal=nr, score=cur, u=u.tolist())]
t0 = time.time(); it = 0; sig = 0.2; fails = 0
fn = f"{HERE}/climb2{TAG}_n{n}_e{eps:g}.json"
while time.time() - t0 < secs and nr < N:
    it += 1
    v = u + sig * rng.normal(size=m)
    v -= (v @ one) * one; v /= np.linalg.norm(v)
    sc, nrv, Zv, Pv = evaluate(v)
    if sc is not None and sc > cur:
        if nrv != nr:
            print(f"it {it}: {2*nr} -> {2*nrv} / {2*N} score {sc:.3f} (sig {sig:.3f}, {time.time()-t0:.0f}s)", flush=True)
        u, cur, nr = v, sc, nrv; fails = 0
        traj.append(dict(it=it, nreal=nr, score=cur, u=u.tolist()))
        json.dump(dict(n=n, eps=eps, N=2 * N, final=2 * nr, iters=it, traj=traj), open(fn, "w"))
        if nr == N:
            np.savez(f"{HERE}/allreal/climb2{TAG}_n{n}_e{eps:g}.npz", Z=Zv, P=Pv, s=1 + eps * v)
    else:
        fails += 1
        sig = max(sig * 0.95, 0.01)
        if fails % 40 == 0:
            sig = 0.2
json.dump(dict(n=n, eps=eps, N=2 * N, final=2 * nr, iters=it, traj=traj), open(fn, "w"))
print(f"final {2*nr}/{2*N} after {it} iterations, score {cur:.3f}")
