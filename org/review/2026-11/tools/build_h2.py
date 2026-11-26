#!/usr/bin/env python3
"""H2: numbers for the owners' decisions.

Writes open-prs.csv, open-issues.csv, licences.csv and zenodo-credits.csv in
this folder; make_docs.py --h2 writes numbers.md from them.
Sources: the mirrors at the pinned heads and the frozen API answers in
sources/ (repo-list.json, open-prs.json, open-issues-items.json, the Zenodo
records), public repositories only. No live call remains: the licence column
reads licenseInfo from the frozen repo-list.json, and a frozen record file
that is missing stops the run with an error instead of fetching.
"""
import collections
import csv
import json
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(TOOLS)
SOURCES = os.path.join(TOOLS, "sources")
OUT = BASE
os.makedirs(OUT, exist_ok=True)
MIRRORS = os.path.join(TOOLS, "mirrors")

# The GitHub license endpoint's spdx_id for each key in the frozen
# repo-list.json licenseInfo. Verified against the committed licences.csv:
# all 35 rows match. A key of "other" means a licence file GitHub cannot
# place in a known family; the endpoint reports those as NOASSERTION.
# A null licenseInfo means no detectable licence, which the endpoint
# reports as a 404, read as "".
SPDX_BY_KEY = {"apache-2.0": "Apache-2.0", "mit": "MIT", "other": "NOASSERTION"}


def sh(args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False).stdout


def public_repos():
    """The repository list, from the snapshot in sources/.

    `gh repo list Foundation-0 --limit 200 --json name,isPrivate,
    defaultBranchRef,licenseInfo --jq '.[] | select(.isPrivate==false)'`
    produced this file on 15 November. Reading it keeps a rerun offline.
    """
    out = json.load(open(os.path.join(SOURCES, "repo-list.json")))
    return {r["name"]: r for r in out if not r["isPrivate"]}


