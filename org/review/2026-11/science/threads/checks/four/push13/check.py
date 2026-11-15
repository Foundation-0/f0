import numpy as np, itertools, time
from conv import *
from eng import *
for k,f in FILES.items():
    A,q=load(f)
    for order in [(0,1,2,3),(2,0,1,3),(1,3,0,2)]:
        th,_=to_theta(A,q,order)
        P,qq=theta_to_PqC(th)
        t=time.time()
        res=[]
        for sc,ct,hm in [(0.5,1e-9,1e-9),(0.5,1e-11,1e-12)]:
            Z=move(Sb,Pb,qb,P,qq,scale=sc,tries=6,corr_tol=ct,hmin=hm,h0=0.005)
            if Z is None: res.append(None); continue
            re,ph,imm=classify(Z); res.append((int(re.sum()),int(ph.sum())))
        print(k,order,np.round(th,4),res,f"{time.time()-t:.0f}s",flush=True)
