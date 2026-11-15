"""LP push (after rigid-realizations lp_push_880.py, rewritten for this system): move real charge
parameters so that a complex-conjugate pair of equilibria approaches the real, all-positive region,
while keeping existing physical equilibria apart. All numerical.

Normalised real parameters theta:
  n=3, D=2: p0=(0,0), p1=(1,0), p2=(a,b); q=(1, e^l1, e^l2)         theta=(a,b,l1,l2)
  n=4, D=3: p0=0, p1=(1,0,0), p2=(a,b,0), p3=(c,d,e); q=(1,e^l1,e^l2,e^l3)  theta=(a,b,c,d,e,l1,l2,l3)
Usage: python push.py n D start_spec n_starts seed out_tag [iters]
  start_spec: random | triangle | centre | file:<json with list of thetas>
"""
import sys, time, json
import numpy as np
from scipy.optimize import linprog
from cross_lib import F_J, newton, track, arc_path, param_jac, merge

n, D = int(sys.argv[1]), int(sys.argv[2])
spec, nstarts, seed, tag = sys.argv[3], int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
ITERS = int(sys.argv[7]) if len(sys.argv) > 7 else 150
rng = np.random.default_rng(seed)
base = np.load(f"out/mono_n{n}_D{D}_s1.npz")
Pb, qb, Sb = base["P"], base["q"], base["S"]
NS = len(Sb)
npos = 2 if D == 2 else 5
m = npos + n - 1


def theta_to_Pq(th):
    th = np.asarray(th, float)
    P = np.zeros((n, D))
    P[1, 0] = 1.0
    if D == 2:
        P[2] = th[0:2]
    else:
        P[2, :2] = th[0:2]
        P[3] = th[2:5]
    q = np.concatenate([[1.0], np.exp(th[npos:])])
    return P.astype(complex), q.astype(complex)


def dPq_dtheta(th):
    """Columns: d(P.flatten(), q)/d theta_j, shape (n*D+n, m)."""
    M = np.zeros((n * D + n, m))
    if D == 2:
        M[2 * D + 0, 0] = 1
        M[2 * D + 1, 1] = 1
    else:
        M[2 * D + 0, 0] = 1
        M[2 * D + 1, 1] = 1
        M[3 * D + 0, 2] = 1
        M[3 * D + 1, 3] = 1
        M[3 * D + 2, 4] = 1
    for j in range(n - 1):
        M[n * D + 1 + j, npos + j] = np.exp(th[npos + j])
    return M


def bc(P, q, B):
    return np.broadcast_to(P, (B, n, D)), np.broadcast_to(q, (B, n))


def move(Z, Pa, qa, Pb_, qb_, scale=0.3, tries=4):
    """Track all solutions from (Pa,qa) to (Pb_,qb_) along complex arcs; return Z or None."""
    for k in range(tries):
        Pm = scale * (rng.normal(size=Pa.shape) + 1j * rng.normal(size=Pa.shape)) * (np.abs(Pb_ - Pa).max() + 1e-3)
        qm = scale * (rng.normal(size=qa.shape) + 1j * rng.normal(size=qa.shape)) * (np.abs(qb_ - qa).max() + 1e-3)
        Pm[0] = 0
        Pm[1] = 0
        qm[0] = 0
        Zt, ok = track(Z, arc_path(Pa, qa, Pb_, qb_, Pm, qm), D)
        if not ok.all():
            continue
        Zt, err = newton(Zt, *bc(Pb_, qb_, len(Zt)), D)
        if err.max() > 1e-9:
            continue
        sep = min(np.max(np.abs(Zt[i] - Zt[j])) for i in range(len(Zt)) for j in range(i))
        if sep < 1e-6:
            continue
        return Zt
    return None


def classify(Z, tol=1e-9):
    imm = np.max(np.abs(Z.imag), axis=1) / (1 + np.max(np.abs(Z.real), axis=1))
    real = imm < tol
    phys = real & np.all(Z[:, D:].real > 0, axis=1)
    return real, phys, imm


def class_counts(Z):
    real, phys, imm = classify(Z)
    pats = {}
    for z in Z[real]:
        s = np.sign(z[D:].real)
        if s[0] < 0:
            s = -s
        k = "".join("+" if v > 0 else "-" for v in s)
        pats[k] = pats.get(k, 0) + 1
    return int(phys.sum()), int(real.sum()), pats


