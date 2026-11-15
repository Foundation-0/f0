#!/usr/bin/env python3
"""Classify unmerged branches: head of an open PR, or stranded.

Writes out/h2/branches.csv and prints a summary.
"""
import csv
import json
import os
import subprocess

TOOLS = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(TOOLS)
SOURCES = os.path.join(TOOLS, "sources")
OUT = BASE
MIRRORS = os.path.join(TOOLS, "mirrors")


def sh(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True).stdout


def content_on_default(repo, sha):
    """yes when merging this head into the default branch changes nothing.

    The test is merge-tree: if the merged tree is the default branch's own tree,
    the branch holds no content that is not already there.
    """
    d = os.path.join(MIRRORS, repo)
    head = sh(["git", "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"], d).strip()
    default = head.split("/")[-1] if head else "main"
    base = sh(["git", "rev-parse", "origin/%s^{tree}" % default], d).strip()
    res = subprocess.run(["git", "merge-tree", "--write-tree", "origin/" + default, sha],
                         cwd=d, capture_output=True, text=True)
    tree = res.stdout.split("\n")[0].strip()
    return "yes" if base and tree == base else "no"


def open_pr_heads():
    """Map (repository, branch name) -> PR number, from the snapshot in sources/.

    A branch is matched by name, not by commit. An open PR can gain commits after
    the branch snapshot was taken (f0 review/o1-o2-f0 did), and the head that
    GitHub reports is the current one; the name is what identifies the branch.
    """
    path = os.path.join(SOURCES, "pr-heads.json")
    data = json.load(open(path))
    return {tuple(k.split("|", 1)): v["number"] for k, v in data.items()}


def main():
    heads = open_pr_heads()
    rows = list(csv.DictReader(open(os.path.join(SOURCES, "unmerged-branches.csv"))))
    for r in rows:
        n = heads.get((r["repository"], r["branch"]))
        r["open_pr"] = str(n) if n else ""
        r["state"] = "open-pr" if n else "stranded"
        r["content_on_default"] = content_on_default(r["repository"], r["head_sha"])
    with open(os.path.join(OUT, "branches.csv"), "w", newline="") as f:
        fields = ["repository", "branch", "head_sha", "last_commit_date",
                  "last_commit_author", "last_commit_subject", "open_pr", "state",
                  "content_on_default"]
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    print("branches", len(rows), Counter(r["state"] for r in rows))
    print("content already on default", Counter(r["content_on_default"] for r in rows))
    stranded = [r for r in rows if r["state"] == "stranded"]
    print("stranded by repo", Counter(r["repository"] for r in stranded).most_common())
    recent = [r for r in stranded if r["last_commit_date"] >= "2026-11-01"]
    print("stranded touched since 2026-11-01", len(recent))
    for r in sorted(recent, key=lambda r: r["last_commit_date"], reverse=True):
        print(r["repository"], r["branch"], r["last_commit_date"][:10], r["last_commit_subject"][:70])


if __name__ == "__main__":
    main()
