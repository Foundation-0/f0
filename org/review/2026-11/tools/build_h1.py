#!/usr/bin/env python3
"""H1 inventory for Foundation-0 public repositories.

Reads the mirrors cloned by clone-all.sh and writes:
  out/inventory.csv      one row per research file
  out/claims-index.csv   every claim ID found in a claims register
  out/checks-census.csv  per-repository check counts

No judgments: classification and counts only.
"""
import csv
import json
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(TOOLS)
SOURCES = os.path.join(TOOLS, "sources")
MIRRORS = os.path.join(TOOLS, "mirrors")
OUT = BASE
os.makedirs(OUT, exist_ok=True)

INVENTORY_TYPES = [
    "claims", "paper", "monograph", "note", "readme", "lean",
    "verifier", "certificate", "dataset", "zenodo",
]

LEAN_EXT = {".lean"}
PAPER_EXT = {".tex", ".bib", ".pdf", ".md"}
DATA_EXT = {".csv", ".tsv", ".npz", ".npy", ".json", ".mrt", ".dat", ".h5"}
CODE_EXT = {".py", ".r", ".c", ".cpp", ".cc", ".js", ".mjs", ".sh", ".rb", ".jl"}

EXCLUDE_DIR_PARTS = {
    ".github", ".git", "node_modules", "vendor", "assets", "docs/assets",
    "docs/img", "results/figures", "png", "figures", "visualizations/source",
}

EXCLUDE_BASENAMES = {
    ".gitignore", ".gitattributes", "package.json", "package-lock.json",
    "pyproject.toml", "requirements.txt", "requirements-dev.txt",
    "lakefile.toml", "lean-toolchain", "lake-manifest.json",
    "CITATION.cff", "CONTRIBUTING.md", "NOTICE.md", "NOTICE", "CONTRIBUTORS.md",
    "AGENTS.md", "CLAUDE.md", "lakefile.lean",
    "LICENSE", "LICENSE-CODE", "LICENSE-TEXT.md", "LICENSE-CC-BY-4.0",
    "LICENSE-DOCS", "SECURITY.md", "codex.css", "codex.js", "page.css", "page.js",
}

FIGURE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico"}
SITE_EXT = {".html", ".css", ".js", ".mjs"}

VERIFIER_TOKENS = (
    "verif", "check", "audit", "probe", "replay", "validat", "independent",
    "recompute", "attest", "confirm", "gates", "equivalence", "vet", "gate",
)


def is_verifier(path, base):
    if base.endswith("_test.py") or base.startswith("test_"):
        return False
    if base.startswith("test"):
        return False
    if not path.split("/")[-1].count("."):
        return False
    low = base.lower()
    return any(t in low for t in VERIFIER_TOKENS)


def sh(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)


def repo_meta(repo):
    d = os.path.join(MIRRORS, repo)
    head = sh(["git", "rev-parse", "HEAD"], d).stdout.strip()
    # files with blob sha and size
    tree = sh(["git", "ls-tree", "-r", "-l", "-z", "HEAD"], d).stdout
    files = []
    for entry in tree.split("\0"):
        if not entry:
            continue
        meta, path = entry.split("\t", 1)
        mode, typ, sha, size = meta.split()
        files.append((path, sha, int(size)))
    # last commit per path, newest first
    log = sh(
        ["git", "log", "--pretty=format:%H\x1f%cI\x1f%s\x1f", "--name-only", "HEAD"],
        d,
    ).stdout
    last = {}
    commit = None
    for line in log.split("\n"):
        if "\x1f" in line:
            parts = line.split("\x1f")
            commit = (parts[0], parts[1], parts[2] if len(parts) > 2 else "")
        elif line.strip() and commit:
            p = line.strip()
            if p not in last:
                last[p] = commit
    return head, files, last


