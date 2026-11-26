import numpy as np, json
from conv import *
from eng import *
out={}
for k,f in FILES.items():
    A,q=load(f); th,tr=to_theta(A,q); s,o,R,_=tr
    P,qq=theta_to_PqC(th)
    Z=move(Sb,Pb,qb,P,qq,scale=0.5,tries=8,corr_tol=1e-11,hmin=1e-12,h0=0.005)
    re,ph,imm=classify(Z)
    # one rep per flip pair: choose sum Re t >=0 ... use flip pairing by index
    n_real_pairs=int(re.sum()//2)
    pos=[i for i in range(len(Z)) if Z[i,3:].real.sum()>=0]
    # dedupe flip: rep with sum Re t>0
    reps=[i for i in range(len(Z)) if Z[i,3:].real.sum()>0]
    print(f"== {k}: solutions {len(Z)}, points(reps) {len(reps)}, real physical {int(ph.sum())}")
    realnp=[i for i in reps if re[i] and not ph[i]]
    cplx=[i for i in reps if not re[i]]
    # a conjugate pair counts as 2 reps (z and conj) -> complex points counted individually; report both
    print(f"   of {len(reps)} points: real physical {int(sum(ph[i] for i in reps))}, real non-physical (some t<0) {len(realnp)}, non-real {len(cplx)}")
    # physical complex candidates (all Re t>0), and nearest overall using T
    def T(z): return float(np.sum(z.imag**2)+np.sum(np.minimum(z[3:].real,0)**2))
    def Tphys(z): return float(np.sum(z.imag**2))
    rows=[]
    for i in cplx:
        z=Z[i]; allpos=bool(np.all(z[3:].real>0))
        rows.append((T(z),i,allpos))
    rows.sort()
    out[k]={"theta":th.tolist(),"rows":[]}
    print("   nearest 8 non-real points by T=|Im|^2+neg-part (engine units, site1-site2 =1):")
    for t_,i,ap in rows[:8]:
        z=Z[i]; xr=z[:3].real; xi=z[:3].imag
        xw=(xr@R*s)+o if False else o+ (R.T@xr)*s
        print(f"     T={t_:.3e} |Im x|={np.linalg.norm(xi):.3e} |Im t|={np.linalg.norm(z[3:].imag):.2e} Re t={np.round(z[3:].real,3)} allpos={ap} x_orig={np.round(xw,4)}")
    pp=[(t_,i) for t_,i,ap in rows if ap]
    print("   nearest all-Re t>0:")
    for t_,i in pp[:5]:
        z=Z[i]; xw=o+(R.T@z[:3].real)*s
        print(f"     T={t_:.3e} |Im x|={np.linalg.norm(z[:3].imag):.3e} x_orig={np.round(xw,4)}  Re t={np.round(z[3:].real,3)}")
    # phys cluster
    X=np.array([o+(R.T@Z[i,:3].real)*s for i in reps if ph[i]])
    print("   physical centroid",np.round(X.mean(0),4),"spread",np.round(np.linalg.norm(X-X.mean(0),axis=1).max(),4))
