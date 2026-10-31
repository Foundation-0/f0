"""Loaders for the IT'IS V5.0 ASCII tables, the NICT model CSV and the transcribed Sasaki (2014) Table 2."""
import io
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
ITIS_MAIN = DATA / "Thermal_dielectric_acoustic_MR properties_database_V5.0(ASCII).txt"
ITIS_ALT = DATA / "Alternative_dielectric_properties_database_V5.0(ASCII).txt"
ITIS_SQLITE = DATA / "IT'IS_Material_database_V5.0.db"
NICT = DATA / "nict-model.csv"
SASAKI = HERE / "sasaki2014_table2.tsv"

COLE = ["ef", "del1", "tau1", "alf1", "del2", "tau2", "alf2", "sig",
        "del3", "tau3", "alf3", "del4", "tau4", "alf4"]


def _read_text(path):
    raw = Path(path).read_bytes()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):  # the alternative table is UTF-16
        return raw.decode("utf-16")
    return raw.decode("latin-1")


def load_itis(path):
    """One row per tissue; columns named 'Group|Field' from the two header rows of the IT'IS export."""
    raw = pd.read_csv(io.StringIO(_read_text(path)), sep="\t", header=None, dtype=str)
    group, cols = "", []
    for top, sub in zip(raw.iloc[1].fillna(""), raw.iloc[2].fillna("")):
        if top.strip():
            group = top.strip()
        cols.append(f"{group}|{sub.strip()}")
    df = raw.iloc[3:].copy()
    df.columns = cols
    df = df[df["Tissue|Name"].notna()].reset_index(drop=True)
    out = pd.DataFrame({"name": df["Tissue|Name"].str.strip(), "source": df["Semcad|source"].str.strip()})
    for c in [c for c in df.columns if c.startswith("Dielectric Properties|")]:
        out[c.split("|")[1].split(" ")[0]] = pd.to_numeric(df[c], errors="coerce")
    for prefix, short in (("LF Conductivity [S/m]", "lf"), ("Water Content [%]", "water")):
        if f"{prefix}|Average" in df.columns:
            for field, tag in (("Average", "av"), ("Standard Deviation", "sd"), ("Sample Size", "n"),
                               ("min", "min"), ("max", "max"), ("Minimum", "min"), ("Maximum", "max")):
                key = f"{prefix}|{field}"
                if key in df.columns:
                    out[f"{short}_{tag}"] = pd.to_numeric(df[key], errors="coerce")
    return out


def load_nict(path=NICT):
    return pd.read_csv(path)


def load_sasaki(path=SASAKI):
    return pd.read_csv(path, sep="\t", comment="#")


def load_itis_sqlite_gabriel(path=ITIS_SQLITE, names=()):
    """Gabriel-parameter vectors from the SQLite material database in the IT'IS download (the file Sim4Life imports).

    Returns rows (tissue, version label, 14 parameters). The vector order is ef, del1, tau1, alf1, del2, tau2, alf2,
    del3, tau3, alf3, del4, tau4, alf4, sig.
    """
    import sqlite3
    import struct
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    prop = con.execute("select prop_id from properties where variable='gabriel_parameters'").fetchone()[0]
    q = ("select m.name, ver.string, v.vals from materials m join vectors v on v.mat_id = m.mat_id "
         "join versions ver on ver.ver_id = m.ver_id where v.prop_id = ? and m.name in (%s)" % ",".join("?" * len(names)))
    rows = []
    for name, ver, vals in con.execute(q, (prop, *names)):
        rows.append((name, ver, struct.unpack("<%dd" % (len(vals) // 8), vals)))
    con.close()
    return rows
