#!/usr/bin/env python3
"""Fetch the published tables and two repository scripts that the programs in this folder read: tables into ./sources/,
the scripts into ./unified/repo_copy/.

Python standard library, plus `curl` and, for one PDF, `pdftotext` (poppler). Nothing here is stored in the repository:
Every file is checked against the sha256 recorded below. See ../../SOURCES.md for what each file is, where it comes from and the date it was read.

Usage:  python3 fetch_sources.py            # fetch what is missing
        python3 fetch_sources.py --list     # print the table of files and addresses
One request per 1.5 s. Existing files are kept.
"""
import gzip
import hashlib
import io
import pathlib
import shutil
import subprocess
import sys
import tarfile
import time

ROOT = pathlib.Path(__file__).resolve().parent / "sources"

SHA256 = {  # sha256 of the bytes read on 2026-11-15 (for the VizieR file: of the lines that do not start with '#')
    "sparc/SPARC_Lelli2016c.mrt": "5aa0501f6b0d881fa579030e315e7b5b6ef561a5bd3a07472f9929c7e5728243",
    "sparc/MassModels_Lelli2016c.mrt": "9108994b12cc401b94a1768beca61c53ec354779385c9c9cc571049f3043244c",
    "atlas3d/Cappellari2011a_Atlas3D_Paper1_Table3.txt": "771c40149c64bdf6177e8646ee9439fdafb342a1995b9306a6884530719959fc",
    "atlas3d/Cappellari2013a_Atlas3D_Paper15_Table1.txt": "ba338a921dd454cc698274e7cf737d6c0edf485bcbcb3b4f610854fee934711d",
    "atlas3d/Cappellari2013b_Atlas3D_Paper20_Table1.txt": "dd1ccf67c8cdc4baeb2377d08691ad598d71aa7cec66cc041fa263d779f33bb2",
    "from_accel/ubler2017_vizier.tsv": "91742f444278810e0fef788b1ce3512d193e35248452ad0e8184e205b1d0a5a7",
    "arxiv-2109.03828/paper_ss.tex": "9add900c87f575c60771b390e8014df4726340be1528ce1ae3aaecbdc14b8e6b",
    "arxiv-2207.02906/paper_ssvla.tex": "a94d0b3d85fb59ab333e13a3534d91a4a21a924e53717c77f773b015d185288d",
    "arxiv-2207.02906/table_dyn.tex": "50a14956ccddb13a088825f6fca3072d8b2a22793ae6251cacd3714dfdcd9e61",
    "arxiv-1909.09080/pogle.tex": "76fdec30803f078e0df58e9f88c207ee793b197ffa47cecfffd332db4a81010d",
    "arxiv-astro-ph_0507092/mprof.tex": "3066c60b17ada73ba7da304b2ba03ae51a2f2f1b4d92356371c3f0a1c2416755",
    "arxiv-0805.2320/ms.tex": "34b71928a5b420a860ecd1886072a1916dd95819f6c22143abddfbe4f3c200a4",
    "arxiv-1409.3845/Lovisari_groups.tex": "3b5cac5ec40288362e1511f6d7d968922b9b085aca29eee90046a87a11c45ee2",
    "arxiv-1309.3565/ms.tex": "340533654ea063293528070903ba3524701de8b0cbff97f41cd4b34a50c2958e",
    "from_accel/rc41_2006.03046.txt": "fa1b114e7c34d81ebb347ac1d1deb430be11e0fe00fbb827be632a11faa07cb2",
    "../unified/repo_copy/wave7_group_cluster_threshold_audit.py": "5de311fa11f22285f62cf82dd5cfc9e2651c2bfbe990fb194e6517171608dc29",
    "../unified/repo_copy/wave10_covariant_jeans_unification.py": "af8a2459aa8f5885250ab6b5914c50cc852bcc691982c8ef5cf692603bece927",
}
REPO_COMMIT = "8f96c4b240f985c3e3e1b81f64c3e91a5534d4f2"   # Foundation-0/gravity, the head the review pinned
REPO_FILES = ["wave7_group_cluster_threshold_audit.py", "wave10_covariant_jeans_unification.py"]


