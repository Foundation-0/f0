"""Driver v3 for cert3: local neighbourhood certificates + global pair separation.

Proof structure (for a shape box S, all positive charges):
  E. Candidate boxes U (beta coordinates) cover {|m| <= 1/3}; all other boxes have |m|^2 > 1/9 rigorously,
     so they hold no local minimum of any V_q (Hess >= 0 at a local min).
  A. Every candidate box B (or each of its descendants) gets a local certificate with a region N(B):
     - kind J: N(B) is a convex beta-box around B on which the interval Jacobian of log rho has
       determinant bounded away from 0, so Z is injective on N(B);
     - kind V: N(B) is a cell C (parallelogram in the plane) and for every q in rho(B) the potential
       V_q has at most one local minimum in C (valley certificate).
     In both cases: if x in B, y in N(B), Z(x) = Z(y) and both are local minima, then x = y.
  B. Every pair (B, B') of leaf boxes either has disjoint rho-enclosures, or B' is inside N(B), or B is
     inside N(B'); pairs are split (both boxes) until one of these holds.
  Hence two local minima of the same V_q cannot exist.
usage: run_cert3.py a_lo a_hi b_lo b_hi out_prefix [d0 d1 kJ maxdepth]
"""
import sys, json, time
import numpy as np
from iv import I
from cert3 import Shape, m2_lower, rho_centered, jac_det, phys
from run_cert2 import excluded, candidates, split4, valley_vec
from lib3 import lami, grad_hess


def local_cert(sh, B, kJ=2):
    """For boxes B (n,4): try J on the (2kJ+1)-box square around B; else valley on a cell.
    Returns kind (0 fail, 1 J, 3/4 valley), region arrays."""
    n = len(B)
    h = (B[:, 1] - B[:, 0])
    NB = np.c_[B[:, 0] - kJ * h, B[:, 1] + kJ * h, B[:, 2] - kJ * h, B[:, 3] + kJ * h]
    dj = jac_det(sh, NB.T)
    kind = np.zeros(n, int)
    kind[(dj.lo > 0) | (dj.hi < 0)] = 1
    cells = np.full((n, 8), np.nan)
    rest = np.where(kind == 0)[0]
    if len(rest):
        Bt = B[rest]
        A = np.array([[0.0, 0.0], [1.0, 0.0], [sh.af, sh.bf]])
        cb = np.c_[0.5 * (Bt[:, 0] + Bt[:, 1]), 0.5 * (Bt[:, 2] + Bt[:, 3])]
        c = np.c_[cb[:, 0] + sh.af * cb[:, 1], sh.bf * cb[:, 1]]
        qf = lami(A, c)[0]
        _, H = grad_hess(A, qf / qf[:, :1], c)
        ev, V = np.linalg.eigh(H)
        k = np.argmin(np.abs(ev), 1)
        t = V[np.arange(len(rest)), :, k]
        s = np.c_[-t[:, 1], t[:, 0]]
        # physical size of the box
        L = h[rest] * np.sqrt(1.0 + sh.af ** 2 + sh.bf ** 2) * 1.5
        R = rho_centered(sh, Bt.T)
        ok = np.zeros(len(rest), bool); kd = np.zeros(len(rest), int)
        cellv = np.zeros((len(rest), 8))
        for (ft, fs) in ((2 * kJ + 1, 3.0), (2 * kJ + 1, 6.0), (2 * kJ + 1, 12.0), (kJ + 1, 4.0), (kJ + 1, 8.0), (kJ + 1, 16.0)):
            todo = np.where(~ok)[0]
            if not len(todo):
                break
            ht = L[todo] * ft / 2; hs = L[todo] * fs / 2
            r, kk = valley_vec(sh, (R[0][todo], R[1][todo]), c[todo], t[todo], s[todo], ht, hs, 4)
            sel = todo[r]
            ok[sel] = True; kd[sel] = kk[r]
            cellv[sel] = np.c_[c[sel], t[sel], s[sel], ht[r], hs[r]]
        okr = np.where(ok)[0]
        if len(okr):
            ins = inside_cell(sh, Bt[okr], cellv[okr])
            ok[okr[~ins]] = False
        kind[rest[ok]] = kd[ok]
        cells[rest[ok]] = cellv[ok]
    return kind, NB, cells


