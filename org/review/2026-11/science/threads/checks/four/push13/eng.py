import numpy as np
from cross_lib import F_J, newton, track, arc_path, param_jac
n,D=4,3
base=np.load("out/mono_n4_D3_s1.npz"); Pb,qb,Sb=base["P"],base["q"],base["S"]
rng=np.random.default_rng(0)
def theta_to_PqC(th):
    P=np.zeros((4,3));P[1,0]=1;P[2,:2]=th[0:2];P[3]=th[2:5]
    return P.astype(complex),np.concatenate([[1.0],np.exp(th[5:])]).astype(complex)
def bc(P,q,B): return np.broadcast_to(P,(B,n,D)),np.broadcast_to(q,(B,n))
def move(Z,Pa,qa,P2,q2,scale=0.3,tries=3,corr_tol=1e-9,hmin=1e-9,h0=0.02,verbose=False):
    for k in range(tries):
        Pm=scale*(rng.normal(size=Pa.shape)+1j*rng.normal(size=Pa.shape))*(np.abs(P2-Pa).max()+1e-3)
        qm=scale*(rng.normal(size=qa.shape)+1j*rng.normal(size=qa.shape))*(np.abs(q2-qa).max()+1e-3)
        Pm[:2]=0;qm[0]=0
        Zt,ok=track(Z,arc_path(Pa,qa,P2,q2,Pm,qm),D,h0=h0,hmin=hmin,corr_tol=corr_tol)
        if not ok.all():
            if verbose: print(" track fail",(~ok).sum()); 
            continue
        Zt,err=newton(Zt,*bc(P2,q2,len(Zt)),D)
        if err.max()>1e-9:
            if verbose: print(" newton err",err.max())
            continue
        dd=np.max(np.abs(Zt[:,None]-Zt[None]),axis=2);np.fill_diagonal(dd,1)
        if dd.min()<1e-6:
            if verbose: print(" collide",dd.min())
            continue
        return Zt
    return None
def classify(Z,tol=1e-9):
    imm=np.max(np.abs(Z.imag),axis=1)/(1+np.max(np.abs(Z.real),axis=1))
    real=imm<tol
    return real,real&np.all(Z[:,D:].real>0,axis=1),imm
