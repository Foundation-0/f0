"""Trust-region LP push of L2288 real count (search code).

State at a real parameter point: all 1144 solutions (one of each mirror pair, v10 above axis).
Real parameters p = (xC, yC, s_1..s_16); s_k squared lengths of non-triangle edges, scale lambda_{3,9} = 1.
Each iteration:
  * sensitivities dZ/dp for all solutions (one batched solve),
  * objective: sum over non-real conjugate pairs of grad(im2)/im2 (log of squared imaginary part),
    optionally restricted to the k most nearly-real pairs,
  * constraints: the closest real pairs may shrink their squared distance by at most a fraction beta,
    and lengths stay inside a box,
  * LP in a box trust region; move with a complex detour arc, accept if the real count does not drop
    and the objective improves (or the count rises).
Usage: python push.py start.npz tag seconds [k_target] [box]
"""
import sys, time
import numpy as np
from scipy.optimize import linprog
from monodromy import make, robust_solve

L, N = make("l2288")
base = np.load("l2288_generic.npz"); S0, P0 = base["Z"], base["P"]
f = L.f


def p_to_P(p):
    P = np.zeros(L.nP, complex)
    P[0] = p[0] + 1j * p[1]; P[1] = p[0] - 1j * p[1]; P[2:] = p[2:]
    return P


def P_to_p(P):
    return np.concatenate([[P[0].real, P[0].imag], P[2:].real])


def lengths(p):
    return L.lengths_from_real_params(p_to_P(p))


def full_solve(p, rng=None):
    Z, good = robust_solve(L, S0, P0, p_to_P(p))
    return Z, np.full(len(Z), good)


def local_move(Z, p, q, rng):
    P1, P2 = p_to_P(p), p_to_P(q)
    for attempt in range(3):
        G = 0.4j * max(np.abs(P2 - P1).max(), 1e-9) * rng.uniform(-1, 1, size=L.nP)
        # keep the detour conjugation-free: G must not be real-structured; random imaginary is fine
        Zn, ok, _ = L.track(Z, P1, P2, G=G, h0=0.25, hmax=0.5, tol_rel=1e-5, hmin=1e-12, max_iter=5000)
        if ok.all() and L.min_sep(Zn)[0] > 1e-8:
            return Zn, True
    return Zn, False


def analyse(Z):
    X = 0.5 * (Z[:, :f] + Z[:, f:]); Y = -0.5j * (Z[:, :f] - Z[:, f:])
    imm = np.maximum(np.abs(X.imag), np.abs(Y.imag)).max(axis=1)
    real = imm < 1e-8
    im2 = (X.imag ** 2 + Y.imag ** 2).sum(axis=1)
    return X, Y, real, im2


def sensitivities(Z, P):
    Jz, D = L.dFdP(Z, P)
    # real parameter directions: xC -> (1, 1, 0..), yC -> (i, -i, 0..), s_k
    Dr = np.empty((Z.shape[0], L.m, 2 + L.m), complex)
    Dr[:, :, 0] = D[:, :, 0] + D[:, :, 1]
    Dr[:, :, 1] = 1j * D[:, :, 0] - 1j * D[:, :, 1]
    Dr[:, :, 2:] = D[:, :, 2:]
    dZ = -np.linalg.solve(Jz, Dr)
    dX = 0.5 * (dZ[:, :f] + dZ[:, f:]); dY = -0.5j * (dZ[:, :f] - dZ[:, f:])
    return dX, dY


def pair_reps(Z, real):
    idx = np.where(~real)[0]
    if len(idx) == 0:
        return np.array([], int)
    C = L.conj_partner(Z[idx])
    reps = []
    seen = set()
    for a, c in zip(idx, C):
        if a in seen:
            continue
        j = idx[np.abs(Z[idx] - c).max(axis=1).argmin()]
        seen.add(a); seen.add(j); reps.append(a)
    return np.array(reps)


