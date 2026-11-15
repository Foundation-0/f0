"""push3: push2 adapted to 11-point seeds. Usage: python push3.py seedname nruns rngseed [iters] [kicks]
Tight tracker tolerances, trust region starts at 1e-7, run i targets the (i mod 6)-th nearest conjugate pair."""
import sys, time, json
import numpy as np
from scipy.optimize import linprog
from conv import *
from eng import *
import eng
name=sys.argv[1]; NRUNS=int(sys.argv[2]); seed=int(sys.argv[3])
ITERS=int(sys.argv[4]) if len(sys.argv)>4 else 150
KICKS=int(sys.argv[5]) if len(sys.argv)>5 else 2
eng.rng=np.random.default_rng(seed); rng=np.random.default_rng(seed+1000)
NS=len(Sb); m=8
LO=np.array([-3,0.02,-3,-3,-3]+[-16]*3,float); HI=np.array([4,4,4,3,3]+[16]*3,float)
import os
TR0=1e-7; TRMAX=float(os.environ.get("TRMAX","2e-4")); TRMIN=1e-10
def dPq_dtheta(th):
    M=np.zeros((16+0,m)) if False else np.zeros((4*3+4,m))
    M[2*3+0,0]=1;M[2*3+1,1]=1
    M[3*3+0,2]=1;M[3*3+1,3]=1;M[3*3+2,4]=1
    for j in range(3): M[12+1+j,5+j]=np.exp(th[5+j])
    return M
def mv(Z,Pa,qa,P2,q2,tries=3):
    # detour scaled to the step size
    return move_s(Z,Pa,qa,P2,q2,tries)
def move_s(Z,Pa,qa,P2,q2,tries):
    for _ in range(tries):
        sc=0.5
        Pm=sc*(eng.rng.normal(size=Pa.shape)+1j*eng.rng.normal(size=Pa.shape))*(np.abs(P2-Pa).max()+1e-12)
        qm=sc*(eng.rng.normal(size=qa.shape)+1j*eng.rng.normal(size=qa.shape))*(np.abs(q2-qa).max()+1e-12)
        Pm[:2]=0;qm[0]=0
        Zt,ok=track(Z,arc_path(Pa,qa,P2,q2,Pm,qm),3,h0=0.05,hmin=1e-12,corr_tol=1e-11)
        if not ok.all(): continue
        Zt,err=newton(Zt,*bc(P2,q2,len(Zt)),3)
        if err.max()>1e-9: continue
        dd=np.max(np.abs(Zt[:,None]-Zt[None]),axis=2);np.fill_diagonal(dd,1)
        if dd.min()<1e-9: continue
        return Zt
    return None
def Tval(z): return float(np.sum(z.imag**2)+np.sum(np.minimum(z[3:].real,0)**2))
def classify2(Z):
    r,p,_=classify(Z,1e-9); return r,p
def reps_of(Z,real):
    return [i for i in np.where(~real)[0] if Z[i,3:].real.sum()>=0 and Z[i].imag[np.argmax(np.abs(Z[i].imag))]>0]
