"""Second exact check: Krawtchouk by the binomial sum K_j(x)=sum_r (-1)^r (q-1)^(j-r) C(x,r) C(n-x,j-r)
(different formula from the recurrence in verify_certs.py).  Fractions/ints only; SystemExit on failure.
Usage: python3 -I -O verify_binomial.py cert.json ..."""
import json,sys
from fractions import Fraction
from math import comb
def K(q,n,j,x): return sum((-1)**r*(q-1)**(j-r)*comb(x,r)*comb(n-x,j-r) for r in range(j+1))
tot=0
for p in sys.argv[1:]:
    for c in json.load(open(p))["certificates"]:
        q,n,k,d=c["q"],c["n"],c["k"],c["excluded_distance"]
        a=[Fraction(v) for v in c["krawtchouk_coefficients"]]
        if not a[0]>0 or any(v<0 for v in a): raise SystemExit(c["id"]+": sign")
        f=lambda x: sum(a[j]*K(q,n,j,x) for j in range(len(a)))
        if any(f(i)>0 for i in range(d,n+1)): raise SystemExit(c["id"]+": f>0 on [d,n]")
        if not f(0)/a[0]<q**k: raise SystemExit(c["id"]+": bound not below q^k")
        tot+=1
print(tot,"certificates pass the binomial-sum exact check")
