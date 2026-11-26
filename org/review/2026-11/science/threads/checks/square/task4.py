"""Task 4: strips counted with exactly j qualifying pairs, j = 0..3, by a direct machine (exact Python integers),
checked against brute-force enumeration of literal grids; then the minimal recurrence of each count is compared with g^(j+1)."""
import sys, itertools, json, numpy as np
from fractions import Fraction
sys.path.insert(0,'.')
from sqlib import all_rows, inside_count, cnt_matrix
from sqprove import charpoly, sqrt_form, pmul
S0='../oeis/certs/'

def exact_counts(k, q, kinds, t, J, nmax):
    rows = all_rows(k, q); w = inside_count(rows, kinds, t).astype(int)
    cnt = cnt_matrix(rows, rows, k, q, kinds, t).astype(int)
    keep = np.where(w <= J)[0]; w = w[keep]; cnt = cnt[np.ix_(keep, keep)]
    Tc = [(cnt == c).astype(object) for c in range(J + 1)]
    X = [np.array([1 if w[i] == c else 0 for i in range(len(keep))], dtype=object) for c in range(J + 1)]
    out = [[sum(X[j]) for j in range(J + 1)]]
    for n in range(2, nmax + 1):
        Y = [sum((X[c] @ Tc[m] for c in range(J + 1) if c + m == cc), np.zeros(len(keep), dtype=object)) for cc in range(J + 1) for m in [None]] if False else None
        newX = [np.zeros(len(keep), dtype=object) for _ in range(J + 1)]
        for c in range(J + 1):
            for m in range(J + 1 - c):
                Z = X[c] @ Tc[m]                      # pairs created between rows
                for i in range(len(keep)):
                    cc = c + m + w[i]
                    if cc <= J: newX[cc][i] += Z[i]
        X = newX; out.append([sum(X[j]) for j in range(J + 1)])
    return out   # out[n-1][j] = count with n rows and exactly j pairs

def brute(n, k, q, kinds, t):
    dirs = {'H': (0, 1), 'V': (1, 0), 'D': (1, 1), 'A': (1, -1)}
    res = {}
    for cells in itertools.product(range(q), repeat=n * k):
        g = [cells[i * k:(i + 1) * k] for i in range(n)]
        c = 0
        for i in range(n):
            for j in range(k):
                for kd in kinds:
                    di, dj = dirs[kd]; ii, jj = i + di, j + dj
                    if 0 <= ii < n and 0 <= jj < k and g[i][j] + g[ii][jj] == t: c += 1
        res[c] = res.get(c, 0) + 1
    return res

def bm(seq):
    """Berlekamp-Massey over Q: minimal c with seq[n] = sum c_i seq[n-i]"""
    s = [Fraction(x) for x in seq]; C = [Fraction(1)]; B = [Fraction(1)]; L = 0; m = 1; b = Fraction(1)
    for n in range(len(s)):
        d = s[n] + sum(C[i] * s[n - i] for i in range(1, L + 1))
        if d == 0: m += 1; continue
        T = C[:]; coef = d / b
        C = C + [Fraction(0)] * (len(B) + m - len(C))
        for i in range(len(B)): C[i + m] -= coef * B[i]
        if 2 * L <= n: L = n + 1 - L; B = T; b = d; m = 1
        else: m += 1
    return L, [-C[i] for i in range(1, L + 1)]

if __name__ == '__main__':
    from flint import fmpz_poly
    # brute-force check of the machine
    for (k, q, kinds, t, nmax) in [(2, 3, {'H','V'}, 2, 5), (3, 2, {'H','V','D'}, 1, 4), (2, 3, {'V','A'}, 2, 5), (3, 3, {'H','A'}, 3, 3)]:
        ex = exact_counts(k, q, kinds, t, 3, nmax)
        for n in range(1, nmax + 1):
            b = brute(n, k, q, kinds, t)
            if not all(ex[n - 1][j] == b.get(j, 0) for j in range(4)): raise SystemExit("machine != brute force: %r" % ((k, q, kinds, t, n),))
    print("machine == brute force for 4 specs, all n up to the listed sizes, j = 0..3")
    # law check
    specs = []
    import glob, os
    for f in sorted(glob.glob(S0 + 'A*.json')):
        c = json.load(open(f)); sp = c['spec']
        if len(c['recurrence']['coefficients']) <= 8 and sp['mode'] == 'exact' and sp['orient'] == 'nxk':
            specs.append((c['oeis_id'], c['name'], c['recurrence']['coefficients']))
    from sqlib import parse
    for aid, name, co in specs[:12]:
        sp = parse(name); k, q, kinds, t = sp['k'], sp['q'], sp['kinds'], sp['total']
        if q ** k > 100: continue
        g, extra = sqrt_form(charpoly(co)); G = fmpz_poly(g)
        nmax = 36; ex = exact_counts(k, q, kinds, t, 3, nmax)
        line = [aid, name[:70], 'g=%s' % G]
        for j in range(0, 4):
            seq = [ex[n][j] for n in range(8, nmax)]            # tail from n=9: drop the initial transient
            L, cs = bm(seq)
            if 2 * L >= len(seq) - 1: line.append('j=%d: order %d (too long to decide)' % (j, L)); continue
            poly = fmpz_poly([int(-cs[L - 1 - i]) if cs[L-1-i].denominator == 1 else 0 for i in range(L)] + [1])
            ok = all(c.denominator == 1 for c in cs)
            # strip the x factors (they only encode the start)
            cst, fac = poly.factor(); fac = [(f, m) for f, m in fac if str(f) != 'x']
            target = [(f, m * (j + 1)) for f, m in G.factor()[1] if str(f) != 'x']
            if extra: target = None
            line.append('j=%d: %s %s' % (j, [(str(f), m) for f, m in fac], 'OK' if ok and fac == target else ('(exception family)' if extra else 'DIFFERENT')))
        print(' | '.join(map(str, line)))
