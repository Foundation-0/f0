"""Like-for-like test of a0(z) = A E(z)^p against RC100 (Nestor Shachar et al. 2023).

For each galaxy: Newtonian baryonic acceleration at the disc R_e from the published
baryonic mass, bulge mass and R_e; predicted circular speed under the algebraic RAR
with a0(z); compared with the published V_c(R_e) and its error.

Variants of the baryonic input:
  A  table M_baryon (dynamical posterior with a photometric+gas-scaling prior)
  B  photometric M* (table col 6) + molecular gas from Tacconi+2018 scaling (independent of kinematics)
  C  the paper's own decomposition as an RAR point: gN = (1-fDM) Vc^2/Re, g = Vc^2/Re

Usage: python rc100_fit.py data/rc100_table3.csv > outputs/rc100_fit.txt
"""
import json, math, sys
import numpy as np
from scipy.optimize import minimize, minimize_scalar
import accel_lib as L

A_SPARC = 1.20e-10      # McGaugh, Lelli & Schombert 2016: 1.20 +- 0.02 (stat) +- 0.24 (sys) e-10
LN10 = math.log(10)
rng = np.random.default_rng(12345)


def prepare(d, variant, thick, mass_shift=0.0, mass_shift_per_z=0.0, pressure='pub', om=0.315):
    z, Re = d['z'], d['Re']
    Vc = d['Vc'].copy()
    if pressure == 'half':      # undo half of the Burkert+2010 correction 2 sigma0^2 (R/Rd) at R = Re
        Vc = np.sqrt(np.maximum(Vc ** 2 - 0.5 * 2 * d['sig0'] ** 2 * 1.6783, 1.0))
    elif pressure == 'x1.5':    # 50% stronger correction than published
        Vc = np.sqrt(Vc ** 2 + 0.5 * 2 * d['sig0'] ** 2 * 1.6783)
    elif pressure == 'none':
        Vc = np.sqrt(np.maximum(Vc ** 2 - 2 * d['sig0'] ** 2 * 1.6783, 1.0))
    sV = d['e_Vc'] / d['Vc'] / LN10
    dm = mass_shift + mass_shift_per_z * (z - 1.5)
    if variant == 'A':
        Mb = 10 ** (d['logMbar'] + dm); sM = d['e_logMbar']
        BT = 10 ** (d['logMbul'] - d['logMbar'])
    elif variant == 'B':
        mu = L.tacconi18_mu(z, d['dMS'], d['logMs'])
        Mb = 10 ** (d['logMs'] + dm) * (1 + mu)
        sM = np.sqrt(0.15 ** 2 + (mu / (1 + mu)) ** 2 * 0.20 ** 2)
        BT = 10 ** (d['logMbul'] - d['logMbar'])
    else:
        raise ValueError(variant)
    return dict(z=z, Re=Re, Vc=Vc, sV=sV, Mb=Mb, Mbu=BT * Mb, sM=sM,
                sR=d['e_Re'] / Re / LN10, thick=thick, E=L.E(z, om))


def logv_pred(P, a0):
    v, _ = L.v_mond(P['Re'], P['Mb'], P['Mbu'], P['Re'], a0, P['thick'])
    return np.log10(v)


def slopes(P, a0, h=0.01):
    """d log v / d log M and d log v / d log Re (Re moves the radius of evaluation and the disc scale)."""
    f = lambda Mb, Mbu, Re: np.log10(L.v_mond(Re, Mb, Mbu, Re, a0, P['thick'])[0])
    base = f(P['Mb'], P['Mbu'], P['Re'])
    k = 10 ** h
    sMd = (f(P['Mb'] * k, P['Mbu'] * k, P['Re']) - base) / h
    sRd = (f(P['Mb'], P['Mbu'], P['Re'] * k) - base) / h
    return sMd, sRd


def nll(P, A, p, sint):
    a0 = A * P['E'] ** p
    r = np.log10(P['Vc']) - logv_pred(P, a0)
    sMd, sRd = slopes(P, a0)
    var = P['sV'] ** 2 + (sMd * P['sM']) ** 2 + (sRd * P['sR']) ** 2 + sint ** 2
    return 0.5 * np.sum(r ** 2 / var + np.log(2 * np.pi * var))


