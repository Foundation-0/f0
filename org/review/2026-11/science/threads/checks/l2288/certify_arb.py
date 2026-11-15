"""Second, separately coded check of a certify.py certificate: interval Krawczyk test in arb ball arithmetic.
Shares no code with certify.py.  For each centre c and box X = c + [-r, r]^m:
  K(X) = c - Y F(c) + (I - Y J(X)) (X - c),  J(X) = interval Jacobian over X,  Y = float inverse of J(c).
If K(X) lies strictly inside X, X contains exactly one zero of F and J is nonsingular on X (Krawczyk).
Boxes are also checked pairwise disjoint.  Usage: python -I certify_arb.py cert.json"""
import json, sys, itertools
import numpy as np
from flint import arb, fmpq, ctx

ctx.prec = 256


def fail(m):
    print("FAIL:", m); raise SystemExit(1)


d = json.load(open(sys.argv[1]))
E = [tuple(e) for e in d["edges"]]; n = d["num_vertices"]
pairs = list(itertools.combinations(range(1, n + 1), 2)); es = set(map(frozenset, E))
code = sum(1 << (len(pairs) - 1 - i) for i, pp in enumerate(pairs) if frozenset(pp) in es)
if code != 18120782205838348:
    fail("graph is not L2288 (code %d)" % code)


def q(sv):
    a, _, b = sv.partition("/")
    return fmpq(int(a), int(b) if b else 1)


s = [q(x) for x in d["sq_lengths"]]
pin = {int(k): (q(v[0]), q(v[1])) for k, v in d["pinned"].items()}
free = d["free_vertices"]; ix = {v: i for i, v in enumerate(free)}
for i, (a, b) in enumerate(E):
    if a in pin and b in pin and (pin[a][0] - pin[b][0]) ** 2 + (pin[a][1] - pin[b][1]) ** 2 != s[i]:
        fail("pinned edge length")
A_, B_, C_ = d["triangle"]
if not (pin[A_] == (0, 0) and pin[B_][1] == 0 and pin[B_][0] > 0 and pin[C_][1] > 0):
    fail("frame")
rows = [i for i, (a, b) in enumerate(E) if not (a in pin and b in pin)]
m = len(rows)
if m != 2 * len(free) or sorted(free + list(pin)) != list(range(1, n + 1)):
    fail("counts")
SC = 2 ** d["center_scale_exp2"]
r = arb(fmpq(1, 2 ** d["box_radius_exp2"]))
rad = arb(0, fmpq(1, 2 ** d["box_radius_exp2"]))  # the ball [-r, r]


def coord(z, v, k):
    return arb(pin[v][k]) if v in pin else z[2 * ix[v] + k]


worst = 0.0
for bi, cint in enumerate(d["centers"]):
    c = [arb(fmpq(x, SC)) for x in cint]
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
            mij = arb(1 if i == j else 0) - sum((Y[i][k] * JX[k][j] for k in range(m)), arb(0))
            acc += mij * rad
        Ki = -YF + acc  # K_i - c_i
        bound = abs(Ki).upper()
        if not bound < r:
            fail(f"box {bi} row {i}: Krawczyk image not inside box")
        worst = max(worst, float(bound / r))
print(f"{len(d['centers'])} boxes pass the interval Krawczyk test (worst |K - c| / r = {worst:.3e})")
C = d["centers"]; two_r = 2 * SC // 2 ** d["box_radius_exp2"]
for i in range(len(C)):
    for j in range(i + 1, len(C)):
        if max(abs(x - y) for x, y in zip(C[i], C[j])) <= two_r:
            fail(f"boxes {i}, {j} overlap")
print(f"boxes pairwise disjoint; RESULT: {len(C)} real solutions with v{C_} above the axis, {2*len(C)} with mirrors")
