"""Search pipeline for the 12-vertex graph (edge frame): solve, LP push (trust region relative to the distance
from unit lengths), multistart, deep-pair-first, single-pair final moves.  Search code, not proof code.
Commands:
  python push12.py push   start.npz tag seconds [mono]
  python push12.py ms     seed n_starts seconds_each eps
  python push12.py deep   state.npz tag n_deep phase1_s climb_s
  python push12.py single state.npz tag
  python push12.py scale  state.npz kappa tag seconds
"""
import sys, time, os, json
import numpy as np
from scipy.optimize import linprog
from mono12 import make
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from monodromy import _distinct

L, N = make()
f = L.f
HERE = os.path.dirname(os.path.abspath(__file__))
_b = np.load(os.path.join(HERE, "g12_generic.npz")); S0, P0 = _b["Z"], _b["P"]
PU = np.ones(L.m)


def full_solve(p, rounds=6, seed=5, tol_rel=1e-6):
    P1 = p.astype(complex); rng = np.random.default_rng(seed)
    Z, ok, _ = L.track(S0, P0, P1, tol_rel=tol_rel, hmin=1e-14, max_iter=30000)
    sol = _distinct(Z[ok])
    for _ in range(rounds):
        if len(sol) >= N:
            break
        G = 0.3j * np.abs(P1 - P0) * rng.uniform(-1, 1, size=L.nP)
        Zb, okb, _ = L.track(S0, P0, P1, G=G, tol_rel=tol_rel, hmin=1e-15, max_iter=60000)
        sol = _distinct(np.vstack([sol, Zb[okb]]))
    good = len(sol) == N and L.min_sep(sol)[0] > 1e-8
    return sol, good


def local_move(Z, p, q, rng):
    P1, P2 = p.astype(complex), q.astype(complex)
    for attempt in range(2):
        G = 0.4j * max(np.abs(P2 - P1).max(), 1e-12) * rng.uniform(-1, 1, size=L.nP)
        Zn, ok, _ = L.track(Z, P1, P2, G=G, h0=0.25, hmax=0.5, tol_rel=1e-5, hmin=1e-12, max_iter=5000)
        if ok.all() and L.min_sep(Zn)[0] > 1e-8:
            return Zn, True
    return Zn, False


def analyse(Z):
    X = 0.5 * (Z[:, :f] + Z[:, f:]); Y = -0.5j * (Z[:, :f] - Z[:, f:])
    imm = np.maximum(np.abs(X.imag), np.abs(Y.imag)).max(axis=1)
    return X, Y, imm < 1e-8, (X.imag ** 2 + Y.imag ** 2).sum(axis=1)


def sensitivities(Z, p):
    Fv, Jz, _, _ = L.FJ(Z, p.astype(complex))
    dZ = np.linalg.inv(Jz)  # dF/ds = -I  =>  dZ/ds = J^{-1}
    return 0.5 * (dZ[:, :f] + dZ[:, f:]), -0.5j * (dZ[:, :f] - dZ[:, f:])


def pair_reps(Z, real):
    idx = np.where(~real)[0]
    if len(idx) == 0:
        return np.array([], int)
    C = L.conj_partner(Z[idx]); seen = set(); reps = []
    for a, c in zip(idx, C):
        if a in seen:
            continue
        j = idx[np.abs(Z[idx] - c).max(axis=1).argmin()]
        seen.add(a); seen.add(j); reps.append(a)
    return np.array(reps)


def closest_pairs(R, k, block=1024):
    sq = (R ** 2).sum(axis=1); cand = []
    for i in range(0, len(R), block):
        G = sq[i:i + block, None] + sq[None, :] - 2 * R[i:i + block] @ R.T
        rows = np.arange(i, min(i + block, len(R)))
        G[:, :i + block] = np.where(np.arange(len(R))[None, :i + block] <= rows[:, None], np.inf, G[:, :i + block])
        flat = np.argpartition(G.ravel(), min(k, G.size - 1))[:k]
        a, b = np.unravel_index(flat, G.shape)
        cand += list(zip(G[a, b], rows[a], b))
    cand.sort()
    return cand[:k]


