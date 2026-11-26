"""Independent reproduction (own code, exact rationals where possible) of the numbers in
gravity@8f96c4b:acceleration-evolution/comparison.json and of the c*H0/(2 pi) constants.
Exit status 1 if any reproduced number disagrees with the repository value beyond 1e-12 relative."""
import math, sys
from fractions import Fraction as F
from flint import arb, ctx

ctx.prec = 200
om = F(315, 1000)

def E2(z):  # exact rational E(z)^2
    return om * (1 + z) ** 3 + 1 - om

lo, hi = F(33, 100), F(144, 100)
ratio2 = E2(hi) / E2(lo)                       # exact rational
growth_H = arb(ratio2.numerator).sqrt() / arb(ratio2.denominator).sqrt()
dc14 = (F(1) + F(159, 100) * hi) / (F(1) + F(159, 100) * lo)          # (1.00 + 1.59 z)
mond = (F(103, 100) + F(120, 100) * hi) / (F(103, 100) + F(120, 100) * lo)  # (1.03 + 1.20 z)
q_dc14 = arb(dc14.numerator).log() - arb(dc14.denominator).log()
q_mond = arb(mond.numerator).log() - arb(mond.denominator).log()
lg = growth_H.log()
rows = [
    ('H_tracking_interval_growth', growth_H, 1.9206998594100706),
    ('dc14 interval_growth', arb(dc14.numerator) / dc14.denominator, 2.1575391880369907),
    ('mond interval_growth', arb(mond.numerator) / mond.denominator, 1.9340813464235624),
    ('dc14 endpoint q', q_dc14 / lg, 1.178153095153886),
    ('mond endpoint q', q_mond / lg, 1.010637257482444),
    ('dc14 growth/H', arb(dc14.numerator) / dc14.denominator / growth_H, 1.123308869663615),
]
bad = 0
for name, val, repo in rows:
    ok = abs(float(val.mid()) - repo) <= 1e-12 * abs(repo) and val.rad() < 1e-30
    bad += not ok
    print('%-28s mine=%s  repo=%.16g  %s' % (name, val.str(18), repo, 'OK' if ok else 'MISMATCH'))

c = 299792458.0; mpc = 3.0856775814913673e22
for H0 in (67.4, 67.36, 70.0, 73.0):
    print('c*H0/(2 pi) for H0=%.2f km/s/Mpc: %.5e m/s^2' % (H0, c * H0 * 1e3 / mpc / (2 * math.pi)))
H0_for_10422 = 1.0422e-10 * 2 * math.pi * mpc / c / 1e3
print('H0 that gives 1.0422e-10: %.3f km/s/Mpc' % H0_for_10422)
print('a0=1.20e-10 corresponds to cH0/(2 pi) with H0 = %.1f km/s/Mpc' % (1.2e-10 * 2 * math.pi * mpc / c / 1e3))
sys.exit(1 if bad else 0)
