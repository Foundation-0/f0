"""
Independent exact check of the gfq-codes Delsarte certificates.
Theorem used (Delsarte 1973): for any code C of length n over an alphabet of size q with
minimum distance >= d, if f(x) = sum_j a_j K_j(x) has a_0 > 0, a_j >= 0 and f(i) <= 0 for
i = d..n, then |C| <= f(0)/a_0.  K_j by the three-term recurrence (not the repository's
binomial sum or generating product).  Integers and Fractions only; failures raise SystemExit, so the check does not depend on assert statements.
Standard library only.
Usage: python3 -I delsarte_independent.py <gfq-codes clone>
"""
import json, sys, glob, os
from fractions import Fraction

def kraw_table(q, n, jmax):
    # K[j][x], recurrence: (j+1)K_{j+1}(x) = ((n-j)(q-1) + j - q x) K_j(x) - (q-1)(n-j+1) K_{j-1}(x)
    K = [[1] * (n + 1), [n * (q - 1) - q * x for x in range(n + 1)]]
    for j in range(1, jmax):
        row = []
        for x in range(n + 1):
            num = ((n - j) * (q - 1) + j - q * x) * K[j][x] - (q - 1) * (n - j + 1) * K[j - 1][x]
            if num % (j + 1): raise SystemExit(f"non-integer Krawtchouk value at j={j+1}, x={x}")
            row.append(num // (j + 1))
        K.append(row)
    return K

def check(c):
    q, n, k, d = c["q"], c["n"], c["k"], c["excluded_distance"]
    a = [Fraction(v) for v in c["krawtchouk_coefficients"]]
    if len(a) > n + 1: raise SystemExit("too many coefficients")
    if not a[0] > 0 or any(v < 0 for v in a[1:]): raise SystemExit(f"{c['id']}: sign condition fails")
    K = kraw_table(q, n, max(1, len(a) - 1))
    f = lambda x: sum(a[j] * K[j][x] for j in range(len(a)))
    worst = max(f(i) for i in range(d, n + 1))
    if worst > 0: raise SystemExit(f"{c['id']}: f positive on [d,n]")
    bound = f(0) / a[0]
    if bound != Fraction(c["size_bound"]): raise SystemExit(f"{c['id']}: declared size_bound differs from f(0)/a_0")
    if not bound < q ** k: raise SystemExit(f"{c['id']}: bound {bound} is not below q^k")
    # how tight: would the same certificate also exclude a smaller dimension or leave room?
    return q, n, k, d, bound, q ** k, max(f(i) for i in range(d, n + 1)), min(i for i in range(n + 1) if f(i) <= 0 and all(f(t) <= 0 for t in range(i, n + 1)))

rows = []
files = sorted(glob.glob(os.path.join(sys.argv[1], "results", "*", "certificate.json")))
for p in files:
    for c in json.load(open(p))["certificates"]:
        rows.append((c["id"],) + check(c))
print(f"{len(rows)} certificates in {len(files)} certificate files pass the independent exact check")
print("id | q n k | excluded d | size bound (float) | q^k | bound/q^k")
for r in rows:
    print(f"{r[0]:28s} | {r[1]} {r[2]:2d} {r[3]:2d} | {r[4]:2d} | {float(r[5]):.6g} | {r[6]} | {float(r[5]/r[6]):.4f}")
