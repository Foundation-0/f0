import numpy as np, time, htrack as ht, hmodel as hm
rng=np.random.default_rng(1); d,F=hm.leading("icosahedron")
th=[rng.normal(size=n)/np.sqrt(n)*0.3 for n in hm.dims(d)]
P0=ht.Poly(hm.model(F,d,th)); t=time.time(); X0=ht.roots(P0); print("total degree", f"{time.time()-t:.2f}s")
for k in range(4):
    th2=[a+0.05*rng.normal(size=a.shape) for a in th]; P1=ht.Poly(hm.model(F,d,th2))
    t=time.time(); X1,done=ht.solve(P1,rng,start=(P0,X0),h0=0.1); ok=ht.check(P1,X1,done); t1=time.time()-t
    t=time.time(); Xr=ht.roots(P1); t2=time.time()-t
    same = np.abs(X1[:,None]-Xr[None]).max(-1).min(1).max()
    print("param", ok, f"{t1:.2f}s vs total {t2:.2f}s; max diff {same:.1e}")
