import numpy as np, time
from level2d import *
rng=np.random.default_rng(7)
for eps in (1e-6,1e-10):
  for p in range(3,10):
    for nm,cA,cB in [("zon/sect",zonal(p),sectoral(p-1)),("sect/zon",sectoral(p),zonal(p-1))]:
      cA2=cA/np.abs(cA).max()+eps*(basis_h(p)@rng.standard_normal(2*p+1)); cB2=cB/np.abs(cB).max()+eps*(basis_h(p-1)@rng.standard_normal(2*p-1))
      X=dedup_pts(crit_level(cA2,cB2,p,ngrid=3000000))
      r=np.linalg.norm(X,axis=1)
      print(f"eps={eps:g} p={p} {nm}: real {len(X)}; p(p-1)-1={p*(p-1)-1}; complex {(p-1)**2+(p-1)*(p-2)+(p-2)**2}; radii {r.min():.1e}..{r.max():.1e}",flush=True)
