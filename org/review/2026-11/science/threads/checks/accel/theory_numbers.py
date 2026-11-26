"""Predictions of the three hypotheses for two observables (task 2).
1. BTFR zero point: velocity shift at fixed baryonic mass, and mass shift at fixed velocity.
   constant a0 (MOND):       dlogV = 0
   a0 = A E(z) (H tracking): dlogV = (1/4) log E,   dlogM|_V = -log E   (slope-4 deep-MOND BTFR)
   naive LCDM:               M_vir = V_vir^3 / (10 G H(z)) (Delta=200 rho_crit); with M_b = f M_vir and V_out = eta V_vir at
                             fixed f, eta:  dlogV|_Mb = (1/3) log E ; slope 3, not 4.
2. Circular speed of an exponential disc (M_b, R_e) at R_e and 3 R_e under nu(y) = 1/(1-exp(-sqrt y)).
"""
import numpy as np
import accel_lib as L

print('z     E(z)   dlogV const  H-track  naiveLCDM   dlogM|V H-track')
for z in (0.5, 0.9, 1.0, 1.44, 2.0, 2.3):
    e = float(L.E(z))
    print('%.2f  %.3f   %+.3f       %+.3f    %+.3f       %+.3f' % (z, e, 0, np.log10(e) / 4, np.log10(e) / 3, -np.log10(e)))

print('\nExponential disc, no bulge. v in km/s. a0 const = 1.2e-10, H-tracking = 1.2e-10 E(z)')
for logM, Re, z in ((10.8, 5.0, 2.2), (10.8, 5.0, 0.9), (9.5, 3.0, 0.9), (9.5, 3.0, 2.2), (11.2, 4.0, 2.2)):
    M = 10 ** logM
    for R in (Re, 3 * Re):
        v0, gN = L.v_mond(R, M, 0.0, Re, 1.2e-10)
        v1, _ = L.v_mond(R, M, 0.0, Re, 1.2e-10 * L.E(z))
        vN = np.sqrt(L.vbar2(R, M, 0.0, Re))
        print('logMb=%.1f Re=%.0f kpc z=%.1f R=%4.1f kpc: gN/a0=%.2f  vNewton=%5.1f  v(const)=%5.1f  v(H)=%5.1f  ratio=%.3f'
              % (logM, Re, z, R, gN / 1.2e-10, vN, v0, v1, v1 / v0))
    vf0 = (L.G_SI * M * L.MSUN * 1.2e-10) ** 0.25 / 1e3
    print('    asymptotic V_flat: const %.1f  H-tracking %.1f km/s' % (vf0, vf0 * float(L.E(z)) ** 0.25))
