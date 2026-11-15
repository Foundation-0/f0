"""Type of the cubic at the flat point, by the number of its singular directions.

A harmonic cubic C at a flat point of four charges: its critical directions
(grad C(v) = 0, |v| = 1, up to sign) are the singular points of the plane cubic
curve C = 0. Smooth: none (Arnold P8 = T333, mu 8). Nodal: one (T334, mu 9).
Line + conic: two (T344, mu 10). Triangle: three (T444, mu 11).
"""
import numpy as np
from c3v import flat_config, jets

def singular_directions(T, starts=4000, seed=0):
    rng = np.random.default_rng(seed)
    G = lambda v: np.einsum('ijk,j,k->i', T, v, v) / 2
    found = []
    scale = np.abs(T).max()
    for _ in range(starts):
        v = rng.standard_normal(3); v /= np.linalg.norm(v)
        for _ in range(60):   # Gauss-Newton on grad C(v) = 0 with |v| = 1
            Jm = np.einsum('ijk,k->ij', T, v)
            A = np.vstack([Jm, v]); b = np.concatenate([G(v), [0.0]])
            v = v - np.linalg.lstsq(A, b, rcond=None)[0]
            v /= np.linalg.norm(v)
        if np.linalg.norm(G(v)) < 1e-12 * scale:
            if all(min(np.linalg.norm(v - w), np.linalg.norm(v + w)) > 1e-6 for w in found):
                found.append(v)
    return found

cases = {
    "general (0.44, 0.45, 0.65, 0.44), the flat route": [0.43934086853062476, 0.44580836016981545, 0.6458977142570842, 0.4370934110220955],
    "two equal pairs (0.4, 0.4, 0.5831, 0.5831)": [0.4, 0.4, np.sqrt(0.34), np.sqrt(0.34)],
    "two equal pairs (0.3, 0.3, 0.6403, 0.6403)": [0.3, 0.3, np.sqrt(0.41), np.sqrt(0.41)],
    "regular tetrahedron": [0.5, 0.5, 0.5, 0.5],
}
for name, n in cases.items():
    A, q = flat_config(n); _, _, T = jets(A, q)
    d = singular_directions(T)
    print("%-52s singular directions of the cubic: %d" % (name, len(d)))
