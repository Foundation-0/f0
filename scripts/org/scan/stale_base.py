"""Detect stale-base writes: a commit whose new version of a file is closer to an OLDER version than to
the version it replaced, so the intervening edits were overwritten. Delete-then-recreate counts as a rewrite.
Usage: stale_base.py MIRRORS OUT.json"""
import subprocess, sys, os, json, difflib, collections
UTC = {**os.environ, "TZ": "UTC"}   # git prints every date in UTC
if len(sys.argv) != 3 or not os.path.isdir(sys.argv[1]):
    print(__doc__.strip(), file=sys.stderr); sys.exit(2)
MIR, OUT = sys.argv[1], sys.argv[2]; EXCL = set(filter(None, os.environ.get("SCAN_EXCLUDE", "").split(",")))
SKIP_EXT = (".png", ".jpg", ".pdf", ".fits", ".gz", ".zip", ".svg", ".lock")
def git(repo, *a): return subprocess.run(["git","-c","core.quotePath=false","-c","log.date=iso-strict-local","-C",repo,*a],capture_output=True,text=True,errors="replace",env=UTC).stdout
def at_head(repo, f): return subprocess.run(["git","-C",repo,"cat-file","-e",f"HEAD:{f}"],capture_output=True).returncode == 0
def lines(repo, sha, f):
    out = git(repo, "show", f"{sha}:{f}"); return [l.rstrip() for l in out.splitlines()]
def sim(a, b):
    if not a and not b: return 1.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()
found = []
for d in sorted(os.listdir(MIR)):
    if not d.endswith(".git") or d[:-4] in EXCL: continue
    name = d[:-4]; repo = os.path.join(MIR, d)
    chain = git(repo, "log", "--first-parent", "--reverse", "--format=%H%x1f%an%x1f%cn%x1f%cd%x1f%s", "HEAD").splitlines()
    history = collections.defaultdict(list)   # file -> [(sha, date, author, subject, lines)] distinct versions incl. deletion markers
    for row in chain:
        h, an, cn, cd, subj = row.split("\x1f")
        changed = git(repo, "diff-tree", "--no-commit-id", "-r", "--name-status", "-m", "--first-parent", "--root", h).splitlines()
        for c in changed:
            parts = c.split("\t"); st = parts[0][0]; f = parts[-1]
            if f.endswith(SKIP_EXT): continue
            if st == "D":
                history[f].append((h, cd, an, subj, None)); continue
            new = lines(repo, h, f)
            if len(new) > 6000: new = new[:6000]
            vers = [v for v in history[f] if v[4] is not None]
            if len(vers) >= 2:
                parent = vers[-1]
                s_parent = sim(new, parent[4])
                best = max(vers[:-1][-6:], key=lambda v: sim(new, v[4]))
                s_best = sim(new, best[4])
                if s_best > s_parent + 0.08 and s_best > 0.5:
                    pset, bset, nset = set(parent[4]), set(best[4]), set(new)
                    clobbered = [l for l in parent[4] if l.strip() and l not in bset and l not in nset]
                    if len(clobbered) >= 3:
                        # A file deleted since then is not counted as still missing: its removal may be deliberate.
                        head_lines = set(lines(repo, "HEAD", f)) if at_head(repo, f) else None
                        lost_now = [] if head_lines is None else [l for l in clobbered if l not in head_lines]
                        between = [v for v in vers if v[1] > best[1]]
                        found.append(dict(repo=name, file=f, sha=h[:9], date=cd[:16], author=an, subject=subj[:90],
                            sim_to_replaced=round(s_parent,2), sim_to_older=round(s_best,2), older=best[0][:9], older_date=best[1][:16],
                            overwritten_commits=[(v[0][:9], v[1][:16], v[2], v[3][:70]) for v in between],
                            clobbered_lines=len(clobbered), file_at_head=head_lines is not None,
                            still_missing_at_head=len(lost_now), sample=[l.strip()[:100] for l in lost_now[:4]]))
            history[f].append((h, cd, an, subj, new))
json.dump(found, open(OUT, "w"), indent=1)
print("stale-base writes:", len(found), "| still missing today (lines):", sum(x["still_missing_at_head"] for x in found))
print("by repo:", collections.Counter(x["repo"] for x in found).most_common())
for x in sorted(found, key=lambda x: -x["still_missing_at_head"]):
    print(f"\n{x['repo']} {x['file']}  {x['sha']} {x['date']} {x['author']}: {x['subject']}")
    print(f"   new version ~ {x['older']} ({x['older_date']}) at {x['sim_to_older']} vs replaced version at {x['sim_to_replaced']}; "
          f"overwrote {x['clobbered_lines']} lines, " +
          (f"{x['still_missing_at_head']} still missing today" if x["file_at_head"] else "file deleted since"))
    for o in x["overwritten_commits"][:4]: print(f"     overwritten: {o[0]} {o[1]} {o[2]}: {o[3]}")
    for s in x["sample"][:2]: print(f"       e.g. {s}")