def main():
    repos = public_repos()
    names = set(repos)

    # ---- open PRs
    prs = json.load(open(os.path.join(SOURCES, "open-prs.json")))
    prs = [p for p in prs if p["repository"]["name"] in names]
    with open(os.path.join(OUT, "open-prs.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["repository", "number", "author", "created_at", "draft", "title"])
        for p in sorted(prs, key=lambda p: (p["repository"]["name"], p["number"])):
            w.writerow([p["repository"]["name"], p["number"], p["author"]["login"],
                        p["createdAt"], p["isDraft"], p["title"]])

    # ---- open issues
    issues = json.load(open(os.path.join(SOURCES, "open-issues-items.json")))
    issues = [i for i in issues
              if i["repository_url"].split("/repos/Foundation-0/")[1] in names]
    with open(os.path.join(OUT, "open-issues.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["repository", "number", "author", "created_at", "title"])
        for i in sorted(issues, key=lambda i: (
                i["repository_url"].split("/repos/Foundation-0/")[1], i["number"])):
            w.writerow([i["repository_url"].split("/repos/Foundation-0/")[1], i["number"],
                        i["user"]["login"], i["created_at"], i["title"]])

    # ---- branches not merged into the default branch
    # branches.csv is built from the frozen snapshot in sources/, so this live
    # scan is only an audit trail. Pass --live to refresh it; it fetches, so it
    # needs the network.
    stranded = []
    for name in sorted(names) if "--live" in sys.argv else []:
        d = os.path.join(MIRRORS, name)
        if not os.path.isdir(d):
            continue
        default = repos[name]["defaultBranchRef"]["name"]
        sh(["git", "fetch", "--quiet", "--all"], d)
        heads = sh(["git", "for-each-ref", "--format=%(refname:short)\t%(objectname)\t%(committerdate:iso-strict)",
                    "refs/remotes/origin/"], d).split("\n")
        for line in heads:
            if not line.strip():
                continue
            ref, sha, date = line.split("\t")
            branch = ref[len("origin/"):]
            if branch in {default, "HEAD"}:
                continue
            if branch.startswith("gh-pages") or branch.startswith("dependabot/"):
                continue
            anc = subprocess.run(
                ["git", "merge-base", "--is-ancestor", sha, f"origin/{default}"],
                cwd=d, capture_output=True)
            if anc.returncode != 0:
                last = sh(["git", "log", "-1", "--format=%cI|%ae|%s", sha], d).strip()
                stranded.append({
                    "repository": name, "branch": branch, "head_sha": sha,
                    "last_commit_date": last.split("|")[0] if last else "",
                    "last_commit_author": last.split("|")[1] if "|" in last else "",
                    "last_commit_subject": last.split("|", 2)[2][:100] if "|" in last else "",
                })
    if stranded:
        # Audit trail only: branches.csv is built from the frozen snapshot in
        # sources/, so its row set does not move under us.
        work = os.path.join(TOOLS, "work")
        os.makedirs(work, exist_ok=True)
        fields = ["repository", "branch", "head_sha", "last_commit_date",
                  "last_commit_author", "last_commit_subject"]
        with open(os.path.join(work, "unmerged-branches-live.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(stranded)
        print("live branch scan", len(stranded), "rows")

    # ---- licences
    lic_rows = []
    for name in sorted(names):
        d = os.path.join(MIRRORS, name)
        files = []
        for root, dirs, fs in os.walk(d):
            dirs[:] = [x for x in dirs if x != ".git"]
            depth = os.path.relpath(root, d).count(os.sep) + (0 if root == d else 1)
            if depth > 1:
                dirs[:] = []
                fs = []
            for fn in fs:
                low = fn.lower()
                if low.startswith("licence") or low.startswith("license") or low == "copying":
                    files.append(os.path.relpath(os.path.join(root, fn), d))
        if "licenseInfo" not in repos[name]:
            sys.exit("sources/repo-list.json has no licenseInfo for %s; "
                     "refresh the frozen snapshot" % name)
        info = repos[name]["licenseInfo"] or {}
        key = info.get("key")
        if key is None:
            gh_license = ""  # the endpoint 404s: no detectable licence
        elif key in SPDX_BY_KEY:
            gh_license = SPDX_BY_KEY[key]
        else:
            sys.exit("sources/repo-list.json: unmapped licenseInfo key %r for %s"
                     % (key, name))
        zen = os.path.join(d, ".zenodo.json")
        zen_license = ""
        if os.path.exists(zen):
            try:
                zen_license = json.load(open(zen)).get("license") or ""
            except Exception:
                zen_license = "PARSE FAIL"
        lic_rows.append({
            "repository": name,
            "license_files": "; ".join(sorted(files)),
            "github_detected_license": gh_license,
            "zenodo_license_field": zen_license,
        })
    with open(os.path.join(OUT, "licences.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lic_rows[0].keys()))
        w.writeheader()
        w.writerows(lic_rows)

    # ---- zenodo credit lines
    records = json.load(open(os.path.join(SOURCES, "zenodo.json")))  # keyword foundation0
    more_ids = ["24146368", "24146382", "24146372", "24146380", "24146384"]
    extra = []
    for rid in more_ids:
        p = os.path.join(SOURCES, f"z-{rid}.json")
        if not os.path.exists(p):
            sys.exit("sources/z-%s.json is missing; refresh the frozen record "
                     "(no live fetch)" % rid)
        extra.append(json.load(open(p)))
    allrec = {r["doi"]: r for r in records + extra}

    credit_rows = []
    for doi, r in sorted(allrec.items(), key=lambda kv: kv[1]["metadata"]["title"]):
        m = r["metadata"]
        desc = m.get("description", "")
        credit = ""
        for sentence in desc.replace("</p>", "\n").split("\n"):
            if "verified by" in sentence.lower() or "directed by" in sentence.lower():
                credit = (" ".join(sentence.replace("<p>", " ").split()))
        related = [x.get("identifier", "") for x in m.get("related_identifiers", [])]
        repo = ""
        for x in related:
            if "github.com/Foundation-0/" in x:
                repo = x.rsplit("/", 1)[-1]
        credit_rows.append({
            "repository": repo, "source": "published record", "title": m["title"],
            "doi": r["doi"], "version": m.get("version") or "",
            "publication_date": m.get("publication_date", ""),
            "license": (m.get("license") or {}).get("id", ""),
            "creators": "; ".join(c.get("name", "") for c in m.get("creators", [])),
            "credit_text": credit,
        })
    # .zenodo.json files in the mirrors
    for name in sorted(names):
        p = os.path.join(MIRRORS, name, ".zenodo.json")
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        desc = d.get("description", "")
        credit = ""
        for sentence in desc.replace("</p>", "\n").split("\n"):
            if "verified by" in sentence.lower() or "directed by" in sentence.lower():
                credit = " ".join(sentence.replace("<p>", " ").split())
        credit_rows.append({
            "repository": name, "source": ".zenodo.json", "title": d.get("title", name),
            "doi": "", "version": d.get("version", ""), "publication_date": "",
            "license": d.get("license", ""),
            "creators": "; ".join(c.get("name", "") for c in d.get("creators", [])),
            "credit_text": credit,
        })
    with open(os.path.join(OUT, "zenodo-credits.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(credit_rows[0].keys()))
        w.writeheader()
        w.writerows(credit_rows)

    # ---- summary numbers
    cut = "2026-11-01T00:00:00Z"
    pr_before = [p for p in prs if p["createdAt"] < cut]
    pr_repos = collections.Counter(p["repository"]["name"] for p in prs)
    iss_repos = collections.Counter(
        i["repository_url"].split("/repos/Foundation-0/")[1] for i in issues)
    lines = []
    lines.append("Public repositories in Foundation-0: %d." % len(names))
    lines.append("")
    lines.append("Open pull requests: %d across %d repositories." % (len(prs), len(pr_repos)))
    lines.append("Open PRs opened before 1 November 2026: %d." % len(pr_before))
    lines.append("Open PRs by account: " + ", ".join(
        "%s %d" % (a, n) for a, n in collections.Counter(
            p["author"]["login"] for p in prs).most_common()) + ".")
    lines.append("Draft PRs: %d." % sum(1 for p in prs if p["isDraft"]))
    lines.append("")
    lines.append("Open issues: %d across %d repositories." % (len(issues), len(iss_repos)))
    lines.append("Open issues opened before 1 November 2026: %d." % sum(
        1 for i in issues if i["created_at"] < cut))
    lines.append("Open issues by account: " + ", ".join(
        "%s %d" % (a, n) for a, n in collections.Counter(
            i["user"]["login"] for i in issues).most_common()) + ".")
    lines.append("")
    lines.append("Branches on public repositories not merged into the default branch "
                 "(gh-pages and dependabot excluded): %d, on %d repositories." % (
                     len(stranded), len({s["repository"] for s in stranded})))
    no_license = [r["repository"] for r in lic_rows
                  if not r["license_files"] and not r["github_detected_license"]]
    lines.append("")
    lines.append("Repositories with no licence file and no GitHub-detected licence: %d (%s)."
                 % (len(no_license), ", ".join(no_license)))
    stated_default = []
    for r in lic_rows:
        if r["license_files"] and not r["github_detected_license"]:
            stated_default.append(r["repository"])
    if stated_default:
        lines.append("Repositories with a licence file GitHub does not detect: %s."
                     % ", ".join(stated_default))
    published = [r for r in credit_rows if r["doi"]]
    lines.append("")
    lines.append("Zenodo records found for the organisation: %d (all version v1.0.0, "
                 "published 2026-11-11)." % len(published))
    files = [r for r in credit_rows if r["source"] == ".zenodo.json"]
    lines.append(".zenodo.json files in the mirrors: %d; %d of them carry the credit line."
                 % (len(files), sum(1 for r in files if r["credit_text"])))
    with_line = [r for r in files if r["credit_text"]]
    without = [r["repository"] for r in files if not r["credit_text"]]
    lines.append("Files without the credit line: %s." % ", ".join(without))
    lines.append("")
    lines.append("## Repositories without a licence")
    lines.append("")
    no_lic = [r for r in lic_rows
              if not r["license_files"] and not r["github_detected_license"]]
    for r in no_lic:
        lines.append("- %s" % r["repository"])
    lines.append("")
    lines.append("License files GitHub does not identify (NOASSERTION): %s." % ", ".join(
        r["repository"] for r in lic_rows if r["github_detected_license"] == "NOASSERTION"))
    lines.append("Repositories whose detected licence is not Apache-2.0: %s." % ", ".join(
        "%s (%s)" % (r["repository"], r["github_detected_license"])
        for r in lic_rows
        if r["github_detected_license"] not in ("", "Apache-2.0", "NOASSERTION")))
    # The summary goes to stdout only; make_docs.py --h2 writes numbers.md, so
    # running this script alone does not clobber the narrative.
    print("\n".join(lines))


if __name__ == "__main__":
    main()
