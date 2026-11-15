#!/usr/bin/env python3
"""Untrusted search that writes a certificate for check.py.

Usage:
    python3 find.py CONFIG.json OUT.cert.json [STARTS] [SEED]

Nothing here needs to be right for the result to be right: check.py re-does
every test. A zero this program misses makes the bisection fail to close,
because no test can exclude a box that holds a zero. It cannot make the
checker accept a wrong count.

Steps: Newton from many starts in floating point, refinement of each zero at
60 digits with mpmath, the largest cube around each zero that passes the
Krawczyk test, then bisection of the root box until every leaf passes a test.
"""

import json
import sys
import time

import mpmath
import numpy as np

import check as C


def float_field(sites, charges):
    p = np.array([[float(v) for v in s] for s in sites])
    q = np.array([float(v) for v in charges])

    def FH(x):
        # x: (m, 3)
        d = x[:, None, :] - p[None, :, :]
        r2 = np.einsum("mjk,mjk->mj", d, d)
        r = np.sqrt(r2)
        ir3 = q[None, :] / (r2 * r)
        ir5 = ir3 / r2
        F = -np.einsum("mj,mjk->mk", ir3, d)
        H = 3 * np.einsum("mj,mja,mjb->mab", ir5, d, d) - ir3.sum(1)[:, None, None] * np.eye(3)[None]
        return F, H

    return p, q, FH


