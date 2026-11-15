#!/usr/bin/env python3
"""W2: one row per statement on the f0 site.

Reads the site files in this checkout and the frozen snapshot in
site-sources.json, then writes org/review/2026-11/site-inventory.csv.

    python3 tools/build_site_inventory.py            # offline, reproducible
    python3 tools/build_site_inventory.py --refresh-sources   # network, refresh snapshot

Columns: page, line, kind, statement, what_is_true_now, source, now_source,
mark, note. [F] is a fact read from a repository or a run; [I] is an inference
or a statement left for W3 to check. Nothing here judges a scientific claim.
"""
import csv
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEW = os.path.dirname(HERE)                       # org/review/2026-11
REPO = os.path.dirname(os.path.dirname(os.path.dirname(REVIEW)))  # repo root
SNAPSHOT = os.path.join(REVIEW, "site-sources.json")
OUT = os.path.join(REVIEW, "site-inventory.csv")
F0_SHA = "6ea3a0b3d18fa1e7cf1845e3dc67220a35781948"
GH_SHA = "81f83c38918382b4ca142b81debd3cc5ccf61d3a"

# Data files whose records are datasets, not site statements: they contribute a
# date row and a count row, but their thousands of PR URLs are not site links.
DATASETS = [
    "docs/feed.json", "docs/chart-data.json", "docs/data/ledger.json",
    "docs/legacy-site/feed.json", "docs/legacy-site/chart-data.json",
    "docs/research/exoplanets/candidates.json",
    "docs/research/exoplanets/lightcurves.json",
    "docs/research/exoplanets/transits.json",
    "docs/research/integer-multiplication/kappa-history.json",
    "docs/research/machine-mathematics/openai-subjects.json",
    "docs/research/maxwell-charges/equilibria.json",
    "docs/research/gf2m-circuits/circuits.js",
    "docs/writing/annotations.json",
    "docs/charter/futures.json",
]
STRUCTURED = [
    "docs/data/projects.json", "docs/data/members.json", "docs/data/writing.json",
    "docs/data/discussions.json",
]
DATASETS += [
    "docs/data/openai-math-families.json", "docs/data/ledger.schema.json",
    "docs/feed.schema.json", "feed.schema.json",
]
ROOT_MD = ["README.md", "JOIN.md", "CONTRIBUTING.md", "FORUM.md", "MERGE-SOP.md"]

DATE_RE = re.compile(
    r"(?:\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+20\d{2}\b"
    r"|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+20\d{2}\b"
    r"|\b20\d{2}-\d{2}-\d{2}(?:T[\d:.]+Z)?\b)")
NUM_RE = re.compile(r"\b\d[\d,.]*\s*(?:%|percent)?\b")
GH_RE = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")
URL_RE = re.compile(r"https?://[^\s\"`'<>)\]}]+")
HREF_RE = re.compile(r'(?:href|src|action)\s*=\s*["\']([^"\']+)["\']')
STATUS_RE = re.compile(
    r"\b(private preview|not started|in design|not peer reviewed|live tracker|"
    r"live demo|released software|open-source software|preprint|founding member|"
    r"disabled|enabled|not confirmed|not reviewed|not clinically validated|"
    r"no verdicts yet|no results yet|seed|published|merged|active)\b", re.I)
FOUR = ("rohanarun", "rohan arun", "doug colkitt", "ryan shea", "eumemic",
        "Mister-Meeseeks", "shea256")


def lines_of(path):
    with open(os.path.join(REPO, path), encoding="utf-8", errors="replace") as fh:
        return fh.read().split("\n")


