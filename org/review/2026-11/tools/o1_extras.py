#!/usr/bin/env python3
"""O1 extra checks that scripts/org/scan (draft 40) does not do.

Inputs: blobless mirrors from scan/mirror_org.sh, the TSV lists from
scan/list_prs.sh, H1 inventory.csv and H2 branches.csv (paths as args).

Outputs (CSV, in --out dir):
  o1-branches.csv    every non-default branch: ahead count, test-merge
                     state, content_on_default (yes when the test merge
                     tree equals the default branch tree)
  o1-pr-merge.csv    every open PR: head, test-merge state, file count
  o1-pr-overlaps.csv files touched by more than one open PR, per repo
  o1-copies.csv      identical research-file blobs in more than one repo
  o1-samepath.csv    same path in more than one repo, different blobs

Read-only. Standard library only. Blobless mirrors fetch missing
objects on demand, so the first run needs the network.

Usage:
  python3 o1_extras.py --mirrors DIR --lists DIR --inventory FILE \
      --h2-branches FILE --out DIR [--only repo,repo]
"""
import argparse
import csv
import collections
import os
import subprocess
import sys

GIT_TIMEOUT = 180


def git(repo, *args):
    p = subprocess.run(['git', '-C', repo, *args], capture_output=True,
                       text=True, errors='replace', timeout=GIT_TIMEOUT)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def default_ref(repo):
    code, out, _ = git(repo, 'symbolic-ref', 'HEAD')
    if code == 0 and out:
        return out  # refs/heads/main in a mirror
    for guess in ('refs/heads/main', 'refs/heads/master'):
        code, _, _ = git(repo, 'rev-parse', '--verify', guess)
        if code == 0:
            return guess
    return None


def tree_of(repo, ref):
    code, out, _ = git(repo, 'rev-parse', f'{ref}^{{tree}}')
    return out if code == 0 else ''


def merge_state(repo, base, head, base_tree):
    """Return (state, content_on_default). state: clean|conflict|error."""
    code, out, err = git(repo, 'merge-tree', '--write-tree', base, head)
    if code == 0:
        tree = out.splitlines()[0] if out else ''
        return 'clean', 'yes' if tree == base_tree else 'no'
    if code == 1:
        return 'conflict', 'no'
    return 'error', 'unknown'


def branch_rows(mirrors, only, open_pr_branches):
    rows = []
    for d in sorted(os.listdir(mirrors)):
        if not d.endswith('.git'):
            continue
        name = d[:-4]
        if only and name not in only:
            continue
        repo = os.path.join(mirrors, d)
        base = default_ref(repo)
        if not base:
            continue
        base_tree = tree_of(repo, base)
        _, refs, _ = git(repo, 'for-each-ref',
                         '--format=%(refname) %(objectname)', 'refs/heads')
        for line in refs.splitlines():
            ref, sha = line.split()
            if ref == base:
                continue
            branch = ref[len('refs/heads/'):]
            _, ahead, _ = git(repo, 'rev-list', '--count', f'{base}..{ref}')
            _, when, _ = git(repo, 'log', '-1', '--format=%cI', ref)
            state, on_default = merge_state(repo, base, ref, base_tree)
            rows.append({
                'repository': name, 'branch': branch, 'head_sha': sha,
                'commits_ahead': ahead, 'last_commit_date': when,
                'test_merge': state, 'content_on_default': on_default,
                'open_pr': open_pr_branches.get((name, branch), ''),
            })
            print(f'branch {name} {branch} {state} on_default={on_default}',
                  file=sys.stderr)
    return rows


