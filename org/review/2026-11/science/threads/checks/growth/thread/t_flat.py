import numpy as np, time
from flatsolve import *
from shapes import *
print("octa d=4", np.abs(eqs(octa(),np.zeros(6),4)).max(), " d=5", np.abs(eqs(octa(),np.zeros(6),5)).max())
print("ico d=6", np.abs(eqs(unit(ico()),np.zeros(12),6)).max(), " d=7", np.abs(eqs(unit(ico()),np.zeros(12),7)).max())
for n,d in [(5,4),(6,4),(7,4),(7,5),(8,5),(9,5),(10,5),(10,6),(11,6)]:
    rng=np.random.default_rng(1); t=time.time(); hits=0; tries=0
    while tries<40 and hits<3:
        tries+=1
        r=solve(n,d,rng)
        if r is not None:
            hits+=1; a,q=r
            print(f"n={n} d={d} try {tries}: q={np.round(q,3)} radii={np.round(np.linalg.norm(a,axis=1),3)}",flush=True)
    print(f"n={n} d={d}: {hits} solutions in {tries} tries, {time.time()-t:.0f}s",flush=True)
