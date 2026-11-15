"""For every non-default branch and closed-unmerged PR: which file versions never appeared on main at any point?
Usage: unlanded.py MIRRORS OUT.json CLOSED_UNMERGED.tsv OPEN_PRS.tsv  (TSVs from list_prs.sh; first two columns repo, number)"""
import subprocess, os, sys, collections, json
MIR, OUT, CLOSED_TSV, OPEN_TSV = sys.argv[1:5]
EXCL = set(filter(None, os.environ.get("SCAN_EXCLUDE", "").split(",")))
def git(r,*a): return subprocess.run(["git","-C",r,*a],capture_output=True,text=True,errors="replace").stdout
closed = collections.defaultdict(list)
for l in open(CLOSED_TSV):
    f=l.rstrip("\n").split("\t"); closed[f[0]].append(int(f[1]))
openp = collections.defaultdict(set)
for l in open(OPEN_TSV):
    f=l.split("\t"); openp[f[0]].add(int(f[1]))
out=[]
for d in sorted(os.listdir(MIR)):
    if not d.endswith(".git"): continue
    r=d[:-4]
    if r in EXCL: continue
    repo=os.path.join(MIR,d)
    # every blob ever on main, per path
    seen=collections.defaultdict(set)
    for l in git(repo,"log","--format=","--raw","--no-abbrev","-m","--first-parent","HEAD").splitlines():
        p=l.split()
        if len(p)>=6 and l.startswith(":"): seen[p[-1]].add(p[3])
    all_blobs=set(b for s in seen.values() for b in s)
    cands=[]
    for l in git(repo,"for-each-ref","--format=%(refname:short) %(objectname)","refs/heads").splitlines():
        b,s=l.split()
        if b not in ("main","master"): cands.append((f"branch:{b}",s))
    for n in closed.get(r,[]):
        s=git(repo,"rev-parse","-q","--verify",f"refs/pull/{n}/head").strip()
        if s: cands.append((f"closed-PR#{n}",s))
    for name,s in cands:
        if subprocess.run(["git","-C",repo,"merge-base","--is-ancestor",s,"HEAD"]).returncode==0: continue
        base=git(repo,"merge-base",s,"HEAD").strip()
        lost=[]
        for l in git(repo,"diff","--raw","--no-abbrev",base,s).splitlines():
            p=l.split(); st=p[4][0]; path=p[-1]; blob=p[3]
            if st=="D": continue
            if blob in seen[path] or blob in all_blobs: continue
            n_lines=len(git(repo,"show",blob).splitlines())
            lost.append((path,n_lines))
        if lost:
            out.append(dict(repo=r,ref=name,sha=s[:9],date=git(repo,"log","-1","--format=%cI",s)[:10],
                            author=git(repo,"log","-1","--format=%an",s).strip(),files=len(lost),lines=sum(x[1] for x in lost),
                            paths=[x[0] for x in sorted(lost,key=lambda x:-x[1])[:6]]))
json.dump(out,open(OUT,"w"),indent=1)
print(f"refs carrying file versions that never reached main: {len(out)}; files {sum(x['files'] for x in out)}; lines {sum(x['lines'] for x in out)}")
for x in sorted(out,key=lambda x:(x['repo'],-x['lines'])):
    print(f"  {x['repo'][:18]:18} {x['ref'][:52]:52} {x['date']} {x['author'][:12]:12} files={x['files']:3} lines={x['lines']:6}  {', '.join(x['paths'][:3])[:90]}")
