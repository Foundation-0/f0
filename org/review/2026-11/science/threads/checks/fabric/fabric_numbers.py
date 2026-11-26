"""Numbers for the woven hypothesis: one acceleration scale for galaxies plus one light fermion of mass m populated
at a fraction chi of the thermal relic number. Each line says what it uses. Scalings from the halo study:
a halo at its packing limit around a galaxy with flat speed 200 km/s and a 5 kpc core holds 0.95 M_b inside 300 kpc
for a fully thermal 12 eV species; packing capacity scales as chi m^4."""
import math
H, EV, MSUN, KPC, KB = 6.62607015e-34, 1.78266192e-36, 1.98847e30, 3.085677581491367e19, 1.380649e-23
MP = 1.67262192369e-27
def line(m, chi, label):
    K = m * chi ** 0.25                    # thermal-equivalent packing mass
    A = chi * m                            # abundance-equivalent mass
    om = A / 93.14                         # Omega h^2
    ratio = A / 2.084                      # cosmic extra-to-baryon ratio (Omega_b h^2 = 0.02237)
    gal = 0.95 * (K / 12.0) ** 4           # halo/baryons inside 300 kpc of a 200 km/s galaxy
    kT = 8.0                               # keV
    sig = math.sqrt(kT * 1.602176634e-16 / (0.60 * MP))
    rho0 = 2 * chi * (m * EV) ** 4 * (2 * math.pi * sig ** 2) ** 1.5 * 0.7651 / H ** 3   # g = 2, f_3/2(0) = 0.7651
    rho0_msun_kpc3 = rho0 / MSUN * KPC ** 3
    v0 = 158.4 / m                         # km/s today, relic mean speed for a thermal momentum distribution
    print(f"{label:38s} m={m:5.1f} eV chi={chi:4.2f} | K={K:5.1f} eV  A={A:5.2f} eV  Omega h2={om:.3f}  cosmic ratio={ratio:4.2f} | galaxy halo/baryons at 300 kpc={gal:4.2f} | core ceiling at 8 keV={rho0_msun_kpc3:.2e} Msun/kpc3 | relic speed today {v0:4.1f} km/s")
print("Reference: fully thermal species")
line(11.0, 1.0, "thermal 11 eV (2008 proposal)")
line(12.0, 1.0, "thermal 12 eV")
print("\nShared after decoupling among 3 ordinary + 1 new species: each at 3/4 of thermal")
line(11.0, 0.75, "11 eV at 3/4")
line(12.0, 0.75, "12 eV at 3/4")
line(13.0, 0.75, "13 eV at 3/4")
print("\nLower populations")
line(15.0, 0.40, "15 eV at 0.40"); line(17.0, 0.36, "17 eV at 0.36"); line(21.0, 0.15, "21 eV at 0.15")
print("\nRadiation count (effective number of light species), if the new species takes its particles from the ordinary")
print("neutrinos after they decouple and is slow by recombination (m >> 0.6 eV):")
for chi_share in (0.75,):
    print(f"  at nucleosynthesis: 3.046 (no extra load); at recombination: {3.046 * chi_share:.2f} (ordinary neutrinos depleted to {chi_share:.2f})")
print("If instead it is produced before decoupling at population chi: nucleosynthesis 3.046 + chi; recombination 3.046.")
print("\nPublished bounds to compare [from the literature notes]: Planck 2018 N_eff = 2.99 +- 0.17 (standard model);")
print("galaxy lensing 2-sigma upper limits on extra/baryons inside 300 kpc: 0.58 to 2.67; central values 0.09 to 0.92;")
print("richest six clusters hold A = 3.3 to 8.8 eV-equivalent inside r500 depending on corrections;")
print("cluster cores need K >= 8 (strong corrections) to 17 eV (none), for 95% of systems.")
