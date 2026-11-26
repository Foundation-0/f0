"""Numerical check (exact integers) of the lemma behind the proofs.
Setting: a(n) = u M^(n-o) v for n >= o, M an integer DxD matrix. A claimed recurrence a(n)=sum c_i a(n-i), order d, has residual
r_n = a(n) - sum c_i a(n-i) = u M^(n-o-d) p(M) v   for n >= o+d,   p(t)=t^d - c_1 t^(d-1) - ... - c_d.
Cayley-Hamilton: j -> u M^j w satisfies the order-D recurrence of chi_M, so D consecutive zeros imply all later zeros.
Tightness: D-1 consecutive zeros do not suffice."""
import random
def mm(A, B): return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
def mv(A, x): return [sum(a * b for a, b in zip(r, x)) for r in A]
def vm(u, A): return [sum(u[k] * A[k][j] for k in range(len(A))) for j in range(len(A))]
def dot(u, v): return sum(a * b for a, b in zip(u, v))
random.seed(1)
trials = 0
for _ in range(300):
    D = random.randint(2, 5); d = random.randint(1, 6); o = random.randint(0, 2)
    M = [[random.randint(-2, 3) for _ in range(D)] for _ in range(D)]
    u = [random.randint(-3, 3) for _ in range(D)]; v = [random.randint(-3, 3) for _ in range(D)]
    c = [random.randint(-3, 3) for _ in range(d)]
    N = o + d + 3 * D + 12
    vecs = [v]
    for _ in range(N): vecs.append(mv(M, vecs[-1]))
    a = {o + j: dot(u, vecs[j]) for j in range(N)}
    # residual formula
    z = [vecs[d][i] - sum(c[l - 1] * vecs[d - l][i] for l in range(1, d + 1)) for i in range(D)]
    r = {}
    for n in range(o + d, o + N - d):
        r[n] = a[n] - sum(c[i - 1] * a[n - i] for i in range(1, d + 1))
        if r[n] != dot(u, z): raise SystemExit('residual formula failed')
        z = mv(M, z)
    # window lemma: wherever D consecutive residuals vanish, all later ones vanish
    ns = sorted(r)
    for i in range(len(ns) - D):
        if all(r[ns[i + k]] == 0 for k in range(D)) and any(r[m] for m in ns[i + D:]): raise SystemExit('window lemma failed')
    trials += 1
print('residual formula and D-window lemma verified on', trials, 'random integer systems')
# tightness: M = cyclic shift of order 3, w = e0, u = e2 : r_j = 1 iff j = 2 (mod 3); two zeros then a one
M = [[0, 0, 1], [1, 0, 0], [0, 1, 0]]; w = [1, 0, 0]; u = [0, 0, 1]; seq = []
for j in range(9):
    seq.append(dot(u, w)); w = mv(M, w)
print('tightness example (D=3):', seq, '-> D-1=2 consecutive zeros are not enough')
