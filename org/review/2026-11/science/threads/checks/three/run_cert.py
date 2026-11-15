"""Driver for cert3: prove 'at most one local minimum for every charge vector' on a triangle shape box.

usage: run_cert.py a_lo a_hi b_lo b_hi out.json [depth0] [maxdepth]
  a_lo..b_hi are floats (decimal strings parsed by float(); the box used is exactly those doubles).
Writes a certificate: candidate boxes, exclusion boxes count, and every pair certificate."""
import sys, json, time
import numpy as np
from iv import I
from cert3 import Shape, m2_lower, rho, jac_det, valley_ok, phys
from lib3 import sites, lami, grad_hess

NINTH = 1.0 / 9.0  # not exact; we use the rigorous comparison lb > 1/9 via lb*9 > 1 below


def excluded(sh, B):
    lb = m2_lower(sh, B)
    # lb > 1/9  <=>  9*lb > 1 ; 9*lb rounded down
    return np.nextafter(9.0 * lb, -np.inf) > 1.0


def split4(B):
    b2lo, b2hi, b3lo, b3hi = B
    m2 = 0.5 * (b2lo + b2hi); m3 = 0.5 * (b3lo + b3hi)
    return [(b2lo, m2, b3lo, m3), (m2, b2hi, b3lo, m3), (b2lo, m2, m3, b3hi), (m2, b2hi, m3, b3hi)]


def arr(boxes):
    a = np.array(boxes, float).reshape(-1, 4)
    return (a[:, 0], a[:, 1], a[:, 2], a[:, 3])


def candidates(sh, depth0, depth1):
    n = 2 ** depth0
    g = np.arange(n) / n
    boxes = [(g[i], g[i] + 1.0 / n, g[j], g[j] + 1.0 / n) for i in range(n) for j in range(n) if g[i] + g[j] < 1.0]
    nex = 0
    for lev in range(depth0, depth1 + 1):
        B = arr(boxes)
        ex = excluded(sh, B)
        nex += int(ex.sum())
        keep = [boxes[k] for k in np.where(~ex)[0]]
        if lev == depth1:
            return keep, nex
        boxes = [c for b in keep for c in split4(b) if c[0] + c[2] < 1.0]


def phys_float(sh, B):
    b2 = np.array([B[0], B[1], B[0], B[1]]); b3 = np.array([B[2], B[2], B[3], B[3]])
    return np.c_[b2 + sh.af * b3, sh.bf * b3]


def try_valley(sh, Bi, Bj, Q):
    A = sites(sh.af, sh.bf)
    pts = np.vstack([phys_float(sh, Bi), phys_float(sh, Bj)])
    c = pts.mean(0)
    qf = lami(A, c[None])[0][0]
    g, H = grad_hess(A, qf / qf[0], c[None])
    ev, V = np.linalg.eigh(H[0])
    t = V[:, np.argmin(np.abs(ev))].copy(); s = np.array([-t[1], t[0]])
    # rigorous (tau, sigma) ranges of both boxes
    det = I.c(t[0]) * s[1] - I.c(t[1]) * s[0]
    tmax = 0.0; smax = 0.0
    for B in (Bi, Bj):
        b2 = I(np.array([B[0]]), np.array([B[1]])); b3 = I(np.array([B[2]]), np.array([B[3]]))
        d = phys(sh, b2, b3)[0]
        px = d[0] - c[0]; py = d[1] - c[1]
        tau = (px * s[1] - py * s[0]) / det
        sig = (py * t[0] - px * t[1]) / det
        tmax = max(tmax, float(np.max(np.abs([tau.lo, tau.hi]))))
        smax = max(smax, float(np.max(np.abs([sig.lo, sig.hi]))))
    ht = tmax * 1.0000001
    for k in (2.0, 4.0, 8.0, 16.0):
        hs = max(smax * k, smax + 2.0 * ht)
        ok, why = valley_ok(sh, Q, c, t, s, ht, hs * (k / 2.0), nsub=4)
        if ok:
            return True, why, dict(c=c.tolist(), t=t.tolist(), s=s.tolist(), ht=ht, hs=hs * (k / 2.0))
    return False, why, None


