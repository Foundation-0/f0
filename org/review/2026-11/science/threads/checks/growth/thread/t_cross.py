import numpy as np, time
from level2d import *
from harm import monos
from numpy.polynomial import legendre
def rotate_zx(c,p):
    """zonal about z -> zonal about x: substitute (x,y,z)->(z,y,x)... (swap x and z)"""
    L,ix=monos(p); out=np.zeros(len(L))
    for k,(i,j,l) in enumerate(L): out[ix[(l,j,i)]]=c[k]
    return out
def crossings(p):
    # pairs (a,b) of zeros of P_p, P_{p-1} with a^2+b^2<1: each gives 2 points on S^2 -> 1 on RP^2? (x,y,z) and (x,-y,z): distinct on RP^2 unless...
    za=legendre.Legendre.basis(p).roots(); zb=legendre.Legendre.basis(p-1).roots()
    n=sum(1 for a in za for b in zb if a*a+b*b<1)
    return n  # points on S^2 = 2n; on RP^2 = n
rng=np.random.default_rng(5)
for p in range(3,15):
    cA=zonal(p); cB=rotate_zx(zonal(p-1),p-1)
    cA/=np.abs(cA).max(); cB/=np.abs(cB).max()
    cA2=cA+1e-4*(basis_h(p)@rng.standard_normal(2*p+1)); cB2=cB+1e-4*(basis_h(p-1)@rng.standard_normal(2*p-1))
    t=time.time(); X=dedup_pts(crit_level(cA2,cB2,p,ngrid=1600000))
    I=crossings(p); a,b=p-1,p-2
    r=np.linalg.norm(X,axis=1)
    print(f"p={p} crossed zonal: real {len(X)}, crossings on RP2 {I} (lower bound I-1={I-1}), complex {a*a+a*b+b*b}, ratio real/complex {len(X)/(a*a+a*b+b*b):.2f}, radii {r.min():.2g}..{r.max():.2g} {time.time()-t:.0f}s",flush=True)
