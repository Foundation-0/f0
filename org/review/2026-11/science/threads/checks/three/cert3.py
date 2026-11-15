"""Rigorous certificate (primary engine, numpy interval arithmetic) for:

  THEOREM (per triangle shape box S): for every triangle A1=(0,0), A2=(1,0), A3=(a,b) with (a,b) in S
  and every positive charge vector q, the in-plane potential V_q has at most one local minimum.
  Hence every non-degenerate configuration on such a triangle has at most 4 equilibria.

Coordinates: x = (beta2, beta3), barycentric coordinates of the point P = beta2*A2 + beta3*A3.
Facts used (proved by hand in the report):
  (F1) a local min x of V_q has Hess >= 0, which is |m(x)| <= 1/3 where m = sum beta_i exp(2i theta_i);
  (F2) x is a critical point of V_q iff q is proportional to (beta_i r_i^3); rho_i := q_i/q_1;
  (F3) |m| >= 2 beta_i - 1 for each i.
Certificate structure:
  1. Exclusion: boxes with |m|^2 > 1/9 (rigorous lower bound) hold no local minimum for any q.
  2. Pairs of remaining boxes (Bi, Bj), i <= j, whose rho-images may intersect are resolved by
     (J) the interval Jacobian of log rho on the convex hull has det excluding 0 (Z injective there), or
     (V) a valley certificate on a cell C containing Bi u Bj for all charges q in Q = rho(Bi) n rho(Bj):
         V_ss > 0 on C, V_s < 0 on the lower and > 0 on the upper s-edge, and psi''' != 0 or psi'''' < 0,
         where psi''' = D3V[w,w,w], psi'''' = D4V[w,w,w,w] - 3 D3V[w,w,s]^2 / V_ss, w = t - (V_ts/V_ss) s;
     or they are split and the child pairs are resolved.
"""
import numpy as np
from iv import I, hull

ONE = 1.0


class Shape:
    def __init__(self, a_lo, a_hi, b_lo, b_hi):
        self.a = I(np.float64(a_lo), np.float64(a_hi))
        self.b = I(np.float64(b_lo), np.float64(b_hi))
        self.af = 0.5 * (a_lo + a_hi); self.bf = 0.5 * (b_lo + b_hi)


def phys(sh, b2, b3):
    """Physical point P = b2*A2 + b3*A3 and the three difference vectors d_i = P - A_i (intervals)."""
    px = b2 + sh.a * b3
    py = sh.b * b3
    d = [(px, py), (px - 1.0, py), (px - sh.a, py - sh.b)]
    return d


def betas(b2, b3):
    return [1.0 - b2 - b3, b2, b3]


def cap(x, lo, hi):
    # fmax/fmin ignore NaN (NaN arises only from 0*inf when a box touches a site): then the cap applies
    return I(np.fmax(x.lo, lo), np.fmin(x.hi, hi))


def m2_lower(sh, B):
    """B = (b2lo,b2hi,b3lo,b3hi) arrays. Returns rigorous lower bound of |m|^2 over the box."""
    b2 = I(B[0], B[1]); b3 = I(B[2], B[3])
    bt = betas(b2, b3)
    d = phys(sh, b2, b3)
    re = None; im = None
    for i in range(3):
        dx, dy = d[i]
        dx2 = dx.sq(); dy2 = dy.sq(); r2 = dx2 + dy2
        c1 = 1.0 - 2.0 * (dy2 / r2)
        c2 = 2.0 * (dx2 / r2) - 1.0
        c = I(np.fmax(np.fmax(c1.lo, c2.lo), -1.0), np.fmin(np.fmin(c1.hi, c2.hi), 1.0))
        s = cap(2.0 * (dx * dy) / r2, -1.0, 1.0)
        tr = bt[i] * c; ti = bt[i] * s
        re = tr if re is None else re + tr
        im = ti if im is None else im + ti
    lb = (re.sq() + im.sq()).lo
    # (F3): |m| >= 2 beta_i - 1
    lb = np.where(np.isnan(lb), 0.0, lb)
    for i in range(3):
        g = 2.0 * bt[i] - 1.0
        lb = np.where(g.lo > 0, np.maximum(lb, g.sq().lo), lb)
    return lb


