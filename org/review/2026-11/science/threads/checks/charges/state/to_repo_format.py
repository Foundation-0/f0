#!/usr/bin/env python3
"""Write my n8/n9 results in the repository's certificate format so that the repository's own
verify_arb.py (copied to repo_copy/) can re-check them as a second program. Zero boxes are cubes
around my ball centres; the half-width starts at rho/2 and is halved until the repository's
Krawczyk test accepts it (box choice only; the proof is verify_arb.py's own run).
Usage: to_repo_format.py config.json mine.json out.json"""
import json, sys, os
from fractions import Fraction
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "repo_copy"))
import verify_arb as va
from flint import fmpq
cfg = json.load(open(sys.argv[1])); mine = json.load(open(sys.argv[2]))
C = va.Config(cfg["sites"], cfg["charges"])
zeros = []
for z in mine["zeros"]:
    c = [Fraction(v) for v in z["centre"]]
    h = Fraction(z["rho"]) / 2
    for _ in range(30):
        lo = [v - h for v in c]; hi = [v + h for v in c]
        ok, _ = va.krawczyk(C, [va.Q(str(v)) for v in lo], [va.Q(str(v)) for v in hi])
        if ok:
            break
        h /= 2
    zeros.append(dict(box=[[str(v) for v in lo], [str(v) for v in hi]], index=z["index"]))
out = dict(name=cfg["name"], sites=cfg["sites"], charges=cfg["charges"], count=len(zeros), zeros=zeros)
json.dump(out, open(sys.argv[3], "w"), indent=1)
print("wrote", sys.argv[3])
