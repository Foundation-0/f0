"""Critical latitudes of psi = P_m(c)/|P_{m+1}(c)|^(m/(m+1)) on (-1,1): for zonal A = r^{m+1}P_{m+1}, B = r^m P_m
the non-zero critical points of A + B form circles (one per critical latitude in the open hemisphere pairs)."""
import numpy as np
from numpy.polynomial import legendre as L
for m in range(1,13):
    p=m/(m+1); a=[0]*(m+1)+[1]; b=[0]*m+[1]
    # psi'=0  <=>  P_m' P_{m+1} - p P_m P_{m+1}' = 0 (polynomial in c), in the variable c=cos(theta); but dc/dtheta=-sin vanishes at poles
    num = L.legsub(L.legmul(L.legder(b),a), p*L.legmul(b,L.legder(a)))
    r = L.legroots(num); r = r[(abs(r.imag)<1e-9)&(abs(r.real)<1-1e-12)].real
    print(m, "critical latitudes:", len(r), " (degree of numerator", len(num)-1, ")")
