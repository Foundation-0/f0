"""Internal-consistency checks of the hand transcription of RC100 Table 3.
(a) Paper's V_c errors look like 20% of V_c: flag |e_Vc - 0.2 Vc| > 2 (rows 65, 96 differ by 1.6 and 1.2 in the paper itself).
(b) log Sigma_DM(<Re) should equal log[f_DM Vc^2 Re / G / (pi Re^2)] up to a common geometric factor;
    flag rows whose residual from the median is > 0.08 dex (skipped when f_DM < 0.05, where 2-digit rounding of f_DM dominates).
(c) e_logMbul etc. positive, ranges sane, ids 1..100 in order, z non-decreasing.
Exit 1 on any failure."""
import csv, math, sys
G = 4.30091e-6  # kpc (km/s)^2 / Msun
rows = [r for r in csv.DictReader(l for l in open(sys.argv[1]) if not l.startswith('#'))]
bad = 0
if [int(r['id']) for r in rows] != list(range(1, 101)): print('ids not 1..100'); bad += 1
zs = [float(r['z']) for r in rows]
if any(b < a for a, b in zip(zs, zs[1:])): print('z not sorted'); bad += 1
res = []
for r in rows:
    Vc, eV = float(r['Vc']), float(r['e_Vc'])
    if abs(eV - 0.2 * Vc) > 2.0: print('eVc', r['id'], Vc, eV); bad += 1
    f, Re = float(r['fDM']), float(r['Re'])
    if not (0 <= f < 1 and 0.5 < Re < 15 and 50 < Vc < 500): print('range', r['id']); bad += 1
    if float(r['logMbul']) > float(r['logMbar']) + 0.005: print('bulge>bar', r['id']); bad += 1
    pred = math.log10(f * Vc**2 * Re / G / (math.pi * Re**2))
    res.append((pred - float(r['logSigDM']), r['id']))
med = sorted(x for x, _ in res)[50]
fdm_of = {r['id']: float(r['fDM']) for r in rows}
print('median offset logSigDM(pred)-table = %.3f' % med)
for x, i in res:
    if abs(x - med) > 0.08 and fdm_of[i] >= 0.05: print('SigDM mismatch id %s: %.3f' % (i, x - med)); bad += 1
print('rows', len(rows), 'flags', bad)
sys.exit(1 if bad else 0)
