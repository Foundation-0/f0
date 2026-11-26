#!/usr/bin/env python3
"""H1b: index the stated results that have no claim ID.

Thirty of the 35 public repositories state results without a claim
identifier. F2 needs one row per stated result, so this reads the mirrors and
writes results-index.csv with the same columns as claims-index.csv, plus a
provisional ID of the form <repository>/R-<n>.

Three sources, all mechanical:

  1. table rows, where the header has a subject column (result, statement,
     theorem, claim, contribution, question, track, area, proposition, lemma,
     evidence, in that priority order) and a status column (label, status,
     verdict);
  2. the title and statement of every PROOF.md and THEOREM.md;
  3. lines that begin Theorem, Proposition, Lemma, Conjecture or Result in a
     file typed paper, monograph or note.

Labels are copied as written. Nothing here judges a result.
"""
import csv
import os
import re

TOOLS = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(TOOLS)
MIRRORS = os.path.join(TOOLS, "mirrors")
OUT = BASE

# Repositories that already carry claim IDs, or that are reference scope only.
# incentre-lattices and rigid-realizations carry a few IDs of their own, but
# their stated results are indexed here all the same; the IDs cover only a
# handful of rows.
SKIP = {"gravity", "exoplanets-frontier", "project-asma"}

# Priority order: the first header that matches names the result. "result" and
# "statement" win over "contribution" in tables that carry both. A bare project
# index ("Project | Question | Status") keeps the question, which is the work
# named, and takes its status as the label.
SUBJECT_WORDS = ("result", "statement", "theorem", "claim", "contribution",
                 "question", "track", "area", "proposition", "lemma", "evidence")
TEXT_WORDS = ("evidence", "claim", "statement", "description", "meaning",
              "summary", "detail", "validated")
STATUS_WORDS = ("label", "status", "verdict")
LABEL_TOKENS = ("PROVEN", "VERIFIED", "CONJECTURE", "KNOWN", "COMPUTED",
                "FALSIFIED", "CLAIMED", "REPRODUCED", "CONFIRMED", "OPEN",
                "OVERSTATED", "CONTRADICTED")
THEOREM_RE = re.compile(
    r"^\s*(?:#{1,6}\s*|[-*+]\s+|\d+\.\s+)?\*{0,2}"
    r"(Theorem|Proposition|Lemma|Conjecture|Result)\b")
LABEL_RE = re.compile(r"\b(" + "|".join(LABEL_TOKENS) + r")\b")
HEADING_RE = re.compile(r"^#{1,6}\s+")
SEP_RE = re.compile(r"^\s*\|?[\s:|-]+\|?\s*$")


def read(path):
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read().split("\n")


def clean(cell):
    """One normalisation for every row: no markdown marks, no stray spacing."""
    text = cell.replace("\\|", "|")
    for mark in ("**", "__", "`"):
        text = text.replace(mark, "")
    return " ".join(text.split())


def header_cells(line):
    cells = [clean(c) for c in line.strip().strip("|").split("|")]
    return [c.lower().strip("*` ") for c in cells]


def table_rows(lines):
    """Yield (line_no, cells) for every body row of every table."""
    i = 0
    while i < len(lines):
        line = lines[i]
        if (line.strip().startswith("|") and i + 1 < len(lines)
                and SEP_RE.match(lines[i + 1]) and "-" in lines[i + 1]):
            head = header_cells(line)
            subject = None
            subject_word = ""
            for word in SUBJECT_WORDS:
                hit = next((n for n, h in enumerate(head)
                            if h.strip("*` ").split(" ")[0].strip(":") == word), None)
                if hit is not None:
                    subject = hit
                    subject_word = word
                    break
            status = next((n for n, h in enumerate(head)
                           if any(w in h for w in STATUS_WORDS)), None)
            bare = subject_word in ("result", "statement", "theorem")
            has_text = any(any(w in h for w in TEXT_WORDS) for n, h in enumerate(head)
                           if n != subject)
            keep = subject is not None and (status is not None or (bare and has_text))
            j = i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                if keep and subject != status:
                    cells = [clean(c) for c in lines[j].strip().strip("|").split("|")]
                    if len(cells) == len(head):
                        label = cells[status] if status is not None else ""
                        yield j + 1, cells[subject], label
                j += 1
            i = j
        else:
            i += 1


def strip_md(line):
    return clean(line)


