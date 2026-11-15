import numpy as np
from scipy.optimize import linprog
from lib3 import *
def Zlog(A,X):
    q=lami(A,X)[0]; return np.log(q[...,1:]/q[...,:1])
def Zlin(A,X):
    q=lami(A,X)[0]; return q[...,1:]
def jacx(f,A,X,h=1e-7):
    J=np.zeros(X.shape[:-1]+(2,2))
    for k in range(2):
        e=np.zeros(2);e[k]=h
        J[...,:,k]=(f(A,X+e)-f(A,X-e))/(2*h)
    return J
def best_P(Js,nv=72):
    th=np.linspace(0,np.pi,nv,endpoint=False); V=np.c_[np.cos(th),np.sin(th)]
    # constraint: v^T P J v >= t ; variables p11,p12,p21,p22,t ; maximize t ; normalise |p|_inf<=1
    rows=[]
    for J in Js:
        Jv=V@J.T  # (nv,2) = J v
        # v^T P w = sum_ab v_a P_ab w_b
        coef=np.stack([V[:,0]*Jv[:,0],V[:,0]*Jv[:,1],V[:,1]*Jv[:,0],V[:,1]*Jv[:,1]],1)
        rows.append(coef)
    C=np.vstack(rows)
    Aub=np.c_[-C,np.ones(len(C))]; bub=np.zeros(len(C))
    res=linprog(c=[0,0,0,0,-1],A_ub=Aub,b_ub=bub,bounds=[(-1,1)]*4+[(None,1)],method='highs')
    return res.x[:4].reshape(2,2), res.x[4]
if __name__=='__main__':
    for (a,b) in [(0.5,0.866),(0.0,1.0),(0.5,0.1),(1.5,0.5),(0.9,0.2),(0.3,2.0)]:
        A=sites(a,b)
        n=500; s=(np.arange(n)+0.5)/n; S,T=np.meshgrid(s,s,indexing='ij'); m=S+T<1
        X=(A[0]+S[...,None]*(A[1]-A[0])+T[...,None]*(A[2]-A[0]))[m]
        M=mu(A,X); sel=M>0
        for name,f in [('log',Zlog),('lin',Zlin)]:
            J=jacx(f,A,X[sel])
            # normalise each J to unit norm to keep LP well scaled
            Jn=J/np.linalg.norm(J,axis=(1,2))[:,None,None]
            P_,t=best_P(Jn[::max(1,len(Jn)//400)])
            vals=[]
            th=np.linspace(0,np.pi,360); V=np.c_[np.cos(th),np.sin(th)]
            mn=np.einsum('va,ab,kbc,vc->kv',V,P_,Jn,V).min()
            print(a,b,name,'LP margin %.4g  check min over all %.4g'%(t,mn))
