import json, sys, time, numpy as np
from fractions import Fraction as Fr
import finder
R='../../../repos/point-charges/certificates/'
C='../../charges/configs/'
files=[R+'n3-triangle.json',R+'n4-triangle-plus-centre.json',R+'n5-abk-bipyramid.json',R+'n6-abk-plus-centre.json',R+'n7-abk-second-pair.json',C+'n8.json',C+'n9.json']
expect=[4,9,24,29,44,49,64]
def load(f):
    d=json.load(open(f))
    sites=d.get('sites') or d['config']['sites']; ch=d.get('charges') or d['config']['charges']
    a=np.array([[float(Fr(c)) for c in s] for s in sites]); q=np.array([float(Fr(c)) for c in ch])
    return a,q
for f,e in zip(files,expect):
    a,q=load(f)
    c=a[:3].mean(0); a=a-c   # centre the nesting point at the origin (exact shift for these configs)
    t=time.time(); r,pts,idx=finder.report(a,q,seed=0)
    print(f.split('/')[-1], 'expect',e, r, f"{time.time()-t:.1f}s", flush=True)
