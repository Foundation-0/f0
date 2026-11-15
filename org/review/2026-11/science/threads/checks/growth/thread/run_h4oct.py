import numpy as np
from harm import *; from opt_local import climb
d=4; L,ix=monos(d); c=np.zeros(len(L))
for (i,j,k),coef in {(4,0,0):1,(0,4,0):1,(0,0,4):1}.items(): c[ix[(i,j,k)]]+=coef
for (i,j,k),coef in {(4,0,0):1,(0,4,0):1,(0,0,4):1,(2,2,0):2,(2,0,2):2,(0,2,2):2}.items(): c[ix[(i,j,k)]]-=0.6*coef
for s in range(4):
    rng=np.random.default_rng(100+s)
    b=climb(c,d,(1,2,3),rng,iters=1500)
    print("seed",s,"best real",b[0],"of",b[3], flush=True)