def nll_C(d, A, p, sint, om=0.315):
    """Variant C: log D = log[1/(1-fDM)] vs log nu(gN/a0); gN from the paper's decomposition."""
    f, Vc, Re = d['fDM'], d['Vc'], d['Re']
    gN = L.accel_si(np.sqrt((1 - f)) * Vc, Re)
    a0 = A * L.E(d['z'], om) ** p
    y = gN / a0
    r = np.log10(1 / (1 - f)) - np.log10(L.nu(y))
    sD = np.maximum(d['e_fDM'], 0.02) / (1 - f) / LN10
    # error on gN: Vc^2 (40%) and (1-f); slope dlog nu/dlog y numerically
    h = 1e-3
    dlnu = (np.log10(L.nu(y * 10 ** h)) - np.log10(L.nu(y))) / h
    sgN = np.sqrt((2 * d['e_Vc'] / Vc) ** 2 + (d['e_fDM'] / (1 - f)) ** 2) / LN10
    var = sD ** 2 + (dlnu * sgN) ** 2 + sint ** 2
    return 0.5 * np.sum(r ** 2 / var + np.log(2 * np.pi * var))


def fit(fun, A_mode, p_fixed=None):
    """A_mode: 'fixed' (A=1.2e-10), 'prior' (log-normal 20% around 1.2e-10), 'free'.
    Returns dict with best params and -2 lnL (prior term included in 'prior' mode)."""
    def obj(x):
        i = 0
        if p_fixed is None:
            p = x[i]; i += 1
        else:
            p = p_fixed
        sint = abs(x[i]); i += 1
        if A_mode == 'fixed':
            lA = 0.0; pen = 0.0
        else:
            lA = x[i]; i += 1
            pen = 0.5 * (lA / math.log10(1.2)) ** 2 if A_mode == 'prior' else 0.0
        return fun(A_SPARC * 10 ** lA, p, sint + 1e-6) + pen
    best = None
    for p0 in ([0.0, 1.0, -1.0, 2.0] if p_fixed is None else [None]):
        for s0 in (0.02, 0.08):
            x0 = ([p0] if p_fixed is None else []) + [s0] + ([0.0] if A_mode != 'fixed' else [])
            r = minimize(obj, x0, method='Nelder-Mead', options=dict(xatol=1e-5, fatol=1e-6, maxiter=4000))
            if best is None or r.fun < best.fun:
                best = r
    x = list(best.x); out = {'m2lnL': 2 * best.fun}
    if p_fixed is None:
        out['p'] = x.pop(0)
    else:
        out['p'] = p_fixed
    out['sint'] = abs(x.pop(0))
    out['A'] = A_SPARC * 10 ** x.pop(0) if A_mode != 'fixed' else A_SPARC
    return out


def profile_p(fun, A_mode, grid):
    return [fit(fun, A_mode, p_fixed=p)['m2lnL'] for p in grid]


def interval(grid, prof, level=1.0):
    prof = np.array(prof); m = prof.min(); ok = grid[prof - m <= level]
    return float(ok.min()), float(ok.max()), bool(ok.min() == grid[0] or ok.max() == grid[-1])


def power(P, A=A_SPARC):
    """Per-galaxy regime and forecast sensitivity to p at p=0 (Fisher)."""
    a0c = A
    v2n = L.vbar2(P['Re'], P['Mb'], P['Mbu'], P['Re'], P['thick'])
    gN = L.accel_si(np.sqrt(v2n), P['Re'])
    lv0 = logv_pred(P, A)
    lv1 = logv_pred(P, A * P['E'])
    sMd, sRd = slopes(P, A)
    sig = np.sqrt(P['sV'] ** 2 + (sMd * P['sM']) ** 2 + (sRd * P['sR']) ** 2)
    h = 1e-3
    dlv_dp = (logv_pred(P, A * P['E'] ** h) - lv0) / h
    return dict(y_const=gN / a0c, y_H=gN / (A * P['E']), dlogv_p0_to_p1=lv1 - lv0, sigma=sig,
                fisher_sigma_p=float(1 / math.sqrt(np.sum(dlv_dp ** 2 / sig ** 2))))


