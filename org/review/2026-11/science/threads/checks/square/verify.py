"""Stand-alone verifier for the square-law certificates (own format).  Usage: python verify.py cert.json [more.json ...]
Re-derives from the OEIS name and the coefficients: the square root of the characteristic polynomial, the machine,
g(A)1 and 1^T g(A) (times A^s) modulo the listed primes, the proved bounds, the theorem index N, the exact counts a(n)
for n <= N (CRT of residues), the recurrence residuals, and the data terms.  Every failed check raises Reject:
no bare assert, so `python -O` behaves identically.
Backends: 'dense' = own matrices built by broadcasting (independent of the prover's engine);
          'tensor' = the prover's matrix-free engine (sqlib.contract), used only when the dense matrices do not fit."""
import sys, json, re, time, os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
import numpy as np

class Reject(Exception): pass
def need(cond, msg):
    if not cond: raise Reject(msg)

# ------------------------------------------------------------------ name parser (own copy)
WORDS = {"zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10}
def parse_name(name):
    name = re.sub(r"\s+", " ", name.replace("_", " ").strip())
    m = re.match(r"Number of (n|\d+) ?X ?(n|\d+) (binary|0\.\.(\d+)) arrays with some element plus some (.+?) adjacent neighbor totalling (\w+) (no more than once|not more than once|exactly once)\.?$", name)
    need(m, "name does not parse")
    a, b, alpha, top, nb, tot, mode = m.groups()
    q = 2 if alpha == "binary" else int(top) + 1
    kinds = set()
    for w in re.split(r"[ ,]+", nb.replace(" or ", " ")):
        if w == "horizontally": kinds.add("H")
        elif w == "vertically": kinds.add("V")
        elif w == "diagonally": kinds.add("D")
        elif w == "antidiagonally": kinds.add("A")
        elif w: raise Reject("unknown direction word " + w)
    need(kinds and tot in WORDS and (a == "n") != (b == "n"), "shape not a strip")
    if a == "n": k = int(b)                       # n rows of width k
    else:
        k = int(a); kinds = {{"H": "V", "V": "H"}.get(x, x) for x in kinds}   # transpose
    return k, q, kinds, WORDS[tot], mode == "exactly once"

# ------------------------------------------------------------------ integer helpers
def is_prime(n):
    if n < 2: return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0: return n == p
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in (2, 3, 5, 7, 11, 13, 17):
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else: return False
    return True
def pmul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b): r[i + j] += x * y
    return r
def sqrt_poly(P):
    n = len(P) - 1
    if n % 2 or P[n] != 1: return None
    d = n // 2; g = [0] * (d + 1); g[d] = 1
    for i in range(1, d + 1):
        s = P[2 * d - i] - sum(g[d - a] * g[d - i + a] for a in range(1, i))
        if s % 2: return None
        g[d - i] = s // 2
    return g if pmul(g, g) == P else None
def divide_x_plus_1(P):
    n = len(P) - 1; q = [0] * n; acc = 0
    for i in range(n, 0, -1):
        acc = P[i] - acc; q[i - 1] = acc
    return q, P[0] - acc
def crt(res, ps):
    x, m = 0, 1
    for r, p in zip(res, ps):
        x += m * ((int(r) - x) * pow(m, -1, p) % p); m *= p
    return x, m

