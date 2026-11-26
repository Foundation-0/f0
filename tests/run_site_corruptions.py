#!/usr/bin/env python3
"""Site gate corruption tests: each corrupted copy of the tree must make
scripts/check_site.py exit nonzero; the uncorrupted copy must pass.
The -O case proves the gate still fails closed when Python drops
assert statements, because the gate raises errors instead.

Corruptions (applied to a temp copy of the whole tree):
  1 bad evidence tier   (ledger entry carries an unknown evidence word)
  2 dead internal link  (home page links to a file that does not exist)
  3 third-party script  (home page loads a script from another origin)
  4 bad tier under -O   (case 1 rerun with python -O)

Usage: python3 tests/run_site_corruptions.py   (exit 0 = gate behaves)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def corrupt_bad_tier(root):
    path = os.path.join(root, 'docs', 'data', 'ledger.json')
    data = json.load(open(path))
    data['milestones'][0]['evidence'] = 'bogus-tier'
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')
    return 'ledger schema: evidence enum'


def corrupt_dead_link(root):
    path = os.path.join(root, 'docs', 'index.html')
    text = open(path).read()
    text = text.replace('</body>',
                        '<a href="no-such-page-xyz.html">x</a></body>', 1)
    with open(path, 'w') as f:
        f.write(text)
    return 'links: relative href must resolve'


def corrupt_third_party_script(root):
    path = os.path.join(root, 'docs', 'index.html')
    text = open(path).read()
    text = text.replace('</body>',
                        '<script src="https://example.com/x.js"></script></body>', 1)
    with open(path, 'w') as f:
        f.write(text)
    return 'scripts: no third-party origins'


CASES = [
    ('bad_evidence_tier', corrupt_bad_tier, []),
    ('dead_internal_link', corrupt_dead_link, []),
    ('third_party_script', corrupt_third_party_script, []),
    ('bad_tier_under_O', corrupt_bad_tier, ['-O']),
]


def run_check(root, flags):
    return subprocess.run(
        [sys.executable, *flags, os.path.join(root, 'scripts', 'check_site.py')],
        capture_output=True, text=True)


def fresh_copy(td, name):
    root = os.path.join(td, name)
    shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns('.git'))
    return root


def main():
    ok = True
    with tempfile.TemporaryDirectory() as td:
        good = fresh_copy(td, 'good')
        p = run_check(good, [])
        if p.returncode != 0:
            print('FAIL: site gate rejects GOOD data:\n' + p.stdout + p.stderr)
            ok = False
        else:
            print('PASS: site gate accepts good data')

    for name, fn, flags in CASES:
        with tempfile.TemporaryDirectory() as td:
            root = fresh_copy(td, 'repo')
            note = fn(root)
            p = run_check(root, flags)
            if p.returncode == 0:
                print(f'FAIL: corruption {name} ({note}) NOT caught by site gate')
                ok = False
            else:
                print(f'PASS: corruption {name} blocked ({note})')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
