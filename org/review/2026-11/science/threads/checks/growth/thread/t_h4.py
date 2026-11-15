import numpy as np, time
from harm import *
d=4
L,ix=monos(d)
c=np.zeros(len(L))
for a in range(3):
    m=[0,0,0]; m[a]=4; c[ix[tuple(m)]]+=1
# -(3/5) r^4
for (i,j,k),coef in {(4,0,0):1,(0,4,0):1,(0,0,4):1,(2,2,0):2,(2,0,2):2,(0,2,2):2}.items():
    c[ix[(i,j,k)]]-=0.6*coef
print("lap", np.abs(lap_mat(d)@c).max())
B=np.hstack([harmonic_basis(d,l) for l in (1,2,3)])
rng=np.random.default_rng(1)
P=Poly(c+B@(0.3*rng.standard_normal(B.shape[1])),d)
t=time.time(); s,lost=solve_all(P); print("complex",len(s),"lost",lost,time.time()-t)
R,idx,me=real_crit(P,s); print("real",len(R),idx)
best=0
for trial in range(200):
    h=rng.standard_normal(B.shape[1])*rng.choice([0.1,0.3,1,3])
    P=Poly(c+B@h,d); s,lost=solve_all(P,rng)
    R,idx,me=real_crit(P,s)
    if len(R)>best: best=len(R); print(trial,len(s),lost,len(R),(idx==1).sum(),(idx==2).sum())
