"""Trust-region LP push, version 2 (search code).

Differences from push.py: the trust region is relative to the current distance eps from the all-unit
point (the real count is close to a function of the direction of the perturbation only), the objective
targets the k most nearly-real conjugate pairs, and when the multi-pair LP gives nothing it tries
single-pair LPs (drive one pair to its wall, overshoot, keep close real pairs apart).
Usage: python push2.py start.npz tag seconds [k_target] [beta]
"""
import sys, time
import numpy as np
from scipy.optimize import linprog
from push import L, N, f, p_to_P, P_to_p, lengths, full_solve, local_move, analyse, sensitivities, pair_reps

PU = np.concatenate([[0.5, np.sqrt(3) / 2], np.ones(16)])


def constraints(X, Y, real, dX, dY, beta, nclose=250):
    ri = np.where(real)[0]
    Xr = np.concatenate([X[ri].real, Y[ri].real], axis=1)
    D2 = ((Xr[:, None, :] - Xr[None, :, :]) ** 2).sum(axis=2)
    iu, ju = np.triu_indices(len(ri), 1)
    dd = D2[iu, ju]
    close = np.argsort(dd)[:nclose]
    dXr = np.concatenate([dX[ri].real, dY[ri].real], axis=1)
    a, b = iu[close], ju[close]
    diff = Xr[a] - Xr[b]
    H = 2 * np.einsum("ij,ijk->ik", diff, dXr[a] - dXr[b])
    return -H, beta * dd[close], dd[close].min()


MAXIM = [np.inf]


def try_step(Z, p, q, nr, obj, rng):
    Zn, okm = local_move(Z, p, q, rng)
    if not okm:
        return None
    Xn, Yn, realn, im2n = analyse(Zn)
    nrn = int(realn.sum())
    repn = pair_reps(Zn, realn)
    objn = np.log(im2n[repn]).sum() if len(repn) else -np.inf
    if len(repn) and im2n[repn].max() > MAXIM[0]:
        return None
    return Zn, nrn, objn


def run(start, tag, seconds, k_target=30, beta=0.3, seed=0, mono=False):
    rng = np.random.default_rng(seed)
    d = np.load(start)
    p = d["p"] if "p" in d else P_to_p(d["P"])
    if "Z" in d and len(d["Z"]) == N and L.min_sep(d["Z"])[0] > 1e-8 and np.abs(L.F(d["Z"], p_to_P(p))).max() < 1e-9:
        Z = d["Z"]
    else:
        Z, ok = full_solve(p); assert ok.all()
    X, Y, real, im2 = analyse(Z)
    nr = int(real.sum())
    best = (nr, Z.copy(), p.copy()); hist = [(0.0, 2 * nr)]
    t0 = time.time()
    print(f"[{tag}] start real {2*nr}, eps {np.abs(p-PU).max():.2e}", flush=True)
    tau = 0.05
    it = 0
    while time.time() - t0 < seconds:
        it += 1
        X, Y, real, im2 = analyse(Z)
        nr = int(real.sum())
        if nr == N:
            print(f"[{tag}] ALL REAL", flush=True); break
        eps = np.abs(p - PU).max()
        dX, dY = sensitivities(Z, p_to_P(p))
        reps = pair_reps(Z, real)
        order = reps[np.argsort(im2[reps])]
        obj = np.log(im2[reps]).sum()
        A, b, dmin = constraints(X, Y, real, dX, dY, beta)
        grads = {}
        for r in order:
            g = 2 * (X[r].imag[:, None] * dX[r].imag + Y[r].imag[:, None] * dY[r].imag).sum(axis=0)
            grads[r] = g
        tgt = order[:k_target]
        c = sum(grads[r] / im2[r] for r in tgt)
        if mono:  # no non-real pair may get deeper (linearised)
            A = np.vstack([A] + [grads[r][None, :] for r in order]); b = np.concatenate([b, np.zeros(len(order))])
        maxim = im2[reps].max() if len(reps) else 0.0
        MAXIM[0] = 1.5 * maxim if mono else np.inf
        accepted = None
        for trs in (1.0, 0.3, 0.1):
            tr = tau * trs * eps
            res = linprog(c, A_ub=A, b_ub=b, bounds=[(-tr, tr)] * len(p), method="highs")
            if not res.success or np.abs(res.x).max() == 0:
                continue
            out = try_step(Z, p, p + res.x, nr, obj, rng)
            if out and (out[1] > nr or (out[1] == nr and out[2] < obj - 1e-6)):
                accepted = (out, p + res.x, f"LP tr {tr:.1e}")
                break
        if accepted is None:
            # single-pair pushes toward the wall, nearest pairs first
            for r in order[:8]:
                g = grads[r]
                dist = im2[r] / max(np.linalg.norm(g, 1), 1e-300)
                for over in (2.0, 5.0):
                    tr = min(over * dist * 3, tau * eps)
                    res = linprog(g, A_ub=A, b_ub=b, bounds=[(-tr, tr)] * len(p), method="highs")
                    if not res.success:
                        continue
                    out = try_step(Z, p, p + res.x, nr, obj, rng)
                    if out and out[1] > nr:
                        accepted = (out, p + res.x, f"pair LP tr {tr:.1e}")
                        break
                if accepted:
                    break
        if accepted:
            (Zn, nrn, objn), q, how = accepted
            if nrn > nr:
                print(f"[{tag}] it {it} ({time.time()-t0:.0f}s): real {2*nr} -> {2*nrn} via {how}, eps {np.abs(q-PU).max():.1e}, "
                      f"min real d2 {dmin:.1e}", flush=True)
            Z, p = Zn, q
            tau = min(tau * 1.5, 0.5)
            if nrn > best[0]:
                best = (nrn, Z.copy(), p.copy()); hist.append((time.time() - t0, 2 * nrn))
                np.savez(f"push2_{tag}_best.npz", Z=Z, P=p_to_P(p), p=p, lam=lengths(p), nreal=nrn, hist=np.array(hist))
        else:
            tau *= 0.4
            print(f"[{tag}] it {it} ({time.time()-t0:.0f}s): no step, tau -> {tau:.1e}, real {2*nr}, pairs {len(reps)}, "
                  f"min im2 {im2[order[0]]:.1e}, min real d2 {dmin:.1e}", flush=True)
            if tau < 1e-4:
                print(f"[{tag}] stuck", flush=True); break
    np.savez(f"push2_{tag}_best.npz", Z=best[1], P=p_to_P(best[2]), p=best[2], lam=lengths(best[2]), nreal=best[0], hist=np.array(hist))
    np.savez(f"push2_{tag}_last.npz", Z=Z, P=p_to_P(p), p=p, lam=lengths(p))
    print(f"[{tag}] done best {2*best[0]} after {time.time()-t0:.0f}s", flush=True)
    return best


if __name__ == "__main__":
    start, tag, secs = sys.argv[1], sys.argv[2], float(sys.argv[3])
    k = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    beta = float(sys.argv[5]) if len(sys.argv) > 5 else 0.3
    mono = len(sys.argv) > 6 and sys.argv[6] == "mono"
    run(start, tag, secs, k_target=k, beta=beta, mono=mono)
