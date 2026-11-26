"""Test of the ladder in T444.md on the thread's own samples (survey_probe.out).

Prediction: near the nodal surface one of the three far index-2 points travels
into the flat point, at a distance proportional to the cubic's distance from
a node, nu = min over unit v of |grad C(v)| / |T|. Recompute both for each n
printed in survey_probe.out (3 decimals; every n gives an exact flat point).
"""
import re, sys
import numpy as np
from c3v import flat_config, jets

def nu(T, starts=3000, seed=0):
    rng = np.random.default_rng(seed); best = np.inf
    G = lambda v: np.einsum('ijk,j,k->i', T, v, v) / 2
    for _ in range(starts):
        v = rng.standard_normal(3); v /= np.linalg.norm(v)
        for _ in range(40):  # gradient descent on |G(v)|^2 over the sphere
            Jm = np.einsum('ijk,k->ij', T, v); g = Jm.T @ G(v)
            g -= (g @ v) * v; v -= 0.2 * g / (np.abs(T).max() ** 2); v /= np.linalg.norm(v)
        best = min(best, np.linalg.norm(G(v)))
    return best / np.abs(T).max()

src = sys.argv[1]
rows = []
for line in open(src):
    m = re.match(r"n \[([^\]]*)\] \| far points .*?: \[(.*)\]", line)
    if not m: continue
    n = np.array([float(t) for t in m.group(1).split()])
    radii = [float(r) for r in re.findall(r"\(([0-9.]+), 2,", m.group(2))]
    A, q = flat_config(n); _, _, T = jets(A, q)
    rows.append((nu(T), min(radii), len(radii), n))
rows.sort(key=lambda r: r[0])
print("%-26s %10s %14s %7s" % ("n (thread, 3 dp)", "nu", "nearest other", "found"))
for v, r, k, n in rows:
    print("%-26s %10.4f %14.4f %7d" % (np.array2string(n, precision=3), v, r, k))
x = np.log([r[0] for r in rows]); y = np.log([r[1] for r in rows])
rank = lambda a: np.argsort(np.argsort(a))
rho = np.corrcoef(rank(x), rank(y))[0, 1]
slope = np.polyfit(x, y, 1)[0]
print("Spearman rank correlation of nu and nearest-other radius: %.3f over %d samples" % (rho, len(rows)))
print("log-log slope: %.2f (prediction: about 1)" % slope)
