import subprocess, re, sys, os, json, collections
MIR, OUT = sys.argv[1], sys.argv[2]
EXCL = set(filter(None, os.environ.get("SCAN_EXCLUDE", "").split(",")))
def git(repo, *a): return subprocess.run(["git","-C",repo,*a],capture_output=True,text=True).stdout
FMT="%H%x1f%P%x1f%an%x1f%ae%x1f%cn%x1f%aI%x1f%cI%x1f%s"
rows=[]
for d in sorted(os.listdir(MIR)):
    if not d.endswith(".git"): continue
    name=d[:-4]; repo=os.path.join(MIR,d)
    if name in EXCL: continue
    # PR heads -> which PR numbers
    heads={}
    for l in git(repo,"for-each-ref","--format=%(objectname) %(refname)","refs/pull").splitlines():
        sha,ref=l.split(); heads.setdefault(sha,[]).append(int(ref.split("/")[2]))
    # commits on PR refs that are NOT on main: index by (author email, author date, subject) -> PR numbers
    idx=collections.defaultdict(set)
    for l in git(repo,"for-each-ref","--format=%(refname)","refs/pull").splitlines():
        n=int(l.split("/")[2])
        for c in git(repo,"log","--format=%ae%x1f%aI%x1f%s",l,"--not","HEAD").splitlines():
            idx[c].add(n)
    chain=git(repo,"log","--first-parent","--format="+FMT,"HEAD").splitlines()
    for line in chain:
        h,parents,an,ae,cn,ad,cd,subj=line.split("\x1f"); np_=len(parents.split())
        m=re.match(r"Merge pull request #(\d+)",subj); key=f"{ae}\x1f{ad}\x1f{subj}"
        prs=[]
        if np_>=2: kind="pr-merge" if m else "merge-direct"; prs=[int(m.group(1))] if m else []
        elif re.search(r"\(#(\d+)\)\s*$",subj): kind="pr-squash"; prs=[int(re.search(r"\(#(\d+)\)\s*$",subj).group(1))]
        elif key in idx: kind="pr-rebase"; prs=sorted(idx[key])
        elif h in heads: kind="pr-head-pushed"; prs=heads[h]
        else: kind="direct-api" if cn=="GitHub" else "direct-push"
        files=[]
        if kind.startswith("direct") or kind in("merge-direct","pr-head-pushed"):
            files=git(repo,"diff-tree","--no-commit-id","--name-only","-r","-m","--first-parent","--root",h).split()
        rows.append(dict(repo=name,sha=h,kind=kind,prs=prs,author=an,email=ae,committer=cn,adate=ad,cdate=cd,subject=subj,nfiles=len(files),files=files[:300]))
json.dump(rows,open(OUT,"w"))
K=("pr-merge","pr-squash","pr-rebase","pr-head-pushed","direct-api","direct-push","merge-direct")
c=collections.Counter((r["repo"],r["kind"]) for r in rows); tot=collections.Counter()
print(f"{'repo':22}"+"".join(f"{k[:11]:>12}" for k in K))
for rp in sorted({r["repo"] for r in rows}):
    v=[c[(rp,k)] for k in K]
    for k,x in zip(K,v): tot[k]+=x
    print(f"{rp:22}"+"".join(f"{x:12}" for x in v))
print(f"{'TOTAL':22}"+"".join(f"{tot[k]:12}" for k in K))