def constraints(X, Y, real, dX, dY, beta, nclose=300):
    ri = np.where(real)[0]
    R = np.concatenate([X[ri].real, Y[ri].real], axis=1)
    cp = closest_pairs(R, nclose)
    dR = np.concatenate([dX[ri].real, dY[ri].real], axis=1)
    A = []; b = []
    for d2, a, c in cp:
        diff = R[a] - R[c]
        A.append(-2 * diff @ (dR[a] - dR[c])); b.append(beta * max(d2, 0.0))
    return np.array(A), np.array(b), cp[0][0]


MAXIM = [np.inf]


def try_step(Z, p, q, rng):
    Zn, ok = local_move(Z, p, q, rng)
    if not ok:
        return None
    Xn, Yn, rn, im2n = analyse(Zn); repn = pair_reps(Zn, rn)
    if len(repn) and im2n[repn].max() > MAXIM[0]:
        return None
    return Zn, int(rn.sum()), (np.log(im2n[repn]).sum() if len(repn) else -np.inf)


def save(fn, Z, p, nreal, hist=None):
    np.savez(fn, Z=Z, p=p, P=p.astype(complex), lam=L.lengths_from_real_params(p), nreal=nreal,
             hist=np.array(hist if hist else []))


def run(start, tag, seconds, k_target=30, beta=0.3, mono=False, seed=0, rmin=0.0):
    rng = np.random.default_rng(seed)
    d = np.load(start); Z, p = d["Z"], d["p"]
    X, Y, real, im2 = analyse(Z); nr = int(real.sum())
    best = (nr, Z.copy(), p.copy()); hist = [(0.0, nr)]
    t0 = time.time(); tau = 0.05; it = 0
    print(f"[{tag}] start real {nr}/{N}, eps {np.abs(p-PU).max():.2e}", flush=True)
    while time.time() - t0 < seconds:
        it += 1
        X, Y, real, im2 = analyse(Z); nr = int(real.sum())
        if nr == N:
            print(f"[{tag}] ALL REAL", flush=True); break
        eps = np.abs(p - PU).max()
        dX, dY = sensitivities(Z, p)
        reps = pair_reps(Z, real); order = reps[np.argsort(im2[reps])]
        obj = np.log(im2[reps]).sum()
        A, b, dmin = constraints(X, Y, real, dX, dY, beta)
        grads = {r: 2 * (X[r].imag[:, None] * dX[r].imag + Y[r].imag[:, None] * dY[r].imag).sum(axis=0) for r in order}
        c = sum(grads[r] / im2[r] for r in order[:k_target])
        A2, b2 = A, b
        if mono:
            A2 = np.vstack([A] + [grads[r][None] for r in order]); b2 = np.concatenate([b, np.zeros(len(order))])
        MAXIM[0] = 1.5 * im2[reps].max() if mono else np.inf
        if rmin > 0:  # keep the perturbation from shrinking below rmin (2-norm), along the current direction
            dev = p - PU; nd_ = np.linalg.norm(dev)
            A2 = np.vstack([A2, -dev[None] / nd_]); b2 = np.concatenate([b2, [nd_ - rmin]])
        acc = None
        for trs in (1.0, 0.3, 0.1):
            tr = tau * trs * eps
            res = linprog(c, A_ub=A2, b_ub=b2, bounds=[(-tr, tr)] * len(p), method="highs")
            if not res.success or np.abs(res.x).max() == 0:
                continue
            out = try_step(Z, p, p + res.x, rng)
            if out and (out[1] > nr or (out[1] == nr and out[2] < obj - 1e-6)):
                acc = (out, p + res.x, f"LP tr {tr:.1e}"); break
        if acc is None:
            for r in order[:4]:
                g = grads[r]; dist = im2[r] / max(np.linalg.norm(g, 1), 1e-300)
                for over in (2.0, 8.0):
                    tr = max(over * dist, 1e-12)
                    res = linprog(g, A_ub=A, b_ub=b, bounds=[(-tr, tr)] * len(p), method="highs")
                    if not res.success:
                        continue
                    out = try_step(Z, p, p + res.x, rng)
                    if out and out[1] > nr:
                        acc = (out, p + res.x, f"pair LP tr {tr:.1e}"); break
                if acc:
                    break
        if acc:
            (Zn, nrn, objn), q, how = acc
            if nrn > nr:
                print(f"[{tag}] it {it} ({time.time()-t0:.0f}s): real {nr} -> {nrn} via {how}, eps {np.abs(q-PU).max():.1e}, min real d2 {dmin:.1e}", flush=True)
            Z, p = Zn, q; tau = min(tau * 1.5, 0.5)
            if nrn > best[0]:
                best = (nrn, Z.copy(), p.copy()); hist.append((time.time() - t0, nrn))
                save(f"push12_{tag}_best.npz", Z, p, nrn, hist)
        else:
            tau *= 0.4
            print(f"[{tag}] it {it} ({time.time()-t0:.0f}s): no step, tau {tau:.1e}, real {nr}, pairs {len(reps)}, min im2 {im2[order[0]]:.1e}, max im2 {im2[order[-1]]:.1e}, min real d2 {dmin:.1e}", flush=True)
            if tau < 1e-7:
                print(f"[{tag}] stuck", flush=True); break
    save(f"push12_{tag}_best.npz", best[1], best[2], best[0], hist)
    save(f"push12_{tag}_last.npz", Z, p, int(analyse(Z)[2].sum()))
    print(f"[{tag}] done best {best[0]} after {time.time()-t0:.0f}s", flush=True)
    return best


