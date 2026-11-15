#!/usr/bin/env python3
"""Machine check of every closed-form formula in DERIVATIONS.md (three-charge thread).

Each check prints one line, 'PASS <label> <what>'. The labels D1 ... D52 are the formula labels
in DERIVATIONS.md. Symbolic identities are checked with SymPy. Formulas that involve limits,
winding numbers, roots, integrals or inequalities are checked at random points with mpmath at
50 significant digits. Section X checks that the thread's programs (cert3.py, lib3.py,
cuspset.py, verify_arb3.py, run_cert2.py) compute the formulas derived here. Checks D46 and D47
test the hypotheses that the assembly lemma needs on the archived certificate out/c3_equi*.
Check N1 reproduces the counterexample behind one correction to three-charges.md (line 50).

Any failure raises CheckFailed. The program then prints 'RESULT FAIL' and exits 1. It exits 0
only if every check passes. There are no assert statements, so python3 -O checks the same things.

usage: python3 -O derivations_check.py [--flip NAME]
  --flip NAME corrupts one formula on purpose (a sign flip) to show that the check catches it.
  NAME is one of: psi4 (D43), jac (D34), kernel (D14), lami (D8), r57 (D29), cusp (D52).
"""
import sys, os, json, random, argparse
from fractions import Fraction

import sympy as sp
import mpmath as mp

mp.mp.dps = 50
TOL = mp.mpf(10) ** -40
HERE = os.path.dirname(os.path.abspath(__file__))
FLIP = set()


class CheckFailed(Exception):
    pass


NPASS = [0]


def check(label, what, ok, detail=''):
    if not ok:
        print('FAIL %-5s %s %s' % (label, what, detail), flush=True)
        raise CheckFailed('%s: %s' % (label, what))
    NPASS[0] += 1
    print('PASS %-5s %s%s' % (label, what, ('  [' + detail + ']') if detail else ''), flush=True)


def flip(name):
    return -1 if name in FLIP else 1


def zero(e):
    """True if the SymPy expression (or matrix) e simplifies to 0."""
    if isinstance(e, sp.MatrixBase):
        return all(zero(x) for x in e)
    e = sp.simplify(e)
    if e == 0:
        return True
    return sp.simplify(sp.trigsimp(sp.expand_trig(sp.expand(e)))) == 0


def close(a, b, tol=TOL):
    return abs(a - b) <= tol * (1 + abs(b))


RNG = random.Random(20261115)


def rnd(lo, hi):
    return mp.mpf(lo) + (mp.mpf(hi) - mp.mpf(lo)) * mp.mpf(RNG.random())


# ---------------------------------------------------------------- plane geometry in mpmath
def sub(u, v):
    return (u[0] - v[0], u[1] - v[1])


def add(u, v):
    return (u[0] + v[0], u[1] + v[1])


def scal(c, u):
    return (c * u[0], c * u[1])


def dot(u, v):
    return u[0] * v[0] + u[1] * v[1]


def cross(u, v):
    return u[0] * v[1] - u[1] * v[0]


def norm(u):
    return mp.sqrt(dot(u, u))


def random_triangle():
    """A1 = (0,0), A2 = (1,0), A3 = (a,b), b > 0 (counterclockwise)."""
    return [(mp.mpf(0), mp.mpf(0)), (mp.mpf(1), mp.mpf(0)), (rnd(-0.6, 1.6), rnd(0.25, 1.6))]


def random_beta():
    u, v = sorted([RNG.random(), RNG.random()])
    b = [mp.mpf(u), mp.mpf(v - u), mp.mpf(1 - v)]
    # keep away from the boundary a little
    b = [mp.mpf('0.02') + mp.mpf('0.94') * x for x in b]
    return b


def point(A, beta):
    return (sum(beta[k] * A[k][0] for k in range(3)), sum(beta[k] * A[k][1] for k in range(3)))


def bary(A, x):
    D = cross(sub(A[1], A[0]), sub(A[2], A[0]))
    b2 = cross(sub(x, A[0]), sub(A[2], A[0])) / D
    b3 = cross(sub(A[1], A[0]), sub(x, A[0])) / D
    return [1 - b2 - b3, b2, b3]


def m_of(A, x):
    beta = bary(A, x)
    m = mp.mpc(0)
    for k in range(3):
        y = sub(x, A[k])
        m += beta[k] * mp.mpc(y[0], y[1]) ** 2 / dot(y, y)  # exp(2 i theta_k)
    return m


def d1r(y, vecs):
    """D48: n-th directional derivative of 1/|y| along vecs (n = len(vecs) = 1..4)."""
    r2 = dot(y, y)
    r = mp.sqrt(r2)
    n = len(vecs)
    yv = [dot(y, v) for v in vecs]
    dd = lambda i, j: dot(vecs[i], vecs[j])
    if n == 1:
        return -yv[0] / r ** 3
    if n == 2:
        return 3 * yv[0] * yv[1] / r ** 5 - dd(0, 1) / r ** 3
    if n == 3:
        return (-15 * yv[0] * yv[1] * yv[2] / r ** 7
                + 3 * (dd(0, 1) * yv[2] + dd(0, 2) * yv[1] + dd(1, 2) * yv[0]) / r ** 5)
    if n == 4:
        s6 = (dd(0, 1) * yv[2] * yv[3] + dd(0, 2) * yv[1] * yv[3] + dd(0, 3) * yv[1] * yv[2]
              + dd(1, 2) * yv[0] * yv[3] + dd(1, 3) * yv[0] * yv[2] + dd(2, 3) * yv[0] * yv[1])
        p3 = dd(0, 1) * dd(2, 3) + dd(0, 2) * dd(1, 3) + dd(0, 3) * dd(1, 2)
        return 105 * yv[0] * yv[1] * yv[2] * yv[3] / r ** 9 - 15 * s6 / r ** 7 + 3 * p3 / r ** 5
    raise ValueError(n)


def DV(A, q, x, vecs):
    return sum(q[k] * d1r(sub(x, A[k]), vecs) for k in range(3))


E1 = (mp.mpf(1), mp.mpf(0))
E2 = (mp.mpf(0), mp.mpf(1))


def grad(A, q, x):
    return (DV(A, q, x, [E1]), DV(A, q, x, [E2]))


def hess(A, q, x):
    return [[DV(A, q, x, [E1, E1]), DV(A, q, x, [E1, E2])], [DV(A, q, x, [E2, E1]), DV(A, q, x, [E2, E2])]]


def winding(F, pts):
    """Winding number of the plane vector field F (returns (x, y)) along the closed polygon pts."""
    ang = [mp.atan2(*reversed(F(p))) for p in pts]
    tot = mp.mpf(0); mx = mp.mpf(0)
    for i in range(len(ang)):
        d = ang[(i + 1) % len(ang)] - ang[i]
        while d > mp.pi:
            d -= 2 * mp.pi
        while d < -mp.pi:
            d += 2 * mp.pi
        tot += d; mx = max(mx, abs(d))
    w = tot / (2 * mp.pi)
    return int(mp.nint(w)), abs(w - mp.nint(w)), mx


def jac_G(A, beta):
    """D34: Jacobian of G = (log rho2, log rho3) w.r.t. (beta2, beta3); A1 = (0,0)."""
    x = point(A, beta)
    e = {2: sub(A[1], A[0]), 3: sub(A[2], A[0])}
    y = {k: sub(x, A[k - 1]) for k in (1, 2, 3)}
    J = {}
    for k in (2, 3):
        for j in (2, 3):
            v = flip('jac') / beta[0] + 3 * dot(y[k], e[j]) / dot(y[k], y[k]) - 3 * dot(y[1], e[j]) / dot(y[1], y[1])
            if k == j:
                v += 1 / beta[k - 1]
            J[(k, j)] = v
    return J


def rho_of(A, beta):
    """D7."""
    x = point(A, beta)
    r = [norm(sub(x, A[k])) for k in range(3)]
    return [beta[k] / beta[0] * (r[k] / r[0]) ** 3 for k in (1, 2)]


