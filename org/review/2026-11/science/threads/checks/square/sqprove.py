"""Cheap proof of an OEIS 'square law' recurrence from the name and the coefficients alone.
Own code; uses sqlib (own parser reused from the reviewer's spot_proof_lib, own tensor engine)."""
import time, numpy as np
from sqlib import parse, all_rows, inside_count, contract, offsets_left, offsets_right

# ---------------------------------------------------------------- number theory helpers
def is_prime(n):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13):
        if n % p == 0: return n == p
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2, 3, 5, 7):                       # deterministic for n < 3,215,031,751
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True
def primes_below(top, count):
    out, n = [], top
    while len(out) < count:
        n -= 1
        if is_prime(n): out.append(n)
    return out
def crt(res, ps):
    x, m = 0, 1
    for r, p in zip(res, ps):
        t = ((int(r) - x) * pow(m, -1, p)) % p
        x += m * t; m *= p
    return x, m

# ---------------------------------------------------------------- polynomials (low-to-high int lists)
def pmul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b): r[i + j] += x * y
    return r
def charpoly(c):                       # x^d - c1 x^(d-1) - ... - cd
    d = len(c); return [-c[d - 1 - i] for i in range(d)] + [1]
def pdivlin(P, r):                     # exact division of P by (x - r); returns (quotient, remainder)
    n = len(P) - 1; q = [0] * n; acc = 0
    for i in range(n, 0, -1):
        acc = P[i] + acc * r; q[i - 1] = acc
    return q, P[0] + acc * r
def psqrt(P):
    """integer monic square root g with g*g == P, or None"""
    n = len(P) - 1
    if n % 2 or P[n] != 1: return None
    d = n // 2; g = [0] * (d + 1); g[d] = 1
    for i in range(1, d + 1):
        s = P[2 * d - i] - sum(g[d - a] * g[d - i + a] for a in range(1, i))
        if s % 2: return None
        g[d - i] = s // 2
    return g if pmul(g, g) == P else None
def sqrt_form(P):
    """(g, extra) with P = g^2 * (x+1)^extra, extra in {0,1}, or None"""
    g = psqrt(P)
    if g is not None: return g, 0
    Q, rem = pdivlin(P, -1)
    if rem == 0:
        g = psqrt(Q)
        if g is not None: return g, 1
    return None

# ---------------------------------------------------------------- the machine (matrix free)
class Strip:
    def __init__(self, name):
        sp = parse(name)
        if sp is None: raise ValueError("name not parsed")
        self.sp = sp; self.k, self.q, self.t, self.kinds = sp["k"], sp["q"], sp["total"], sp["kinds"]
        rows = all_rows(self.k, self.q)
        self.w = inside_count(rows, self.kinds, self.t).astype(np.int64)      # pairs inside the row
        self.N = len(rows)
        self.m0 = (self.w == 0).astype(np.int64); self.m1 = (self.w == 1).astype(np.int64)
        self.R, self.R1 = int(self.m0.sum()), int(self.m1.sum())
        self.oR, self.oL = offsets_right(self.kinds), offsets_left(self.kinds)
    # operators on Omega0 (vectors live on all rows, zero off Omega0)
    def A_right(self, v, p):          # (A v)[a] = sum_b A[a][b] v[b]
        return contract(v * self.m0, self.oR, self.q, self.k, self.t, 0) % p * self.m0
    def A_left(self, v, p):           # (A^T u)[b] = sum_a u[a] A[a][b]
        return contract(v * self.m0, self.oL, self.q, self.k, self.t, 0) % p * self.m0
    def row_col_max(self):
        """exact max row sum and max column sum of A (no reduction)"""
        one = self.m0.reshape(1, 1, -1)
        big = np.int64(1) << 62
        r = contract(one, self.oR, self.q, self.k, self.t, 0) * self.m0
        c = contract(one, self.oL, self.q, self.k, self.t, 0) * self.m0
        return int(r.max()), int(c.max())
    def rho_T(self):
        """max over rows a (<=1 pair inside) of #{b (<=1 inside): pairs(a,b) <= 1}"""
        ind = (self.w <= 1).astype(np.int64)
        v = np.zeros((1, 2, self.N), dtype=np.int64); v[0, 0] = ind
        y = contract(v, self.oR, self.q, self.k, self.t, 1)[0]
        return int(((y[0] + y[1]) * ind).max()), int(ind.sum())
    def window(self, ps, Nmax):
        """a(n) mod each prime for n = 1..Nmax, exact and at-most counts: returns two lists of int64 arrays (B,)"""
        p = np.array(ps, dtype=np.int64).reshape(-1, 1, 1); B = len(ps)
        w = self.w
        X = np.zeros((B, 2, self.N), dtype=np.int64)
        X[:, 0] = (w == 0); X[:, 1] = (w == 1)
        ex, am = [], []
        for n in range(1, Nmax + 1):
            ex.append(X[:, 1].sum(axis=1) % p[:, 0, 0]); am.append((X[:, 0].sum(axis=1) + X[:, 1].sum(axis=1)) % p[:, 0, 0])
            if n == Nmax: break
            Y = contract(X, self.oL, self.q, self.k, self.t, 1)
            Z = np.zeros_like(X)
            Z[:, 0] = Y[:, 0] * (w == 0)
            Z[:, 1] = Y[:, 1] * (w == 0) + Y[:, 0] * (w == 1)
            X = Z % p
        return ex, am