# ------------------------------------------------------------------ the machine
def rows_of(k, q):
    idx = np.arange(q ** k, dtype=np.int64)
    return np.stack([(idx // q ** (k - 1 - j)) % q for j in range(k)], axis=1)
def inside(rows, kinds, t):
    if "H" not in kinds: return np.zeros(len(rows), dtype=np.int64)
    return ((rows[:, :-1] + rows[:, 1:]) == t).sum(axis=1).astype(np.int64)
def pair_cols(k, kinds):
    out = []
    for j in range(k):
        if "V" in kinds: out.append((j, j))
        if "D" in kinds and j + 1 < k: out.append((j, j + 1))
        if "A" in kinds and j >= 1: out.append((j, j - 1))
    return out
def cnt_dense(up, down, k, kinds, t, chunk=512):
    pc = pair_cols(k, kinds)
    out = np.zeros((len(up), len(down)), dtype=np.int8)
    for i in range(0, len(up), chunk):
        blk = up[i:i + chunk]
        for j, jj in pc:
            out[i:i + chunk] += ((blk[:, j][:, None] + down[:, jj][None, :]) == t)
    return out

class Dense:
    """Omega = rows with at most one inside pair, kept in order: Omega0 first, then Omega1."""
    name = "dense"
    def __init__(self, k, q, kinds, t):
        rows = rows_of(k, q); w = inside(rows, kinds, t)
        self.rows0, self.rows1 = rows[w == 0], rows[w == 1]
        self.R, self.R1 = len(self.rows0), len(self.rows1)
        om = np.concatenate([self.rows0, self.rows1]); self.wO = np.concatenate([np.zeros(self.R, np.int64), np.ones(self.R1, np.int64)])
        cnt = cnt_dense(om, om, k, kinds, t)
        self.T0 = (cnt == 0).astype(np.int8); self.T1 = (cnt == 1).astype(np.int8)
        self.nOm = self.R + self.R1
        self.rho_T = int(((cnt <= 1).sum(axis=1)).max())
        A = self.T0[:self.R, :self.R]
        self.rho_rows = int(A.sum(axis=1, dtype=np.int64).max()); self.rho_cols = int(A.sum(axis=0, dtype=np.int64).max())
        self.A = A
    @staticmethod
    def mm(M, V, transpose=False):
        """exact integer product of a 0/1 int8 matrix with a (rows x B) int64 matrix of entries < 2^31 via float64:
        every product is an integer < 2^31 and every partial sum is < n*2^31 <= 2^53 (n <= 2^22), hence exact."""
        n = M.shape[1] if not transpose else M.shape[0]
        if n >= 2 ** 22: raise Reject("dimension too large for exact float64 sums")
        Vf = V.astype(np.float64); out = []
        if not transpose:
            for i in range(0, M.shape[0], 1024): out.append(M[i:i + 1024].astype(np.float64) @ Vf)
            return np.rint(np.concatenate(out)).astype(np.int64)
        acc = np.zeros((M.shape[1], V.shape[1]), dtype=np.float64)
        for i in range(0, M.shape[0], 1024): acc += M[i:i + 1024].astype(np.float64).T @ Vf[i:i + 1024]
        return np.rint(acc).astype(np.int64)
    def A_right(self, V, p): return self.mm(self.A, V) % p
    def A_left(self, V, p): return self.mm(self.A, V, True) % p
    def window_step(self, X0, X1, p):
        """X0, X1: (nOm, B) counts of arrays ending in each row with 0 / 1 pairs; returns next state."""
        w = self.wO[:, None]
        Y0 = self.mm(self.T0, X0, True) % p                         # arrays extended by a row, 0 pairs so far
        Y1 = (self.mm(self.T0, X1, True) + self.mm(self.T1, X0, True)) % p
        # a new row with w inside pairs shifts the count by w
        Z0 = Y0 * (w == 0)
        Z1 = Y1 * (w == 0) + Y0 * (w == 1)
        return Z0 % p, Z1 % p

class Tensor:
    name = "tensor"
    def __init__(self, k, q, kinds, t):
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import sqlib
        self.sq = sqlib; self.k, self.q, self.kinds, self.t = k, q, kinds, t
        rows = rows_of(k, q); self.w = inside(rows, kinds, t); self.N = len(rows)
        self.m0 = (self.w == 0).astype(np.int64)
        self.R = int(self.m0.sum()); self.R1 = int((self.w == 1).sum()); self.nOm = self.R + self.R1
        self.oR, self.oL = sqlib.offsets_right(kinds), sqlib.offsets_left(kinds)
        one = self.m0.reshape(1, 1, -1)
        self.rho_rows = int((sqlib.contract(one, self.oR, q, k, t, 0) * self.m0).max())
        self.rho_cols = int((sqlib.contract(one, self.oL, q, k, t, 0) * self.m0).max())
        ind = (self.w <= 1).astype(np.int64); v = np.zeros((1, 2, self.N), dtype=np.int64); v[0, 0] = ind
        y = sqlib.contract(v, self.oR, q, k, t, 1)[0]
        self.rho_T = int(((y[0] + y[1]) * ind).max())
    def A_right(self, V, p):      # V: (N, B)
        r = self.sq.contract((V * self.m0[:, None]).T[:, None, :].copy(), self.oR, self.q, self.k, self.t, 0)[:, 0, :].T
        return r % p * self.m0[:, None]
    def A_left(self, V, p):
        r = self.sq.contract((V * self.m0[:, None]).T[:, None, :].copy(), self.oL, self.q, self.k, self.t, 0)[:, 0, :].T
        return r % p * self.m0[:, None]

def make_machine(k, q, kinds, t):
    om = None
    # dense matrices are int8 (nOm^2 bytes each, two of them): use them up to 20000 rows in Omega
    rows = rows_of(k, q); w = inside(rows, kinds, t)
    nOm = int((w <= 1).sum())
    if nOm <= 20000: return Dense(k, q, kinds, t)
    return Tensor(k, q, kinds, t)

# ------------------------------------------------------------------ the checks
def horner(M, gc, ps, side):
    p = np.array(ps, dtype=np.int64).reshape(1, -1)
    if isinstance(M, Dense): one = np.ones((M.R, 1), dtype=np.int64)
    else: one = M.m0.reshape(-1, 1)
    acc = np.repeat(one, len(ps), axis=1)
    ap = M.A_right if side == "R" else M.A_left
    for i in range(len(gc) - 2, -1, -1):
        gi = np.array([gc[i] % pp for pp in ps], dtype=np.int64).reshape(1, -1)
        acc = (ap(acc, p) + gi * one) % p
    return acc

def verify(cert):
    t0 = time.time()
    need(cert.get("format") == "square-law-cert/1", "bad format tag")
    name, co, data = cert["name"], cert["coefficients"], cert["data_terms"]
    need(all(isinstance(c, int) for c in co) and len(co) >= 1, "bad coefficients")
    k, q, kinds, t, exact = parse_name(name)
    D_P = len(co)
    P = [-co[D_P - 1 - i] for i in range(D_P)] + [1]
    g = sqrt_poly(P); extra = 0
    if g is None:
        Q, rem = divide_x_plus_1(P)
        need(rem == 0, "characteristic polynomial is not a square or a square times (x+1)")
        g = sqrt_poly(Q); extra = 1
        need(g is not None, "characteristic polynomial is not a square or a square times (x+1)")
    need(g == cert["sqrt_poly"] and extra == cert["extra_x_plus_1"], "sqrt polynomial differs from the certificate")
    gc = g if not extra else pmul(g, [1, 1])
    M = make_machine(k, q, kinds, t)
    need(M.R == cert["omega0"] and M.R1 == cert["omega1"], "row counts differ")
    rho = max(M.rho_rows, M.rho_cols)
    need(M.rho_rows == cert["rho_rows"] and M.rho_cols == cert["rho_cols"], "row/column sums differ")
    s = cert["nilpotency_s"]; need(isinstance(s, int) and s >= 0, "bad s")
    # --- hypothesis: A^s g(A) 1 = 0 and 1^T g(A) A^s = 0, exactly, via primes
    bound = sum(abs(c) * rho ** (i + s) for i, c in enumerate(gc))
    ph = cert["primes_hypothesis"]
    need(len(set(ph)) == len(ph) and all(isinstance(p, int) and 2 ** 30 < p < 2 ** 31 and is_prime(p) for p in ph), "hypothesis primes invalid")
    prod = 1
    for p in ph: prod *= p
    need(prod > 2 * bound, "hypothesis primes too few for the proved bound")
    pr = np.array(ph, dtype=np.int64).reshape(1, -1)
    for side in "RL":
        v = horner(M, gc, ph, side); ap = M.A_right if side == "R" else M.A_left
        for _ in range(s): v = ap(v, pr)
        need(not v.any(), "g(A)1 is not annihilated (side %s)" % side)
    # --- index of the theorem
    D = (len(gc) - 1) + s
    N = 2 * D + (2 if M.R1 else 1)
    need(N == cert["theorem_index"], "theorem index differs")
    # --- window
    amax = M.nOm * M.rho_T ** (N - 1)
    rb = (1 + sum(abs(c) for c in co)) * amax
    pw = cert["primes_window"]
    need(len(set(pw)) == len(pw) and all(isinstance(p, int) and 2 ** 30 < p < 2 ** 31 and is_prime(p) for p in pw), "window primes invalid")
    prod = 1
    for p in pw: prod *= p
    need(prod > 2 * rb, "window primes too few for the proved bound")
    seq = window_values(M, k, q, kinds, t, exact, pw, N)
    for n, x in enumerate(seq, 1):
        need(0 <= x <= amax, "count outside its proved range at n=%d" % n)
    for i, x in enumerate(data[:N]):
        need(seq[i] == x, "OEIS data term %d differs from the machine" % (i + 1))
    start = cert["start"]
    need(isinstance(start, int) and D_P + 1 <= start <= N, "start out of range")
    def resid(n): return seq[n - 1] - sum(c * seq[n - 1 - i] for i, c in enumerate(co, 1))
    for n in range(start, N + 1): need(resid(n) == 0, "recurrence fails at n=%d" % n)
    need(start == D_P + 1 or resid(start - 1) != 0, "start is not minimal (recurrence also holds at start-1)")
    if extra: need(N - 1 >= D_P + 1, "too early for the (x+1) argument")   # resid(N) = 0 was just checked; r(n) = -r(n-1) for n >= N
    return dict(ok=True, start=start, N=N, D=D, s=s, backend=M.name, seconds=round(time.time() - t0, 2), primes=(len(ph), len(pw)),
                note=("recurrence m^2 proved from N; P = m^2/(x+1) follows from one vanishing residual (see NOTES)" if extra else "recurrence proved for all n >= start"))

def window_values(M, k, q, kinds, t, exact, pw, N):
    p = np.array(pw, dtype=np.int64).reshape(1, -1); B = len(pw)
    if isinstance(M, Dense):
        X0 = np.repeat((M.wO == 0).astype(np.int64)[:, None], B, 1); X1 = np.repeat((M.wO == 1).astype(np.int64)[:, None], B, 1)
        vals = []
        for n in range(1, N + 1):
            tot = (X1.sum(axis=0) if exact else X0.sum(axis=0) + X1.sum(axis=0)) % p[0]
            vals.append(crt(tot, pw)[0])
            if n < N: X0, X1 = M.window_step(X0, X1, p)
        return vals
    sq = M.sq; w = M.w
    X = np.zeros((B, 2, M.N), dtype=np.int64); X[:, 0] = (w == 0); X[:, 1] = (w == 1)
    pp = p.reshape(B, 1, 1); vals = []
    for n in range(1, N + 1):
        tot = (X[:, 1].sum(axis=1) if exact else X[:, 0].sum(axis=1) + X[:, 1].sum(axis=1)) % p[0]
        vals.append(crt(tot, pw)[0])
        if n < N:
            Y = sq.contract(X, M.oL, q, k, t, 1)
            Z = np.zeros_like(X); Z[:, 0] = Y[:, 0] * (w == 0); Z[:, 1] = Y[:, 1] * (w == 0) + Y[:, 0] * (w == 1)
            X = Z % pp
    return vals

if __name__ == "__main__":
    bad = 0
    for fn in sys.argv[1:]:
        c = json.load(open(fn))
        try:
            r = verify(c); print("PASS", c["oeis_id"], r)
        except Reject as e:
            bad += 1; print("REJECT", c.get("oeis_id"), "-", e)
    sys.exit(1 if bad else 0)
