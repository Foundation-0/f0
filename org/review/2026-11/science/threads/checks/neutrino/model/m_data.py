"""Systems for the neutrino-model tests. Masses and gas fractions from ../../gravity2/t4_systems.json (my parse of
Vikhlinin+06, Sun+09, Lovisari+15, Gonzalez+13 TeX tables); temperatures and published c500 parsed here from the same TeX."""
import re, json, math, pathlib
import numpy as np
H = pathlib.Path(__file__).resolve().parent; G2 = H.parents[1] / "gravity2"
SRC = G2 / "sources"
def num(s):
    s = s.replace("$", "").replace("*", "").replace("(", "").replace(")", "")
    m = re.match(r"\s*([0-9.]+)", s); return float(m.group(1)) if m else None
def temps():
    T, C = {}, {}
    t = (SRC / "arxiv-astro-ph_0507092/mprof.tex").read_text()
    blk = t[t.index("tab:masses"):]; blk = blk[blk.index("startdata") + 9: blk.index("enddata")]
    for ent in blk.split("\\\\"):
        if "dotfill" not in ent: continue
        name = re.sub(r"[\\,~ \n]", "", ent.split("\\dotfill")[0]); c = [x.strip() for x in ent.split("\\dotfill")[1].split("&")][1:]
        T[("V06", name)] = (num(c[2]), "T_mg (Vikhlinin+06)"); C[("V06", name)] = num(c[3])
    t = (SRC / "arxiv-0805.2320/ms.tex").read_text()
    b3 = t[t.index("Derived properties of groups (I"):]; b3 = b3[b3.index("\\hline", b3.index("Group &")) + 6: b3.index("\\hline \\hline", 400)]
    for ln in b3.split("\\\\"):
        c = [x.strip() for x in ln.split("&")]
        if len(c) < 9: continue
        name = re.sub(r"[~ ]", "", c[0]); T[("S09", name)] = (num(c[1]), "T500 (Sun+09)"); cc = num(c[9]) if len(c) > 9 else None
        C[("S09", name)] = cc
    t = (SRC / "arxiv-1409.3845/Lovisari_groups.tex").read_text()
    b = t[t.index("tab:propgroups") - 4000: t.index("tab:propgroups")]; b = b[b.index("\\hline", b.index("Group \\ name")) + 6:]
    for ln in b.split("\\\\"):
        c = [x.strip() for x in ln.split("&")]
        if len(c) < 9: continue
        name = re.sub(r"\\rm|[{} \t]|\^\{?\*\}?|\^", "", c[0]).replace("*", ""); T[("L15", name)] = (num(c[1]), "kT (Lovisari+15)")
    t = (SRC / "arxiv-1309.3565/ms.tex").read_text()
    b = t[t.index("Observed Cluster Properties"):]; b = b[b.index("startdata"):b.index("enddata")]
    for ln in b.split("\\\\"):
        c = [x.strip() for x in ln.split("&")]
        if len(c) < 9: continue
        name = re.sub(r"%.*\n|\s|startdata|\\hline", "", c[0]); T[("G13", name)] = (num(c[2]), "T_X (Gonzalez+13)")
    return T, C
def systems():
    rows = json.load(open(G2 / "t4_systems.json"))
    drop = {("S09", "MKW4"), ("S09", "A1991"), ("G13", "Abell0478"), ("G13", "Abell2029"), ("G13", "Abell2390")}
    rows = [r for r in rows if (r["sample"], r["name"]) not in drop]
    T, C = temps()
    g = [r for r in rows if r["sample"] == "G13" and r["fstar500"]]
    sl, ic = np.polyfit(np.log10([r["M500"] / 1e14 for r in g]), np.log10([r["fstar500"] for r in g]), 1)
    for r in rows:
        r["kT"], r["T_def"] = T[(r["sample"], r["name"])]
        r["c500_pub"] = C.get((r["sample"], r["name"]))
        r["fstar500_used"] = r.get("fstar500") or 10 ** ic * (r["M500"] / 1e14) ** sl
        r["fstar_measured"] = bool(r.get("fstar500"))
    return rows
if __name__ == "__main__":
    rs = systems()
    print(len(rs), "systems;", sum("M2500" in r for r in rs), "with both radii")
    for r in rs[:3] + rs[-2:]: print(r["sample"], r["name"], r["kT"], r["T_def"], r["c500_pub"])