def horner_g(S, gc, ps, side):
    """g(A) 1 (side 'R') or 1^T g(A) (side 'L') modulo each prime, Horner's rule. gc low-to-high, monic."""
    p = np.array(ps, dtype=np.int64).reshape(-1, 1, 1)
    one = S.m0.reshape(1, 1, -1)
    ap = S.A_right if side == 'R' else S.A_left
    d = len(gc) - 1
    acc = np.broadcast_to(one * 1, (len(ps), 1, S.N)).copy()          # leading coefficient 1
    for i in range(d - 1, -1, -1):
        gi = np.array([gc[i] % pp for pp in ps], dtype=np.int64).reshape(-1, 1, 1)
        acc = (ap(acc, p) + gi * one) % p
    return acc

def is_zero(v): return not v.any()

def bound_poly(gc, rho, s):
    return sum(abs(c) * rho ** (i + s) for i, c in enumerate(gc))

def nprimes_for(bound, pool_top=2**31):
    need = 2 * bound + 1; m, n = 1, 0
    ps = []
    for p in primes_below(pool_top, 400):
        ps.append(p); m *= p
        if m > need: return ps
    raise RuntimeError("not enough primes")

def prove(name, coeffs, data=None, log=print):
    """Full cheap proof. Returns a certificate dict (own format)."""
    t0 = time.time()
    P = charpoly(coeffs); Dp = len(coeffs)
    sf = sqrt_form(P)
    if sf is None: return dict(status="not a square (or square times x+1)", poly=P)
    g, extra = sf
    gc = g if extra == 0 else pmul(g, [1, 1])          # annihilating polynomial, (x+1) factor for the two exceptions
    d = len(gc) - 1
    S = Strip(name)
    rhoR, rhoC = S.row_col_max(); rho = max(rhoR, rhoC)
    # --- s: smallest s with A^s g(A) 1 = 0 : heuristic on one prime, then proof with enough primes
    ps1 = primes_below(2**31, 1)
    v = horner_g(S, gc, ps1, 'R'); s = 0
    while not is_zero(v) and s < 4 * d + 200:
        v = S.A_right(v, np.array(ps1, dtype=np.int64).reshape(-1, 1, 1)); s += 1
    if not is_zero(v): return dict(status="g(A)1 not nilpotent-annihilated: hypothesis fails", poly=P)
    while True:
        ps = nprimes_for(bound_poly(gc, rho, s))
        pr = np.array(ps, dtype=np.int64).reshape(-1, 1, 1)
        res = {}
        for side in 'RL':
            v = horner_g(S, gc, ps, side); s_found = 0
            ap = S.A_right if side == 'R' else S.A_left
            while not is_zero(v) and s_found <= s:
                v = ap(v, pr); s_found += 1
            res[side] = s_found if is_zero(v) else None
        if res['R'] is not None and res['L'] is not None: break
        s += 1
    sR, sL = res['R'], res['L']
    s_used = max(sR, sL)
    D = d + s_used
    # --- index of the theorem
    Nthm = 2 * D + (2 if S.R1 else 1)
    # --- window
    rhoT, nOm = S.rho_T()
    amax = nOm * rhoT ** (Nthm - 1)
    resid_bound = (1 + sum(abs(c) for c in coeffs)) * amax
    psw = nprimes_for(resid_bound)
    ex, am = S.window(psw, Nthm)
    key = 'exact' if S.sp['exact'] else 'atmost'
    seq = []
    for n in range(Nthm):
        vals = (ex if S.sp['exact'] else am)[n]
        x, m = crt(vals, psw)
        seq.append(x)
    # modular residuals (primary) and exact residuals (CRT value is exact since 0 <= a(n) <= amax < prod/2)
    last_bad = Dp
    bad_mod = []
    for n in range(Dp + 1, Nthm + 1):
        r_exact = seq[n - 1] - sum(c * seq[n - 1 - i] for i, c in enumerate(coeffs, 1))
        if r_exact != 0: last_bad = n
    start = last_bad + 1
    matches = None
    if data is not None:
        matches = all(seq[i] == data[i] for i in range(min(len(data), len(seq))))
        ncmp = min(len(data), len(seq))
    cert = dict(status="proved", name=name, coeffs=coeffs, sqrt_poly=g, extra_x_plus_1=extra,
                annihilator=gc, nilp_s=s_used, nilp_s_right=sR, nilp_s_left=sL, deg_annihilator=D,
                rows=S.N, omega0=S.R, omega1=S.R1, rho_rows=rhoR, rho_cols=rhoC,
                hypothesis_primes=len(ps), primes_hyp=ps, primes_win=psw, hypothesis_bound_bits=bound_poly(gc, rho, s_used).bit_length(),
                theorem_index=Nthm, window_primes=len(psw), window_bound_bits=resid_bound.bit_length(),
                start=start, natural=Dp + 1, data_match=matches, data_compared=(ncmp if data is not None else 0),
                seconds=round(time.time() - t0, 2))
    return cert
