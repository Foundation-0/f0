#!/usr/bin/env python3
"""Independent re-check (python-flint arb ball arithmetic) of a run_cert3 certificate.

Shares no code with iv.py / cert3.py / run_cert*.py / lib3.py. Reads only the shape box and the leaf
array (boxes, kinds, regions, cells) from the certificate files and re-derives everything else.

Checks:
  X. Exclusion/coverage: recursively from the 2^d0 grid on the beta-simplex, every box is either shown to
     satisfy |m|^2 > 1/9 (arb), lies outside the closed triangle, or (at depth d1) is covered by leaf boxes.
  J. Every J-leaf: the interval Jacobian determinant of (log rho2, log rho3) w.r.t. (beta2, beta3) over its
     region NB excludes 0, and NB contains the leaf box.
  V. Every V-leaf: on its cell, with q in an arb enclosure of rho(leaf box): V_ss > 0, V_s < 0 on the lower
     and > 0 on the upper s-edge, and psi''' != 0 (one sign) or psi'''' < 0; the leaf box lies in the cell.
  B. Phase B (pair separation) is re-checked on a random sample of pairs only (stated as such).
usage: verify_arb3.py prefix [nsample] [corrupt]
"""
import sys, json, random
import numpy as np
from flint import arb, ctx

ctx.prec = 96


class Fail(Exception):
    pass


class Iv:
    """Endpoint interval arithmetic on top of arb: each endpoint is an arb ball; results take the rigorous
    lower()/upper() of arb operations, so enclosures are rigorous and as tight as interval arithmetic."""
    __slots__ = ('lo', 'hi')

    def __init__(self, lo, hi=None):
        lo = lo if isinstance(lo, arb) else arb(lo)
        hi = lo if hi is None else (hi if isinstance(hi, arb) else arb(hi))
        self.lo = lo.lower(); self.hi = hi.upper()

    @staticmethod
    def w(x):
        return x if isinstance(x, Iv) else Iv(x)

    def __add__(a, b):
        b = Iv.w(b); return Iv((a.lo + b.lo).lower(), (a.hi + b.hi).upper())
    __radd__ = __add__

    def __neg__(a):
        return Iv(-a.hi, -a.lo)

    def __sub__(a, b):
        b = Iv.w(b); return Iv((a.lo - b.hi).lower(), (a.hi - b.lo).upper())

    def __rsub__(a, b):
        return Iv.w(b) - a

    def __mul__(a, b):
        b = Iv.w(b)
        p = [a.lo * b.lo, a.lo * b.hi, a.hi * b.lo, a.hi * b.hi]
        lo = p[0].lower(); hi = p[0].upper()
        for x in p[1:]:
            if x.lower() < lo:
                lo = x.lower()
            if x.upper() > hi:
                hi = x.upper()
        return Iv(lo, hi)
    __rmul__ = __mul__

    def inv(a):
        if not (a.lo > 0 or a.hi < 0):
            raise Fail('division by interval containing 0')
        return Iv((1 / a.hi).lower(), (1 / a.lo).upper())

    def __truediv__(a, b):
        return a * Iv.w(b).inv()

    def __rtruediv__(a, b):
        return Iv.w(b) * a.inv()

    def sq(a):
        if a.lo > 0:
            return Iv((a.lo * a.lo).lower(), (a.hi * a.hi).upper())
        if a.hi < 0:
            return Iv((a.hi * a.hi).lower(), (a.lo * a.lo).upper())
        m = a.hi if a.hi > -a.lo else -a.lo
        return Iv(arb(0), (m * m).upper())

    def sqrt(a):
        if not a.lo > 0:
            raise Fail('sqrt of nonpositive')
        return Iv(a.lo.sqrt().lower(), a.hi.sqrt().upper())

    def __gt__(a, x):
        return bool(a.lo > x)

    def __lt__(a, x):
        return bool(a.hi < x)

    def lower(self):
        return self.lo

    def upper(self):
        return self.hi

    def union(self, o):
        lo = self.lo if self.lo < o.lo else o.lo
        hi = self.hi if self.hi > o.hi else o.hi
        return Iv(lo, hi)

    def overlaps(self, o):
        return not (self.hi < o.lo or o.hi < self.lo)


