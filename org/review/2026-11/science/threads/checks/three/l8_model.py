"""Local model L8: two charges (1 at (0,0), lam at (1,0)) in a uniform field E (V = 1/r1 + lam/r2 - E.x).
Limit of three charges when one charge is far and large (equivalently two sites merging).
Inverse map: for fixed field direction alpha, x -> (lam, |E|). Minima region and fold image."""
import numpy as np, sys
def inv(X, al):
    A = np.array([[0.0, 0.0], [1.0, 0.0]])
    d = X[..., None, :] - A; r = np.linalg.norm(d, axis=-1); u = d / r[..., None]
    f1 = u[..., 0, :] / r[..., 0, None] ** 2; f2 = u[..., 1, :] / r[..., 1, None] ** 2
    e = np.array([np.cos(al), np.sin(al)])
    # f1 + lam f2 = E0 e  -> lam f2 - E0 e = -f1
    det = f2[..., 0] * (-e[1]) - f2[..., 1] * (-e[0])
    lam = ((-f1[..., 0]) * (-e[1]) - (-f1[..., 1]) * (-e[0])) / det
    E0 = (f2[..., 0] * (-f1[..., 1]) - f2[..., 1] * (-f1[..., 0])) / det
    c = np.stack([np.ones_like(lam), lam], -1) / r ** 3
    H = 3 * np.einsum('...n,...nk,...nl->...kl', c / r ** 2, d, d) - c.sum(-1)[..., None, None] * np.eye(2)
    dt = H[..., 0, 0] * H[..., 1, 1] - H[..., 0, 1] ** 2
    return lam, E0, dt
if __name__ == '__main__':
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    g = np.linspace(-2, 3, 1500); X = np.stack(np.meshgrid(g, g, indexing='ij'), -1)
    fig, ax = plt.subplots(2, 6, figsize=(24, 8))
    for k, al in enumerate(np.linspace(0.05, np.pi / 2, 6)):
        lam, E0, dt = inv(X, al)
        ok = (lam > 0) & (E0 > 0)
        mn = ok & (dt > 0)
        ax[0, k].contourf(X[..., 0], X[..., 1], np.where(ok, np.where(mn, 2, 1), 0), levels=[-.5, .5, 1.5, 2.5], colors=['w', '#ddd', '#c33'])
        ax[0, k].plot([0, 1], [0, 0], 'bo'); ax[0, k].set_aspect('equal'); ax[0, k].set_title('alpha=%.2f' % al)
        L = np.log(lam[mn]); Ee = np.log(E0[mn])
        ax[1, k].plot(L, Ee, ',', color='r')
        cs = ax[0, k].contour(X[..., 0], X[..., 1], np.where(ok, dt, np.nan), levels=[0])
        for seg in cs.allsegs[0]:
            l2, e2, _ = inv(seg, al); m = (l2 > 0) & (e2 > 0)
            ax[1, k].plot(np.log(l2[m]), np.log(e2[m]), 'k.', ms=1)
        print(al, 'min pixels', mn.sum())
    plt.tight_layout(); plt.savefig('out/l8_model.png', dpi=60)