# ================================================================= section 1: Lemmas 1 and 2
def sec_planarity():
    p1, p2, z, ax, ay = sp.symbols('p1 p2 z a_x a_y', real=True)
    R = sp.sqrt((p1 - ax) ** 2 + (p2 - ay) ** 2 + z ** 2)
    r = sp.sqrt((p1 - ax) ** 2 + (p2 - ay) ** 2)
    check('D1', 'd/dz 1/R = -z/R^3', zero(sp.diff(1 / R, z) + z / R ** 3))
    check('D2', 'd2/dz2 1/R = -1/r^3 at z = 0', zero(sp.diff(1 / R, z, 2).subs(z, 0) + 1 / r ** 3))
    e = sp.diff(1 / R, p1, z)
    check('D3', 'd2/dp dz 1/R = 3 z (p - a)/R^5, zero at z = 0',
          zero(e - 3 * z * (p1 - ax) / R ** 5) and zero(e.subs(z, 0)))
    y1, y2 = sp.symbols('y1 y2', real=True)
    rr = sp.sqrt(y1 ** 2 + y2 ** 2)
    Hs = sp.hessian(1 / rr, (y1, y2))
    Y = sp.Matrix([y1, y2])
    form = (3 * Y * Y.T - rr ** 2 * sp.eye(2)) / rr ** 5
    x3, y3, z3 = sp.symbols('x3 y3 z3', real=True)
    r3 = sp.sqrt(x3 ** 2 + y3 ** 2 + z3 ** 2)
    lap3 = sum(sp.diff(1 / r3, v, 2) for v in (x3, y3, z3))
    check('D4', 'Hess(1/|y|) = (3yy^T - |y|^2 I)/|y|^5 in the plane, trace 1/|y|^3; 1/|y| harmonic in space',
          zero(Hs - form) and zero(Hs.trace() - 1 / rr ** 3) and zero(lap3))


# ================================================================= section 2: Lemma 3
def sec_index():
    ph = sp.symbols('phi', real=True)
    u = sp.Matrix([sp.cos(ph), sp.sin(ph)])
    Mx = sp.eye(2) - 3 * u * u.T
    ev = sorted(sp.simplify(v) for v in Mx.eigenvals())
    ok_norm = (sp.simplify(ev[0] + 2) == 0) and (sp.simplify(ev[1] - 1) == 0)
    # far-field bound at random points
    ok = True; worst = mp.mpf(0)
    for _ in range(20):
        A = random_triangle(); q = [rnd(0.2, 3) for _ in range(3)]
        Q = sum(q)
        for Rbig in (mp.mpf(50), mp.mpf(10) ** 3, mp.mpf(10) ** 6):
            phi = rnd(0, 2 * mp.pi)
            x = (Rbig * mp.cos(phi), Rbig * mp.sin(phi))
            F = grad(A, q, x)
            E = (F[0] + Q * x[0] / Rbig ** 3, F[1] + Q * x[1] / Rbig ** 3)
            bound = sum(q[k] * 2 * norm(A[k]) / (Rbig - norm(A[k])) ** 3 for k in range(3))
            ok &= norm(E) <= bound * (1 + TOL)
            worst = max(worst, norm(E) / bound)
    check('D5', 'far field: |grad V + Q x/R^3| <= sum 2 q_k |A_k|/(R - |A_k|)^3; eigenvalues of I - 3uu^T are 1, -2',
          ok and ok_norm, 'max ratio %s over 60 points' % mp.nstr(worst, 4))
    # windings of grad V: +1 around each site, +1 on a big circle
    res = []
    for _ in range(3):
        A = random_triangle(); q = [rnd(0.2, 3) for _ in range(3)]
        F = lambda p: grad(A, q, p)
        side = min(norm(sub(A[i], A[j])) for i in range(3) for j in range(i))
        n = 720
        for k in range(3):
            eps = side * mp.mpf('1e-3')
            pts = [add(A[k], (eps * mp.cos(2 * mp.pi * i / n), eps * mp.sin(2 * mp.pi * i / n))) for i in range(n)]
            res.append(winding(F, pts))
        Rb = mp.mpf(1000)
        pts = [(Rb * mp.cos(2 * mp.pi * i / n), Rb * mp.sin(2 * mp.pi * i / n)) for i in range(n)]
        res.append(winding(F, pts))
    check('D6', 'winding of grad V is +1 on small circles around each site and +1 on a big circle',
          all(w == 1 and err < mp.mpf('1e-6') and mx < mp.mpf('0.5') for (w, err, mx) in res),
          '%d circles, 3 random configurations' % len(res))


# ================================================================= section 3: Lemma 4
def sec_inverse():
    b2, b3, lam = sp.symbols('beta2 beta3 lambda', positive=True)
    S = sp.symbols('a1x a1y a2x a2y a3x a3y', real=True)
    A = [sp.Matrix([S[0], S[1]]), sp.Matrix([S[2], S[3]]), sp.Matrix([S[4], S[5]])]
    b = [1 - b2 - b3, b2, b3]
    x = b[0] * A[0] + b[1] * A[1] + b[2] * A[2]
    y = [x - A[k] for k in range(3)]
    r = [sp.sqrt(y[k].dot(y[k])) for k in range(3)]
    q = [lam * b[k] * r[k] ** 3 for k in range(3)]
    g = -sum((q[k] * y[k] / r[k] ** 3 for k in range(3)), sp.zeros(2, 1))
    rk, r1 = sp.symbols('r_k r_1', positive=True)
    bk, bb1 = sp.symbols('beta_k beta_1', positive=True)
    s_ = rk ** 2 / r1 ** 2
    check('D7', 'rho_k = q_k/q_1 = (beta_k/beta_1)(r_k/r_1)^3 = (beta_k/beta_1) s sqrt(s), s = r_k^2/r_1^2',
          zero((bk * rk ** 3) / (bb1 * r1 ** 3) - bk / bb1 * (rk / r1) ** 3) and zero(bk / bb1 * s_ * sp.sqrt(s_) - bk / bb1 * (rk / r1) ** 3))
    crs = lambda u, v: u[0] * v[1] - u[1] * v[0]
    T2 = crs(A[1] - A[0], A[2] - A[0])
    ok = True
    for k in range(3):
        l, n = (k + 1) % 3, (k + 2) % 3
        ok &= zero(flip('lami') * crs(A[l] - x, A[n] - x) / T2 - b[k])
    # numeric: q proportional to r_k^2 w_k with w_k = u_l x u_n
    for _ in range(10):
        At = random_triangle(); be = random_beta(); xx = point(At, be)
        rr = [norm(sub(xx, At[k])) for k in range(3)]
        uu = [scal(1 / rr[k], sub(xx, At[k])) for k in range(3)]
        w = [cross(uu[(k + 1) % 3], uu[(k + 2) % 3]) for k in range(3)]
        qa = [be[k] * rr[k] ** 3 for k in range(3)]; qb = [rr[k] ** 2 * w[k] for k in range(3)]
        sa, sb = sum(qa), sum(qb)
        ok &= all(close(qa[k] / sa, qb[k] / sb) for k in range(3))
    check('D8', 'beta_k = (A_l - x) x (A_n - x)/((A_2 - A_1) x (A_3 - A_1)) (symbolic); Z(x) = [r_k^2 w_k] (10 random points)', ok)
    uv = sp.symbols('u v', real=True)
    ruv = sp.sqrt(uv[0] ** 2 + uv[1] ** 2)
    check('D9', 'grad(1/|y|) = -y/|y|^3, and grad V = 0 at x for q_k = lambda beta_k r_k^3',
          zero(g) and zero(sp.Matrix([sp.diff(1 / ruv, w) for w in uv]) + sp.Matrix(uv) / ruv ** 3))


