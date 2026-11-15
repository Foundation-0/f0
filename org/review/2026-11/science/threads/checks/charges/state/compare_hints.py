#!/usr/bin/env python3
"""After the independent count: compare my zero balls with the certificate's zero boxes (hints only).

For each of my zeros, find certificate boxes whose 'box' contains my ball centre, and compare indices.
This is a consistency check between two separately produced lists; it is not part of the proof.
"""
import json
import sys
from fractions import Fraction


def main(mine_path, cert_path):
    M = json.load(open(mine_path))
    C = json.load(open(cert_path))
    zs = C["zeros"]
    used = [0] * len(zs)
    bad = 0
    for z in M["zeros"]:
        x = [Fraction(v) for v in z["centre"]]
        hits = []
        for k, cz in enumerate(zs):
            lo, hi = cz["box"]
            if all(Fraction(lo[a]) <= x[a] <= Fraction(hi[a]) for a in range(3)):
                hits.append(k)
        if len(hits) != 1:
            bad += 1
            print("my zero", z["centre_float"], "in", len(hits), "certificate boxes")
            continue
        k = hits[0]
        used[k] += 1
        if zs[k]["index"] != z["index"]:
            bad += 1
            print("index differs at", z["centre_float"], z["index"], zs[k]["index"])
    unmatched = sum(1 for u in used if u == 0)
    print(f"{cert_path.split('/')[-1]}: mine={len(M['zeros'])} cert={len(zs)} "
          f"matched one-to-one={sum(1 for u in used if u == 1)} unmatched cert boxes={unmatched} problems={bad}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
