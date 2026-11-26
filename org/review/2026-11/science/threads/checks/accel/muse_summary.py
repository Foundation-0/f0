"""Summary-level translation of the published MUSE-DARK III linear a0(z) curves into the exponent p of
a0 = A E(z)^p. NOT a fit to galaxy data (the per-galaxy RAR points were not retrievable).

Method: least-squares match of log10(a + b z) to log10 A + p log10 E(z) on a uniform grid over the
sample range 0.33-1.44, then Monte Carlo over (a, b) using the published 95% half-widths / 1.96 as
Gaussian sigmas with zero covariance (the paper says its corner plot shows no significant correlation).
"""
import numpy as np
import accel_lib as L

rng = np.random.default_rng(7)
z = np.linspace(0.33, 1.44, 200)
X = np.vstack([np.ones_like(z), np.log10(L.E(z))]).T


def fit_curve(a, b):
    y = np.log10(a + b * z)
    c, *_ = np.linalg.lstsq(X, y, rcond=None)
    rms = np.sqrt(np.mean((y - X @ c) ** 2))
    return 10 ** c[0], c[1], rms


for name, a, sa, b, sb in (('DC14 Eq.4 (1.00+1.59z)', 1.00, 0.04 / 1.96, 1.59, 0.10 / 1.96),
                           ('MOND Eq.14 (1.03+1.20z)', 1.03, 0.05 / 1.96, 1.20, 0.10 / 1.96),
                           ('DC14 best-profile Eq.9 (1.05+1.63z)', 1.05, 0.05 / 1.96, 1.63, 0.125 / 1.96)):
    A, p, rms = fit_curve(a, b)
    ps = [fit_curve(a + sa * rng.standard_normal(), b + sb * rng.standard_normal())[1] for _ in range(4000)]
    lo, hi = np.percentile(ps, [16, 84])
    print('%-38s best A=%.3fe-10 p=%.3f (curve-shape rms %.4f dex); p 68%% range from quoted errors [%.3f, %.3f]'
          % (name, A, p, rms, lo, hi))
print('Note: these ranges are statistical only, inherit all modelling of the source, and treat 95% intervals as 1.96 sigma.')
