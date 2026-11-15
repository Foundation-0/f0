"""Vectorised driver for cert3 (same proof structure as run_cert.py, batch processing of pairs).

usage: run_cert2.py a_lo a_hi b_lo b_hi out.json [d0] [d1] [maxdepth]"""
import sys, json, time
import numpy as np
from iv import I
from cert3 import Shape, m2_lower, rho_centered, jac_det, valley_ok, phys
from lib3 import lami, grad_hess


def excluded(sh, B):
    lb = m2_lower(sh, B)
    return np.nextafter(9.0 * lb, -np.inf) > 1.0


def candidates(sh, depth0, depth1):
    n = 2 ** depth0
    g = np.arange(n) / n
    G2, G3 = np.meshgrid(g, g, indexing='ij')
    m = (G2 + G3) < 1.0
    B = np.c_[G2[m], G2[m] + 1.0 / n, G3[m], G3[m] + 1.0 / n]
    nex = 0
    for lev in range(depth0, depth1 + 1):
        ex = excluded(sh, B.T)
        nex += int(ex.sum())
        B = B[~ex]
        if lev == depth1:
            return B, nex
        B = split4(B)
        B = B[B[:, 0] + B[:, 2] < 1.0]


def split4(B):
    m2 = 0.5 * (B[:, 0] + B[:, 1]); m3 = 0.5 * (B[:, 2] + B[:, 3])
    c = [np.c_[B[:, 0], m2, B[:, 2], m3], np.c_[m2, B[:, 1], B[:, 2], m3], np.c_[B[:, 0], m2, m3, B[:, 3]], np.c_[m2, B[:, 1], m3, B[:, 3]]]
    return np.stack(c, 1).reshape(-1, 4)


def valley_batch(sh, Bi, Bj, Q2, Q3, nsub=4):
    """Vectorised valley certificate. Returns ok mask, kind ('3' or '4' as int), cells."""
    n = len(Bi)
    A = np.array([[0.0, 0.0], [1.0, 0.0], [sh.af, sh.bf]])
    def corners(B):
        b2 = np.stack([B[:, 0], B[:, 1], B[:, 0], B[:, 1]], 1); b3 = np.stack([B[:, 2], B[:, 2], B[:, 3], B[:, 3]], 1)
        return np.stack([b2 + sh.af * b3, sh.bf * b3], -1)
    pts = np.concatenate([corners(Bi), corners(Bj)], 1)
    c = pts.mean(1)
    qf = lami(A, c)[0]
    _, H = grad_hess(A, qf / qf[:, :1], c)
    ev, V = np.linalg.eigh(H)
    k = np.argmin(np.abs(ev), 1)
    t = V[np.arange(n), :, k]
    s = np.c_[-t[:, 1], t[:, 0]]
    det = I.c(t[:, 0]) * s[:, 1] - I.c(t[:, 1]) * s[:, 0]
    tmax = np.zeros(n); smax = np.zeros(n)
    for B in (Bi, Bj):
        d = phys(sh, I(B[:, 0], B[:, 1]), I(B[:, 2], B[:, 3]))[0]
        px = d[0] - c[:, 0]; py = d[1] - c[:, 1]
        tau = (px * s[:, 1] - py * s[:, 0]) / det
        sig = (py * t[:, 0] - px * t[:, 1]) / det
        tmax = np.maximum(tmax, np.maximum(np.abs(tau.lo), np.abs(tau.hi)))
        smax = np.maximum(smax, np.maximum(np.abs(sig.lo), np.abs(sig.hi)))
    ht = np.nextafter(tmax * 1.000001, np.inf)
    ok = np.zeros(n, bool); kind = np.zeros(n, int); hs_used = np.zeros(n)
    for fac in (2.0, 4.0, 8.0, 16.0, 32.0):
        todo = np.where(~ok)[0]
        if len(todo) == 0:
            break
        hs = np.maximum(smax[todo] * fac, smax[todo] + fac * ht[todo])
        r, kd = valley_vec(sh, (Q2[todo], Q3[todo]), c[todo], t[todo], s[todo], ht[todo], hs, nsub)
        ok[todo[r]] = True; kind[todo[r]] = kd[r]; hs_used[todo[r]] = hs[r]
    cells = np.c_[c, t, s, ht, hs_used]
    return ok, kind, cells