def target_value(z):
    """Distance of a non-real solution from the real, all-positive region (numerical)."""
    return float(np.sum(z.imag ** 2) + np.sum(np.minimum(z[D:].real, 0) ** 2))


def start_thetas():
    if spec == "random":
        out = []
        for _ in range(nstarts):
            if D == 2:
                th = [rng.uniform(-1, 2), rng.uniform(0.1, 2)] + list(rng.uniform(-4, 4, n - 1))
            else:
                th = [rng.uniform(-1, 2), rng.uniform(0.1, 2), rng.uniform(-1, 2), rng.uniform(-1.5, 1.5),
                      rng.uniform(0.05, 2)] + list(rng.uniform(-6, 3, n - 1))
            out.append(np.array(th))
        return out
    if spec == "triangle":
        th0 = np.array([0.5, np.sqrt(3) / 2, 0.0, 0.0])
    elif spec == "centre":
        th0 = np.array([0.5, np.sqrt(3) / 2, 0.5, np.sqrt(3) / 6, 0.0, 0.0, 0.0, -10 * np.log(2)])
    elif spec.startswith("file:"):
        return [np.array(t) for t in json.load(open(spec[5:]))][:nstarts]
    out = [th0]
    for _ in range(nstarts - 1):
        out.append(th0 + rng.normal(size=m) * np.concatenate([0.03 * np.ones(npos), 0.1 * np.ones(n - 1)]))
    return out


LO = np.array([-3, 0.02, -12, -12] if D == 2 else [-3, 0.02, -3, -3, -3] + [-16] * 3, float)
HI = np.array([4, 4, 12, 12] if D == 2 else [4, 4, 4, 3, 3] + [16] * 3, float)
TR0 = np.concatenate([0.05 * np.ones(npos), 0.2 * np.ones(n - 1)])

