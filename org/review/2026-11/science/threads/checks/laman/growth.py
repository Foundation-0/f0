from fractions import Fraction
import mpmath as mp
mp.mp.dps = 30
for r in (860, 868, 880, 2288, 6180):
    pass
print('formula: count >= 2^((n-3) mod 7) * 2 * (r/2)^floor((n-3)/7); growth per vertex = (r/2)^(1/7)  [n_G=10, |V_H|=3]')
for r in (860, 868, 880):
    print('r=%d  (r/2)=%d  (r/2)^(1/7)=%s   [wrong variant r^(1/7)=%s]' % (r, r//2, mp.nstr(mp.mpf(r//2)**(mp.mpf(1)/7), 8), mp.nstr(mp.mpf(r)**(mp.mpf(1)/7), 8)))
# sanity: explicit bound for n=3+7k and ratio of consecutive terms
for r in (860, 880):
    print('r', r, 'bound at n=73 (k=10):', 2*(r//2)**10, ' (n)^(1/n) check: %s' % mp.nstr(mp.mpf(2*(r//2)**10)**(mp.mpf(1)/73), 6))
# does the n=10 uses |V_G|-|V_H| =7 ; other glueing alternative: share an edge? not in paper.
