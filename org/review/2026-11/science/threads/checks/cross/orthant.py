"""For a list of real configurations: count physical equilibria and the non-real conjugate pairs whose
Re t lies in the positive orthant, and decompose the nearest pair's distance T = |Im z|^2 + |neg Re t|^2.
Numerical. Usage: python orthant.py n D thetas.json tag"""
import sys, json, collections
import numpy as np
from cross_lib import track, arc_path, newton

n, D = int(sys.argv[1]), int(sys.argv[2])
thetas = [np.array(t) for t in json.load(open(sys.argv[3]))]
tag = sys.argv[4]
rng = np.random.default_rng(3)
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


rows = []
for th in thetas:
    P, q = theta_to_Pq(th)
    Z = None
    for _ in range(6):
        Pm = 0.5 * (rng.normal(size=P.shape) + 1j * rng.normal(size=P.shape)); Pm[:2] = 0
        qm = 0.5 * (rng.normal(size=q.shape) + 1j * rng.normal(size=q.shape)); qm[0] = 0
        Zt, ok = track(Sb, arc_path(Pb, qb, P, q, Pm, qm), D)
        if not ok.all():
            continue
        Zt, err = newton(Zt, np.broadcast_to(P, (len(Zt), n, D)), np.broadcast_to(q, (len(Zt), n)), D)
        dd = np.max(np.abs(Zt[:, None] - Zt[None]), axis=2); np.fill_diagonal(dd, 1)
        if err.max() < 1e-9 and dd.min() > 1e-6:
            Z = Zt; break
    if Z is None:
        continue
    imm = np.max(np.abs(Z.imag), axis=1) / (1 + np.max(np.abs(Z.real), axis=1))
    real = imm < 1e-9
    phys = int((real & np.all(Z[:, D:].real > 0, axis=1)).sum())
    reps = [z for z in Z[~real] if z[D:].real.sum() >= 0 and z.imag[np.argmax(np.abs(z.imag))] > 0]
    npos_pairs = sum(1 for z in reps if np.all(z[D:].real > 0))
    Ts = sorted((float(np.sum(z.imag ** 2) + np.sum(np.minimum(z[D:].real, 0) ** 2)),
                 float(np.sum(z.imag ** 2)), float(np.sum(np.minimum(z[D:].real, 0) ** 2)),
                 int(np.sum(z[D:].real < 0))) for z in reps)
    rows.append({"theta": th.tolist(), "phys": phys, "pos_pairs": npos_pairs, "nearest": Ts[:3]})
json.dump(rows, open(f"out/orthant_{tag}.json", "w"), indent=1)
c = collections.Counter((r["phys"], r["pos_pairs"]) for r in rows)
print(tag, "configs", len(rows), "(physical, non-real pairs with all Re t > 0):", dict(sorted(c.items())))
for b in sorted(set(r["phys"] for r in rows)):
    rs = [r for r in rows if r["phys"] == b]
    near = sorted(r["nearest"][0] for r in rs)
    print(f"  phys {b}: nearest pair T min {near[0][0]:.4f} (Im^2 {near[0][1]:.4f}, negRe^2 {near[0][2]:.4f}, #neg Re t {near[0][3]})")