# reach a real starting point from the complex base
results = []
t_all = time.time()
for si, th in enumerate(start_thetas()):
    t0 = time.time()
    th = np.clip(th, LO, HI)
    P, q = theta_to_Pq(th)
    Z = move(Sb, Pb, qb, P, q, scale=0.5, tries=6)
    if Z is None:
        print(f"[{tag} start {si}] could not reach start", flush=True)
        results.append({"start": si, "theta0": th.tolist(), "status": "start_fail"})
        continue
    phys0, real0, pats0 = class_counts(Z)
    best = (phys0, th.copy())
    log = []
    stop = "iters"
    stuck = 0
    for it in range(ITERS):
        real, phys, imm = classify(Z)
        nphys = int(phys.sum())
        # candidate pairs: non-real solutions with Im of t_0 > 0 as representative
        nr = np.where(~real)[0]
        reps = [i for i in nr if Z[i, D:].real.sum() >= 0 and (Z[i].imag[np.argmax(np.abs(Z[i].imag))] > 0)]
        if not reps:
            stop = "no_nonreal"
            break
        T = np.array([target_value(Z[i]) for i in reps])
        order = np.argsort(T)
        # sensitivities
        Pbt, qbt = bc(P, q, len(Z))
        F, J = F_J(Z, Pbt, qbt, D)
        dFth = param_jac(Z, Pbt, qbt, D) @ dPq_dtheta(th)  # (NS, N, m)
        dZ = -np.linalg.solve(J, dFth)  # (NS, N, m) complex
        # constraints: physical solutions stay apart
        A_ub, b_ub = [], []
        ph = np.where(phys)[0]
        for ii in range(len(ph)):
            for jj in range(ii + 1, len(ph)):
                a, b = ph[ii], ph[jj]
                diff = (Z[a] - Z[b]).real
                Dab = float(diff @ diff)
                g = 2 * diff @ (dZ[a] - dZ[b]).real
                A_ub.append(-g)
                b_ub.append(0.35 * Dab)
        # also: physical solutions keep t bounded (stay away from sites): d t_i grows <= 30%
        for a in ph:
            for i in range(n):
                ti = Z[a, D + i].real
                A_ub.append(dZ[a, D + i].real / ti)
                b_ub.append(0.3)
        k = order[it % min(3, len(order))] if it % 4 != 3 else order[0]
        i0 = reps[k]
        z = Z[i0]
        gT = 2 * (z.imag @ dZ[i0].imag) + 2 * (np.minimum(z[D:].real, 0) @ dZ[i0, D:].real)
        accepted = False
        for shrink in [1, 0.4, 0.15, 0.05, 0.015]:
            tr = TR0 * shrink
            bounds = [(max(-tr[j], LO[j] - th[j]), min(tr[j], HI[j] - th[j])) for j in range(m)]
            res = linprog(gT / (np.linalg.norm(gT) + 1e-300), A_ub=np.array(A_ub) if A_ub else None,
                          b_ub=np.array(b_ub) if b_ub else None, bounds=bounds, method="highs")
            if not res.success:
                continue
            dth = res.x
            if np.linalg.norm(dth) < 1e-12:
                continue
            th2 = th + dth
            P2, q2 = theta_to_Pq(th2)
            Z2 = move(Z, P, q, P2, q2, scale=0.3, tries=2)
            if Z2 is None:
                continue
            real2, phys2, imm2 = classify(Z2)
            n2 = int(phys2.sum())
            reps2 = [i for i in np.where(~real2)[0]]
            Tmin_new = min([target_value(Z2[i]) for i in reps2], default=0.0)
            if n2 > nphys or (n2 == nphys and Tmin_new <= T.min() * (1 + 1e-9) + 1e-14) or \
                    (n2 == nphys and target_value(Z2[np.argmin([np.max(np.abs(Z2[j] - z)) for j in range(NS)])]) < T[k] * 0.999):
                if n2 > nphys:
                    print(f"*** [{tag} start {si} it {it}] physical {nphys} -> {n2}", flush=True)
                th, P, q, Z = th2, P2, q2, Z2
                accepted = True
                break
        Tmin = float(T.min())
        i_min = reps[order[0]]
        log.append([it, nphys, Tmin, float(np.max(np.abs(Z[i_min].imag))), float(np.min(Z[i_min, D:].real))])
        if nphys > best[0]:
            best = (nphys, th.copy())
        if n2 if accepted else False:
            pass
        if not accepted:
            stuck += 1
            if stuck >= 3:
                stop = "lp_stalled"
                break
        else:
            stuck = 0
    real, phys, imm = classify(Z)
    nphys, nreal, pats = class_counts(Z)
    reps = [i for i in np.where(~real)[0]]
    Tl = sorted((target_value(Z[i]), i) for i in reps)
    zc = Z[Tl[0][1]] if Tl else None
    diag = {}
    if zc is not None:
        diag = {"T": Tl[0][0], "max_im": float(np.max(np.abs(zc.imag))), "Re_t": zc[D:].real.tolist(),
                "Im_t": zc[D:].imag.tolist(), "x": [str(v) for v in zc[:D]], "abs_x": float(np.max(np.abs(zc[:D])))}
    at_bound = [j for j in range(m) if th[j] <= LO[j] + 1e-6 or th[j] >= HI[j] - 1e-6]
    rec = {"start": si, "theta0": start_thetas()[si].tolist() if spec != "random" else None,
           "phys0": phys0, "real0": real0, "pats0": pats0, "best_phys": best[0], "best_theta": best[1].tolist(),
           "final_phys": nphys, "final_real": nreal, "final_pats": pats, "final_theta": th.tolist(),
           "iters": len(log), "stop": stop, "nearest_pair": diag, "params_at_bound": at_bound,
           "T_first": log[0][2] if log else None, "T_last": log[-1][2] if log else None,
           "min_t_phys": float(Z[phys, D:].real.min()) if phys.any() else None, "secs": time.time() - t0}
    results.append(rec)
    print(f"[{tag} start {si}] phys {phys0}->{nphys} (best {best[0]}), real {real0}->{nreal} {pats}, "
          f"T {rec['T_first']:.3e}->{rec['T_last']:.3e}, stop {stop}, iters {len(log)}, at_bound {at_bound}, "
          f"{time.time()-t0:.0f}s", flush=True)
    json.dump(results, open(f"out/push_{tag}.json", "w"), indent=1)
    np.savez(f"out/push_{tag}_last.npz", Z=Z, theta=th)
print(f"DONE {tag}: {len(results)} starts, {time.time()-t_all:.0f}s")
