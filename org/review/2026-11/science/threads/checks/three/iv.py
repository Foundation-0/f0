"""Minimal vectorised interval arithmetic (numpy float64) with outward rounding.

Only +, -, *, /, square, sqrt and comparisons are used. IEEE 754 makes these correctly rounded
(round-to-nearest), so widening each computed endpoint by one ulp (np.nextafter) gives a rigorous
enclosure. No transcendental functions are used in proof steps.
"""
import numpy as np

INF = np.inf


def _dn(x):
    return np.nextafter(x, -INF)


def _up(x):
    return np.nextafter(x, INF)


class I:
    __slots__ = ('lo', 'hi')
    __array_priority__ = 1000

    def __init__(self, lo, hi=None, exact=False):
        lo = np.asarray(lo, dtype=float)
        hi = lo if hi is None else np.asarray(hi, dtype=float)
        self.lo = lo
        self.hi = hi

    @staticmethod
    def c(x):
        """Exact constant (must be a float exactly representing the intended value)."""
        return I(np.asarray(x, float), np.asarray(x, float))

    def __repr__(self):
        return 'I(%r, %r)' % (self.lo, self.hi)

    def _wrap(o):
        return o if isinstance(o, I) else I(o, o)

    def __add__(a, b):
        b = I._wrap(b)
        return I(_dn(a.lo + b.lo), _up(a.hi + b.hi))
    __radd__ = __add__

    def __neg__(a):
        return I(-a.hi, -a.lo)

    def __sub__(a, b):
        b = I._wrap(b)
        return I(_dn(a.lo - b.hi), _up(a.hi - b.lo))

    def __rsub__(a, b):
        return I._wrap(b) - a

    def __mul__(a, b):
        b = I._wrap(b)
        p = np.stack([a.lo * b.lo, a.lo * b.hi, a.hi * b.lo, a.hi * b.hi])
        # 0*inf guard not needed: no infinities expected
        return I(_dn(p.min(0)), _up(p.max(0)))
    __rmul__ = __mul__

    def sq(a):
        lo2 = a.lo * a.lo; hi2 = a.hi * a.hi
        mx = np.maximum(lo2, hi2)
        mn = np.where((a.lo <= 0) & (a.hi >= 0), 0.0, np.minimum(lo2, hi2))
        return I(np.where(mn > 0, _dn(mn), 0.0), _up(mx))

    def inv(a):
        bad = (a.lo <= 0) & (a.hi >= 0)
        with np.errstate(divide='ignore', invalid='ignore'):
            lo = np.where(bad, -INF, _dn(1.0 / a.hi))
            hi = np.where(bad, INF, _up(1.0 / a.lo))
        return I(lo, hi)

    def __truediv__(a, b):
        b = I._wrap(b)
        return a * b.inv()

    def __rtruediv__(a, b):
        return I._wrap(b) * a.inv()

    def sqrt(a):
        lo = np.sqrt(np.maximum(a.lo, 0.0)); hi = np.sqrt(np.maximum(a.hi, 0.0))
        return I(np.maximum(_dn(lo), 0.0), _up(hi))

    def __getitem__(self, k):
        return I(self.lo[k], self.hi[k])

    @property
    def mid(self):
        return 0.5 * (self.lo + self.hi)

    @property
    def rad(self):
        return 0.5 * (self.hi - self.lo)

    def pos(self):
        return self.lo > 0

    def neg(self):
        return self.hi < 0

    def nonzero(self):
        return (self.lo > 0) | (self.hi < 0)


def hull(a, b):
    return I(np.minimum(a.lo, b.lo), np.maximum(a.hi, b.hi))


def sum_(lst):
    s = lst[0]
    for x in lst[1:]:
        s = s + x
    return s
