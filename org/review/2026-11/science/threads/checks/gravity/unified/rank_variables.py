"""Part 2: rank candidate variables. In-sample class-balanced RMS, leave-one-class-out (LOCO), bootstrap over systems,
and perturbations (hydrostatic masses x1.2; stellar masses +-0.2 dex)."""
import sys, json, math, pathlib, itertools, time
import numpy as np
from multiprocessing import Pool
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import build_table as bt
from fitlib import *
NB = int(sys.argv[1]) if len(sys.argv) > 1 else 40
def local_arrays(dl=0.0, hse=1.0):
    rows = [d for d in bt.build(dl, hse, with_highz=False)]
    return arrays(rows)
def evaluate(A, x0s, combos, loco=True):
    res = {}
    for law, v in combos:
        p, L = fit(A, law, v, x0s[v])
        pred = LAWS[law][1](p, A, v, x0s[v])
        out = dict(p=list(map(float, p)), rms=math.sqrt(L), per_class=class_rms(A, pred))
        if loco:
            lo = {}
            for c in LOCAL:
                m = A["cls"] != c
                pc, _ = fit(sub(A, m), law, v, x0s[v], starts=[list(p)] + LAWS[law][2])
                pr = LAWS[law][1](pc, sub(A, ~m), v, x0s[v])
                r = np.log10(A["Mtot"][~m]) - pr
                lo[c] = (float(np.sqrt(np.mean(r ** 2))), float(np.mean(r)))
            out["loco"] = lo; out["loco_rms"] = float(np.sqrt(np.mean([lo[c][0] ** 2 for c in LOCAL])))
        res[(law, v)] = out
    return res
def boot_job(args):
    seed, dl, hse = args
    A = local_arrays(dl, hse); rng = np.random.default_rng(seed)
    idx = np.concatenate([rng.choice(np.where(A["cls"] == c)[0], (A["cls"] == c).sum()) for c in LOCAL])
    B = sub(A, idx)
    r = evaluate(B, X0, COMBOS, loco=False)
    return {f"{k[0]}|{k[1]}": v["rms"] for k, v in r.items()}
A0rows = local_arrays()
X0 = {v: float(np.median(np.log10(A0rows[v]))) for v in VARS}
COMBOS = [(law, v) for law in LAWS for v in VARS]
if __name__ == "__main__":
    t0 = time.time()
    out = {"x0": X0}
    for tag, dl, hse in [("nominal", 0.0, 1.0), ("hse1.2", 0.0, 1.2), ("mstar+0.2", 0.2, 1.0), ("mstar-0.2", -0.2, 1.0)]:
        A = local_arrays(dl, hse)
        base = BASE["RAR_only"](A); w = weights(A)
        r = evaluate(A, X0, COMBOS, loco=(tag == "nominal"))
        out[tag] = {"RAR_only_rms": math.sqrt(loss(base, A, w)), "RAR_only_class": class_rms(A, base),
                    "fits": {f"{k[0]}|{k[1]}": v for k, v in r.items()}}
        print(tag, "done", round(time.time() - t0), "s", flush=True)
    with Pool(2) as pool:
        bs = pool.map(boot_job, [(s, 0.0, 1.0) for s in range(NB)])
    out["bootstrap_rms"] = bs
    json.dump(out, open(HERE / "rank_variables.json", "w"), indent=1, default=float)
    print("total", round(time.time() - t0), "s")
