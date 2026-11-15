import numpy as np, time
import finder
from shapes import *
rng=np.random.default_rng(0)
def rep(name,a,q,**kw):
    t=time.time(); r,pts,idx=finder.report(np.array(a,float),np.array(q,float),**kw)
    print(f"{name}: {r} {time.time()-t:.1f}s",flush=True); return r,pts,idx
for nm,f in [("tetra",tetra),("octa",octa),("cube",cube),("ico",ico),("dodeca",dodeca)]:
    a=unit(f()); n=len(a)
    rep(nm,a,np.ones(n))
    rep(nm+" jitter1e-3",a+1e-3*rng.standard_normal(a.shape),1+1e-3*rng.standard_normal(n))
    for qc in (1e-2,1e-4,1e-6):
        rep(nm+f" +centre {qc:g}",np.vstack([a,[[0,0,0]]]),np.r_[np.ones(n),qc])
