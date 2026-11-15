import mpmath as mp, numpy as np
from jetsolve import *
v=[mp.mpf(x) for x in TET]; P,Q=unpack(v); cx=cubic_parts(jets(P,Q)[2])[0]
tgt=([0,0,0],[0]*5,[0,0,0],cx)
f=F(v,tgt); h=mp.mpf(10)**-20; J=np.zeros((16,16))
for j in range(16):
    w=list(v); w[j]+=h; fj=F(w,tgt)
    for i in range(16): J[i,j]=float((fj[i]-f[i])/h)
s=np.linalg.svd(J,compute_uv=False); print('singular values',s)
U,S,Vt=np.linalg.svd(J); print('null vector',np.round(Vt[-1],4)); print('left null',np.round(U[:,-1],4))