def rho(sh, B):
    """Enclosure of rho2 = q2/q1, rho3 = q3/q1 over the box."""
    b2 = I(B[0], B[1]); b3 = I(B[2], B[3])
    bt = betas(b2, b3)
    d = phys(sh, b2, b3)
    r2 = [d[i][0].sq() + d[i][1].sq() for i in range(3)]
    out = []
    for i in (1, 2):
        s = r2[i] / r2[0]
        out.append((bt[i] / bt[0]) * (s * s.sqrt()))
    return out


def jac_det(sh, B):
    """Interval det of the Jacobian of (log rho2, log rho3) w.r.t. (beta2, beta3) over the box."""
    b2 = I(B[0], B[1]); b3 = I(B[2], B[3])
    bt = betas(b2, b3)
    d = phys(sh, b2, b3)
    r2 = [d[i][0].sq() + d[i][1].sq() for i in range(3)]
    ib1 = 1.0 / bt[0]
    # dP/dbeta2 = (1,0); dP/dbeta3 = (a,b)
    def g(i, k):
        if k == 2:
            dot = d[i][0]
        else:
            dot = d[i][0] * sh.a + d[i][1] * sh.b
        return 3.0 * (dot / r2[i])
    J = {}
    for i in (2, 3):
        for k in (2, 3):
            v = ib1 + g(i - 1, k) - g(0, k)
            if i == k:
                v = v + 1.0 / bt[i - 1]
            J[(i, k)] = v
    return J[(2, 2)] * J[(3, 3)] - J[(2, 3)] * J[(3, 2)]


# ---------------- valley certificate ----------------

def _dot(u, v):
    return u[0] * v[0] + u[1] * v[1]


def tensors(sh, q, P, t, s):
    """Directional derivatives of V_q at physical points P (interval pair) along float vectors t, s.
    q = (I(1), rho2, rho3). Returns dict with keys like 's','ss','ts','tt','ttt','tts','tss','sss',
    'tttt','ttts','ttss','tsss','ssss'."""
    A = [(I.c(0.0), I.c(0.0)), (I.c(1.0), I.c(0.0)), (sh.a, sh.b)]
    vec = {'t': t, 's': s}
    keys2 = ['ss', 'ts', 'tt']
    keys3 = ['ttt', 'tts', 'tss', 'sss']
    keys4 = ['tttt', 'ttts', 'ttss', 'tsss', 'ssss']
    out = {k: None for k in ['s'] + keys2 + keys3 + keys4}
    for i in range(3):
        y = (P[0] - A[i][0], P[1] - A[i][1])
        r2 = y[0].sq() + y[1].sq()
        r = r2.sqrt()
        ir2 = 1.0 / r2
        ir = 1.0 / r
        ir3 = ir * ir2; ir5 = ir3 * ir2; ir7 = ir5 * ir2; ir9 = ir7 * ir2
        yv = {k: y[0] * v[0] + y[1] * v[1] for k, v in vec.items()}
        dd = {}
        for k1 in 'ts':
            for k2 in 'ts':
                dd[k1 + k2] = I.c(vec[k1][0]) * vec[k2][0] + I.c(vec[k1][1]) * vec[k2][1]
        qi = q[i]
        # gradient along s
        val = -(yv['s'] * ir3)
        out['s'] = qi * val if out['s'] is None else out['s'] + qi * val
        for k in keys2:
            a, b = k
            val = 3.0 * (yv[a] * yv[b]) * ir5 - dd[a + b] * ir3
            out[k] = qi * val if out[k] is None else out[k] + qi * val
        for k in keys3:
            a, b, c = k
            val = -15.0 * (yv[a] * yv[b] * yv[c]) * ir7 + 3.0 * (dd[a + b] * yv[c] + dd[a + c] * yv[b] + dd[b + c] * yv[a]) * ir5
            out[k] = qi * val if out[k] is None else out[k] + qi * val
        for k in keys4:
            a, b, c, e = k
            y4 = yv[a] * yv[b] * yv[c] * yv[e]
            s6 = (dd[a + b] * yv[c] * yv[e] + dd[a + c] * yv[b] * yv[e] + dd[a + e] * yv[b] * yv[c]
                  + dd[b + c] * yv[a] * yv[e] + dd[b + e] * yv[a] * yv[c] + dd[c + e] * yv[a] * yv[b])
            p3 = dd[a + b] * dd[c + e] + dd[a + c] * dd[b + e] + dd[a + e] * dd[b + c]
            val = 105.0 * y4 * ir9 - 15.0 * s6 * ir7 + 3.0 * p3 * ir5
            out[k] = qi * val if out[k] is None else out[k] + qi * val
    return out


