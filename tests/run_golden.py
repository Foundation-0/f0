#!/usr/bin/env python3
"""Golden-file parser regression (offline). Exit 0 iff every case parses to expected."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from fetch import parse_kappa  # noqa: E402


def main():
    g = json.load(open(os.path.join(ROOT, 'tests', 'golden_kappa_parse.json')))
    fails = 0
    for c in g['cases']:
        text = c['title'] + '\n' + c['body']
        r = parse_kappa(text)
        exp = c['expected']
        if r is None:
            print(f"FAIL pr {c['pr']}: parsed None, expected {exp}")
            fails += 1
            continue
        got = (r['num'], r['den'], r['decimal'])
        want = (exp['kappa_num'], exp['kappa_den'], exp['kappa_decimal'])
        if got != want:
            print(f"FAIL pr {c['pr']}: got {got} want {want}")
            fails += 1
        elif not r['agree']:
            print(f"FAIL pr {c['pr']}: fraction/decimal disagree")
            fails += 1
        else:
            print(f"ok pr {c['pr']} [{r['kind']}]: {got[2]}")
    if fails:
        print(f"{fails} golden case(s) failed")
        sys.exit(1)
    print(f"all {len(g['cases'])} golden cases pass")


if __name__ == '__main__':
    main()
