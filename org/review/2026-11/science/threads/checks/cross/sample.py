"""Random real configurations: track all complex solutions, record physical count, real counts by
sign class, and the distance T of each non-real pair from the real all-positive region. Numerical.
Usage: python sample.py n D count seed tag"""
import sys, json, time
import numpy as np
from cross_lib import F_J, newton, track, arc_path

n, D, cnt, seed, tag = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
rng = np.random.default_rng(seed)
base = np.load(f"out/mono_n{n}_D{D}_s1.npz")
Pb, qb, Sb = base["P"], base["q"], base["S"]
npos = 2 if D == 2 else 5


def theta_to_Pq(th):
    P = np.zeros((n, D)); P[1, 0] = 1.0
    if D == 2:
        P[2] = th[0:2]
    else:
        P[2, :2] = th[0:2]; P[3] = th[2:5]
    return P.astype(complex), np.concatenate([[1.0], np.exp(th[npos:])]).astype(complex)


def move(Z, Pa, qa, P2, q2, scale=0.4, tries=5):
    for _ in range(tries):
        Pm = scale * (rng.normal(size=Pa.shape) + 1j * rng.normal(size=Pa.shape)) * (np.abs(P2 - Pa).max() + 1e-3)
        qm = scale * (rng.normal(size=qa.shape) + 1j * rng.normal(size=qa.shape)) * (np.abs(q2 - qa).max() + 1e-3)
        Pm[:2] = 0; qm[0] = 0
        Zt, ok = track(Z, arc_path(Pa, qa, P2, q2, Pm, qm), D)
        if not ok.all():
            continue
        Zt, err = newton(Zt, np.broadcast_to(P2, (len(Zt), n, D)), np.broadcast_to(q2, (len(Zt), n)), D)
        if err.max() > 1e-9:
            continue
        sep = min(np.max(np.abs(Zt[i] - Zt[j])) for i in range(len(Zt)) for j in range(i))
        if sep < 1e-6:
            continue
        return Zt
    return None


rows = []
Z, P, q = Sb, Pb, qb
t0 = time.time()
for k in range(cnt):
    if D == 2:
        th = np.array([rng.uniform(-1, 2), np.exp(rng.uniform(np.log(0.02), np.log(3)))] + list(rng.uniform(-6, 6, n - 1)))
    else:
        th = np.array([rng.uniform(-1, 2), np.exp(rng.uniform(np.log(0.05), np.log(2))), rng.uniform(-1, 2),
                       rng.uniform(-1.5, 1.5), np.exp(rng.uniform(np.log(0.02), np.log(2)))] + list(rng.uniform(-8, 4, n - 1)))
    P2, q2 = theta_to_Pq(th)
    Z2 = move(Z, P, q, P2, q2)
    if Z2 is None:
        continue
    Z, P, q = Z2, P2, q2
    imm = np.max(np.abs(Z.imag), axis=1) / (1 + np.max(np.abs(Z.real), axis=1))
    real = imm < 1e-9
    phys = real & np.all(Z[:, D:].real > 0, axis=1)
    pats = {}
    for z in Z[real]:
        s = np.sign(z[D:].real); s = -s if s[0] < 0 else s
        key = "".join("+" if v > 0 else "-" for v in s); pats[key] = pats.get(key, 0) + 1
    # non-real: one rep per quadruple {z, conj z, -z, -conj z}
    T_all, T_pos = [], []
    for z in Z[~real]:
        if z[D:].real.sum() < 0:
            continue
        if z.imag[np.argmax(np.abs(z.imag))] < 0:
            continue
        T_all.append(float(np.sum(z.imag ** 2) + np.sum(np.minimum(z[D:].real, 0) ** 2)))
        if np.all(z[D:].real > 0):
            T_pos.append(float(np.sum(z.imag ** 2)))
    rows.append({"theta": th.tolist(), "phys": int(phys.sum()), "real": int(real.sum()), "pats": pats,
                 "T_all": sorted(T_all)[:5], "T_pos": sorted(T_pos)[:5], "n_pos_pairs": len(T_pos)})
    if k % 50 == 0:
        print(k, rows[-1]["phys"], f"{time.time()-t0:.0f}s", flush=True)
json.dump(rows, open(f"out/sample_{tag}.json", "w"))
ph = [r["phys"] for r in rows]
print("DONE", tag, len(rows), {v: ph.count(v) for v in sorted(set(ph))})
