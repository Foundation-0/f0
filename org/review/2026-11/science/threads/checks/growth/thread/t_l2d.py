import numpy as np, time
from level2d import *
from level import count_level
rng=np.random.default_rng(11)
for p in range(3,12):
  for nm,cA,cB,forced in [("zon/sect",zonal(p),sectoral(p-1),(p-1)**2),("sect/zon",sectoral(p),zonal(p-1),p*(p-2))]:
    cA2=cA/np.abs(cA).max(); cB2=cB/np.abs(cB).max()
    cA2=cA2+1e-3*(basis_h(p)@rng.standard_normal(2*p+1)); cB2=cB2+1e-3*(basis_h(p-1)@rng.standard_normal(2*p-1))
    t=time.time(); X=dedup_pts(crit_level(cA2,cB2,p)); 
    X2=dedup_pts(crit_level(cA2,cB2,p,ngrid=1600000))
    a,b=p-1,p-2
    print(f"p={p} {nm}: real {len(X)} (finer grid {len(X2)}), forced {forced}, complex {a*a+a*b+b*b}, radii {np.linalg.norm(X2,axis=1).min():.2g}..{np.linalg.norm(X2,axis=1).max():.2g}  {time.time()-t:.0f}s",flush=True)
