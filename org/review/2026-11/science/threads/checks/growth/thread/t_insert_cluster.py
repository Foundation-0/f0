"""Task D: local model at an O_h flat point (outer cube: top -K4; outer octahedron: +K4) with a small O_h cluster
(octahedron of 6 or cube of 8) of total charge Q at radius 1. Count critical points away from the origin.
F(Y) = sgn*K4(Y) + lam * sum 1/|Y - b_j|. Gain per level = count (origin stays an O_h flat point)."""
import numpy as np
from localmodel import Local, K4
from shapes import octa, cube, unit
c,d=K4(); rng=np.random.default_rng(0)
for outer,sg in [("outer cube",-1),("outer octa",+1)]:
    for nm,b in [("oct",octa()),("cube",unit(cube()))]:
        best=(0,None)
        for lam in np.geomspace(1e-3,1e2,26):
            M=Local(sg*c,d,b,lam*np.ones(len(b)))
            pts,idx,ev,cen=M.find(rng,Rmax=4,ngrid=3000)
            k=len(pts)
            if k>best[0]: best=(k,lam,(idx==1).sum(),(idx==2).sum())
        print(f"{outer} + small {nm} ({len(b)} charges): best local count {best[0]} at lam={best[1]:.3g} (index1 {best[2]}, index2 {best[3]}); per charge {best[0]/len(b):.2f}",flush=True)
