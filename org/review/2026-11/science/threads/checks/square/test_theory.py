"""Dense checks of the two structural facts used in the theorem:
 (S) symmetry: A^T = P A P and B1^T = P B1 P with P = left-right reversal of rows;
 (E) the decomposition e(n) = T1 + T2 + T3 + T4 + T5, compared with the direct machine (exact integers)."""
import sys, json, glob, numpy as np
sys.path.insert(0,'.')
from sqlib import Machine
from task4 import exact_counts
S0='../oeis/certs/'
nsym = ndec = 0
for f in sorted(glob.glob(S0 + 'A*.json')):
    c = json.load(open(f)); M = Machine(c['name'])
    if M.R > 700: continue
    P = M.row_perm()
    assert (M.A.T == M.A[np.ix_(P, P)]).all() and (M.B1.T == M.B1[np.ix_(P, P)]).all(), f
    nsym += 1
    if M.R > 60: continue
    sp = M.sp; ex = exact_counts(sp['k'], sp['q'], sp['kinds'], sp['total'], 1, 9)
    A = M.A.astype(object); B1 = M.B1.astype(object); C = M.C.astype(object); D = M.D.astype(object)
    one = np.ones(M.R, dtype=object); one1 = np.ones(M.R1, dtype=object)
    Lp = [one]; Rp = [one]
    for i in range(10): Lp.append(Lp[-1] @ A); Rp.append(A @ Rp[-1])
    dvec = one1 @ D; cvec = C @ one1
    for n in range(1, 10):
        e = 0
        if n == 1: e += M.R1
        if n >= 2:
            e += sum(Lp[p] @ B1 @ Rp[n - 2 - p] for p in range(n - 1))
            e += dvec @ Rp[n - 2] + Lp[n - 2] @ cvec
        if n >= 3: e += sum(Lp[p] @ C @ D @ Rp[n - 3 - p] for p in range(n - 2))
        assert e == ex[n - 1][1], (f, n, e, ex[n - 1][1])
    ndec += 1
print("symmetry A^T = P A P and B1^T = P B1 P holds for", nsym, "certificates (Omega0 <= 700 rows); decomposition of e(n) verified exactly for n=1..9 on", ndec)