# ================================================================= section 4: Lemma 5
def sec_hessian():
    lam, be, r = sp.symbols('lambda beta r', positive=True)
    y1, y2 = sp.symbols('y1 y2', real=True)
    Y = sp.Matrix([y1, y2]); rr = sp.sqrt(y1 ** 2 + y2 ** 2)
    q = lam * be * rr ** 3
    U = Y / rr
    check('D10', 'q_k (3 y y^T - r^2 I)/r^5 = lambda beta_k (3 u u^T - I) when q_k = lambda beta_k r_k^3',
          zero(q * (3 * Y * Y.T - rr ** 2 * sp.eye(2)) / rr ** 5 - lam * be * (3 * U * U.T - sp.eye(2))))
    th = sp.symbols('theta1:4', real=True)
    b2, b3 = sp.symbols('beta2 beta3', positive=True)
    b = [1 - b2 - b3, b2, b3]
    uut = lambda t: sp.Matrix([[sp.cos(t) ** 2, sp.cos(t) * sp.sin(t)], [sp.cos(t) * sp.sin(t), sp.sin(t) ** 2]])
    one = zero(uut(th[0]) - sp.Rational(1, 2) * sp.Matrix([[1 + sp.cos(2 * th[0]), sp.sin(2 * th[0])],
                                                          [sp.sin(2 * th[0]), 1 - sp.cos(2 * th[0])]]))
    M = sum((b[k] * uut(th[k]) for k in range(3)), sp.zeros(2, 2))
    re = sum(b[k] * sp.cos(2 * th[k]) for k in range(3)); im = sum(b[k] * sp.sin(2 * th[k]) for k in range(3))
    check('D11', 'u u^T = (1/2)[[1+cos2t, sin2t],[sin2t, 1-cos2t]], so M = (1/2)[[1+Re m, Im m],[Im m, 1-Re m]]',
          one and zero(M - sp.Rational(1, 2) * sp.Matrix([[1 + re, im], [im, 1 - re]])))
    p, s = sp.symbols('p s', real=True)
    Mg = sp.Rational(1, 2) * sp.Matrix([[1 + p, s], [s, 1 - p]])
    rad = sp.sqrt(p ** 2 + s ** 2)
    evM = sorted(Mg.eigenvals().keys(), key=lambda e: sp.sign(sp.simplify(e - sp.Rational(1, 2)).subs({p: 1, s: 1})))
    evH = list((lam * (3 * Mg - sp.eye(2))).eigenvals().keys())
    ok = zero(Mg.det() - (1 - p ** 2 - s ** 2) / 4)
    ok &= zero(evM[0] - (1 - rad) / 2) and zero(evM[1] - (1 + rad) / 2)
    want = [lam * (1 - 3 * rad) / 2, lam * (1 + 3 * rad) / 2]
    ok &= all(any(zero(e - w) for e in evH) for w in want)
    check('D12', 'det M = (1-|m|^2)/4; eig M = (1 +- |m|)/2; eig H = lambda (1 +- 3|m|)/2', ok)
    rho = sp.symbols('rho', real=True)
    half = sp.Interval(0, sp.oo)
    i1 = sp.solve_univariate_inequality((1 - rho ** 2) / 4 > sp.Rational(2, 9), rho, relational=False).intersect(half)
    i2 = sp.solve_univariate_inequality((1 - rho) / (1 + rho) > sp.Rational(1, 2), rho, relational=False).intersect(half)
    target = sp.Interval.Ropen(0, sp.Rational(1, 3))
    check('D13', 'for |m| >= 0: det M > 2/9 <=> |m| < 1/3 <=> lambda_min/lambda_max(M) > 1/2',
          i1 == target and i2 == target, 'both sets = %s' % target)
    ph, rh = sp.symbols('phi rho', real=True)
    Nm = rh * sp.Matrix([[sp.cos(ph), sp.sin(ph)], [sp.sin(ph), -sp.cos(ph)]])
    v = sp.Matrix([-sp.sin(ph / 2), flip('kernel') * sp.cos(ph / 2)])
    H13 = (sp.eye(2) + 3 * Nm.subs(rh, sp.Rational(1, 3)))
    check('D14', 'N v = -|m| v for v = (-sin(phi/2), cos(phi/2)); so H v = 0 at |m| = 1/3; m = -1/3 gives kernel (1,0)',
          zero(Nm * v + rh * v) and zero(H13 * v) and zero((sp.eye(2) + 3 * Nm.subs({rh: sp.Rational(1, 3), ph: sp.pi})) * sp.Matrix([1, 0])))
    ok = True
    for _ in range(40):
        A = random_triangle(); bb = random_beta(); x = point(A, bb)
        mm = abs(m_of(A, x))
        ok &= all(mm >= 2 * bb[k] - 1 - TOL for k in range(3))
    check('D15', '|m| >= 2 beta_k - 1 for each k (40 random interior points)', ok)
    qk, rk = sp.symbols('q_k r_k', positive=True)
    u1, u2 = sp.symbols('u1 u2', real=True)
    U = sp.Matrix([u1, u2])
    check('D16', '(q_k/r_k)(u_k/r_k)(u_k/r_k)^T = (q_k/r_k^3) u_k u_k^T (moment of the inverted charges)',
          zero((qk / rk) * (U / rk) * (U / rk).T - qk / rk ** 3 * U * U.T))


# ================================================================= section 5: Lemma 6
def sec_isotropic():
    ok = True
    for _ in range(5):
        A = random_triangle()
        for (l, n) in ((0, 1), (1, 2), (2, 0)):
            e = sub(A[n], A[l]); al = mp.atan2(e[1], e[0])
            for _ in range(3):
                tt = rnd(0.01, 0.99)
                x = add(A[l], scal(tt, e))
                ok &= close(m_of(A, x), mp.expj(2 * al))
    check('D17', 'on an open edge, m = exp(2 i alpha), alpha the edge direction (45 random edge points)', ok)
    ok = True
    for _ in range(10):
        A = random_triangle()
        for k in range(3):
            l, n = (k + 1) % 3, (k + 2) % 3
            for sc in ('1e-2', '1e-5', '1e-9'):
                t1, t2 = rnd(0.05, 0.95), rnd(0.05, 0.95)
                x = add(A[k], scal(mp.mpf(sc), add(scal(t1, sub(A[l], A[k])), scal(t2 * (1 - t1), sub(A[n], A[k])))))
                bb = bary(A, x)
                y = sub(x, A[k])
                ok &= abs(m_of(A, x) - mp.mpc(y[0], y[1]) ** 2 / dot(y, y)) <= 2 * (1 - bb[k]) + TOL
    check('D18', '|m - exp(2 i theta_k)| <= 2(1 - beta_k) near each vertex (90 random points)', ok)
    res = []
    for _ in range(4):
        A = random_triangle(); eps = mp.mpf('1e-4')
        pts = []
        for k in range(3):
            prv, nxt = A[(k - 1) % 3], A[(k + 1) % 3]
            ein = sub(A[k], prv); L = norm(ein); ein = scal(1 / L, ein)
            for i in range(40):  # edge from prv to A_k, cut off by eps at both ends
                pts.append(add(prv, scal(eps + (L - 2 * eps) * mp.mpf(i) / 40, ein)))
            a0 = mp.atan2(prv[1] - A[k][1], prv[0] - A[k][0])
            a1 = mp.atan2(nxt[1] - A[k][1], nxt[0] - A[k][0])
            gam = a0 - a1
            while gam < 0:
                gam += 2 * mp.pi
            while gam > 2 * mp.pi:
                gam -= 2 * mp.pi
            for i in range(80):  # arc around A_k, clockwise as seen from A_k
                a = a0 - gam * mp.mpf(i) / 80
                pts.append(add(A[k], (eps * mp.cos(a), eps * mp.sin(a))))
        res.append(winding(lambda p: (mp.re(m_of(A, p)), mp.im(m_of(A, p))), pts))
    check('D19', 'winding of m along the boundary of the triangle with the corners cut off is -1 (4 random triangles)',
          all(w == -1 and err < mp.mpf('1e-6') and mx < mp.mpf('0.5') for (w, err, mx) in res))