def snippet(line, match=None, width=100):
    text = " ".join(line.split())
    if match:
        a = max(0, match.start() - width // 2)
        b = min(len(text), match.end() + width // 2)
        text = text[a:b]
    return text[:240]


def pin(page, line, repo="Foundation-0/f0", sha=F0_SHA):
    return "%s@%s:%s:%s" % (repo, sha, page, line)


def now_pin(page, repo="Foundation-0/f0", sha=F0_SHA):
    return "%s@%s:%s:1" % (repo, sha, page)


def site_files():
    out = []
    for root, dirs, files in os.walk(os.path.join(REPO, "docs")):
        dirs[:] = [d for d in dirs if d != ".git"]
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), REPO)
            if fn.endswith((".html", ".js", ".json", ".md")):
                out.append(rel)
    out += [f for f in ROOT_MD if os.path.exists(os.path.join(REPO, f))]
    return sorted(out)


def emit(rows, page, line_no, kind, statement, now, source, now_source, mark, note=""):
    rows.append({
        "page": page, "line": line_no, "kind": kind, "statement": statement,
        "what_is_true_now": now, "source": source, "now_source": now_source,
        "mark": mark, "note": note,
    })


def data_rows(rows, snap):
    files = snap["files"]
    for path in DATASETS + STRUCTURED:
        if not os.path.exists(os.path.join(REPO, path)):
            continue
        text_lines = lines_of(path)
        last = files.get(path, {}).get("date", "unknown")
        # date field
        for n, line in enumerate(text_lines[:12], 1):
            m = re.search(r'"(updated|generated_at|date|feed_version)"\s*:\s*"([^"]+)"', line)
            if m:
                if path == "docs/feed.json":
                    now = ("No newer feed exists at %s. The owner says update.yml has been "
                           "disabled since, so the live tracker serves this 11 Oct feed."
                           % F0_SHA[:7])
                    note = "Data date and the owner's disable statement; W3 refreshes the feed."
                else:
                    now = ("The site still carries this field at %s. The file was last "
                           "committed on %s, so no refresh has landed." % (F0_SHA[:7], last))
                    note = "Data date; W3 refreshes the site data."
                emit(rows, path, n, "date", snippet(line, m), now,
                     pin(path, n), now_pin(path), "[F]", note)
                break
        # count of top-level records
        try:
            obj = json.loads("\n".join(text_lines))
        except Exception:
            continue
        counts = []
        for key in ("projects", "members", "milestones", "quarantined", "claimed",
                    "posts", "threads", "categories", "fields", "entries", "records",
                    "candidates", "rows"):
            if isinstance(obj, dict) and isinstance(obj.get(key), list):
                counts.append("%s %d" % (key, len(obj[key])))
        if isinstance(obj, dict) and isinstance(obj.get("projects"), list):
            ks = [p for p in obj["projects"] if p.get("kind") == "repository"]
            counts.append("projects of kind repository %d" % len(ks))
        if isinstance(obj, dict) and "total" in obj:
            counts.append("total %s" % obj["total"])
        if counts:
            if path == "docs/data/projects.json":
                now = ("Recomputed from the file at %s: %s. A live read on 15 November "
                       "finds 35 public repositories (34 excluding .github), so 19 of the "
                       "35 are not listed here, or 18 of the 34. W3 adds them."
                       % (F0_SHA[:7], "; ".join(counts)))
                note = "The site comment says 34; that count excludes .github."
            else:
                now = "Recomputed from the file at %s: %s." % (F0_SHA[:7], "; ".join(counts))
                note = "Counts in the site's own data, not a judgment on the content."
            emit(rows, path, 1, "count", "; ".join(counts), now,
                 pin(path, 1), now_pin(path), "[F]", note)
        # status strings in structured data
        if path in STRUCTURED:
            for n, line in enumerate(text_lines, 1):
                m = re.search(r'"status"\s*:\s*"([^"]+)"', line)
                if not m:
                    continue
                status = m.group(1)
                emit(rows, path, n, "status", status,
                     "Still the value in the pinned data. W3 checks it against the repository at its pinned head.",
                     pin(path, n), now_pin(path), "[I]",
                     "Project status; a content check belongs to W3.")
                if "private preview" in status.lower():
                    emit(rows, path, n, "status", status,
                         "No public repository named Exo or Exo OS is in the 35 public repositories read on 15 November, and these entries carry no repository URL.",
                         pin(path, n), "Foundation-0/.github@%s:profile/README.md:1" % GH_SHA,
                         "[F]", "Statuses to check, from the site comment.")


