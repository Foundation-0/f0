"""Threshold model under test (independent reimplementation; imports nothing from the repository).
Source: gravity@8f96c4b:wave10_covariant_jeans_unification.py:44-53,219-231 (nu_rar, f_trap, R = DUST_TO_B_R2500).
sigma_J(z) for set A is read from gravity@8f96c4b:results/wave10_covariant_jeans_certificates.json
(press_schechter_redshift_trajectory, sigma_1D_star_kms) and interpolated linearly in (z, log sigma)."""
import math
import numpy as np

G = 6.67430e-11; MSUN = 1.98847e30; KPC = 3.085677581491367e19; MPC = 1e3 * KPC; A0 = 1.2e-10

def nu(y):
    y = np.asarray(y, float)
    return 1.0 / (1.0 - np.exp(-np.sqrt(y)))

SJ_TRAJ_Z = np.array([0.0, 0.3, 0.5, 1.0, 2.0, 3.0, 5.0])
SJ_TRAJ = np.array([185.59, 139.28, 114.36, 69.92, 27.33, 11.36, 2.22])

def sigJ_A(z):
    return float(np.exp(np.interp(z, SJ_TRAJ_Z, np.log(SJ_TRAJ))))

PARAMS = {"A": dict(sigJ0=185.59, R=8.524), "B": dict(sigJ0=200.0, R=4.0)}

def sigJ(p, z=0.0, evolve=True):
    s0 = PARAMS[p]["sigJ0"]
    if not evolve:
        return s0
    return s0 * sigJ_A(z) / 185.59      # B scaled by the same growth-factor trajectory

def ftrap(sigma, sj):
    sigma = np.asarray(sigma, float)
    return np.clip(1.0 - (sj / sigma) ** 2, 0.0, None)

def ratio(p, y, sigma, z=0.0, evolve=True):
    """Predicted g_tot/g_b = M_tot(<r)/M_b(<r) at a radius where g_b/a0 = y."""
    return nu(y) + PARAMS[p]["R"] * ftrap(sigma, sigJ(p, z, evolve))

def y_of(Mb_msun, r_kpc):
    return G * np.asarray(Mb_msun) * MSUN / (np.asarray(r_kpc) * KPC) ** 2 / A0

def sigma_from_mass(M_msun, r_kpc):
    """Repository convention g_tot = 2 sigma^2 / r -> sigma = sqrt(G M / (2 r)), km/s."""
    return np.sqrt(G * np.asarray(M_msun) * MSUN / (2 * np.asarray(r_kpc) * KPC)) / 1e3

def M_threshold(sj_kms):
    """Baryonic mass where deep-MOND BTFR gives V_flat/sqrt2 = sigma_J."""
    V = math.sqrt(2) * sj_kms * 1e3
    return V ** 4 / (G * A0) / MSUN

if __name__ == "__main__":
    for p in "AB":
        print(p, PARAMS[p], "M_thr = %.3e" % M_threshold(PARAMS[p]["sigJ0"]))
    for z in [0, 0.5, 1, 1.5, 2, 2.5]:
        print("z=%.1f sigJ_A=%.2f sigJ_B(scaled)=%.2f" % (z, sigJ("A", z), sigJ("B", z)))
    # corrupt-input check: nu must fall with y and approach 1
    assert nu(100.0) < 1.01 and nu(0.01) > 10