# ================================================================= section 6: Lemma 7
def sec_model():
    q2, d2, d3 = sp.symbols('q2 d2 d3', positive=True)
    q3 = q2 * d3 ** 2 / d2 ** 2
    y1, y2 = sp.symbols('y1 y2', real=True)
    V0 = q2 / sp.sqrt((y1 + d2) ** 2 + y2 ** 2) + q3 / sp.sqrt((y1 - d3) ** 2 + y2 ** 2)
    g0 = [sp.diff(V0, v).subs({y1: 0, y2: 0}) for v in (y1, y2)]
    H0 = sp.hessian(V0, (y1, y2)).subs({y1: 0, y2: 0})
    C0 = q2 / d2 ** 3 + q3 / d3 ** 3
    check('D20', 'two charges in balance at the origin: grad = 0 and Hessian = C0 diag(2, -1)',
          zero(sp.Matrix(g0)) and zero(H0 - C0 * sp.diag(2, -1)))
    p1, p2, lam, C0s = sp.symbols('p1 p2 lambda C0', positive=True)
    X1, X2 = sp.symbols('X1 X2', real=True)
    rX = sp.sqrt(X1 ** 2 + X2 ** 2)
    eps = C0s * lam ** 3
    L1, L2 = -2 * p1 / lam, p2 / lam
    lhs = C0s * ((p1 + lam * X1) ** 2 - (p2 + lam * X2) ** 2 / 2) + eps / (lam * rX)
    rhs = C0s * (p1 ** 2 - p2 ** 2 / 2) + C0s * lam ** 2 * (X1 ** 2 - X2 ** 2 / 2 + 1 / rX - L1 * X1 - L2 * X2)
    check('D21', 'rescaling: quadratic saddle + charge C0 lambda^3 at p = C0 (p1^2 - p2^2/2) + C0 lambda^2 F_L(X), L = (-2p1, p2)/lambda',
          zero(lhs - rhs))
    LL1, LL2 = sp.symbols('L1 L2', real=True)
    F = X1 ** 2 - X2 ** 2 / 2 + 1 / rX - LL1 * X1 - LL2 * X2
    gF = sp.Matrix([sp.diff(F, X1), sp.diff(F, X2)])
    check('D22', 'grad F_L = (2X1 - X1/r^3 - L1, -X2 - X2/r^3 - L2)',
          zero(gF - sp.Matrix([2 * X1 - X1 / rX ** 3 - LL1, -X2 - X2 / rX ** 3 - LL2])))
    c = sp.symbols('c', positive=True)
    Aa, Bb = sp.symbols('A B', positive=True)
    g = c ** sp.Rational(2, 3) * (Aa / (2 - c) ** 2 + Bb / (1 + c) ** 2)
    Xc = (LL1 / (2 - c), -LL2 / (1 + c))
    ok = zero(c ** sp.Rational(-2, 3) * g.subs({Aa: LL1 ** 2, Bb: LL2 ** 2}) - (Xc[0] ** 2 + Xc[1] ** 2))
    rr = sp.symbols('r', positive=True)
    gsub = [2 * Xc[0] - Xc[0] * c - LL1, -Xc[1] - Xc[1] * c - LL2]
    ok &= zero(sp.Matrix(gsub))
    check('D23', 'X = (L1/(2-c), -L2/(1+c)) solves grad F_L = 0 with 1/r^3 = c, and |X|^2 = c^(-2/3) g(c)', ok)
    HF = sp.hessian(F, (X1, X2))
    U = sp.Matrix([X1, X2]) / rX
    check('D24', 'Hess F_L = diag(2 - c, -1 - c) + 3c u u^T with c = 1/r^3; trace = 1 + c',
          zero(HF - (sp.diag(2 - 1 / rX ** 3, -1 - 1 / rX ** 3) + 3 / rX ** 3 * U * U.T)) and zero(HF.trace() - (1 + 1 / rX ** 3)))
    u1, u2, a, b = sp.symbols('u1 u2 a b', real=True)
    Hc = sp.diag(2 - c, -1 - c) + 3 * c * sp.Matrix([[u1 ** 2, u1 * u2], [u1 * u2, u2 ** 2]])
    detf = (2 - c) * (-1 - c) + 3 * c * ((-1 - c) * a + (2 - c) * b)
    gp_ab = sp.Rational(2, 3) / c * (a + b) + 2 * a / (2 - c) - 2 * b / (1 + c)
    ok = zero(Hc.det() - detf.subs({a: u1 ** 2, b: u2 ** 2}))
    ok &= zero(detf - (-sp.Rational(3, 2) * c * (2 - c) * (1 + c) * gp_ab) - (2 - c) * (-1 - c) * (1 - a - b))
    aa = c ** sp.Rational(2, 3) * Aa / (2 - c) ** 2; bb = c ** sp.Rational(2, 3) * Bb / (1 + c) ** 2
    ok &= zero(sp.diff(g, c) - gp_ab.subs({a: aa, b: bb}))
    check('D25', 'det H = (2-c)(-1-c) + 3c((-1-c)a + (2-c)b) = -(3c/2)(2-c)(1+c) g\'(c) + (2-c)(-1-c)(1-a-b)', ok)
    gp = c ** sp.Rational(2, 3) / (3 * c) * (4 * Aa * (1 + c) / (2 - c) ** 3 - 2 * Bb * (2 * c - 1) / (1 + c) ** 3)
    check('D26', "g'(c) = (c^(2/3)/(3c)) [4A(1+c)/(2-c)^3 - 2B(2c-1)/(1+c)^3]", zero(sp.diff(g, c) - gp))
    R = 2 * (1 + c) ** 4 / ((2 - c) ** 3 * (2 * c - 1))
    check('D27', "g'(c) = (2(2c-1) c^(2/3)/(3c(1+c)^3)) (A R(c) - B), R = 2(1+c)^4/((2-c)^3(2c-1))",
          zero(gp - 2 * (2 * c - 1) * c ** sp.Rational(2, 3) / (3 * c * (1 + c) ** 3) * (Aa * R - Bb)))
    check('D28', "R'(c)/R(c) = 4/(1+c) + 3/(2-c) - 2/(2c-1) = 3(7c-5)/((1+c)(2-c)(2c-1))",
          zero(sp.diff(R, c) / R - (4 / (1 + c) + 3 / (2 - c) - 2 / (2 * c - 1)))
          and zero(4 / (1 + c) + 3 / (2 - c) - 2 / (2 * c - 1) - 3 * (7 * c - 5) / ((1 + c) * (2 - c) * (2 * c - 1))))
    check('D29', 'R(5/7) = 512/27', sp.nsimplify(R.subs(c, sp.Rational(5, 7))) == flip('r57') * sp.Rational(512, 27))
    ok = True
    for _ in range(50):
        cc = rnd(2.0001, 200); A_ = rnd(0.01, 10); B_ = rnd(0, 10)
        ok &= (1 + cc) / (2 - cc) ** 3 < 0 and (2 * cc - 1) > 0
        ok &= mp.mpf(4) * A_ * (1 + cc) / (2 - cc) ** 3 - 2 * B_ * (2 * cc - 1) / (1 + cc) ** 3 < 0
    check('D30', "g' < 0 on (2, inf) (50 random c, A, B)", ok)
    # numeric: all critical points of F_L from the degree 12 polynomial in y = c^(1/3)
    yv = sp.symbols('y', positive=True)
    P = sp.Poly(yv ** 2 * (Aa * (1 + yv ** 3) ** 2 + Bb * (2 - yv ** 3) ** 2) - (2 - yv ** 3) ** 2 * (1 + yv ** 3) ** 2, yv)
    coeffs = [sp.lambdify((Aa, Bb), co, 'mpmath') for co in P.all_coeffs()]
    ok = True; nmin_cases = 0; nnomin_small = 0; stats = {}
    for it in range(80):
        if it % 2 == 0:  # broad sample of L
            L1v = mp.mpf(RNG.choice([-1, 1])) * mp.power(10, rnd(-1, 1))
            L2v = L1v * mp.mpf(RNG.choice([-1, 1])) * mp.power(10, rnd(-1, 2))
        else:  # the thin band of L where a minimum exists: small |L1|, |L2| near 2
            L1v = mp.mpf(RNG.choice([-1, 1])) * mp.power(10, rnd(-3, -0.3))
            L2v = mp.mpf(RNG.choice([-1, 1])) * rnd(1.5, 3)
        Av, Bv = L1v ** 2, L2v ** 2
        roots = mp.polyroots([f(Av, Bv) for f in coeffs], maxsteps=500, extraprec=500)
        cs = sorted(mp.re(z) ** 3 for z in roots if abs(mp.im(z)) < mp.mpf('1e-25') and mp.re(z) > 0)
        mins = 0; n02 = 0; n2 = 0
        for cv in cs:
            X = (L1v / (2 - cv), -L2v / (1 + cv)); r = norm(X)
            ok &= close(r ** 3 * cv, 1)
            gr = (2 * X[0] - X[0] / r ** 3 - L1v, -X[1] - X[1] / r ** 3 - L2v)
            ok &= norm(gr) < mp.mpf('1e-35') * (1 + abs(L1v) + abs(L2v))
            u = scal(1 / r, X)
            H = [[2 - cv + 3 * cv * u[0] ** 2, 3 * cv * u[0] * u[1]], [3 * cv * u[0] * u[1], -1 - cv + 3 * cv * u[1] ** 2]]
            det = H[0][0] * H[1][1] - H[0][1] ** 2
            gpv = cv ** (mp.mpf(2) / 3) / (3 * cv) * (4 * Av * (1 + cv) / (2 - cv) ** 3 - 2 * Bv * (2 * cv - 1) / (1 + cv) ** 3)
            ok &= close(det, -mp.mpf(3) / 2 * cv * (2 - cv) * (1 + cv) * gpv, mp.mpf('1e-30'))
            if cv < 2:
                n02 += 1
            else:
                n2 += 1
            if det > 0 and H[0][0] + H[1][1] > 0:
                mins += 1
                ok &= mp.mpf(1) / 2 < cv < 2
        ok &= n2 == 1 and n02 in (1, 3) and mins <= 1 and mins == (n02 - 1) // 2
        if Bv / Av < mp.mpf(512) / 27:
            ok &= mins == 0; nnomin_small += 1
        nmin_cases += mins
        stats[(n02 + n2, mins)] = stats.get((n02 + n2, mins), 0) + 1
    check('D31', 'F_L: 1 or 3 critical points with c < 2, exactly 1 with c > 2, at most one minimum, '
          'minima only for 1/2 < c < 2, none if L2^2/L1^2 < 512/27 (80 random L, roots of a degree 12 polynomial)',
          ok and nmin_cases > 5, '(critical points, minima): counts %s' % sorted(stats.items()))


