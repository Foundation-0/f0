import numpy as np, time, stage, hmodel as hm, htrack as ht
rng=np.random.default_rng(3)
for m in (4,5):
  for k in range(3):
    A=hm.harm(m+1,rng.normal(size=2*m+3)); B=hm.harm(m,rng.normal(size=2*m+1))
    t=time.time()
    d=m+1; lows=[(mm,1e-4*c) for mm,c in stage.lowterms(m,d)]
    P=ht.Poly(hm.to_array([A,B]+lows,d)); X,done=ht.solve(P,rng); ok=ht.check(P,X,done)
    r=np.sort(np.abs(X).max(1))
    print(m, ok, "done",done.sum(), "radii quantiles", np.round(r[[0,(m-1)**3-1,(m-1)**3,-1]],4), f"{time.time()-t:.1f}s")
    print("  count:", (lambda c: None if c is None else (c['real'],c['idx']))(stage.count(A,B,m)))
