"""Ray profile through the certified record points: u* = direction of (s/mean(s) - 1), eps_equiv = its norm.
Does the record ray stay all-real as eps -> 0?  Usage: python certray.py {880|2288}"""
import sys, json
from fractions import Fraction
import numpy as np
from unit import make, load_generic, solve_at_s, classify, HERE

import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
# Clone of the rigid-realizations repository (not in this folder). Set RIGID_REPO to its path.
RIGID_REPO = _os.environ.get("RIGID_REPO", _os.path.join(_HERE, "..", "..", "..", "repos", "rigid-realizations"))
L2288 = _os.path.join(_HERE, "..", "l2288", "lengths_2288.json")
which = sys.argv[1]
if which == "880":
    n = 10
    d = json.load(open(RIGID_REPO + "/rigid_realizations_l880_pr_bundle/results/l880-all-880-real/l880_certificate.json"))
    s = np.array([float(Fraction(x)) ** 2 for x in d["edge_lengths"]]); E = [tuple(e) for e in d["edges"]]
elif which == "868":
    n = 10
    d = json.load(open(RIGID_REPO + "/rigid_realizations_l880_pr_bundle/results/l880-bartzos-868/l880_bartzos868_certificate.json"))
    s = np.array([float(Fraction(x)) ** 2 for x in d["edge_lengths"]]); E = [tuple(e) for e in d["edges"]]
else:
    n = 11
    d = json.load(open(L2288))
    s = np.array([float(Fraction(x)) for x in d["sq_lengths_exact"]]); E = [tuple(e) for e in d["edges"]]
L, N = make(n)
assert [tuple(e) for e in L.E] == E, "edge order differs"
S0, P0 = load_generic(n)
s = s / s.mean()
e0 = np.linalg.norm(s - 1); u = (s - 1) / e0
out = dict(which=which, eps_equiv=e0, profile=[])
for eps in [e0, 0.01, 3e-3, 1e-3, 1e-4, 1e-5]:
    Z, P1 = solve_at_s(L, S0, P0, 1 + eps * u, tol_rel=1e-7, rounds=8)
    r = classify(L, Z)
    ok = r["nfound"] == N and r["conj_ok"]
    out["profile"].append(dict(eps=eps, ok=bool(ok), real_full=2 * r["nreal"], minsep=r["minsep"]))
    print(f"{which}: eps={eps:.3g} ok={ok} real={2*r['nreal']}/{2*N} minsep={r['minsep']:.2e}", flush=True)
json.dump(out, open(f"{HERE}/certray_{which}.json", "w"), indent=1)