# ================================================================= section 7: Lemma 8 (exclusion)
def sec_exclusion():
    dx, dy = sp.symbols('dx dy', real=True)
    r2 = dx ** 2 + dy ** 2
    th, r = sp.symbols('theta r', positive=True)
    subs = {dx: r * sp.cos(th), dy: r * sp.sin(th)}
    c1 = 1 - 2 * dy ** 2 / r2; c2 = 2 * dx ** 2 / r2 - 1; s2 = 2 * dx * dy / r2
    check('D32', 'cos 2theta = 1 - 2dy^2/r^2 = 2dx^2/r^2 - 1, sin 2theta = 2 dx dy/r^2',
          zero(c1 - c2) and zero(c1.subs(subs) - sp.cos(2 * th)) and zero(s2.subs(subs) - sp.sin(2 * th)))
    b2, b3, a, b = sp.symbols('beta2 beta3 a b', real=True)
    x = b2 * sp.Matrix([1, 0]) + b3 * sp.Matrix([a, b])
    check('D33', 'x = beta2 A2 + beta3 A3 = (beta2 + a beta3, b beta3) when A1 = 0',
          zero(x - sp.Matrix([b2 + a * b3, b * b3])))


# ================================================================= section 8: Lemmas 10 and 12 (Jacobian, injectivity)
def sec_jacobian():
    b2, b3 = sp.symbols('beta2 beta3', positive=True)
    a, b = sp.symbols('a b', real=True)
    A = [sp.Matrix([0, 0]), sp.Matrix([1, 0]), sp.Matrix([a, b])]
    be = [1 - b2 - b3, b2, b3]
    x = be[1] * A[1] + be[2] * A[2]
    y = [x - A[k] for k in range(3)]
    r2 = [y[k].dot(y[k]) for k in range(3)]
    G = {k: sp.log(be[k - 1] / be[0]) + sp.Rational(3, 2) * sp.log(r2[k - 1] / r2[0]) for k in (2, 3)}
    e = {2: A[1] - A[0], 3: A[2] - A[0]}
    bv = {2: b2, 3: b3}
    ok = True; okr = True
    for k in (2, 3):
        rho_k = sp.exp(G[k])
        for j in (2, 3):
            form = flip('jac') / be[0] + 3 * y[k - 1].dot(e[j]) / r2[k - 1] - 3 * y[0].dot(e[j]) / r2[0] + (1 / be[k - 1] if k == j else 0)
            ok &= zero(sp.diff(G[k], bv[j]) - form)
            okr &= zero(sp.diff(rho_k, bv[j]) - rho_k * sp.diff(G[k], bv[j]))
    check('D34', 'dG_k/dbeta_j = 1/beta1 + delta_kj/beta_k + 3 y_k.e_j/r_k^2 - 3 y_1.e_j/r_1^2', ok)
    check('D35', 'd rho_k/d beta_j = rho_k dG_k/d beta_j', okr)
    ok = True; okd = True
    for _ in range(25):
        At = random_triangle(); bb = random_beta(); xx = point(At, bb)
        rho = rho_of(At, bb); q = [mp.mpf(1), rho[0], rho[1]]
        H = hess(At, q, xx)
        J = jac_G(At, bb)
        E = [[At[1][0] - At[0][0], At[2][0] - At[0][0]], [At[1][1] - At[0][1], At[2][1] - At[0][1]]]
        yk = {k: sub(xx, At[k - 1]) for k in (2, 3)}
        N = [[-yk[k][i] / norm(yk[k]) ** 3 for k in (2, 3)] for i in range(2)]
        for i in range(2):
            for j in range(2):
                lhs = sum(H[i][l] * E[l][j] for l in range(2))
                rhs = -sum(N[i][l] * q[l + 1] * J[(l + 2, j + 2)] for l in range(2))
                ok &= close(lhs, rhs, mp.mpf('1e-35'))
        lamb = sum(q[k] / norm(sub(xx, At[k])) ** 3 for k in range(3))
        mm = abs(m_of(At, xx))
        detJ = J[(2, 2)] * J[(3, 3)] - J[(2, 3)] * J[(3, 2)]
        detE = E[0][0] * E[1][1] - E[0][1] * E[1][0]; detN = N[0][0] * N[1][1] - N[0][1] * N[1][0]
        okd &= close(detJ, lamb ** 2 * (1 - 9 * mm ** 2) * detE / (4 * detN * q[1] * q[2]), mp.mpf('1e-35'))
    check('D36', 'H E = -q1 N diag(rho) DG, and det DG = lambda^2 (1 - 9|m|^2) det E/(4 det N rho2 rho3) (25 random points)', ok and okd)
    ok = True
    for _ in range(6):
        At = random_triangle(); bx = random_beta()
        d = (rnd(-0.03, 0.03), rnd(-0.03, 0.03))
        by = [bx[0] - d[0] - d[1], bx[1] + d[0], bx[2] + d[1]]
        if min(by) <= 0:
            continue
        Gf = lambda bb: [mp.log(v) for v in rho_of(At, bb)]
        Gx, Gy = Gf(bx), Gf(by)
        seg = lambda t: [bx[0] - t * (d[0] + d[1]), bx[1] + t * d[0], bx[2] + t * d[1]]
        Mm = {(k, j): mp.quad(lambda t: jac_G(At, seg(t))[(k, j)], [0, 1]) for k in (2, 3) for j in (2, 3)}
        for k in (2, 3):
            ok &= close(Gy[k - 2] - Gx[k - 2], Mm[(k, 2)] * d[0] + Mm[(k, 3)] * d[1], mp.mpf('1e-35'))
    check('D37', 'G(y) - G(x) = M (y - x) with M the average of DG along the segment (mean-value matrix, 6 random pairs)', ok)


# ================================================================= section 9: Lemma 13 (valley)
def sec_valley():
    tau, sig = sp.symbols('tau sigma')
    cs = {}
    f = 0
    for j in range(5):
        for k in range(5 - j):
            if (j, k) in ((0, 0), (0, 1)):
                continue  # f_sigma(0,0) = 0: the base point is on the valley floor
            cs[(j, k)] = sp.Symbol('c%d%d' % (j, k))
            f += cs[(j, k)] * tau ** j * sig ** k / (sp.factorial(j) * sp.factorial(k))
    s1, s2, s3 = sp.symbols('s1 s2 s3')
    S = s1 * tau + s2 * tau ** 2 + s3 * tau ** 3
    fs = sp.expand(sp.diff(f, sig).subs(sig, S))
    sol = {}
    for n, sv in ((1, s1), (2, s2), (3, s3)):
        co = sp.expand(fs.coeff(tau, n).subs(sol))
        sol[sv] = sp.solve(co, sv)[0]
    psi = sp.expand(f.subs(sig, S).subs(sol))
    dpsi = {n: sp.factorial(n) * psi.coeff(tau, n) for n in range(1, 5)}
    c = lambda j, k: cs[(j, k)]
    a = -c(1, 1) / c(0, 2)
    check('D38', "sigma*'(0) = -V_ts/V_ss, so gamma' = w = t - (V_ts/V_ss) s", zero(sol[s1] - a))
    check('D39', 'D2V[w, s] = V_ts + sigma*\' V_ss = 0 on the valley floor', zero(c(1, 1) + a * c(0, 2)))
    check('D40', "psi' = DV[t] = DV[w] on the floor", zero(dpsi[1] - c(1, 0)))
    D2ww = c(2, 0) + 2 * a * c(1, 1) + a ** 2 * c(0, 2)
    check('D41', "psi'' = D2V[w,w] = V_tt - V_ts^2/V_ss", zero(dpsi[2] - D2ww) and zero(D2ww - (c(2, 0) - c(1, 1) ** 2 / c(0, 2))))
    D3www = c(3, 0) + 3 * a * c(2, 1) + 3 * a ** 2 * c(1, 2) + a ** 3 * c(0, 3)
    check('D42', "psi''' = D3V[w,w,w]", zero(dpsi[3] - D3www))
    D3wws = c(2, 1) + 2 * a * c(1, 2) + a ** 2 * c(0, 3)
    D4 = c(4, 0) + 4 * a * c(3, 1) + 6 * a ** 2 * c(2, 2) + 4 * a ** 3 * c(1, 3) + a ** 4 * c(0, 4)
    check('D43', "psi'''' = D4V[w,w,w,w] - 3 D3V[w,w,s]^2/V_ss", zero(dpsi[4] - (D4 + flip('psi4') * (-3) * D3wws ** 2 / c(0, 2))))
    check('D44', "sigma*''(0) = -D3V[w,w,s]/V_ss", zero(2 * sol[s2] + D3wws / c(0, 2)))
    # D45: expansions in terms of V_ttt, ... with a_code = V_ts/V_ss, w = t - a_code s, t and s arbitrary
    t1, t2, u1, u2, ac = sp.symbols('t1 t2 s1 s2 a', real=True)
    tv = (t1, t2); sv = (u1, u2); wv = (t1 - ac * u1, t2 - ac * u2)
    T3 = {}; T4 = {}
    import itertools
    for idx in itertools.combinations_with_replacement(range(2), 3):
        T3[idx] = sp.Symbol('T' + ''.join(map(str, idx)))
    for idx in itertools.combinations_with_replacement(range(2), 4):
        T4[idx] = sp.Symbol('Q' + ''.join(map(str, idx)))
    def con3(u, v, w):
        return sum(T3[tuple(sorted((i, j, k)))] * u[i] * v[j] * w[k] for i in range(2) for j in range(2) for k in range(2))
    def con4(u, v, w, z):
        return sum(T4[tuple(sorted((i, j, k, l)))] * u[i] * v[j] * w[k] * z[l]
                   for i in range(2) for j in range(2) for k in range(2) for l in range(2))
    V3 = lambda key: con3(*[tv if ch == 't' else sv for ch in key])
    V4 = lambda key: con4(*[tv if ch == 't' else sv for ch in key])
    ok = zero(con3(wv, wv, wv) - (V3('ttt') - 3 * ac * V3('tts') + 3 * ac ** 2 * V3('tss') - ac ** 3 * V3('sss')))
    ok &= zero(con3(wv, wv, sv) - (V3('tts') - 2 * ac * V3('tss') + ac ** 2 * V3('sss')))
    ok &= zero(con4(wv, wv, wv, wv) - (V4('tttt') - 4 * ac * V4('ttts') + 6 * ac ** 2 * V4('ttss') - 4 * ac ** 3 * V4('tsss') + ac ** 4 * V4('ssss')))
    check('D45', 'multilinear expansions of D3V[w,w,w], D3V[w,w,s], D4V[w^4] for w = t - a s, any t, s', ok)


