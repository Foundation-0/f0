# [I] my own arithmetic checks of formulas quoted in notes; constants CODATA
import math
h=4.135667696e-15 # eV s
c=2.99792458e5 # km/s
pc=3.0856775814913673e13 # km
Msun_eV=1.98847e30*(2.99792458e8)**2/1.602176634e-19 # eV
eVcm=1.602176634e-19 # J/eV
# relic neutrino mean speed
kT0=8.617333262e-5*1.9454 # eV, T_nu0=1.945 K
mean_p=3.1514*kT0
print("mean speed km/s per eV mass:",mean_p/1.0*c)
# TG max density (Sanders 2007 eq 10 type): rho = (2pi)^1.5 m^4 sigma^3 h^-3 per species incl antiparticle, natural units c=1
def rho_TG(m_eV,sigma_kms,g=2):
    s=sigma_kms/c # sigma/c
    # phase space density f_max = g/2 /h^3 (in units: h*c) ; rho = m * f_max*(2pi sigma^2 m^2)^1.5 -> m^4 (2pi)^1.5 s^3 (g/2) /(h c)^3 [eV^4/(eV m)^3]
    hc=h*c*1e3 # eV m: h[eV s]*c[m/s]
    rho_eV_m3=(g/2)*(2*math.pi)**1.5*m_eV**4*s**3/hc**3  # eV / m^3
    kg_m3=rho_eV_m3*1.602176634e-19/(2.99792458e8)**2
    return kg_m3
# Sanders/PS05: rho<=4.8e-24 (m/2)^4 T^1.5 kg/m^3 for 3 species; T=1 keV -> sigma^2 = kT/mu m_p
mp=938.272e6 # eV
sig=lambda T_keV,mu=0.6: c*math.sqrt(T_keV*1e3/(mu*mp))
for mu in (0.6,):
    s=sig(1.0,mu); r=3*rho_TG(2.0,s)
    print("3 species, m=2eV, T=1keV, sigma=%.0f km/s: rho=%.2e kg/m3 (PS05 quote 4.8e-24)"%(s,r))
    Msun_pc3=1.98847e30/(3.0856775814913673e16)**3
    print("   in Msun/pc3 per species:",r/3/Msun_pc3," (Angus08 quote 7e-5 per species)")
# Angus 2010 eq 14: 11 eV sterile
Msun_kg=1.98847e30; pc_m=3.0856775814913673e16
for sigma_over_c in (1e-3,):
    r=rho_TG(11,sigma_over_c*c,g=2)/Msun_kg*pc_m**3
    print("11 eV, sigma/c=1e-3: rho=%.3g Msun/pc3 ; Angus10 eq14 coefficient 3.15e6*(1e-3)^3 = %.3g"%(r,3.15e6*1e-9))
# Kelleher eq 19: 1e-28 g/cm3 (T/keV)^1.5 sum (m/eV)^4 -> Msun/pc3
print("1e-28 g/cm3 in Msun/pc3:",1e-28*1e3/Msun_kg*pc_m**3,"(quoted 1.5e-6)")
# Omega h2 = 93.14 eV
rho_crit_h2=1.8784e-26 # kg/m3 per h^2
n_nu=112 # per cm^3 per species (nu+antinu)
print("Omega h2 per eV:",n_nu*1e6*1.602176634e-19/(2.99792458e8)**2/rho_crit_h2," (1/93.14=%.5f)"%(1/93.14))
# 11 eV sterile: thermal with T_s such that Omega h2=0.117: n_s relative to a standard neutrino
print("Omega h2 for 11 eV if one species with active-neutrino abundance: %.4f"%(11/93.14))
