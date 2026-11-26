"""Own machine for the square-law thread. Built only from the OEIS name (parser from the reviewer's spot_proof_lib, reused).
Rows of width k over 0..q-1. Omega0 = rows with no inside pair, Omega1 = rows with exactly one inside pair.
cnt(a,b) = number of qualifying pairs created between row a (above) and row b (below)."""
import re, numpy as np
WORDS = {"zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10,"eleven":11,"twelve":12}
def parse(name):
    name = re.sub(r'\s+', ' ', name.replace('_', ' ').strip())
    m = re.match(r"Number of\s+(n|\d+)\s*X\s*(n|\d+)\s+(binary|0\.\.(\d+)) arrays with some element plus some (.+?) adjacent neighbor totalling (\w+) (no more than once|not more than once|exactly once)\.?$", name)
    if not m: return None
    a, b, alpha, top, nb, tot, mode = m.groups()
    q = 2 if alpha == "binary" else int(top) + 1
    kinds = set()
    for w in re.split(r"[ ,]+", nb.replace(" or ", " ")):
        w = w.strip()
        if w == "horizontally": kinds.add("H")
        elif w == "vertically": kinds.add("V")
        elif w == "diagonally": kinds.add("D")
        elif w == "antidiagonally": kinds.add("A")
        elif w: return None
    if a == "n": k = int(b)
    else:
        k = int(a); kinds = {{"H":"V","V":"H"}.get(x, x) for x in kinds}
    return dict(k=k, q=q, kinds=kinds, total=WORDS[tot], exact=(mode == "exactly once"))

def all_rows(k, q):
    N = q**k
    idx = np.arange(N, dtype=np.int64)
    return np.stack([(idx // q**(k-1-j)) % q for j in range(k)], axis=1).astype(np.int8)  # N x k

def inside_count(rows, kinds, t):
    if "H" not in kinds: return np.zeros(len(rows), dtype=np.int8)
    r = rows.astype(np.int16)
    return ((r[:, :-1] + r[:, 1:]) == t).sum(axis=1).astype(np.int8)

def onehot(rows, j, q):
    X = np.zeros((len(rows), q), dtype=np.float32)
    X[np.arange(len(rows)), rows[:, j]] = 1
    return X

def cnt_matrix(up, down, k, q, kinds, t):
    """cnt[a,b] for a in up rows, b in down rows (a above b), int8. Pair (a_j, b_j') with a_j+b_j'=t.
    Product U @ W^T of one-hot blocks: sum over (j,j') pairs and values v of [a_j=v][b_j'=t-v]."""
    pairs = []
    for j in range(k):
        if "V" in kinds: pairs.append((j, j))
        if "D" in kinds and j + 1 < k: pairs.append((j, j + 1))
        if "A" in kinds and j - 1 >= 0: pairs.append((j, j - 1))
    if not pairs: return np.zeros((len(up), len(down)), dtype=np.int8)
    U = np.concatenate([onehot(up, j, q) for j, jj in pairs], axis=1)
    Wb = []
    for j, jj in pairs:
        Y = onehot(down, jj, q)                    # Y[b, w] = [b_jj = w]
        Z = np.zeros_like(Y)
        for v in range(q):                          # need b_jj = t - v
            if 0 <= t - v < q: Z[:, v] = Y[:, t - v]
        Wb.append(Z)
    W = np.concatenate(Wb, axis=1)
    return np.rint(U @ W.T).astype(np.int8)       # float32 sums of <= 3k ones: exact

class Machine:
    def __init__(self, name):
        sp = parse(name)
        if sp is None: raise ValueError("unparsed name")
        self.sp = sp; k, q, t = sp["k"], sp["q"], sp["total"]
        rows = all_rows(k, q); ins = inside_count(rows, sp["kinds"], t)
        self.rows0 = rows[ins == 0]; self.rows1 = rows[ins == 1]; self.nbig = int((ins >= 2).sum())
        self.R = len(self.rows0); self.R1 = len(self.rows1)
        kd = sp["kinds"]
        self.A_cnt = cnt_matrix(self.rows0, self.rows0, k, q, kd, t)
        self.A = (self.A_cnt == 0)
        self.B1 = (self.A_cnt == 1)
        if self.R1:
            self.C = (cnt_matrix(self.rows0, self.rows1, k, q, kd, t) == 0)
            self.D = (cnt_matrix(self.rows1, self.rows0, k, q, kd, t) == 0)
        else:
            self.C = np.zeros((self.R, 0), bool); self.D = np.zeros((0, self.R), bool)
    def row_perm(self):
        """index of the left-right reversal of each Omega0 row"""
        k, q = self.sp["k"], self.sp["q"]
        key = {tuple(r): i for i, r in enumerate(self.rows0.tolist())}
        return np.array([key[tuple(r[::-1])] for r in self.rows0.tolist()])

# ---------------------------------------------------------------- matrix-free tensor engine
def contract(v, offsets, q, k, t, J):
    """Apply the pair-transfer operator to a batch of ring vectors without storing any matrix.
    v: int64 array (B, J+1, q**k): ring element sum_c v[c] eps^c per row x (eps^(J+1)=0).
    Output y[row Y] = sum_X v[X] * eps^(number of pairs (Y_j, X_{j+d}), d in offsets, with Y_j + X_{j+d} = t).
    offsets: tuple of d in {-1,0,1}.  Column by column: introduce Y_j, sum out X_{j-1}.
    No residue is ever multiplied by a residue: only sums of at most q entries, so |value| <= q*max|input|."""
    B, C, N = v.shape
    if not (C == J + 1 and N == q**k): raise ValueError("contract: bad input shape")
    state = v.reshape(B, C, 1, 1, N)                  # (B,C, q^j, X, q^(k-j))
    hasA = -1 in offsets; hasV = 0 in offsets; hasD = 1 in offsets
    for j in range(k):
        Aj = q**j; Xd = state.shape[3]
        if k - j >= 2: cd, rest = q, q**(k - j - 2)
        else: cd, rest = 1, 1
        S = state.reshape(B, C, Aj, Xd, q, cd, rest)
        Sx = S.sum(axis=3)                             # (B,C,Aj,q,cd,rest)
        outs = []
        xs = np.arange(q).reshape(q, 1); cs = np.arange(cd).reshape(1, cd)
        for y in range(q):
            w = t - y; wv = 0 <= w < q
            mf = np.zeros((q, cd), dtype=np.int64)      # pairs fixed by (x_j, x_{j+1}) for this y
            if hasV and wv: mf += (xs == w)
            if hasD and wv and cd == q: mf += (cs == w)
            useA = hasA and Xd == q and wv
            Sa = S[:, :, :, w, :, :, :] if useA else None
            base = Sx - Sa if useA else Sx
            out = np.zeros_like(Sx)
            for m in range(J + 1):
                mk = (mf == m).reshape(1, 1, 1, q, cd, 1)
                if not mk.any(): continue
                out[:, m:] += mk * base[:, :C - m]
                if useA and m + 1 <= J: out[:, m + 1:] += mk * Sa[:, :C - m - 1]
            outs.append(out)
        new = np.stack(outs, axis=3)                   # (B,C,Aj,y,q(xj),cd,rest)
        state = new.reshape(B, C, Aj * q, q, cd * rest)
    return state.sum(axis=3).reshape(B, C, N)

def offsets_right(kinds):   # (A v)[a] = sum_b ... ; output index = upper row a, input = lower row b
    o = []
    if "A" in kinds: o.append(-1)
    if "V" in kinds: o.append(0)
    if "D" in kinds: o.append(1)
    return tuple(o)
def offsets_left(kinds):    # output index = lower row b, input = upper row a
    o = []
    if "A" in kinds: o.append(1)
    if "V" in kinds: o.append(0)
    if "D" in kinds: o.append(-1)
    return tuple(o)
