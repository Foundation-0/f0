"""Assemble T4 table: per system and radius, M_tot, M_gas (hydrostatic X-ray), radius, redshift.
Sources (TeX of the arXiv versions, cached under sources/):
 V06 = Vikhlinin+2006 astro-ph/0507092 mprof.tex Table 'tab:masses' (h=0.72)
 S09 = Sun+2009 0805.2320 ms.tex Table 3 (h=0.73; M2500 from r2500 and rho_c(z)); only groups with measured M500
 L15 = Lovisari+2015 1409.3845 Table 'tab:propgroups' (h=0.70)
 G13 = Gonzalez+2013 1309.3565 Tables 'tab:data','tab:baryonfracs' (r500 only; gas and stars)"""
import re, math, pathlib, json
src = pathlib.Path(__file__).parent / "sources"
G = 6.67430e-11; MSUN = 1.98847e30; KPC = 3.085677581491367e19
def rhoc(z, h, Om=0.3):
    H0 = 100 * h * 1e3 / (1e3 * KPC)
    return 3 * (H0 ** 2) * (Om * (1 + z) ** 3 + 1 - Om) / (8 * math.pi * G)
def r_from_M(M, D, z, h, Om=0.3):   # kpc
    return (3 * M * MSUN / (4 * math.pi * D * rhoc(z, h, Om))) ** (1 / 3) / KPC
def M_from_r(r, D, z, h, Om=0.3):
    return 4 * math.pi / 3 * D * rhoc(z, h, Om) * (r * KPC) ** 3 / MSUN
def num(s):
    """first number and a symmetric error (mean of +/-) from a TeX cell"""
    s = s.replace("$", "").replace("*", "").replace("(", "").replace(")", "")
    m = re.match(r"\s*([0-9.]+)", s)
    if not m: return None, None
    v = float(m.group(1))
    e = re.findall(r"\\pm\s*([0-9.]+)", s)
    if e: return v, float(e[0])
    up = re.findall(r"\^\{\+?([0-9.]+)\}", s); dn = re.findall(r"_\{-?([0-9.]+)\}", s)
    if up and dn: return v, 0.5 * (float(up[0]) + float(dn[0]))
    return v, None
rows = []
# ---- V06
t = (src / "arxiv-astro-ph_0507092" / "mprof.tex").read_text()
zV = {}
blk = t[t.index("tab:sample"):]; blk = blk[:blk.index("enddata")]
for ln in blk.split("\\\\"):
    m = re.match(r"\s*(?:\\startdata)?\s*([A-Z][^\\&]*?)\\?(?:,|~)?\s*([0-9+]*)\s*\\dotfill\s*&\s*([0-9.]+)", ln.strip())
    m = re.search(r"([A-Za-z][^\n]*?)\\dotfill\s*&\s*([0-9.]+)", ln)
    if m: zV[re.sub(r"[\\,~ \n]", "", m.group(1))] = float(m.group(2))
blk = t[t.index("tab:masses"):]; blk = blk[blk.index("startdata") + 9: blk.index("enddata")]
for ent in blk.split("\\\\"):
    if "dotfill" not in ent: continue
    name = re.sub(r"[\\,~ \n]", "", ent.split("\\dotfill")[0])
    cells = [c.strip() for c in ent.split("\\dotfill")[1].split("&")][1:]
    r500, _ = num(cells[0]); M2500, eM2 = num(cells[4]); M500, eM5 = num(cells[5])
    fg2, efg2 = num(cells[6]); fg5, efg5 = num(cells[7])
    if M500 is None: continue
    z = zV[name]; h = 0.72
    rows.append(dict(sample="V06", name=name, z=z, h=h,
        r2500=r_from_M(M2500 * 1e14, 2500, z, h), M2500=M2500 * 1e14, eM2500=eM2 * 1e14, fg2500=fg2, efg2500=efg2,
        r500=r500, M500=M500 * 1e14, eM500=eM5 * 1e14, fg500=fg5, efg500=efg5))
# ---- S09
t = (src / "arxiv-0805.2320" / "ms.tex").read_text()
zS = {}
b1 = t[t.index("The group sample and the"):]; b1 = b1[:b1.index("end{table}")]
for ln in b1.split("\\\\"):
    c = [x.strip() for x in ln.split("&")]
    if len(c) > 3 and c[0] and re.match(r"[0-9.]+$", c[1]):
        zS[re.sub(r"[~ ]|\(.*\)", "", c[0].split("\n")[-1])] = float(c[1])
