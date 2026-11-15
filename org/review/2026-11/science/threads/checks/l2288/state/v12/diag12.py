import numpy as np, sys
from scipy.optimize import linprog
import push12 as P
d=np.load(sys.argv[1]); Z=d['Z']; p=d['p']
X,Y,real,im2=P.analyse(Z); nr=int(real.sum()); reps=P.pair_reps(Z,real); order=reps[np.argsort(im2[reps])]
eps=np.abs(p-1).max(); dX,dY=P.sensitivities(Z,p)
A,b,dmin=P.constraints(X,Y,real,dX,dY,0.3)
print('real',nr,'pairs',len(reps),'eps',eps,'smallest im2',np.round(im2[order[:8]],5),'closest d2',np.sort(b/0.3)[:5])
grads={r:2*(X[r].imag[:,None]*dX[r].imag+Y[r].imag[:,None]*dY[r].imag).sum(axis=0) for r in order[:60]}
for r in order[:6]:
    g=grads[r]; print(' pair im2 %.2e |g| %.2e lin dist %.2e'%(im2[r],np.linalg.norm(g),im2[r]/np.linalg.norm(g)))
c=sum(grads[r]/im2[r] for r in order[:30])
rng=np.random.default_rng(0)
for tr in [1e-2*eps,1e-3*eps,1e-4*eps]:
    for useA in (True,False):
        res=linprog(c,A_ub=A if useA else None,b_ub=b if useA else None,bounds=[(-tr,tr)]*len(p),method='highs')
        if not res.success: print(tr,useA,'infeasible'); continue
        Zn,ok=P.local_move(Z,p,p+res.x,rng)
        if not ok: print(tr,useA,'move fail'); continue
        Xn,Yn,rn,im2n=P.analyse(Zn); rp=P.pair_reps(Zn,rn)
        print('tr %.1e A %s: real %d, pred dobj %.2e, actual dobj %.2e, smallest im2 %s'%(tr,useA,rn.sum(),c@res.x,np.log(im2n[rp]).sum()-np.log(im2[reps]).sum(),np.round(np.sort(im2n[rp])[:4],5)))
