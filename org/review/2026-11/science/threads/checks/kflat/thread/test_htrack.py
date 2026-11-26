import numpy as np, time, htrack as ht, hmodel as hm, polysys as ps
for d in (3,4,6):
    e=d-1; C=np.zeros((d+1,)*3)
    for v in range(3):
        m=[0,0,0]; m[v]=d; C[tuple(m)]=1/d; m[v]=2; C[tuple(m)]=-(v+2)/2
    t=time.time(); r=ht.count(ht.Poly(C)); print("selftest d",d,"real",r['real'],"expected",(3 if e%2 else 2)**3,"idx",r['idx'],f"{time.time()-t:.2f}s")
# icosahedron random unfoldings: success rate
rng=np.random.default_rng(1); d,F=hm.leading("icosahedron"); ok=0; hist={}; t=time.time()
for s in range(40):
    th=[rng.normal(size=n)/np.sqrt(n)*10**rng.uniform(-2,0.5) for n in hm.dims(d)]
    r=ht.count(ht.Poly(hm.model(F,d,th)),seed=s)
    if r: ok+=1; hist[r['real']]=hist.get(r['real'],0)+1; assert r['idx'][2]-r['idx'][1]==11, r['idx']
print("ico ok",ok,"/40", dict(sorted(hist.items())), f"{(time.time()-t)/40:.2f}s each")
