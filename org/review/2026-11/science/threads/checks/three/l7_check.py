"""Numerical check of Lemma L7 (local model F_L(X) = X1^2 - X2^2/2 + 1/|X| - L.X):
count local minima by 2D Newton from many seeds, and by the 1D root count of
Psi(c) = c^(2/3) [L1^2/(2-c)^2 + L2^2/(1+c)^2] - 1."""
import numpy as np
rng = np.random.default_rng(0)
def crit2d(L):
    th = np.linspace(0, 2*np.pi, 60, endpoint=False); rr = 10**np.linspace(-1.5, 1, 30)
    X = np.array([[r*np.cos(t), r*np.sin(t)] for r in rr for t in th])
    for _ in range(80):
        r = np.linalg.norm(X, axis=1)
        g = np.c_[2*X[:,0], -X[:,1]] - X/r[:,None]**3 - L
        c = 1/r**3; u = X/r[:,None]
        H = np.zeros((len(X),2,2)); H[:,0,0]=2; H[:,1,1]=-1
        H += c[:,None,None]*(3*np.einsum('ni,nj->nij',u,u) - np.eye(2))
        st = np.linalg.solve(H, g[...,None])[...,0]
        n = np.linalg.norm(st,axis=1); f = np.minimum(1, 0.3*r/np.maximum(n,1e-300))
        X = X - st*f[:,None]
    r = np.linalg.norm(X, axis=1)
    g = np.c_[2*X[:,0], -X[:,1]] - X/r[:,None]**3 - L
    ok = np.linalg.norm(g,axis=1) < 1e-10
    P = []
    for x in X[ok]:
        if all(np.linalg.norm(x-p) > 1e-6 for p in P): P.append(x)
    mins = 0
    for x in P:
        r = np.linalg.norm(x); c = 1/r**3; u = x/r
        H = np.diag([2.,-1.]) + c*(3*np.outer(u,u)-np.eye(2))
        if np.linalg.eigvalsh(H)[0] > 0: mins += 1
    return len(P), mins
def roots1d(L):
    c = np.r_[np.linspace(1e-6, 2-1e-9, 200001), np.linspace(2+1e-9, 200, 200001)]
    Psi = c**(2/3)*(L[0]**2/(2-c)**2 + L[1]**2/(1+c)**2) - 1
    left = c < 2
    nl = (np.diff(np.sign(Psi[left])) != 0).sum(); nr = (np.diff(np.sign(Psi[~left])) != 0).sum()
    return nl, nr
from collections import Counter
C = Counter(); bad = []
for k in range(400):
    L = rng.normal(size=2) * 10**rng.uniform(-1, 1)
    n, m = crit2d(L); nl, nr = roots1d(L)
    C[(n, m, nl + nr)] += 1
    if m > 1 or n != nl + nr: bad.append((L.tolist(), n, m, nl, nr))
print(sorted(C.items())); print('mismatch or >1 min:', bad[:5])