# ================================================================= section 10: Lemma 14 and the archived certificate
def sec_certificate():
    lo, hi = Fraction(0.8660254037844385), Fraction(0.8660254037844387)
    meta = json.load(open(os.path.join(HERE, 'out', 'c3_equi.json')))
    ok = (2 * lo) ** 2 < 3 < (2 * hi) ** 2 and Fraction(0.5) == Fraction(1, 2)
    ok &= meta['shape'] == [0.5, 0.5, 0.8660254037844385, 0.8660254037844387]
    check('D46', 'the shape box of out/c3_equi.json contains the equilateral triangle (1/2, sqrt(3)/2) (exact rationals)', ok,
          'b in [%s, %s]' % (mp.nstr(mp.mpf(lo.numerator) / lo.denominator, 20), mp.nstr(mp.mpf(hi.numerator) / hi.denominator, 20)))
    import numpy as np
    L = np.load(os.path.join(HERE, 'out', 'c3_equi_leaves.npy'))
    kind = L[:, 4]
    inside = lambda B: (B[:, 0] > 0).all() and (B[:, 2] > 0).all() and all(Fraction(float(u)) + Fraction(float(v)) < 1 for u, v in zip(B[:, 1], B[:, 3]))
    ok = inside(L[:, 0:4]) and inside(L[kind == 1, 5:9])
    ok &= set(np.unique(kind).tolist()) == {1.0, 3.0, 4.0} and len(L) == meta['nleaves']
    J = L[kind == 1]
    ok &= bool(((J[:, 5] <= J[:, 0]) & (J[:, 1] <= J[:, 6]) & (J[:, 7] <= J[:, 2]) & (J[:, 3] <= J[:, 8])).all())
    sites = [(mp.mpf(0), mp.mpf(0)), (mp.mpf(1), mp.mpf(0)), (mp.mpf(1) / 2, mp.mpf(lo.numerator) / lo.denominator),
             (mp.mpf(1) / 2, mp.mpf(hi.numerator) / hi.denominator)]
    margin = mp.inf
    for row in L[kind >= 3]:
        cc = (mp.mpf(row[9]), mp.mpf(row[10])); t = (mp.mpf(row[11]), mp.mpf(row[12])); s = (mp.mpf(row[13]), mp.mpf(row[14]))
        rad = mp.mpf(row[15]) * norm(t) + mp.mpf(row[16]) * norm(s)
        margin = min(margin, min(norm(sub(cc, A)) - rad for A in sites))
    ok &= margin > 0
    check('D47', 'archived certificate: every leaf box and every J region lies inside the open simplex, '
          'each J region contains its box, no valley cell contains a site', ok,
          '%d leaves (J %d, V %d); min beta over leaves %.6g; site-to-cell margin >= %s' % (
              len(L), int((kind == 1).sum()), int((kind >= 3).sum()), float(min(L[:, 0].min(), L[:, 2].min(), (1 - L[:, 1] - L[:, 3]).min())),
              mp.nstr(margin, 4)))


# ================================================================= appendix: derivatives of 1/r, cusp coefficient
def sec_appendix():
    y1, y2 = sp.symbols('y1 y2', real=True)
    Y = (y1, y2); r = sp.sqrt(y1 ** 2 + y2 ** 2)
    dl = lambda i, j: 1 if i == j else 0
    import itertools
    def form(idx):
        n = len(idx)
        if n == 1:
            i, = idx; return -Y[i] / r ** 3
        if n == 2:
            i, j = idx; return 3 * Y[i] * Y[j] / r ** 5 - dl(i, j) / r ** 3
        if n == 3:
            i, j, k = idx
            return -15 * Y[i] * Y[j] * Y[k] / r ** 7 + 3 * (dl(i, j) * Y[k] + dl(i, k) * Y[j] + dl(j, k) * Y[i]) / r ** 5
        i, j, k, l = idx
        s6 = (dl(i, j) * Y[k] * Y[l] + dl(i, k) * Y[j] * Y[l] + dl(i, l) * Y[j] * Y[k]
              + dl(j, k) * Y[i] * Y[l] + dl(j, l) * Y[i] * Y[k] + dl(k, l) * Y[i] * Y[j])
        p3 = dl(i, j) * dl(k, l) + dl(i, k) * dl(j, l) + dl(i, l) * dl(j, k)
        return 105 * Y[i] * Y[j] * Y[k] * Y[l] / r ** 9 - 15 * s6 / r ** 7 + 3 * p3 / r ** 5
    ok = True
    for n in range(1, 5):
        for idx in itertools.product(range(2), repeat=n):
            ok &= zero(sp.diff(1 / r, *[Y[i] for i in idx]) - form(idx))
    check('D48', 'derivative tensors of 1/|y| of orders 1 to 4 (all components)', ok)
    V4, V3, Vs = sp.symbols('V_tttt V_tts V_ss', real=True)
    check('D49', "kappa = V_tttt/24 - V_tts^2/(8 V_ss) = psi''''/24 when V_ts = 0", zero(V4 / 24 - V3 ** 2 / (8 * Vs) - (V4 - 3 * V3 ** 2 / Vs) / 24))
    ps, rr = sp.symbols('psi r', positive=True)
    subs = {y1: rr * sp.cos(ps), y2: rr * sp.sin(ps)}
    C = sp.cos(ps)
    P3 = (5 * C ** 3 - 3 * C) / 2; P4 = (35 * C ** 4 - 30 * C ** 2 + 3) / 8
    ok = zero(form((0, 0, 0)).subs(subs) + 6 * P3 / rr ** 4)
    ok &= zero(form((0, 0, 1)).subs(subs) + 3 * sp.sin(ps) * (5 * C ** 2 - 1) / rr ** 4)
    ok &= zero(form((0, 0, 0, 0)).subs(subs) - 24 * P4 / rr ** 5)
    check('D50', 'D3(1/r)[t,t,t] = -6 P3(cos psi)/r^4, D3(1/r)[t,t,s] = -3 sin psi (5cos^2 psi - 1)/r^4, D4(1/r)[t^4] = 24 P4(cos psi)/r^5', ok)
    p = sp.symbols('p1:4', real=True)
    u = [sp.Matrix([sp.cos(v), sp.sin(v)]) for v in p]
    w = [sp.sin(p[2] - p[1]), sp.sin(p[0] - p[2]), sp.sin(p[1] - p[0])]
    crs = lambda a_, b_: a_[0] * b_[1] - a_[1] * b_[0]
    ok = zero(sum((w[k] * u[k] for k in range(3)), sp.zeros(2, 1)))
    ok &= all(zero(w[k] - crs(u[(k + 1) % 3], u[(k + 2) % 3])) for k in range(3))
    check('D51', 'sum_k w_k u_k = 0 with w_k = sin(psi_n - psi_l) = u_l x u_n (cyclic)', ok)
    # D52 numeric: fold configurations of cuspset.py
    done = 0; ok = True; tries = 0
    while done < 12 and tries < 5000:
        tries += 1
        psv = [rnd(0, 2 * mp.pi) for _ in range(3)]
        P = [mp.expj(2 * v) for v in psv]
        X0 = mp.mpc(-1, 0) / 3
        ar = lambda a_, b_, c_: mp.im(mp.conj(b_ - a_) * (c_ - a_))
        tot = ar(P[0], P[1], P[2])
        beta = [ar(X0, P[1], P[2]) / tot, ar(P[0], X0, P[2]) / tot, ar(P[0], P[1], X0) / tot]
        w = [mp.sin(psv[2] - psv[1]), mp.sin(psv[0] - psv[2]), mp.sin(psv[1] - psv[0])]
        sg = 1 if w[0] > 0 else -1
        w = [sg * v for v in w]
        if min(beta) <= mp.mpf('0.01') or min(w) <= mp.mpf('0.01'):
            continue
        done += 1
        uu = [(mp.cos(v), mp.sin(v)) for v in psv]
        r = [w[k] / beta[k] for k in range(3)]
        A = [scal(-r[k], uu[k]) for k in range(3)]
        q = [beta[k] * r[k] ** 3 for k in range(3)]
        x = (mp.mpf(0), mp.mpf(0))
        ok &= close(sum(beta[k] * mp.mpc(*uu[k]) ** 2 for k in range(3)), X0)
        g = grad(A, q, x); ok &= norm(g) < TOL * 10
        Vtt = DV(A, q, x, [E1, E1]); Vts = DV(A, q, x, [E1, E2]); Vss = DV(A, q, x, [E2, E2])
        ok &= abs(Vtt) < TOL * 10 and abs(Vts) < TOL * 10 and close(Vss, 1)
        G = sum(beta[k] ** 2 * (5 * mp.cos(psv[k]) ** 3 - 3 * mp.cos(psv[k])) / 2 / w[k] for k in range(3))
        P4 = lambda cc: (35 * cc ** 4 - 30 * cc ** 2 + 3) / 8
        bb = sum(beta[k] ** 2 * mp.sin(psv[k]) * (5 * mp.cos(psv[k]) ** 2 - 1) / w[k] for k in range(3))
        K = sum(beta[k] ** 3 * P4(mp.cos(psv[k])) / w[k] ** 2 for k in range(3)) - mp.mpf(9) / 8 * bb ** 2
        Vttt = DV(A, q, x, [E1, E1, E1]); Vtts = DV(A, q, x, [E1, E1, E2]); Vtttt = DV(A, q, x, [E1] * 4)
        ok &= close(Vttt, -6 * G) and close(Vtts, -3 * bb)
        ok &= close(Vtttt - 3 * Vtts ** 2 / Vss, 24 * K * flip('cusp'))
    check('D52', "fold configurations: grad = 0, kernel t = (1,0), V_ss = 1, V_ttt = -6G, psi'''' = 24K (cuspset.py) (12 random)",
          ok and done == 12)


