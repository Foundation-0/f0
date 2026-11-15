"""
Independent recomputation for gravity C-23c, C-26, C-27 (the ~185 km/s scale).
Written from the formulas stated in CLAIMS.md, not from the repository's functions.
The only thing imported from the repository is the hard-coded 126-row data table
(wave7.build_catalog), because that table is the claim's stated input.
Usage: python3 -I g185_independent.py <path-to-gravity-clone>
"""
import math, sys, importlib.util
import numpy as np
from scipy import integrate, optimize

G = 6.67430e-11; MSUN = 1.98847e30; MPC = 3.085677581491367e22; KPC = MPC / 1e3
C = 299792458.0; A0 = 1.20e-10

# ---------- Part 1: Planck 2018 sigma(R), M_*, sigma_* ----------
def cosmo(h=0.6736, obh2=0.02237, och2=0.1200, mnuh2=0.00064, ns=0.9649, s8=0.8111, tcmb=2.7255):
    omh2 = obh2 + och2 + mnuh2
    return dict(h=h, obh2=obh2, omh2=omh2, om=omh2 / h**2, ob=obh2 / h**2, ns=ns, s8=s8, tcmb=tcmb)

def T_eh_nowiggle(k, c):
    """Eisenstein & Hu 1998 eqs 26, 28-31 (zero-baryon-oscillation shape). k in 1/Mpc."""
    om, ob, h, omh2, obh2 = c['om'], c['ob'], c['h'], c['omh2'], c['obh2']
    th = c['tcmb'] / 2.7
    s = 44.5 * np.log(9.83 / omh2) / np.sqrt(1 + 10 * obh2**0.75)
    al = 1 - 0.328 * np.log(431 * omh2) * (ob / om) + 0.38 * np.log(22.3 * omh2) * (ob / om)**2
    gam = om * h * (al + (1 - al) / (1 + (0.43 * k * s)**4))
    q = (k / h) * th**2 / gam
    L0 = np.log(2 * np.e + 1.8 * q); C0 = 14.2 + 731.0 / (1 + 62.5 * q)
    return L0 / (L0 + C0 * q * q)

def T_eh_full(k, c):
    """Eisenstein & Hu 1998 full fitting formula with baryon oscillations (eqs 2-24). k in 1/Mpc."""
    om, ob, h, omh2, obh2 = c['om'], c['ob'], c['h'], c['omh2'], c['obh2']
    th = c['tcmb'] / 2.7
    oc = om - ob; fb = ob / om; fc = oc / om
    zeq = 2.50e4 * omh2 * th**-4
    keq = 7.46e-2 * omh2 * th**-2
    b1 = 0.313 * omh2**-0.419 * (1 + 0.607 * omh2**0.674)
    b2 = 0.238 * omh2**0.223
    zd = 1291 * omh2**0.251 / (1 + 0.659 * omh2**0.828) * (1 + b1 * obh2**b2)
    R = lambda z: 31.5 * obh2 * th**-4 * (1e3 / z)
    Req, Rd = R(zeq), R(zd)
    s = (2 / (3 * keq)) * np.sqrt(6 / Req) * np.log((np.sqrt(1 + Rd) + np.sqrt(Rd + Req)) / (1 + np.sqrt(Req)))
    ksilk = 1.6 * obh2**0.52 * omh2**0.73 * (1 + (10.4 * omh2)**-0.95)
    q = k / (13.41 * keq)
    a1 = (46.9 * omh2)**0.670 * (1 + (32.1 * omh2)**-0.532)
    a2 = (12.0 * omh2)**0.424 * (1 + (45.0 * omh2)**-0.582)
    alpha_c = a1**(-fb) * a2**(-fb**3)
    bb1 = 0.944 / (1 + (458 * omh2)**-0.708); bb2 = (0.395 * omh2)**-0.0266
    beta_c = 1 / (1 + bb1 * (fc**bb2 - 1))
    def T0(k, ac, bc):
        q = k / (13.41 * keq)
        Cc = 14.2 / ac + 386 / (1 + 69.9 * q**1.08)
        L = np.log(np.e + 1.8 * bc * q)
        return L / (L + Cc * q * q)
    f = 1 / (1 + (k * s / 5.4)**4)
    Tc = f * T0(k, 1, beta_c) + (1 - f) * T0(k, alpha_c, beta_c)
    y = (1 + zeq) / (1 + zd)
    Gy = y * (-6 * np.sqrt(1 + y) + (2 + 3 * y) * np.log((np.sqrt(1 + y) + 1) / (np.sqrt(1 + y) - 1)))
    alpha_b = 2.07 * keq * s * (1 + Rd)**-0.75 * Gy
    beta_b = 0.5 + fb + (3 - 2 * fb) * np.sqrt((17.2 * omh2)**2 + 1)
    beta_node = 8.41 * omh2**0.435
    st = s / (1 + (beta_node / (k * s))**3)**(1 / 3)
    j0 = np.sinc(k * st / np.pi)
    Tb = (T0(k, 1, 1) / (1 + (k * s / 5.2)**2) + alpha_b / (1 + (beta_b / (k * s))**3) * np.exp(-(k / ksilk)**1.4)) * j0
    return fb * Tb + fc * Tc

