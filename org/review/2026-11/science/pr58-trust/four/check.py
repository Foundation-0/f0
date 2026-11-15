#!/usr/bin/env python3
"""Trusted checker: count the balance points of positive point charges.

Usage:
    python3 -O check.py CONFIG.json CERT.json [EXPECTED_COUNT]

CONFIG.json holds "sites" (n triples) and "charges" (n values), each number a
decimal or fraction string such as "-0.35180" or "-1759/5000". CERT.json is
written by find.py, which is not trusted. This file is the whole trusted base.

What it proves, for the exact rational configuration in CONFIG.json, with the
Coulomb potential V(x) = sum_j q_j / |x - p_j| in three dimensions:

  1. LOWER BOUND. Each box listed in the certificate contains exactly one
     zero of grad V, and that zero is non-degenerate. The boxes are pairwise
     disjoint. So V has at least that many balance points. The index of each
     (the number of negative eigenvalues of the Hessian) is 2 when the Hessian
     determinant is positive and 1 when it is negative, because the Hessian has
     trace zero.
  2. EXACT COUNT. A bisection tree, replayed here from a root box that this
     program computes from the sites itself, covers every place a balance
     point can be. Every leaf is either shown here to hold no zero, or lies
     inside one of the boxes of item 1. So V has exactly that many.

Nothing here uses floating point. Every number is an int or a Fraction.
Every coordinate and charge must be a JSON string, and an unquoted JSON number
with a fraction or exponent is refused anywhere: it would pass through a
binary float on reading. (JSON integers are read exactly.) Keys
may not repeat. Each file is read once; its sha256 is of those same bytes.
Every real quantity is enclosed in an interval [lo, hi] of integers scaled by
2**P, and each operation rounds lo down and hi up. Square roots are bounded
with math.isqrt. Every failed check raises CheckFailed; there is no assert,
so python3 -O does not weaken anything.

The four lemmas used (proofs in NOTE.md beside this file):

  L1 (hull). Every balance point lies in the interior of the convex hull of
     the sites. A box lying in the closed outer half-space of a face of the
     tetrahedron holds none.
  L2 (dominance). |grad V(x)| >= q_k/|x-p_k|^2 - sum_{j!=k} q_j/|x-p_j|^2.
     If the right side is positive on a box, the box holds no balance point.
  L3 (Taylor). For a box B with centre c and any fixed matrix Y, each
     component of Y grad V on B lies in
       (Y F(c))_m + (Y H(c) h)_m + (1/2) h^T (sum_i Y_mi T_i(B)) h,
     with F, H, T the first, second and third derivatives of V, h = x - c,
     and T_i(B) an enclosure of the third derivatives over B. If that range
     excludes 0 for some m, B holds no zero.
  L4 (Krawczyk). If K(B) = c - Y F(c) + (I - Y J(B))(B - c) lies in the
     interior of B, where J(B) encloses the Hessian of V over B, then B holds
     exactly one zero of grad V and every matrix in J(B) is non-singular.
     (R. Krawczyk 1969; R. E. Moore 1977; A. Neumaier, Interval Methods for
     Systems of Equations, 1990, Thm 5.1.8.)
"""

import hashlib
import json
import re
import sys
from fractions import Fraction
from math import isqrt

P = 128                 # fractional bits of the fixed-point grid
S = 1 << P              # the number 1 on that grid
MAX_DEPTH = 200


class CheckFailed(Exception):
    pass


def require(cond, msg):
    if not cond:
        raise CheckFailed(msg)