def iv(lo, hi):
    lo = float(lo); hi = float(hi)
    if lo > hi:
        raise Fail('bad interval')
    return Iv(arb(lo), arb(hi))


def mul(x, y):
    return Iv.w(x) * Iv.w(y)


def sq(x):
    return Iv.w(x).sq()


def pos(x):
    return bool(x > 0)


def neg(x):
    return bool(x < 0)


class Tri:
    def __init__(self, shape):
        self.a = iv(shape[0], shape[1]); self.b = iv(shape[2], shape[3])

    def point(self, b2, b3):
        return (b2 + mul(self.a, b3), mul(self.b, b3))

    def sites(self):
        return [(Iv(0), Iv(0)), (Iv(1), Iv(0)), (self.a, self.b)]


def m2_lower_bound(T, box):
    b2 = iv(box[0], box[1]); b3 = iv(box[2], box[3])
    bet = [1 - b2 - b3, b2, b3]
    # |m| >= 2 beta_i - 1
    best = Iv(0)
    for x in bet:
        g = 2 * x - 1
        if g > 0:
            v = g * g
            if v.lower() > best.lower():
                best = v
    P = T.point(b2, b3)
    re = Iv(0); im = Iv(0)
    for (sx, sy), bi in zip(T.sites(), bet):
        dx = P[0] - sx; dy = P[1] - sy
        r2 = sq(dx) + sq(dy)
        if not r2 > 0:
            return best.lower()
        c = 1 - 2 * sq(dy) / r2
        c2 = 2 * sq(dx) / r2 - 1
        # intersect the two enclosures of cos 2theta and [-1,1]
        lo = max(float(c.lower()), float(c2.lower()), -1.0); hi = min(float(c.upper()), float(c2.upper()), 1.0)
        # (lower/upper of arb are rigorous bounds; float() of an arb endpoint is exact for these values
        #  because arb.lower()/upper() return exactly representable midpoints; we widen by one ulp anyway)
        cc = iv(np.nextafter(np.nextafter(lo, -2), -2), np.nextafter(np.nextafter(hi, 2), 2))
        s = 2 * mul(dx, dy) / r2
        slo = max(float(s.lower()), -1.0); shi = min(float(s.upper()), 1.0)
        ss = iv(np.nextafter(np.nextafter(slo, -2), -2), np.nextafter(np.nextafter(shi, 2), 2))
        re += mul(bi, cc); im += mul(bi, ss)
    v = sq(re) + sq(im)
    return max(v.lower(), best.lower()) if isinstance(best, arb) else v.lower()


def excluded(T, box):
    lb = m2_lower_bound(T, box)
    return bool(9 * lb > 1)


def rho_enc(T, box):
    b2 = iv(box[0], box[1]); b3 = iv(box[2], box[3])
    bet = [1 - b2 - b3, b2, b3]
    P = T.point(b2, b3)
    r2 = [sq(P[0] - sx) + sq(P[1] - sy) for (sx, sy) in T.sites()]
    out = []
    for i in (1, 2):
        s = r2[i] / r2[0]
        out.append((bet[i] / bet[0]) * s * s.sqrt())
    return out


def jac_entries(T, box):
    b2 = iv(box[0], box[1]); b3 = iv(box[2], box[3])
    bet = [1 - b2 - b3, b2, b3]
    if not (bet[0] > 0 and bet[1] > 0 and bet[2] > 0):
        return None
    P = T.point(b2, b3)
    S = T.sites()
    d = [(P[0] - sx, P[1] - sy) for (sx, sy) in S]
    r2 = [sq(x) + sq(y) for x, y in d]
    e = {2: (Iv(1), Iv(0)), 3: (T.a, T.b)}
    J = {}
    for i in (2, 3):
        for k in (2, 3):
            v = 1 / bet[0] + 3 * (d[i - 1][0] * e[k][0] + d[i - 1][1] * e[k][1]) / r2[i - 1] - 3 * (d[0][0] * e[k][0] + d[0][1] * e[k][1]) / r2[0]
            if i == k:
                v = v + 1 / bet[i - 1]
            J[(i, k)] = v
    return J