def W(x):
    x = np.asarray(x, float)
    out = np.where(x < 1e-3, 1 - x * x / 10, 3 * (np.sin(x) - x * np.cos(x)) / np.where(x == 0, 1, x)**3)
    return out

def make_sigma(c, T):
    lk = np.linspace(np.log(1e-6), np.log(1e3), 40001); k = np.exp(lk)
    P = k**c['ns'] * T(k, c)**2
    def raw(Rm):
        return math.sqrt(integrate.simpson(k**3 * P * W(k * Rm)**2 / (2 * np.pi**2), x=lk))
    norm = c['s8'] / raw(8.0 / c['h'])
    return lambda Rm: norm * raw(Rm)

def growth(z, om):
    ol = 1 - om
    E = lambda a: math.sqrt(om / a**3 + ol)
    f = lambda a: 1.0 / (a * E(a))**3
    D = lambda a: 2.5 * om * E(a) * integrate.quad(f, 0, a)[0]
    return D(1 / (1 + z)) / D(1.0)

def sigma_star(c, T, z=0.0, delta_c=1.686, Delta=200.0, ref='crit'):
    sig = make_sigma(c, T)
    D = growth(z, c['om'])
    Rs = optimize.brentq(lambda R: sig(R) * D - delta_c, 1e-3, 60.0, xtol=1e-10)
    H0 = 100 * c['h'] * 1e3 / MPC
    rhoc0 = 3 * H0**2 / (8 * math.pi * G)
    M = 4 / 3 * math.pi * (Rs * MPC)**3 * c['om'] * rhoc0
    Ez2 = c['om'] * (1 + z)**3 + 1 - c['om']
    rho_ref = rhoc0 * Ez2 if ref == 'crit' else rhoc0 * c['om'] * (1 + z)**3
    rD = (3 * M / (4 * math.pi * Delta * rho_ref))**(1 / 3)
    V = math.sqrt(G * M / rD) / 1e3
    return Rs, M / MSUN, V, V / math.sqrt(2)

# ---------- Part 2: the other three scales ----------
def v_milgrom(Mb_msun): return (G * Mb_msun * MSUN * A0)**0.25 / 1e3

def sigma_cooling(Delta, c, gff=1.2):
    """Free-free cooling time = 1/H0 at overdensity Delta x rho_crit, as stated in C-27 (Rees & Ostriker 1977 scaling)."""
    hbar = 1.054571817e-34; me = 9.1093837015e-31; mp = 1.67262192369e-27; alpha = 1 / 137.035999084
    H0 = 100 * c['h'] * 1e3 / MPC; rhoc0 = 3 * H0**2 / (8 * math.pi * G)
    # emissivity eps_ff = Cff * ne*ni * sqrt(kT): Cff = (16/3) sqrt(2pi/3) gff alpha^3 lambdabar_e^2 c sqrt(me c^2)
    Cff = (16 / 3) * math.sqrt(2 * math.pi / 3) * gff * alpha**3 * (hbar / (me * C))**2 * C * math.sqrt(me * C**2)
    ne = (c['ob'] / c['om']) * Delta * rhoc0 / (1.14 * mp)
    # (3/2) n_tot kT / (Cff ne ni sqrt(kT)) = 1/H0, with n_tot/ni ~ 2/1.15..: keep the claim's own closure
    sqrt_kT = (1.15 * Cff * ne / H0) / 3.0
    return math.sqrt(sqrt_kT**2 / (0.60 * mp)) / 1e3

# ---------- Part 3: the 60-system comparison ----------
def nu(y):
    sy = math.sqrt(max(y, 0.0))
    if sy == 0: return 1.0
    return 1.0 if sy > 40 else 1.0 / (1.0 - math.exp(-sy))

def model_ratios(sigma, sigJ, dust):
    """Returns (R_acc, R_mass) at 250 kpc for the two-branch model g_tot = g_b nu(g_b/a0) + f_trap*dust*g_b.
    R_acc  = g_tot / (g_b nu(g_b/a0))           -- total acceleration over MOND acceleration from the baryons
    R_mass = g_N' / g_b, g_N' nu(g_N'/a0)=g_tot -- baryonic mass MOND would need, over the baryonic mass present
    """
    if sigma <= sigJ: return 1.0, 1.0
    f = 1 - (sigJ / sigma)**2
    yt = 2 * (sigma * 1e3)**2 / (250 * KPC) / A0          # everything in units of a0
    yb = optimize.brentq(lambda y: y * (nu(y) + f * dust) - yt, 1e-12, yt, xtol=1e-15, rtol=1e-14)
    yN = optimize.brentq(lambda y: y * nu(y) - yt, 1e-12, yt, xtol=1e-15, rtol=1e-14)
    return yt / (yb * nu(yb)), yN / yb