PLAIN = [  # (relative path, address)
    ("sparc/SPARC_Lelli2016c.mrt", "https://astroweb.case.edu/SPARC/SPARC_Lelli2016c.mrt"),
    ("sparc/MassModels_Lelli2016c.mrt", "https://astroweb.case.edu/SPARC/MassModels_Lelli2016c.mrt"),
    ("atlas3d/Cappellari2011a_Atlas3D_Paper1_Table3.txt",
     "https://groups.physics.ox.ac.uk/atlas3d/tables/Cappellari2011a_Atlas3D_Paper1_Table3.txt"),
    ("atlas3d/Cappellari2013a_Atlas3D_Paper15_Table1.txt",
     "https://groups.physics.ox.ac.uk/atlas3d/tables/Cappellari2013a_Atlas3D_Paper15_Table1.txt"),
    ("atlas3d/Cappellari2013b_Atlas3D_Paper20_Table1.txt",
     "https://groups.physics.ox.ac.uk/atlas3d/tables/Cappellari2013b_Atlas3D_Paper20_Table1.txt"),
    ("from_accel/ubler2017_vizier.tsv",
     "https://vizier.cfa.harvard.edu/viz-bin/asu-tsv?-source=J/ApJ/842/121&-out.max=unlimited&-out.all"),
]
# arXiv e-print archives: (directory name, arXiv identifier, members to keep)
EPRINT = [
    ("arxiv-2109.03828", "2109.03828", ["paper_ss.tex"]),
    ("arxiv-2207.02906", "2207.02906", ["paper_ssvla.tex", "table_dyn.tex"]),
    ("arxiv-1909.09080", "1909.09080", ["pogle.tex"]),
    ("arxiv-astro-ph_0507092", "astro-ph/0507092", ["mprof.tex"]),
    ("arxiv-0805.2320", "0805.2320", ["ms.tex"]),
    ("arxiv-1409.3845", "1409.3845", ["Lovisari_groups.tex"]),
    ("arxiv-1309.3565", "1309.3565", ["ms.tex"]),
]
PDF = ("from_accel/rc41_2006.03046.txt", "https://arxiv.org/pdf/2006.03046")


def get(url):
    """Download with curl, which uses the system certificate store (certificates are always verified)."""
    r = subprocess.run(["curl", "-fsSL", "--max-time", "180", "-A", "research-script", url], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"curl exit {r.returncode}: {r.stderr.decode(errors='replace').strip()[:200]}")
    return r.stdout


def digest(path):
    b = path.read_bytes()
    if path.name.startswith("ubler"):
        b = b"".join(l for l in b.splitlines(True) if not l.startswith(b"#"))
    return hashlib.sha256(b).hexdigest()


def verify(rel):
    p = ROOT / rel
    if rel in SHA256 and p.exists() and digest(p) != SHA256[rel]:
        raise RuntimeError(f"sha256 mismatch for {rel}: the source changed since 2026-11-15")


def main():
    if "--list" in sys.argv:
        for rel, url in PLAIN:
            print(f"{rel}\t{url}")
        for d, ident, members in EPRINT:
            print(f"{d}/{','.join(members)}\thttps://arxiv.org/e-print/{ident}")
        print(f"{PDF[0]}\t{PDF[1]} (pdftotext -layout)")
        for f in REPO_FILES:
            print(f"../unified/repo_copy/{f}\thttps://raw.githubusercontent.com/Foundation-0/gravity/{REPO_COMMIT}/{f}")
        return 0
    failed = []
    jobs = []
    jobs += [("plain", rel, url) for rel, url in PLAIN]
    jobs += [("eprint", d, (ident, members)) for d, ident, members in EPRINT]
    jobs += [("pdf", PDF[0], PDF[1])]
    jobs += [("repo", "../unified/repo_copy/" + f, f) for f in REPO_FILES]
    for kind, rel, arg in jobs:
        try:
            if kind == "plain":
                dest = ROOT / rel
                if dest.exists() and dest.stat().st_size > 0:
                    print("kept", rel); continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(get(arg)); print("fetched", rel)
            elif kind == "eprint":
                ident, members = arg
                dest = ROOT / rel
                if all((dest / m).exists() for m in members):
                    print("kept", rel); continue
                raw = get(f"https://arxiv.org/e-print/{ident}")
                dest.mkdir(parents=True, exist_ok=True)
                try:
                    tf = tarfile.open(fileobj=io.BytesIO(raw), mode="r:*")
                    names = {pathlib.PurePosixPath(n).name: n for n in tf.getnames()}
                    for m in members:
                        (dest / m).write_bytes(tf.extractfile(names[m]).read())
                except tarfile.ReadError:  # a single gzipped TeX file
                    (dest / members[0]).write_bytes(gzip.decompress(raw))
                print("fetched", rel, members)
            elif kind == "repo":
                dest = ROOT / rel
                if dest.exists() and dest.stat().st_size > 0:
                    verify(rel); print("kept", rel); continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(get(f"https://raw.githubusercontent.com/Foundation-0/gravity/{REPO_COMMIT}/{arg}"))
                verify(rel); print("fetched", rel)
            else:
                dest = ROOT / rel
                if dest.exists() and dest.stat().st_size > 0:
                    print("kept", rel); continue
                if not shutil.which("pdftotext"):
                    raise RuntimeError("pdftotext not found")
                dest.parent.mkdir(parents=True, exist_ok=True)
                tmp = dest.with_suffix(".pdf")
                tmp.write_bytes(get(arg))
                subprocess.run(["pdftotext", "-layout", str(tmp), str(dest)], check=True)
                tmp.unlink(); print("fetched", rel)
        except Exception as e:  # report and go on
            failed.append(rel); print("ERROR", rel, repr(e))
        time.sleep(1.5)
    for rel in SHA256:
        try:
            if (ROOT / rel).exists():
                verify(rel)
        except Exception as e:
            failed.append(rel); print("ERROR", rel, repr(e))
    if failed:
        print("FAILED:", ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
