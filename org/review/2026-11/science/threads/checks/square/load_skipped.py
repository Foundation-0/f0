import json, glob, re, os, sys, time, urllib.request
O='../oeis/'
SKIP="A268910 A268977 A269041 A269058 A269096 A269108 A269199 A269212 A269274 A269275 A269281 A269287 A269288 A269294 A269763 A269764 A269765 A269766 A269898 A269899 A269900 A269934 A270055 A270056 A270057 A269095 A269107".split()
def load_entries():
    d={}
    for fn in glob.glob(O+'sources/q_*.json'):
        x=json.load(open(fn))
        if isinstance(x,dict): x=x.get('results') or []
        for e in x or []: d[e['number']]=e
    return d
TERM=re.compile(r'([+-]?)\s*(?:(\d+)\s*\*\s*)?a\(n\s*-\s*(\d+)\)')
def parse_rec(text):
    m=re.search(r'Empirical:\s*a\(n\)\s*=\s*(.*?)(?:\s+for\s+n|\.\s|$)',text.replace('\n',' '))
    if not m: return None
    body=m.group(1); co={}
    for sg,c,i in TERM.findall(body):
        v=int(c) if c else 1; co[int(i)]=co.get(int(i),0)+(-v if sg=='-' else v)
    if not co: return None
    sm=re.search(r'for\s+n\s*(>=|>)\s*(\d+)',text)
    st=None if not sm else int(sm.group(2))+(1 if sm.group(1)=='>' else 0)
    return [co.get(i,0) for i in range(1,max(co)+1)], st
last=[0.0]
def fetch_txt(a):
    path='sources/a%06d.txt'%a
    if os.path.exists(path): return open(path).read()
    for p in (O+'sources/a%06d.txt'%a,):
        if os.path.exists(p): return open(p).read()
    wait=1.1-(time.time()-last[0])
    if wait>0: time.sleep(wait)
    url='https://oeis.org/A%06d/a%06d.txt'%(a,a)
    data=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'recurrence-check/0.1'}),timeout=40).read().decode()
    last[0]=time.time(); open(path,'w').write(data); return data
def get(aid):
    a=int(aid[1:]); e=load_entries()[a]
    rec=None
    for f in e.get('formula',[]):
        rec=parse_rec(f)
        if rec: break
    src='entry formula line'
    if not rec:
        rec=parse_rec(fetch_txt(a)); src='linked file a%06d.txt'%a
    data=[int(x) for x in e['data'].split(',')]
    return dict(id=aid,name=e['name'],coeffs=rec[0] if rec else None,stated_start=rec[1] if rec else None,source=src,data=data)
if __name__=='__main__':
    out={}
    for a in SKIP:
        r=get(a); out[a]=r
        print(a,r['name'][:60],len(r['coeffs']) if r['coeffs'] else None,r['stated_start'],len(r['data']))
    json.dump(out,open('skipped_inputs.json','w'))
