"""R(d): hill-climb the number of real critical points of H_d + h over harmonic h of degree < d.
Top H_d: 'random' (Gaussian harmonic) or a named symmetric top. Numerical exploration."""
import numpy as np, sys, time
from harm import *
from opt_local import climb
d=int(sys.argv[1]); seed=int(sys.argv[2]); iters=int(sys.argv[3]); top=sys.argv[4] if len(sys.argv)>4 else 'random'
rng=np.random.default_rng(seed)
L,ix=monos(d)
if top=='random':
    c=harmonic_basis(d,d)@rng.standard_normal(2*d+1)
elif top=='K4':
    from localmodel import K4; c,_=K4()
P=Poly(c+np.hstack([harmonic_basis(d,l) for l in range(1,d)])@(0.1*rng.standard_normal(d*d-1)),d)
s,lost=solve_all(P,rng); print(f"d={d} top={top} seed={seed}: complex finite {len(s)} lost {lost} (Bezout {(d-1)**3})",flush=True)
t=time.time()
b=climb(c,d,tuple(range(1,d)),rng,iters=iters)
print(f"d={d} top={top} seed={seed}: best real {b[0]} of {b[3]} complex; index1 {(b[2]==1).sum()} index2 {(b[2]==2).sum()}; {time.time()-t:.0f}s",flush=True)
np.save(f"out/Rd_d{d}_{top}_s{seed}.npy",np.r_[b[0],c,b[1]])