def statement_of(lines):
    """Return (title, statement, label, title_line, statement_line).

    A PROOF.md or THEOREM.md states one result. The title is the first heading,
    or the first bold line when the file has no heading. The statement is the
    first prose paragraph of its Statement section, when the file has one.
    """
    title = ""
    title_line = 0
    for n, line in enumerate(lines):
        if HEADING_RE.match(line):
            title = HEADING_RE.sub("", line).strip()
            title_line = n + 1
            break
    if not title:
        for n, line in enumerate(lines):
            text = line.strip()
            if text and not text.startswith("|"):
                title = strip_md(text)
                title_line = n + 1
                break

    label = ""
    for line in lines:
        low = strip_md(line).lower()
        if low.startswith(("evidence label", "evidence:", "status:")):
            label = strip_md(line)
            break

    start = None
    for n, line in enumerate(lines):
        if re.match(r"^#{1,6}\s+statement\b", line.strip(), re.I):
            start = n + 1
            break
    statement = ""
    statement_line = 0
    if start is None:
        start = title_line
    if start:
        collecting = False
        for n in range(start, min(start + 80, len(lines))):
            text = lines[n].strip()
            if not text or HEADING_RE.match(text) or text.startswith("|"):
                if collecting:
                    break
                continue
            low = strip_md(text).lower()
            if low.startswith(("evidence label", "evidence:", "status:", "replay:", "certificate:")):
                continue
            if not collecting:
                collecting = True
                statement_line = n + 1
            statement = (statement + " " + text).strip()
    return title, statement, label, title_line, statement_line


def build():
    inventory = list(csv.DictReader(open(os.path.join(OUT, "inventory.csv"))))
    by_repo = {}
    for row in inventory:
        by_repo.setdefault(row["repository"], []).append(row)

    rows = []
    for repo in sorted(by_repo):
        if repo in SKIP:
            continue
        seen_files = set()
        for item in sorted(by_repo[repo], key=lambda r: r["path"]):
            path = item["path"]
            if not path.endswith(".md") or path in seen_files:
                continue
            seen_files.add(path)
            full = os.path.join(MIRRORS, repo, path)
            if not os.path.exists(full):
                continue
            lines = read(full)
            name = os.path.basename(path)
            if name in ("PROOF.md", "THEOREM.md"):
                title, statement, label, title_line, stmt_line = statement_of(lines)
                if title:
                    rows.append({
                        "repository": repo, "kind": "proof-title", "file": path,
                        "line": title_line, "label": label, "text": title, "xref": "",
                        "_parent": "",
                    })
                if statement:
                    rows.append({
                        "repository": repo, "kind": "proof-statement", "file": path,
                        "line": stmt_line, "label": label, "text": statement,
                        "xref": "", "_parent": title,
                    })
                continue
            if item["type"] in ("paper", "monograph", "note", "readme"):
                for line_no, text, label in table_rows(lines):
                    if text:
                        rows.append({
                            "repository": repo, "kind": "result-table", "file": path,
                            "line": line_no, "label": label, "text": text, "xref": "",
                        })
            if item["type"] in ("paper", "monograph", "note"):
                in_fence = False
                for n, line in enumerate(lines):
                    if line.lstrip().startswith("```"):
                        in_fence = not in_fence
                        continue
                    if in_fence or not THEOREM_RE.match(line):
                        continue
                    text = clean(HEADING_RE.sub("", line.strip()))
                    if len(text) < 25:
                        continue
                    labels = []
                    for token in LABEL_RE.findall(line):
                        if token not in labels:
                            labels.append(token)
                    rows.append({
                        "repository": repo, "kind": "result-line", "file": path,
                        "line": n + 1, "label": ", ".join(labels), "text": text,
                        "xref": "",
                    })

    rows.sort(key=lambda r: (r["repository"], r["file"], int(r["line"]), r["kind"]))
    counter = {}
    title_id = {}
    for r in rows:
        counter[r["repository"]] = counter.get(r["repository"], 0) + 1
        r["claim_id"] = "%s/R-%d" % (r["repository"], counter[r["repository"]])
        if r["kind"] == "proof-title":
            title_id[(r["repository"], r["file"])] = r["claim_id"]
        elif r["kind"] == "proof-statement":
            r["xref"] = title_id.get((r["repository"], r["file"]), "")
    with open(os.path.join(OUT, "results-index.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[
            "repository", "claim_id", "kind", "file", "line", "label", "text",
            "xref", "scope"])
        w.writeheader()
        for r in rows:
            r.pop("_parent", None)
            r["scope"] = "in"
            w.writerow(r)
    return rows


if __name__ == "__main__":
    result = build()
    from collections import Counter
    print("rows", len(result))
    print(Counter(r["kind"] for r in result))
    print("repos", len({r["repository"] for r in result}))
    print("with label", sum(1 for r in result if r["label"]))
