"""Task C: balance points against n for families (numerical, finder.py with both Morse checks)."""
import numpy as np, itertools, sys, time
import finder
from shapes import *
rng=np.random.default_rng(2026)
def run(name,a,q):
    t=time.time(); r,_,_=finder.report(np.asarray(a,float),np.asarray(q,float),rounds=2)
    print(f"{name}\tn={r['n']}\ttotal={r['total']}\tm1={r['m1']}\tm2={r['m2']}\tM1={r['M1']}\tM2={r['M2']}\tpairs={r.get('pairs')}\t{time.time()-t:.0f}s",flush=True)
fam=sys.argv[1]
if fam=="random":
    for n in (5,10,15,20,30,40):
        for trial in range(3):
            run(f"random-equal",rng.standard_normal((n,3)),np.ones(n))
            run(f"random-unequal",rng.standard_normal((n,3)),10**rng.uniform(-3,0,n))
if fam=="lattice":
    for L in (2,3):
        sc=np.array(list(itertools.product(range(L),repeat=3)),float); run(f"sc-{L}",sc+1e-4*rng.standard_normal(sc.shape),np.ones(len(sc)))
        bcc=np.vstack([sc,sc[np.all(sc<L-1,1)]+0.5]); run(f"bcc-{L}",bcc+1e-4*rng.standard_normal(bcc.shape),np.ones(len(bcc)))
        fcc=np.vstack([sc]+[sc+np.array(v) for v in ([0.5,0.5,0],[0.5,0,0.5],[0,0.5,0.5])]); fcc=fcc[np.all(fcc<=L-1,1)]
        run(f"fcc-{L}",fcc+1e-4*rng.standard_normal(fcc.shape),np.ones(len(fcc)))
if fam=="chain":
    for n in (5,10,20,40):
        x=np.c_[np.arange(n),np.zeros(n),np.zeros(n)]; run("chain",x+1e-3*rng.standard_normal(x.shape),np.ones(n))
        th=2*np.pi*np.arange(n)/n; ring=np.c_[np.cos(th),np.sin(th),np.zeros(n)]; run("ring",ring+1e-3*rng.standard_normal(ring.shape),np.ones(n))
        run("ring+centre",np.vstack([ring+1e-3*rng.standard_normal(ring.shape),[[0,0,0]]]),np.r_[np.ones(n),1e-3])
if fam=="shells":
    for nm,f in [("octa",octa),("cube",cube),("ico",ico),("dodeca",dodeca)]:
        a=unit(f())
        for ratio in (0.3,0.1):
            for qr in (1e-2,1e-4):
                for dual in (False,True):
                    b=a.copy()
                    if dual: b=b@np.array([[0,1,0],[-1,0,0],[0,0,1]]).T@np.array([[1,0,0],[0,np.cos(.3),-np.sin(.3)],[0,np.sin(.3),np.cos(.3)]]).T
                    run(f"{nm} nested ratio={ratio} q={qr} rotated={dual}",np.vstack([a,ratio*b])+1e-6*rng.standard_normal((2*len(a),3)),np.r_[np.ones(len(a)),qr*np.ones(len(a))])
