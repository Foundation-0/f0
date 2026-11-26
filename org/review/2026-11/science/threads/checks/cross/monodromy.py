"""Monodromy solve of the equilibrium system at a random complex parameter point (numerical).
Usage: python monodromy.py n D seed [stall_loops]
Writes out/mono_n{n}_D{D}_s{seed}.npz with the base parameters and all solutions found."""
import sys, time, json
import numpy as np
from cross_lib import F_J, newton, track, linear_path, merge

n, D, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
stall_max = int(sys.argv[4]) if len(sys.argv) > 4 else 12
assert n - 1 == D, "seed construction assumes n-1 == D"
rng = np.random.default_rng(seed)
cn = lambda *s: rng.normal(size=s) + 1j * rng.normal(size=s)

t0 = time.time()
x = cn(D)
P = cn(n, D)
dx = x[None] - P
d = np.sum(dx * dx, axis=1)
t = 1 / np.sqrt(d)
# solve q with q_0 = 1
A = (t[1:, None] ** 3 * dx[1:]).T  # (D, n-1)
b = -(t[0] ** 3) * dx[0]
q = np.concatenate([[1.0], np.linalg.solve(A, b)])
Z0 = np.concatenate([x, t])[None]
Z0, err = newton(Z0, P[None], q[None], D)
print("seed residual", err, flush=True)
S = np.concatenate([Z0, Z0 * np.concatenate([np.ones(D), -np.ones(n)])[None]])
stall = 0
loop = 0
hist = []
while stall < stall_max:
    loop += 1
    P1, q1 = P + 0.8 * cn(n, D), q + 0.8 * cn(n)
    P2, q2 = P + 0.8 * cn(n, D), q + 0.8 * cn(n)
    Z = S.copy()
    okall = np.ones(len(Z), bool)
    for (Pa, qa, Pb, qb) in [(P, q, P1, q1), (P1, q1, P2, q2), (P2, q2, P, q)]:
        Z, ok = track(Z, linear_path(Pa, qa, Pb, qb), D)
        okall &= ok
    Z = Z[okall]
    Z, err = newton(Z, np.broadcast_to(P, (len(Z), n, D)), np.broadcast_to(q, (len(Z), n)), D)
    Z = Z[err < 1e-10]
    # add global flip
    Z = np.concatenate([Z, Z * np.concatenate([np.ones(D), -np.ones(n)])[None]])
    S, added = merge(S, Z)
    hist.append((loop, len(S), added, int((~okall).sum())))
    print(f"loop {loop}: total {len(S)} (+{added}), path failures {int((~okall).sum())}, {time.time()-t0:.1f}s", flush=True)
    stall = 0 if added else stall + 1

# final check
F, J = F_J(S, np.broadcast_to(P, (len(S), n, D)), np.broadcast_to(q, (len(S), n)), D)
cond = np.linalg.cond(J)
dmin = min(np.max(np.abs(S[i] - S[j])) for i in range(len(S)) for j in range(i))
print(f"FINAL n={n} D={D} seed={seed}: {len(S)} solutions, max residual {np.max(np.abs(F)):.2e}, max cond {np.max(cond):.2e}, min sep {dmin:.2e}, loops {loop}, {time.time()-t0:.1f}s")
np.savez(f"out/mono_n{n}_D{D}_s{seed}.npz", P=P, q=q, S=S, hist=np.array(hist))
