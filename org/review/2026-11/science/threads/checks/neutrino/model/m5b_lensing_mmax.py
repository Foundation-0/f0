"""Largest m whose equilibrium halo (occupation 1/2, flat-V field, core 5 kpc) stays below the 2-sigma lensing limit at 300 kpc."""
import math, numpy as np
from m_lib import *
import m5_galaxies as m5
out = []
def P(*a): print(*a, flush=True); out.append(" ".join(map(str, a)))
def halo300(m, V, rc=5.0):
    Vv = V * 1e3; sig = Vv / math.sqrt(2)
    Mh, rr = halo_mass(300.0, m, 2, sig, lambda r: 0.5 * Vv ** 2 * np.log1p((np.asarray(r) / rc) ** 2)); return Mh[-1]
for lab, lm, V, e in m5.T2:
    Mb = 10 ** lm; up = m5.Mextra_at(V + 2 * e, Mb) / Mb; up2 = m5.Mextra_at(V + 2 * e, Mb / 10 ** 0.1) / (Mb / 10 ** 0.1)
    res = []
    for rc in (2.0, 5.0, 10.0):
        lo, hi = 1.0, 100.0
        for _ in range(30):
            mid = math.sqrt(lo * hi)
            if halo300(mid, V, rc) / Mb <= up: lo = mid
            else: hi = mid
        res.append(lo)
    P(f"{lab} logMb {lm:5.2f} V {V:5.1f}: 2-sigma limit M_extra/M_b <= {up:.2f} ({up2:.2f} with M_b -0.1 dex); largest m with equilibrium halo below it: {res[1]:.1f} eV (core 2/5/10 kpc: {res[0]:.1f}/{res[1]:.1f}/{res[2]:.1f}); share of cosmic at 12 eV allowed: {up/(12/M_AB_G2):.2f}")
open("m5b_lensing_mmax.out", "w").write("\n".join(out) + "\n")
