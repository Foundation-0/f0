"""The wall structure of a point-charge configuration.

For positive charges the potential V rises to infinity at each charge. Follow the field uphill from any point and
you reach a charge, so space divides into one basin per charge. The walls between basins are the surfaces that
flow uphill INTO an index-2 balance point (two downhill directions lie in the wall, one uphill direction crosses it).
So each index-2 point is one wall, and the two uphill branches from it end at the two charges whose basins it
separates.  This program follows those two branches for every index-2 point of a certified configuration and
prints the multigraph: vertices = charges, edges = walls.

Checks: with n charges, m2 walls and one connected piece, the number of independent cycles is m2 - (n - 1),
which must equal the number of index-1 points (the Morse relation).  Maxwell's bound (n-1)^2 is the count when
every pair of charges shares exactly one wall: m2 = n(n-1)/2.

Numerical, not a proof: arb ball arithmetic at high precision is used only so that the tiny charges are resolved.
Usage: python wall_graph.py <result.json from indep_count.py> [<config or certificate .json>]"""
import json, sys, itertools, collections
from fractions import Fraction as Fr
from flint import arb, ctx
ctx.prec = 600
def A(fr): fr = Fr(fr); return arb(fr.numerator) / arb(fr.denominator)
res = json.load(open(sys.argv[1]))
cfg = json.load(open(sys.argv[2] if len(sys.argv) > 2 else res["file"]))
sites = [[A(c) for c in s] for s in cfg["sites"]]; q = [A(c) for c in cfg["charges"]]; n = len(q)
rad = [A(r) for r in res["charge_ball_radii"]]
def grad(x):
    g = [arb(0)] * 3
    for a, qi in zip(sites, q):
        d = [x[k] - a[k] for k in range(3)]; r2 = d[0] * d[0] + d[1] * d[1] + d[2] * d[2]; r3 = r2 * r2.sqrt()
        for k in range(3): g[k] = g[k] - qi * d[k] / r3
    return g
def hess(x):
    Hm = [[arb(0)] * 3 for _ in range(3)]
    for a, qi in zip(sites, q):
        d = [x[k] - a[k] for k in range(3)]; r2 = d[0] * d[0] + d[1] * d[1] + d[2] * d[2]; r5 = r2 * r2 * r2.sqrt()
        for i in range(3):
            for j in range(3):
                Hm[i][j] = Hm[i][j] + qi * (3 * d[i] * d[j] - (r2 if i == j else 0)) / r5
    return Hm
def norm(v): return (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]).sqrt()
def uphill_dir(Hm):
    # eigenvector of the single positive eigenvalue, by power iteration on H + s I (s makes it the largest)
    import numpy as np
    Hf = np.array([[float(Hm[i][j].mid()) for j in range(3)] for i in range(3)])
    sc = np.abs(Hf).max(); w, V = np.linalg.eigh(Hf / sc)
    if not (w[2] > 0 and w[1] < 0): return None
    return [arb(float(V[k, 2])) for k in range(3)]
def nearest(x):
    best = None
    for i, a in enumerate(sites):
        d = norm([x[k] - a[k] for k in range(3)])
        if best is None or d < best[1]: best = (i, d)
    return best
def climb(x0, v, sign):
    i0, d0 = nearest(x0)
    # start a small step along the uphill direction; the step scale is the distance to the nearest charge
    # a tiny generic offset stands in for a generic perturbation of the configuration: in a symmetric
    # configuration an uphill branch can run exactly along an axis into another balance point and stall there
    off = [arb("0.3718"), arb("-0.8123"), arb("0.4496")]
    x = [x0[k] + sign * v[k] * d0 * arb("1e-3") + off[k] * d0 * arb("1e-40") for k in range(3)]
    for it in range(20000):
        i, d = nearest(x)
        if d < rad[i]: return i, it
        # work with midpoints only: this is a numerical trace, and carried error radii would swamp the tiny
        # field near another balance point
        g = [t.mid() for t in grad(x)]; gn = norm(g).mid(); h = (d * arb("0.02")).mid()
        xm = [(x[k] + g[k] / gn * h / 2).mid() for k in range(3)]
        gm = [t.mid() for t in grad(xm)]; gmn = norm(gm).mid()
        x = [(x[k] + gm[k] / gmn * h).mid() for k in range(3)]
    return None, it
edges = []; bad = 0
for z in res["zeros"]:
    if int(z["index"]) != 2: continue
    x0 = [A(c) for c in z["centre"]]
    v = uphill_dir(hess(x0))
    if v is None: bad += 1; continue
    a, _ = climb(x0, v, +1); b, _ = climb(x0, v, -1)
    if a is None or b is None: bad += 1; continue
    edges.append(tuple(sorted((a, b))))
m2 = int(res["index2"]); m1 = int(res["index1"])
cnt = collections.Counter(edges)
pairs = len([e for e in cnt if e[0] != e[1]]); loops = sum(c for e, c in cnt.items() if e[0] == e[1])
# connected components
par = list(range(n))
def find(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
for a, b in edges: par[find(a)] = find(b)
comp = len({find(i) for i in range(n)})
print(f"{cfg.get('name', sys.argv[1])}: n = {n}, index-2 points = {m2}, walls traced = {len(edges)}, failures = {bad}")
print(f"  pairs of charges that share a wall: {pairs} of {n*(n-1)//2} possible; walls from a charge back to itself: {loops}; connected pieces: {comp}")
print(f"  independent cycles = walls - n + pieces = {len(edges) - n + comp}; index-1 points = {m1}; Maxwell's count needs {n*(n-1)//2} walls, one per pair")
mult = collections.Counter(c for e, c in cnt.items() if e[0] != e[1])
print(f"  number of walls shared by a pair: " + ", ".join(f"{k} walls: {v} pairs" for k, v in sorted(mult.items())))
print("  charges (index: value): " + ", ".join(f"{i}: {float(qi.mid()):.3g}" for i, qi in enumerate(q)))
print("  walls: " + ", ".join(f"{a}-{b} x{c}" for (a, b), c in sorted(cnt.items())))
