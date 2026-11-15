"""Corrupt a certificate in several ways and confirm certify.py rejects each (run also under python -O).
Usage: python test_certify_corrupt.py cert.json"""
import json, sys, subprocess, copy, os
from fractions import Fraction as Fr

src = sys.argv[1]
d = json.load(open(src))
here = os.path.dirname(os.path.abspath(__file__))
py = sys.executable
cases = {}
# 1. shift one centre coordinate by 2^-30 (far outside its 2^-36 box)
c = copy.deepcopy(d); c["centers"] = c["centers"][:20]
c["centers"][3][5] += 2 ** (c["center_scale_exp2"] - 30); cases["shifted centre"] = c
# 2. change one squared length by 1e-6
c = copy.deepcopy(d); c["centers"] = c["centers"][:20]
c["sq_lengths"][0] = str(Fr(c["sq_lengths"][0]) + Fr(1, 10 ** 6)); cases["changed length"] = c
# 3. duplicate a centre (two boxes for one solution)
c = copy.deepcopy(d); c["centers"] = c["centers"][:20]; c["centers"].append(list(c["centers"][7])); cases["duplicate box"] = c
# 4. inconsistent pinned triangle
c = copy.deepcopy(d); c["centers"] = c["centers"][:20]
c["pinned"]["10"][0] = str(Fr(c["pinned"]["10"][0]) + Fr(1, 10 ** 9)); cases["pinned vertex moved"] = c
# 5. wrong graph (swap an edge)
c = copy.deepcopy(d); c["centers"] = c["centers"][:20]; c["edges"][0] = [1, 3]; cases["edge changed"] = c
# control: the first 20 boxes unchanged must pass
c = copy.deepcopy(d); c["centers"] = c["centers"][:20]; cases["control (unchanged, 20 boxes)"] = c
ok_all = True
for opt in ([], ["-O"]):
    for name, c in cases.items():
        p = os.path.join(here, "_corrupt.json"); json.dump(c, open(p, "w"))
        r = subprocess.run([py, "-I"] + opt + [os.path.join(here, "certify.py"), p], capture_output=True, text=True)
        expect_fail = not name.startswith("control")
        failed = r.returncode != 0
        status = "rejected" if failed else "accepted"
        last = (r.stdout.strip().splitlines() or [""])[-1]
        good = failed == expect_fail
        ok_all &= good
        print(f"{' '.join(opt) or '  '} {name:32s} {status:8s} {'OK' if good else 'WRONG'} | {last[:90]}")
os.remove(os.path.join(here, "_corrupt.json"))
print("ALL CORRUPTION TESTS BEHAVED" if ok_all else "SOME TESTS MISBEHAVED")