def inside_cell(sh, Bq, cell):
    """Rigorous test that beta-boxes Bq (n,4) lie inside the cells (n,8) = c(2), t(2), s(2), ht, hs."""
    c = cell[:, 0:2]; t = cell[:, 2:4]; s = cell[:, 4:6]; ht = cell[:, 6]; hs = cell[:, 7]
    det = I.c(t[:, 0]) * s[:, 1] - I.c(t[:, 1]) * s[:, 0]
    d = phys(sh, I(Bq[:, 0], Bq[:, 1]), I(Bq[:, 2], Bq[:, 3]))[0]
    px = d[0] - c[:, 0]; py = d[1] - c[:, 1]
    tau = (px * s[:, 1] - py * s[:, 0]) / det
    sig = (py * t[:, 0] - px * t[:, 1]) / det
    return (tau.lo >= -ht) & (tau.hi <= ht) & (sig.lo >= -hs) & (sig.hi <= hs)


def run(sh, d0=5, d1=8, kJ=2, maxdepth=6, log=print):
    t0 = time.time()
    cand, nex = candidates(sh, d0, d1)
    log('candidates %d, excluded boxes %d (%.1fs)' % (len(cand), nex, time.time() - t0))
    # ---- phase A: local certificates (split boxes that fail) ----
    leaves = []  # rows: box(4), kind, NB(4), cell(8)
    work = cand; depth = 0; nfailA = 0
    while len(work) and depth <= maxdepth:
        kind, NB, cells = local_cert(sh, work, kJ)
        good = kind > 0
        leaves.append(np.c_[work[good], kind[good], NB[good], cells[good]])
        bad = work[~good]
        log('phase A depth %d: %d boxes, %d certified (J %d, V3 %d, V4 %d), %d split (%.1fs)' % (
            depth, len(work), good.sum(), (kind == 1).sum(), (kind == 3).sum(), (kind == 4).sum(), len(bad), time.time() - t0))
        if not len(bad):
            work = bad
            break
        ch = split4(bad)
        ch = ch[ch[:, 0] + ch[:, 2] < 1.0]
        ch = ch[~excluded(sh, ch.T)]
        work = ch; depth += 1
    if len(work):
        log('PHASE A FAILED on %d boxes' % len(work))
        return None
    Lf = np.vstack(leaves)
    nL = len(Lf)
    log('leaves %d' % nL)
    # ---- phase B: pairs ----
    R = rho_centered(sh, Lf[:, :4].T)
    lo2, hi2, lo3, hi3 = R[0].lo, R[0].hi, R[1].lo, R[1].hi
    order = np.argsort(lo2)
    PI = []; PJ = []
    for a_ in range(nL):
        i = order[a_]; js = order[a_ + 1:]
        js = js[lo2[js] <= hi2[i]]
        js = js[(lo3[js] <= hi3[i]) & (lo3[i] <= hi3[js]) & (lo2[i] <= hi2[js])]
        PI.extend([i] * len(js)); PJ.extend(js.tolist())
    PI = np.array(PI, int); PJ = np.array(PJ, int)
    log('overlapping leaf pairs %d (%.1fs)' % (len(PI), time.time() - t0))
    # pair state: boxes (may be sub-boxes of leaves) + leaf index for the region.
    # Depth-first processing in chunks of at most CHUNK pairs keeps memory bounded.
    CHUNK = 1_500_000
    stack = [(Lf[PI, :4], Lf[PJ, :4], PI, PJ, 0)]
    stats = dict(contained=0, disjoint=0, chunks=0, maxlevel=0)
    fails = 0; it = 0
    while stack:
        Bi, Bj, li, lj, lev = stack.pop()
        if len(Bi) > CHUNK:
            for k in range(0, len(Bi), CHUNK):
                stack.append((Bi[k:k + CHUNK], Bj[k:k + CHUNK], li[k:k + CHUNK], lj[k:k + CHUNK], lev))
            continue
        it += 1; stats['chunks'] += 1; stats['maxlevel'] = max(stats['maxlevel'], lev)
        Ri = rho_centered(sh, Bi.T); Rj = rho_centered(sh, Bj.T)
        dis = (np.maximum(Ri[0].lo, Rj[0].lo) > np.minimum(Ri[0].hi, Rj[0].hi)) | (np.maximum(Ri[1].lo, Rj[1].lo) > np.minimum(Ri[1].hi, Rj[1].hi))
        cont = np.zeros(len(Bi), bool)
        for (X, ly) in ((Bi, lj), (Bj, li)):
            kind = Lf[ly, 4]
            NB = Lf[ly, 5:9]
            inJ = (kind == 1) & (X[:, 0] >= NB[:, 0]) & (X[:, 1] <= NB[:, 1]) & (X[:, 2] >= NB[:, 2]) & (X[:, 3] <= NB[:, 3])
            cont |= inJ
            vv = np.where((kind >= 3) & ~dis & ~cont)[0]
            if len(vv):
                cont[vv] |= inside_cell(sh, X[vv], Lf[ly[vv], 9:17])
        stats['contained'] += int((cont & ~dis).sum()); stats['disjoint'] += int(dis.sum())
        bad = ~(dis | cont)
        nb = int(bad.sum())
        if it % 20 == 1 or nb == 0:
            log('phase B chunk %d level %d: pairs %d, unresolved %d, stack %d (%.1fs)' % (it, lev, len(Bi), nb, len(stack), time.time() - t0))
        if nb == 0:
            continue
        if lev >= maxdepth + 6:
            fails += nb
            log('FAIL: %d unresolved pairs at level %d' % (nb, lev))
            continue
        Xi = split4(Bi[bad]); Xj = split4(Bj[bad])
        nbad = int(bad.sum())
        nBi = np.repeat(Xi, 4, axis=0); nBj = np.tile(Xj.reshape(-1, 4, 4), (1, 4, 1)).reshape(-1, 4)
        nli = np.repeat(li[bad], 16); nlj = np.repeat(lj[bad], 16)
        keep = (nBi[:, 0] + nBi[:, 2] < 1.0) & (nBj[:, 0] + nBj[:, 2] < 1.0)
        nBi, nBj, nli, nlj = nBi[keep], nBj[keep], nli[keep], nlj[keep]
        keep = ~excluded(sh, nBi.T) & ~excluded(sh, nBj.T)
        stack.append((nBi[keep], nBj[keep], nli[keep], nlj[keep], lev + 1))
    return dict(ncand=len(cand), nexcl=nex, nleaves=nL, leaves=Lf, stats=stats, fails=fails, time=time.time() - t0)


if __name__ == '__main__':
    import warnings; warnings.filterwarnings('ignore')
    a_lo, a_hi, b_lo, b_hi = [float(x) for x in sys.argv[1:5]]
    pre = sys.argv[5]
    args = [int(x) for x in sys.argv[6:10]]
    d0, d1, kJ, md = (args + [5, 8, 2, 6][len(args):])[:4]
    sh = Shape(a_lo, a_hi, b_lo, b_hi)
    res = run(sh, d0, d1, kJ, md, log=lambda *a: print(*a, flush=True))
    if res is None:
        print('RESULT NOT PROVED (phase A)'); sys.exit(1)
    np.save(pre + '_leaves.npy', res['leaves'])
    json.dump(dict(shape=[a_lo, a_hi, b_lo, b_hi], d0=d0, d1=d1, kJ=kJ, maxdepth=md, ncand=res['ncand'],
                   nexcl=res['nexcl'], nleaves=res['nleaves'], stats=res['stats'], fails=res['fails'], time=res['time']),
              open(pre + '.json', 'w'))
    print('RESULT', 'PROVED' if res['fails'] == 0 else 'NOT PROVED', res['stats'], flush=True)
