"""Second-stage push (numerical): one tracked target pair at a time, persistent adaptive trust region,
longer patience, and random kicks (basin hopping) when the LP stalls. Keeps the best physical count.
Usage: python push2.py n D starts.json seed tag [iters] [kicks]
starts.json: list of theta vectors (same normalisation as push.py)."""
import sys, time, json
import numpy as np
from scipy.optimize import linprog
from cross_lib import F_J, newton, track, arc_path, param_jac

n, D = int(sys.argv[1]), int(sys.argv[2])
starts = [np.array(t, float) for t in json.load(open(sys.argv[3]))]
seed, tag = int(sys.argv[4]), sys.argv[5]
ITERS = int(sys.argv[6]) if len(sys.argv) > 6 else 300
KICKS = int(sys.argv[7]) if len(sys.argv) > 7 else 6
rng = np.random.default_rng(seed)
base = np.load(f"out/mono_n{n}_D{D}_s1.npz")
Pb, qb, Sb = base["P"], base["q"], base["S"]
NS = len(Sb)
npos = 2 if D == 2 else 5
m = npos + n - 1
LO = np.array([-3, 0.02, -12, -12] if D == 2 else [-3, 0.02, -3, -3, -3] + [-16] * 3, float)
HI = np.array([4, 4, 12, 12] if D == 2 else [4, 4, 4, 3, 3] + [16] * 3, float)
TRMAX = np.concatenate([0.05 * np.ones(npos), 0.2 * np.ones(n - 1)])
KICK = np.concatenate([0.03 * np.ones(npos), 0.15 * np.ones(n - 1)])


def theta_to_Pq(th):
    P = np.zeros((n, D)); P[1, 0] = 1.0
    if D == 2:
        P[2] = th[0:2]
    else:
        P[2, :2] = th[0:2]; P[3] = th[2:5]
    return P.astype(complex), np.concatenate([[1.0], np.exp(th[npos:])]).astype(complex)


def dPq_dtheta(th):
    M = np.zeros((n * D + n, m))
    M[2 * D + 0, 0] = 1; M[2 * D + 1, 1] = 1
    if D == 3:
        M[3 * D + 0, 2] = 1; M[3 * D + 1, 3] = 1; M[3 * D + 2, 4] = 1
    for j in range(n - 1):
        M[n * D + 1 + j, npos + j] = np.exp(th[npos + j])
    return M


def bc(P, q, B):
    return np.broadcast_to(P, (B, n, D)), np.broadcast_to(q, (B, n))


def move(Z, Pa, qa, P2, q2, scale=0.3, tries=3):
    for _ in range(tries):
        Pm = scale * (rng.normal(size=Pa.shape) + 1j * rng.normal(size=Pa.shape)) * (np.abs(P2 - Pa).max() + 1e-3)
        qm = scale * (rng.normal(size=qa.shape) + 1j * rng.normal(size=qa.shape)) * (np.abs(q2 - qa).max() + 1e-3)
        Pm[:2] = 0; qm[0] = 0
        Zt, ok = track(Z, arc_path(Pa, qa, P2, q2, Pm, qm), D)
        if not ok.all():
            continue
        Zt, err = newton(Zt, *bc(P2, q2, len(Zt)), D)
        if err.max() > 1e-9:
            continue
        dd = np.max(np.abs(Zt[:, None] - Zt[None]), axis=2); np.fill_diagonal(dd, 1)
        if dd.min() < 1e-6:
            continue
        return Zt
    return None


def classify(Z):
    imm = np.max(np.abs(Z.imag), axis=1) / (1 + np.max(np.abs(Z.real), axis=1))
    real = imm < 1e-9
    return real, real & np.all(Z[:, D:].real > 0, axis=1)


def Tval(z):
    return float(np.sum(z.imag ** 2) + np.sum(np.minimum(z[D:].real, 0) ** 2))


def reps_of(Z, real):
    return [i for i in np.where(~real)[0]
            if Z[i, D:].real.sum() >= 0 and Z[i].imag[np.argmax(np.abs(Z[i].imag))] > 0]