def page_rows(rows, snap, files):
    public = set(snap["public_repos"])
    profile = snap.get("profile_text", "")
    for path in files:
        if path in DATASETS or path in STRUCTURED:
            continue
        text_lines = lines_of(path)
        last = snap["files"].get(path, {}).get("date", "unknown")
        seen_links = set()
        for n, line in enumerate(text_lines, 1):
            if len(line) > 4000:
                continue
            src = pin(path, n)
            for m in DATE_RE.finditer(line):
                emit(rows, path, n, "date", snippet(line, m),
                     "The site still shows this date at %s. The file was last committed on %s."
                     % (F0_SHA[:7], last),
                     src, now_pin(path), "[F]",
                     "Date as written on the page; W3 refreshes it if the data moves.")
                break
            for m in STATUS_RE.finditer(line):
                word = m.group(0)
                low = word.lower()
                if low in ("disabled", "enabled", "live tracker"):
                    now = ("update.yml is disabled, so the live tracker serves the 11 Oct feed."
                           if low in ("disabled", "live tracker") else
                           "The forum data still reports enabled: false at 6ea3a0b.")
                    ns = now_pin(".github/workflows/update.yml")
                elif low == "founding member":
                    now = "Four of the five named founding members never joined; W1 removes them as members and keeps their names only as credit for their own work."
                    ns = now_pin("README.md")
                elif low == "private preview":
                    now = "No public repository named Exo or Exo OS is in the 35 public repositories read on 15 November."
                    ns = "run: gh repo list Foundation-0 --limit 200 --json name,isPrivate (site-sources.json)"
                else:
                    now = "Still the wording in the pinned site file. W3 checks the underlying state."
                    ns = now_pin(path)
                emit(rows, path, n, "status", snippet(line, m), now, src, ns,
                     "[F]" if low in ("disabled", "enabled", "live tracker",
                                      "founding member", "private preview") else "[I]",
                     "Status wording, not a judgment on the work.")
                break
            if re.search(r"https?://|\bhref=|\burl\b|\bsrc=", line, re.I):
                pass
            else:
                m = re.search(r"\b\d[\d,.]{1,}\s*(?:%|percent)?\b", line)
                if m and re.search(
                        r"\b(candidates|papers|repositories|members|stars|commits|entries|"
                        r"rows|tests|records|projects|percent|percentages|threads|issues|"
                        r"pull requests|days|weeks|months|years)\b",
                        line[max(0, m.start() - 70):m.end() + 70], re.I):
                    emit(rows, path, n, "count", snippet(line, m),
                         "Recorded from the pinned page. Research counts are re-checked by Fable, not here.",
                         src, now_pin(path), "[I]",
                         "A number the site states; W3 uses it to decide what to refresh.")
            for m in GH_RE.finditer(line):
                owner, name = m.group(1), m.group(2).rstrip(".,")
                key = (owner, name)
                if (path, key) in seen_links:
                    continue
                seen_links.add((path, key))
                if owner.lower() == "foundation-0":
                    now = ("Public repository, present in the 35 public repositories read on 15 November."
                           if name in public else
                           "No public Foundation-0 repository by that name in the 35 public repositories read on 15 November.")
                    note = "Named by the site; W3 keeps the project list in step."
                else:
                    now = "Repository outside Foundation-0. Its links are checked in the link rows."
                    note = "Outside project, credited by name on the page."
                emit(rows, path, n, "repository", "%s/%s" % (owner, name), now,
                     src, "run: gh repo list Foundation-0 --limit 200 --json name,isPrivate (site-sources.json)", "[F]", note)
            for m in HREF_RE.finditer(line) if path.endswith(".html") else []:
                target = m.group(1)
                add_link(rows, snap, path, n, target, seen_links, src)
            for m in URL_RE.finditer(line) if not path.endswith(".html") else []:
                add_link(rows, snap, path, n, m.group(0), seen_links, src)
    # org profile, read from the snapshot so a fresh clone of f0 is enough
    for n, line in enumerate(profile.split("\n"), 1):
        src = "Foundation-0/.github@%s:profile/README.md:%d" % (GH_SHA, n)
        for m in GH_RE.finditer(line):
            owner, name = m.group(1), m.group(2).rstrip(".,")
            now = ("Public repository, present in the 35 public repositories read on 15 November."
                   if owner == "Foundation-0" and name in set(snap["public_repos"]) else
                   "Private repository named in the organisation profile; not in the 35 public repositories.")
            emit(rows, "Foundation-0/.github:profile/README.md", n, "repository",
                 "%s/%s" % (owner, name), now, src,
                 "run: gh repo list Foundation-0 --limit 200 --json name,isPrivate (site-sources.json)", "[F]",
                 "The organisation profile is out of reach for a cloud session; an owner changes it.")
        if "admin on all repos" in line or "core" in line and "admin" in line:
            emit(rows, "Foundation-0/.github:profile/README.md", n, "status",
                 snippet(line), "REPO-PROTECTION section 2 gives agents Write only; the owners decide the correction.",
                 src, src, "[F]",
                 "Flagged in the site comment as a statement an owner must change.")
        if "founding member" in line.lower():
            emit(rows, "Foundation-0/.github:profile/README.md", n, "member",
                 snippet(line), "The four who never joined are removed as members by W1; this profile needs an owner to change it.",
                 src, src, "[F]",
                 "A cloud session cannot write to Foundation-0/.github.")
        for m in URL_RE.finditer(line):
            add_link(rows, snap, "Foundation-0/.github:profile/README.md", n,
                     m.group(0), set(), src)


