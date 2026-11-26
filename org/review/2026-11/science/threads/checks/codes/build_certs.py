import sys,json,os
from fractions import Fraction
q=int(sys.argv[1]); sys.argv=['x',str(q)]
import scan2
from scan2 import lp1,Kt
import verify_certs as V
scan=json.load(open(f'scan{q}.json'))
certs=[];failed=[]
for key,r in scan.items():
    if r['dmin'] is None: continue
    n,k=map(int,key.split(',')); d=r['dmin']; ok=False
    K=Kt(n)[0]
    for deg in [r['deg'],n]:
      for s in [0,1e-9,1e-7,1e-5,1e-3,1e-2,0.1]:
        out=lp1(n,k,d,s,deg)
        if out is None: continue
        g=out[1]
        a=[Fraction(1)]+[Fraction(float(g[j-1]))/K[j][0] for j in range(1,n+1)]
        while len(a)>1 and a[-1]==0: a.pop()
        f0=sum(a[j]*K[j][0] for j in range(len(a)))
        c=dict(id=f'gf{q}-n{n}-k{k}-exclude-d{d}',q=q,n=n,k=k,excluded_distance=d,
               krawtchouk_coefficients=[str(v) for v in a],size_bound=str(f0/a[0]))
        try: V.check(c); ok=True; break
        except SystemExit: continue
      if ok: break
    if ok: certs.append(c)
    else: failed.append(key)
os.makedirs('certs',exist_ok=True)
json.dump(dict(format_version=1,certificates=certs),open(f'certs/gf{q}_certs.json','w'))
json.dump(failed,open(f'certs/gf{q}_uncertified.json','w'))
print(q,'certified',len(certs),'float candidates not certified',len(failed),failed[:30])
