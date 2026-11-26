import numpy as np, warnings; warnings.filterwarnings('ignore')
import run_cert3 as rc
from run_cert3 import *
from lib3 import mu
sh=Shape(0.5,0.5,0.8660254037844385,0.8660254037844387)
A=np.array([[0,0],[1,0],[0.5,0.8660254037844386]])
cap={}
orig=rc.split4
# run phase A + one B round manually by copying code: easier to monkeypatch log to capture state is complex; replicate
cand,nex=candidates(sh,5,8)
kind,NB,cells=local_cert(sh,cand,2)
good=kind>0
bad=cand[~good]; ch=split4(bad); ch=ch[ch[:,0]+ch[:,2]<1]; ch=ch[~excluded(sh,ch.T)]
k2,NB2,c2=local_cert(sh,ch,2)
Lf=np.vstack([np.c_[cand[good],kind[good],NB[good],cells[good]],np.c_[ch,k2,NB2,c2]])
R=rho_centered(sh,Lf[:,:4].T)
lo2,hi2,lo3,hi3=R[0].lo,R[0].hi,R[1].lo,R[1].hi
order=np.argsort(lo2);PI=[];PJ=[]
for a_ in range(len(Lf)):
    i=order[a_];js=order[a_+1:];js=js[lo2[js]<=hi2[i]];js=js[(lo3[js]<=hi3[i])&(lo3[i]<=hi3[js])&(lo2[i]<=hi2[js])]
    PI+=[i]*len(js);PJ+=js.tolist()
PI=np.array(PI);PJ=np.array(PJ)
Bi=Lf[PI,:4];Bj=Lf[PJ,:4]
cont=np.zeros(len(PI),bool)
for X,ly in ((Bi,PJ),(Bj,PI)):
    kd=Lf[ly,4];N=Lf[ly,5:9]
    cont|=(kd==1)&(X[:,0]>=N[:,0])&(X[:,1]<=N[:,1])&(X[:,2]>=N[:,2])&(X[:,3]<=N[:,3])
    vv=np.where(kd>=3)[0]; cont[vv]|=inside_cell(sh,X[vv],Lf[ly[vv],9:17])
u=~cont
ci=np.c_[(Bi[:,0]+Bi[:,1])/2,(Bi[:,2]+Bi[:,3])/2]; cj=np.c_[(Bj[:,0]+Bj[:,1])/2,(Bj[:,2]+Bj[:,3])/2]
X=lambda c: c[:,:1]*A[1]+c[:,1:]*A[2]
h=1/256
d=np.linalg.norm(ci-cj,axis=1)/h
from lib3 import lami
qi=lami(A,X(ci))[0];qj=lami(A,X(cj))[0]
imd=np.abs(np.log(qi[:,1:]/qi[:,:1])-np.log(qj[:,1:]/qj[:,:1])).max(1)
mi=mu(A,X(ci));mj=mu(A,X(cj))
print('unresolved',u.sum(),'of',len(u))
print('dist (leaf units) of unresolved: pct',np.percentile(d[u],[5,25,50,75,95]))
print('image dist pct',np.percentile(imd[u],[5,25,50,75,95]))
print('frac both inside Rmin',np.mean((mi[u]>0)&(mj[u]>0)),'one outside',np.mean((mi[u]>0)!=(mj[u]>0)),'both outside',np.mean((mi[u]<=0)&(mj[u]<=0)))
print('kinds of leaves in unresolved', np.bincount(Lf[PI[u],4].astype(int)), np.bincount(Lf[PJ[u],4].astype(int)))
