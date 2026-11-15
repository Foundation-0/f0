import numpy as np, itertools
ph=(1+5**.5)/2
def octa(): return np.array([[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]],float)
def cube(): return np.array(list(itertools.product([-1,1],repeat=3)),float)
def tetra(): return np.array([[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]],float)
def ico():
    v=[]
    for s1 in (-1,1):
        for s2 in (-1,1):
            v+=[[0,s1,s2*ph],[s1,s2*ph,0],[s2*ph,0,s1]]
    return np.array(v,float)
def dodeca():
    v=list(itertools.product([-1,1],repeat=3))
    for s1 in (-1,1):
        for s2 in (-1,1):
            v+=[[0,s1/ph,s2*ph],[s1/ph,s2*ph,0],[s2*ph,0,s1/ph]]
    return np.array(v,float)
def sq_antiprism(h):
    v=[[np.cos(k*np.pi/2),np.sin(k*np.pi/2),h] for k in range(4)]+[[np.cos(k*np.pi/2+np.pi/4),np.sin(k*np.pi/2+np.pi/4),-h] for k in range(4)]
    return np.array(v,float)
def unit(v): return v/np.linalg.norm(v,axis=1)[:,None]
