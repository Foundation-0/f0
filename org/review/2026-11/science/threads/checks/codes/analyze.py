import json,csv
from fractions import Fraction
tab=json.load(open('table.json'))
rows=[];summary={}
for q in (7,8,9):
    t={tuple(map(int,k.split(','))):v for k,v in tab[str(q)].items()}
    U={c:v[1] for c,v in t.items()}; L={c:v[0] for c,v in t.items()}
    certs={}
    for x in json.load(open(f'certs/gf{q}_certs.json'))['certificates']:
        certs[(x['n'],x['k'])]=x
    direct={c:x['excluded_distance']-1 for c,x in certs.items()}
    def closure(U0):
        U=dict(U0)
        ch=True
        while ch:
            ch=False
            for (n,k) in sorted(U):
                v=U[(n,k)]; cands=[]
                if (n-1,k) in U: cands.append(U[(n-1,k)]+1)
                if (n-1,k-1) in U: cands.append(U[(n-1,k-1)])
                if (n,k-1) in U: cands.append(U[(n,k-1)])
                if (n+1,k) in U: cands.append(U[(n+1,k)])
                m=min(cands+[v])
                if m<v: U[(n,k)]=m; ch=True
        return U
    Ts=closure(U)
    U1=dict(U)
    for c,v in direct.items(): U1[c]=min(U1[c],v)
    Ls=closure(U1)
    stale=sum(1 for c in U if Ts[c]<U[c])
    imp=[c for c in U if Ls[c]<U[c]]
    nb=0
    for c in sorted(imp):
        n,k=c
        # propagation value from neighbours using final L*
        cands=[]
        if (n-1,k) in Ls: cands.append(Ls[(n-1,k)]+1)
        if (n-1,k-1) in Ls: cands.append(Ls[(n-1,k-1)])
        if (n,k-1) in Ls: cands.append(Ls[(n,k-1)])
        if (n+1,k) in Ls: cands.append(Ls[(n+1,k)])
        P=min(cands) if cands else 10**9
        dv=direct.get(c)
        base = dv is not None and dv<=Ls[c] and dv<P   # direct LP strictly better than any neighbour propagation
        nb+=base
        rows.append(dict(q=q,n=n,k=k,lower=L[c],table_upper=U[c],new_upper=Ls[c],kind='base' if base else 'derived',
            direct_lp_upper=dv if dv is not None else '',cert=(f'certs/gf{q}_certs.json#'+certs[c]['id']) if c in certs else '',
            table_self_closure_upper=Ts[c]))
    summary[q]=dict(cells=len(U),gaps=sum(1 for c in U if L[c]<U[c]),certified_direct=len(direct),improved=len(imp),base=nb,derived=len(imp)-nb,
        improved_beyond_table_own_closure=sum(1 for c in imp if Ls[c]<Ts[c]),table_cells_stale_vs_own_closure=stale)
json.dump(summary,open('summary.json','w'),indent=1)
with open('improved_cells.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(json.dumps(summary,indent=1))
