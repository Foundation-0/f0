import json,sys,time
from fractions import Fraction
import numpy as np
from scipy.optimize import linprog
q=int(sys.argv[1]); tab=json.load(open('table.json'))[str(q)]
def kraw(n):
    K=[[1]*(n+1),[n*(q-1)-q*x for x in range(n+1)]]
    for j in range(1,n):
        K.append([((n-j)*(q-1)+j-q*x)*K[j][x]-(q-1)*(n-j+1)*K[j-1][x] for x in range(n+1)])
        K[j+1]=[v//(j+1) for v in K[j+1]]
    return K
cache={}
def Kt(n):
    if n not in cache:
        K=kraw(n); cache[n]=(K,np.array([[K[j][x]/K[j][0] for x in range(n+1)] for j in range(n+1)]))
    return cache[n]
def lp1(n,k,d,s=0.0,deg=None):
    """column-scaled dual: g_j = u_j/c_j, c_j=max_{i>=d}|Kt_j(i)|; min sum g_j s.t. 1+sum g_j Kt_j(i) <= -s, i=d..n.
    Returns (ratio=(1+sum g)/q^k, g) or None."""
    K,A=Kt(n); m=n if deg is None else min(n,deg)
    M=A[1:m+1,d:].T
    c=np.abs(M).max(axis=0); c[c==0]=1
    obj=1/c
    r=linprog(obj,A_ub=M/c,b_ub=-(1+s)*np.ones(n-d+1),bounds=(0,None),method='highs')
    if r.status!=0: return None
    g=np.zeros(n); g[:m]=r.x/c
    return (1+g.sum())/float(q)**k,g

def lp(n,k,d,s=0.0):
    best=None
    for deg in [7,8,9,10,12,14,16,20,24,32,48,n]:
        if deg>n: deg=n
        r=lp1(n,k,d,s,deg)
        if r is not None and r[0]<1-1e-9: return r,deg
        if r is not None and (best is None or r[0]<best[0][0]): best=(r,deg)
        if deg==n: break
    return best
if __name__=="__main__":
    res={};nofeas=0;t0=time.time()
    for key,(lo,up) in tab.items():
        n,k=map(int,key.split(','))
        if lo>=up or up>n: continue
        r=lp(n,k,up)
        if r is None: nofeas+=1; continue
        if r[0][0]>=1-1e-9: res[key]=dict(lo=lo,up=up,dmin=None,ratio=r[0][0],deg=r[1]); continue
        d=up; best=r
        while d-1>lo+0 and d-1<=n:
            r2=lp(n,k,d-1)
            if r2 is not None and r2[0][0]<1-1e-9: d-=1; best=r2
            else: break
        res[key]=dict(lo=lo,up=up,dmin=d,ratio=best[0][0],deg=best[1])
        print('CAND',q,n,k,lo,up,'-> excl from d=',d,'ratio %.4g deg %d'%(best[0][0],best[1]),flush=True)
    json.dump(res,open(f'scan{q}.json','w'))
    print('done cells with feasible float dual',len(res),'no feasible dual found',nofeas,'time',time.time()-t0)