def rho_centered(T, box):
    """Mean-value enclosure rho(c) + sum_k d rho/d beta_k (box) * (box_k - c_k), intersected with the
    natural enclosure. d rho_i / d beta_k = rho_i * d log rho_i / d beta_k."""
    nat = rho_enc(T, box)
    J = jac_entries(T, box)
    if J is None:
        return nat
    c2 = (box[0] + box[1]) / 2; c3 = (box[2] + box[3]) / 2
    cen = rho_enc(T, (c2, c2, c3, c3))
    h2 = Iv(arb(box[0]) - arb(c2), arb(box[1]) - arb(c2)); h3 = Iv(arb(box[2]) - arb(c3), arb(box[3]) - arb(c3))
    out = []
    for idx, i in enumerate((2, 3)):
        e = cen[idx] + nat[idx] * J[(i, 2)] * h2 + nat[idx] * J[(i, 3)] * h3
        lo = e.lo if e.lo > nat[idx].lo else nat[idx].lo
        hi = e.hi if e.hi < nat[idx].hi else nat[idx].hi
        out.append(Iv(lo, hi))
    return out


def jac_det(T, box):
    b2 = iv(box[0], box[1]); b3 = iv(box[2], box[3])
    bet = [1 - b2 - b3, b2, b3]
    if not (bet[0] > 0 and bet[1] > 0 and bet[2] > 0):
        return arb(0).union(arb(1))  # undefined: treat as failure (contains 0)
    P = T.point(b2, b3)
    S = T.sites()
    d = [(P[0] - sx, P[1] - sy) for (sx, sy) in S]
    r2 = [sq(x) + sq(y) for x, y in d]
    e = {2: (Iv(1), Iv(0)), 3: (T.a, T.b)}
    J = {}
    for i in (2, 3):
        for k in (2, 3):
            v = 1 / bet[0] + 3 * (d[i - 1][0] * e[k][0] + d[i - 1][1] * e[k][1]) / r2[i - 1] - 3 * (d[0][0] * e[k][0] + d[0][1] * e[k][1]) / r2[0]
            if i == k:
                v = v + 1 / bet[i - 1]
            J[(i, k)] = v
    return J[(2, 2)] * J[(3, 3)] - J[(2, 3)] * J[(3, 2)]


def derivs(T, q, P, t, s):
    """Directional derivatives of V = sum q_i/|x - a_i| at P (arb pair) along t, s (arb pairs)."""
    vec = {'t': t, 's': s}
    names = ['s', 'ss', 'ts', 'ttt', 'tts', 'tss', 'sss', 'tttt', 'ttts', 'ttss', 'tsss', 'ssss']
    out = {k: Iv(0) for k in names}
    dd = {a + b: vec[a][0] * vec[b][0] + vec[a][1] * vec[b][1] for a in 'ts' for b in 'ts'}
    for (sx, sy), qi in zip(T.sites(), q):
        y = (P[0] - sx, P[1] - sy)
        r2 = sq(y[0]) + sq(y[1])
        r = r2.sqrt()
        i3 = 1 / (r * r2); i5 = i3 / r2; i7 = i5 / r2; i9 = i7 / r2
        yv = {k: y[0] * v[0] + y[1] * v[1] for k, v in vec.items()}
        out['s'] += qi * (-yv['s'] * i3)
        for k in ('ss', 'ts'):
            a, b = k
            out[k] += qi * (3 * yv[a] * yv[b] * i5 - dd[a + b] * i3)
        for k in ('ttt', 'tts', 'tss', 'sss'):
            a, b, c = k
            out[k] += qi * (-15 * yv[a] * yv[b] * yv[c] * i7 + 3 * (dd[a + b] * yv[c] + dd[a + c] * yv[b] + dd[b + c] * yv[a]) * i5)
        for k in ('tttt', 'ttts', 'ttss', 'tsss', 'ssss'):
            a, b, c, e = k
            y4 = yv[a] * yv[b] * yv[c] * yv[e]
            s6 = (dd[a + b] * yv[c] * yv[e] + dd[a + c] * yv[b] * yv[e] + dd[a + e] * yv[b] * yv[c]
                  + dd[b + c] * yv[a] * yv[e] + dd[b + e] * yv[a] * yv[c] + dd[c + e] * yv[a] * yv[b])
            p3 = dd[a + b] * dd[c + e] + dd[a + c] * dd[b + e] + dd[a + e] * dd[b + c]
            out[k] += qi * (105 * y4 * i9 - 15 * s6 * i7 + 3 * p3 * i5)
    return out


