import numpy as np
def flat_config(n):
    n = np.asarray(n, float); n = n/np.linalg.norm(n)
    t = n/np.sqrt(1-n**2); w = t**2
    G = np.diag(w + w**2) - np.outer(w, w)          # Gram matrix a_i . a_j
    ev, U = np.linalg.eigh(G)
    keep = ev > 1e-12 * ev.max()
    A = U[:, keep] * np.sqrt(ev[keep])               # rows = sites in R^3
    q = t**3/(1+w)
    return A, q
def jets(A, q):
    F = np.zeros(3); H = np.zeros((3,3)); T = np.zeros((3,3,3)); I3=np.eye(3)
    for p, c in zip(A, q):
        d = -p; r = np.linalg.norm(d)
        F += -c*d/r**3
        H += c*(3*np.outer(d,d)/r**5 - I3/r**3)
        T += c*(-15*np.einsum('i,j,k->ijk',d,d,d)/r**7 + 3*(np.einsum('ij,k->ijk',I3,d)+np.einsum('ik,j->ijk',I3,d)+np.einsum('jk,i->ijk',I3,d))/r**5)
    return F, H, T
def cubic_parts(A, T):
    # axis along site 0; decompose harmonic cubic C(x)=T[x,x,x]/6 into zonal (m=0) and m=3 parts
    e3 = A[0]/np.linalg.norm(A[0]); e1 = np.cross(e3, [0.3,0.5,0.7]); e1/=np.linalg.norm(e1); e2=np.cross(e3,e1)
    R = np.array([e1,e2,e3])
    Tr = np.einsum('ai,bj,ck,ijk->abc', R, R, R, T)
    # sample on circle: C(cos f, sin f, 0) for the m=3 part, C(0,0,1) for zonal
    zonal = Tr[2,2,2]/6
    f = np.linspace(0, 2*np.pi, 64, endpoint=False)
    v = np.stack([np.cos(f), np.sin(f), 0*f], 1)
    Cv = np.einsum('abc,na,nb,nc->n', Tr, v, v, v)/6
    m3 = np.abs(np.fft.rfft(Cv)[3])*2/len(f)
    m1 = np.abs(np.fft.rfft(Cv)[1])*2/len(f)
    return zonal, m3, m1
if __name__ == "__main__":
    for a in [0.2,0.3,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95]:
        b = np.sqrt((1-a*a)/3)
        A, q = flat_config([a,b,b,b])
        F, H, T = jets(A, q)
        z, m3, m1 = cubic_parts(A, T)
        print("a=%.3f  |grad|=%.1e |Hess|=%.1e  zonal(axis^3)=%+.5f  m3=%.5f  m1=%.1e  charges=%s" % (a, np.abs(F).max(), np.abs(H).max(), z, m3, m1, np.round(q/q.max(),4)))