b3 = t[t.index("Derived properties of groups (I"):]; b3 = b3[b3.index("\\hline", b3.index("Group &")) + 6: b3.index("\\hline \\hline", 400)]
for ln in b3.split("\\\\"):
    c = [x.strip() for x in ln.split("&")]
    if len(c) < 9 or not c[5]: continue
    name = re.sub(r"[~ ]", "", c[0])
    z = zS.get(name)
    if z is None:
        z = {"RXJ1159": 0.081, "A1275": zS.get("A1275")}.get(name)
    if z is None: print("S09: no z for", name); continue
    h = 0.73
    r500, _ = num(c[3]); r2500, er25 = num(c[4]); M500, eM5 = num(c[5]); fg5, efg5 = num(c[6]); fg2, efg2 = num(c[7])
    M2500 = M_from_r(r2500, 2500, z, h, 0.24)
    rows.append(dict(sample="S09", name=name, z=z, h=h, r2500=r2500, M2500=M2500, eM2500=3 * er25 / r2500 * M2500,
        fg2500=fg2, efg2500=efg2, r500=r500, M500=M500 * 1e13, eM500=eM5 * 1e13, fg500=fg5, efg500=efg5,
        tier2=("*" in c[5])))
# ---- L15
t = (src / "arxiv-1409.3845" / "Lovisari_groups.tex").read_text()
zL = {}
b1 = t[t.index("Galaxy groups in the sample sorted"):]; b1 = b1[b1.index("\\hline", b1.index("Name")) + 6:b1.index("tab:sample")]
for ln in b1.split("\\\\"):
    c = [x.strip() for x in ln.split("&")]
    if len(c) >= 2: zL[re.sub(r"\\rm|[{}\s]|\^|\*|\\hline", "", c[0])] = float(c[1])
b = t[t.index("tab:propgroups") - 4000: t.index("tab:propgroups")]
b = b[b.index("\\hline", b.index("Group \\ name")) + 6:]
for ln in b.split("\\\\"):
    c = [x.strip() for x in ln.split("&")]
    if len(c) < 9: continue
    name = re.sub(r"\\rm|[{} \t]|\^\{?\*\}?|\^", "", c[0]).replace("*", "")
    z = zL.get(name)
    if z is None: print("L15: no z for", name, list(zL)[:3]); continue
    h = 0.70
    r500, _ = num(c[3]); M500, eM5 = num(c[4]); Mg5, eMg5 = num(c[5]); r2500, _ = num(c[6]); M2500, eM2 = num(c[7]); Mg2, eMg2 = num(c[8])
    rows.append(dict(sample="L15", name=name, z=z, h=h, r2500=r2500, M2500=M2500 * 1e13, eM2500=eM2 * 1e13,
        fg2500=Mg2 * 1e12 / (M2500 * 1e13), efg2500=eMg2 * 1e12 / (M2500 * 1e13),
        r500=r500, M500=M500 * 1e13, eM500=eM5 * 1e13, fg500=Mg5 * 1e12 / (M500 * 1e13), efg500=eMg5 * 1e12 / (M500 * 1e13)))
# ---- G13 (r500 only)
t = (src / "arxiv-1309.3565" / "ms.tex").read_text()
b = t[t.index("Observed Cluster Properties"):]; b = b[b.index("startdata"):b.index("enddata")]
fs = {}
bb = t[t.index("Derived Mass Fractions"):]; bb = bb[bb.index("startdata"):bb.index("enddata")]
for ln in bb.split("\\\\"):
    c = [x.strip() for x in ln.split("&")]
    if len(c) >= 3: fs[re.sub(r"%.*\n|\s|startdata|\\\\hline", "", c[0])] = num(c[2])
for ln in b.split("\\\\"):
    c = [x.strip() for x in ln.split("&")]
    if len(c) < 9: continue
    name = re.sub(r"%.*\n|\s|startdata|\\hline", "", c[0])
    z = float(c[1]); r500, _ = num(c[5]); M500, eM5 = num(c[6]); Mg, eMg = num(c[7])
    fst = fs.get(name, (None, None))
    rows.append(dict(sample="G13", name=name, z=z, h=0.702, r500=r500 * 1e3, M500=M500 * 1e14, eM500=eM5 * 1e14,
        fg500=Mg * 1e13 / (M500 * 1e14), efg500=eMg * 1e13 / (M500 * 1e14), fstar500=fst[0], efstar500=fst[1]))
if __name__ == "__main__": json.dump(rows, open(pathlib.Path(__file__).parent / "t4_systems.json", "w"), indent=1)
for s in (["V06", "S09", "L15", "G13"] if __name__ == "__main__" else []):
    rr = [r for r in rows if r["sample"] == s]
    print(s, len(rr), "systems:", ", ".join(r["name"] for r in rr))