def box_in_cell(T, box, c, t, s, ht, hs):
    b2 = iv(box[0], box[1]); b3 = iv(box[2], box[3])
    P = T.point(b2, b3)
    px = P[0] - c[0]; py = P[1] - c[1]
    det = t[0] * s[1] - t[1] * s[0]
    tau = (px * s[1] - py * s[0]) / det
    sig = (py * t[0] - px * t[1]) / det
    return bool(tau > -ht) and bool(tau < ht) and bool(sig > -hs) and bool(sig < hs)


def valley_check(T, box, cell, nsub=4):
    c = (Iv(float(cell[0])), Iv(float(cell[1]))); t = (Iv(float(cell[2])), Iv(float(cell[3])))
    s = (Iv(float(cell[4])), Iv(float(cell[5]))); ht = Iv(float(cell[6])); hs = Iv(float(cell[7]))
    R = rho_centered(T, box)
    q = [Iv(1), R[0], R[1]]
    if not box_in_cell(T, box, c, t, s, ht, hs):
        raise Fail('leaf box not in cell')
    u = [Iv(-1) + Iv(2 * k) / nsub for k in range(nsub + 1)]
    third_sign = set(); fourth_ok = True
    for i in range(nsub):
        tau = (u[i] * ht).union(u[i + 1] * ht)
        for j in range(nsub):
            sig = (u[j] * hs).union(u[j + 1] * hs)
            P = (c[0] + tau * t[0] + sig * s[0], c[1] + tau * t[1] + sig * s[1])
            D = derivs(T, q, P, t, s)
            if not pos(D['ss']):
                raise Fail('V1')
            a = D['ts'] / D['ss']
            a2 = sq(a)
            w3 = D['ttt'] - 3 * a * D['tts'] + 3 * a2 * D['tss'] - a * a2 * D['sss']
            if pos(w3):
                third_sign.add(1)
            elif neg(w3):
                third_sign.add(-1)
            else:
                third_sign.add(0)
            w4 = D['tttt'] - 4 * a * D['ttts'] + 6 * a2 * D['ttss'] - 4 * a * a2 * D['tsss'] + sq(a2) * D['ssss']
            w3s = D['tts'] - 2 * a * D['tss'] + a2 * D['sss']
            f4 = w4 - 3 * sq(w3s) / D['ss']
            if not neg(f4):
                fourth_ok = False
    third_ok = (third_sign == {1}) or (third_sign == {-1})
    if not (third_ok or fourth_ok):
        raise Fail('V3/V4')
    for sgn in (-1, 1):
        for i in range(nsub):
            tau = (u[i] * ht).union(u[i + 1] * ht)
            sig = sgn * hs
            P = (c[0] + tau * t[0] + sig * s[0], c[1] + tau * t[1] + sig * s[1])
            D = derivs(T, q, P, t, s)
            if sgn < 0 and not neg(D['s']):
                raise Fail('V2 lower')
            if sgn > 0 and not pos(D['s']):
                raise Fail('V2 upper')
    return 'V3' if third_ok else 'V4'


def valley_robust(T, box, cell, level=0):
    """The valley claim for q in rho(box) follows from the claims for q in rho(sub-box) over a split of box."""
    try:
        return valley_check(T, box, cell, nsub=4 if level == 0 else 8)
    except Fail as e:
        if level >= 2 or 'not in cell' in str(e):
            raise
        kinds = [valley_robust(T, c, cell, level + 1) for c in split4(box)]
        return 'V3' if all(k == 'V3' for k in kinds) else 'V4'


def split4(b):
    m2 = 0.5 * (b[0] + b[1]); m3 = 0.5 * (b[2] + b[3])
    return [(b[0], m2, b[2], m3), (m2, b[1], b[2], m3), (b[0], m2, m3, b[3]), (m2, b[1], m3, b[3])]


