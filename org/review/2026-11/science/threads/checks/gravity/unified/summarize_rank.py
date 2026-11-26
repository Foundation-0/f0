import json, pathlib, numpy as np, math
H = pathlib.Path(__file__).resolve().parent
R = json.load(open(H / "rank_variables.json"))
out = []
def P(*a): print(*a); out.append(" ".join(map(str, a)))
nom = R["nominal"]["fits"]; keys = list(nom)
LOCAL = ["SPARC_outer", "SPARC_inner", "giant_spirals", "ATLAS3D_Re", "GC_r2500", "GC_r500"]
P(f"RAR only (no extra mass): class-balanced RMS {R['nominal']['RAR_only_rms']:.3f} dex; per class (rms, mean obs-pred): " +
  ", ".join(f"{c} {v[0]:.3f}/{v[1]:+.3f}" for c, v in R["nominal"]["RAR_only_class"].items()))
bs = R["bootstrap_rms"]; B = np.array([[b[k] for k in keys] for b in bs])
ranks = np.argsort(np.argsort(B, axis=1), axis=1) + 1
P(f"\nbootstrap replicates: {len(bs)}")
P("law|variable                 in-sample  boot mean+-sd  P(rank1) median rank | LOCO overall | LOCO rms (mean bias) per held-out class: " + " ".join(LOCAL))
order = sorted(keys, key=lambda k: nom[k]["loco_rms"])
for k in order:
    i = keys.index(k)
    lo = nom[k]["loco"]
    P(f"{k:28s} {nom[k]['rms']:.3f}   {B[:,i].mean():.3f}+-{B[:,i].std():.3f}   {np.mean(ranks[:,i]==1):.2f}   {np.median(ranks[:,i]):4.0f}   | {nom[k]['loco_rms']:.3f} | " +
      " ".join(f"{lo[c][0]:.2f}({lo[c][1]:+.2f})" for c in LOCAL))
P("\nperturbations: in-sample class-balanced RMS and rank among the 50 law|variable pairs")
P("law|variable                  nominal(rank)  hse x1.2(rank)  M*+0.2(rank)  M*-0.2(rank)")
rk = {}
for tag in ["nominal", "hse1.2", "mstar+0.2", "mstar-0.2"]:
    v = R[tag]["fits"]; s = sorted(v, key=lambda k: v[k]["rms"]); rk[tag] = {k: s.index(k) + 1 for k in s}
for k in sorted(keys, key=lambda k: nom[k]["rms"])[:20]:
    P(f"{k:28s} " + "  ".join(f"{R[t]['fits'][k]['rms']:.3f}({rk[t][k]:2d})" for t in ["nominal", "hse1.2", "mstar+0.2", "mstar-0.2"]))
P("\nbest-fit parameters (nominal), log10 of x relative to sample median x0 (x0 in log10 units):")
P("  x0: " + ", ".join(f"{k}={v:.3f}" for k, v in R["x0"].items()))
for k in sorted(keys, key=lambda k: nom[k]["rms"])[:12]:
    P(f"  {k:28s} p = {np.round(nom[k]['p'], 3).tolist()}")
open(H / "summarize_rank.out", "w").write("\n".join(out) + "\n")
