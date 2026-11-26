#!/usr/bin/env python3
"""Render the H1 and H2 markdown notes from the generated CSVs."""
import collections
import csv
import os
import re

TOOLS = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(TOOLS)
SOURCES = os.path.join(TOOLS, "sources")
OUT = BASE


def table(rows, cols):
    out = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |")
    return "\n".join(out)


def h1_doc():
    inv = list(csv.DictReader(open(os.path.join(OUT, "inventory.csv"))))
    claims = list(csv.DictReader(open(os.path.join(OUT, "claims-index.csv"))))
    census = list(csv.DictReader(open(os.path.join(OUT, "checks-census.csv"))))
    cov = list(csv.DictReader(open(os.path.join(OUT, "coverage.csv"))))
    heads = [{"repository": r["repository"], "branch": "", "head": r["pinned_head"]}
             for r in cov]
    types = collections.Counter(r["type"] for r in inv)
    kinds = collections.Counter(r["kind"] for r in claims)
    total = lambda k: sum(int(r[k]) for r in census)
    no_ids = [r["repository"] for r in cov if int(r["claim_ids"]) == 0]
    res = list(csv.DictReader(open(os.path.join(OUT, "results-index.csv"))))
    res_kinds = collections.Counter(r["kind"] for r in res)
    empty_res = sorted({r["repository"] for r in cov}
                       - {"gravity", "exoplanets-frontier", "project-asma"}
                       - {r["repository"] for r in res})

    lines = []
    lines.append("# H1 inventory, claims index and checks census")
    lines.append("")
    lines.append("Foundation-0 public repositories, read on 15 November 2026. "
                 "Every fact here is read from a fresh clone at the head named in the table "
                 "below. Nothing in these files judges a claim.")
    lines.append("")
    lines.append("## Scope and pinned heads")
    lines.append("")
    lines.append("35 public repositories, cloned from their default branch. Private "
                 "repositories are out of scope as the issue says. Size: %d research files "
                 "in `inventory.csv`." % len(inv))
    lines.append("")
    lines.append(table(heads, ["repository", "head"]))
    lines.append("")
    lines.append("## What counts as a research file")
    lines.append("")
    lines.append("`inventory.csv` has one row per research file, with its type, blob hash, "
                 "size, and the last commit that touched it. The types and the rule for each:")
    lines.append("")
    lines.append(table([{"type": t, "rows": types[t]} for t in
                        ["claims", "paper", "monograph", "note", "readme", "lean",
                         "verifier", "certificate", "dataset", "zenodo"]],
                       ["type", "rows"]))
    lines.append("")
    lines.append("- **claims**: a claims register (`CLAIMS.md`, `registries/claims-ledger.json`, "
                 "`CLAIM_MAP.json`, `notes/reports/ai-claims.md`).")
    lines.append("- **paper**: files under `papers/` or `paper/`, `manuscript.md`, and `.tex` "
                 "sources outside `docs/`.")
    lines.append("- **monograph**: files under `monographs/`, excluding figures and checksums.")
    lines.append("- **note**: Markdown or text research writing, including every `PROOF.md` "
                 "and `THEOREM.md`.")
    lines.append("- **readme**: a `README.md`. Kept apart because most repositories state "
                 "their result there.")
    lines.append("- **lean**: `*.lean`, except the build file `lakefile.lean`.")
    lines.append("- **verifier**: a script whose name marks it as a checker (`verify`, "
                 "`check`, `audit`, `probe`, `replay`, `recompute`, `validate`, `independent`, "
                 "`attest`, `confirm`, `gate`, `vet`, `equivalence`), excluding `test_*` "
                 "files.")
    lines.append("- **certificate**: `SHA256SUMS`, `commitment/ROOT`, and files with "
                 "`certificate` or `.cert.json` in the name.")
    lines.append("- **dataset**: data and results files under `data/`, `results/`, `inputs/`, "
                 "`snapshot/`, `registries/` and the crystal-structure `cod/` folder.")
    lines.append("- **zenodo**: every `.zenodo.json`.")
    lines.append("")
    lines.append("Not inventoried: figures, site HTML, CSS and JavaScript, CI workflows, "
                 "licences, `AGENTS.md` and `CLAUDE.md`, tests, and library code that is not a "
                 "checker. The rules are mechanical, so a few edge cases are debatable. "
                 "`coverage.csv` shows the counts per repository, so a gap is easy to see.")
    lines.append("")
    lines.append("## Claims index")
    lines.append("")
    lines.append("`claims-index.csv` has %d rows: %d claims, %d method entries and %d review "
                 "dispositions." % (len(claims), kinds["claim"], kinds["method"],
                                     kinds["review-disposition"]))
    lines.append("")
    lines.append("- gravity: 33 claims (`C-01` to `C-33`) from `CLAIMS.md`, 10 methods "
                 "(`M-01` to `M-10`) from `METHODS_AND_PLAYBOOK.md`, and 9 disposition rows "
                 "(`D01` to `D09`) from `research/update-d144448-review/CLAIM_MAP.json`. Each "
                 "D row names the claim it reviews in the `xref` column.")
    lines.append("- exoplanets-frontier: 8 claims (`C-01` to `C-08`) from `CLAIMS.md`.")
    lines.append("- project-asma: 128 claims, 118 from `registries/claims-ledger.json` "
                 "and 10 (`A1` to `A5`, `B1`, `C1` to `C3`) from "
                 "`docs/cdr2-hla-ii-evidence-map-2026-11-06.md`, found by the scan.")
    lines.append("- incentre-lattices: 1 claim (`H1`) from `docs/audit.md`, found by "
                 "the scan.")
    lines.append("- rigid-realizations: 3 claims (`L344`, `L880`, `G160`) from "
                 "`README.md`, found by the scan.")
    lines.append("")
    lines.append("The `scope` column carries the decision: `in` for gravity, "
                 "exoplanets-frontier, incentre-lattices and rigid-realizations, 64 rows "
                 "in all, and `reference` for project-asma, 128 rows. F2 can filter on "
                 "the column instead of the repository name.")
    lines.append("")
    lines.append("The label column repeats the label as written, with Markdown backticks "
                 "removed and nothing else changed. Where a claim carries two labels, both "
                 "are kept. The text column keeps the claim wording verbatim, backticks "
                 "included. Only the label column strips them.")
    lines.append("")
    lines.append("**30 of the 35 public repositories define no claim ID at all.** They state "
                 "results in a `README.md`, a `PROOF.md`, or named result folders, without "
                 "IDs to cite. The exceptions are gravity, exoplanets-frontier, "
                 "project-asma, incentre-lattices and rigid-realizations. A scan of every "
                 "Markdown and JSON file for an ID pattern "
                 "followed by a label found no other register. The 30:")
    lines.append("")
    lines.append(", ".join("`%s`" % r for r in no_ids) + ".")
    lines.append("")
    lines.append("This matters for decision 4 and for F2: a glossary cannot be applied to "
                 "claims that have no identifier to carry a label. The next section indexes "
                 "their stated results. The repositories that do use IDs use three different "
                 "label vocabularies:")
    lines.append("")
    lines.append(table([
        {"repository": "gravity",
         "labels": "COMPUTED (known framework or model scan), EMPIRICAL-FIT, "
                   "KNOWN-LITERATURE-VALUE, CONJECTURE, and PROVEN (ARITHMETIC-LEMMA) on "
                   "the Lean lemmas"},
        {"repository": "exoplanets-frontier",
         "labels": "VERIFIED, FALSIFIED, CONJECTURE, KNOWN"},
        {"repository": "project-asma", "labels": "VERIFIED, KNOWN, CONJECTURE"},
        {"repository": "incentre-lattices", "labels": "CLAIMED"},
        {"repository": "rigid-realizations", "labels": "KNOWN, CLAIMED"},
    ], ["repository", "labels"]))
    lines.append("")
    lines.append("## Results without a claim ID")
    lines.append("")
    lines.append("`results-index.csv` has %d rows from %d repositories. The columns match "
                 "`claims-index.csv`. The ID is provisional, `<repository>/R-<n>`, numbered in "
                 "file and line order within each repository. %d rows carry a label. Labels "
                 "and text have Markdown emphasis, backticks and heading marks removed and "
                 "whitespace collapsed. Nothing else changes." %
                 (len(res), len({r["repository"] for r in res}),
                  sum(1 for r in res if r["label"])))
    lines.append("")
    lines.append("Two repositories in this index also carry a few claim IDs of their own "
                 "(incentre-lattices `H1`, rigid-realizations `L344`, `L880`, `G160`). "
                 "Their stated results are indexed here all the same, since the IDs cover "
                 "only a handful of rows.")
    lines.append("")
    lines.append("Three sources, all mechanical:")
    lines.append("")
    lines.append("- **result-table**, %d rows: the body rows of a table whose header has a "
                 "subject column and a status column. The subject column is the first header "
                 "that begins with `result`, `statement`, `theorem`, `claim`, `contribution`, "
                 "`question`, `track`, `area`, `proposition`, `lemma` or `evidence`, in that "
                 "order. The label comes from a `label`, `status` or `verdict` column. A "
                 "project index (`Project | Question | Status`) keeps the question as the text "
                 "and the status as the label." % res_kinds["result-table"])
    lines.append("- **proof-title** and **proof-statement**, %d rows each: every `PROOF.md` "
                 "and `THEOREM.md` gives two rows. The first is the title, taken from the first "
                 "heading or the first bold line. The second is the first paragraph of the "
                 "statement, or the paragraph after the title when the file has no statement "
                 "heading. The statement row names the title row in `xref`."
                 % res_kinds["proof-title"])
    lines.append("- **result-line**, %d rows: a line that begins `Theorem`, `Proposition`, "
                 "`Lemma`, `Conjecture` or `Result` in a file typed paper, monograph or note, "
                 "outside a code fence and at least 25 characters long." % res_kinds["result-line"])
    lines.append("")
    lines.append("%d repositories give no row: %s. None of them has a result table, a "
                 "`PROOF.md` or `THEOREM.md`, or a theorem line at this head, so any result "
                 "they state is written in prose. Fable's F1 covers prose."
                 % (len(empty_res), ", ".join("`%s`" % r for r in empty_res)))
    lines.append("")
    lines.append("Rows that record a plan rather than a result are kept and labelled as "
                 "written, for example `Not started.` in `astr0`, `physics0` and `math0`. The "
                 "rule copies and does not judge, and F2 decides what to do with them.")
    lines.append("")
    lines.append("`coverage.csv` carries a `results_indexed` column, so a repository with no "
                 "row is visible in the same table as the claim count. The `scope` column is "
                 "`in` on every row: these are results in repositories the issue puts in "
                 "scope, and a result indexed here cannot be outside it.")
    lines.append("")
    lines.append("## Checks census")
    lines.append("")
    lines.append("`checks-census.csv` counts, per repository:")
    lines.append("")
    lines.append("- **bare assert**: statement-level `assert` lines inside verifier files, "
                 "counted separately for Python and for other languages.")
    lines.append("- **check mode**: verifier files that implement a `--check` flag, and "
                 "separately those that implement `--write`.")
    lines.append("- **skip ci**: commits on the default branch whose subject contains "
                 "`[skip ci]`, all time and since 7 November.")
    lines.append("- **Lean**: `sorry` occurrences and `axiom` declarations, after removing "
                 "comments.")
    lines.append("")
    lines.append(table([
        {"what": "verifier files", "count": total("verifier_files")},
        {"what": "bare `assert` in Python verifiers", "count": total("bare_assert_py_in_verifiers")},
        {"what": "bare `assert` in verifiers in other languages", "count": total("bare_assert_other_languages")},
        {"what": "verifier files with a `--check` mode", "count": total("check_mode_files")},
        {"what": "verifier files with a `--write` mode", "count": total("write_mode_files")},
        {"what": "`[skip ci]` commits, all time", "count": total("skip_ci_commits")},
        {"what": "`[skip ci]` commits since 7 November", "count": total("skip_ci_commits_since_2026_11_07")},
        {"what": "Lean files", "count": total("lean_files")},
        {"what": "`sorry`", "count": total("lean_sorry")},
        {"what": "`axiom`", "count": total("lean_axiom")},
    ], ["what", "count"]))
    lines.append("")
    lines.append("All 50 `[skip ci]` commits are in exoplanets-frontier. gravity has none at "
                 "this head. No Lean file at these heads contains `sorry` or declares an "
                 "`axiom`. Matches in comments are excluded, and the two Lean modules that "
                 "mention them say \"zero sorry, zero axiom\".")
    lines.append("")
    lines.append("### Difference from the 14 November scan")
    lines.append("")
    lines.append("The issue gives 107 bare asserts in gravity, 96 in vitruvian3d, 7 in "
                 "incentre-lattices, 6 in point-charges and 4 in rigid-realizations. This "
                 "census gives 245, 155, 9, 5 and 4.")
    lines.append("")
    lines.append("The gap is scope. This count covers every file whose name marks it as a "
                 "checker, and the 14 November scan's file list is not recorded. The "
                 "file-by-file counts are in the `assert_files` column so the two can be "
                 "reconciled. The comparison is a number to refresh, not a finding about "
                 "either scan.")
    lines.append("")
    lines.append("## How to rerun")
    lines.append("")
    lines.append("```")
    lines.append("bash tools/clone-all.sh          # clones the 35 repositories into tools/mirrors,")
    lines.append("                                 # writes tools/heads.tsv")
    lines.append("python3 tools/build_h1.py        # writes inventory.csv, claims-index.csv,")
    lines.append("                                 # checks-census.csv")
    lines.append("python3 tools/build_results.py   # writes results-index.csv from inventory.csv")
    lines.append("python3 tools/build_coverage.py  # writes coverage.csv")
    lines.append("python3 tools/make_docs.py --h1  # writes this note")
    lines.append("```")
    lines.append("")
    lines.append("The scripts are in `tools/`. `tools/mirrors/` holds the clones and "
                 "`tools/.gitignore` keeps them out of the commit. `clone-all.sh` is the only "
                 "step that needs the network.")
    lines.append("")
    lines.append("Three runs on 15 November produced byte-identical copies of every file "
                 "here: two plain runs and one under `python3 -O`. The scripts contain no "
                 "`assert`, so an optimised run cannot skip a check.")
    lines.append("")
    lines.append("Three mutation tests on copies of the clones, each discarded afterwards:")
    lines.append("")
    lines.append("- Deleting the `gaia-dr4` row, `astr0/R-4`, from the project table in "
                 "`astr0/README.md` removed exactly one row (the rows after it renumber, "
                 "so `R-5` is the ID that vanishes) and left 382")
    lines.append("- Deleting the `C-10` line from `gravity/CLAIMS.md` removed exactly that "
                 "row, 192 to 191")
    lines.append("- Adding one `assert` to `gravity/verify_all.py` raised gravity's count "
                 "from 245 to 246")
    lines.append("")
    lines.append("## Limits")
    lines.append("")
    lines.append("- The head is a moment. Counts will move as PRs merge.")
    lines.append("- The classification is by name and path, not by reading each file, so a "
                 "checker with an unusual name is missed and library code that happens to be "
                 "named `check_*` is included. The lists are in the CSV so the error is "
                 "visible.")
    lines.append("- No network fetch is involved. The repository clones are the only "
                 "input, and `heads.tsv` records the commit each file was read at.")
    lines.append("")
    return "\n".join(lines) + "\n"


