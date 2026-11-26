#!/usr/bin/env python3
"""Controls for check.py. Run with python3 -O from this folder.

Part A: configurations with other counts. find.py writes a certificate and
check.py must prove the count. The expected numbers are the ones the threads
state; where this run disagrees, it says so and continues.

Part B: corrupted inputs. Each must make check.py raise CheckFailed. A control
that passes is a failure of the checker, and this program then raises.
"""

import copy
import json
import os
import subprocess
import sys
from fractions import Fraction

import check as C

HERE = os.path.dirname(os.path.abspath(__file__))
THREADS = os.path.normpath(os.path.join(HERE, "..", "..", "threads", "checks"))
TMP = os.path.join(HERE, "certs", "controls")
os.makedirs(TMP, exist_ok=True)


def write(path, obj):
    with open(path, "w") as fh:
        json.dump(obj, fh)
    return path


def frac_str(x):
    x = Fraction(x)
    return "%d/%d" % (x.numerator, x.denominator)


def run_find(cfg, cert, starts=20000):
    subprocess.run([sys.executable, os.path.join(HERE, "find.py"), cfg, cert, str(starts), "1"],
                   check=True, stderr=subprocess.DEVNULL)


def count_of(cfg, cert):
    out = C.check(cfg, cert)
    for line in out.splitlines():
        if line.startswith("PROVED exactly"):
            return int(line.split()[2]), out
    raise C.CheckFailed("no exact count in the output")


def rounded(cfg_path, digits):
    sites, charges = C.load_config(cfg_path)
    r = lambda x: frac_str(round(Fraction(x), digits))
    return {"sites": [[r(v) for v in s] for s in sites], "charges": [r(q) for q in charges]}


def part_a():
    lines = ["Part A: other configurations, count proved by find.py + check.py"]
    for d in (4, 3):
        subprocess.run([sys.executable, os.path.join(THREADS, "four/verify/short_cert.py"),
                        os.path.join(THREADS, "four/flat-route/fat2.json"),
                        os.path.join(TMP, "fat2_%ddp.json" % d), "fat2_%ddp" % d, str(d)], check=True)
    cases = [
        ("second family (threads: exactly 9)", os.path.join(THREADS, "charges/configs/n4-second-family.json"), 9),
        ("jet route, linear term -1e-10 (threads: 9)", os.path.join(THREADS, "four/controls/ctrl_lam1e-10.json"), 9),
        ("jet route, one charge x 1.000001 (threads: 5)", os.path.join(THREADS, "four/controls/ctrl_charge1.json"), 5),
        ("fat2.json rounded to 4 decimals, as short_cert.py does (threads: 9)",
         os.path.join(TMP, "fat2_4dp.json"), 9),
        ("fat2.json rounded to 3 decimals, as short_cert.py does (threads: 5)",
         os.path.join(TMP, "fat2_3dp.json"), 5),
        ("the printed 5-decimal table rounded again to 4 (indep_count.py: 7)",
         write(os.path.join(TMP, "short_4dp.json"), rounded(os.path.join(HERE, "short_table.json"), 4)), 7),
        ("a hand-picked tetrahedron, unequal charges (indep_count.py: 5)",
         write(os.path.join(TMP, "random.json"), {
             "sites": [["0", "0", "0"], ["1", "0", "0"], ["3/10", "9/10", "0"], ["2/5", "3/10", "4/5"]],
             "charges": ["1", "2", "3/2", "7/10"]}), 5),
    ]
    try:
        got, _ = count_of(os.path.join(TMP, "fold_quoted.json"), os.path.join(TMP, "fold_quoted.cert.json"))
        lines.append("  %-70s proved exactly %2d  %s" % (
            "short table, charge 3 set 1.2e-17 above a fold (review: 9)", got, "agrees" if got == 9 else "DIFFERS from 9"))
    except C.CheckFailed as e:
        lines.append("  fold case not closed (%s)" % e)
    for label, cfg, want in cases:
        cert = os.path.join(TMP, os.path.basename(cfg).replace(".json", ".cert.json"))
        try:
            run_find(cfg, cert)
            got, _ = count_of(cfg, cert)
            mark = "agrees" if got == want else "DIFFERS from %d" % want
            lines.append("  %-70s proved exactly %2d  %s" % (label, got, mark))
        except (subprocess.CalledProcessError, C.CheckFailed) as e:
            lines.append("  %-70s not closed (%s)" % (label, type(e).__name__))
    return lines


def expect_fail(label, fn):
    try:
        fn()
    except C.CheckFailed as e:
        return "  rejected as it should: %-50s (%s)" % (label, e)
    raise SystemExit("CONTROL PASSED THAT MUST FAIL: " + label)


