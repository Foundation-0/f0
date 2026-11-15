"""Sample the cusp surface {G = 0} inside the valid fold set and record the cusp type Kn."""
import numpy as np, sys
from cuspset import GK
n = int(sys.argv[1]) if len(sys.argv) > 1 else 300
g1 = np.linspace(0, 2 * np.pi, n, endpoint=False)
g3 = np.linspace(0, 2 * np.pi, 4 * n, endpoint=False)
out = []
for p1 in g1:
    P1, P2, P3_ = np.meshgrid([p1], g1, g3, indexing='ij')
    psi = np.stack([P1, P2, P3_], -1)[0]  # (n, 4n, 3)
    G, K, Kn, valid, b, w, r = GK(psi)
    # sign changes of G along psi3 within valid region
    ch = (np.sign(G[:, :-1]) != np.sign(G[:, 1:])) & valid[:, :-1] & valid[:, 1:]
    I, J = np.where(ch)
    for i, j in zip(I, J):
        lo, hi = g3[j], g3[j + 1]
        f = lambda t: GK(np.array([p1, g1[i], t]))[0]
        flo = f(lo)
        for _ in range(40):
            mid = (lo + hi) / 2
            fm = f(mid)
            if np.sign(fm) == np.sign(flo):
                lo, flo = mid, fm
            else:
                hi = mid
        ps = np.array([p1, g1[i], (lo + hi) / 2])
        Gv, Kv, Knv, vv, bv, wv, rv = GK(ps)
        if vv and abs(Gv) < 1e-8:
            out.append(np.r_[ps, Knv, Kv, bv, rv / rv.sum()])
out = np.array(out)
np.save('out/cusp_samples.npy', out)
print('cusp samples', len(out))
print('Kn max', out[:, 3].max(), 'Kn min', out[:, 3].min())
k = np.argsort(out[:, 3])[-10:]
np.set_printoptions(precision=5, suppress=True, linewidth=150)
print(out[k])
