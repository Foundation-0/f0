#!/usr/bin/env python3
"""NUMERICAL side experiment for the superlinear-growth question (not proof).

How many real critical points can a harmonic polynomial of degree d on R^3 have in the unit ball?
If the answer grows like d^2 (the dimension of the space of such polynomials), then building a
degree-d local jet from ~d^2 charges and unfolding it gives only O(n) equilibria. If it grows
faster (towards the Bezout number (d-1)^3), the jet route could give superlinear growth.

Random model: h(x) = sum_{l=1..d} sum_{j=1..2l+1} Re(c_lj (a_lj . x)^l), with a_lj = u + i v for
random orthonormal u, v (so a.a = 0 and (a.x)^l is harmonic) and c_lj complex Gaussian. The degree-l
part is scaled so that every degree has comparable size on the unit sphere.
Critical points in |x| < 1 are found by vectorised Newton from many seeds and deduplicated.
"""
import sys

import numpy as np


def random_poly(d, rng):
    terms = []
    for l in range(1, d + 1):
        for _ in range(2 * l + 1):
            u = rng.normal(size=3)
            u /= np.linalg.norm(u)
            v = rng.normal(size=3)
            v -= (v @ u) * u
            v /= np.linalg.norm(v)
            a = u + 1j * v
            c = (rng.normal() + 1j * rng.normal()) / np.sqrt(2 * l + 1)
            terms.append((l, a, c))
    return terms


def gH(terms, X):
    g = np.zeros(X.shape, dtype=float)
    H = np.zeros((X.shape[0], 3, 3), dtype=float)
    for l, a, c in terms:
        s = X @ a
        g += np.real((c * l * s ** (l - 1))[:, None] * a[None, :])
        if l >= 2:
            H += np.real((c * l * (l - 1) * s ** (l - 2))[:, None, None] * np.outer(a, a)[None])
    return g, H


def count(terms, rng, nseed=20000, iters=60):
    X = rng.uniform(-1, 1, size=(nseed, 3))
    X = X[np.linalg.norm(X, axis=1) < 1]
    for _ in range(iters):
        g, H = gH(terms, X)
        try:
            step = np.linalg.solve(H, g[..., None])[..., 0]
        except np.linalg.LinAlgError:
            step = np.zeros_like(X)
        nrm = np.linalg.norm(step, axis=1, keepdims=True)
        step = np.where(nrm > 0.2, step * 0.2 / np.maximum(nrm, 1e-300), step)
        X = X - step
    g, H = gH(terms, X)
    ok = (np.linalg.norm(g, axis=1) < 1e-10) & (np.linalg.norm(X, axis=1) < 1)
    P = X[ok]
    pts = []
    for p in P:
        if all(np.linalg.norm(p - q) > 1e-6 for q in pts):
            pts.append(p)
    return len(pts)


if __name__ == "__main__":
    rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
    print(" d  trials  mean   max   (d-1)^3  d^2")
    for d in range(2, 10):
        cs = [count(random_poly(d, rng), rng) for _ in range(12)]
        print(f"{d:2d} {len(cs):6d} {np.mean(cs):6.1f} {max(cs):5d} {(d-1)**3:8d} {d*d:5d}", flush=True)
