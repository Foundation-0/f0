"""Shared physics for the neutrino-model tests. SI inside, Msun/kpc/keV/eV at the edges."""
import math, numpy as np
from scipy.optimize import brentq
from scipy.integrate import quad
G = 6.67430e-11; MSUN = 1.98847e30; KPC = 3.085677581491367e19; MP = 1.67262192e-27; KEV = 1.602176634e-16
H = 6.62607015e-34; EV_KG = 1.78266192e-36; C = 299792458.0
MU = 0.60                                      # mean molecular weight for sigma^2 = kT/(mu m_p)
OBH2 = 0.02237                                 # Planck 2018 Omega_b h^2
M_AB_G2 = 93.14 * OBH2                          # eV: thermal-relic mass whose Omega equals Omega_b (g=2, one species) = 2.0836
def sigma_T(kT_keV): return math.sqrt(kT_keV * KEV / (MU * MP))           # m/s
# ---------------- interpolating functions nu(y), y = g_N/a0
def nu_exp(y): y = np.asarray(y, float); return 1.0 / (1.0 - np.exp(-np.sqrt(y)))
def nu_simple(y): y = np.asarray(y, float); return 0.5 + np.sqrt(0.25 + 1.0 / y)
def nu_standard(y): y = np.asarray(y, float); return np.sqrt(0.5 + np.sqrt(0.25 + 1.0 / y ** 2))
NU = {"exp (RAR)": nu_exp, "simple": nu_simple, "standard": nu_standard}
def gtot_of_gN(gN, a0=1.2e-10, nu=nu_exp, ge=0.0):
    """1D QUMOND-style external field approximation (Famaey & McGaugh 2012, eq. for EFE):
       g = nu(|gN+ge|/a0)(gN+ge) - nu(ge/a0) ge"""
    if ge <= 0: return nu(gN / a0) * gN
    return nu((gN + ge) / a0) * (gN + ge) - nu(ge / a0) * ge
def solve_gN(gtot, a0=1.2e-10, nu=nu_exp, ge=0.0):
    f = lambda lg: math.log(gtot_of_gN(10 ** lg, a0, nu, ge)) - math.log(gtot)
    return 10 ** brentq(f, -18, math.log10(gtot) + 0.5)
# ---------------- NFW
def mnfw(x): return np.log1p(x) - x / (1 + x)
def nfw_two_point(r1, M1, r2, M2):
    """rs [kpc], rho_s [Msun/kpc^3] of the NFW through (r1,M1),(r2,M2), r1<r2"""
    q = M1 / M2
    f = lambda lrs: mnfw(r1 / 10 ** lrs) / mnfw(r2 / 10 ** lrs) - q
    lo, hi = -1.0, 5.0
    if f(lo) * f(hi) > 0: return None
    rs = 10 ** brentq(f, lo, hi)
    rhos = M2 / (4 * math.pi * rs ** 3 * mnfw(r2 / rs))
    return rs, rhos
def nfw_M(r, rs, rhos): return 4 * math.pi * rhos * rs ** 3 * mnfw(np.asarray(r) / rs)
def nfw_dphi(r, rs, rhos):
    """Phi(r) - Phi(0) in (m/s)^2"""
    x = np.asarray(r, float) / rs
    return 4 * math.pi * G * rhos * MSUN / KPC ** 3 * (rs * KPC) ** 2 * (1 - np.log1p(x) / np.where(x > 0, x, 1e-12))
# ---------------- Fermi-Dirac
_eta = np.linspace(-60, 40, 4001)
def _f32(e):
    # f_{3/2}(e^eta) = (2/sqrt pi) int_0^inf sqrt(x)/(exp(x-eta)+1) dx  (classical limit e^eta)
    if e < -30: return math.exp(e)
    return 2 / math.sqrt(math.pi) * quad(lambda x: math.sqrt(x) / (math.exp(min(x - e, 700)) + 1), 0, max(e, 0) + 60, limit=200)[0]
_F32 = np.array([_f32(e) for e in _eta])
def f32(eta): return np.interp(eta, _eta, _F32, left=0.0)
def rho_fermi(r, m_eV, g, sig, dphi_fun, eta0=0.0):
    """isothermal FD density [Msun/kpc^3]; eta0 = 0 means central occupation 1/2 (primordial maximum of a thermal relic)"""
    m = m_eV * EV_KG
    pref = g * m ** 4 / H ** 3 * (2 * math.pi * sig ** 2) ** 1.5      # kg/m^3 per unit f32
    return pref * f32(eta0 - dphi_fun(r) / sig ** 2) / MSUN * KPC ** 3
def halo_mass(rmax, m_eV, g, sig, dphi_fun, eta0=0.0, n=600):
    r = np.concatenate([[0], np.geomspace(1e-3, rmax, n)])
    rho = rho_fermi(r, m_eV, g, sig, dphi_fun, eta0)
    dm = 4 * math.pi * r ** 2 * rho
    return np.concatenate([[0], np.cumsum(0.5 * (dm[1:] + dm[:-1]) * np.diff(r))]), r
# ---------------- phase-space limits
def m_pauli(rho_msun_kpc3, sig, g):
    rho = rho_msun_kpc3 * MSUN / KPC ** 3
    return (rho * H ** 3 / (g * (2 * math.pi * sig ** 2) ** 1.5)) ** 0.25 / EV_KG
def m_tg(rho, sig, g): return 2 ** 0.25 * m_pauli(rho, sig, g)
