"""Exact verifier for Delsarte certificates (same conditions as work/delsarte_independent.py; Krawtchouk by the
three-term recurrence, Fractions only, failures raise SystemExit, no bare assert).
Usage: python3 -I -O verify_certs.py cert.json [more.json ...]
"""
import json, sys
from fractions import Fraction

def kraw_table(q, n, jmax):
    K = [[1] * (n + 1), [n * (q - 1) - q * x for x in range(n + 1)]]
    for j in range(1, jmax):
        row = []
        for x in range(n + 1):
            num = ((n - j) * (q - 1) + j - q * x) * K[j][x] - (q - 1) * (n - j + 1) * K[j - 1][x]
            if num % (j + 1):
                raise SystemExit("non-integer Krawtchouk value")
            row.append(num // (j + 1))
        K.append(row)
    return K

def check(c):
    q, n, k, d = c["q"], c["n"], c["k"], c["excluded_distance"]
    a = [Fraction(v) for v in c["krawtchouk_coefficients"]]
    if len(a) > n + 1: raise SystemExit("too many coefficients")
    if not a[0] > 0 or any(v < 0 for v in a[1:]): raise SystemExit(f"{c['id']}: sign condition fails")
    if not (1 <= d <= n): raise SystemExit("bad d")
    K = kraw_table(q, n, max(2, len(a)))
    f = lambda x: sum(a[j] * K[j][x] for j in range(len(a)))
    if max(f(i) for i in range(d, n + 1)) > 0: raise SystemExit(f"{c['id']}: f positive on [d,n]")
    bound = f(0) / a[0]
    if bound != Fraction(c["size_bound"]): raise SystemExit(f"{c['id']}: size_bound differs from f(0)/a_0")
    if not bound < q ** k: raise SystemExit(f"{c['id']}: bound not below q^k")
    return bound

if __name__ == "__main__":
    tot = 0
    for p in sys.argv[1:]:
        for c in json.load(open(p))["certificates"]:
            check(c); tot += 1
    print(f"{tot} certificates pass the exact check")
