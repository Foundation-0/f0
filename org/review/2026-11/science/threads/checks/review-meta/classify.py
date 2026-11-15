#!/usr/bin/env python3
"""Statistics of the team review of pull request 58.

Input: the review's own record, findings.json (in the pull-request-60 folder pr58-addendum/), and the table below, which
assigns each of its 68 problem findings a kind, the layer where the defect sits, and the direction of the error.
The assignment is the reviewed author's reading of each finding and is open to dispute, which is why it is a table
in a file and not prose. The findings are taken in the order the record lists them: passes 1 to 11, and inside a
pass in file order, skipping the entries marked OK.

Kinds:  SC    the folder is not self-contained (a file, input, program or cited document is missing or external)
        LABEL a verdict word or evidence mark is stronger than the evidence, or labels disagree
        SCOPE wording wider than what was tested ("every", "all", "exactly", "whole")
        NUM   a number or statement that the shipped data contradicts
        IND   independence of checks overstated
        CHK   a checking program can pass when it should not, or is fragile
        STAT  circular fit, selective quoting, or a statistic with no stated meaning
        PROOF a derivation is asserted or sketched and not written
        HYG   housekeeping
Layers: program, packaging, note (one thread's note or report), synthesis (README, convergences, fabric, pull-request text, state notes)
Direction: up = the text claims more than the evidence, down = less, none = no direction
Usage: classify.py <findings.json>"""
import json, sys, collections
TABLE = """
01 SC packaging none
02 NUM note up
03 PROOF note none
04 CHK program none
05 LABEL note up
06 SCOPE note up
07 CHK program up
08 PROOF note none
09 SCOPE note up
10 SCOPE synthesis up
11 HYG note none
12 SC packaging none
13 NUM note up
14 IND note up
15 SCOPE note up
16 IND note up
17 SCOPE note up
18 SCOPE note none
19 HYG program none
20 SC packaging none
21 SC packaging none
22 STAT note up
23 STAT note up
24 LABEL synthesis up
25 NUM synthesis up
26 NUM note up
27 SCOPE note up
28 STAT note up
29 NUM synthesis down
30 HYG synthesis none
31 HYG synthesis none
32 HYG packaging none
33 SC packaging none
34 NUM note up
35 NUM note up
36 IND note up
37 LABEL note up
38 SCOPE note up
39 HYG packaging none
40 SC packaging none
41 SC packaging none
42 PROOF program none
43 CHK program none
44 CHK program none
45 PROOF program none
46 SC packaging none
47 SC packaging none
48 SCOPE note up
49 SCOPE note up
50 NUM note up
51 LABEL synthesis up
52 SCOPE synthesis up
53 SCOPE note up
54 SC packaging none
55 IND note up
56 IND note up
57 NUM synthesis up
58 IND note up
59 LABEL synthesis up
60 PROOF note up
61 CHK program up
62 PROOF note up
63 NUM note up
64 SCOPE note up
65 NUM note up
66 CHK program none
67 CHK program none
68 SCOPE note up
"""
# pairs of findings that two different passes reached separately (same defect)
SAME = [(5, 51), (6, 68), (14, 55), (10, 52), (53, 64), (40, 54), (25, 57), (36, 58)]
J = json.load(open(sys.argv[1])); allp = {**J["prior_results"], **J["inline_results"]}
rows = []; ok = 0
for k in sorted(allp, key=int):
    for x in allp[k]["findings"]:
        u = x.upper().lstrip()
        if u.startswith("[OK"): ok += 1; continue
        sev = "BLOCK" if u.startswith("[BLOCK") else "MAJOR" if u.startswith("[MAJOR") else "MINOR"
        rows.append((int(k), sev, x))
tab = [l.split() for l in TABLE.strip().splitlines()]
if len(tab) != len(rows): raise SystemExit(f"table has {len(tab)} rows, record has {len(rows)} problem findings")
print(f"findings in the record: {len(rows) + ok}; confirmations (OK): {ok}; problem findings: {len(rows)}")
sev = collections.Counter(r[1] for r in rows); print("by severity:", dict(sev))
def cross(col, name):
    c = collections.defaultdict(collections.Counter)
    for (i, kind, layer, direc), r in zip(tab, rows): c[(kind, layer, direc)[col]][r[1]] += 1
    print(f"\nby {name}:   (BLOCK, MAJOR, MINOR, all)")
    for key, v in sorted(c.items(), key=lambda kv: -sum(kv[1].values())):
        print(f"  {key:10s} {v['BLOCK']:3d} {v['MAJOR']:3d} {v['MINOR']:3d} {sum(v.values()):4d}")
cross(0, "kind"); cross(1, "layer"); cross(2, "direction")
heavy = [(t, r) for t, r in zip(tab, rows) if r[1] in ("BLOCK", "MAJOR")]
print(f"\nblocking and major findings: {len(heavy)}; of these in a program: {sum(1 for t, r in heavy if t[2] == 'program')}, packaging: {sum(1 for t, r in heavy if t[2] == 'packaging')}, a note: {sum(1 for t, r in heavy if t[2] == 'note')}, the synthesis layer: {sum(1 for t, r in heavy if t[2] == 'synthesis')}")
directed = [t for t in tab if t[3] != "none"]
print(f"findings with a direction: {len(directed)}; claiming more than the evidence: {sum(1 for t in directed if t[3] == 'up')}; claiming less: {sum(1 for t in directed if t[3] == 'down')}")
# physics and data pass against the mathematics passes
kind_of_pass = {1: "math", 2: "math", 3: "math", 6: "math", 7: "math", 8: "math", 10: "math", 4: "data", 5: "cross", 9: "cross", 11: "cross"}
c = collections.defaultdict(collections.Counter)
for (i, kind, layer, direc), r in zip(tab, rows): c[kind_of_pass[r[0]]][kind] += 1
print("\nkinds by type of pass:")
for key in ("math", "data", "cross"): print(f"  {key:6s}", dict(c[key]))
# capture and recapture: the thread passes (1-8, 10) against the cross-cutting label pass (9), wording kinds only
word = {"LABEL", "SCOPE", "NUM", "IND"}
n1 = sum(1 for t, r in zip(tab, rows) if r[0] not in (9, 11) and t[1] in word)
n2 = sum(1 for t, r in zip(tab, rows) if r[0] == 9 and t[1] in word)
idx = {int(t[0]): r[0] for t, r in zip(tab, rows)}
m = sum(1 for a, b in SAME if (idx[a] not in (9, 11)) and idx[b] == 9 and tab[b - 1][1] in word)
est = (n1 + 1) * (n2 + 1) / (m + 1) - 1
print(f"\nwording defects (LABEL, SCOPE, NUM, IND): thread passes found {n1}, the label pass found {n2}, both found {m}")
print(f"capture-recapture estimate of all such defects (Chapman): {est:.0f}; found by either: {n1 + n2 - m}; estimated not found: {est - (n1 + n2 - m):.0f}")
