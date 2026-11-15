import sys, numpy as np, random
sys.path.insert(0,'.')
from sqlib import *
# cross-check tensor engine vs dense for random specs
random.seed(1)
for trial in range(40):
    k=random.choice([2,3,4]); q=random.choice([2,3,4]); t=random.randrange(0,2*(q-1)+1)
    kinds=set(random.sample("HVDA",random.randint(1,4)))
    rows=all_rows(k,q); N=len(rows)
    cnt=cnt_matrix(rows,rows,k,q,kinds,t)       # cnt[a,b], a above b
    J=2
    v=np.random.randint(0,50,size=(2,J+1,N)).astype(np.int64)
    # right: y[a] = sum_b v[b] eps^cnt(a,b)
    y=contract(v,offsets_right(kinds),q,k,t,J)
    ref=np.zeros_like(v)
    for c in range(J+1):
        Mc=(cnt==c).astype(np.int64)
        for cc in range(J+1-c): ref[:,c+cc]+= v[:,cc]@Mc.T
    ok1=np.array_equal(y,ref)
    y=contract(v,offsets_left(kinds),q,k,t,J)
    ref=np.zeros_like(v)
    for c in range(J+1):
        Mc=(cnt==c).astype(np.int64)
        for cc in range(J+1-c): ref[:,c+cc]+= v[:,cc]@Mc
    ok2=np.array_equal(y,ref)
    print(trial,k,q,t,sorted(kinds),ok1,ok2)
    if not(ok1 and ok2): break
