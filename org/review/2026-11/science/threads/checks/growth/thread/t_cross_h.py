import numpy as np
from harm import Poly, solve_all
from level import zonal, emb
from t_cross_util import rotate_zx, crossings
rng=np.random.default_rng(1)
for p in range(3,10):
    cA=zonal(p); cA/=np.abs(cA).max(); cB=rotate_zx(zonal(p-1),p-1); cB/=np.abs(cB).max()
    P=Poly(cA+emb(cB,p-1,p),p); best=None
    for rep in range(3):
        s,lost=solve_all(P,rng,steps0=400)
        s=s[np.linalg.norm(s,axis=1)>1e-3]; r=np.abs(s.imag).max(1)<1e-7*np.abs(s).max(1)
        a,b=p-1,p-2
        if best is None or len(s)>best[0]: best=(len(s),r.sum())
    print(f"p={p}: homotopy nonzero finite {best[0]} of {a*a+a*b+b*b}, real {best[1]}, I-1 = {crossings(p)-1}",flush=True)
