#!/usr/bin/env python3
"""NUMERICAL exploration (not proof): n=8 (C7 + centre charge) and n=9 (C7 + third ABK pair).

Uses the arb-midpoint Newton of indep_count.py as a local finder near the centre c=(1,1,1).
Equilibria of C7 farther than R_LOC from c are assumed to persist (the added charges are tiny and
far away from them); this is checked afterwards by the rigorous run of indep_count.py on the
chosen configurations.
"""
import json
import sys
from fractions import Fraction

import numpy as np
from flint import arb, ctx, fmpq

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import indep_count as ic  # noqa: E402

ctx.prec = 200
S = "."   # set to the folder that holds repos/point-charges (a clone at a2fd159) and work/
C7 = json.load(open(S + "/repos/point-charges/certificates/n7-abk-second-pair.json"))
C5 = json.load(open(S + "/repos/point-charges/certificates/n5-abk-bipyramid.json"))
c = [fmpq(1), fmpq(1), fmpq(1)]
SQ6 = 6 ** 0.5


def alpha_at_centre(sites, charges):
    cfg = ic.Config(sites, charges)
    g, H = cfg.gH_arb([arb(v) for v in c])
    Hm = np.array([[float(H[i][j].mid()) for j in range(3)] for i in range(3)])
    e = np.ones(3) / 3 ** 0.5
    k_axis = e @ Hm @ e
    k_plane = (np.trace(Hm) - k_axis) / 2
    alpha = -(6 * SQ6 * k_axis) / 4  # ABK units: V_ABK(u) = sqrt6 V(sqrt6 u)
    return alpha, k_plane, k_axis, [float(v.mid()) for v in g]


def abk_q(alpha, t, beta=15 / 8):
    eta = t / 2 ** 0.5  # offset t(1,1,1) has length t*sqrt3; circumradius sqrt6
    gamma = beta ** 2 / (30 * alpha)
    return alpha * eta ** 3 - gamma * eta ** 5


def local_count(sites, charges, rloc, nseed=1500, rmin=1e-12, seed=0):
    cfg = ic.Config(sites, charges)
    rng = np.random.default_rng(seed)
    pts = []
    for _ in range(nseed):
        v = rng.normal(size=3)
        v /= np.linalg.norm(v)
        r = np.exp(rng.uniform(np.log(rmin), np.log(rloc)))
        x0 = np.ones(3) + r * v
        xq = ic.newton(cfg, x0)
        if xq is None:
            continue
        y = np.array([float(Fraction(int(q.p), int(q.q)) - 1) for q in xq])
        if np.linalg.norm(y) > rloc:
            continue
        new = True
        for p in pts:
            if np.linalg.norm(p[0] - y) <= 1e-9 * max(np.linalg.norm(y), np.linalg.norm(p[0])) + 1e-30:
                new = False
                break
        if new:
            g, H = cfg.gH_arb([arb(v) for v in xq])
            det = float((H[0][0] * (H[1][1] * H[2][2] - H[1][2] * H[2][1])
                         - H[0][1] * (H[1][0] * H[2][2] - H[1][2] * H[2][0])
                         + H[0][2] * (H[1][0] * H[2][1] - H[1][1] * H[2][0])).mid())
            pts.append((y, 2 if det > 0 else 1))
    return pts


if __name__ == "__main__":
    mode = sys.argv[1]
    a5, kp5, ka5, _ = alpha_at_centre(C5["sites"], C5["charges"])
    print(f"C5 centre: alpha={a5:.6g} (NOTE: ~0.00284); ABK q for t=1/2048: {abk_q(a5, 1/2048):.6g} (NOTE: ~1.168e-13)")
    a7, kp7, ka7, g7 = alpha_at_centre(C7["sites"], C7["charges"])
    print(f"C7 centre: alpha={a7:.6g}, in-plane k={kp7:.6g}, axial k={ka7:.6g}, |g|={np.linalg.norm(g7):.2e}")
    sites7, q7 = C7["sites"], C7["charges"]
    if mode == "n8":
        for p in [int(x) for x in sys.argv[2:]]:
            q8 = Fraction(1, 2 ** p)
            ring = (float(q8) / kp7) ** (1 / 3)
            pts = local_count(sites7 + [["1", "1", "1"]], q7 + [str(q8)], 1e-5, nseed=800)
            m1 = sum(1 for p_ in pts if p_[1] == 1)
            print(f"n8 q8=2^-{p}: ring radius ~{ring:.3g}; local zeros within 1e-5: {len(pts)} "
                  f"(idx1 {m1}, idx2 {len(pts)-m1}); radii {sorted(set(float('%.3g' % np.linalg.norm(p_[0])) for p_ in pts))}",
                  flush=True)
    if mode == "n7local":
        pts = local_count(sites7, q7, 1e-5, nseed=800)
        print("C7 local zeros within 1e-5:", len(pts), sorted(float('%.3g' % np.linalg.norm(p_[0])) for p_ in pts))
    if mode == "n9":
        t = Fraction(1, 2 ** int(sys.argv[2]))
        qf = abk_q(a7, float(t))
        print(f"t=2^-{sys.argv[2]}: ABK formula q9={qf:.6g}", flush=True)
        P = 100
        k0 = round(qf * 2 ** P)
        for rel in [float(x) for x in sys.argv[3:]]:
            k = round(k0 * (1 + rel))
            q9 = Fraction(k, 2 ** P)
            s = [["%s" % (1 + t)] * 3, ["%s" % (1 - t)] * 3]
            pts = local_count(sites7 + s, q7 + [str(q9), str(q9)], 1e-5, nseed=1500,
                              rmin=float(t) * 1e-4)
            m1 = sum(1 for p_ in pts if p_[1] == 1)
            print(f"  rel={rel:+.4f} k={k}: local zeros within 1e-5: {len(pts)} (idx1 {m1}, idx2 {len(pts)-m1})"
                  f" -> total {len(pts) + 40} if the 40 outer C7 zeros persist", flush=True)
