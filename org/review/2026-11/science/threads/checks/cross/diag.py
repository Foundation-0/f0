"""Diagnose a stalled push (numerical): at theta, take the nearest non-real pair, and move along
-grad T (no constraints) with growing steps; report the physical count, T of the tracked pair, and the
smallest pairwise distance and smallest Hessian singular value among physical solutions.
Usage: python diag.py n D theta.json index"""
import sys, json
import numpy as np
from cross_lib import F_J, newton, track, arc_path, param_jac

n, D = int(sys.argv[1]), int(sys.argv[2])
th0 = np.array(json.load(open(sys.argv[3]))[int(sys.argv[4])])
rng = np.random.default_rng(1)
base = np.load(f"out/mono_n{n}_D{D}_s1.npz")
Pb, qb, Sb = base["P"], base["q"], base["S"]
npos = 2 if D == 2 else 5
m = len(th0)


def theta_to_Pq(th):
    P = np.zeros((n, D)); P[1, 0] = 1.0
    if D == 2:
        P[2] = th[0:2]
    else:
        P[2, :2] = th[0:2]; P[3] = th[2:5]
    return P.astype(complex), np.concatenate([[1.0], np.exp(th[npos:])]).astype(complex)


def solve(Z, Pa, qa, th, tries=6):
    P, q = theta_to_Pq(th)
    for _ in range(tries):
        Pm = 0.3 * (rng.normal(size=P.shape) + 1j * rng.normal(size=P.shape)) * (np.abs(P - Pa).max() + 1e-3); Pm[:2] = 0
        qm = 0.3 * (rng.normal(size=q.shape) + 1j * rng.normal(size=q.shape)) * (np.abs(q - qa).max() + 1e-3); qm[0] = 0
        Zt, ok = track(Z, arc_path(Pa, qa, P, q, Pm, qm), D)
        if ok.all():
            Zt, err = newton(Zt, np.broadcast_to(P, (len(Zt), n, D)), np.broadcast_to(q, (len(Zt), n)), D)
            if err.max() < 1e-9:
                return Zt, P, q
    return None, P, q


Z, P, q = solve(Sb, Pb, qb, th0)
imm = np.max(np.abs(Z.imag), axis=1) / (1 + np.max(np.abs(Z.real), axis=1))
real = imm < 1e-9
phys = real & np.all(Z[:, D:].real > 0, axis=1)
T = lambda z: float(np.sum(z.imag ** 2) + np.sum(np.minimum(z[D:].real, 0) ** 2))
cand = [i for i in np.where(~real)[0] if Z[i].imag[np.argmax(np.abs(Z[i].imag))] > 0 and Z[i, D:].real.sum() >= 0]
i0 = min(cand, key=lambda i: T(Z[i]))
z = Z[i0]
print("theta", np.round(th0, 4).tolist())
print("physical", phys.sum(), "nearest pair T", T(z), "x", np.round(z[:D], 4), "t", np.round(z[D:], 4))
print("physical x:", [np.round(Z[i, :D].real, 4).tolist() for i in np.where(phys)[0]])


def tracked(th, Zfrom, Pf, qf, zref):
    Z2, P2, q2 = solve(Zfrom, Pf, qf, th)
    if Z2 is None:
        return None, None
    j = int(np.argmin(np.max(np.abs(Z2 - zref[None]), axis=1)))
    imm2 = np.max(np.abs(Z2.imag), axis=1) / (1 + np.max(np.abs(Z2.real), axis=1))
    ph2 = (imm2 < 1e-9) & np.all(Z2[:, D:].real > 0, axis=1)
    return T(Z2[j]), int(ph2.sum())


h = 1e-5
g = np.zeros(m)
for k in range(m):
    e = np.zeros(m); e[k] = h
    Tp, _ = tracked(th0 + e, Z, P, q, z)
    Tm, _ = tracked(th0 - e, Z, P, q, z)
    g[k] = (Tp - Tm) / (2 * h)
print("grad T (finite differences)", np.round(g, 4).tolist(), "norm", np.linalg.norm(g))
d = -g / np.linalg.norm(g)
for s_ in [1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1]:
    Tn, cnt = tracked(th0 + s_ * d, Z, P, q, z)
    print(f"step {s_:.0e}: tracked-pair T {Tn}, physical count {cnt}")