A,q=load(FILES[name]); th0,_=to_theta(A,q)
P0,q0=theta_to_PqC(th0)
Z0=move(Sb,Pb,qb,P0,q0,scale=0.5,tries=8,corr_tol=1e-11,hmin=1e-12,h0=0.005)
r0,p0=classify2(Z0); print(name,"seed count",int(p0.sum()),flush=True)
results=[]
overall_best=0
for run in range(NRUNS):
    t0=time.time()
    th=th0.copy();P,q=P0,q0;Z=Z0.copy()
    real,phys=classify2(Z); nphys=int(phys.sum())
    best_n=nphys;best_th=th.copy()
    reps=reps_of(Z,real); T=np.array([Tval(Z[i]) for i in reps]); order=np.argsort(T)
    target=Z[reps[order[run%6]]].copy(); T_start=float(T[order[run%6]])
    tr=np.full(m,TR0); stall=0; kicks=0; accepted=0; events=[]; Tmin_hist=[]
    for it in range(ITERS):
        real,phys=classify2(Z); nphys=int(phys.sum())
        reps=reps_of(Z,real)
        T=np.array([Tval(Z[i]) for i in reps])
        i0=int(np.argmin(np.max(np.abs(Z-target[None]),axis=1)))
        z=Z[i0];Tt=Tval(z)
        Pbt,qbt=bc(P,q,NS)
        F,J=F_J(Z,Pbt,qbt,3)
        dZ=-np.linalg.solve(J,param_jac(Z,Pbt,qbt,3)@dPq_dtheta(th))
        A_ub=[];b_ub=[]
        ph=np.where(phys)[0]
        for a_ in range(len(ph)):
            for b_ in range(a_+1,len(ph)):
                a,b=ph[a_],ph[b_]
                diff=(Z[a]-Z[b]).real
                A_ub.append(-2*diff@(dZ[a]-dZ[b]).real);b_ub.append(0.35*float(diff@diff))
        gT=2*(z.imag@dZ[i0].imag)+2*(np.minimum(z[3:].real,0)@dZ[i0,3:].real)
        bounds=[(max(-tr[j],LO[j]-th[j]),min(tr[j],HI[j]-th[j])) for j in range(m)]
        res=linprog(gT/(np.linalg.norm(gT)+1e-300),A_ub=np.array(A_ub) if A_ub else None,b_ub=np.array(b_ub) if b_ub else None,bounds=bounds,method="highs")
        ok=False
        if res.success and np.linalg.norm(res.x)>1e-16:
            th2=th+res.x;P2,q2=theta_to_PqC(th2)
            Z2=move_s(Z,P,q,P2,q2,3)
            if Z2 is not None:
                real2,phys2=classify2(Z2);n2=int(phys2.sum())
                j0=int(np.argmin(np.max(np.abs(Z2-z[None]),axis=1)))
                if n2>nphys or (n2>=nphys and Tval(Z2[j0])<Tt):
                    if n2!=nphys:
                        events.append((it,nphys,n2));print(f"*** [{name} run {run} it {it}] physical {nphys} -> {n2}",flush=True)
                    th,P,q,Z=th2,P2,q2,Z2
                    target=Z2[j0].copy() if n2==nphys else None
                    ok=True;accepted+=1;tr=np.minimum(tr*1.5,TRMAX)
        if target is None:
            reps=reps_of(Z,classify2(Z)[0])
            if reps:
                T=np.array([Tval(Z[i]) for i in reps]);target=Z[reps[int(np.argmin(T))]].copy()
        if not ok:
            tr=tr*0.4;stall+=1
            if tr.max()<TRMIN:
                tr=np.full(m,TR0);
                if kicks>=KICKS: break
                kicks+=1
                # kick from base seed: relative size log-uniform 1e-7..1e-5
                thk=np.clip(best_th+rng.normal(size=m)*10**rng.uniform(-7,-5),LO,HI)
                Pk,qk=theta_to_PqC(thk)
                Zk=move_s(Z,P,q,Pk,qk,4)
                if Zk is not None:
                    th,P,q,Z=thk,Pk,qk,Zk;rk,pk=classify2(Z)
                    reps=reps_of(Z,rk);T=np.array([Tval(Z[i]) for i in reps]);order=np.argsort(T)
                    target=Z[reps[order[rng.integers(min(4,len(order)))]]].copy()
                    events.append((it,"kick",int(pk.sum())))
        real,phys=classify2(Z)
        if int(phys.sum())>best_n: best_n=int(phys.sum());best_th=th.copy()
    real,phys=classify2(Z); reps=reps_of(Z,real); T=np.array([Tval(Z[i]) for i in reps])
    rec={"run":run,"best_phys":best_n,"best_theta":best_th.tolist(),"final_theta":th.tolist(),"final_count":int(phys.sum()),
         "iters":it+1,"accepted":accepted,"kicks":kicks,"T_target_start":T_start,"T_nearest_final":float(T.min()),
         "dtheta_norm":float(np.linalg.norm(th-th0)),"events":events,"secs":time.time()-t0}
    results.append(rec)
    print(f"[{name} run {run}] best {best_n} final {int(phys.sum())} acc {accepted}/{it+1} kicks {kicks} T {T_start:.3e}->{T.min():.3e} |dth|={rec['dtheta_norm']:.2e} {rec['secs']:.0f}s",flush=True)
    json.dump(results,open(f"out/push3_{name}_{seed}_tr{TRMAX:g}.json","w"),indent=1)
print("DONE",name)
