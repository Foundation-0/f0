"""Symmetric sub-families: harmonic terms of degrees 1..d-1 invariant under a subgroup G of the symmetry group of the
leading form (Ih for the icosahedron, Oh for the octahedron). Families are named <solid>:<kind>:<axis> with kind
stab (elements fixing the axis vector: C5v, C3v, C2v, C4v), pm (elements mapping the axis to +-itself: D5d, D3d, D2h,
D4h), rot (rotations mapping the axis to +-itself: D5, D3, D2, D4), crot (rotations fixing the axis: C5, C3, C2, C4)."""
import numpy as np, itertools
import hmodel as hm
phi = (1 + 5 ** 0.5) / 2
def rotation(axis, ang):
    a = np.asarray(axis, float); a /= np.linalg.norm(a); K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + np.sin(ang) * K + (1 - np.cos(ang)) * K @ K
def closure(gens):
    G = [np.eye(3)]; frontier = [np.eye(3)]
    while frontier:
        new = []
        for g in frontier:
            for h in gens:
                p = h @ g
                if not any(np.abs(p - q).max() < 1e-9 for q in G): G.append(p); new.append(p)
        frontier = new
    return G
def full_group(solid):
    if solid == "icosahedron":
        return closure([rotation((0, 1, phi), 2 * np.pi / 5), rotation((1, 1, 1), 2 * np.pi / 3), np.diag([-1., 1, 1])])
    return closure([rotation((0, 0, 1), np.pi / 2), rotation((1, 1, 1), 2 * np.pi / 3), np.diag([-1., 1, 1])])
AXES = {"icosahedron": {"5": (0, 1, phi), "3": (1, 1, 1), "2": (1, 0, 0)},
        "octahedron": {"4": (0, 0, 1), "3": (1, 1, 1), "2": (1, 1, 0)}}
def subgroup(solid, kind, ax):
    G = full_group(solid); v = np.array(AXES[solid][ax], float); v /= np.linalg.norm(v)
    if kind == "stab": return [g for g in G if np.allclose(g @ v, v)]
    if kind == "pm": return [g for g in G if np.allclose(np.abs(g @ v @ v), 1)]
    if kind == "rot": return [g for g in G if np.linalg.det(g) > 0 and np.allclose(np.abs(g @ v @ v), 1)]
    if kind == "crot": return [g for g in G if np.linalg.det(g) > 0 and np.allclose(g @ v, v)]
    if kind == "T": return [g for g in G if np.linalg.det(g) > 0 and np.allclose(np.abs(g), np.round(np.abs(g)))]
    raise ValueError(kind)
def invariant_basis(j, G):
    """orthonormal coefficient vectors (in the hm.hbasis(j) basis) spanning the G-invariant harmonics of degree j."""
    mons, B = hm.hbasis(j); rng = np.random.default_rng(5); X = rng.normal(size=(8 * len(mons), 3))
    E = np.array(mons); V = lambda Y: np.prod(Y[:, None, :] ** E[None], axis=2)
    VB = V(X) @ B.T                     # values of basis polys at X
    Pm = np.zeros((B.shape[0], B.shape[0]))
    for g in G:
        Pm += np.linalg.lstsq(VB, V(X @ g.T) @ B.T, rcond=None)[0]
    Pm /= len(G)
    u, s, vt = np.linalg.svd(Pm); r = int((s > 0.5).sum())
    return u[:, :r].T
def family(name):
    solid, kind, ax = name.split(":"); G = subgroup(solid, kind, ax)
    d, F = hm.leading(solid)
    return d, F, {j: invariant_basis(j, G) for j in range(1, d)}, len(G)
if __name__ == "__main__":
    for solid in ("octahedron", "icosahedron"):
        print(solid, "group order", len(full_group(solid)))
        for kind in ("stab", "pm", "rot", "crot"):
            for ax in AXES[solid]:
                d, F, ib, n = family(f"{solid}:{kind}:{ax}")
                print(f"  {kind}:{ax} order {n}: invariant dims by degree", [ib[j].shape[0] for j in range(1, d)])
