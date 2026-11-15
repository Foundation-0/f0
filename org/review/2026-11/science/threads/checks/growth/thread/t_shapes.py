import numpy as np, itertools
from charges_repo import find_fast
def rep(name,a,q):
    a=np.array(a,float); q=np.array(q,float)
    pts,idx,ev=find_fast(a,q,seed=1,rounds=3)
    m1=(idx==1).sum(); m2=(idx==2).sum()
    rc=np.linalg.norm(pts-a.mean(0),axis=1)
    print(f"{name}: n={len(q)} found {len(pts)} m1={m1} m2={m2} m2-m1={m2-m1} (need {len(q)-1}); min|eig| {np.abs(ev).min():.2e}; radii {np.round(np.sort(rc),3)[:12]}")
    return pts,idx
oct_=[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]]
cube=[list(v) for v in itertools.product([-1,1],repeat=3)]
rng=np.random.default_rng(0)
rep("octahedron",oct_,[1]*6)
rep("octahedron jitter 1e-3",np.array(oct_)+1e-3*rng.standard_normal((6,3)),1+1e-3*rng.standard_normal(6))
rep("cube",cube,[1]*8)
rep("cube jitter",np.array(cube)+1e-3*rng.standard_normal((8,3)),1+1e-3*rng.standard_normal(8))
ph=(1+5**.5)/2
ico=[]
for s1 in (-1,1):
  for s2 in (-1,1):
    ico+= [[0,s1,s2*ph],[s1,s2*ph,0],[s2*ph,0,s1]]
rep("icosahedron",ico,[1]*12)
rep("icosahedron jitter",np.array(ico)+1e-3*rng.standard_normal((12,3)),1+1e-3*rng.standard_normal(12))
tet=[[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]]
rep("tetrahedron",tet,[1]*4)
rep("tetra jitter",np.array(tet)+1e-3*rng.standard_normal((4,3)),1+1e-3*rng.standard_normal(4))