results = []
for si, th in enumerate(starts):
    t0 = time.time()
    th = np.clip(th, LO, HI)
    P, q = theta_to_Pq(th)
    Z = move(Sb, Pb, qb, P, q, scale=0.5, tries=6)
    if Z is None:
        print(f"[{tag} {si}] start fail", flush=True); continue
    real, phys = classify(Z)
    best_n, best_th, best_T = int(phys.sum()), th.copy(), np.inf
    best_T_theta = th.copy()
    nearest_hist = []
    kicks = 0
    tr = TRMAX * 0.3
    stall = 0
    target = None
    events = []
    for it in range(ITERS):
        real, phys = classify(Z)
        nphys = int(phys.sum())
        reps = reps_of(Z, real)
        if not reps:
            break
        T = np.array([Tval(Z[i]) for i in reps])
        if target is None or stall >= 4:
            # choose among the 3 nearest at random after stalls
            order = np.argsort(T)
            target = Z[reps[order[0] if stall < 4 else order[rng.integers(min(3, len(order)))]]].copy()
            stall = 0 if stall >= 4 else stall
        i0 = int(np.argmin(np.max(np.abs(Z - target[None]), axis=1)))
        z = Z[i0]
        Tt = Tval(z)
        nearest_hist.append(float(T.min()))
        if nphys == best_n and float(T.min()) < best_T:
            best_T = float(T.min()); best_T_theta = th.copy()
        Pbt, qbt = bc(P, q, NS)
        F, J = F_J(Z, Pbt, qbt, D)
        dZ = -np.linalg.solve(J, param_jac(Z, Pbt, qbt, D) @ dPq_dtheta(th))
        A_ub, b_ub = [], []
        ph = np.where(phys)[0]
        for a_ in range(len(ph)):
            for b_ in range(a_ + 1, len(ph)):
                a, b = ph[a_], ph[b_]
                diff = (Z[a] - Z[b]).real
                A_ub.append(-2 * diff @ (dZ[a] - dZ[b]).real); b_ub.append(0.35 * float(diff @ diff))
        gT = 2 * (z.imag @ dZ[i0].imag) + 2 * (np.minimum(z[D:].real, 0) @ dZ[i0, D:].real)
        bounds = [(max(-tr[j], LO[j] - th[j]), min(tr[j], HI[j] - th[j])) for j in range(m)]
        res = linprog(gT / (np.linalg.norm(gT) + 1e-300), A_ub=np.array(A_ub) if A_ub else None,
                      b_ub=np.array(b_ub) if b_ub else None, bounds=bounds, method="highs")
        ok = False
        if res.success and np.linalg.norm(res.x) > 1e-14:
            th2 = th + res.x
            P2, q2 = theta_to_Pq(th2)
            Z2 = move(Z, P, q, P2, q2)
            if Z2 is not None:
                real2, phys2 = classify(Z2)
                n2 = int(phys2.sum())
                j0 = int(np.argmin(np.max(np.abs(Z2 - z[None]), axis=1)))
                if n2 > nphys or (n2 >= nphys and Tval(Z2[j0]) < Tt):
                    if n2 != nphys:
                        events.append((it, nphys, n2))
                        print(f"*** [{tag} {si} it {it}] physical {nphys} -> {n2}", flush=True)
                    th, P, q, Z = th2, P2, q2, Z2
                    target = Z2[j0].copy() if n2 == nphys else None
                    ok = True
                    tr = np.minimum(tr * 1.5, TRMAX)
        if not ok:
            tr = tr * 0.4
            if tr.max() < 1e-4 * TRMAX.max():
                stall = 4
                tr = TRMAX * 0.3
                if kicks >= KICKS:
                    break
                # kick from the best configuration
                kicks += 1
                thk = np.clip(best_th + rng.normal(size=m) * KICK, LO, HI)
                Pk, qk = theta_to_Pq(thk)
                Zk = move(Z, P, q, Pk, qk, scale=0.5, tries=4)
                if Zk is not None:
                    th, P, q, Z = thk, Pk, qk, Zk
                    target = None
                    rk, pk = classify(Z)
                    events.append((it, "kick", int(pk.sum())))
        real, phys = classify(Z)
        if int(phys.sum()) > best_n:
            best_n, best_th, best_T = int(phys.sum()), th.copy(), np.inf
    rec = {"start": si, "best_phys": best_n, "best_theta": best_th.tolist(), "iters": it + 1, "kicks": kicks,
           "nearest_T_min_at_best_count": best_T, "theta_at_min_T": best_T_theta.tolist(), "events": events, "final_theta": th.tolist(),
           "secs": time.time() - t0}
    results.append(rec)
    print(f"[{tag} {si}] best {best_n}, nearest T at best count {best_T:.3e}, kicks {kicks}, iters {it+1}, {time.time()-t0:.0f}s", flush=True)
    json.dump(results, open(f"out/push2_{tag}.json", "w"), indent=1)
print("DONE", tag)
