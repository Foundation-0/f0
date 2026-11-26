"""Where in the flat family is the cubic term degenerate?
For a flat configuration n the cubic C is harmonic. Its gradient is three quadrics. If they have a common non-zero
(complex) solution, the flat point has multiplicity above 8. The degree-4 Macaulay matrix of the three quadrics has
rank 27 exactly when the only common solution is 0, so its 27th singular value measures the distance to degeneracy;
the 26th and 25th measure deeper degeneracy (the regular tetrahedron, cubic xyz, has three lines of solutions)."""
import numpy as np, sys, json
import quadrics as qd
rng = np.random.default_rng(int(sys.argv[1])); NS = int(sys.argv[2])
def tensors(ns):
    t = ns / np.sqrt(1 - ns**2)
    G = -np.einsum('si,sj->sij', t**2, t**2); G[:, range(4), range(4)] = t**2
    w, V = np.linalg.eigh(G); A = V[:, :, 1:] * np.sqrt(np.maximum(w[:, None, 1:], 0))
    r = np.linalg.norm(A, axis=2); U = A / r[..., None]; q = t**3 / (1 + t**2); c = q / r**4
    T = qd.tensor(U, c); T /= np.sqrt((T**2).sum(axis=(1, 2, 3)))[:, None, None, None]
    return T
def small_sv(ns):
    T = tensors(ns); B = ns.shape[0]
    co = qd.coefficients(T, np.zeros((B, 3, 3)), np.zeros((B, 3)))
    M = np.zeros((B, 30, 35))
    for a in range(3):
        for m in range(10): M[:, a * 10 + m, qd.ADD[m]] = co[:, a, :]
    sv = np.linalg.svd(M, compute_uv=False)
    return sv[:, 22:27] / sv[:, :1]
if __name__ == "__main__":
    ns = np.abs(rng.normal(size=(NS, 4))); ns /= np.linalg.norm(ns, axis=1)[:, None]
    ns = ns[ns.min(1) > 0.02]
    sv = np.vstack([small_sv(ns[i:i + 20000]) for i in range(0, len(ns), 20000)])
    print("regular tetrahedron: singular values 23..27 over the largest:", np.array2string(small_sv(np.full((1, 4), 0.5))[0], precision=2))
    for k, name in ((4, "27th"), (3, "26th"), (2, "25th")):
        v = sv[:, k]; print(f"{name} singular value: median {np.median(v):.3f}, 1% quantile {np.quantile(v, 0.01):.2e}, minimum {v.min():.2e}")
    order = np.argsort(sv[:, 3])[:12]
    print("configurations with the smallest 26th singular value (n sorted, then singular values 25th, 26th, 27th):")
    for i in order: print("  ", np.round(np.sort(ns[i]), 4), np.array2string(sv[i, 2:], precision=2))
    order = np.argsort(sv[:, 4])[:8]
    print("configurations with the smallest 27th singular value:")
    for i in order: print("  ", np.round(np.sort(ns[i]), 4), np.array2string(sv[i, 2:], precision=2))
    np.save("disc_scan_ns.npy", ns); np.save("disc_scan_sv.npy", sv)
