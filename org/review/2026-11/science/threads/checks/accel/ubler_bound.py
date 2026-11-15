"""KMOS3D (Ubler et al. 2017, CDS J/ApJ/842/121 table3, 135 galaxies) upper-bound test.

In MOND with the RAR form, an isolated disc reaches V_flat^4 = G M_b a0 far out, and the
maximum circular speed satisfies V_max >= V_flat (equality for low surface density). So each galaxy
gives an upper bound  a0 <= a_max = V_max^4 / (G M_b).
Missing baryons (HI omitted by Ubler) make the true bound lower, so the bound is conservative there.
We compare the per-bin distribution of a_max with a0 = 1.2e-10 (constant) and 1.2e-10 E(z) (H tracking),
and fit p in a0 = A E^p under the assumption V_max = V_flat (deep-MOND BTFR) as a descriptive number.
"""
import json, math, sys
import numpy as np
import accel_lib as L

d = L.load_ubler(sys.argv[1])
n = len(d['z'])
GM = L.G_SI * 10 ** d['logMb'] * L.MSUN
amax = (d['V'] * 1e3) ** 4 / GM
la = np.log10(amax)
out = {'N': n, 'bins': []}
print('N galaxies read:', n)
for lo, hi in ((0.5, 1.2), (1.2, 1.9), (1.9, 2.7)):
    m = (d['z'] >= lo) & (d['z'] < hi)
    zm = float(np.median(d['z'][m]))
    aH = 1.2e-10 * float(L.E(zm))
    q = np.percentile(la[m], [16, 50, 84])
    f_below_c = float(np.mean(amax[m] < 1.2e-10)); f_below_H = float(np.mean(amax[m] < aH))
    se = float(np.std(la[m]) / math.sqrt(m.sum()))
    out['bins'].append(dict(z=[lo, hi], n=int(m.sum()), z_median=zm, log_amax_16_50_84=[float(x) for x in q],
                            median_amax=float(10 ** q[1]), se_log_median=se, a0_H=aH,
                            frac_amax_below_1p2=f_below_c, frac_amax_below_a0H=f_below_H))
    print('z %.1f-%.1f n=%3d zmed=%.2f  median a_max=%.2fe-10 (16-84%%: %.2f-%.2f)  a0_H=%.2fe-10  '
          'frac(a_max<1.2)=%.2f frac(a_max<a0_H)=%.2f' % (lo, hi, m.sum(), zm, 10 ** q[1] / 1e-10, 10 ** q[0] / 1e-10, 10 ** q[2] / 1e-10, aH / 1e-10, f_below_c, f_below_H))
# descriptive fit of log a_max = log A + p log E(z) with free scatter (ordinary least squares)
X = np.vstack([np.ones(n), np.log10(L.E(d['z']))]).T
coef, res, *_ = np.linalg.lstsq(X, la, rcond=None)
resid = la - X @ coef; s2 = resid.var(ddof=2); cov = s2 * np.linalg.inv(X.T @ X)
out['ols'] = dict(logA=float(coef[0]), p=float(coef[1]), p_err=float(math.sqrt(cov[1, 1])), scatter_dex=float(math.sqrt(s2)))
print('OLS log a_max = %.3f + %.2f(+-%.2f) log E ; scatter %.2f dex' % (coef[0], coef[1], math.sqrt(cov[1, 1]), math.sqrt(s2)))
# z-independent-mass-composition check: same fit restricted to logMb in a common window
w = (d['logMb'] > 10.4) & (d['logMb'] < 11.0)
c2, *_ = np.linalg.lstsq(X[w], la[w], rcond=None)
r2 = la[w] - X[w] @ c2; s22 = r2.var(ddof=2); cv2 = s22 * np.linalg.inv(X[w].T @ X[w])
out['ols_mass_window_10.4_11.0'] = dict(n=int(w.sum()), p=float(c2[1]), p_err=float(math.sqrt(cv2[1, 1])))
print('same, 10.4<logMb<11.0 (n=%d): p = %.2f +- %.2f' % (w.sum(), c2[1], math.sqrt(cv2[1, 1])))
json.dump(out, open(sys.argv[2], 'w'), indent=1)