def chi2(rows, pred):
    """Same statistic as the claim states (orthogonal distance in log sigma / log R, with the x-y slope 'cov')."""
    tot = 0.0
    for r in rows:
        xi, yi, sx, sy, a = math.log10(r['sig']), r['logR'], r['sx'], r['sy'], r['cov']
        us = xi + np.arange(-14, 15) / 4.0 * sx
        q = [((xi - u) / sx)**2 + (((yi - a * (xi - u)) - pred(10**u)) / sy)**2 for u in us]
        tot += min(q)
    return tot

def main(repo):
    c = cosmo()
    print("== Part 1: nonlinear collapse scale at z=0 ==")
    for name, T in [("EH98 no-wiggle (the form the claim uses)", T_eh_nowiggle), ("EH98 full, with baryon oscillations", T_eh_full)]:
        Rs, M, V, s1 = sigma_star(c, T)
        print(f"  {name:44s} R*={Rs:.4f} Mpc  M*={M:.3e} Msun  V200={V:.2f}  sigma*={s1:.2f} km/s")
    print("  -- convention sensitivity (no-wiggle shape) --")
    for lab, kw in [("Delta=200 crit (claim)", {}), ("Delta=200 mean", dict(ref='mean')), ("Delta=500 crit", dict(Delta=500.)),
                    ("Delta=102 crit (virial, LCDM z=0)", dict(Delta=102.)), ("delta_c=1.676 (LCDM z=0)", dict(delta_c=1.676))]:
        Rs, M, V, s1 = sigma_star(c, T_eh_nowiggle, **kw); print(f"    {lab:36s} sigma*={s1:7.2f} km/s  (M*={M:.2e})")
    for s8 in (0.8051, 0.8111, 0.8171, 0.76, 0.83):
        cc = cosmo(s8=s8); print(f"    sigma8={s8:.4f}                       sigma*={sigma_star(cc, T_eh_nowiggle)[3]:7.2f} km/s")
    for z in (0.5, 1.0, 3.0, 5.0):
        print(f"    z={z}: sigma*={sigma_star(c, T_eh_nowiggle, z=z)[3]:.2f} km/s")

    print("== Part 2: the other scales and what they depend on ==")
    for Mb in (3e10, 6e10, 1e11): print(f"  Milgrom (G Mb a0)^(1/4): Mb={Mb:.0e} -> {v_milgrom(Mb):.2f} km/s")
    for D in (200, 500, 1000, 2500): print(f"  cooling scale at Delta={D:5d}: {sigma_cooling(D, c):8.2f} km/s   (ratio to Delta: {sigma_cooling(D, c)/D:.5f})")

    print("== Part 3: the 60-system test ==")
    spec = importlib.util.spec_from_file_location("w7data", repo + "/wave7_group_cluster_threshold_audit.py")
    w7 = importlib.util.module_from_spec(spec); spec.loader.exec_module(w7)
    rows = w7.build_catalog()
    clean = [r for r in rows if r['cat'] not in ("Milgrom2019_opt", "Milgrom2019_rich")]
    print("  rows:", len(rows), "clean:", len(clean), {k: sum(1 for r in clean if r['cat'] == k) for k in sorted({r['cat'] for r in clean})})
    dust = (1 - 0.105) / 0.105
    sJ = 185.59
    for lab, idx in (("R_acc  (what the scripts compare)", 0), ("R_mass (what the data table holds)", 1)):
        f = lambda s, i=idx, j=sJ: math.log10(model_ratios(s, j, dust)[i])
        print(f"  sigma_J=185.59, dust=8.524: chi2 with {lab}: {chi2(clean, f):8.2f}  (N=60)")
    print("  profile over sigma_J (clean 60):")
    print("   sigJ   chi2[R_acc]  chi2[R_mass]")
    for j in (130, 150, 170, 180, 185.59, 190, 200, 220, 250, 300, 350, 400, 500):
        a = chi2(clean, lambda s: math.log10(model_ratios(s, j, dust)[0]))
        m = chi2(clean, lambda s: math.log10(model_ratios(s, j, dust)[1]))
        print(f"   {j:6.2f}  {a:9.2f}   {m:9.2f}")
    print("  model ratios at sigma_J=185.59:")
    print("   sigma  g_tot/a0   R_acc   R_mass")
    for s in (200, 250, 300, 400, 600, 800, 1000, 1300):
        ra, rm = model_ratios(s, sJ, dust); print(f"   {s:5d}  {2*(s*1e3)**2/(250*KPC)/A0:7.3f}  {ra:6.3f}  {rm:6.3f}")
    print("  data table, binned median R by sigma (clean 60):")
    for lo, hi in ((60, 150), (150, 230), (230, 390), (390, 600), (600, 900), (900, 1200), (1200, 1500)):
        sub = [r for r in clean if lo <= r['sig'] < hi]
        if sub: print(f"   {lo:5d}-{hi:5d}  n={len(sub):2d}  median R={np.median([r['R'] for r in sub]):6.3f}  cats={sorted({r['cat'] for r in sub})}")

if __name__ == "__main__":
    main(sys.argv[1])