def classify(path):
    parts = path.split("/")
    base = parts[-1]
    lower = base.lower()
    ext = os.path.splitext(base)[1].lower()

    if base == ".zenodo.json":
        return "zenodo"
    if lower in {"claims.md", "claims-ledger.json", "claim_map.json", "claims.csv"} or (
        re.search(r"(^|[-_])claims?([-_.]|$)", lower) and ext in {".md", ".json", ".csv"}
    ):
        return "claims"
    if ext == ".lean":
        return "lean"
    if parts[0] == "monographs":
        if lower == "sha256sums":
            return "certificate"
        if re.match(r"^fig", lower):
            return None
        return "monograph"
    if parts[0] in {"papers", "paper"}:
        if ext in PAPER_EXT or lower in {"readme.md"}:
            return "paper"
    if lower in {"manuscript.md", "main.tex"} or (
        ext == ".tex" and not path.startswith("docs/")
    ):
        return "paper"
    if lower in {"sha256sums", "sha256sum"} or lower == "root" or "certificate" in lower:
        if ext in {".json", "", ".txt", ".sha256"} or lower == "root":
            return "certificate"
    if lower.endswith(".cert.json") or lower == "cert.json":
        return "certificate"
    if ext in CODE_EXT and is_verifier(path, base):
        return "verifier"
    if base == "README.md":
        return "readme"
    if ext in DATA_EXT and parts[0] in {
        "data", "results", "inputs", "snapshots", "snapshot", "registries",
        "certificates", "certificate", "commitment", "census",
    }:
        return "dataset"
    if ext in DATA_EXT and any(
        p in {"data", "results", "inputs", "snapshot", "snapshots", "registries",
              "certificates", "census", "cod", "certificates"}
        for p in parts[:-1]
    ):
        return "dataset"
    if ext in {".md", ".txt", ".rst"}:
        return "note"
    return None


def excluded(path):
    parts = path.split("/")
    if any(p in EXCLUDE_DIR_PARTS for p in parts[:-1]):
        return True
    joined = "/".join(parts)
    if any(joined.startswith(x + "/") or joined == x for x in (
        "docs/assets", "docs/img", "results/figures", "assets/vendor",
        "docs/legacy-site", "visualizations/source",
    )):
        return True
    base = parts[-1]
    if base in EXCLUDE_BASENAMES:
        return True
    ext = os.path.splitext(base)[1].lower()
    if ext in FIGURE_EXT:
        return True
    if ext in {".html", ".css"} and not base.startswith("README"):
        return True
    if base.endswith(".cjs"):
        return True
    return False