def add_link(rows, snap, path, n, target, seen, src):
    target = target.strip().rstrip(".,;:")
    if (not target or target.startswith(("#", "mailto:", "javascript:", "data:"))
            or "${" in target or "{{" in target or target.endswith("`")):
        return
    key = (path, target)
    if key in seen:
        return
    seen.add(key)
    url = target
    if target.startswith("/") and not target.startswith("//"):
        rel = "docs" + target.split("#")[0].split("?")[0]
        if rel.endswith("/"):
            rel += "index.html"
        if os.path.exists(os.path.join(REPO, rel)):
            emit(rows, path, n, "link", target,
                 "Internal link resolves to %s at %s." % (rel, F0_SHA[:7]),
                 src, now_pin(rel), "[F]", "Checked against the pinned checkout.")
            return
        url = "https://fdn0.org" + target
    elif target.startswith("../") or target.startswith("./") or not re.match(r"^[a-z]+:", target):
        base = os.path.dirname(path)
        resolved = os.path.normpath(os.path.join(base, target.split("#")[0].split("?")[0]))
        if os.path.exists(os.path.join(REPO, resolved)):
            emit(rows, path, n, "link", target,
                 "Internal link resolves to %s at %s." % (resolved, F0_SHA[:7]),
                 src, now_pin(resolved), "[F]", "Checked against the pinned checkout.")
            return
        if "." in os.path.basename(resolved):
            emit(rows, path, n, "link", target,
                 "No file at %s in the pinned checkout." % resolved,
                 src, now_pin(resolved), "[F]", "Broken at 6ea3a0b; W3 fixes it.")
            return
        url = "https://fdn0.org/" + resolved
    prefix = url.rstrip("/").count("/") == 2 or url.endswith("/")
    rec = snap["links"].get(url, {})
    status = rec.get("status")
    if status is None:
        now = "External link, not checked in the frozen snapshot."
        mark, note = "[I]", "Not in the 15 November link check; W3 checks it."
    elif status == 0:
        now = "No response within the check timeout."
        mark, note = "[I]", "Network check timed out; retry before W3 uses it."
    elif prefix and status >= 400:
        now = "HTTP %s on the bare URL prefix; the page appends a path at render time." % status
        mark, note = "[I]", "A URL prefix in a template, not a broken link on its own."
    else:
        now = "HTTP %s%s" % (status, " (redirected to %s)" % rec["final"] if rec.get("final") and rec["final"] != url else "")
        mark, note = "[F]", "HTTP status read on 15 November; rerun --refresh-sources to update."
    emit(rows, path, n, "link", url, now, src,
         "run: curl -sIL (site-sources.json:links)", mark, note)