# ================================================================= section X: the programs compute these formulas
def sec_code():
    import warnings
    warnings.filterwarnings('ignore')
    sys.path.insert(0, HERE)
    import numpy as np
    import cert3, lib3, cuspset
    from iv import I
    rel = lambda a, b: abs(mp.mpf(float(a)) - b) <= mp.mpf('1e-11') * (1 + abs(b))
    ok1 = ok2 = ok3 = ok4 = ok5 = ok6 = True
    for _ in range(8):
        At = random_triangle(); be = random_beta()
        af, bf = float(At[2][0]), float(At[2][1])
        At = [At[0], At[1], (mp.mpf(af), mp.mpf(bf))]
        b2f, b3f = float(be[1]), float(be[2])
        be = [1 - mp.mpf(b2f) - mp.mpf(b3f), mp.mpf(b2f), mp.mpf(b3f)]
        sh = cert3.Shape(af, af, bf, bf)
        B = np.array([[b2f], [b2f], [b3f], [b3f]])
        Jc = cert3.jac_entries(sh, B); Jm = jac_G(At, be)
        ok1 &= all(rel(Jc[key].mid[0], Jm[key]) for key in Jm)
        Rc = cert3.rho(sh, B); Rm = rho_of(At, be)
        ok2 &= rel(Rc[0].mid[0], Rm[0]) and rel(Rc[1].mid[0], Rm[1])
        x = point(At, be)
        mm = abs(m_of(At, x))
        ok4 &= rel(lib3.mu(np.array([[float(a) for a in At[0]], [1.0, 0.0], [af, bf]]), np.array([[float(x[0]), float(x[1])]]))[0],
                   (1 - mm) / (1 + mm) - mp.mpf(1) / 2)
        lb = cert3.m2_lower(sh, B)[0]
        ok5 &= mp.mpf(float(lb)) <= mm ** 2 * (1 + mp.mpf('1e-14')) and rel(lb, mm ** 2)
        ph = RNG.random() * 6.283
        tf = (np.cos(ph), np.sin(ph)); sf = (-np.sin(ph) * 1.3, np.cos(ph) * 0.7)
        q = [mp.mpf(1), mp.mpf(float(Rm[0])), mp.mpf(float(Rm[1]))]
        qI = (I.c(np.array([1.0])), I.c(np.array([float(Rm[0])])), I.c(np.array([float(Rm[1])])))
        P = (I.c(np.array([float(x[0])])), I.c(np.array([float(x[1])])))
        xf = (mp.mpf(float(x[0])), mp.mpf(float(x[1])))
        D = cert3.tensors(sh, qI, P, (np.array([tf[0]]), np.array([tf[1]])), (np.array([sf[0]]), np.array([sf[1]])))
        vec = {'t': (mp.mpf(tf[0]), mp.mpf(tf[1])), 's': (mp.mpf(sf[0]), mp.mpf(sf[1]))}
        for key, val in D.items():
            ok3 &= rel(val.mid[0], DV(At, q, xf, [vec[ch] for ch in key]))
        Afl = np.array([[0.0, 0.0], [1.0, 0.0], [af, bf]])
        ql = lib3.lami(Afl, np.array([[float(x[0]), float(x[1])]]))[0][0]
        qm = [be[k] * norm(sub(x, At[k])) ** 3 for k in range(3)]
        ok6 &= all(rel(ql[k], qm[k] / sum(qm)) for k in range(3))
    check('X1', 'cert3.jac_entries computes D34', ok1)
    check('X2', 'cert3.rho computes D7', ok2)
    check('X3', 'cert3.tensors computes D48 contracted with t, s (all 13 directional derivatives)', ok3)
    check('X4', 'lib3.mu = lambda_min/lambda_max(M) - 1/2 = (1-|m|)/(1+|m|) - 1/2 (D12, D13)', ok4)
    check('X5', 'cert3.m2_lower is a lower bound for |m|^2 (D32) and tight on a point box', ok5)
    check('X6', 'lib3.lami computes Z(x) = [beta_k r_k^3] (D7, D8)', ok6)
    ok = True; n = 0
    while n < 6:
        psv = np.array([RNG.random() * 6.283 for _ in range(3)])
        Gc, Kc, Kn, valid, b, w, r = cuspset.GK(psv[None])
        if not valid[0] or b.min() < 0.01 or w.min() < 0.01:
            continue
        n += 1
        beta = [mp.mpf(float(v)) for v in b[0]]; ww = [mp.mpf(float(v)) for v in w[0]]
        ps = [mp.mpf(float(v)) for v in psv]
        G = sum(beta[k] * (5 * mp.cos(ps[k]) ** 3 - 3 * mp.cos(ps[k])) / 2 / (ww[k] / beta[k]) for k in range(3))
        P4 = lambda cc: (35 * cc ** 4 - 30 * cc ** 2 + 3) / 8
        bb = sum(beta[k] ** 2 * mp.sin(ps[k]) * (5 * mp.cos(ps[k]) ** 2 - 1) / ww[k] for k in range(3))
        K = sum(beta[k] ** 3 * P4(mp.cos(ps[k])) / ww[k] ** 2 for k in range(3)) - mp.mpf(9) / 8 * bb ** 2
        ok &= abs(mp.mpf(float(Gc[0])) - G) < mp.mpf('1e-9') * (1 + abs(G)) and abs(mp.mpf(float(Kc[0])) - K) < mp.mpf('1e-9') * (1 + abs(K))
    check('X7', 'cuspset.GK computes G and K of D52', ok)
    import verify_arb3 as VA
    ok = True
    for _ in range(4):
        At = random_triangle(); be = random_beta()
        af, bf = float(At[2][0]), float(At[2][1])
        At = [At[0], At[1], (mp.mpf(af), mp.mpf(bf))]
        b2f, b3f = float(be[1]), float(be[2])
        be = [1 - mp.mpf(b2f) - mp.mpf(b3f), mp.mpf(b2f), mp.mpf(b3f)]
        T = VA.Tri([af, af, bf, bf])
        Jm = jac_G(At, be)
        dt = VA.jac_det(T, (b2f, b2f, b3f, b3f))
        detm = Jm[(2, 2)] * Jm[(3, 3)] - Jm[(2, 3)] * Jm[(3, 2)]
        mid = (mp.mpf(float(dt.lo)) + mp.mpf(float(dt.hi))) / 2
        ok &= abs(mid - detm) <= mp.mpf('1e-11') * (1 + abs(detm))
        x = point(At, be); Rm = rho_of(At, be)
        qI = [VA.Iv(1), VA.Iv(float(Rm[0])), VA.Iv(float(Rm[1]))]
        q = [mp.mpf(1), mp.mpf(float(Rm[0])), mp.mpf(float(Rm[1]))]
        xf = (mp.mpf(float(x[0])), mp.mpf(float(x[1])))
        tt = (VA.Iv(0.6), VA.Iv(0.8)); ss = (VA.Iv(-0.8), VA.Iv(0.6))
        D = VA.derivs(T, qI, (VA.Iv(float(x[0])), VA.Iv(float(x[1]))), tt, ss)
        vec = {'t': (mp.mpf(0.6), mp.mpf(0.8)), 's': (mp.mpf(-0.8), mp.mpf(0.6))}
        for key, val in D.items():
            want = DV(At, q, xf, [vec[ch] for ch in key])
            mid = (mp.mpf(float(val.lo)) + mp.mpf(float(val.hi))) / 2
            ok &= abs(mid - want) <= mp.mpf('1e-11') * (1 + abs(want))
    check('X8', 'verify_arb3.jac_det and verify_arb3.derivs compute D34 and D48', ok)

    import inspect, re
    import run_cert2
    vt = sp.symbols('V_ts V_ss V_ttt V_tts V_tss V_sss V_tttt V_ttts V_ttss V_tsss V_ssss', real=True)
    keys = ['ts', 'ss', 'ttt', 'tts', 'tss', 'sss', 'tttt', 'ttts', 'ttss', 'tsss', 'ssss']

    class Sym:
        """Stands in for an interval: holds a SymPy expression; floats in the source become exact rationals."""
        def __init__(self, e):
            self.e = e
        @staticmethod
        def w(o):
            return o if isinstance(o, Sym) else Sym(sp.Rational(o))
        def __add__(s_, o): return Sym(s_.e + Sym.w(o).e)
        __radd__ = __add__
        def __sub__(s_, o): return Sym(s_.e - Sym.w(o).e)
        def __rsub__(s_, o): return Sym(Sym.w(o).e - s_.e)
        def __mul__(s_, o): return Sym(s_.e * Sym.w(o).e)
        __rmul__ = __mul__
        def __truediv__(s_, o): return Sym(s_.e / Sym.w(o).e)
        def __neg__(s_): return Sym(-s_.e)
        def sq(s_): return Sym(s_.e ** 2)
    V = dict(zip(keys, vt))
    ac = V['ts'] / V['ss']
    want = {'w3': V['ttt'] - 3 * ac * V['tts'] + 3 * ac ** 2 * V['tss'] - ac ** 3 * V['sss'],
            'w3s': V['tts'] - 2 * ac * V['tss'] + ac ** 2 * V['sss'],
            'w4': V['tttt'] - 4 * ac * V['ttts'] + 6 * ac ** 2 * V['ttss'] - 4 * ac ** 3 * V['tsss'] + ac ** 4 * V['ssss']}
    want['f4'] = want['w4'] - 3 * want['w3s'] ** 2 / V['ss']
    ok = True; seen = []
    for fn in (run_cert2.valley_vec, cert3.valley_ok, VA.valley_check):
        ns = {'D': {k: Sym(v) for k, v in V.items()}, 'sq': lambda z: z.sq()}
        got = set()
        for line in inspect.getsource(fn).splitlines():
            mt = re.match(r'^\s*(a|a2|w3|w4|w3s|f4)\s*=\s*(.+?)\s*$', line)
            if mt:
                ns[mt.group(1)] = eval(mt.group(2), {}, ns)
                got.add(mt.group(1))
        ok &= {'a', 'w3', 'w4', 'w3s', 'f4'} <= got
        for k in ('w3', 'w3s', 'w4', 'f4'):
            ok &= zero(ns[k].e - want[k])
        seen.append(fn.__module__ + '.' + fn.__name__)
    check('X9', 'the valley tests evaluate D45 and D43 (their source lines executed on symbols): ' + ', '.join(seen), ok)


