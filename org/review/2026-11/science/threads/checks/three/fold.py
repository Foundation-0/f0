"""Fold curve, cusps and cusp type for a fixed triangle (floating point exploration).

For triangle (a,b): R_min = {x in T : mu(x) > 0}. We locate c = argmax mu, check that
R_min is star-shaped about c (single sign change of mu along each ray, sampled), trace the fold
curve F(theta), compute the cubic coefficient V_ttt along the kernel direction, locate its zeros
(cusps) and the effective quartic coefficient kappa = V_tttt/24 - V_tts^2/(8 mu_s) there.
kappa > 0 at a cusp would give two local minima nearby (counterexample to Maxwell)."""
import numpy as np
from scipy.optimize import minimize
from lib3 import sites, lami, mu, derivs, grad_hess


def inside(A, X):
    # barycentric test
    T = np.array([A[1] - A[0], A[2] - A[0]]).T
    L = np.linalg.solve(T, (X - A[0]).T).T if X.ndim == 2 else np.linalg.solve(T, X - A[0])
    return (L[..., 0] > 0) & (L[..., 1] > 0) & (L[..., 0] + L[..., 1] < 1)


def center(A, n=120):
    s = (np.arange(n) + 0.5) / n
    S, T = np.meshgrid(s, s, indexing='ij')
    m = S + T < 1
    X = (A[0] + S[..., None] * (A[1] - A[0]) + T[..., None] * (A[2] - A[0]))[m]
    M = mu(A, X)
    x0 = X[np.argmax(M)]
    f = lambda x: -mu(A, x[None])[0] if inside(A, x[None])[0] else 1.0
    r = minimize(f, x0, method='Nelder-Mead', options=dict(xatol=1e-12, fatol=1e-14))
    return r.x, -r.fun


def ray_exit(A, c, th, nsamp=200):
    """Distance along ray from c at angle th to the first zero of mu; also number of sign changes."""
    e = np.array([np.cos(th), np.sin(th)])
    # max distance to triangle boundary
    hi = 0.0; step = 1.0
    # find boundary distance by bisection on inside()
    lo_, hi_ = 0.0, 10.0
    for _ in range(60):
        mid = (lo_ + hi_) / 2
        if inside(A, (c + mid * e)[None])[0]:
            lo_ = mid
        else:
            hi_ = mid
    R = lo_
    t = R * (np.arange(1, nsamp) / nsamp) ** 1.0
    M = mu(A, c + t[:, None] * e)
    sg = np.sign(M)
    nchg = int((sg[1:] != sg[:-1]).sum())
    k = np.argmax(M < 0)
    if M[k] >= 0:
        return None, nchg, R
    lo, hi = (t[k - 1] if k > 0 else 0.0), t[k]
    for _ in range(60):
        mid = (lo + hi) / 2
        if mu(A, (c + mid * e)[None])[0] > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2, nchg, R


def fold_data(A, x):
    q = lami(A, x[None])[0][0]
    g, H, T, F = derivs(A, q, x)
    ev, V = np.linalg.eigh(H)
    k = np.argmin(np.abs(ev))
    t = V[:, k]; n = V[:, 1 - k]; ms = ev[1 - k]
    a3 = np.einsum('abc,a,b,c', T, t, t, t)
    b3 = np.einsum('abc,a,b,c', T, t, t, n)
    e4 = np.einsum('abcd,a,b,c,d', F, t, t, t, t)
    kap = e4 / 24 - b3 ** 2 / (8 * ms)
    kn = kap / (abs(e4) / 24 + b3 ** 2 / (8 * ms))
    scale = (q / np.linalg.norm(x - A, axis=1) ** 4).sum()
    return dict(q=q, t=t, n=n, ms=ms, a3=a3, a3n=a3 / scale, b3=b3, e4=e4, kap=kap, kapn=kn, ev=ev)


def analyse(a, b, nth=720):
    A = sites(a, b)
    c, mumax = center(A)
    if mumax <= 0:
        return dict(a=a, b=b, empty=True, mumax=mumax)
    ths = np.linspace(0, 2 * np.pi, nth, endpoint=False)
    rho = []; nch = []
    for th in ths:
        r_, k_, R_ = ray_exit(A, c, th)
        rho.append(r_); nch.append(k_)
    rho = np.array(rho, dtype=float)
    star = all(k == 1 for k in nch)
    P = c + rho[:, None] * np.c_[np.cos(ths), np.sin(ths)]

    def a3_at(th, tref=None):
        r_, _, _ = ray_exit(A, c, th)
        x = c + r_ * np.array([np.cos(th), np.sin(th)])
        d = fold_data(A, x)
        sgn = 1.0
        if tref is not None and d['t'] @ tref < 0:
            sgn = -1.0
        return d['a3n'] * sgn, x, d, d['t'] * sgn
    # a3 is odd in the kernel vector t (defined up to sign): orient t continuously along F.
    vals = []; tv = []
    tref = None
    for i, th in enumerate(ths):
        v, x, d, t = a3_at(th, tref)
        vals.append(v); tv.append(t); tref = t
    vals = np.array(vals)
    flip_loop = bool(tv[-1] @ tv[0] < 0)
    if flip_loop:
        pass
    cusps = []
    for i in range(nth):
        j = (i + 1) % nth
        vj = vals[j] * (-1.0 if (j == 0 and flip_loop) else 1.0)
        if np.sign(vals[i]) != np.sign(vj):
            lo, hi = ths[i], (ths[j] if j else 2 * np.pi)
            flo = vals[i]; tlo = tv[i]
            for _ in range(50):
                mid = (lo + hi) / 2
                v, x, d, t = a3_at(mid, tlo)
                if np.sign(v) == np.sign(flo):
                    lo = mid; tlo = t
                else:
                    hi = mid
            v, x, d, t = a3_at((lo + hi) / 2, tlo)
            cusps.append(dict(th=(lo + hi) / 2, x=x, q=d['q'], kap=d['kap'], kapn=d['kapn'], b3=d['b3'], e4=d['e4'], ms=d['ms']))
    # image of fold curve and self-intersection test (polyline)
    Q = lami(A, P)[0]
    return dict(a=a, b=b, empty=False, c=c, mumax=mumax, star=star, nch=nch, P=P, Q=Q, cusps=cusps, a3=vals, flip_loop=flip_loop)


def seg_intersections(Y):
    """Count proper self-intersections of a closed polyline Y (n,2), ignoring adjacent segments."""
    n = len(Y)
    p = Y; q = np.roll(Y, -1, axis=0)
    cnt = 0; where = []
    d = q - p
    for i in range(n):
        # vectorised test of segment i vs segments j > i+1
        j = np.arange(i + 2, n)
        if i == 0:
            j = j[j != n - 1]
        if len(j) == 0:
            continue
        r = d[i]; s = d[j]
        den = r[0] * s[:, 1] - r[1] * s[:, 0]
        w = p[j] - p[i]
        with np.errstate(divide='ignore', invalid='ignore'):
            tt = (w[:, 0] * s[:, 1] - w[:, 1] * s[:, 0]) / den
            uu = (w[:, 0] * r[1] - w[:, 1] * r[0]) / den
        hit = (den != 0) & (tt > 0) & (tt < 1) & (uu > 0) & (uu < 1)
        cnt += int(hit.sum())
        where += [(i, int(k)) for k in j[hit]]
    return cnt, where
