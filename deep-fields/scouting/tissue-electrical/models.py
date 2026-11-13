"""Cole-Cole models used by the three tissue databases compared in this pilot.

Every function returns the relative permittivity eps' and the conductivity sigma (S/m) at frequency f (Hz),
from the complex relative permittivity eps* = eps' - j eps'' with sigma = 2 pi f eps0 eps''.
"""
import numpy as np

EPS0 = 8.8541878128e-12  # F/m


def _split(f, e):
    f = np.asarray(f, float)
    return e.real, -e.imag * 2 * np.pi * f * EPS0


def gabriel(f, p):
    """Four-term Cole-Cole model of Gabriel, Lau and Gabriel (1996c), in the units of the IT'IS tables.

    p holds ef, sig (S/m), del1..del4, alf1..alf4 and tau1 (ps), tau2 (ns), tau3 (us), tau4 (ms).
    The IT'IS "alternative" (Sasaki 2014) table uses the same columns and units.
    """
    f = np.asarray(f, float)
    w = 2 * np.pi * f
    e = np.full(f.shape, float(p["ef"]), complex)
    for n, unit in ((1, 1e-12), (2, 1e-9), (3, 1e-6), (4, 1e-3)):
        d = float(p[f"del{n}"])
        if d:
            e = e + d / (1 + (1j * w * float(p[f"tau{n}"]) * unit) ** (1 - float(p[f"alf{n}"])))
    e = e + float(p["sig"]) / (1j * w * EPS0)
    return _split(f, e)


def relaxation_terms(f, eps_inf, sigma_dc, terms):
    """eps_inf + sigma_dc/(j w eps0) + sum of delta / (1 + (j f / f_r)^(1 - alpha)); terms = [(delta, f_r Hz, alpha)].

    This is the form of Sasaki et al. (2014), Table 2, and of the NICT parametric models.
    """
    f = np.asarray(f, float)
    w = 2 * np.pi * f
    e = np.full(f.shape, float(eps_inf), complex) + float(sigma_dc) / (1j * w * EPS0)
    for delta, fr, alpha in terms:
        if delta:
            e = e + delta / (1 + (1j * f / fr) ** (1 - alpha))
    return _split(f, e)


def sasaki(f, row):
    """A row of Sasaki, Wake and Watanabe (2014), Table 2 (see sasaki2014_table2.tsv)."""
    return relaxation_terms(f, row["eps_s1"], row["sigma_dc_S_per_m"], [
        (row["delta1"], row["f_r1_GHz"] * 1e9, row["alpha1"]),
        (row["delta2"], row["f_r2_MHz"] * 1e6, row["alpha2"]),
    ])


def nict(f, row):
    """A row of the NICT parametric-model CSV."""
    return relaxation_terms(f, row["epsilon_rinf"], row["sigma_S"], [
        (row["delta_1"], row["f_r1"], row["alpha_1"]),
        (row["delta_2"], row["f_r2"], row["alpha_2"]),
    ])


def water_static_permittivity(t_celsius):
    """Static relative permittivity of pure water, Malmberg and Maryott (1956), valid 0-100 C."""
    t = t_celsius
    return 87.740 - 0.40008 * t + 9.398e-4 * t**2 - 1.410e-6 * t**3


def water_relaxation_time_ps(t_celsius):
    """Primary (Debye) relaxation time of pure water, from the relaxation frequency gamma_1 of the double-Debye model of
    Liebe, Hufford and Manabe (1991), eq. (4a): gamma_1 = 20.20 + 146.4 th + 316 th^2 GHz, th = 1 - 300/(273.15 + T)."""
    th = 1 - 300 / (273.15 + np.asarray(t_celsius, float))
    gamma1 = (20.20 + 146.4 * th + 316 * th**2) * 1e9
    return 1e12 / (2 * np.pi * gamma1)
