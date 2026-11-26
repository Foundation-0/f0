"""Hill-climb real nonzero critical points of A+B (one level). Counting by total-degree homotopy.
usage: level_climb.py p seed iters [fixA: ico6|none]"""
import numpy as np, sys, time
from harm import Poly, solve_all, monos
from level import emb, basis_h, zonal, sectoral
p=int(sys.argv[1]); seed=int(sys.argv[2]); iters=int(sys.argv[3]); fix=sys.argv[4] if len(sys.argv)>4 else 'none'
rng=np.random.default_rng(seed)
BA=basis_h(p); BB=basis_h(p-1)
a,b=p-1,p-2; NC=a*a+a*b+b*b
if fix=='ico6':
    from shapes import ico, unit; from flatsolve import top_poly
    cA=top_poly(unit(ico()),np.ones(12),6); cA=cA/np.abs(cA).max(); L6,_=monos(6)
    xA=np.linalg.lstsq(BA,cA[:len(BA)] if False else cA,rcond=None)[0]
else:
    xA=np.linalg.lstsq(BA,zonal(p),rcond=None)[0]
xB=np.linalg.lstsq(BB,sectoral(p-1),rcond=None)[0]
xA=xA/np.linalg.norm(xA); xB=xB/np.linalg.norm(xB)
def cnt(xA,xB):
    c=BA@xA+emb(BB@xB,p-1,p); P=Poly(c,p)
    s,lost=solve_all(P,rng)
    nz=np.linalg.norm(s,axis=1)>1e-4
    s=s[nz]
    r=np.abs(s.imag).max(1)<1e-7*np.abs(s).max(1)
    return int(r.sum()), len(s)
cur,nc=cnt(xA,xB); print(f"p={p} fix={fix} start real {cur} of {nc} nonzero found (expected {NC})",flush=True)
best=cur; t=time.time()
for it in range(iters):
    sc=0.15*rng.random()
    nA=xA if fix=='ico6' else xA+sc*rng.standard_normal(len(xA)); nB=xB+sc*rng.standard_normal(len(xB))
    nA/=np.linalg.norm(nA); nB/=np.linalg.norm(nB)
    k,nc=cnt(nA,nB)
    if nc>=NC-2 and k>=cur:
        if k>cur: print(f"  it {it}: real {k} of {nc}",flush=True)
        xA,xB,cur=nA,nB,k
print(f"p={p} fix={fix} seed={seed}: best {cur} of {NC}; {time.time()-t:.0f}s",flush=True)
np.save(f"out/level_p{p}_{fix}_s{seed}.npy",np.r_[cur,xA,xB])