def valley_ok(sh, Q, c, t, s, ht, hs, nsub=4):
    """Valley certificate on the cell {c + tau t + sig s : |tau|<=ht, |sig|<=hs} for charges
    q = (1, Q[0], Q[1]). c, t, s float 2-vectors (t, s need not be orthonormal). Returns (ok, reason)."""
    q = (I.c(1.0), Q[0], Q[1])
    # subdivide the cell into nsub x nsub pieces for V1, V3 and nsub pieces along each s-edge for V2
    taus = np.linspace(-ht, ht, nsub + 1); sigs = np.linspace(-hs, hs, nsub + 1)
    T0, S0 = np.meshgrid(taus[:-1], sigs[:-1], indexing='ij'); T1, S1 = np.meshgrid(taus[1:], sigs[1:], indexing='ij')
    tau = I(T0.ravel(), T1.ravel()); sig = I(S0.ravel(), S1.ravel())
    P = (c[0] + tau * t[0] + sig * s[0], c[1] + tau * t[1] + sig * s[1])
    D = tensors(sh, q, P, t, s)
    if not D['ss'].pos().all():
        return False, 'V1'
    a = D['ts'] / D['ss']
    w3 = D['ttt'] - 3.0 * a * D['tts'] + 3.0 * a.sq() * D['tss'] - a * a.sq() * D['sss']
    third_ok = w3.pos().all() or w3.neg().all()
    if not third_ok:
        a2 = a.sq()
        w4 = (D['tttt'] - 4.0 * a * D['ttts'] + 6.0 * a2 * D['ttss'] - 4.0 * a * a2 * D['tsss'] + a2 * a2 * D['ssss'])
        w3s = D['tts'] - 2.0 * a * D['tss'] + a2 * D['sss']
        f4 = w4 - 3.0 * w3s.sq() / D['ss']
        if not f4.neg().all():
            return False, 'V3'
    # V2: edges
    tau_e = I(taus[:-1], taus[1:])
    for sg, want in ((-hs, 'neg'), (hs, 'pos')):
        Pe = (c[0] + tau_e * t[0] + sg * s[0], c[1] + tau_e * t[1] + sg * s[1])
        De = tensors(sh, q, Pe, t, s)
        if want == 'neg' and not De['s'].neg().all():
            return False, 'V2'
        if want == 'pos' and not De['s'].pos().all():
            return False, 'V2'
    return True, 'V' + ('3' if third_ok else '4')


def jac_entries(sh, B):
    """Interval entries J[(i,k)] of the Jacobian of (log rho2, log rho3) w.r.t. (beta2, beta3)."""
    b2 = I(B[0], B[1]); b3 = I(B[2], B[3])
    bt = betas(b2, b3)
    d = phys(sh, b2, b3)
    r2 = [d[i][0].sq() + d[i][1].sq() for i in range(3)]
    ib1 = 1.0 / bt[0]
    def g(i, k):
        dot = d[i][0] if k == 2 else d[i][0] * sh.a + d[i][1] * sh.b
        return 3.0 * (dot / r2[i])
    J = {}
    for i in (2, 3):
        for k in (2, 3):
            v = ib1 + g(i - 1, k) - g(0, k)
            if i == k:
                v = v + 1.0 / bt[i - 1]
            J[(i, k)] = v
    return J


def rho_centered(sh, B):
    """Centred-form enclosure of (rho2, rho3), intersected with the natural enclosure."""
    nat = rho(sh, B)
    c2 = 0.5 * (B[0] + B[1]); c3 = 0.5 * (B[2] + B[3])
    dn = lambda x: np.nextafter(x, -np.inf); up = lambda x: np.nextafter(x, np.inf)
    h2 = I(dn(B[0] - c2), up(B[1] - c2))
    h3 = I(dn(B[2] - c3), up(B[3] - c3))
    cen = rho(sh, (c2, c2, c3, c3))
    J = jac_entries(sh, B)
    out = []
    for idx, i in enumerate((2, 3)):
        der2 = nat[idx] * J[(i, 2)]; der3 = nat[idx] * J[(i, 3)]
        e = cen[idx] + der2 * h2 + der3 * h3
        lo = np.fmax(e.lo, nat[idx].lo); hi = np.fmin(e.hi, nat[idx].hi)
        out.append(I(lo, hi))
    return out