def h2_doc():
    prs = list(csv.DictReader(open(os.path.join(OUT, "open-prs.csv"))))
    issues = list(csv.DictReader(open(os.path.join(OUT, "open-issues.csv"))))
    branches = list(csv.DictReader(open(os.path.join(OUT, "branches.csv"))))
    lic = list(csv.DictReader(open(os.path.join(OUT, "licences.csv"))))
    zen = list(csv.DictReader(open(os.path.join(OUT, "zenodo-credits.csv"))))
    cut = "2026-11-01"

    pr_by_repo = collections.Counter(p["repository"] for p in prs)
    pr_by_author = collections.Counter(p["author"] for p in prs)
    iss_by_author = collections.Counter(i["author"] for i in issues)
    stranded = [b for b in branches if b["state"] == "stranded"]
    open_pr = len(branches) - len(stranded)
    already = [b for b in stranded if b["content_on_default"] == "yes"]
    recent = [b for b in stranded if b["last_commit_date"][:10] >= "2026-11-01"]
    records = [z for z in zen if z["source"] == "published record"]
    files = [z for z in zen if z["source"] == ".zenodo.json"]
    no_lic = [r for r in lic if not r["license_files"] and not r["github_detected_license"]]

    lines = []
    lines.append("# H2 numbers for the decisions")
    lines.append("")
    lines.append("Read on 15 November 2026 at 01:25 UTC, as ahrazzle, against the GitHub API "
                 "and the Zenodo API. Counts cover the 35 public repositories only.")
    lines.append("")
    lines.append("The snapshot is taken before this pull request and its H1 sibling "
                 "existed, so neither branch nor either pull request is counted here. A "
                 "later read will show two more branches and two more open pull requests. "
                 "Repeat the method below and expect the numbers to move.")
    lines.append("")
    lines.append("## The problem, item 5, refreshed")
    lines.append("")
    lines.append(table([
        {"measure": "open pull requests", "issue_14_nov": "164 across 29 repos",
         "now": "%d across %d repos" % (len(prs), len(pr_by_repo))},
        {"measure": "open PRs opened before 1 November", "issue_14_nov": "115",
         "now": str(sum(1 for p in prs if p["created_at"][:10] < cut))},
        {"measure": "open issues", "issue_14_nov": "121",
         "now": "%d across %d repos" % (len(issues), len({i["repository"] for i in issues}))},
        {"measure": "branch heads not reachable from the default branch",
         "issue_14_nov": "not counted",
         "now": "%d (%d are the head of an open PR, %d have no open PR; %d of the %d are "
                "already on the default branch in content)"
                % (len(branches), open_pr, len(stranded),
                   sum(1 for b in stranded if b["content_on_default"] == "yes"),
                   len(stranded))},
        {"measure": "Phase 2 branches holding work not on `main`", "issue_14_nov": "13",
         "now": "13, all still present"},
    ], ["measure", "issue_14_nov", "now"]))
    lines.append("")
    lines.append("Open PRs by account: " + ", ".join(
        "%s %d" % (a, n) for a, n in pr_by_author.most_common()) + ".")
    lines.append("")
    lines.append("Open issues by account: " + ", ".join(
        "%s %d" % (a, n) for a, n in iss_by_author.most_common()) + ".")
    lines.append("")
    lines.append("The 14 November figure of 164 PRs is now 166, and the account totals moved "
                 "by two for ahrazzle, which is PRs #43 and #44, the review-workspace and "
                 "polish PRs opened on 15 November. "
                 "The issue count moved from 121 to 122. The per-repository lists are in "
                 "`open-prs.csv` and `open-issues.csv`.")
    lines.append("")
    lines.append("### Branches")
    lines.append("")
    lines.append("%d branch heads are not reachable from the default branch of their "
                 "repository. %d of them are the head of an open pull request, so they are "
                 "not stranded work in the sense of the issue. %d have no open pull request. "
                 "%d of those were touched on or after 1 November."
                 % (len(branches), open_pr, len(stranded), len(recent)))
    lines.append("")
    lines.append("%d of the %d have their content on the default branch already, so merging "
                 "them would change nothing. The test is `git merge-tree --write-tree <default> "
                 "<head>`: it prints the default branch's own tree. `branches.csv` gives each "
                 "branch, its head, its last author, its state and the `content_on_default` "
                 "column." % (len(already), len(stranded)))
    lines.append("")
    lines.append(table([{"repository": b["repository"], "branch": b["branch"]}
                        for b in already], ["repository", "branch"]))
    lines.append("")
    lines.append("The 13 branches named in Phase 2 were checked one by one. All 13 still "
                 "exist, none is merged into `main`, and none of them passes the "
                 "`content_on_default` test:")
    lines.append("")
    phase2 = [
        ("gaia-dr4", "prep/gaia-dr4-tasks"),
        ("incentre-lattices", "gpt-forge/distributed-folding"),
        ("incentre-lattices", "codex/focused-fcc-paper"),
        ("incentre-lattices", "prior-art-sources"),
        ("proven-commons", "claude/brave-knuth-x3bkfi"),
        ("proven-commons", "sync/upstream"),
        ("exoplanets-frontier", "orda-aska-patch-1"),
        (".github", "org-pr-template"),
        ("virtual-human", "auto/E-sbml-import"),
        ("virtual-human", "claude/admiring-cori-0qyybb"),
        ("virtual-human", "port/asma-verification-tooling-20261113"),
        ("f0", "claude/beautiful-sagan-ssa4lh"),
        ("f0", "claude/affectionate-ride-rezj73"),
    ]
    lines.append(table([{"repository": r, "branch": b, "state": "present, unmerged"}
                        for r, b in phase2], ["repository", "branch", "state"]))
    lines.append("")
    lines.append("gfq-codes `axiom/delsarte-sweep` also still exists and is unmerged. It "
                 "fails the `content_on_default` test as well, because `main` has edited the "
                 "same files since. Its tip differs from `main` in 15 files. The issue says it "
                 "landed through #15 to #17 and can be deleted after a check.")
    lines.append("")
    lines.append("## Decision 5: the Zenodo credit line")
    lines.append("")
    lines.append("The exact line in every place it appears:")
    lines.append("")
    lines.append("> Researched and verified by different model families across Gemini, Claude, "
                 "Grok, OpenAI, and Muse")
    lines.append("")
    lines.append("- %d `.zenodo.json` files exist. %d carry the line. The two that do not are "
                 "`incentre-lattices/.zenodo.json` and `project-asma/.zenodo.json`. Both have "
                 "their own description, and both belong to repositories with no v1.0.0 "
                 "deposit. The issue body's figure of 18 matches the files that carry the "
                 "line." % (len(files), sum(1 for f in files if f["credit_text"])))
    lines.append("- 16 published records carry the line. All are version v1.0.0, published "
                 "11 November 2026, and each record's description is byte-identical to the "
                 "repository's `.zenodo.json` description. Editing the file alone does not "
                 "change the published record. Each record has to be edited in Zenodo by a "
                 "person with access to the account.")
    lines.append("  `zenodo-credits.csv` lists every `.zenodo.json` file and every published "
                 "v1.0.0 record, with the credit text each carries, so the edit can be "
                 "checked against it.")
    lines.append("")
    lines.append(table([{"repository": r["repository"], "doi": r["doi"],
                         "creators": r["creators"]} for r in sorted(
        records, key=lambda r: r["repository"])],
                       ["repository", "doi", "creators"]))
    lines.append("")
    lines.append("Five more published records carry research from these repositories but no "
                 "repository deposit:")
    lines.append("")
    lines.append(table([
        {"doi": "10.5281/zenodo.23322080", "what": "incentre-lattices paper, v1.0.0",
         "credit": "none"},
        {"doi": "10.5281/zenodo.23340326", "what": "same paper, v2.0.0", "credit": "none"},
        {"doi": "10.5281/zenodo.23841188", "what": "same paper, v3.0.0", "credit": "none"},
        {"doi": "10.5281/zenodo.24145786", "what": "rigid-realizations L880 paper, v1",
         "credit": "a different wording: \"Researched & verified by models across Gemini, "
                   "Claude, Grok, OpenAI, and Muse families\""},
        {"doi": "10.5281/zenodo.23322079", "what": "the same incentre-lattices paper, "
                                                   "v1.0.0. This DOI now resolves to the v3 "
                                                   "record", "credit": "none on the v3 record"},
    ], ["doi", "what", "credit"]))
    lines.append("")
    lines.append("The line is character-for-character identical in all 16 records and in the "
                 "18 files that carry it. The L880 paper's variant is the one different "
                 "string that the decision meets.")
    lines.append("")
    lines.append("## Decision 7: licences")
    lines.append("")
    lines.append("Repositories with no licence file and no licence GitHub detects: %d."
                 % len(no_lic))
    lines.append("")
    lines.append("\n".join("- `%s`" % r["repository"] for r in no_lic))
    lines.append("")
    lines.append("Licence files GitHub reads as NOASSERTION: " + ", ".join(
        "`%s`" % r["repository"] for r in lic
        if r["github_detected_license"] == "NOASSERTION") + ". The file is present but is a "
                 "split licence or a modified text, so GitHub cannot name it.")
    lines.append("")
    lines.append("Detected licences other than Apache-2.0: " + ", ".join(
        "`%s` (%s)" % (r["repository"], r["github_detected_license"]) for r in lic
        if r["github_detected_license"] not in ("", "Apache-2.0", "NOASSERTION")) + ".")
    lines.append("")
    lines.append("Only ductricity and thermal-capture differ: Apache-2.0 for the code with a "
                 "CC BY 4.0 file for the documentation, and cc-by-4.0 in Zenodo. "
                 "nhanes-bioimpedance and point-charges carry an extra `LICENSE-CC-BY-4.0` for "
                 "text. cfrp-strengthening says MIT in Zenodo and has a licence file that "
                 "GitHub reads as NOASSERTION. `licences.csv` lists all of them.")
    lines.append("")
    lines.append("## How to rerun")
    lines.append("")
    lines.append("```")
    lines.append("bash tools/clone-all.sh          # clones the 35 repositories, writes heads.tsv")
    lines.append("gh search prs is:public --owner Foundation-0 --state open --limit 400 \\")
    lines.append("  --json number,createdAt,author,repository,isDraft,title \\")
    lines.append("  > tools/sources/open-prs.json")
    lines.append("gh api 'search/issues?q=is:issue+is:open+is:public+org:Foundation-0&per_page=100' \\")
    lines.append("  --paginate > tools/sources/open-issues-items.json")
    lines.append("python3 tools/build_h2.py        # writes open-prs.csv, open-issues.csv,")
    lines.append("                                 # licences.csv, zenodo-credits.csv")
    lines.append("python3 tools/build_branches.py  # writes branches.csv with open-PR or stranded,")
    lines.append("                                 # and content_on_default")
    lines.append("python3 tools/make_docs.py --h2  # writes this note")
    lines.append("```")
    lines.append("")
    lines.append("The scripts are in `tools/`. The API answers are frozen in `tools/sources/`, "
                 "taken on 15 November, and the scripts read those, so a rerun needs no network "
                 "and reproduces the same rows. The clones are needed for `content_on_default`, "
                 "which runs `git merge-tree` in each repository.")
    lines.append("")
    lines.append("`open-prs.json` and `open-issues-items.json` are the two searches above, "
                 "both `is:public`, so the frozen files hold public repositories only and no "
                 "issue bodies. "
                 "`zenodo.json` is `https://zenodo.org/api/records?q=keywords:foundation0"
                 "&size=25` and `z-<id>.json` is one record each. `unmerged-branches.csv` is "
                 "the branch list at 01:25 UTC, `pr-heads.json` maps each open pull request to "
                 "its branch, and `repo-list.json` is `gh repo list` for the 35 public "
                 "repositories.")
    lines.append("")
    lines.append("The one command that fetches is `python3 tools/build_h2.py --live`. It "
                 "refreshes the branch list for an audit trail and feeds no CSV.")
    lines.append("")
    lines.append("A branch is matched to a pull request by name, not by commit. `f0` "
                 "`review/o1-o2-f0` gained a commit after the snapshot, so its head no longer "
                 "matches the recorded one, while the pull request is open and counted.")
    lines.append("")
    lines.append("Two runs produced byte-identical files, and a run under `python3 -O` "
                 "matched them. One mutation test on a copy of `gaia-dr4`: pointing "
                 "`origin/main` at the head of `prep/gaia-dr4-tasks` flipped that branch's "
                 "`content_on_default` from `no` to `yes`, and changed no other row.")
    lines.append("")
    lines.append("The counts move with every PR and issue. They were taken once, on 15 "
                 "November, and the file lists let a later run be compared.")
    lines.append("")
    return "\n".join(lines) + "\n"


def main(which):
    if which in ("all", "h1"):
        if os.path.exists(os.path.join(OUT, "inventory.csv")):
            open(os.path.join(OUT, "h1-method.md"), "w").write(h1_doc())
            print("wrote h1-method.md")
        else:
            print("skipped h1-method.md: no inventory.csv")
    if which in ("all", "h2"):
        if os.path.exists(os.path.join(OUT, "open-prs.csv")):
            open(os.path.join(OUT, "numbers.md"), "w").write(h2_doc())
            print("wrote numbers.md")
        else:
            print("skipped numbers.md: no open-prs.csv")


if __name__ == "__main__":
    import sys
    main(sys.argv[1].lstrip("-") if len(sys.argv) > 1 else "all")
