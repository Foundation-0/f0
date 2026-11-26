import numpy as np
from scipy.optimize import least_squares
from scipy.integrate import solve_ivp

rng = np.random.default_rng(7)

# ---------- 1) flat-point hunt: minimize |grad|^2+|Hess|^2 at origin over sites+charges ----------
def flat_resid(p, n):
    # residuals divided by total weight A, plus a term fixing the geometric-mean
    # radius at 1; without both, shrinking or expanding all radii fakes a zero
    s = p[:3*n].reshape(n,3); q = np.exp(p[3*n:])  # positive charges
    r = np.linalg.norm(s,axis=1); a = q/r**3; u = s/r[:,None]; A = a.sum()
    g = (a[:,None]*s).sum(0)/A
    H = (a[:,None,None]*(3*u[:,:,None]*u[:,None,:]-np.eye(3))).sum(0)/A
    return np.concatenate([g, H[np.triu_indices(3)], [np.log(r).mean()]])

for n in (3,4):
    best=1e9
    for t in range(80):
        p0 = np.concatenate([rng.normal(size=3*n), rng.normal(scale=.5,size=n)])
        sol = least_squares(flat_resid, p0, args=(n,), method="trf", max_nfev=4000)
        best = min(best, np.linalg.norm(sol.fun[:-1]))
    print(f"flat hunt n={n}: best flat residual with mean radius fixed, 80 starts = {best:.3e}")

# ---------- 2) wall graph of the printed 5-decimal 11-configuration ----------
cfg_q = np.array([0.26712,0.28010,1.0,0.26274])
cfg_s = np.array([[-0.35180,-0.27373,-0.20165],[-0.05642,0.44608,-0.21436],
                  [-0.00274,0.00705,0.84585],[0.40862,-0.17404,-0.19749]])
seeds = [((-0.00021,0.00022,0.00155),2),((-0.00540,0.00212,-0.00514),2),
         ((0.00014,-0.00055,-0.00251),1),((0.00583,-0.00243,0.00455),1),
         ((0.00041,-0.00328,-0.00342),2),((0.01945,-0.00805,0.01529),2),
         ((0.00395,0.00287,-0.00454),2),((-0.01747,-0.01312,0.01561),2),
         ((-0.00487,-0.00360,0.00427),1),((-0.00307,0.02304,0.01606),2),
         ((-0.00088,0.00615,0.00431),1)]

def gradU(p):
    d = p-cfg_s; r = np.linalg.norm(d,axis=1)
    return -(cfg_q[:,None]*d/r[:,None]**3).sum(0)
def hessU(p):
    d = p-cfg_s; r = np.linalg.norm(d,axis=1)
    return (cfg_q[:,None,None]*(3*d[:,:,None]*d[:,None,:]/r[:,None,None]**5
            - np.eye(3)/r[:,None,None]**3)).sum(0)
def refine(p):
    p=np.array(p,float)
    for _ in range(50):
        g=gradU(p)
        if np.linalg.norm(g)<1e-13: break
        p -= np.linalg.solve(hessU(p),g)
    return p

def ascend(p0):
    # gradient ascent of U with unit speed; stop within 0.01 of a charge or |p|>5
    def rhs(t,p):
        g=gradU(p); n=np.linalg.norm(g)
        return g/n if n>0 else g
    def ev(t,p):
        return min(np.min(np.linalg.norm(cfg_s-p,axis=1))-0.01, 5-np.linalg.norm(p))
    ev.terminal=True
    out=solve_ivp(rhs,[0,10],p0,events=ev,max_step=0.02,rtol=1e-9,atol=1e-11)
    p=out.y[:,-1]
    d=np.linalg.norm(cfg_s-p,axis=1)
    return int(np.argmin(d)) if d.min()<0.05 else -1  # -1 = infinity

from collections import Counter
walls=Counter()
for seed,idx in seeds:
    p=refine(seed)
    w,V=np.linalg.eigh(hessU(p))
    neg=int((w<0).sum())
    if neg!=idx:
        raise RuntimeError(f"index mismatch at seed {seed}: {neg} negative eigenvalues, expected {idx}")
    if idx==2:
        v=V[:,np.argmax(w)]  # unique positive eigenvalue direction: unstable under +gradU
        a=ascend(p+1e-6*v); b=ascend(p-1e-6*v)
        walls[tuple(sorted((a,b)))]+=1
        print(f"index2 at {np.round(p,4)} -> charges {a},{b}")
print("wall multigraph (charge pair -> walls, -1=infinity):",dict(walls))
print("total walls:",sum(walls.values()))