def candidates(sites, charges, starts, seed, extra):
    rng = np.random.default_rng(seed)
    p, q, FH = float_field(sites, charges)
    # uniform points in the tetrahedron (Dirichlet weights) plus points near the
    # charge-weighted centre at several spreads
    w = rng.dirichlet(np.ones(len(p)), size=starts)
    pts = [w @ p]
    centre = (q[:, None] * p).sum(0) / q.sum()
    for spread in (0.003, 0.01, 0.03, 0.1):
        pts.append(centre + spread * rng.standard_normal((starts // 4, 3)))
    if extra:
        pts.append(np.array(extra, dtype=float))
    x = np.vstack(pts)
    scale = np.linalg.norm(p - p.mean(0), axis=1).max()
    for _ in range(80):
        F, H = FH(x)
        try:
            step = np.linalg.solve(H, F[..., None])[..., 0]
        except np.linalg.LinAlgError:
            step = np.zeros_like(x)
        n = np.linalg.norm(step, axis=1)
        cap = 0.05 * scale
        step *= np.minimum(1.0, cap / np.maximum(n, 1e-300))[:, None]
        x = x - step
        bad = ~np.isfinite(x).all(1)
        x[bad] = centre
    F, H = FH(x)
    gnorm = np.linalg.norm(F, axis=1)
    hnorm = np.abs(np.linalg.eigvalsh(H)).max(1)
    ok = np.isfinite(gnorm) & (gnorm < 1e-9 * np.maximum(hnorm, 1e-30) * scale)
    found = []
    for z in x[ok]:
        if all(np.linalg.norm(z - y) > 1e-9 * scale for y in found):
            found.append(z)
    return found


def refine(sites, charges, z, dps=60):
    mpmath.mp.dps = dps
    p = [[mpmath.mpf(str(v.numerator)) / v.denominator for v in s] for s in sites]
    q = [mpmath.mpf(str(v.numerator)) / v.denominator for v in charges]
    x = mpmath.matrix([mpmath.mpf(float(t)) for t in z])
    for _ in range(40):
        F = mpmath.matrix(3, 1)
        H = mpmath.matrix(3, 3)
        for j in range(len(p)):
            d = [x[i] - p[j][i] for i in range(3)]
            r2 = d[0] ** 2 + d[1] ** 2 + d[2] ** 2
            r = mpmath.sqrt(r2)
            a3 = q[j] / (r2 * r)
            a5 = a3 / r2
            for i in range(3):
                F[i] -= a3 * d[i]
                for k in range(3):
                    H[i, k] += 3 * a5 * d[i] * d[k] - (a3 if i == k else 0)
        step = mpmath.lu_solve(H, F)
        x = x - step
        if mpmath.norm(step) < mpmath.mpf(10) ** (-(dps - 8)):
            return [x[i] for i in range(3)]
    return None          # no convergence: a near-zero that is not a zero


def to_grid(v):
    return int(mpmath.nint(v * C.S))


def unique_boxes(tests, zeros, sites):
    boxes = []
    pts = [np.array([float(t) for t in z]) for z in zeros]
    sp = [np.array([float(v) for v in s]) for s in sites]
    for a, z in enumerate(zeros):
        dz = min([np.linalg.norm(pts[a] - pts[b]) for b in range(len(pts)) if b != a] + [1e9])
        ds = min(np.linalg.norm(pts[a] - s) for s in sp)
        r0 = 0.45 * min(dz, ds) / np.sqrt(3)
        c = [to_grid(t) for t in z]
        r = r0
        got = None
        while r > 1e-30:
            ri = int(r * C.S)
            lo = [x - ri for x in c]
            hi = [x + ri for x in c]
            sgn = tests.krawczyk(lo, hi)
            if sgn != 0:
                got = (lo, hi, sgn, r)
                break
            r *= 0.5
        if got is None:
            raise RuntimeError("no Krawczyk box found around zero %d" % a)
        boxes.append(got)
    return boxes


def bisect(tests, root, boxes, max_depth, log_every=20000):
    out = []
    stack = [(root, 0)]
    leaves = 0
    t0 = time.time()
    kbox = [(lo, hi) for (lo, hi, _, _) in boxes]
    while stack:
        (lo, hi), depth = stack.pop()
        leaf = None
        if tests.hull(lo, hi):
            leaf = "H"
        else:
            for m, kb in enumerate(kbox):
                if C.contains(kb, (lo, hi)):
                    leaf = "K%d." % m
                    break
        if leaf is None:
            for k in range(tests.n):
                if tests.dominance(lo, hi, k):
                    leaf = "D%d" % k
                    break
        if leaf is None and tests.taylor(lo, hi, True):
            leaf = "N"
        if leaf is None and tests.taylor(lo, hi, False):
            leaf = "I"
        if leaf is not None:
            out.append(leaf)
            leaves += 1
            if leaves % log_every == 0:
                sys.stderr.write("  %d leaves, %d open, %.0f s\n" % (leaves, len(stack), time.time() - t0))
            continue
        if depth >= max_depth:
            raise RuntimeError("bisection did not close at depth %d near (%s)"
                               % (depth, ", ".join(C.fmt((lo[i] + hi[i]) >> 1) for i in range(3))))
        widths = [hi[i] - lo[i] for i in range(3)]
        ax = widths.index(max(widths))
        mid = (lo[ax] + hi[ax]) >> 1
        out.append("xyz"[ax])
        lh = list(hi)
        lh[ax] = mid
        rl = list(lo)
        rl[ax] = mid
        stack.append(((rl, list(hi)), depth + 1))
        stack.append(((list(lo), lh), depth + 1))
    return "".join(out), leaves


def main(argv):
    cfg, outp = argv[1], argv[2]
    starts = int(argv[3]) if len(argv) > 3 else 20000
    seed = int(argv[4]) if len(argv) > 4 else 1
    sites, charges = C.load_config(cfg)
    extra = json.load(open(cfg)).get("points", [])
    extra = [[float(C.parse_number(v)) for v in pt] for pt in extra]
    t0 = time.time()
    zs = candidates(sites, charges, starts, seed, extra)
    sys.stderr.write("float Newton: %d distinct zeros (%.1f s)\n" % (len(zs), time.time() - t0))
    zeros = []
    for z in zs:
        x = refine(sites, charges, z)
        if x is None:
            continue
        if all(max(abs(x[i] - y[i]) for i in range(3)) > mpmath.mpf(10) ** -40 for y in zeros):
            zeros.append(x)
    sys.stderr.write("refined: %d zeros\n" % len(zeros))
    tests = C.Tests(sites, charges)
    boxes = unique_boxes(tests, zeros, sites)
    sys.stderr.write("Krawczyk boxes: %d (%.1f s)\n" % (len(boxes), time.time() - t0))
    tree, leaves = bisect(tests, C.root_box(sites), boxes, C.MAX_DEPTH)
    sys.stderr.write("bisection closed: %d leaves (%.1f s)\n" % (leaves, time.time() - t0))
    cert = {
        "P": C.P,
        "config": cfg,
        "boxes": [{"lo": [str(x) for x in lo], "hi": [str(x) for x in hi]} for (lo, hi, _, _) in boxes],
        "tree": tree,
    }
    with open(outp, "w") as fh:
        json.dump(cert, fh)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