def multistart(seed, n, secs, eps, rmin=0.0):
    rng = np.random.default_rng(seed); out = []
    for k in range(n):
        p = PU + eps * rng.uniform(0, 1, L.m)
        Z, ok = full_solve(p)
        if not ok:
            print(f"[ms{seed}.{k}] start solve incomplete ({len(Z)}), skip", flush=True); continue
        fn = f"ms12_{seed}_{k}_start.npz"; save(fn, Z, p, int(analyse(Z)[2].sum()))
        b = run(fn, f"ms{seed}.{k}", secs, seed=k, rmin=rmin)
        out.append(dict(k=k, start=int(analyse(Z)[2].sum()), best=b[0]))
        json.dump(out, open(f"ms12_{seed}_summary.json", "w"))
        print(f"[ms{seed}.{k}] start {out[-1]['start']} -> best {b[0]}", flush=True)


def deep(state, tag, nd, t1, t2):
    d = np.load(state); Z, p = d["Z"], d["p"]
    X, Y, real, im2 = analyse(Z); reps = pair_reps(Z, real)
    tg = list(reps[np.argsort(im2[reps])[::-1][:nd]])
    print(f"[{tag}] start real {int(real.sum())}, targets im2 {im2[tg]}", flush=True)
    rng = np.random.default_rng(0); tau = 0.05; t0 = time.time()
    while time.time() - t0 < t1:
        X, Y, real, im2 = analyse(Z)
        live = [r for r in tg if not real[r]]
        if not live:
            print(f"[{tag}] all targets real, count {int(real.sum())}", flush=True); break
        eps = np.abs(p - PU).max(); dX, dY = sensitivities(Z, p)
        c = sum(2 * (X[r].imag[:, None] * dX[r].imag + Y[r].imag[:, None] * dY[r].imag).sum(axis=0) / im2[r] for r in live)
        tr = tau * eps
        res = linprog(c, bounds=[(-tr, tr)] * len(p), method="highs")
        q = p + res.x
        Zq, ok = local_move(Z, p, q, rng)
        if ok:
            Xq, Yq, rq, im2q = analyse(Zq)
            if sum(np.log(max(im2q[r], 1e-30)) for r in live) < sum(np.log(im2[r]) for r in live) or any(rq[r] for r in live):
                Z, p = Zq, q; tau = min(tau * 1.5, 0.5)
                print(f"[{tag}] ({time.time()-t0:.0f}s) target im2 {np.round(im2q[live], 4)}, real {int(rq.sum())}", flush=True)
                continue
        tau *= 0.5
        if tau < 1e-5:
            print(f"[{tag}] phase 1 stuck", flush=True); break
    fn = f"deep12_{tag}_mid.npz"; save(fn, Z, p, int(analyse(Z)[2].sum()))
    return run(fn, tag, t2, mono=True)


