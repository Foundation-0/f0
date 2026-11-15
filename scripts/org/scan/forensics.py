"""Two integrity scans over each repo's default branch.
1. lost-merges: every merged PR's content is still on main (ancestor, squash '(#N)', or patch-equivalent).
2. clobbers: lines deleted by a first-parent commit that another commit had added < WINDOW hours earlier,
   excluding lines that reappear in the same commit (moves/reflows)."""
import subprocess, sys, os, re, json, collections, datetime as dt
MIR, MERGED, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
EXCL = set(filter(None, os.environ.get("SCAN_EXCLUDE", "").split(","))); WINDOW_H = 48
def git(repo, *a, check=False):
    p = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, errors="replace")
    return p.stdout
def ts(s): return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
merged = collections.defaultdict(list)
for l in open(MERGED):
    f = l.rstrip("\n").split("\t"); merged[f[0]].append((int(f[1]), f[2], f[4], f[5]))
res = {"lost": [], "clobbers": []}
for d in sorted(os.listdir(MIR)):
    if not d.endswith(".git"): continue
    name = d[:-4]
    if name in EXCL: continue
    repo = os.path.join(MIR, d)
    chain = git(repo, "log", "--first-parent", "--format=%H%x1f%P%x1f%an%x1f%cn%x1f%cI%x1f%s", "HEAD").splitlines()
    subj_nums = set()
    for line in chain:
        m = re.search(r"\(#(\d+)\)\s*$", line.split("\x1f")[-1]); 
        if m: subj_nums.add(int(m.group(1)))
        m = re.match(r"Merge pull request #(\d+)", line.split("\x1f")[-1])
        if m: subj_nums.add(int(m.group(1)))
    # ---- scan 1
    for n, author, mdate, title in merged.get(name, []):
        ref = f"refs/pull/{n}/head"
        head = git(repo, "rev-parse", "-q", "--verify", ref).strip()
        if not head: res["lost"].append(dict(repo=name, pr=n, title=title, merged=mdate, why="no head ref")); continue
        if subprocess.run(["git","-C",repo,"merge-base","--is-ancestor",head,"HEAD"]).returncode == 0: continue
        if n in subj_nums: continue
        cherry = git(repo, "cherry", "HEAD", head).split()
        plus = [c for i, c in enumerate(cherry) if i % 2 == 1 and cherry[i-1] == "+"]
        if not plus: continue
        # content check: are the PR's final file versions present on main (maybe later edited)?
        base = git(repo, "merge-base", head, "HEAD").strip()
        files = git(repo, "diff", "--name-only", base, head).split()
        same = sum(1 for f in files if git(repo, "rev-parse", f"{head}:{f}").strip() == git(repo, "rev-parse", f"HEAD:{f}").strip())
        res["lost"].append(dict(repo=name, pr=n, title=title, merged=mdate, author=author, unmatched_commits=len(plus), files=len(files), files_identical_on_main=same))
    # ---- scan 2
    for line in chain:
        h, parents, an, cn, cd, subj = line.split("\x1f")
        ps = parents.split()
        if not ps: continue
        p = ps[0]; when = ts(cd)
        diff = git(repo, "diff", "-U0", "--no-color", "-M", p, h)
        cur = None; dels = collections.defaultdict(list); added = set()
        for dl in diff.splitlines():
            if dl.startswith("--- "): cur = dl[6:] if dl.startswith("--- a/") else None
            elif dl.startswith("@@") and cur:
                m = re.match(r"@@ -(\d+)(?:,(\d+))? ", dl); start = int(m.group(1)); cnt = int(m.group(2) or 1)
                if cnt: dels[cur].append((start, cnt))
            elif dl.startswith("+") and not dl.startswith("+++"): added.add(dl[1:].strip())
        for f, ranges in dels.items():
            args = []
            for s, c in ranges: args += ["-L", f"{s},{s+c-1}"]
            bl = git(repo, "blame", "--line-porcelain", *args, p, "--", f)
            origin = None; info = {}
            for bline in bl.splitlines():
                m = re.match(r"^([0-9a-f]{40}) \d+ \d+", bline)
                if m: origin = m.group(1); continue
                if bline.startswith("committer-time "): info["t"] = int(bline.split()[1])
                elif bline.startswith("summary "): info["s"] = bline[8:]
                elif bline.startswith("author "): info["a"] = bline[7:]
                elif bline.startswith("\t"):
                    text = bline[1:].strip()
                    if not text or text in added or origin == h: continue
                    age_h = (when.timestamp() - info.get("t", 0)) / 3600
                    if 0 <= age_h <= WINDOW_H:
                        res["clobbers"].append(dict(repo=name, sha=h[:9], date=cd[:16], author=an, subject=subj, file=f,
                                                    origin=origin[:9], origin_author=info.get("a"), origin_subject=info.get("s"),
                                                    age_h=round(age_h, 1), text=text[:120]))
json.dump(res, open(OUT, "w"))
print("merged PRs whose content is not on main:", len(res["lost"]))
for x in res["lost"]: print("  ", x)
c = collections.Counter((x["repo"], x["sha"], x["date"], x["author"], x["subject"][:70]) for x in res["clobbers"])
print("\ncommits deleting lines added by OTHER commits within 48h (moved/reflowed lines excluded):", len(c), "commits,", len(res["clobbers"]), "lines")
for (r, s, d, a, sub), n in sorted(c.items(), key=lambda kv: -kv[1])[:45]:
    print(f"  {n:5} {r[:18]:18} {s} {d} {a[:10]:10} {sub}")
