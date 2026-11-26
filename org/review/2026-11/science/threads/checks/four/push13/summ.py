import json,glob,collections,numpy as np
for f in sorted(glob.glob("out/push3_*_*.json")):
    r=json.load(open(f))
    bc=collections.Counter(x["best_phys"] for x in r); fc=collections.Counter(x["final_count"] for x in r)
    print(f, "runs",len(r),"best counts",dict(bc),"final counts",dict(fc),
      "T start min/ nearest final min %.3f %.3f"%(min(x["T_target_start"] for x in r),min(x["T_nearest_final"] for x in r)),
      "max |dtheta| %.1e"%max(x["dtheta_norm"] for x in r),"mean accepted %.0f"%np.mean([x["accepted"] for x in r]))