def refresh_sources(snap, files):
    """Refresh the frozen snapshot: repo list, file dates, link statuses."""
    snap["public_repos"] = sorted(json.loads(subprocess.run(
        ["gh", "repo", "list", "Foundation-0", "--limit", "200", "--json", "name,isPrivate",
         "--jq", "[.[] | select(.isPrivate == false) | .name]"],
        capture_output=True, text=True, check=True).stdout))
    for path in files + DATASETS:
        r = subprocess.run(["git", "log", "-1", "--format=%H|%cI", F0_SHA, "--", path],
                           cwd=REPO, capture_output=True, text=True)
        sha, _, date = r.stdout.strip().partition("|")
        snap["files"][path] = {"last_commit": sha, "date": date or "unknown"}
    urls = set()
    for path in files:
        if path in DATASETS:
            continue
        for line in lines_of(path):
            if len(line) > 4000:
                continue
            for m in URL_RE.finditer(line):
                urls.add(m.group(0).rstrip(".,;:"))
            for m in HREF_RE.finditer(line) if path.endswith(".html") else []:
                t = m.group(1)
                if t.startswith("http"):
                    urls.add(t.rstrip(".,;:"))
    for line in snap.get("profile_text", "").split("\n"):
        for m in URL_RE.finditer(line):
            urls.add(m.group(0).rstrip(".,;:"))

    def one(url):
        # curl uses the machine's CA bundle; urllib does not on this host.
        try:
            out = subprocess.run(
                ["curl", "-sIL", "-o", "/dev/null", "--max-time", "12",
                 "-w", "%{http_code}\t%{url_effective}", url],
                capture_output=True, text=True, timeout=20).stdout.strip()
            code, _, final = out.partition("\t")
            return url, {"status": int(code) if code.isdigit() else 0, "final": final}
        except Exception:
            return url, {"status": 0, "final": ""}

    with ThreadPoolExecutor(max_workers=16) as pool:
        for u, rec in pool.map(one, sorted(urls)):
            snap["links"][u] = rec
    snap["link_count"] = len(urls)


def main():
    files = site_files()
    snap = json.load(open(SNAPSHOT)) if os.path.exists(SNAPSHOT) else {
        "public_repos": [], "files": {}, "links": {}, "profile_text": ""}
    if "--refresh-sources" in sys.argv:
        refresh_sources(snap, files)
        with open(SNAPSHOT, "w") as fh:
            json.dump(snap, fh, indent=1, sort_keys=True)
        print("refreshed", len(snap["public_repos"]), "repos and", snap["link_count"], "links")
    rows = []
    data_rows(rows, snap)
    page_rows(rows, snap, files)
    seen_rows = set()
    unique = []
    for r in rows:
        key = (r["page"], r["kind"], r["statement"])
        if key in seen_rows:
            continue
        seen_rows.add(key)
        unique.append(r)
    rows = unique
    rows.sort(key=lambda r: (r["page"], int(r["line"]), r["kind"], r["statement"]))
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "page", "line", "kind", "statement", "what_is_true_now", "source",
            "now_source", "mark", "note"])
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print("rows", len(rows), Counter(r["kind"] for r in rows))
    return rows


if __name__ == "__main__":
    main()
