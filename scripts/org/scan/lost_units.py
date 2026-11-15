"""Inventory named units (py defs/classes, Lean decls, claim IDs, md headings, whole files) that existed on a
default branch at some point and are absent everywhere in the repo today. Records who removed them and why.
Usage: lost_units.py MIRRORS OUT.json"""
import subprocess, os, re, sys, json, collections
UTC = {**os.environ, "TZ": "UTC"}   # git prints every date in UTC
if len(sys.argv) != 3 or not os.path.isdir(sys.argv[1]):
    print(__doc__.strip(), file=sys.stderr); sys.exit(2)
MIR, OUT = sys.argv[1], sys.argv[2]; EXCL = set(filter(None, os.environ.get("SCAN_EXCLUDE", "").split(",")))
INTENT=re.compile(r"\b(remov|delet|drop|purg|supersed|replac|renam|refactor|consolidat|withdr|retract|retir|deprecat|clean|dedup|duplicate|revert|move|merge|split|rewrite)", re.I)
def git(r,*a): return subprocess.run(["git","-c","core.quotePath=false","-c","log.date=iso-strict-local","-C",r,*a],capture_output=True,text=True,errors="replace",env=UTC).stdout
def units(path, text):
    u=set()
    if path.endswith(".py"):
        cls=None
        for l in text.splitlines():
            m=re.match(r"^class\s+(\w+)",l); 
            if m: cls=m.group(1); u.add(f"py:class {cls}"); continue
            m=re.match(r"^def\s+(\w+)",l)
            if m: cls=None; u.add(f"py:def {m.group(1)}"); continue
            m=re.match(r"^    def\s+(\w+)",l)
            if m and cls: u.add(f"py:def {cls}.{m.group(1)}")
    elif path.endswith(".lean"):
        for m in re.finditer(r"^\s*(?:@\[[^\]]*\]\s*)?(?:private\s+|protected\s+|noncomputable\s+)*(theorem|lemma|def|structure|inductive|abbrev)\s+([\w.'’]+)",text,re.M):
            u.add(f"lean:{m.group(1)} {m.group(2)}")
    elif path.endswith(".md"):
        for m in re.finditer(r"^#{1,4}\s+(.+?)\s*$",text,re.M): u.add(f"md:# {m.group(1)[:80]}")
    if path.endswith((".md",".json",".py",".lean",".csv",".tex")):
        for m in re.finditer(r"\b([CFM]-\d{2,3})\b",text): u.add(f"id:{m.group(1)}")
    return u
res=[]
for d in sorted(os.listdir(MIR)):
    if not d.endswith(".git") or d[:-4] in EXCL: continue
    r=d[:-4]; repo=os.path.join(MIR,d)
    head_files=set(f for f in git(repo,"ls-tree","-r","-z","--name-only","HEAD").split("\0") if f)
    head_units=set()
    for f in head_files:
        if f.endswith((".py",".lean",".md",".json",".csv",".tex")):
            head_units|=units(f,git(repo,"show",f"HEAD:{f}"))
    last_seen={}   # unit -> (sha,date,author,subject,path)
    removed_by={}  # unit -> (sha,date,author,subject)
    prev=collections.defaultdict(set)
    chain=git(repo,"log","--first-parent","--reverse","--format=%H%x1f%cd%x1f%an%x1f%s","HEAD").splitlines()
    present=set()
    for row in chain:
        h,cd,an,subj=row.split("\x1f")
        for l in git(repo,"diff-tree","--no-commit-id","-r","--name-status","-m","--first-parent","--root",h).splitlines():
            p=l.split("\t"); st=p[0][0]; f=p[-1]
            if st=="R": 
                old=p[1]; prev[f]=prev.pop(old,set()); 
            if st=="D":
                gone=prev.pop(f,set())|{f"file:{f}"}
                for u in gone:
                    removed_by.setdefault((u,f),(h[:9],cd[:16],an,subj[:90]))
                continue
            if not f.endswith((".py",".lean",".md",".json",".csv",".tex")):
                last_seen[(f"file:{f}",f)]=(h[:9],cd[:16],an,subj[:90]); prev[f].add(f"file:{f}"); continue
            new=units(f,git(repo,"show",f"{h}:{f}"))|{f"file:{f}"}
            for u in prev[f]-new: removed_by.setdefault((u,f),(h[:9],cd[:16],an,subj[:90]))
            for u in new:
                last_seen[(u,f)]=(h[:9],cd[:16],an,subj[:90]); removed_by.pop((u,f),None)
            prev[f]=new
    for (u,f),rb in removed_by.items():
        if u.startswith("file:"):
            if f in head_files: continue
            base=os.path.basename(f)
            if any(os.path.basename(x)==base for x in head_files): continue   # moved
        elif u in head_units: continue
        ls=last_seen.get((u,f))
        if not ls: continue
        res.append(dict(repo=r,unit=u,path=f,added_in=ls,removed_in=rb,explained=bool(INTENT.search(rb[3]))))
json.dump(res,open(OUT,"w"),indent=1)
c=collections.Counter((x["repo"],x["unit"].split(":")[0],x["explained"]) for x in res)
print("units that existed on main and are gone today:",len(res))
rep=collections.defaultdict(lambda: collections.Counter())
for (r,k,e),n in c.items(): rep[r][f"{k}{'' if e else '*'}"]+=n
for r,cn in sorted(rep.items(),key=lambda kv:-sum(kv[1].values())):
    print(f"  {r[:20]:20} total={sum(cn.values()):4}  "+"  ".join(f"{k}={v}" for k,v in sorted(cn.items())))
print("(* = removing commit's message does not mention removing, replacing, refactoring etc.)")
