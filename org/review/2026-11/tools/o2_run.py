#!/usr/bin/env python3
"""O2 verifier runner: mechanical runs only, no scientific judgment.

For each H1 inventory row with type=verifier, in a clone pinned by
h1-method.md, run up to three modes and record exit code, duration,
output hash and whether the run dirtied the tree (restored after):
  documented   python <file>            cwd = repository root
  optimised    python -O <file>         cwd = repository root
  empty-cwd    python <abs file>        cwd = empty temp folder
Corrupted-input probes need per-verifier knowledge and belong to
F2; this runner records them as MANUAL. Bare-assert counts give
the -O risk signal beside the optimised run.

Classes: PASS0, FAILNZ, TIMEOUT, NEEDS-ARGS (exit 2 with argparse),
DEP-MISSING (ModuleNotFoundError, module recorded), NOT-RUN.

Usage:
  python3 o2_run.py --inventory FILE --repos DIR --out FILE \
      [--timeout 120] [--python python3] [--only repo,repo]
"""
import argparse
import csv
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import time

ASSERT_RE = re.compile(r'^\s*assert\b', re.M)
MOD_RE = re.compile(r"No module named '([^']+)'")


def run(cmd, cwd, timeout):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           errors='replace', timeout=timeout)
        out = (p.stdout or '') + (p.stderr or '')
        return p.returncode, round(time.time() - t0, 1), out
    except subprocess.TimeoutExpired as e:
        out = ((e.stdout or b'').decode('utf-8', 'replace')
               if isinstance(e.stdout, bytes) else (e.stdout or ''))
        return 'TIMEOUT', round(time.time() - t0, 1), out


def classify(code, out, has_argparse):
    if code == 'TIMEOUT':
        return 'TIMEOUT', ''
    if code == 0:
        return 'PASS0', ''
    m = MOD_RE.search(out)
    if m:
        return 'DEP-MISSING', m.group(1)
    if code == 2 and has_argparse:
        return 'NEEDS-ARGS', ''
    return 'FAILNZ', ''


def tree_dirty(repo):
    p = subprocess.run(['git', '-C', repo, 'status', '--porcelain'],
                       capture_output=True, text=True)
    return 'yes' if p.stdout.strip() else 'no'


def restore(repo):
    subprocess.run(['git', '-C', repo, 'checkout', '--', '.'],
                   capture_output=True)
    subprocess.run(['git', '-C', repo, 'clean', '-fd'],
                   capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--inventory', required=True)
    ap.add_argument('--repos', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--timeout', type=int, default=120)
    ap.add_argument('--python', default=sys.executable)
    ap.add_argument('--only', default='')
    a = ap.parse_args()
    if '/' in a.python:
        a.python = os.path.abspath(a.python)
    only = set(filter(None, a.only.split(','))) or None

    with open(a.inventory, newline='') as f:
        rows = [r for r in csv.DictReader(f) if r['type'] == 'verifier']
    rows.sort(key=lambda r: (r['repository'], r['path']))

    fields = ['repo', 'commit', 'path', 'asserts', 'mode', 'command',
              'exit_code', 'class', 'detail', 'seconds', 'output_sha256_16',
              'dirtied_tree']
    out_rows = []
    for r in rows:
        repo_name, path = r['repository'], r['path']
        if only and repo_name not in only:
            continue
        repo = os.path.join(a.repos, repo_name)
        full = os.path.join(repo, path)
        head = subprocess.run(['git', '-C', repo, 'rev-parse', 'HEAD'],
                              capture_output=True, text=True).stdout.strip()
        ext = path.rsplit('.', 1)[-1] if '.' in path.rsplit('/', 1)[-1] else ''
        try:
            text = open(full, errors='replace').read()
        except OSError:
            text = ''
        asserts = len(ASSERT_RE.findall(text)) if ext == 'py' else ''
        has_argparse = 'argparse' in text or 'sys.argv' in text

        def emit(mode, cmd, code, secs, out, dirtied=''):
            cls, detail = (classify(code, out, has_argparse)
                           if secs is not None else (code, out))
            digest = hashlib.sha256(out.encode()).hexdigest()[:16] if out else ''
            out_rows.append({
                'repo': repo_name, 'commit': head, 'path': path,
                'asserts': asserts, 'mode': mode,
                'command': ' '.join(cmd) if cmd else '',
                'exit_code': code if secs is not None else '',
                'class': cls, 'detail': detail,
                'seconds': '' if secs is None else secs,
                'output_sha256_16': digest, 'dirtied_tree': dirtied})
            print(f"{repo_name} {path} {mode} -> {cls} ({code}) {secs}s",
                  file=sys.stderr)

        if ext != 'py':
            emit('documented', [], 'NOT-RUN', None,
                 f'extension .{ext}: no generic runner in O2')
            emit('corrupted', [], 'MANUAL', None, 'per-verifier probe, F2')
            continue

        for mode, cmd, cwd in (
                ('documented', [a.python, path], repo),
                ('optimised', [a.python, '-O', path], repo)):
            code, secs, out = run(cmd, cwd, a.timeout)
            dirty = tree_dirty(repo)
            if dirty == 'yes':
                restore(repo)
            emit(mode, cmd, code, secs, out, dirty)

        with tempfile.TemporaryDirectory() as td:
            cmd = [a.python, os.path.abspath(full)]
            code, secs, out = run(cmd, td, a.timeout)
            emit('empty-cwd', cmd, code, secs, out)

        emit('corrupted', [], 'MANUAL', None, 'per-verifier probe, F2')

    with open(a.out, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)
    print(f'{a.out}: {len(out_rows)} rows', file=sys.stderr)


if __name__ == '__main__':
    main()