def valley_vec(sh, Q, c, t, s, ht, hs, nsub):
    from cert3 import tensors
    n = len(c)
    u = (np.arange(nsub + 1) / nsub) * 2 - 1  # [-1,1] grid (exact dyadic for nsub power of 2)
    T0, S0 = np.meshgrid(u[:-1], u[:-1], indexing='ij'); T1, S1 = np.meshgrid(u[1:], u[1:], indexing='ij')
    T0 = T0.ravel(); T1 = T1.ravel(); S0 = S0.ravel(); S1 = S1.ravel()
    m = len(T0)
    rep = lambda x: np.repeat(x, m, axis=0)
    tau = I(np.outer(ht, T0).ravel(), np.outer(ht, T1).ravel())  # ht*T exact? not nec.: fix by widening
    sig = I(np.outer(hs, S0).ravel(), np.outer(hs, S1).ravel())
    tau = I(np.nextafter(tau.lo, -np.inf), np.nextafter(tau.hi, np.inf))
    sig = I(np.nextafter(sig.lo, -np.inf), np.nextafter(sig.hi, np.inf))
    cc = rep(c); tt = rep(t); ss = rep(s)
    q = (I.c(np.ones(n * m)), I(rep(Q[0].lo), rep(Q[0].hi)), I(rep(Q[1].lo), rep(Q[1].hi)))
    P = (cc[:, 0] + tau * tt[:, 0] + sig * ss[:, 0], cc[:, 1] + tau * tt[:, 1] + sig * ss[:, 1])
    D = tensors(sh, q, P, (tt[:, 0], tt[:, 1]), (ss[:, 0], ss[:, 1]))
    v1 = D['ss'].pos().reshape(n, m).all(1)
    a = D['ts'] / D['ss']
    a2 = a.sq()
    w3 = D['ttt'] - 3.0 * a * D['tts'] + 3.0 * a2 * D['tss'] - a * a2 * D['sss']
    w3pos = w3.pos().reshape(n, m).all(1); w3neg = w3.neg().reshape(n, m).all(1)
    third = w3pos | w3neg
    w4 = D['tttt'] - 4.0 * a * D['ttts'] + 6.0 * a2 * D['ttss'] - 4.0 * a * a2 * D['tsss'] + a2 * a2 * D['ssss']
    w3s = D['tts'] - 2.0 * a * D['tss'] + a2 * D['sss']
    f4 = w4 - 3.0 * w3s.sq() / D['ss']
    fourth = f4.neg().reshape(n, m).all(1)
    # V2 on the two s-edges, nsub pieces in tau
    te = I(np.nextafter(np.outer(ht, u[:-1]).ravel(), -np.inf), np.nextafter(np.outer(ht, u[1:]).ravel(), np.inf))
    me = nsub
    rep2 = lambda x: np.repeat(x, me, axis=0)
    cc2 = rep2(c); tt2 = rep2(t); ss2 = rep2(s); hs2 = rep2(hs)
    q2 = (I.c(np.ones(n * me)), I(rep2(Q[0].lo), rep2(Q[0].hi)), I(rep2(Q[1].lo), rep2(Q[1].hi)))
    v2 = np.ones(n, bool)
    for sg in (-1.0, 1.0):
        sgI = I.c(sg * hs2)
        Pe = (cc2[:, 0] + te * tt2[:, 0] + sgI * ss2[:, 0], cc2[:, 1] + te * tt2[:, 1] + sgI * ss2[:, 1])
        De = tensors(sh, q2, Pe, (tt2[:, 0], tt2[:, 1]), (ss2[:, 0], ss2[:, 1]))
        if sg < 0:
            v2 &= De['s'].neg().reshape(n, me).all(1)
        else:
            v2 &= De['s'].pos().reshape(n, me).all(1)
    ok = v1 & v2 & (third | fourth)
    kind = np.where(third, 3, 4)
    return ok, kind


