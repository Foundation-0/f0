"""Hill-climb the number of real critical points of P = Htop + h, h harmonic of degree < d. Numerical."""
import numpy as np, sys, time, json
from harm import *

def climb(c, d, lows, rng, iters=3000, scale0=0.5, verbose=True, fixed_top=True, seed_h=None, B=None):
    if B is None:
        B = np.hstack([harmonic_basis(d, l) for l in lows])
    h = rng.standard_normal(B.shape[1]) * scale0 if seed_h is None else seed_h.copy()
    def cnt(h):
        P = Poly(c + B @ h, d); s, lost = solve_all(P, rng)
        R, idx, me = real_crit(P, s)
        # demand non-degenerate, well separated
        okR = len(R) == 0 or me.min() > 1e-6 * np.abs(B @ h).max()
        return len(R), len(s), idx, R, okR
    cur, ns, idx, R, ok = cnt(h); best = (cur, h.copy(), idx, ns)
    sc = scale0
    for it in range(iters):
        hn = h + rng.standard_normal(len(h)) * sc * np.abs(h).mean() * 0.3
        k, ns, idx, R, ok = cnt(hn)
        if ok and k >= cur:
            if k > cur and verbose:
                print(f"  it {it}: real {k} of {ns} complex, index1 {int((idx==1).sum())} index2 {int((idx==2).sum())}", flush=True)
            h, cur = hn, k
            if k > best[0]:
                best = (k, h.copy(), idx, ns)
    return best

if __name__ == "__main__":
    pass