def single(state, tag):
    """Single-pair LP moves with a range of trust radii and dropped constraints; save the best result."""
    d = np.load(state); Z, p = d["Z"], d["p"]
    X, Y, real, im2 = analyse(Z); reps = pair_reps(Z, real); nr = int(real.sum())
    dX, dY = sensitivities(Z, p)
    A, b, _ = constraints(X, Y, real, dX, dY, 0.3, nclose=400)
    rng = np.random.default_rng(0); best = (nr, Z, p)
    for r in reps[np.argsort(im2[reps])][:12]:
        g = 2 * (X[r].imag[:, None] * dX[r].imag + Y[r].imag[:, None] * dY[r].imag).sum(axis=0)
        for K in (0, 1, 2):
            for tr in (1e-8, 1e-7, 1e-6, 1e-5, 1e-4):
                res = linprog(g, A_ub=A[K:], b_ub=b[K:], bounds=[(-tr, tr)] * len(p), method="highs")
                if not res.success:
                    continue
                Zq, ok = local_move(Z, p, p + res.x, rng)
                if not ok:
                    continue
                n2 = int(analyse(Zq)[2].sum())
                print(f"[{tag}] pair {r} K {K} tr {tr:.0e}: real {n2}", flush=True)
                if n2 > best[0]:
                    best = (n2, Zq, p + res.x); save(f"single12_{tag}_best.npz", Zq, p + res.x, n2)
    print(f"[{tag}] best {best[0]}", flush=True)
    return best


def scale(state, kappa, tag, secs):
    d = np.load(state); Z, p = d["Z"], d["p"]; rng = np.random.default_rng(0); k = 1.0
    while k < kappa:
        k2 = min(2 * k, kappa); q = PU + (k2 / k) * (p - PU)
        Z, ok = local_move(Z, p, q, rng)
        if not ok:
            raise SystemExit("scale move failed")
        p, k = q, k2
        print(f"[{tag}] x{k}: real {int(analyse(Z)[2].sum())}", flush=True)
    fn = f"scaled12_{tag}.npz"; save(fn, Z, p, int(analyse(Z)[2].sum()))
    return run(fn, tag, secs, mono=False, rmin=0.7 * np.linalg.norm(p - PU))


if __name__ == "__main__":
    cmd = sys.argv[1]; a = sys.argv[2:]
    if cmd == "push":
        run(a[0], a[1], float(a[2]), mono=len(a) > 3 and a[3] == "mono", rmin=float(a[4]) if len(a) > 4 else 0.0)
    elif cmd == "ms":
        multistart(int(a[0]), int(a[1]), float(a[2]), float(a[3]), float(a[4]) if len(a) > 4 else 0.0)
    elif cmd == "deep":
        deep(a[0], a[1], int(a[2]), float(a[3]), float(a[4]))
    elif cmd == "single":
        single(a[0], a[1])
    elif cmd == "scale":
        scale(a[0], float(a[1]), a[2], float(a[3]))
