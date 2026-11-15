"""Independent exact elastic tensor of the n-dimensional 'contact framework'.

Written from the definition only (results/rigidity-nd/PROOF.md, Statement); imports nothing from the repository.

Definition used:
  cell lattice 2Z^n; dots p(i,s) = s*t*e_i (i = 1..n, s = +-1) in each cell.
  Default t = c = 2 - sqrt2 (incentre of the facet pyramid of [-1,1]^n).
  Bars: every pair of dots at the minimum distance (found by search, not hard coded).
  Model: harmonic central springs, spring constant 1, rest length = present length (no pre-stress),
  energy per cell E = 1/2 sum_bars delta^2, delta = first-order length change.
  Homogeneous strain eps (symmetric tensor) plus one-cell-periodic internal displacements u, relaxed exactly.
  C_ijkl from W = E/V = 1/2 eps:C:eps, V = 2^n. Voigt: C11 = C_1111, C12 = C_1122, C44 = C_1212.

Arithmetic: exact, in Q(sqrt2) built on flint.fmpq (no floating point anywhere in the proof path).
For general t the option --t p/q uses a rational t; then bars are found per class (see --t notes below).
"""
import sys, itertools, argparse
from flint import fmpq


class Q2:
    """a + b*sqrt2 with a, b rational."""
    __slots__ = ("a", "b")

    def __init__(self, a, b=0):
        self.a = a if isinstance(a, fmpq) else fmpq(a)
        self.b = b if isinstance(b, fmpq) else fmpq(b)

    def __add__(s, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return Q2(s.a + o.a, s.b + o.b)
    __radd__ = __add__

    def __sub__(s, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return Q2(s.a - o.a, s.b - o.b)

    def __rsub__(s, o):
        return Q2(o) - s

    def __neg__(s):
        return Q2(-s.a, -s.b)

    def __mul__(s, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return Q2(s.a * o.a + 2 * s.b * o.b, s.a * o.b + s.b * o.a)
    __rmul__ = __mul__

    def inv(s):
        d = s.a * s.a - 2 * s.b * s.b
        if d == 0:
            raise ZeroDivisionError("zero in Q(sqrt2)")
        return Q2(s.a / d, -s.b / d)

    def __truediv__(s, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return s * o.inv()

    def iszero(s):
        return s.a == 0 and s.b == 0

    def __eq__(s, o):
        o = o if isinstance(o, Q2) else Q2(o)
        return s.a == o.a and s.b == o.b

    def __hash__(s):
        return hash((int(s.a.p), int(s.a.q), int(s.b.p), int(s.b.q)))

    def sign(s):
        """Exact sign of a + b sqrt2."""
        a, b = s.a, s.b
        sa = (a > 0) - (a < 0)
        sb = (b > 0) - (b < 0)
        if sb == 0:
            return sa
        if sa == 0:
            return sb
        if sa == sb:
            return sa
        # opposite signs: compare a^2 with 2 b^2
        d = a * a - 2 * b * b
        return sa if d > 0 else (sb if d < 0 else 0)

    def __lt__(s, o):
        return (s - o).sign() < 0

    def __float__(s):
        return float(s.a) + float(s.b) * 2 ** 0.5

    def __repr__(s):
        if s.b == 0:
            return str(s.a)
        return f"({s.a} + {s.b}*sqrt2)"


ZERO = Q2(0)


def check(cond, msg):
    if not cond:
        raise SystemExit("CHECK FAILED: " + msg)


def build(n, t, graph=False):
    """Return dots (list of vectors), bars as (i, j, shift, lvec, d2) with lvec = x_j + shift - x_i.
    graph=False: bars = all pairs at the minimum distance (contact rule; used for t = 2 - sqrt2).
    graph=True: bars by the combinatorial rule of the statement (intra: same cell, different axes;
    cross: p(i,+) to p(i,-) of the cell shifted by +2 e_i). Used for rational t, where bar lengths differ."""
    dots = []
    for i in range(n):
        for s in (1, -1):
            v = [ZERO] * n
            v[i] = t * s
            dots.append(v)
    # neighbour cells: shifts in 2*{-1,0,1}^n. Any pair farther apart is at least
    # 2*1 - 2t... we only need cells that can be within the minimal distance; since |coords| <= t < 1,
    # a difference in cell index of 2 or more along some axis gives distance >= 4 - 2t > 2 > any candidate.
    best = None
    pairs = []
    for i in range(len(dots)):
        for j in range(len(dots)):
            for sh in itertools.product((-2, 0, 2), repeat=n):
                if i == j and all(x == 0 for x in sh):
                    continue
                l = [dots[j][k] + sh[k] - dots[i][k] for k in range(n)]
                d2 = ZERO
                for x in l:
                    d2 = d2 + x * x
                pairs.append((d2, i, j, sh, l))
                if best is None or d2 < best:
                    best = d2
    bars = []
    for d2, i, j, sh, l in pairs:
        if graph:
            ai, si = divmod(i, 2)
            aj, sj = divmod(j, 2)
            intra = all(x == 0 for x in sh) and ai != aj
            cross = (ai == aj and si == 0 and sj == 1 and
                     all(sh[k] == (2 if k == ai else 0) for k in range(n)))
            if intra or cross:
                key = (i, j, sh)
                rkey = (j, i, tuple(-x for x in sh))
                if intra and rkey < key:
                    continue
                bars.append((i, j, sh, l, d2))
            continue
        if d2 == best:
            # keep each undirected bar once: (i,j,sh) ~ (j,i,-sh)
            key = (i, j, sh)
            rkey = (j, i, tuple(-x for x in sh))
            if rkey < key:
                continue
            bars.append((i, j, sh, l, d2))
    return dots, bars, best


def strain_index(n):
    idx = []
    for a in range(n):
        idx.append((a, a))
    for a in range(n):
        for b in range(a + 1, n):
            idx.append((a, b))
    return idx


def rows(n, dots, bars, d2):
    """Each bar gives delta = r . [eps ; u] * (1/|l|). We store r without 1/|l| and divide by |l|^2 in energy."""
    sidx = strain_index(n)
    m = len(sidx)
    N = len(dots) * n
    R = []
    for i, j, sh, l, bd2 in bars:
        r = [ZERO] * (m + N)
        for k, (a, b) in enumerate(sidx):
            if a == b:
                r[k] = l[a] * l[a]
            else:
                r[k] = 2 * l[a] * l[b]          # tensor strain e_ab = e_ba
        for k in range(n):
            r[m + j * n + k] = r[m + j * n + k] + l[k]
            r[m + i * n + k] = r[m + i * n + k] - l[k]
        R.append((r, bd2.inv()))
    return R, m, N


def solve_consistent(K, B):
    """Solve K X = B exactly (K square, maybe singular). Return X (one solution); raise if inconsistent."""
    nr = len(K)
    nc = len(B[0])
    A = [K[r][:] + B[r][:] for r in range(nr)]
    piv_cols = []
    row = 0
    for col in range(nr):
        p = None
        for r in range(row, nr):
            if not A[r][col].iszero():
                p = r
                break
        if p is None:
            continue
        A[row], A[p] = A[p], A[row]
        inv = A[row][col].inv()
        A[row] = [x * inv for x in A[row]]
        for r in range(nr):
            if r != row and not A[r][col].iszero():
                f = A[r][col]
                Ar = A[r]
                Ap = A[row]
                A[r] = [Ar[k] - f * Ap[k] for k in range(len(Ar))]
        piv_cols.append(col)
        row += 1
        if row == nr:
            break
    rank = row
    for r in range(rank, nr):
        for k in range(nr + nc):
            check(A[r][k].iszero(), "inconsistent relaxation system")
    X = [[ZERO] * nc for _ in range(nr)]
    for r, col in enumerate(piv_cols):
        for k in range(nc):
            X[col][k] = A[r][nr + k]
    return X, rank


def elastic(n, t, graph=False):
    dots, bars, d2 = build(n, t, graph)
    R, m, N = rows(n, dots, bars, d2)
    # energy per cell = 1/2 sum_bars (r.x)^2 / |l|^2 ; H below is twice that quadratic form's matrix /2,
    # i.e. E = 1/2 x^T H x with H = sum r r^T / |l|^2
    H = [[ZERO] * (m + N) for _ in range(m + N)]
    for r, w in R:
        nz = [k for k in range(m + N) if not r[k].iszero()]
        for a in nz:
            for b in nz:
                H[a][b] = H[a][b] + r[a] * r[b] * w
    Hee = [row[:m] for row in H[:m]]
    Heu = [row[m:] for row in H[:m]]
    Huu = [row[m:] for row in H[m:]]
    Hue = [row[:m] for row in H[m:]]
    X, rank_uu = solve_consistent(Huu, Hue)
    Ceff = [[Hee[a][b] - sum((Heu[a][k] * X[k][b] for k in range(N)), ZERO) for b in range(m)] for a in range(m)]
    # unrelaxed (affine) tensor
    V = Q2(2 ** n)
    # W = 1/2 e^T Ceff e / V with tensor strains. Voigt: diagonal unchanged; shear gamma = 2 e_ab.
    Cv = [[None] * m for _ in range(m)]
    Ca = [[None] * m for _ in range(m)]
    for a in range(m):
        for b in range(m):
            fa = 1 if a < n else 2
            fb = 1 if b < n else 2
            Cv[a][b] = Ceff[a][b] / (V * fa * fb)
            Ca[a][b] = Hee[a][b] / (V * fa * fb)
    return dict(dots=dots, bars=bars, d2=d2, Cv=Cv, Ca=Ca, m=m, N=N, rank_uu=rank_uu, R=R)


def rank_of(M):
    M = [r[:] for r in M]
    nr, nc = len(M), len(M[0])
    rank = 0
    for col in range(nc):
        p = None
        for r in range(rank, nr):
            if not M[r][col].iszero():
                p = r
                break
        if p is None:
            continue
        M[rank], M[p] = M[p], M[rank]
        inv = M[rank][col].inv()
        M[rank] = [x * inv for x in M[rank]]
        for r in range(nr):
            if r != rank and not M[r][col].iszero():
                f = M[r][col]
                M[r] = [M[r][k] - f * M[rank][k] for k in range(nc)]
        rank += 1
        if rank == nr:
            break
    return rank


def poisson(Cv, n):
    """Uniaxial stress along axis 1: solve C_diag e = (1,0,...,0); nu = -e2/e1."""
    D = [[Cv[a][b] for b in range(n)] for a in range(n)]
    rhs = [[Q2(1 if a == 0 else 0)] for a in range(n)]
    if rank_of(D) < n:
        # uniaxial stress cannot be carried (n = 2: C11 = C12). Report the strain-ratio formula
        # nu = C12 / (C11 + (n-2) C12) from dW/de_j = 0, j >= 2, as the repository does ("formally").
        return D[0][1] / (D[0][0] + (n - 2) * D[0][1])
    X, rk = solve_consistent(D, rhs)
    check(rk == n, "diagonal block singular")
    return -(X[1][0] / X[0][0])


def run(n, t, label, corrupt=False, graph=False):
    out = {}
    res = elastic(n, t, graph)
    Cv, Ca, m = res["Cv"], res["Ca"], res["m"]
    nb = len(res["bars"])
    out["bars_per_cell"] = nb
    check(nb == 2 * n * n - n, f"n={n}: bars per cell {nb} != 2n^2-n")
    # coordination
    deg = [0] * (2 * n)
    for i, j, sh, l, bd2 in res["bars"]:
        deg[i] += 1
        deg[j] += 1
    check(all(d == 2 * n - 1 for d in deg), f"n={n}: coordination {deg}")
    C11, C12, C44 = Cv[0][0], Cv[0][1], (Cv[n][n] if m > n else None)
    two_n = Q2(2 ** n)
    nn = Q2(n * n)
    exp11 = Q2(4 * (n - 1) ** 2) / (nn * two_n)
    exp12 = Q2(4) / (nn * two_n)
    if corrupt:
        # control: a wrong target formula (C12 off by 1 percent) must be reported as a mismatch
        exp12 = exp12 * Q2(fmpq(101, 100))
    # cubic symmetry checks
    for a in range(n):
        check(Cv[a][a] == C11, "C11 not uniform")
        for b in range(n):
            if a != b:
                check(Cv[a][b] == C12, "C12 not uniform")
    for a in range(m):
        for b in range(m):
            if a >= n or b >= n:
                check(Cv[a][b].iszero(), f"shear entry ({a},{b}) = {Cv[a][b]} not zero")
    nu = poisson(Cv, n)
    out.update(C11=C11, C12=C12, C44=C44, nu=nu,
               ratio=C11 / C12, Cprime=(C11 - C12) / 2,
               match_C11=(C11 == exp11), match_C12=(C12 == exp12),
               match_ratio=(C11 / C12 == Q2((n - 1) ** 2)),
               match_nu=(nu == Q2(1) / Q2(n * n - n - 1)))
    # affine (unrelaxed) constants: Cauchy check
    out.update(A11=Ca[0][0], A12=Ca[0][1], A44=(Ca[n][n] if m > n else None))
    # Maxwell counts at q = 0 (periodic, fixed lattice): rank of rigidity matrix on u
    Ru = [r[m:] for r, w in res["R"]]
    rk = rank_of(Ru)
    out["q0_zero_modes"] = 2 * n * n - rk
    out["q0_self_stresses"] = nb - rk
    # rank of relaxed elastic tensor
    out["rank_C"] = rank_of(Cv)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--nmax", type=int, default=6)
    ap.add_argument("--t", default=None, help="rational t instead of 2 - sqrt2, e.g. 3/10")
    ap.add_argument("--corrupt", action="store_true", help="multiply C12 by 1.01: must FAIL")
    args = ap.parse_args()
    if args.t is None:
        t = Q2(2, -1)
        label = "t = 2 - sqrt2"
    else:
        p, q = args.t.split("/")
        t = Q2(fmpq(int(p), int(q)))
        label = f"t = {args.t}"
    allok = True
    print(f"# {label}")
    for n in range(2, args.nmax + 1):
        o = run(n, t, label, corrupt=args.corrupt, graph=args.t is not None)
        ok = o["match_C11"] and o["match_C12"] and o["match_ratio"] and o["match_nu"]
        allok &= ok
        print(f"n={n}: bars/cell={o['bars_per_cell']} C11={o['C11']} C12={o['C12']} C44={o['C44']} "
              f"C11/C12={o['ratio']} C'=(C11-C12)/2={o['Cprime']} nu100={o['nu']} "
              f"rankC={o['rank_C']} q0: zero modes={o['q0_zero_modes']} self-stresses={o['q0_self_stresses']} "
              f"| affine A11={o['A11']} A12={o['A12']} A44={o['A44']} | match={ok}", flush=True)
    print("ALL MATCH" if allok else "MISMATCH")
    if not allok:
        sys.exit(1)
