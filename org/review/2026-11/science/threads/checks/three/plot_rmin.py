import numpy as np, matplotlib, sys; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from lib3 import *
def grid(A,n=600):
    s=(np.arange(n)+0.5)/n
    S,T=np.meshgrid(s,s,indexing='ij')
    m=S+T<1
    X=A[0]+S[...,None]*(A[1]-A[0])+T[...,None]*(A[2]-A[0])
    return X,m
def simp(q): return q[...,1:2]*np.array([1,0])+q[...,2:3]*np.array([0.5,np.sqrt(3)/2])
cases=eval(sys.argv[1]); out=sys.argv[2]
fig,ax=plt.subplots(2,len(cases),figsize=(4*len(cases),8),squeeze=False)
for k,(a,b) in enumerate(cases):
    A=sites(a,b); X,m=grid(A)
    M=np.where(m,mu(A,X),np.nan)
    ax[0,k].contourf(X[...,0],X[...,1],M,levels=[-0.5,0,0.5],colors=['#ddd','#c33'])
    cs=ax[0,k].contour(X[...,0],X[...,1],M,levels=[0],colors='k')
    ax[0,k].plot(*np.r_[A,A[:1]].T,'b-'); ax[0,k].set_aspect('equal'); ax[0,k].set_title(f'a={a} b={b}')
    q=lami(A,X)[0]; P2=simp(q); sel=m&(M>0)
    ax[1,k].plot(P2[sel][:,0],P2[sel][:,1],',',color='r',alpha=0.3)
    for seg in cs.allsegs[0]:
        pp=simp(lami(A,seg)[0]); ax[1,k].plot(pp[:,0],pp[:,1],'k-',lw=0.6)
    ax[1,k].plot([0,1,0.5,0],[0,0,np.sqrt(3)/2,0],'b-'); ax[1,k].set_aspect('equal')
plt.tight_layout(); plt.savefig(out,dpi=70)
