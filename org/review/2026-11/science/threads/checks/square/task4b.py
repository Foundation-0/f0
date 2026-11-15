import sys, json
sys.path.insert(0,'.')
from task4 import *
from sqlib import parse
from flint import fmpz_poly
for aid in ('A268762','A268770'):
    c=json.load(open(S0+aid+'.json')); sp=parse(c['name']); k,q,kinds,t=sp['k'],sp['q'],sp['kinds'],sp['total']
    g,extra=sqrt_form(charpoly(c['recurrence']['coefficients'])); G=fmpz_poly(g)
    nmax=56; ex=exact_counts(k,q,kinds,t,3,nmax)
    for j in (3,):
        seq=[ex[n][j] for n in range(8,nmax)]
        L,cs=bm(seq)
        poly=fmpz_poly([int(-cs[L-1-i]) for i in range(L)]+[1]); fac=[(str(f),m) for f,m in poly.factor()[1] if str(f)!='x']
        print(aid,'j=3 order',L,'of tail len',len(seq),fac,'target',[(str(f),m*4) for f,m in G.factor()[1] if str(f)!='x'])