def part_b():
    lines = ["Part B: corrupted inputs, each must be rejected"]
    cfg = os.path.join(HERE, "short_table.json")
    cert = os.path.join(HERE, "certs", "short_table.cert.json")
    base_cfg = json.load(open(cfg))
    base_cert = json.load(open(cert))

    def with_cfg(mod, label):
        c = copy.deepcopy(base_cfg)
        mod(c)
        p = write(os.path.join(TMP, "bad_cfg.json"), c)
        lines.append(expect_fail(label, lambda: C.check(p, cert, 11)))

    def with_cert(mod, label, expected=11):
        c = copy.deepcopy(base_cert)
        mod(c)
        p = write(os.path.join(TMP, "bad_cert.json"), c)
        lines.append(expect_fail(label, lambda: C.check(cfg, p, expected)))

    # the clean run must pass first
    C.check(cfg, cert, 11)
    lines.append("  clean run proves 11: yes")

    def scale_charge(c, i, f):
        c["charges"][i] = frac_str(Fraction(c["charges"][i]) * Fraction(f))

    with_cfg(lambda c: scale_charge(c, 0, "1.000001"), "charge 1 times 1.000001")
    with_cfg(lambda c: scale_charge(c, 2, "0.99999"), "charge 3 times 0.99999")
    with_cfg(lambda c: c["sites"][1].__setitem__(0, "-0.05643"), "one coordinate changed by 1e-5")
    with_cfg(lambda c: c["sites"].reverse(), "sites listed in reverse order")
    with_cfg(lambda c: c["charges"].__setitem__(1, "-0.28010"), "a negative charge")
    with_cfg(lambda c: c["sites"][3].__setitem__(2, c["sites"][0][2]) or
             c["sites"][2].__setitem__(2, c["sites"][0][2]) or
             c["sites"][1].__setitem__(2, c["sites"][0][2]), "four coplanar sites")
    with_cert(lambda c: c.__setitem__("P", 100), "certificate on another grid")
    with_cert(lambda c: None, "claim of 13 points", expected=13)
    with_cert(lambda c: None, "claim of 9 points", expected=9)

    def drop_box(c):
        c["boxes"].pop(5)
        out, i = [], 0
        t = c["tree"]
        while i < len(t):
            if t[i] == "K":
                j = t.index(".", i)
                m = int(t[i + 1:j])
                out.append("K%d." % (m - 1 if m > 5 else m))
                i = j + 1
            else:
                out.append(t[i])
                i += 1
        c["tree"] = "".join(out)
    with_cert(drop_box, "one uniqueness box removed")
    with_cert(lambda c: c["boxes"].append(copy.deepcopy(c["boxes"][0])), "a box listed twice")

    def shift_box(c):
        b = c["boxes"][3]
        w = int(b["hi"][0]) - int(b["lo"][0])
        b["lo"][0] = str(int(b["lo"][0]) + 3 * w)
        b["hi"][0] = str(int(b["hi"][0]) + 3 * w)
    with_cert(shift_box, "a box moved off its zero")

    def first_leaf(c, old, new):
        t = c["tree"]
        i = t.index(old)
        c["tree"] = t[:i] + new + t[i + len(old):]
    with_cert(lambda c: first_leaf(c, "N", "H"), "a Taylor leaf relabelled hull")
    with_cert(lambda c: first_leaf(c, "H", "N"), "a hull leaf relabelled Taylor")
    def k_to_taylor(c):
        t = c["tree"]
        i = t.index("K")
        j = t.index(".", i)
        c["tree"] = t[:i] + "N" + t[j + 1:]
    with_cert(k_to_taylor, "a leaf inside a box relabelled Taylor")
    with_cert(lambda c: c.__setitem__("tree", "x" + c["tree"][1:]) if c["tree"][0] != "x"
              else c.__setitem__("tree", "y" + c["tree"][1:]), "first split on another axis")
    with_cert(lambda c: c.__setitem__("tree", c["tree"][:-1]), "tree cut short by one token")
    with_cert(lambda c: c.__setitem__("tree", c["tree"] + "H"), "tree with a token added")
    with_cert(lambda c: c.__setitem__("tree", "K0."), "whole root claimed inside one box")
    with_cert(lambda c: c.__setitem__("tree", c["tree"] + "D"), "tree ending in a bare D")
    with_cert(lambda c: c.__setitem__("tree", c["tree"].replace(".", "", 1)), "a K token without its full stop")
    with_cert(lambda c: c.__setitem__("tree", list(c["tree"])), "tree given as a list")
    with_cert(lambda c: c["boxes"][0]["lo"].pop(), "a box corner with two coordinates")
    with_cert(lambda c: c["boxes"][0]["lo"].__setitem__(0, int(c["boxes"][0]["lo"][0])), "a box corner as a bare number")
    lines.append(expect_fail("an unquoted decimal that a float would move across a fold", lambda: C.check(
        os.path.join(TMP, "fold_unquoted.json"), os.path.join(TMP, "fold_unquoted.cert.json"), 11)))
    dup = os.path.join(TMP, "dup_key.json")
    with open(dup, "w") as fh:
        fh.write(open(cfg).read().replace('"charges":', '"charges": ["1", "-1", "1", "1"], "charges":', 1))
    lines.append(expect_fail("a key given twice, a negative charge in the first", lambda: C.check(dup, cert, 11)))
    return lines


def main():
    lines = part_a() + [""] + part_b()
    text = "\n".join(lines)
    print(text)
    with open(os.path.join(HERE, "controls.out"), "w") as fh:
        fh.write(text + "\n")


if __name__ == "__main__":
    main()
