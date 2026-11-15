"""Compare a certificate (cert_arb.py output) with Ferrario's 2002 tables (arXiv math/0204198, parsed from the
cached text) by the invariant P = U sqrt(I) (Moeckel's potential, masses 1, I = 1 scaling).
Ferrario's isotropy i relates to our stabiliser order s by i = s/2 (i = 1/2 for no symmetry).
Usage: python compare_lit.py cert.json sources/ferrario.txt"""
import sys, json, re
from fractions import Fraction as Fr

cert = json.load(open(sys.argv[1])); n = cert['n']
L = open(sys.argv[2]).read().split('\n')[550:]
ents = []; cur = None
for l in L:
    m = re.search(r'U I = ([\d.]+)', l)
    if m:
        cur = {'P': float(m.group(1)), 'z': 0}; ents.append(cur); continue
    if cur is None:
        continue
    for key in ['Crit ind', 'Isotropy']:
        m = re.search(key + r' = ([\d/]+)', l)
        if m:
            cur[key] = m.group(1)
    cur['z'] += len(re.findall(r'z\d+ = \(', l))
fer = [e for e in ents if e['z'] == n]
ours = []
for c in cert['classes']:
    mid = float(c['P_enclosure'].strip('[').split('+/-')[0])
    ours.append((mid, c['morse_index'], c['sym_order']))
used = set()
print(f"n = {n}: ours {len(ours)} classes, Ferrario {len(fer)} entries")
print(" P (ours, certified)   h  s | Ferrario P     h  iso | note")
for P, h, s in sorted(ours):
    j = min(range(len(fer)), key=lambda t: abs(fer[t]['P'] - P)) if fer else None
    note = ''
    if j is not None and abs(fer[j]['P'] - P) < 2e-6 and j not in used:
        used.add(j); f = fer[j]
        iso = Fr(f['Isotropy']); ok_h = int(f['Crit ind']) == h; ok_s = iso == Fr(s, 2)
        note = ('' if ok_h else 'Morse index differs; ') + ('' if ok_s else f'isotropy differs (ours s/2 = {Fr(s,2)}); ')
        print(f" {P:18.10f}  {h}  {s:2d} | {f['P']:14.8f}  {f['Crit ind']}  {f['Isotropy']:>3} | {note or 'agrees'}")
    else:
        print(f" {P:18.10f}  {h}  {s:2d} | {'(none)':>14}          | not in Ferrario's table")
for j, f in enumerate(fer):
    if j not in used:
        print(f" Ferrario entry P = {f['P']:.8f} (h {f['Crit ind']}, iso {f['Isotropy']}) has no certified match")
