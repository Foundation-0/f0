import json, numpy as np, itertools
from fractions import Fraction
S="../"   # checks/four/, which holds verify/ and jet-route/
FILES={"short":S+"verify/n4_eleven_short.json","flat":S+"verify/n4_eleven_flat.json","b12":S+"jet-route/n4_eleven_b12.json"}
def load(f):
    c=json.load(open(f)); A=np.array([[float(Fraction(x)) for x in s] for s in c["sites"]]); q=np.array([float(Fraction(x)) for x in c["charges"]]); return A,q
def to_theta(A,q,order=(0,1,2,3)):
    A=A[list(order)];q=q[list(order)]
    p=A-A[0]; s=np.linalg.norm(p[1]); e1=p[1]/s
    v=p[2]-(p[2]@e1)*e1; e2=v/np.linalg.norm(v); e3=np.cross(e1,e2)
    R=np.stack([e1,e2,e3]); X=(p@R.T)/s
    qq=q/q[0]
    th=np.array([X[2,0],X[2,1],X[3,0],X[3,1],X[3,2],*np.log(qq[1:])])
    return th,(s,A[0],R,order)
def theta_to_Pq(th):
    P=np.zeros((4,3));P[1,0]=1;P[2,:2]=th[0:2];P[3]=th[2:5]
    return P,np.concatenate([[1.0],np.exp(th[5:])])
if __name__=="__main__":
    for k,f in FILES.items():
        A,q=load(f)
        print(k,q); 
        D=np.linalg.norm(A[:,None]-A[None],axis=2); print(np.round(D,3))
