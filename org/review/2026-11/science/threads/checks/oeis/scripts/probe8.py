import sys; sys.path.insert(0,'.')
import fsm, spec
c = spec.load_cache()
for a in (268627,268636,268748,268763,268771,268778,268909,268976):
    e=c[a]; s=spec.parse_name(e['name']); coef,txt,_st=spec.parse_recurrence(e['formula'])
    m=fsm.build(s); D=len(m['states']); d=len(coef)
    pw=[m['init']]
    for _ in range(d): pw.append(fsm.advance(pw[-1],m['edges']))
    z=[pw[d][i]-sum(coef[l-1]*pw[d-l][i] for l in range(1,d+1)) for i in range(D)]
    sc=[]
    for j in range(D+5):
        sc.append(sum(x for x,ac in zip(z,m['accept']) if ac)); z=fsm.advance(z,m['edges'])
    nz=[j for j,x in enumerate(sc) if x]
    print(a,s['q'],s['k'],s['nbrs'],s['orient'],s['mode'],'D',D,'ord',d,'nonzero residual count',len(nz),'last nonzero j',nz[-1] if nz else None,'first',nz[:3], 'terms in data',len(e['data'].split(',')),flush=True)
    print('   ',txt[:200])