def build_inventory():
    rows = []
    repos = [l.split("\t")[0] for l in open(os.path.join(TOOLS, "repos.tsv")) if l.strip()]
    for repo in repos:
        head, files, last = repo_meta(repo)
        for path, sha, size in files:
            if excluded(path):
                continue
            t = classify(path)
            if t is None:
                continue
            c = last.get(path, ("", "", ""))
            rows.append({
                "repository": repo,
                "path": path,
                "type": t,
                "size_bytes": size,
                "blob_sha": sha,
                "last_commit": c[0],
                "last_commit_date": c[1],
                "last_commit_subject": c[2][:120],
            })
    rows.sort(key=lambda r: (r["repository"], r["path"]))
    with open(os.path.join(OUT, "inventory.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return rows


# ---------------------------------------------------------------- claims index

def line_of(path, needle, start=0):
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            if i >= start and needle in line:
                return i
    return 0


def read(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read().split("\n")


def claims_gravity():
    """gravity/CLAIMS.md: - **C-01 (Title)** -- `LABEL`"""
    repo, rel = "gravity", "CLAIMS.md"
    p = os.path.join(MIRRORS, repo, rel)
    out = []
    if not os.path.exists(p):
        return out
    for i, line in enumerate(read(p), 1):
        m = re.match(r"^\s*-\s+\*\*([A-Z]{1,2}-\d{2}[a-z]?)\s+(.+?)\*\*\s*--\s*(.+)$", line)
        if not m:
            continue
        label = m.group(3).strip().strip("`")
        out.append({
            "repository": repo, "claim_id": m.group(1), "kind": "claim", "file": rel,
            "line": i, "label": label,
            "text": re.sub(r"^\((.*)\)$", r"\1", m.group(2).strip()), "xref": "",
        })
    return out


def claims_gravity_methods():
    """gravity/METHODS_AND_PLAYBOOK.md: method ids M-01..M-10."""
    repo, rel = "gravity", "METHODS_AND_PLAYBOOK.md"
    p = os.path.join(MIRRORS, repo, rel)
    out = []
    if not os.path.exists(p):
        return out
    lines = read(p)
    for i, line in enumerate(lines, 1):
        m = re.match(r"^\s*[-*]\s+\*\*(M-\d{2})\b([^*]*)\*\*", line)
        if m:
            out.append({
                "repository": repo, "claim_id": m.group(1), "kind": "method",
                "file": rel, "line": i,
                "label": "", "text": m.group(2).strip(" :—-"), "xref": "",
            })
    return out


def claims_exoplanets():
    """exoplanets-frontier/CLAIMS.md: ### `C-01`: Title, then - **Status**: LABEL"""
    repo, rel = "exoplanets-frontier", "CLAIMS.md"
    p = os.path.join(MIRRORS, repo, rel)
    out = []
    if not os.path.exists(p):
        return out
    lines = read(p)
    for i, line in enumerate(lines, 1):
        m = re.match(r"^#{2,4}\s*`?([A-Z]{1,2}-\d{2}[a-z]?)`?\s*[:\-]\s*(.+)$", line)
        if not m:
            continue
        claim_id, title = m.group(1), m.group(2).strip()
        label = ""
        for j in range(i, min(i + 6, len(lines))):
            nxt = lines[j]
            sm = re.match(r"^-\s*\*\*Status\*\*\s*:\s*(.+)$", nxt)
            if sm:
                label = sm.group(1).strip()
                break
        out.append({
            "repository": repo, "claim_id": claim_id, "kind": "claim", "file": rel,
            "line": i, "label": label.strip("`"), "text": title, "xref": "",
        })
    return out


def claims_json_ledger(repo, rel, id_field="id", label_field="label", text_field="statement",
                       kind="claim", xref_field=None, label_fallback_field=None):
    p = os.path.join(MIRRORS, repo, rel)
    out = []
    if not os.path.exists(p):
        return out
    lines = read(p)
    data = json.load(open(p))
    entries = data.get("claims") or data.get("entries") or []
    if isinstance(entries, dict):
        entries = list(entries.values())
    for e in entries:
        cid = str(e.get(id_field) or "")
        if not cid:
            continue
        ln = 0
        for i, line in enumerate(lines, 1):
            if re.search(r'"%s"\s*:\s*"%s"' % (id_field, re.escape(cid)), line):
                ln = i
                break
        label = str(e.get(label_field) or "")
        if not label and label_fallback_field:
            label = str(e.get(label_fallback_field) or "")
        xref = ""
        if xref_field and e.get(xref_field):
            xref = ",".join(str(x) for x in e[xref_field])
        out.append({
            "repository": repo, "claim_id": cid, "kind": kind, "file": rel, "line": ln,
            "label": label,
            "text": str(e.get(text_field) or "").replace("\n", " "),
            "xref": xref,
        })
    return out


def claims_scan_md():
    """Catch ID definitions in other markdown files: a line that starts with the
    id followed by a separator, and carries a label token on the same line."""
    labels = r"(PROVEN|VERIFIED|REPRODUCED|KNOWN|OPEN|OVERSTATED|CONTRADICTED|NOT CHECKABLE|CONJECTURE|CLAIMED|COMPUTED|EMPIRICAL-FIT|FALSIFIED)"
    out = []
    repos = [l.split("\t")[0] for l in open(os.path.join(TOOLS, "repos.tsv")) if l.strip()]
    for repo in repos:
        d = os.path.join(MIRRORS, repo)
        for root, dirs, filenames in os.walk(d):
            dirs[:] = [x for x in dirs if x != ".git"]
            for fn in filenames:
                if not fn.endswith(".md"):
                    continue
                rel = os.path.relpath(os.path.join(root, fn), d)
                if rel in {"CLAIMS.md"}:
                    continue
                try:
                    lines = read(os.path.join(root, fn))
                except Exception:
                    continue
                for i, line in enumerate(lines, 1):
                    m = re.match(
                        r"^\s*(?:[-*|#]+\s*)?\**`?([A-Z]{1,2}-?\d{1,3}[a-z]?)`?\**\s*(?:[:(]|—|--|\|)\s*(.+)$",
                        line,
                    )
                    if not m:
                        continue
                    cid = m.group(1)
                    rest = m.group(2)
                    lm = re.search(labels, rest, re.I)
                    if not lm:
                        continue
                    out.append({
                        "repository": repo, "claim_id": cid, "file": rel, "line": i,
                        "label": lm.group(1).upper(),
                        "text": rest.strip()[:300],
                    })
    return out


def build_claims():
    rows = []
    rows += claims_gravity()
    rows += claims_gravity_methods()
    rows += claims_exoplanets()
    rows += claims_json_ledger("project-asma", "registries/claims-ledger.json")
    rows += claims_json_ledger(
        "gravity", "research/update-d144448-review/CLAIM_MAP.json",
        label_field="status", text_field="summary", kind="review-disposition",
        xref_field="claim_ids",
    )
    for r in rows:
        r["label"] = " ".join(str(r["label"]).replace("`", "").split())
        r["scope"] = "reference" if r["repository"] == "project-asma" else "in"
    rows.sort(key=lambda r: (r["repository"], r["file"], int(r["line"]), r["claim_id"]))
    with open(os.path.join(OUT, "claims-index.csv"), "w", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["repository", "claim_id", "kind", "file", "line", "label",
                           "text", "xref", "scope"]
        )
        w.writeheader()
        w.writerows(rows)
    return rows


# ---------------------------------------------------------------- checks census

ASSERT_RE = re.compile(r"^\s*assert\s")
CHECK_RE = re.compile(r"--check\b")
WRITE_RE = re.compile(r"--write\b")


def build_census(inventory):
    repos = [l.split("\t")[0] for l in open(os.path.join(TOOLS, "repos.tsv")) if l.strip()]
    verifiers = {}
    for r in inventory:
        if r["type"] == "verifier":
            verifiers.setdefault(r["repository"], []).append(r["path"])
    rows = []
    for repo in repos:
        d = os.path.join(MIRRORS, repo)
        assert_py = assert_other = 0
        assert_files = []
        check_files = []
        write_files = []
        py_count = 0
        for path in verifiers.get(repo, []):
            if path.endswith(".py"):
                py_count += 1
            try:
                lines = read(os.path.join(d, path))
            except Exception:
                continue
            n = sum(1 for l in lines if ASSERT_RE.match(l))
            if n:
                if path.endswith(".py"):
                    assert_py += n
                else:
                    assert_other += n
                assert_files.append(f"{path} ({n})")
            if any(CHECK_RE.search(l) for l in lines):
                check_files.append(path)
            if any(WRITE_RE.search(l) for l in lines):
                write_files.append(path)
        log = sh(
            ["git", "log", "--pretty=format:%H\x1f%cI\x1f%s", "HEAD"], d
        ).stdout.split("\n")
        skip_all = 0
        skip_recent = 0
        for line in log:
            if "\x1f" not in line:
                continue
            _, date, subj = line.split("\x1f", 2)
            if re.search(r"\[skip[ _-]?ci\]", subj, re.I):
                skip_all += 1
                if date >= "2026-11-07":
                    skip_recent += 1
        sorry = axiom = 0
        lean_files = []
        for r in inventory:
            if r["repository"] != repo or r["type"] != "lean":
                continue
            lean_files.append(r["path"])
            try:
                txt = open(os.path.join(d, r["path"]), encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            stripped = re.sub(r"/-.*?-/", "", txt, flags=re.S)
            stripped = re.sub(r"(?m)--.*$", "", stripped)
            sorry += len(re.findall(r"(?<![\w'])sorry(?![\w'])", stripped))
            axiom += len(re.findall(r"(?m)^\s*axiom\s", txt))
        # context count: every assert statement in every tracked .py file except tests
        all_py = 0
        for path, _, size in repo_meta(repo)[1]:
            if not path.endswith(".py"):
                continue
            base = path.split("/")[-1]
            if base.startswith("test_") or base.endswith("_test.py"):
                continue
            try:
                lines = read(os.path.join(d, path))
            except Exception:
                continue
            all_py += sum(1 for l in lines if ASSERT_RE.match(l))
        rows.append({
            "repository": repo,
            "verifier_files": len(verifiers.get(repo, [])),
            "verifier_py_files": py_count,
            "bare_assert_py_in_verifiers": assert_py,
            "verifier_files_with_bare_assert": len(assert_files),
            "bare_assert_other_languages": assert_other,
            "assert_files": "; ".join(assert_files),
            "check_mode_files": len(check_files),
            "check_mode_list": "; ".join(check_files),
            "write_mode_files": len(write_files),
            "skip_ci_commits": skip_all,
            "skip_ci_commits_since_2026_11_07": skip_recent,
            "lean_files": len(lean_files),
            "lean_sorry": sorry,
            "lean_axiom": axiom,
            "assert_lines_all_py_context": all_py,
        })
    with open(os.path.join(OUT, "checks-census.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return rows


if __name__ == "__main__":
    inv = build_inventory()
    print("inventory rows", len(inv))
    cl = build_claims()
    print("claim rows", len(cl))
    ce = build_census(inv)
    print("census rows", len(ce))
