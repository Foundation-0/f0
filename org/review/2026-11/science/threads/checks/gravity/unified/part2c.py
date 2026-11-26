"""Onset and two-variable exponents under perturbations (no bootstrap): hydrostatic x1.2, stellar masses +-0.2 dex,
and with ATLAS3D or giant spirals removed."""
import sys, pathlib, math, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import part2b as pb
from fitlib import *
out = []
def P(*a): print(*a, flush=True); out.append(" ".join(map(str, a)))
for tag, dl, hse, drop in [("nominal", 0, 1, None), ("hse x1.2", 0, 1.2, None), ("M* +0.2", 0.2, 1, None), ("M* -0.2", -0.2, 1, None),
                           ("no ATLAS3D", 0, 1, "ATLAS3D_Re"), ("no giant spirals", 0, 1, "giant_spirals")]:
    A = pb.local(dl, hse)
    if drop: A = sub(A, A["cls"] != drop)
    pb.A = A
    pb.LOCAL[:] = [c for c in ["SPARC_outer", "SPARC_inner", "giant_spirals", "ATLAS3D_Re", "GC_r2500", "GC_r500"] if c != drop]
    r = pb.onset_job(-1); p2, L2 = pb.fit2(A)
    P(f"{tag:17s}: " + "; ".join(f"{c[0]} sigma_J={x[0]:.0f} R={x[1]:.2f} s={x[2]:.1f}" for c, x in zip(pb.CASES, r)) + f" | two-var a={p2[1]:.2f} b={p2[2]:.2f} rms {math.sqrt(L2):.3f}")
open(pathlib.Path(__file__).with_suffix(".out"), "w").write("\n".join(out) + "\n")