def main(argv):
    pre = argv[1]
    nsample = int(argv[2]) if len(argv) > 2 else 2000
    corrupt = argv[3] if len(argv) > 3 else ''
    meta = json.load(open(pre + '.json'))
    L = np.load(pre + '_leaves.npy')
    shape = meta['shape']; d0, d1 = meta['d0'], meta['d1']
    if corrupt == 'shape':
        shape = [shape[0], shape[1], shape[2] * 0.7, shape[3] * 0.7]
    if corrupt == 'cell':
        k = np.where(L[:, 4] >= 3)[0][0]
        L = L.copy(); L[k, 16] *= 0.05
    if corrupt == 'region':
        k = np.where(L[:, 4] == 1)[0][0]
        L = L.copy(); L[k, 5] -= 0.3; L[k, 7] -= 0.3
    T = Tri(shape)
    rep = {}
    # ---- X: coverage ----
    leafset = set(tuple(map(float, r[:4])) for r in L)
    n = 2 ** d0
    boxes = [(i / n, (i + 1) / n, j / n, (j + 1) / n) for i in range(n) for j in range(n) if i + j < n]
    nexcl = 0
    for lev in range(d0, d1 + 1):
        nxt = []
        for b in boxes:
            if excluded(T, b):
                nexcl += 1
                continue
            if lev == d1:
                if b in leafset:
                    continue
                kids = [c for c in split4(b) if c[0] + c[2] < 1.0]
                for c in kids:
                    if c in leafset:
                        continue
                    if excluded(T, c):
                        nexcl += 1
                        continue
                    raise Fail('uncovered box %r' % (c,))
            else:
                nxt += [c for c in split4(b) if c[0] + c[2] < 1.0]
        boxes = nxt
    rep['coverage'] = 'ok (%d boxes excluded by the verifier)' % nexcl
    print('coverage ok', flush=True)
    # ---- J and V leaves ----
    cnt = {'J': 0, 'V3': 0, 'V4': 0}
    for nr, r in enumerate(L):
        if nr % 1000 == 0:
            print('leaf', nr, cnt, flush=True)
        box = tuple(r[:4]); kind = int(r[4])
        if kind == 1:
            NB = r[5:9]
            if not (NB[0] <= box[0] and box[1] <= NB[1] and NB[2] <= box[2] and box[3] <= NB[3]):
                raise Fail('J region does not contain box')
            dt = jac_det(T, NB)
            if not (pos(dt) or neg(dt)):
                raise Fail('J det contains 0 for leaf %r' % (box,))
            cnt['J'] += 1
        else:
            cnt[valley_robust(T, box, r[9:17])] += 1
    rep['leaves'] = cnt
    # ---- B: sampled pairs ----
    rng = random.Random(1)
    idx = list(range(len(L)))
    ok_s = 0; tried = 0
    while tried < nsample:
        i, j = rng.sample(idx, 2)
        tried += 1
        Ri = rho_enc(T, tuple(L[i, :4])); Rj = rho_enc(T, tuple(L[j, :4]))
        disj = any(not Ri[k].overlaps(Rj[k]) for k in range(2))
        if disj:
            ok_s += 1
            continue
        # containment in a certified region
        def inside(X, r):
            if int(r[4]) == 1:
                NB = r[5:9]
                return NB[0] <= X[0] and X[1] <= NB[1] and NB[2] <= X[2] and X[3] <= NB[3]
            cc = r[9:17]
            return box_in_cell(T, X, (Iv(float(cc[0])), Iv(float(cc[1]))), (Iv(float(cc[2])), Iv(float(cc[3]))),
                               (Iv(float(cc[4])), Iv(float(cc[5]))), Iv(float(cc[6])), Iv(float(cc[7])))
        if inside(tuple(L[i, :4]), L[j]) or inside(tuple(L[j, :4]), L[i]):
            ok_s += 1
        # otherwise the pair needs phase-B refinement; not re-checked here
    rep['sampled_pairs'] = '%d of %d random leaf pairs resolved at leaf level (rest rely on phase-B refinement)' % (ok_s, tried)
    print(json.dumps(rep))
    print('VERIFIED (phase A, coverage); phase B sampled only')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv))
    except Fail as e:
        print('REJECTED:', e)
        sys.exit(2)
