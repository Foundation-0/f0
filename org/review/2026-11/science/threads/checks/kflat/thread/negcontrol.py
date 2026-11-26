"""Negative controls for certify.py: (1) shifted points must not certify; (2) a duplicated root must be caught by
the separation rule (boxes shrink to sep/4 = 0 -> fail); (3) a model with a known count (random unfolding) certifies
exactly the solver's real count, never more."""
import numpy as np, htrack as ht, hmodel as hm, certify as cf
solid, d, F, th = hm.load_model("sym_octahedron_crot_3_2.json")
C = hm.model(F, d, th); P = ht.Poly(C); X = ht.roots(P, 11); Xr, idx, pok = ht.real_roots(P, X)
Cl = hm.to_array([F], d)
ok, n = cf.certify(solid, C, Cl, Xr + 1e-4 * np.random.default_rng(0).normal(size=Xr.shape)); print("shifted points certified:", ok, "(expect 0)")
ok, n = cf.certify(solid, C, Cl, np.vstack([Xr, Xr[:1]])); print("with one duplicate:", ok, "(expect 25: the duplicated root fails twice)")
rng = np.random.default_rng(5)
th2 = [rng.normal(size=2 * j + 1) * 0.3 for j in range(1, d)]; C2 = hm.model(F, d, th2); P2 = ht.Poly(C2)
X2 = ht.roots(P2, 1); Xr2, idx2, _ = ht.real_roots(P2, X2)
ok, n = cf.certify(solid, C2, Cl, Xr2); print("random unfolding: solver real", len(Xr2), "certified", ok)