def main(path):
    d = L.load_rc100(path)
    res = {'source': 'Nestor Shachar et al. 2023 Table 3 (hand transcription, data/rc100_table3.csv)', 'N': int(len(d['z']))}
    # thickness calibration: match median of model vbar^2 to published (1-fDM)Vc^2 using variant-A masses
    Mb = 10 ** d['logMbar']; Mbu = 10 ** d['logMbul']
    disc = L.v2_expdisk(d['Re'], Mb - Mbu, d['Re'] / 1.6783); bul = L.v2_bulge(d['Re'], Mbu)
    target = (1 - d['fDM']) * d['Vc'] ** 2
    t = minimize_scalar(lambda k: np.median(np.log10((k * disc + bul) / target)) ** 2, bounds=(0.5, 1.2), method='bounded').x
    lr_thin = np.log10((disc + bul) / target); lr_thick = np.log10((t * disc + bul) / target)
    res['vbar_check'] = dict(thin_median_dex=float(np.median(lr_thin)), thin_std_dex=float(np.std(lr_thin)),
                             thick_factor=float(t), thick_median_dex=float(np.median(lr_thick)), thick_std_dex=float(np.std(lr_thick)))
    print('Baryonic v^2 at Re, my model vs paper (1-fDM)Vc^2: thin disc median %+.3f dex (std %.3f); '
          'disc v^2 factor %.3f brings median to %+.3f (std %.3f)' % (np.median(lr_thin), np.std(lr_thin), t, np.median(lr_thick), np.std(lr_thick)))
    grid = np.round(np.arange(-4.0, 4.01, 0.05), 3)
    runs = {}
    configs = [('A', t, 'pub', 0, 0), ('A', 1.0, 'pub', 0, 0), ('B', t, 'pub', 0, 0),
               ('A', t, 'half', 0, 0), ('A', t, 'none', 0, 0), ('A', t, 'x1.5', 0, 0),
               ('A', t, 'pub', +0.2, 0), ('A', t, 'pub', -0.2, 0),
               ('A', t, 'pub', 0, +0.1), ('A', t, 'pub', 0, -0.1), ('A', t, 'pub', 0, -0.2), ('A', t, 'pub', 0, -0.3),
               ('B', t, 'pub', 0, +0.1), ('B', t, 'pub', 0, -0.1)]
    for var, th, pr, ms, msz in configs:
        key = '%s_thick%.2f_press-%s_dM%+.1f_dMdz%+.2f' % (var, th, pr, ms, msz)
        P = prepare(d, var, th, ms, msz, pr)
        fun = lambda A, p, s, P=P: nll(P, A, p, s)
        r = {}
        for mode in ('fixed', 'prior', 'free'):
            b = fit(fun, mode)
            f0 = fit(fun, mode, 0.0); f1 = fit(fun, mode, 1.0)
            prof = profile_p(fun, mode, grid)
            lo, hi, edge = interval(grid, prof, 1.0)
            lo2, hi2, edge2 = interval(grid, prof, 4.0)
            r[mode] = dict(best=b, m2lnL_p0=f0['m2lnL'], m2lnL_p1=f1['m2lnL'], A_p0=f0['A'], A_p1=f1['A'],
                           sint_p0=f0['sint'], sint_p1=f1['sint'],
                           delta_m2lnL_p1_minus_p0=f1['m2lnL'] - f0['m2lnL'],
                           p_68=[lo, hi], p_95=[lo2, hi2], interval_hits_grid_edge=edge or edge2)
            print('%-40s A-%-6s p=%+.2f [68%%: %+.2f,%+.2f] [95%%: %+.2f,%+.2f] sint=%.3f A=%.2fe-10 | -2lnL(p=1)-(p=0)=%+.1f'
                  % (key, mode, b['p'], lo, hi, lo2, hi2, b['sint'], b['A'] / 1e-10, f1['m2lnL'] - f0['m2lnL']))
        pw = power(P)
        r['power'] = dict(frac_gN_below_a0const=float(np.mean(pw['y_const'] < 1)),
                          frac_gN_below_a0H=float(np.mean(pw['y_H'] < 1)),
                          median_gN_over_a0const=float(np.median(pw['y_const'])),
                          quartiles_gN_over_a0const=[float(x) for x in np.percentile(pw['y_const'], [25, 75])],
                          median_dlogv_p0_to_p1=float(np.median(pw['dlogv_p0_to_p1'])),
                          median_sigma_logv=float(np.median(pw['sigma'])),
                          fisher_sigma_p_noscatter=pw['fisher_sigma_p'])
        runs[key] = r
        print('    power: frac gN<a0(const)=%.2f, frac gN<a0_H=%.2f, median gN/a0=%.2f (IQR %.2f-%.2f), median dlogv(p0->p1)=%.3f dex, median sigma_logv=%.3f, Fisher sigma_p(no scatter)=%.2f'
              % tuple([r['power'][k] for k in ('frac_gN_below_a0const', 'frac_gN_below_a0H', 'median_gN_over_a0const')] + r['power']['quartiles_gN_over_a0const'] + [r['power'][k] for k in ('median_dlogv_p0_to_p1', 'median_sigma_logv', 'fisher_sigma_p_noscatter')]))
    # variant C
    funC = lambda A, p, s: nll_C(d, A, p, s)
    rC = {}
    for mode in ('fixed', 'prior', 'free'):
        b = fit(funC, mode); f0 = fit(funC, mode, 0.0); f1 = fit(funC, mode, 1.0)
        prof = profile_p(funC, mode, grid); lo, hi, e1 = interval(grid, prof, 1.0); lo2, hi2, e2 = interval(grid, prof, 4.0)
        rC[mode] = dict(best=b, delta_m2lnL_p1_minus_p0=f1['m2lnL'] - f0['m2lnL'], p_68=[lo, hi], p_95=[lo2, hi2],
                        interval_hits_grid_edge=e1 or e2)
        print('%-40s A-%-6s p=%+.2f [68%%: %+.2f,%+.2f] [95%%: %+.2f,%+.2f] sint=%.3f A=%.2fe-10 | -2lnL(p=1)-(p=0)=%+.1f'
              % ('C_paper_decomposition_RAR', mode, b['p'], lo, hi, lo2, hi2, b['sint'], b['A'] / 1e-10, f1['m2lnL'] - f0['m2lnL']))
    runs['C_paper_decomposition_RAR'] = rC
    # galaxy bootstrap for the main configuration, A free and A prior
    P = prepare(d, 'A', t, 0, 0, 'pub')
    PB = prepare(d, 'B', t, 0, 0, 'pub')
    boots = {'free': [], 'prior': []}
    n = len(d['z'])
    for b in range(200):
        idx = rng.integers(0, n, n)
        Pb = {k: (v[idx] if isinstance(v, np.ndarray) else v) for k, v in P.items()}
        for mode in boots:
            boots[mode].append(fit(lambda A, p, s, Pb=Pb: nll(Pb, A, p, s), mode)['p'])
    for mode, arr in boots.items():
        arr = np.array(arr)
        q = np.percentile(arr, [2.5, 16, 50, 84, 97.5])
        print('bootstrap (200 galaxy resamples) main A-%s: p percentiles 2.5/16/50/84/97.5 = %s' % (mode, np.round(q, 2)))
        runs['bootstrap_main_' + mode] = [float(x) for x in q]
    # redshift-binned a0 (variant A main, A free per bin == fit log a0 per bin with p=0)
    bins = [(0.6, 1.0), (1.0, 1.6), (1.6, 2.2), (2.2, 2.6)]
    for vname, P in (('A', P), ('B', PB)):
      binned = []
      for lo_, hi_ in bins:
          m = (d['z'] >= lo_) & (d['z'] < hi_)
          Pm = {k: (v[m] if isinstance(v, np.ndarray) else v) for k, v in P.items()}
          f = lambda A, p, s, Pm=Pm: nll(Pm, A, 0.0, s)
          prof = []
          lAgrid = np.arange(-1.5, 1.51, 0.02)
          for lA in lAgrid:
              rr = minimize_scalar(lambda s: f(A_SPARC * 10 ** lA, 0, abs(s) + 1e-6), bounds=(0, 0.3), method='bounded')
              prof.append(2 * rr.fun)
          prof = np.array(prof); j = prof.argmin(); ok = lAgrid[prof - prof.min() <= 1]
          zm = float(np.median(d['z'][m]))
          binned.append(dict(z_range=[lo_, hi_], n=int(m.sum()), z_median=zm,
                             a0_best=float(A_SPARC * 10 ** lAgrid[j]), a0_68=[float(A_SPARC * 10 ** ok.min()), float(A_SPARC * 10 ** ok.max())],
                             a0_H_track_pred=float(A_SPARC * L.E(zm))))
          print(vname, 'bin z %.1f-%.1f n=%d zmed=%.2f: a0 = %.2f [%.2f, %.2f] e-10  (H-tracking from 1.20: %.2f)'
                % (lo_, hi_, m.sum(), zm, A_SPARC * 10 ** lAgrid[j] / 1e-10, A_SPARC * 10 ** ok.min() / 1e-10, A_SPARC * 10 ** ok.max() / 1e-10, A_SPARC * L.E(zm) / 1e-10))
      runs['binned_a0_variant' + vname] = binned
    res['runs'] = runs
    return res


if __name__ == '__main__':
    out = main(sys.argv[1])
    with open(sys.argv[2] if len(sys.argv) > 2 else 'outputs/rc100_fit.json', 'w') as fh:
        json.dump(out, fh, indent=1, default=float)
