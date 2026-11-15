"""Model polynomials: leading harmonic form F of degree d plus harmonic terms of degrees 1..d-1, as dense arrays."""
import numpy as np, itertools
import polysys as ps
phi = (1 + 5 ** 0.5) / 2
SOLIDS = {"octahedron": np.array([(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)], float),
          "cube": np.array(list(itertools.product((-1, 1), repeat=3)), float),
          "icosahedron": np.array([p for s1 in (-1,1) for s2 in (-1,1) for p in ((0, s1, s2*phi), (s1, s2*phi, 0), (s2*phi, 0, s1))], float)}
_hb = {}
def hbasis(j):
    if j not in _hb: _hb[j] = ps.harmonic_basis(j)
    return _hb[j]
def to_array(terms, d):
    C = np.zeros((d + 1,) * 3)
    for mons, c in terms:
        for m, v in zip(mons, c): C[m] += v
    return C
def harm(j, theta):
    mons, B = hbasis(j); return mons, np.asarray(theta) @ B
def leading(which):
    U = SOLIDS[which]; U = U / np.linalg.norm(U[0]); d = 6 if which == "icosahedron" else 4
    mons, c = ps.solid_term(U, d); c = np.where(np.abs(c) < 1e-12 * np.abs(c).max(), 0, c)
    return d, (mons, c / np.abs(c).max())
def model(Fterm, d, thetas):
    """thetas: list over j = 1..d-1 of coefficient vectors in the orthonormal harmonic basis of degree j."""
    terms = [Fterm] + [harm(j, thetas[j - 1]) for j in range(1, d)]
    return to_array(terms, d)
def dims(d): return [2 * j + 1 for j in range(1, d)]
def split(theta, d):
    out = []; o = 0
    for n in dims(d): out.append(theta[o:o + n]); o += n
    return out
def load_model(path):
    """(solid, d, Fterm, thetas) from a sym_scan.py result ("family", "p") or an assembled model ("solid", "theta")."""
    import json, sym
    J = json.load(open(path))
    if "theta" in J and isinstance(J["theta"][0], list):
        solid = J["solid"]; d, F = leading(solid); return solid, d, F, [np.array(t) for t in J["theta"]]
    fam = J["family"]; solid = fam.split(":")[0]; d, F, ib, order = sym.family(fam)
    p = np.array(J["p"]); TH = []; o = 0
    for j in range(1, d):
        n = ib[j].shape[0]; TH.append(p[o:o + n] @ ib[j] if n else np.zeros(2 * j + 1)); o += n
    return solid, d, F, TH
