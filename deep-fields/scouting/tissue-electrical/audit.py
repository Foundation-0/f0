"""Five checks on the tissue dielectric models most simulations use. Run ./fetch.sh first.

  A  lf_vs_gabriel.tsv          Gabriel (1996) model conductivity at 10 Hz-1 kHz vs the IT'IS low-frequency compilation
  B  sasaki_transcription.tsv   each IT'IS "alternative" entry vs the row of Sasaki et al. (2014) Table 2 it reproduces
  C  rf_three_way.tsv           Gabriel vs Sasaki vs NICT (2023) at 64 MHz-2.45 GHz
  D  water_content.tsv          permittivity at 900 MHz vs tissue water content (outliers)
  E  physics_checks.tsv         simple physical bounds: pure water, acellular fluids, fitted frequency bands

Writes results/*.tsv and results/summary.txt.
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import models as M
from data_sources import COLE, ITIS_ALT, ITIS_MAIN, ITIS_SQLITE, load_itis, load_itis_sqlite_gabriel, load_nict, load_sasaki

OUT = Path(__file__).resolve().parent / "results"
RF = [64e6, 128e6, 300e6, 900e6, 2.45e9]
LINES = []


def say(s=""):
    print(s)
    LINES.append(s)


def norm(s):
    return re.sub(r"[^a-z]", "", str(s).lower())


def params(row):
    return {k: float(row[k]) for k in COLE}


def has_model(row):
    return row["ef"] > 1.5 and row["name"] not in ("Water",)


# IT'IS main entries whose dielectric parameters are two-term fits that are not among the Gabriel (1996) sets
# (the IT'IS V5.0 reference list cites Peyman et al. for most of them). Kept in the tables, left out of the summaries.
OTHER_FITS = {"Adrenal Gland", "Intervertebral Disc", "Lymphnode", "Salivary Gland", "Thymus", "Urine"}


# ---------------------------------------------------------------- A
def check_lf(main):
    rows = []
    for _, r in main.iterrows():
        if not has_model(r) or np.isnan(r.get("lf_av", np.nan)) or r["lf_av"] == 0:
            continue
        _, s = M.gabriel([10, 100, 1e3], params(r))
        rows.append(dict(
            tissue=r["name"], dielectric_params_from=r["source"],
            own_params=norm(r["name"])[:8] == norm(r["source"])[:8],
            gabriel_1996_fit=r["name"] not in OTHER_FITS and r["source"] not in OTHER_FITS,
            sigma_model_10Hz=s[0], sigma_model_100Hz=s[1], sigma_model_1kHz=s[2],
            lf_av=r["lf_av"], lf_sd=r.get("lf_sd"), lf_n=r.get("lf_n"), lf_min=r.get("lf_min"), lf_max=r.get("lf_max"),
            ratio_lf_over_model_100Hz=r["lf_av"] / s[1],
            model_outside_lf_range=bool(s[1] < r.get("lf_min", -np.inf) or s[1] > r.get("lf_max", np.inf)),
        ))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "lf_vs_gabriel.tsv", sep="\t", index=False, float_format="%.4g")
    own = df[df.own_params & df.gabriel_1996_fit & (df.lf_n >= 5)].sort_values("ratio_lf_over_model_100Hz", ascending=False)
    say("A. Gabriel model at 100 Hz vs IT'IS low-frequency compilation (tissues with their own Gabriel fit, n >= 5)")
    for _, r in own.iterrows():
        say(f"   {r.tissue:24s} model {r.sigma_model_100Hz:7.4f} S/m   compiled {r.lf_av:6.3f} "
            f"(range {r.lf_min:.3g}-{r.lf_max:.3g}, n={int(r.lf_n)})   ratio {r.ratio_lf_over_model_100Hz:6.1f}"
            + ("   model outside range" if r.model_outside_lf_range else ""))
    k = own.ratio_lf_over_model_100Hz
    say(f"   {int((k > 3).sum())} of {len(own)} are more than 3x below the compiled mean; "
        f"{int(own.model_outside_lf_range.sum())} fall outside the compiled min-max range.")
    say()
    return df


# ---------------------------------------------------------------- B
ALIAS = {  # IT'IS "source" label -> Sasaki (2014) Table 2 tissue
    "bile": "Gall Bladder Bile", "bloodvesselwall": "Aorta", "bonecancellous": "Bone Cancellous",
    "bonecortical": "Bone Cortical", "bonemarrowyellow": "Bone Marrow", "braingreymatter": "Grey Matter",
    "brainwhitematter": "White Matter", "eyecornea": "Cornea", "eyelens": "Lens Nucleus",
    "eyelenscortex": "Lens Cortex", "eyesclera": "Eye Sclera", "eyevitroushumor": "Vitreous Humor",
    "fataverageinfiltrated": "Fat", "gallbladder": "Gall Bladder", "largeintestine": "Colon",
    "lunginflated": "Lung (Inflated)", "lungdeflated": "Lung (Deflated)", "muscle": "Muscle (Transverse)",
    "muscles": "Muscle (Transverse)", "skin": "Skin (Dry)", "skindry": "Skin (Dry)",
    "tendonligament": "Tendon", "thyroidgland": "Thyroid", "urinarybladderwall": "Bladder",
}


def check_sasaki(alt, sas):
    T = sas[["eps_s1", "sigma_dc_S_per_m", "f_r1_GHz", "delta1", "alpha1", "f_r2_MHz", "delta2", "alpha2"]].to_numpy(float)
    rows = []
    for _, r in alt.iterrows():
        if r["ef"] <= 1.5:
            continue
        fr1 = 1 / (2 * np.pi * r["tau2"] * 1e-9) / 1e9
        fr2 = 1 / (2 * np.pi * r["tau3"] * 1e-6) / 1e6
        key = np.array([r["ef"], r["sig"], fr1, r["del2"], r["alf2"], fr2, r["del3"], r["alf3"]])
        rel = np.max(np.abs(T - key) / np.maximum(np.abs(T), 1e-12), axis=1)
        j = int(np.argmin(rel))
        expected = ALIAS.get(norm(r["source"]))
        if expected is None:
            hit = [t for t in sas.tissue if norm(t) == norm(r["source"])]
            expected = hit[0] if hit else ""
        rows.append(dict(itis_tissue=r["name"], itis_declared_source=r["source"], expected_sasaki_row=expected,
                         matching_sasaki_row=sas.tissue[j], matching_row_no=int(sas.no[j]),
                         max_rel_param_diff=float(rel[j]), consistent=(expected == sas.tissue[j])))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "sasaki_transcription.tsv", sep="\t", index=False, float_format="%.3g")
    exact = int((df.max_rel_param_diff < 1e-3).sum())
    bad = df[~df.consistent]
    unused = sorted(set(sas.tissue) - set(df.matching_sasaki_row))
    say(f"B. IT'IS V5.0 alternative dielectric entries vs Sasaki et al. (2014) Table 2: {len(df)} entries, "
        f"{exact} reproduce a Table 2 row exactly.")
    for _, r in bad.iterrows():
        say(f"   {r.itis_tissue}: declared source '{r.itis_declared_source}' (Table 2 '{r.expected_sasaki_row}'), "
            f"but its parameters are row {r.matching_row_no} '{r.matching_sasaki_row}'.")
    say(f"   Table 2 rows used by no IT'IS entry: {', '.join(unused)}.")
    if ITIS_SQLITE.exists():
        aorta = sas.set_index("tissue").loc["Aorta"]
        for name, ver, v in sorted(load_itis_sqlite_gabriel(names=("Urinary Bladder Wall",)), key=lambda r: r[1]):
            if "sasaki" in ver:
                same = abs(v[0] - aorta.eps_s1) < 1e-9 and abs(v[4] - aorta.delta1) < 1e-9 and abs(v[13] - aorta.sigma_dc_S_per_m) < 1e-9
                say(f"   SQLite material database, version '{ver}': {name} = "
                    f"{'Aorta row' if same else 'not the Aorta row'} (ef {v[0]}, del2 {v[4]}, sig {v[13]}).")
    say()
    return df


# ---------------------------------------------------------------- C
PAIRS = [  # NICT tissue, IT'IS tissue, Sasaki Table 2 row (None if IT'IS uses a surrogate or a non-Gabriel fit)
    ("Aorta", "Blood Vessel Wall", "Aorta"), ("Bladder", "Urinary Bladder Wall", "Bladder"),
    ("Blood", "Blood", "Blood"), ("Brain-Cerebellum", "Cerebellum", "Cerebellum"),
    ("Brain-Cerebrospinal fluid", "Cerebrospinal Fluid", "Cerebrospinal Fluid"),
    ("Brain-Grey matter", "Brain (Grey Matter)", "Grey Matter"),
    ("Brain-White matter", "Brain (White Matter)", "White Matter"), ("Eye-Cornea", "Eye (Cornea)", "Cornea"),
    ("Eye-Sclera", "Eye (Sclera)", "Eye Sclera"), ("Eye-Vitreous", "Eye (Vitreous Humor)", "Vitreous Humor"),
    ("Fat-Breast", "Breast Fat", "Breast Fat"), ("Fat-Subcutaneous", "Fat (Average Infiltrated)", "Fat"),
    ("Gallbladder", "Gallbladder", "Gall Bladder"), ("Gallbladder bile", "Bile", "Gall Bladder Bile"),
    ("Genital organ-Ovary", "Ovary", "Ovary"), ("Genital organ-Testis", "Testis", "Testis"),
    ("Genital organ-Uterus", "Uterus", "Uterus"), ("Intestine-Large intestine", "Large Intestine", "Colon"),
    ("Intestine-Small intestine", "Small Intestine", "Small Intestine"), ("Kidney", "Kidney", "Kidney"),
    ("Liver", "Liver", "Liver"), ("Lung", "Lung (Deflated)", "Lung (Deflated)"),
    ("Muscle-Heart", "Heart Muscle", "Heart Muscle"), ("Muscle-Thigh", "Muscle", "Muscle (Transverse)"),
    ("Nerve (Spinal cord)", "Spinal Cord", "Nerve"), ("Skin-Epidermis + dermis", "Skin", "Skin (Dry)"),
    ("Spleen", "Spleen", "Spleen"), ("Stomach", "Stomach", "Stomach"), ("Tendon", "Tendon\\Ligament", "Tendon"),
    ("Thyroid", "Thyroid Gland", "Thyroid"),
    # IT'IS assigns these a surrogate tissue's parameters (or a non-Gabriel fit)
    ("Pancreas", "Pancreas", None), ("Mammary gland", "Breast Gland", None),
    ("Brain-Pituitary gland", "Hypophysis", None), ("Brain-Pineal gland", "Pineal Body", None),
    ("Brain-Thalamus", "Thalamus", None), ("Brain-Hypothalamus", "Hypothalamus", None),
    ("Medulla oblongata", "Medulla Oblongata", None), ("Genital organ-Epididymis", "Epididymis", None),
    ("Genital organ-Vagina", "Vagina", None), ("Esophagus", "Esophagus", None), ("Diaphragm", "Diaphragm", None),
    ("Submandibular gland", "Salivary Gland", None), ("Thymus", "Thymus", None),
    ("Adrenal gland", "Adrenal Gland", None), ("Intestine-Mesenteric lymph", "Lymphnode", None),
]


def check_rf(main, sas, nict):
    m = main.set_index("name")
    s = sas.set_index("tissue")
    n = nict.set_index("Tissue")
    F = np.array(RF)
    rows = []
    for nt, it, st in PAIRS:
        en, sn = M.nict(F, n.loc[nt])
        eg, sg = M.gabriel(F, params(m.loc[it]))
        es, ss = M.sasaki(F, s.loc[st]) if st else (np.full(len(F), np.nan),) * 2
        for i, f in enumerate(F):
            rows.append(dict(nict_tissue=nt, itis_tissue=it, itis_params_from=m.loc[it, "source"], sasaki_row=st or "",
                             f_MHz=f / 1e6, eps_gabriel=eg[i], eps_sasaki=es[i], eps_nict=en[i],
                             sigma_gabriel=sg[i], sigma_sasaki=ss[i], sigma_nict=sn[i],
                             eps_ratio_nict_over_itis=en[i] / eg[i], sigma_ratio_nict_over_itis=sn[i] / sg[i]))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "rf_three_way.tsv", sep="\t", index=False, float_format="%.4g")
    at = df[df.f_MHz == 128].copy()
    at["worst"] = np.maximum(np.abs(np.log(at.eps_ratio_nict_over_itis)), np.abs(np.log(at.sigma_ratio_nict_over_itis)))
    say("C. At 128 MHz (3 T MRI): NICT (2023) fit vs the IT'IS main entry, largest disagreements")
    for _, r in at.sort_values("worst", ascending=False).head(12).iterrows():
        tag = "" if norm(r.itis_tissue)[:8] == norm(r.itis_params_from)[:8] else f" [IT'IS uses {r.itis_params_from}]"
        say(f"   {r.nict_tissue:26s} eps {r.eps_gabriel:5.1f} -> {r.eps_nict:5.1f} (x{r.eps_ratio_nict_over_itis:4.2f})   "
            f"sigma {r.sigma_gabriel:5.3f} -> {r.sigma_nict:5.3f} (x{r.sigma_ratio_nict_over_itis:4.2f}){tag}")
    within = (at.worst < np.log(1.25)).sum()
    say(f"   {within} of {len(at)} pairs agree within 25% in both permittivity and conductivity at 128 MHz.")
    say()
    return df


# ---------------------------------------------------------------- D
def check_water(main, nict):
    d = main[[has_model(r) and not np.isnan(r.get("water_av", np.nan)) for _, r in main.iterrows()]].copy()
    d = d[[norm(a)[:8] == norm(b)[:8] and a not in OTHER_FITS for a, b in zip(d.name, d.source)]]
    d["eps900"] = [float(M.gabriel([9e8], params(r))[0][0]) for _, r in d.iterrows()]
    x, y = d.water_av.to_numpy(float), d.eps900.to_numpy(float)
    b = np.polyfit(x, y, 1)
    d["eps900_trend"] = np.polyval(b, x)
    d["residual"] = y - d.eps900_trend
    rms = float(np.sqrt(np.mean(d.residual**2)))
    d["residual_over_rms"] = d.residual / rms
    d[["name", "water_av", "water_n", "eps900", "eps900_trend", "residual", "residual_over_rms"]] \
        .sort_values("residual").to_csv(OUT / "water_content.tsv", sep="\t", index=False, float_format="%.4g")
    say(f"D. Gabriel permittivity at 900 MHz vs IT'IS water content ({len(d)} tissues with their own fit): "
        f"eps = {b[0]:.3f} x water% {b[1]:+.1f}, rms scatter {rms:.1f}")
    for _, r in d.sort_values("residual").head(3).iterrows():
        say(f"   {r['name']:22s} water {r.water_av:5.1f}% (n={int(r.water_n)})  eps {r.eps900:5.1f}  "
            f"trend {r.eps900_trend:5.1f}  residual {r.residual:+6.1f} ({r.residual_over_rms:+.1f} rms)")
    bl = nict.set_index("Tissue").loc["Bladder"]
    e_n = float(M.nict([9e8], bl)[0][0])
    wb = float(d.set_index("name").loc["Urinary Bladder Wall", "water_av"])
    say(f"   NICT bladder at 900 MHz: eps {e_n:.1f} (trend at {wb:.0f}% water: {np.polyval(b, wb):.1f})")
    say()
    return d


# ---------------------------------------------------------------- E
FIT_LOWER_LIMIT_MHZ = {  # Sasaki et al. (2014), Table 1: measured data start above 1 MHz
    "Cerebrospinal Fluid": 130, "Dura": 130, "Gall Bladder": 12, "Gall Bladder Bile": 20,
    "Lung (Deflated)": 3.6, "Stomach": 3, "Testis": 3.6, "Vitreous Humor": 130,
}


def check_physics(main, sas, nict):
    rows = []
    m = main.set_index("name")
    w = m.loc["Water"]
    static = w["ef"] + w["del1"] + w["del2"] + w["del3"] + w["del4"]
    temps = np.arange(0, 60.01, 0.01)
    t_static = float(temps[np.argmin(np.abs(M.water_static_permittivity(temps) - static))])
    t_tau = float(temps[np.argmin(np.abs(M.water_relaxation_time_ps(temps) - w["tau1"]))])
    rows.append(dict(check="IT'IS 'Water': static permittivity (sum of ef and deltas)", value=static,
                     reference=f"{M.water_static_permittivity(25):.2f} at 25 C, {M.water_static_permittivity(37):.2f} at 37 C",
                     note=f"equals pure water at {t_static:.1f} C (Malmberg & Maryott 1956), but its relaxation time "
                          f"{w['tau1']:.2f} ps is that of water at {t_tau:.1f} C (Liebe et al. 1991)"))
    e37 = M.water_static_permittivity(37)
    F = np.logspace(7, 9, 201)
    fluids = [("Gabriel", "Cerebrospinal Fluid"), ("Gabriel", "Eye (Vitreous Humor)"), ("Gabriel", "Bile"),
              ("IT'IS (Peyman)", "Urine")]
    for src, t in fluids:
        e, _ = M.gabriel(F, params(m.loc[t]))
        i = int(np.argmax(e))
        above = F[e > e37]
        rows.append(dict(check=f"{src} {t}: max permittivity 10 MHz-1 GHz", value=e[i],
                         reference=f"pure water at 37 C: {e37:.2f}",
                         note=(f"above pure water from {above.min()/1e6:.0f} to {above.max()/1e6:.0f} MHz"
                               if len(above) else "never above pure water")))
    for nt in ("Brain-Cerebrospinal fluid", "Eye-Vitreous", "Eye-Anterior humor", "Gallbladder bile"):
        e, _ = M.nict(F, nict.set_index("Tissue").loc[nt])
        rows.append(dict(check=f"NICT {nt}: max permittivity 10 MHz-1 GHz", value=float(e.max()),
                         reference=f"pure water at 37 C: {e37:.2f}",
                         note="above pure water" if e.max() > e37 else "below pure water"))
    s = sas.set_index("tissue")
    for t, lo in FIT_LOWER_LIMIT_MHZ.items():
        e1, s1 = M.sasaki([1e6], s.loc[t])
        elo, slo = M.sasaki([lo * 1e6], s.loc[t])
        rows.append(dict(check=f"Sasaki {t}: permittivity at 1 MHz (fitted data start at {lo} MHz)",
                         value=float(e1[0]), reference=f"{float(elo[0]):.1f} at {lo} MHz",
                         note="IT'IS documents the alternative set as valid above 1 MHz"))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "physics_checks.tsv", sep="\t", index=False, float_format="%.4g")
    say("E. Physical bounds")
    for _, r in df.iterrows():
        say(f"   {r.check}: {r.value:.1f}  ({r.reference}; {r.note})")
    say()
    return df


def main():
    OUT.mkdir(exist_ok=True)
    try:
        itis_main, itis_alt, nict = load_itis(ITIS_MAIN), load_itis(ITIS_ALT), load_nict()
    except FileNotFoundError as e:
        sys.exit(f"missing {e.filename}: run ./fetch.sh first")
    sas = load_sasaki()
    check_lf(itis_main)
    check_sasaki(itis_alt, sas)
    check_rf(itis_main, sas, nict)
    check_water(itis_main, nict)
    check_physics(itis_main, sas, nict)
    (OUT / "summary.txt").write_text("\n".join(LINES) + "\n")


if __name__ == "__main__":
    main()
