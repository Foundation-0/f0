import numpy as np
from harm import Poly, solve_all
from level import *
rng=np.random.default_rng(3)
for p in range(3,9):
  for nm,cA,cB,forced in [("sect/zon",sectoral(p),zonal(p-1),p*(p-2)),("zon/sect",zonal(p),sectoral(p-1),(p-1)**2)]:
    cA2=cA+1e-3*np.abs(cA).max()*(basis_h(p)@rng.standard_normal(2*p+1)); cB2=cB+1e-3*np.abs(cB).max()*(basis_h(p-1)@rng.standard_normal(2*p-1))
    P=Poly(cA2+emb(cB2,p-1,p),p); s,lost=solve_all(P,rng)
    s=s[np.linalg.norm(s,axis=1)>1e-4]; r=np.abs(s.imag).max(1)<1e-7*np.abs(s).max(1)
    a,b=p-1,p-2
    print(f"p={p} {nm}: homotopy nonzero {len(s)} (expect {a*a+a*b+b*b}), real {r.sum()}, forced {forced}, max|x| real {np.abs(s[r]).max():.3g}",flush=True)