def run(start, tag, seconds, k_target=0, box=(0.9, 1.1), beta=0.3, seed=0):
    rng = np.random.default_rng(seed)
    d = np.load(start)
    p = P_to_p(d["P"])
    Z, ok = full_solve(p)
    assert ok.all(), "start solve incomplete"
    X, Y, real, im2 = analyse(Z)
    nr = int(real.sum())
    best = (nr, Z.copy(), p.copy())
    hist = [(0.0, 2 * nr)]
    t0 = time.time()
    print(f"[{tag}] start real {2*nr}/2288, minsep {L.min_sep(Z)[0]:.2e}", flush=True)
    tr = 2e-3
    stall = 0
    it = 0
    while time.time() - t0 < seconds:
        it += 1
        X, Y, real, im2 = analyse(Z)
        nr = int(real.sum())
        if nr == N:
            print(f"[{tag}] ALL REAL", flush=True); break
        P = p_to_P(p)
        dX, dY = sensitivities(Z, P)
        reps = pair_reps(Z, real)
        order = reps[np.argsort(im2[reps])]
        tgt = order if k_target <= 0 else order[:k_target]
        G = []
        for r in tgt:
            g = 2 * (X[r].imag[:, None] * dX[r].imag + Y[r].imag[:, None] * dY[r].imag).sum(axis=0)
            G.append(g / im2[r])
        G = np.array(G)
        c = G.sum(axis=0)
        # separation constraints among the closest real solutions
        ri = np.where(real)[0]
        Xr = np.concatenate([X[ri].real, Y[ri].real], axis=1)
        D2 = ((Xr[:, None, :] - Xr[None, :, :]) ** 2).sum(axis=2)
        iu, ju = np.triu_indices(len(ri), 1)
        dd = D2[iu, ju]
        close = np.argsort(dd)[:200]
        A = []; b = []
        dXr = np.concatenate([dX[ri].real, dY[ri].real], axis=1)  # (nr, 2f, np)
        for ci in close:
            a_, b_ = iu[ci], ju[ci]
            diff = Xr[a_] - Xr[b_]
            h = 2 * diff @ (dXr[a_] - dXr[b_])
            A.append(-h); b.append(beta * dd[ci])
        # lengths box (via s and triangle coordinates kept near current)
        lam = lengths(p)
        A = np.array(A); b = np.array(b)
        lo = np.full(len(p), -tr); hi = np.full(len(p), tr)
        s = p[2:]
        lo[2:] = np.maximum(lo[2:], box[0] ** 2 - s); hi[2:] = np.minimum(hi[2:], box[1] ** 2 - s)
        accepted = False
        for trs in (1.0, 0.4, 0.15, 0.05):
            res = linprog(c, A_ub=A, b_ub=b, bounds=list(zip(lo * trs, hi * trs)), method="highs")
            if not res.success:
                continue
            q = p + res.x
            Zn, okm = local_move(Z, p, q, rng)
            if not okm:
                Zn, okf = full_solve(q, rng)
                if not (okf.all() and L.min_sep(Zn)[0] > 1e-8):
                    continue
            Xn, Yn, realn, im2n = analyse(Zn)
            nrn = int(realn.sum())
            obj_old = np.log(im2[~real]).sum() / 2 if (~real).any() else 0
            reps_n = pair_reps(Zn, realn)
            if nrn > nr or (nrn == nr and np.log(im2n[reps_n]).sum() < np.log(im2[reps]).sum() - 1e-6):
                accepted = True
                Z, p = Zn, q
                if nrn > nr:
                    print(f"[{tag}] it {it} ({time.time()-t0:.0f}s): real {2*nr} -> {2*nrn}, tr {tr*trs:.1e}, "
                          f"minsep {L.min_sep(Zn)[0]:.1e}", flush=True)
                if nrn > best[0]:
                    best = (nrn, Z.copy(), p.copy()); hist.append((time.time() - t0, 2 * nrn))
                    np.savez(f"push_{tag}_best.npz", Z=Z, P=p_to_P(p), p=p, lam=lengths(p), nreal=nrn,
                             hist=np.array(hist))
                break
        if accepted:
            tr = min(tr * 1.3, 2e-2); stall = 0
        else:
            tr *= 0.5; stall += 1
            if it % 1 == 0:
                print(f"[{tag}] it {it}: no step, tr -> {tr:.1e}, real {2*nr}", flush=True)
            if tr < 1e-7:
                print(f"[{tag}] trust region collapsed", flush=True); break
        if it % 10 == 0:
            reps = pair_reps(Z, analyse(Z)[2])
            print(f"[{tag}] it {it} ({time.time()-t0:.0f}s) real {2*int(analyse(Z)[2].sum())} best {2*best[0]} "
                  f"smallest pair im2 {np.sort(analyse(Z)[3][reps])[:4]}", flush=True)
    np.savez(f"push_{tag}_best.npz", Z=best[1], P=p_to_P(best[2]), p=best[2], lam=lengths(best[2]),
             nreal=best[0], hist=np.array(hist))
    np.savez(f"push_{tag}_last.npz", Z=Z, P=p_to_P(p), p=p, lam=lengths(p))
    print(f"[{tag}] done best {2*best[0]}", flush=True)


if __name__ == "__main__":
    start, tag, secs = sys.argv[1], sys.argv[2], float(sys.argv[3])
    k = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    bw = float(sys.argv[5]) if len(sys.argv) > 5 else 0.1
    run(start, tag, secs, k_target=k, box=(1 - bw, 1 + bw))
