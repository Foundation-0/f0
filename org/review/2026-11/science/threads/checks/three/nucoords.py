import numpy as np
from lib3 import *
def xnu(A,nu):
    w=np.stack([np.ones(nu.shape[:-1]),np.exp(nu[...,0]),np.exp(nu[...,1])],-1); w=w/w.sum(-1,keepdims=True)
    return w@A
def Zt(A,nu):
    """log(q2/q1), log(q3/q1) as a function of nu = log(beta2/beta1), log(beta3/beta1)."""
    x=xnu(A,nu); r=np.linalg.norm(x[...,None,:]-A,axis=-1)
    return nu+3*np.stack([np.log(r[...,1]/r[...,0]),np.log(r[...,2]/r[...,0])],-1)
def jac(A,N,h=1e-6):
    J=np.zeros(N.shape[:-1]+(2,2))
    for k in range(2):
        e=np.zeros(2);e[k]=h
        J[...,:,k]=(Zt(A,N+e)-Zt(A,N-e))/(2*h)
    return J
