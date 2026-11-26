import numpy as np, sys
from scipy.optimize import linprog
from push2 import *
d=np.load(sys.argv[1]); Z=d['Z']; p=d['p']
X,Y,real,im2=analyse(Z); reps=pair_reps(Z,real); nr=int(real.sum())
eps=np.abs(p-PU).max(); print('real',2*nr,'eps',eps,'pairs im2',im2[reps])
dX,dY=sensitivities(Z,p_to_P(p))
A,b,dmin=constraints(X,Y,real,dX,dY,0.3,nclose=400)
print('closest real d2', np.sort(b/0.3)[:5])
rng=np.random.default_rng(0)
for r in reps:
    g=2*(X[r].imag[:,None]*dX[r].imag+Y[r].imag[:,None]*dY[r].imag).sum(axis=0)
    print('pair',r,'im2',im2[r],'|g|',np.linalg.norm(g),'lin dist', im2[r]/np.linalg.norm(g))
    for K in (0,1,2,4):
      for tr in (1e-9,1e-8,1e-7,1e-6,1e-5):
        res=linprog(g,A_ub=A[K:],b_ub=b[K:],bounds=[(-tr,tr)]*len(p),method='highs')
        if not res.success: print('  K',K,'tr',tr,'LP infeasible'); continue
        Zq,ok=local_move(Z,p,p+res.x,rng)
        if not ok: print('  K',K,'tr',tr,'move fail'); continue
        Xq,Yq,rq,im2q=analyse(Zq); rp=pair_reps(Zq,rq)
        print(f'  K {K} tr {tr:.0e}: pred dim2 {g@res.x:.2e} real {2*int(rq.sum())} pairs im2 {np.round(im2q[rp],7)}')