def pr_rows(mirrors, lists, only):
    rows, overlaps = [], []
    open_tsv = os.path.join(lists, 'open.tsv')
    per_repo_files = collections.defaultdict(lambda: collections.defaultdict(list))
    with open(open_tsv, newline='') as f:
        for parts in csv.reader(f, delimiter='\t'):
            if len(parts) < 2:
                continue
            name, number = parts[0], parts[1]
            if only and name not in only:
                continue
            repo = os.path.join(mirrors, f'{name}.git')
            if not os.path.isdir(repo):
                rows.append({'repository': name, 'number': number,
                             'head_sha': '', 'test_merge': 'no-mirror',
                             'changed_files': ''})
                continue
            base = default_ref(repo)
            head_ref = f'refs/pull/{number}/head'
            code, sha, _ = git(repo, 'rev-parse', '--verify', head_ref)
            if code != 0:
                rows.append({'repository': name, 'number': number,
                             'head_sha': '', 'test_merge': 'no-head-ref',
                             'changed_files': ''})
                continue
            base_tree = tree_of(repo, base)
            state, _ = merge_state(repo, base, head_ref, base_tree)
            _, mb, _ = git(repo, 'merge-base', base, head_ref)
            _, files, _ = git(repo, 'diff', '--name-only', f'{mb}..{head_ref}')
            flist = [x for x in files.splitlines() if x]
            for path in flist:
                per_repo_files[name][path].append(number)
            rows.append({'repository': name, 'number': number,
                         'head_sha': sha, 'test_merge': state,
                         'changed_files': len(flist)})
            print(f'pr {name}#{number} {state} files={len(flist)}',
                  file=sys.stderr)
    for name in sorted(per_repo_files):
        for path in sorted(per_repo_files[name]):
            prs = per_repo_files[name][path]
            if len(prs) > 1:
                overlaps.append({'repository': name, 'path': path,
                                 'open_prs': ' '.join(prs),
                                 'pr_count': len(prs)})
    return rows, overlaps


def copy_rows(inventory_path):
    with open(inventory_path, newline='') as f:
        inv = list(csv.DictReader(f))
    by_blob = collections.defaultdict(list)
    by_path = collections.defaultdict(list)
    for r in inv:
        by_blob[r['blob_sha']].append(r)
        by_path[r['path']].append(r)
    copies, samepath = [], []
    for blob, rs in sorted(by_blob.items()):
        repos = sorted(set(x['repository'] for x in rs))
        if len(repos) > 1:
            newest = max(rs, key=lambda x: x['last_commit_date'])
            copies.append({
                'blob_sha': blob, 'repos': ' '.join(repos),
                'paths': ' | '.join(sorted(set(x['path'] for x in rs))),
                'newest_repo': newest['repository'],
                'newest_date': newest['last_commit_date']})
    for path, rs in sorted(by_path.items()):
        repos = sorted(set(x['repository'] for x in rs))
        blobs = sorted(set(x['blob_sha'] for x in rs))
        if len(repos) > 1 and len(blobs) > 1:
            newest = max(rs, key=lambda x: x['last_commit_date'])
            samepath.append({
                'path': path, 'repos': ' '.join(repos),
                'distinct_blobs': len(blobs),
                'newest_repo': newest['repository'],
                'newest_date': newest['last_commit_date']})
    return copies, samepath


def write_csv(path, rows, fields):
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f'{path}: {len(rows)} rows', file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mirrors', required=True)
    ap.add_argument('--lists', required=True)
    ap.add_argument('--inventory', required=True)
    ap.add_argument('--h2-branches', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--only', default='')
    a = ap.parse_args()
    only = set(filter(None, a.only.split(','))) or None
    os.makedirs(a.out, exist_ok=True)

    open_pr_branches = {}
    with open(a.h2_branches, newline='') as f:
        for r in csv.DictReader(f):
            if r.get('open_pr'):
                open_pr_branches[(r['repository'], r['branch'])] = r['open_pr']

    write_csv(os.path.join(a.out, 'o1-branches.csv'),
              branch_rows(a.mirrors, only, open_pr_branches),
              ['repository', 'branch', 'head_sha', 'commits_ahead',
               'last_commit_date', 'test_merge', 'content_on_default',
               'open_pr'])
    prs, overlaps = pr_rows(a.mirrors, a.lists, only)
    write_csv(os.path.join(a.out, 'o1-pr-merge.csv'), prs,
              ['repository', 'number', 'head_sha', 'test_merge',
               'changed_files'])
    write_csv(os.path.join(a.out, 'o1-pr-overlaps.csv'), overlaps,
              ['repository', 'path', 'open_prs', 'pr_count'])
    copies, samepath = copy_rows(a.inventory)
    write_csv(os.path.join(a.out, 'o1-copies.csv'), copies,
              ['blob_sha', 'repos', 'paths', 'newest_repo', 'newest_date'])
    write_csv(os.path.join(a.out, 'o1-samepath.csv'), samepath,
              ['path', 'repos', 'distinct_blobs', 'newest_repo',
               'newest_date'])


if __name__ == '__main__':
    main()