def cdiv(a, b):
    """Ceiling of a/b for integers, b > 0."""
    return -((-a) // b)


def ceil_isqrt(n):
    r = isqrt(n)
    return r if r * r == n else r + 1


# ---------------------------------------------------------------------------
# Interval arithmetic on the grid. I(lo, hi) stands for [lo/S, hi/S].
# ---------------------------------------------------------------------------

class I:
    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi):
        require(lo <= hi, "interval with lo > hi")
        self.lo = lo
        self.hi = hi

    @staticmethod
    def of(x):
        """Smallest grid interval containing the rational x."""
        x = Fraction(x)
        n = x.numerator * S
        d = x.denominator
        return I(n // d, cdiv(n, d))

    @staticmethod
    def pt(n):
        return I(n, n)

    def __add__(a, b):
        return I(a.lo + b.lo, a.hi + b.hi)

    def __sub__(a, b):
        return I(a.lo - b.hi, a.hi - b.lo)

    def __neg__(a):
        return I(-a.hi, -a.lo)

    def __mul__(a, b):
        p = (a.lo * b.lo, a.lo * b.hi, a.hi * b.lo, a.hi * b.hi)
        return I(min(p) >> P, -((-max(p)) >> P))

    def times_int(a, k):
        return I(a.lo * k, a.hi * k) if k >= 0 else I(a.hi * k, a.lo * k)

    def sqr(a):
        if a.lo >= 0:
            lo2, hi2 = a.lo * a.lo, a.hi * a.hi
        elif a.hi <= 0:
            lo2, hi2 = a.hi * a.hi, a.lo * a.lo
        else:
            lo2, hi2 = 0, max(a.lo * a.lo, a.hi * a.hi)
        return I(lo2 >> P, -((-hi2) >> P))

    def cube(a):
        # x -> x^3 is increasing
        return I((a.lo ** 3) >> (2 * P), -((-(a.hi ** 3)) >> (2 * P)))

    def sqrt(a):
        require(a.lo >= 0, "square root of an interval below zero")
        return I(isqrt(a.lo << P), ceil_isqrt(a.hi << P))

    def recip(a):
        require(a.lo > 0, "reciprocal of an interval that is not positive")
        return I((S * S) // a.hi, cdiv(S * S, a.lo))

    def mag(a):
        """Upper bound of |x| on the interval, on the grid."""
        return max(-a.lo, a.hi)

    def mig(a):
        """Lower bound of |x| on the interval, on the grid."""
        if a.lo > 0:
            return a.lo
        if a.hi < 0:
            return -a.hi
        return 0


ZERO = I(0, 0)
TRIPLES = [(i, j, k) for i in range(3) for j in range(i, 3) for k in range(j, 3)]


def tidx(i, j, k):
    return tuple(sorted((i, j, k)))


# ---------------------------------------------------------------------------
# The configuration.
# ---------------------------------------------------------------------------

NUMBER = re.compile(r"^[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:/[0-9]+)?$")


def parse_number(s):
    """A decimal or fraction given as a JSON string, read exactly."""
    require(isinstance(s, str), "a number is not written as a string: %r" % (s,))
    require(NUMBER.match(s) is not None, "not a plain decimal or fraction: %r" % (s,))
    return Fraction(s)          # Fraction accepts "-0.35180" and "-1759/5000"


def _no_float(text):
    raise CheckFailed("the unquoted JSON number %s would be read as a float" % text)


def _no_repeats(pairs):
    keys = [k for k, _ in pairs]
    require(len(keys) == len(set(keys)), "a key repeats in a JSON object")
    return dict(pairs)


def read_json(path):
    """Read the file once; return its bytes' sha256 and the parsed object."""
    with open(path, "rb") as fh:
        raw = fh.read()
    try:
        obj = json.loads(raw.decode("utf-8"), parse_float=_no_float,
                         parse_constant=_no_float, object_pairs_hook=_no_repeats)
    except ValueError as e:
        raise CheckFailed("not valid JSON: %s" % e)
    return hashlib.sha256(raw).hexdigest(), obj


def config_from(cfg):
    require(isinstance(cfg, dict), "the configuration is not a JSON object")
    require(isinstance(cfg.get("sites"), list) and isinstance(cfg.get("charges"), list),
            "the configuration needs lists 'sites' and 'charges'")
    for p in cfg["sites"]:
        require(isinstance(p, list) and len(p) == 3, "a site is not a triple")
    sites = [tuple(parse_number(v) for v in p) for p in cfg["sites"]]
    charges = [parse_number(q) for q in cfg["charges"]]
    require(len(sites) == len(charges) and len(sites) >= 1, "sites and charges differ in number")
    for q in charges:
        require(q > 0, "a charge is not positive")
    for a in range(len(sites)):
        for b in range(a):
            require(sites[a] != sites[b], "two sites coincide")
    return sites, charges


def load_config(path):
    return config_from(read_json(path)[1])


class Field:
    """Enclosures of the derivatives of V = sum q_j / |x - p_j|."""

    def __init__(self, sites, charges):
        self.n = len(sites)
        self.sites = sites
        self.charges = charges
        self.p = [[I.of(c) for c in s] for s in sites]
        self.q = [I.of(c) for c in charges]

    def sq_dist(self, X):
        """Interval of |x - p_j|^2 over the box X, for each j."""
        out = []
        for pj in self.p:
            d = [X[i] - pj[i] for i in range(3)]
            out.append(d[0].sqr() + d[1].sqr() + d[2].sqr())
        return out

    def derivs(self, X, third=True):
        """F = grad V, H = Hessian, T = third derivatives, over the box X.

        Returns None when the box may contain a site (V is singular there).
        """
        F = [ZERO] * 3
        H = [[ZERO] * 3 for _ in range(3)]
        T = {t: ZERO for t in TRIPLES} if third else None
        for j in range(self.n):
            q = self.q[j]
            d = [X[i] - self.p[j][i] for i in range(3)]
            d2 = [d[i].sqr() for i in range(3)]
            s = d2[0] + d2[1] + d2[2]
            if s.lo <= 0:
                return None
            ir = s.sqrt().recip()
            ir2 = ir.sqr()
            ir3 = ir2 * ir
            ir5 = ir3 * ir2
            q3 = q * ir3
            q5 = q * ir5
            for i in range(3):
                F[i] = F[i] - q3 * d[i]
            for i in range(3):
                for k in range(i, 3):
                    dd = d2[i] if i == k else d[i] * d[k]
                    h = (q5 * dd).times_int(3)
                    if i == k:
                        h = h - q3
                    H[i][k] = H[i][k] + h
            if third:
                q7 = q5 * ir2
                for (a, b, c) in TRIPLES:
                    if a == b == c:
                        ddd = d[a].cube()
                    elif a == b:
                        ddd = d2[a] * d[c]
                    elif b == c:
                        ddd = d2[b] * d[a]
                    else:
                        ddd = d[a] * d[b] * d[c]
                    t = -(q7 * ddd).times_int(15)
                    # 3 (delta_ab d_c + delta_ac d_b + delta_bc d_a) / r^5
                    lin = ZERO
                    if a == b:
                        lin = lin + d[c]
                    if a == c:
                        lin = lin + d[b]
                    if b == c:
                        lin = lin + d[a]
                    if a == b or a == c or b == c:
                        t = t + (q5 * lin).times_int(3)
                    T[(a, b, c)] = T[(a, b, c)] + t
        for i in range(3):
            for k in range(i):
                H[i][k] = H[k][i]
        return F, H, T


# ---------------------------------------------------------------------------
# Boxes are (lo, hi) pairs of integer triples on the grid.
# ---------------------------------------------------------------------------

def box_intervals(lo, hi):
    return [I(lo[i], hi[i]) for i in range(3)]


def centre_radius(lo, hi):
    c = [(lo[i] + hi[i]) >> 1 for i in range(3)]
    r = [max(hi[i] - c[i], c[i] - lo[i]) for i in range(3)]
    return c, r


def approx_inverse(H):
    """An exact grid matrix close to the inverse of the midpoint of H.

    Any matrix is sound in L3 and L4; this one only makes the tests succeed.
    Returns None when the midpoint matrix is singular.
    """
    m = [[(H[i][k].lo + H[i][k].hi) >> 1 for k in range(3)] for i in range(3)]
    adj = [[0] * 3 for _ in range(3)]
    for i in range(3):
        for k in range(3):
            r = [x for x in range(3) if x != k]
            c = [x for x in range(3) if x != i]
            minor = m[r[0]][c[0]] * m[r[1]][c[1]] - m[r[0]][c[1]] * m[r[1]][c[0]]
            adj[i][k] = minor if (i + k) % 2 == 0 else -minor
    det = sum(m[0][k] * adj[k][0] for k in range(3))
    if det == 0:
        return None
    # inverse of (m / S) is adj(m) * S / det(m); on the grid multiply by S again
    return [[(adj[i][k] * S * S) // det for k in range(3)] for i in range(3)]


def _dot(row, v):
    """Interval of sum_i (row_i / S) * v_i, row exact on the grid."""
    acc_lo = 0
    acc_hi = 0
    for i in range(3):
        y = row[i]
        if y >= 0:
            acc_lo += y * v[i].lo
            acc_hi += y * v[i].hi
        else:
            acc_lo += y * v[i].hi
            acc_hi += y * v[i].lo
    return I(acc_lo >> P, -((-acc_hi) >> P))


def det3(H):
    return (H[0][0] * (H[1][1] * H[2][2] - H[1][2] * H[2][1])
            - H[0][1] * (H[1][0] * H[2][2] - H[1][2] * H[2][0])
            + H[0][2] * (H[1][0] * H[2][1] - H[1][1] * H[2][0]))


# ---------------------------------------------------------------------------
# The four tests.
# ---------------------------------------------------------------------------

class Tests:
    def __init__(self, sites, charges):
        self.field = Field(sites, charges)
        self.n = len(sites)
        self.faces = self._faces(sites)

    @staticmethod
    def _faces(sites):
        """Outer half-spaces of the faces of the hull, exactly (needs n = 4)."""
        require(len(sites) == 4, "the hull test here is written for four sites")
        faces = []
        for opp in range(4):
            a, b, c = [sites[i] for i in range(4) if i != opp]
            u = [b[i] - a[i] for i in range(3)]
            v = [c[i] - a[i] for i in range(3)]
            nrm = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
            side = sum(nrm[i] * (sites[opp][i] - a[i]) for i in range(3))
            require(side != 0, "the four sites are coplanar")
            if side > 0:
                nrm = [-x for x in nrm]
            faces.append((nrm, sum(nrm[i] * a[i] for i in range(3))))
        return faces

    def hull(self, lo, hi):
        """L1: the box lies in the closed outer half-space of some face."""
        for nrm, off in self.faces:
            m = Fraction(0)
            for i in range(3):
                m += min(nrm[i] * Fraction(lo[i], S), nrm[i] * Fraction(hi[i], S))
            if m >= off:
                return True
        return False

    def dominance(self, lo, hi, k):
        """L2 for charge k."""
        s = self.field.sq_dist(box_intervals(lo, hi))
        if s[k].hi <= 0:
            return False
        lhs = Fraction(self.field.q[k].lo, s[k].hi)
        rhs = Fraction(0)
        for j in range(self.n):
            if j == k:
                continue
            if s[j].lo <= 0:
                return False
            rhs += Fraction(self.field.q[j].hi, s[j].lo)
        return lhs > rhs

    def _centre_and_box(self, lo, hi):
        c, r = centre_radius(lo, hi)
        at_c = self.field.derivs([I.pt(x) for x in c], third=False)
        on_b = self.field.derivs(box_intervals(lo, hi), third=True)
        if at_c is None or on_b is None:
            return None
        F, H, _ = at_c
        _, _, T = on_b
        return c, r, F, H, T

    def taylor(self, lo, hi, newton):
        """L3 with Y the approximate inverse (newton=True) or the identity."""
        got = self._centre_and_box(lo, hi)
        if got is None:
            return False
        c, r, F, H, T = got
        if newton:
            Y = approx_inverse(H)
            if Y is None:
                return False
        else:
            Y = [[S if i == k else 0 for k in range(3)] for i in range(3)]
        for m in range(3):
            g = _dot(Y[m], F)
            # linear part: sum_j |(Y H)_mj| r_j, on scale S^2
            lin = 0
            for jj in range(3):
                a = _dot(Y[m], [H[i][jj] for i in range(3)])
                lin += a.mag() * r[jj]
            # quadratic part: (1/2) sum_jk |sum_i Y_mi T_ijk| r_j r_k, on scale S^3
            quad = 0
            for jj in range(3):
                for kk in range(3):
                    mm = _dot(Y[m], [T[tidx(i, jj, kk)] for i in range(3)])
                    quad += mm.mag() * r[jj] * r[kk]
            # exclusion needs mig(g) > lin + quad/2, compared exactly on scale 2 S^3
            if 2 * g.mig() * S * S > 2 * lin * S + quad:
                return True
        return False

    def krawczyk(self, lo, hi):
        """L4. Returns the sign of det H at the centre on success, else 0."""
        got = self._centre_and_box(lo, hi)
        if got is None:
            return 0
        c, r, F, H, T = got
        Y = approx_inverse(H)
        if Y is None:
            return 0
        # J(B) = H(c) + T(B)[h], h in [-r, r]
        J = [[None] * 3 for _ in range(3)]
        for i in range(3):
            for jj in range(3):
                acc = H[i][jj]
                for kk in range(3):
                    acc = acc + T[tidx(i, jj, kk)] * I(-r[kk], r[kk])
                J[i][jj] = acc
        for m in range(3):
            g = _dot(Y[m], F)
            rho = 0                       # on scale S^2
            for jj in range(3):
                cm = _dot(Y[m], [J[i][jj] for i in range(3)])
                if m == jj:
                    cm = I.pt(S) - cm
                else:
                    cm = -cm
                rho += cm.mag() * r[jj]
            # K_m lies in [c_m - g.hi - rho, c_m - g.lo + rho] (real units);
            # it must lie strictly inside (lo_m, hi_m). Compared on scale S^2.
            if not ((c[m] - lo[m]) * S - g.hi * S - rho > 0):
                return 0
            if not ((hi[m] - c[m]) * S + g.lo * S - rho > 0):
                return 0
        dH = det3(H)
        if dH.lo > 0:
            return 1
        if dH.hi < 0:
            return -1
        return 0


# ---------------------------------------------------------------------------
# Checking a certificate.
# ---------------------------------------------------------------------------

def root_box(sites):
    lo = [min(Fraction(s[i]) for s in sites) for i in range(3)]
    hi = [max(Fraction(s[i]) for s in sites) for i in range(3)]
    lo = [(x.numerator * S) // x.denominator for x in lo]
    hi = [cdiv(x.numerator * S, x.denominator) for x in hi]
    return lo, hi


def contains(outer, inner):
    (olo, ohi), (ilo, ihi) = outer, inner
    return all(olo[i] <= ilo[i] and ihi[i] <= ohi[i] for i in range(3))


def disjoint(a, b):
    (alo, ahi), (blo, bhi) = a, b
    return any(ahi[i] < blo[i] or bhi[i] < alo[i] for i in range(3))


def fmt(x, digits=6):
    """Decimal text of the grid number x/S without floating point."""
    q = Fraction(x, S)
    sign = "-" if q < 0 else "+"
    q = abs(q)
    scaled = (q * 10 ** digits).numerator // (q * 10 ** digits).denominator
    whole, frac = divmod(scaled, 10 ** digits)
    return "%s%d.%0*d" % (sign, whole, digits, frac)


INTEGER = re.compile(r"^-?[0-9]+$")
TREE = re.compile(r"^(?:[xyzHNI]|D[0-9]|K[0-9]+\.)*$")


def check(config_path, cert_path, expected=None):
    digest, cfg = read_json(config_path)
    sites, charges = config_from(cfg)
    cert_digest, cert = read_json(cert_path)
    require(isinstance(cert, dict), "the certificate is not a JSON object")
    require(cert.get("P") == P, "certificate made for a different grid")
    require(isinstance(cert.get("boxes"), list), "the certificate has no list of boxes")
    for b in cert["boxes"]:
        require(isinstance(b, dict) and isinstance(b.get("lo"), list) and isinstance(b.get("hi"), list)
                and len(b["lo"]) == 3 and len(b["hi"]) == 3, "a box is not two triples")
        for v in b["lo"] + b["hi"]:
            require(isinstance(v, str) and INTEGER.match(v) is not None, "a box corner is not an integer string")
    require(isinstance(cert.get("tree"), str) and TREE.match(cert["tree"]) is not None,
            "the tree is not a string of known tokens")
    tests = Tests(sites, charges)

    # Item 1: the uniqueness boxes.
    boxes = []
    for b in cert["boxes"]:
        lo = [int(x) for x in b["lo"]]
        hi = [int(x) for x in b["hi"]]
        require(all(lo[i] < hi[i] for i in range(3)), "an empty uniqueness box")
        boxes.append((lo, hi))
    signs = []
    for idx, (lo, hi) in enumerate(boxes):
        sgn = tests.krawczyk(lo, hi)
        require(sgn != 0, "the Krawczyk test fails on box %d" % idx)
        signs.append(sgn)
    for a in range(len(boxes)):
        for b in range(a):
            require(disjoint(boxes[a], boxes[b]), "boxes %d and %d overlap" % (b, a))
    n_two = sum(1 for s in signs if s > 0)
    n_one = sum(1 for s in signs if s < 0)

    # Item 2: replay the bisection tree.
    tree = cert["tree"]
    pos = 0
    stats = {"H": 0, "D": 0, "N": 0, "I": 0, "K": 0}

    def token():
        nonlocal pos
        require(pos < len(tree), "the tree ends early")
        ch = tree[pos]
        pos += 1
        if ch == "D":
            k = int(tree[pos])
            pos += 1
            return ch, k
        if ch == "K":
            end = tree.index(".", pos)
            m = int(tree[pos:end])
            pos = end + 1
            return ch, m
        return ch, None

    stack = [(root_box(sites), 0)]
    while stack:
        (lo, hi), depth = stack.pop()
        require(depth <= MAX_DEPTH, "the tree is too deep")
        kind, arg = token()
        if kind in "xyz":
            ax = "xyz".index(kind)
            mid = (lo[ax] + hi[ax]) >> 1
            require(lo[ax] < mid < hi[ax], "a split of a box too thin to split")
            left_hi = list(hi)
            left_hi[ax] = mid
            right_lo = list(lo)
            right_lo[ax] = mid
            # push right first so the left half is read first
            stack.append(((right_lo, list(hi)), depth + 1))
            stack.append(((list(lo), left_hi), depth + 1))
            continue
        if kind == "H":
            require(tests.hull(lo, hi), "hull test fails on a leaf")
        elif kind == "D":
            require(0 <= arg < tests.n, "bad charge index in the tree")
            require(tests.dominance(lo, hi, arg), "dominance test fails on a leaf")
        elif kind == "N":
            require(tests.taylor(lo, hi, True), "Taylor test (Newton) fails on a leaf")
        elif kind == "I":
            require(tests.taylor(lo, hi, False), "Taylor test (plain) fails on a leaf")
        elif kind == "K":
            require(0 <= arg < len(boxes), "bad box index in the tree")
            require(contains(boxes[arg], (lo, hi)), "a leaf is not inside its box")
        else:
            raise CheckFailed("unknown tree token %r" % kind)
        stats[kind] += 1
    require(pos == len(tree), "the tree has trailing tokens")

    # Every leaf marked K lies in a box, so every balance point is in a box.
    # Each box holds exactly one and the boxes are disjoint.
    count = len(boxes)
    # Morse: for positive charges, (index 2) - (index 1) = n - 1.
    require(n_two - n_one == len(sites) - 1,
            "index sums break the Morse relation; the count cannot be complete")
    if expected is not None:
        require(count == expected, "the certificate proves %d, not %d" % (count, expected))

    lines = []
    lines.append("config %s sha256 %s" % (config_path, digest))
    lines.append("certificate %s sha256 %s" % (cert_path, cert_digest))
    lines.append("charges %s" % ", ".join(str(q) for q in charges))
    for j, p in enumerate(sites):
        lines.append("site %d: (%s)" % (j, ", ".join(str(v) for v in p)))
    lines.append("uniqueness boxes: %d, pairwise disjoint" % count)
    for idx, ((lo, hi), sgn) in enumerate(zip(boxes, signs)):
        c, r = centre_radius(lo, hi)
        lines.append("  box %2d centre (%s, %s, %s) half-width %s  index %d"
                     % (idx, fmt(c[0]), fmt(c[1]), fmt(c[2]), fmt(max(r), 9).lstrip("+"),
                        2 if sgn > 0 else 1))
    lines.append("tree leaves: hull %d, dominance %d, taylor-newton %d, taylor-plain %d, inside a box %d"
                 % (stats["H"], stats["D"], stats["N"], stats["I"], stats["K"]))
    lines.append("PROVED at least %d balance points (%d of index 2, %d of index 1)" % (count, n_two, n_one))
    lines.append("PROVED exactly %d balance points" % count)
    return "\n".join(lines)


def main(argv):
    if len(argv) not in (3, 4):
        sys.stderr.write(__doc__)
        return 2
    expected = int(argv[3]) if len(argv) == 4 else None
    print(check(argv[1], argv[2], expected))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