def certify(sh, depth0=5, depth1=9, maxdepth=18, log=print):
    t0 = time.time()
    cand, nex = candidates(sh, depth0, depth1)
    log('candidates %d excluded %d (%.1fs)' % (len(cand), nex, time.time() - t0))
    R = rho(sh, arr(cand))
    lo2, hi2, lo3, hi3 = R[0].lo, R[0].hi, R[1].lo, R[1].hi
    # initial pairs: overlapping images (i <= j)
    order = np.argsort(lo2)
    pairs = []
    for a_ in range(len(cand)):
        i = order[a_]
        for b_ in range(a_, len(cand)):
            j = order[b_]
            if lo2[j] > hi2[i]:
                break
            if lo3[j] <= hi3[i] and lo3[i] <= hi3[j] and lo2[i] <= hi2[j]:
                pairs.append((cand[min(i, j)], cand[max(i, j)]))
    log('initial pairs %d' % len(pairs))
    certs = []; stats = {'J': 0, 'V3': 0, 'V4': 0, 'disjoint': 0, 'excluded': 0, 'split': 0}
    stack = [(p[0], p[1], 0) for p in pairs]
    fails = []
    while stack:
        Bi, Bj, dep = stack.pop()
        Ri = rho(sh, arr([Bi])); Rj = rho(sh, arr([Bj]))
        Q2 = I(np.maximum(Ri[0].lo, Rj[0].lo), np.minimum(Ri[0].hi, Rj[0].hi))
        Q3 = I(np.maximum(Ri[1].lo, Rj[1].lo), np.minimum(Ri[1].hi, Rj[1].hi))
        if (Q2.lo > Q2.hi).any() or (Q3.lo > Q3.hi).any():
            stats['disjoint'] += 1
            certs.append(('D', Bi, Bj))
            continue
        Hb = (min(Bi[0], Bj[0]), max(Bi[1], Bj[1]), min(Bi[2], Bj[2]), max(Bi[3], Bj[3]))
        dj = jac_det(sh, arr([Hb]))
        if dj.lo[0] > 0 or dj.hi[0] < 0:
            stats['J'] += 1
            certs.append(('J', Bi, Bj, Hb))
            continue
        ok, why, cell = try_valley(sh, Bi, Bj, (Q2, Q3))
        if ok:
            stats[why] += 1
            certs.append((why, Bi, Bj, cell, [float(Q2.lo[0]), float(Q2.hi[0]), float(Q3.lo[0]), float(Q3.hi[0])]))
            continue
        if dep >= maxdepth:
            fails.append((Bi, Bj, why))
            continue
        stats['split'] += 1
        # split the larger box (both if same)
        si = (Bi[1] - Bi[0]); sj = (Bj[1] - Bj[0])
        if Bi == Bj:
            ch = [c for c in split4(Bi) if c[0] + c[2] < 1.0]
            exm = excluded(sh, arr(ch)) if ch else []
            ch = [c for c, e in zip(ch, exm) if not e]
            stats['excluded'] += 4 - len(ch)
            for x in range(len(ch)):
                for y in range(x, len(ch)):
                    stack.append((ch[x], ch[y], dep + 1))
        else:
            big, other = (Bi, Bj) if si >= sj else (Bj, Bi)
            ch = [c for c in split4(big) if c[0] + c[2] < 1.0]
            exm = excluded(sh, arr(ch)) if ch else []
            ch = [c for c, e in zip(ch, exm) if not e]
            stats['excluded'] += 4 - len(ch)
            for c in ch:
                stack.append((c, other, dep + 1))
    log('stats %s fails %d (%.1fs)' % (stats, len(fails), time.time() - t0))
    return cand, nex, certs, fails, stats


if __name__ == '__main__':
    a_lo, a_hi, b_lo, b_hi = [float(x) for x in sys.argv[1:5]]
    out = sys.argv[5]
    d0 = int(sys.argv[6]) if len(sys.argv) > 6 else 5
    d1 = int(sys.argv[7]) if len(sys.argv) > 7 else 9
    sh = Shape(a_lo, a_hi, b_lo, b_hi)
    cand, nex, certs, fails, stats = certify(sh, d0, d1)
    json.dump(dict(shape=[a_lo, a_hi, b_lo, b_hi], depth0=d0, depth1=d1, ncand=len(cand), nexcluded=nex,
                   stats=stats, nfails=len(fails), fails=fails[:50], certs=certs), open(out, 'w'))
    print('RESULT', 'PROVED' if not fails else 'NOT PROVED', stats)
