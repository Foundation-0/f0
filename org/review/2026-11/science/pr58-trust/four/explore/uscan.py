import numpy as np, sys
from scipy.optimize import minimize
sys.path.insert(0,'.')
from c3v import flat_config, jets
def resid(params):
    u = params[:4]; n = np.abs(u)/np.linalg.norm(u)
    if n.min() < 1e-3: return 1e3
    e = params[4:7]; e = e/np.linalg.norm(e)
    A, q = flat_config(n); _, _, T = jets(A, q)
    D = np.einsum('ijk,k->ij', T, e)          # directional derivative of the cubic: quadratic form
    return (D**2).sum()/(T**2).sum()
rng = np.random.default_rng(7); best=[]
for s in range(400):
    x0 = np.concatenate([rng.random(4)+0.05, rng.standard_normal(3)])
    r = minimize(resid, x0, method='Nelder-Mead', options={'xatol':1e-10,'fatol':1e-14,'maxiter':4000})
    n = np.abs(r.x[:4])/np.linalg.norm(r.x[:4])
    best.append((r.fun, np.sort(n)))
best.sort(key=lambda b: b[0])
for f, n in best[:8]: print("%.3e" % f, np.round(n, 4))
