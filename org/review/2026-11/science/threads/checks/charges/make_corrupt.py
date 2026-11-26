import json, sys
C = sys.argv[1]; T = sys.argv[2]
def load(n): return json.load(open(f"{C}/{n}.json"))
def save(d, n): json.dump(d, open(f"{T}/corrupt/{n}.json", "w"), indent=1)
d = load("n7-abk-second-pair"); d["count"] = 43; save(d, "n7_count43")
d = load("n5-abk-bipyramid"); d["charges"][3] = d["charges"][4] = "441/131072"; save(d, "n5_q5_441")
d = load("n7-abk-second-pair"); d["charges"][5] = d["charges"][6] = "136000/1152921504606846976"; save(d, "n7_q7_136000")
d = load("n6-abk-plus-centre"); d["sites"][0] = ["3", "0", "1/10"]; save(d, "n6_site_moved")
d = load("n5-abk-bipyramid")
for z in d["zeros"]:
    z["box"] = [[0, 0, 0], [1e-9, 1e-9, 1e-9]]; z["index"] = 1
save(d, "n5_hints_garbage")
