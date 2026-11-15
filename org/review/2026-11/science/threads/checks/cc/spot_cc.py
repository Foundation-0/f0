"""Lead's numerical spot check of the central-configuration certificates (not a proof): rebuild each configuration
from the certificate's centre, evaluate the equations sum_j (q_i - q_j)/r_ij^3 - q_i = 0 in high-precision
floating point, and count distinct values of the moment of inertia."""
import json, sys
from fractions import Fraction as Fr
from flint import arb, ctx
ctx.prec = 200
for path in sys.argv[1:]:
    c = json.load(open(path))
    if "classes" not in c:
        print(path, "keys:", list(c.keys())[:12]); continue
    cl = c["classes"]; n = c["n"]
    if path == sys.argv[1]: print("class keys:", list(cl[0].keys()))
    worst = 0.0; Is = []
    for k in cl:
        sc = 2 ** c.get("centre_exp2", c.get("center_exp2", 50))
        z = [Fr(int(v), sc) for v in k["centre_num"]]
        pin = k["pinned_body"]
        q = []; it = iter(z)
        for i in range(n):
            x = next(it); y = Fr(0) if i == pin else next(it)
            q.append((x, y))
        res = 0.0
        for i in range(n):
            fx = arb(0); fy = arb(0)
            for j in range(n):
                if i == j: continue
                dx = q[i][0] - q[j][0]; dy = q[i][1] - q[j][1]
                r2 = arb(dx.numerator) / dx.denominator; r2 = r2 * r2 + (arb(dy.numerator) / dy.denominator) ** 2
                r3 = r2 * r2.sqrt()
                fx += (arb(dx.numerator) / dx.denominator) / r3; fy += (arb(dy.numerator) / dy.denominator) / r3
            fx -= arb(q[i][0].numerator) / q[i][0].denominator; fy -= arb(q[i][1].numerator) / q[i][1].denominator
            res = max(res, abs(float(fx.mid())), abs(float(fy.mid())))
        worst = max(worst, res)
        Is.append(float(sum(a * a + b * b for a, b in q)))
    Is.sort(); gap = min(b - a for a, b in zip(Is, Is[1:]))
    print(f"{path.split('/')[-1]}: n={n}, {len(cl)} classes, worst equation residual {worst:.2e}, smallest gap between inertia values {gap:.2e}")
