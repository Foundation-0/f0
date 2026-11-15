import sys, numpy as np, mpmath as mp
from try11 import run
nu=[float(a) for a in sys.argv[1].split(',')]; A=[float(a) for a in sys.argv[2].split(',')]; lam=[float(a) for a in sys.argv[3].split(',')]
v,out=run(nu,A,lam,'nu=%s A=%s lam=%s'%(nu,A,lam))
print('config',[mp.nstr(x,20) for x in v])
