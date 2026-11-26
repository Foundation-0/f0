import numpy as np, time
from push import *
from scipy.optimize import linprog
d = np.load("snap_B_1988.npz"); Z = d["Z"]; p = d["p"]
rng = np.random.default_rng(0)
X, Y, real, im2 = analyse(Z); nr = int(real.sum()); print("real", 2*nr)
dX, dY = sensitivities(Z, p_to_P(p))
reps = pair_reps(Z, real); order = reps[np.argsort(im2[reps])]
print("n pairs", len(reps), "smallest im2", np.sort(im2[reps])[:10])
lam = lengths(p); print("lengths range", lam.min(), lam.max())
# per pair: predicted step to wall along its own gradient, ignoring constraints
for r in order[:8]:
    g = 2 * (X[r].imag[:, None] * dX[r].imag + Y[r].imag[:, None] * dY[r].imag).sum(axis=0)
    print(f"pair im2 {im2[r]:.2e}  |grad| {np.linalg.norm(g):.2e}  dist-to-wall est {im2[r]/np.linalg.norm(g):.2e}")
# closest real pairs
ri = np.where(real)[0]
Xr = np.concatenate([X[ri].real, Y[ri].real], axis=1)
D2 = ((Xr[:, None, :] - Xr[None, :, :]) ** 2).sum(axis=2); iu, ju = np.triu_indices(len(ri), 1); dd = D2[iu, ju]
print("closest real pair d2", np.sort(dd)[:10])
sv = np.array([np.linalg.svd(j, compute_uv=False)[-1] for j in L.FJ(Z, p_to_P(p))[1]])
print("sigma_min real quantiles", np.quantile(sv[real], [0, .01, .1, .5]))
# try a single-pair LP-free step: move along -grad of nearest pair by its estimated distance * 1.5
for r in order[:5]:
    g = 2 * (X[r].imag[:, None] * dX[r].imag + Y[r].imag[:, None] * dY[r].imag).sum(axis=0)
    step = -g / np.dot(g, g) * im2[r] * 1.5
    q = p + step
    t = time.time(); Zn, ok = local_move(Z, p, q, rng)
    Xn, Yn, rn, _ = analyse(Zn)
    print(f"single-pair step |step| {np.abs(step).max():.2e}: local ok {ok}, real {2*int(rn.sum())} ({time.time()-t:.1f}s)")
