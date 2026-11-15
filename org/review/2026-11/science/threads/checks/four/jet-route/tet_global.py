import numpy as np, finder
P=np.array([(1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1)],float); Q=np.ones(4)
res=finder.find_all(P,Q,nstart=20000,seed=1,dedup=1e-4)
for r,ev in res: print(np.round(r,6),ev)
print(len(res))
far=[(r,ev) for r,ev in res if np.linalg.norm(r)>0.02]
print('away from centre:',len(far))
for r,ev in far: print(r,ev)