def certify(sh, d0=4, d1=7, maxdepth=10, log=print):
    t0 = time.time()
    cand, nex = candidates(sh, d0, d1)
    log('candidates %d excluded %d' % (len(cand), nex))
    R = rho_centered(sh, cand.T)
    lo2, hi2, lo3, hi3 = R[0].lo, R[0].hi, R[1].lo, R[1].hi
    order = np.argsort(lo2)
    PI = []; PJ = []
    for a_ in range(len(cand)):
        i = order[a_]
        js = order[a_:]
        js = js[lo2[js] <= hi2[i]]
        js = js[(lo3[js] <= hi3[i]) & (lo3[i] <= hi3[js]) & (lo2[i] <= hi2[js])]
        for j in js:
            PI.append(min(i, j)); PJ.append(max(i, j))
    Bi = cand[PI]; Bj = cand[PJ]; dep = np.zeros(len(PI), int)
    log('initial pairs %d (%.1fs)' % (len(Bi), time.time() - t0))
    certs = {'D': 0, 'J': [], 'V3': [], 'V4': []}
    stats = {'D': 0, 'J': 0, 'V3': 0, 'V4': 0, 'split': 0, 'excl': 0}
    fails = []
    rnd = 0
    while len(Bi):
        rnd += 1
        Ri = rho_centered(sh, Bi.T); Rj = rho_centered(sh, Bj.T)
        Q2 = I(np.maximum(Ri[0].lo, Rj[0].lo), np.minimum(Ri[0].hi, Rj[0].hi))
        Q3 = I(np.maximum(Ri[1].lo, Rj[1].lo), np.minimum(Ri[1].hi, Rj[1].hi))
        dis = (Q2.lo > Q2.hi) | (Q3.lo > Q3.hi)
        stats['D'] += int(dis.sum())
        keep = ~dis
        Hb = np.c_[np.minimum(Bi[:, 0], Bj[:, 0]), np.maximum(Bi[:, 1], Bj[:, 1]), np.minimum(Bi[:, 2], Bj[:, 2]), np.maximum(Bi[:, 3], Bj[:, 3])]
        dj = jac_det(sh, Hb.T)
        jok = keep & ((dj.lo > 0) | (dj.hi < 0))
        stats['J'] += int(jok.sum()); certs['J'].append(np.c_[Bi[jok], Bj[jok]])
        rest = np.where(keep & ~jok)[0]
        vok = np.zeros(len(Bi), bool)
        if len(rest):
            ok, kind, cells = valley_batch(sh, Bi[rest], Bj[rest], Q2[rest], Q3[rest])
            vok[rest[ok]] = True
            for kk in (3, 4):
                sel = ok & (kind == kk)
                stats['V%d' % kk] += int(sel.sum())
                certs['V%d' % kk].append(np.c_[Bi[rest[sel]], Bj[rest[sel]], cells[sel], Q2.lo[rest[sel]], Q2.hi[rest[sel]], Q3.lo[rest[sel]], Q3.hi[rest[sel]]])
        bad = np.where(keep & ~jok & ~vok)[0]
        deep = dep[bad] >= maxdepth
        for k in bad[deep]:
            fails.append((Bi[k].tolist(), Bj[k].tolist()))
        bad = bad[~deep]
        stats['split'] += len(bad)
        nBi = []; nBj = []; ndep = []
        for k in bad:
            bi, bj = Bi[k], Bj[k]
            if np.array_equal(bi, bj):
                ch = split4(bi[None]); ch = ch[ch[:, 0] + ch[:, 2] < 1.0]
                ch = ch[~excluded(sh, ch.T)]
                for x in range(len(ch)):
                    for y in range(x, len(ch)):
                        nBi.append(ch[x]); nBj.append(ch[y]); ndep.append(dep[k] + 1)
            else:
                big, oth = (bi, bj) if (bi[1] - bi[0]) >= (bj[1] - bj[0]) else (bj, bi)
                ch = split4(big[None]); ch = ch[ch[:, 0] + ch[:, 2] < 1.0]
                ch = ch[~excluded(sh, ch.T)]
                for cbox in ch:
                    nBi.append(cbox); nBj.append(oth); ndep.append(dep[k] + 1)
        Bi = np.array(nBi).reshape(-1, 4); Bj = np.array(nBj).reshape(-1, 4); dep = np.array(ndep, int)
        log('round %d: next %d  stats %s fails %d (%.1fs)' % (rnd, len(Bi), stats, len(fails), time.time() - t0))
    return cand, nex, certs, fails, stats


if __name__ == '__main__':
    import warnings; warnings.filterwarnings('ignore')
    a_lo, a_hi, b_lo, b_hi = [float(x) for x in sys.argv[1:5]]
    out = sys.argv[5]
    d0 = int(sys.argv[6]) if len(sys.argv) > 6 else 4
    d1 = int(sys.argv[7]) if len(sys.argv) > 7 else 7
    md = int(sys.argv[8]) if len(sys.argv) > 8 else 10
    sh = Shape(a_lo, a_hi, b_lo, b_hi)
    cand, nex, certs, fails, stats = certify(sh, d0, d1, md, log=lambda *a: print(*a, flush=True))
    np.savez_compressed(out.replace('.json', '.npz'), cand=cand,
                        J=np.vstack(certs['J']) if certs['J'] else np.zeros((0, 8)),
                        V3=np.vstack(certs['V3']) if certs['V3'] else np.zeros((0, 20)),
                        V4=np.vstack(certs['V4']) if certs['V4'] else np.zeros((0, 20)))
    json.dump(dict(shape=[a_lo, a_hi, b_lo, b_hi], d0=d0, d1=d1, maxdepth=md, ncand=len(cand), nexcluded=nex,
                   stats=stats, nfails=len(fails), fails=fails[:100]), open(out, 'w'))
    print('RESULT', 'PROVED' if not fails else 'NOT PROVED', stats, flush=True)
