import numpy as np, mpmath as mp, sys
from try11 import *
import localcount, finder
nu=[1e-3,1.2e-3,0.8e-3]; A=[1e-5,1e-5,0,0,0]; lam=[-1.2e-9]*3
v=build([mp.mpf(x) for x in nu],[mp.mpf(x) for x in A],[mp.mpf(x) for x in lam])
P,Q=unpack(v); Pf=np.array([[float(c) for c in p] for p in P]); Qf=np.array([float(q) for q in Q])
print('sites',Pf.round(6).tolist(),'charges',Qf.round(6).tolist())
# 1D scan along each axis of the axial gradient component sign, and full g norm
for ax in range(3):
    for sgn in (1,-1):
        rs=np.geomspace(1e-6,0.05,4000)
        vals=[]
        for r in rs:
            x=np.zeros(3); x[ax]=sgn*r
            g,H=finder.gH(x,Pf,Qf); vals.append(g[ax])
        vals=np.array(vals); ch=np.where(np.sign(vals[1:])!=np.sign(vals[:-1]))[0]
        print('axis',ax,'sign',sgn,'g_axis sign changes at r=',[('%.2e'%rs[i]) for i in ch])
