"""Sanity and corruption checks (explicit raises, so they also run under python -O)."""
import sys, pathlib, re, subprocess, shutil, tempfile, math
here = pathlib.Path(__file__).parent; sys.path.insert(0, str(here))
from model import nu, M_threshold, sigJ, ftrap
def need(c, msg):
    if not c: raise SystemExit("CHECK FAILED: " + msg)
    print("ok:", msg)
need(abs(math.log10(M_threshold(185.59)) - math.log10(2.98e11)) < 0.003, "threshold mass A = 2.98e11")
need(abs(math.log10(M_threshold(200.0)) - math.log10(4.02e11)) < 0.003, "threshold mass B = 4.02e11")
need(abs(sigJ("A", 0.5) - 114.36) < 0.01 and abs(sigJ("A", 1.0) - 69.92) < 0.01, "sigma_J(z) matches wave10 certificate at z=0.5, 1")
need(float(nu(0.01)) > float(nu(1)) > float(nu(100)) > 1, "nu decreasing toward 1")
need(float(ftrap(150, 185.59)) == 0 and abs(float(ftrap(371.18, 185.59)) - 0.75) < 1e-3, "f_trap zero below threshold, 0.75 at 2 sigma_J")
# corruption 1: change one v_c in the RC41 text copy; the row-match guard in t6 must report a mismatch
tmp = pathlib.Path(tempfile.mkdtemp())
shutil.copytree(here, tmp / "g", ignore=shutil.ignore_patterns("__pycache__"))
f = tmp / "g/sources/from_accel/rc41_2006.03046.txt"; t = f.read_text()
i = t.index("Appendix D"); j = t.index("  2     U3_21388", i)
t2 = t[:j] + t[j:].replace(" 230 ", " 231 ", 1); f.write_text(t2)
r = subprocess.run([sys.executable, "-O", str(tmp / "g/t6_highz_fdm.py")], capture_output=True, text=True)
need("row mismatch 2" in r.stdout, "t6 detects a corrupted v_c in Table D1 (run under -O)")
# corruption 2: double sigma_e of all galaxies in ATLAS3D table XV; the model-A step test must change sign/size
f = tmp / "g/sources/atlas3d/Cappellari2013a_Atlas3D_Paper15_Table1.txt"
lines = [l if l.startswith("#") or not l.strip() else re.sub(r"^(\s*\S+\s+)(\S+)", lambda m: m.group(1) + ("%.3f" % (float(m.group(2)) - 0.6)), l) for l in f.read_text().splitlines()]
f.write_text("\n".join(lines) + "\n")
r = subprocess.run([sys.executable, "-O", str(tmp / "g/t3_atlas3d.py")], capture_output=True, text=True)
need("sigma_e>185.59 (0 gal)" in r.stdout or "n=0" in r.stdout or r.returncode != 0 or "(36 gal)" not in r.stdout,
     "t3 output changes when sigma_e is corrupted (no galaxy left above threshold)")
shutil.rmtree(tmp)
