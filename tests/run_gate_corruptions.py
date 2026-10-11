#!/usr/bin/env python3
"""Gate corruption tests (ARCHITECTURE acceptance (ii)): each of four fixture
corruptions must make scripts/gate.py exit nonzero; the uncorrupted copy must pass.

Corruptions (tests/corruptions.json -> applied to docs/feed.json etc. in a temp copy):
  1 field-drop          (record missing required field)          -> check 1
  2 bad SHA             (head_sha not 40-hex)                    -> check 1
  3 fraction/decimal mismatch (agreement broken)                 -> check 1
  4 tier swap           (claimed record promoted into verified)  -> check 4

Usage: python3 tests/run_gate_corruptions.py   (exit 0 = gate behaves as required)
"""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def pick_claimed(feed):
    for r in feed['records']:
        if r['tier'] == 'claimed' and not r.get('stale'):
            return r
    raise SystemExit('fixture feed has no clean claimed record')


def corrupt_field_drop(feed, charts, records):
    r = pick_claimed(feed)
    del r['kappa_den']
    return 'check 1: missing required'


def corrupt_bad_sha(feed, charts, records):
    r = pick_claimed(feed)
    r['head_sha'] = 'zz' + r['head_sha'][2:]
    return 'check 1: sha pattern'


def corrupt_mismatch(feed, charts, records):
    r = pick_claimed(feed)
    r['kappa_decimal'] = '0.001' + r['kappa_decimal'][6:]  # break 15-digit agreement
    return 'check 1: fraction/decimal agreement'


def corrupt_tier_swap(feed, charts, records):
    r = pick_claimed(feed)
    # move this claimed row into the verified chart array (the exact failure the
    # separation check exists to block), keeping the record itself consistent
    charts['verified'].append({
        'pr': r['pr'], 'head_sha': r['head_sha'],
        'kappa_decimal': r['kappa_decimal'], 'tier': 'claimed',
        'pr_updated_at': r['pr_updated_at'],
        'pr_url': r['source_refs']['pr_url']})
    return 'check 4: separation'


CORRUPTIONS = {
    'field_drop': corrupt_field_drop,
    'bad_sha': corrupt_bad_sha,
    'fraction_decimal_mismatch': corrupt_mismatch,
    'tier_swap': corrupt_tier_swap,
}


def run_gate(root):
    return subprocess.run([sys.executable, os.path.join(root, 'scripts', 'gate.py'),
                           '--root', root],
                          capture_output=True, text=True)


def main():
    base = ROOT
    ok = True

    with tempfile.TemporaryDirectory() as td:
        # good data must pass
        good = os.path.join(td, 'good')
        shutil.copytree(base, good, ignore=shutil.ignore_patterns('.git'))
        p = run_gate(good)
        if p.returncode != 0:
            print('FAIL: gate rejects GOOD data:\n' + p.stdout + p.stderr)
            ok = False
        else:
            print('PASS: gate accepts good data')

    for name, fn in CORRUPTIONS.items():
        with tempfile.TemporaryDirectory() as td:
            root = os.path.join(td, 'repo')
            shutil.copytree(base, root, ignore=shutil.ignore_patterns('.git'))
            feed = json.load(open(os.path.join(root, 'docs', 'feed.json')))
            charts = json.load(open(os.path.join(root, 'docs', 'chart-data.json')))
            records = json.load(open(os.path.join(root, 'data', 'records.json')))
            note = fn(feed, charts, records)
            with open(os.path.join(root, 'docs', 'feed.json'), 'w') as f:
                json.dump(feed, f, indent=2, sort_keys=True, ensure_ascii=False)
                f.write('\n')
            with open(os.path.join(root, 'docs', 'chart-data.json'), 'w') as f:
                json.dump(charts, f, indent=2, sort_keys=True, ensure_ascii=False)
                f.write('\n')
            with open(os.path.join(root, 'data', 'records.json'), 'w') as f:
                json.dump(records, f, indent=2, sort_keys=True, ensure_ascii=False)
                f.write('\n')
            p = run_gate(root)
            if p.returncode == 0:
                print(f'FAIL: corruption {name} ({note}) NOT caught by gate')
                ok = False
            else:
                first = p.stdout.strip().splitlines()[0] if p.stdout.strip() else '(no stdout)'
                print(f'PASS: corruption {name} blocked ({note}) -> {first}')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
