# C3v-symmetric 2-parameter family: vertex 0 at (1,1,1)(1+s), charge 1+q; others fixed, charge 1.
# Count balance points near the centre via 2D Newton in the mirror plane y=z.
# count = n_axis + 3*n_offaxis (in the plane y=z, which contains the C3 axis).
import numpy as np, sys
import finder
e1=np.array([1,1,1])/np.sqrt(3); e2=np.array([2,-1,-1])/np.sqrt(6)
B=np.stack([e1,e2],1)  # 3x2
def conf(s,q):
    P=np.array([(1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1)],float); P[0]*=1+s
    Q=np.array([1+q,1,1,1.]); return P,Q
def crit2d(P,Q,R=0.3,nr=60,nth=48):
    sols=[]
    for r in np.geomspace(1e-5,R,nr):
        for th in np.linspace(0,2*np.pi,nth,endpoint=False):
            u=np.array([r*np.cos(th),r*np.sin(th)])
            for it in range(100):
                x=B@u; g,H=finder.gH(x,P,Q)
                g2=B.T@g; H2=B.T@H@B
                try: du=np.linalg.solve(H2,g2)
                except: break
                nd=np.linalg.norm(du)
                if nd>0.5*max(np.linalg.norm(u),1e-4): du*=0.5*max(np.linalg.norm(u),1e-4)/nd
                u=u-du
                if np.linalg.norm(u)>0.6: break
                if nd<1e-15: break
            x=B@u; g,H=finder.gH(x,P,Q)
            if np.linalg.norm(u)<0.6 and np.linalg.norm(g)<1e-13:
                if not any(np.linalg.norm(u-w)<1e-9*(1+0) for w in sols): sols.append(u)
    return sols
def count(s,q,**kw):
    P,Q=conf(s,q); sols=crit2d(P,Q,**kw)
    ax=[u for u in sols if abs(u[1])<1e-10]; off=[u for u in sols if abs(u[1])>=1e-10]
    return len(ax)+3*len(off), ax, off
if __name__=='__main__':
    for s in [float(a) for a in sys.argv[1].split(',')]:
        for q in [float(a) for a in sys.argv[2].split(',')]:
            c,ax,off=count(s,q,nr=30,nth=24)
            print(f"s={s:+.4g} q={q:+.4g} count={c} axis={len(ax)} off={len(off)}",flush=True)
