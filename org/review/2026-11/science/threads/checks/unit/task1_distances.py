"""Task 1: how far the record lengths are from the all-equal point.
eps_equiv = || s / mean(s) - 1 ||_2 with s the squared lengths: this is exactly the eps of the near cell
(s = 1 + eps u, u a unit vector orthogonal to (1,..,1)) after rescaling.  Also report it for lengths."""
import json, os
from fractions import Fraction
import numpy as np

S = "S"
R = S + "/repos/rigid-realizations/rigid_realizations_l880_pr_bundle/results"


def stats(name, lam):
    lam = np.asarray(lam, float)
    s = lam ** 2
    out = dict(name=name, m=len(lam), ratio_max_min=float(lam.max() / lam.min()),
               max_rel_dev_len=float(np.abs(lam / lam.mean() - 1).max()),
               l2_dev_len=float(np.linalg.norm(lam / lam.mean() - 1)),
               eps_equiv_sq=float(np.linalg.norm(s / s.mean() - 1)))
    return out


rows = []
d = json.load(open(R + "/l880-all-880-real/l880_certificate.json"))
rows.append(stats("L880 all-880 certificate", [float(Fraction(x)) for x in d["edge_lengths"]]))
d = json.load(open(R + "/l880-bartzos-868/l880_bartzos868_certificate.json"))
rows.append(stats("L880 Bartzos et al. published lengths (>=860 Maple, 868 certified)", [float(Fraction(x)) for x in d["edge_lengths"]]))
d = json.load(open(S + "/threads/l2288/lengths_2288.json"))
rows.append(stats("L2288 all-2288 lengths", [float(Fraction(x)) ** 0.5 for x in d["sq_lengths_exact"]]))
# reference: typical eps of the far cell (iid U[0.5,1.5])
rng = np.random.default_rng(0)
for m in (17, 19):
    e = [stats("", rng.uniform(0.5, 1.5, m))["eps_equiv_sq"] for _ in range(20000)]
    rows.append(dict(name=f"far cell reference, m={m}: median eps_equiv_sq", eps_equiv_sq=float(np.median(e)),
                     q05=float(np.quantile(e, 0.05)), q95=float(np.quantile(e, 0.95))))
for r in rows:
    print(json.dumps(r))
json.dump(rows, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "task1_distances.json"), "w"), indent=1)