# ================================================================= N1: a valley box on which Z is two-to-one
def sec_note():
    """Line 50 of three-charges.md said the inverse map is one-to-one in every leaf box. Here is a valley
    leaf of the archived equilateral certificate that holds a minimum x and a saddle y with Z(x) = Z(y)."""
    import numpy as np
    L = np.load(os.path.join(HERE, 'out', 'c3_equi_leaves.npy'))
    box = (0.2265625, 0.23046875, 0.359375, 0.36328125)
    rows = [r for r in L if tuple(float(v) for v in r[:4]) == box]
    At = [(mp.mpf(0), mp.mpf(0)), (mp.mpf(1), mp.mpf(0)), (mp.mpf(1) / 2, mp.sqrt(3) / 2)]
    bx = [None, mp.mpf('0.23045707'), mp.mpf('0.36074435')]
    bx[0] = 1 - bx[1] - bx[2]
    Gt = [mp.log(v) for v in rho_of(At, bx)]
    def Fy(u, v):
        bb = [1 - u - v, u, v]
        return [mp.log(w) - g for w, g in zip(rho_of(At, bb), Gt)]
    def Jy(u, v):
        J = jac_G(At, [1 - u - v, u, v])
        return [[J[(2, 2)], J[(2, 3)]], [J[(3, 2)], J[(3, 3)]]]
    sol = mp.findroot(Fy, (mp.mpf('0.23029868'), mp.mpf('0.36083772')), J=Jy)
    by = [1 - sol[0] - sol[1], sol[0], sol[1]]
    res = max(abs(v) for v in Fy(sol[0], sol[1]))
    mx = abs(m_of(At, point(At, bx))); my = abs(m_of(At, point(At, by)))
    inb = lambda bb: box[0] <= bb[1] <= box[1] and box[2] <= bb[2] <= box[3]
    dist = mp.sqrt((by[1] - bx[1]) ** 2 + (by[2] - bx[2]) ** 2)
    ok = len(rows) == 1 and int(rows[0][4]) in (3, 4) and inb(bx) and inb(by) and res < TOL and dist > mp.mpf('1e-4')
    ok &= mx < mp.mpf(1) / 3 < my
    # how many valley leaves cross the fold, on a 9 x 9 grid in floating point (a statistic only)
    A = np.array([[0.0, 0.0], [1.0, 0.0], [0.5, np.sqrt(3) / 2]])
    V = L[L[:, 4] >= 3]
    g = np.linspace(0, 1, 9)
    b2 = V[:, 0, None, None] + g[None, :, None] * (V[:, 1] - V[:, 0])[:, None, None] + 0 * g[None, None, :]
    b3 = V[:, 2, None, None] + g[None, None, :] * (V[:, 3] - V[:, 2])[:, None, None] + 0 * g[None, :, None]
    be = np.stack([1 - b2 - b3, b2, b3], -1)
    x = be[..., 1:2] * A[1] + be[..., 2:3] * A[2]
    d = x[..., None, :] - A
    z = (d[..., 0] + 1j * d[..., 1]) ** 2 / (d ** 2).sum(-1)
    mm = np.abs((be * z).sum(-1)).reshape(len(V), -1)
    cross_n = int(((mm < 1 / 3).any(1) & (mm > 1 / 3).any(1)).sum())
    J = L[L[:, 4] == 1]
    check('N1', 'a valley leaf of the archived certificate holds a minimum x and a saddle y with Z(x) = Z(y), '
          'so Z is not one-to-one on every leaf box', ok,
          '|m(x)| = %s, |m(y)| = %s, |y - x| = %s, residual %s; %d of %d valley leaves cross the fold on a 9x9 float grid'
          % (mp.nstr(mx, 8), mp.nstr(my, 8), mp.nstr(dist, 3), mp.nstr(res, 3), cross_n, len(V)))


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument('--flip', action='append', default=[], choices=['psi4', 'jac', 'kernel', 'lami', 'r57', 'cusp'])
    args = ap.parse_args(argv[1:])
    FLIP.update(args.flip)
    print('derivations_check.py: sympy %s, mpmath %s, mp.dps = %d, flips = %s' % (sp.__version__, mp.__version__, mp.mp.dps, sorted(FLIP) or 'none'))
    try:
        for sec in (sec_planarity, sec_index, sec_inverse, sec_hessian, sec_isotropic, sec_model,
                    sec_exclusion, sec_jacobian, sec_valley, sec_certificate, sec_appendix, sec_code, sec_note):
            sec()
    except CheckFailed as e:
        print('RESULT FAIL (%d checks passed before the failure): %s' % (NPASS[0], e), flush=True)
        return 1
    print('RESULT ALL %d CHECKS PASSED' % NPASS[0], flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
