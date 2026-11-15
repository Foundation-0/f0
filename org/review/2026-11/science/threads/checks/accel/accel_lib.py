"""Independent physics library for the acceleration-evolution test.

Written from first principles for this thread. It does not import or copy
S/repos/gravity/acceleration-evolution/*.py.

Units: kpc, km/s, Msun internally; accelerations converted to m/s^2.
"""
import math
import csv
import numpy as np
from scipy.special import i0, i1, k0, k1

G_KPC = 4.300917e-6            # kpc (km/s)^2 / Msun
KPC_M = 3.0856775814913673e19   # m
C_MS = 299792458.0
MPC_M = 3.0856775814913673e22
G_SI = 6.67430e-11
MSUN = 1.98840987e30


def E(z, om=0.315):
    """H(z)/H0, flat matter + Lambda, radiation neglected."""
    z = np.asarray(z, float)
    return np.sqrt(om * (1 + z) ** 3 + 1 - om)


def nu(y):
    """McGaugh et al. 2016 / Milgrom 'simple-exponential' interpolation: g = nu(gN/a0) gN."""
    y = np.asarray(y, float)
    return 1.0 / (-np.expm1(-np.sqrt(y)))


def accel_si(v_kms, r_kpc):
    """v^2/r in m/s^2."""
    return (np.asarray(v_kms) * 1e3) ** 2 / (np.asarray(r_kpc) * KPC_M)


def v2_expdisk(R, Md, Rd):
    """Thin exponential disc (Freeman 1970): v^2 = 2 G Md/Rd * y^2 [I0K0 - I1K1], y = R/(2Rd)."""
    y = R / (2.0 * Rd)
    return 2.0 * G_KPC * Md / Rd * y ** 2 * (i0(y) * k0(y) - i1(y) * k1(y))


def v2_bulge(R, Mb, Re_b=1.0):
    """Spherical bulge approximated by a Hernquist sphere with the same projected R_e (a = Re/1.8153)."""
    a = Re_b / 1.8153
    return G_KPC * Mb * R / (R + a) ** 2


def vbar2(R, Mbar, Mbul, Re_disk, thick=1.0):
    """Newtonian baryonic v^2 at radius R. Disc = Mbar - Mbul, exponential with Rd = Re/1.678.
    'thick' multiplies the disc v^2 to mimic finite thickness (1 = thin)."""
    Md = np.maximum(Mbar - Mbul, 0.0)
    Rd = Re_disk / 1.6783
    return thick * v2_expdisk(R, Md, Rd) + v2_bulge(R, Mbul)


def v_mond(R, Mbar, Mbul, Re_disk, a0, thick=1.0):
    """Velocity predicted by the algebraic RAR g = nu(gN/a0) gN at R (km/s)."""
    v2n = vbar2(R, Mbar, Mbul, Re_disk, thick)
    gN = accel_si(np.sqrt(v2n), R)
    g = nu(gN / a0) * gN
    return np.sqrt(g * R * KPC_M) / 1e3, gN


def tacconi18_mu(z, dms, logms):
    """Tacconi et al. 2018 Table 3b 'best' beta=2 (S14 MS), size term omitted:
    log Mmolgas/M* = 0.12 - 3.62 (log(1+z) - 0.66)^2 + 0.53 dMS - 0.35 (logM* - 10.7)."""
    return 10 ** (0.12 - 3.62 * (np.log10(1 + z) - 0.66) ** 2 + 0.53 * dms - 0.35 * (logms - 10.7))


def load_rc100(path):
    rows = [r for r in csv.DictReader(l for l in open(path) if not l.startswith('#'))]
    out = {}
    for k in rows[0]:
        if k == 'name':
            out[k] = [r[k] for r in rows]
        else:
            out[k] = np.array([float(r[k]) for r in rows])
    return out


def load_ubler(path):
    z, lms, lmb, v, s = [], [], [], [], []
    for line in open(path):
        if line.startswith('#') or not line.strip():
            continue
        f = line.rstrip('\n').split('\t')
        if len(f) < 7:
            continue
        try:
            vals = [float(x) for x in f[2:7]]
        except ValueError:
            continue
        z.append(vals[0]); lms.append(vals[1]); lmb.append(vals[2]); v.append(vals[3]); s.append(vals[4])
    return {k: np.array(x) for k, x in zip(('z', 'logMs', 'logMb', 'V', 'sig0'), (z, lms, lmb, v, s))}
