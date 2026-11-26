"""Task 6: random relative perturbations, counted with width.py's method (count function copied verbatim, with
fixed per-call rng stream). Usage: rand_perturb.py name cfg indep N"""
import json, sys, numpy as np, collections
from fractions import Fraction
name,cfgf,indf,N=sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4])
cfg=json.load(open(cfgf)); res=json.load(open(indf))
A0=np.array([[float(Fraction(c)) for c in s] for s in cfg["sites"]]); q0=np.array([float(Fraction(c)) for c in cfg["charges"]])
Z=np.array([z["centre_float"] for z in res["zeros"]]); 
inner_c=Z[np.argsort(np.linalg.norm(Z-np.median(Z,axis=0),axis=1))[:8]].mean(0)
rng=np.random.default_rng(3)
def gH(X,A,q):
    D=X[:,None,:]-A[None];r2=(D*D).sum(-1);r=np.sqrt(r2)
    g=-(q[None,:,None]*D/(r2*r)[...,None]).sum(1)
    H=(q[None,:,None,None]*(3*D[...,:,None]*D[...,None,:]-r2[...,None,None]*np.eye(3))/(r2*r2*r)[...,None,None]).sum(1)
    return g,H
def count(A,q):
    R=np.linalg.norm(A.max(0)-A.min(0))
    X=np.vstack([Z,inner_c+rng.normal(size=(6000,3))*R*10**rng.uniform(-5,-0.3,size=(6000,1)),rng.uniform(A.min(0),A.max(0),size=(3000,3))])
    with np.errstate(all="ignore"):
        for it in range(90):
            g,H=gH(X,A,q);d=np.linalg.solve(H,g[...,None])[...,0]
            s=np.linalg.norm(d,axis=1);d*=np.minimum(1.0,0.03*R/np.maximum(s,1e-300))[:,None];X=X-d
        g,H=gH(X,A,q)
    ok=np.isfinite(X).all(1)&(np.linalg.norm(g,axis=1)<1e-10*q.sum()/R**2)&(X>=A.min(0)).all(1)&(X<=A.max(0)).all(1)
    pts=[]
    for x,h in zip(X[ok],H[ok]):
        if all(np.linalg.norm(x-p[0])>1e-9*R for p in pts): pts.append((x,int((np.linalg.eigvalsh(h)<0).sum())))
    m2=sum(1 for p in pts if p[1]==2);m1=sum(1 for p in pts if p[1]==1)
    return len(pts) if m2-m1==3 and m1+m2==len(pts) else -1
print(name,"unperturbed",count(A0,q0),flush=True)
import os
for size in [float(os.environ["SIZE"])]:
    rng=np.random.default_rng(int(1e9*size)%1000+5)
    c=collections.Counter()
    for k in range(N):
        c[count(A0*(1+size*rng.normal(size=A0.shape)),q0*(1+size*rng.normal(size=4)))]+=1
        if (k+1)%250==0: print(name,"size %.0e"%size,k+1,dict(sorted(c.items())),flush=True)
    print(name,"size %.0e"%size,dict(sorted(c.items())),"max>11:",any(k>11 for k in c),flush=True)
