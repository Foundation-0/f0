"""Second, separately coded check of a certify12.py certificate (edge-pinned frame): interval Krawczyk test in
arb ball arithmetic.  Shares no code with certify12.py.  For each centre c and box X = c + [-r, r]^m:
  K(X) = c - Y F(c) + (I - Y J(X)) (X - c),  J(X) the interval Jacobian over X,  Y a float inverse of J(c).
K(X) strictly inside X proves exactly one zero of F in X and J nonsingular on X.  Boxes are checked pairwise
disjoint with a sort-and-sweep on one coordinate (exact integers).
Usage: python -I certify12_arb.py cert.json [expected LSB code of this labelling]"""
import json, sys, itertools
import numpy as np
from flint import arb, fmpq, ctx

ctx.prec = 256


def fail(m):
    print("FAIL:", m); raise SystemExit(1)


def q(sv):
    a, _, b = sv.partition("/")
    return fmpq(int(a), int(b) if b else 1)


d = json.load(open(sys.argv[1]))
E = [tuple(e) for e in d["edges"]]; n = d["num_vertices"]
for k in range(2, n + 1):
    for S_ in itertools.combinations(range(1, n + 1), k):
        st = set(S_)
        if sum(1 for u, v in E if u in st and v in st) > 2 * k - 3:
            fail("not Laman")
if len(E) != 2 * n - 3:
    fail("edge count")
lsb = 0
for u, v in E:
    a, b = sorted((u - 1, v - 1)); lsb |= 1 << (b * (b - 1) // 2 + a)
if len(sys.argv) > 2 and lsb != int(sys.argv[2]):
    fail(f"LSB code {lsb} is not the expected one")
s = [q(x) for x in d["sq_lengths"]]
pin = {int(k): (q(v[0]), q(v[1])) for k, v in d["pinned"].items()}
free = d["free_vertices"]; ix = {v: i for i, v in enumerate(free)}
A_, B_ = d["triangle"][:2]
if len(pin) != 2 or not (pin[A_] == (0, 0) and pin[B_][1] == 0 and pin[B_][0] > 0):
    fail("frame")
pe = [i for i, (a, b) in enumerate(E) if a in pin and b in pin]
if len(pe) != 1 or pin[B_][0] ** 2 != s[pe[0]]:
    fail("pinned edge")
if any(not x > 0 for x in s):
    fail("squared length")
rows = [i for i in range(len(E)) if i != pe[0]]
m = len(rows)
if m != 2 * len(free) or sorted(free + list(pin)) != list(range(1, n + 1)):
    fail("counts")
SC = 2 ** d["center_scale_exp2"]
r = arb(fmpq(1, 2 ** d["box_radius_exp2"]))
rad = arb(0, fmpq(1, 2 ** d["box_radius_exp2"]))


def coord(z, v, k):
    return arb(pin[v][k]) if v in pin else z[2 * ix[v] + k]


worst = 0.0
for bi, cint in enumerate(d["centers"]):
    c = [arb(fmpq(int(x), SC)) for x in cint]
    X = [ci + rad for ci in c]
    Fc = []; Jc = np.zeros((m, m)); JX = [[arb(0)] * m for _ in range(m)]
    for row, ei in enumerate(rows):
        a, b = E[ei]
        dx = coord(c, a, 0) - coord(c, b, 0); dy = coord(c, a, 1) - coord(c, b, 1)
        Fc.append(dx * dx + dy * dy - arb(s[ei]))
        Dx = coord(X, a, 0) - coord(X, b, 0); Dy = coord(X, a, 1) - coord(X, b, 1)
        for v, sg in ((a, 1), (b, -1)):
            if v in ix:
                JX[row][2 * ix[v]] = 2 * sg * Dx; JX[row][2 * ix[v] + 1] = 2 * sg * Dy
                Jc[row, 2 * ix[v]] = 2 * sg * float(dx.mid()); Jc[row, 2 * ix[v] + 1] = 2 * sg * float(dy.mid())
    Yf = np.linalg.inv(Jc)
    Y = [[arb(float(Yf[i, j])) for j in range(m)] for i in range(m)]
    for i in range(m):
        YF = sum((Y[i][k] * Fc[k] for k in range(m)), arb(0))
        acc = arb(0)
        for j in range(m):
            acc += (arb(1 if i == j else 0) - sum((Y[i][k] * JX[k][j] for k in range(m)), arb(0))) * rad
        bound = abs(acc - YF).upper()
        if not bound < r:
            fail(f"box {bi} row {i}: Krawczyk image not inside box")
        worst = max(worst, float(bound / r))
print(f"{len(d['centers'])} boxes pass the interval Krawczyk test (worst |K - c| / r = {worst:.3e}); graph LSB code {lsb}")
C = [[int(x) for x in c] for c in d["centers"]]
two_r = 2 * SC // 2 ** d["box_radius_exp2"]
order = sorted(range(len(C)), key=lambda i: C[i][0])
for a in range(len(order)):
    for b in range(a + 1, len(order)):
        i, j = order[a], order[b]
        if C[j][0] - C[i][0] > two_r:
            break
        if max(abs(x - y) for x, y in zip(C[i], C[j])) <= two_r:
            fail(f"boxes {i}, {j} overlap")
print(f"boxes pairwise disjoint; RESULT: {len(C)} real realizations modulo direct isometries")
