"""Fixed vs moving split at eps = 1e-3 (uses analysis.json and structure_n*.json)."""
import json
A = json.load(open("analysis.json"))
out = {}
for n, N in [(6, 12), (7, 28), (8, 68), (9, 172), (10, 440), (11, 1144)]:
    F = json.load(open(f"structure_n{n}.json"))["common_limits_all_rays"]["count"]
    mf = A["cells"][f"{n}_e0.001"]["mean_frac"]; far = A["cells"][f"{n}_far"]["mean_frac"]
    mov = (mf * N - F) / (N - F)
    out[n] = dict(N_full=2 * N, fixed_full=2 * F, moving_full=2 * (N - F), mean_frac_e1em3=mf,
                  moving_real_frac_e1em3=mov, far_mean_frac=far)
    print(n, out[n])
json.dump(out, open("summary.json", "w"), indent=1)
