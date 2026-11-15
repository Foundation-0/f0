import json, glob, re, csv, collections
O='../oeis/'
first={}
for l in open(O+'verify_all.log'):
    m=re.match(r'PASS (A\d+) .* ([\d.]+)s\s*$',l)
    if m: first[m.group(1)]=float(m.group(2))
vt={}
for l in open('verify_all.log'):
    m=re.match(r"PASS (A\d+) .*'seconds': ([\d.]+)",l)
    if m: vt[m.group(1)]=float(m.group(2))
be={}
for l in open('verify_all.log'):
    m=re.match(r"PASS (A\d+) .*'backend': '(\w+)'",l)
    if m: be[m.group(1)]=m.group(2)
rows=[]
for grp,src in (('first211','certs'),('skipped27','certs_skipped')):
    for f in sorted(glob.glob(src+'/A*.json')):
        r=json.load(open(f))
        if r['status']!='proved': rows.append(dict(entry=r['oeis_id'],group=grp,status=r['status'])); continue
        d=len(r['sqrt_poly'])-1
        ref=r.get('first_cert_start') if grp=='first211' else r.get('stated_start')
        rows.append(dict(entry=r['oeis_id'],group=grp,status='proved',order=r['order'],deg_g=d,x_plus_1=r['extra_x_plus_1'],s=r['nilp_s'],D=r['deg_annihilator'],
            omega0=r['omega0'],omega1=r['omega1'],primes_hyp=r['hypothesis_primes'],primes_win=r['window_primes'],
            index_N=r['theorem_index'],start=r['start'],ref_start=ref,agrees=(r['start']==ref),
            prove_s=r['wall'],verify_s=vt.get(r['oeis_id']),first_method_s=first.get(r['oeis_id']),verifier_engine=be.get(r['oeis_id']),note=''))
# the note column for A269765, A269766, A269900 and A270057 was filled in by hand (see square-law.md)
cols=['entry','group','status','order','deg_g','x_plus_1','s','D','omega0','omega1','primes_hyp','primes_win','index_N','start','ref_start','agrees','prove_s','verify_s','first_method_s','verifier_engine','note']
with open('table.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); [w.writerow(r) for r in rows]
for grp in ('first211','skipped27'):
    rs=[r for r in rows if r['group']==grp]; ok=[r for r in rs if r['status']=='proved']
    print(grp,'entries',len(rs),'proved',len(ok),'start agrees',sum(r['agrees'] for r in ok),
      'prove_s total',round(sum(r['prove_s'] for r in ok),1),'verify_s total',round(sum(r['verify_s'] or 0 for r in ok),1),
      'first method total',round(sum(r['first_method_s'] or 0 for r in ok),1))
ok=[r for r in rows if r['status']=='proved' and r['group']=='first211']
print('s dist',sorted(collections.Counter(r['s'] for r in ok).items()),'x+1',sum(r['x_plus_1'] for r in ok))
print('start==N',sum(r['start']==r['index_N'] for r in ok),'of',len(ok), ' with omega1=0:',sum(r['start']==r['index_N'] and r['omega1']==0 for r in ok),' omega1>0:',sum(r['start']==r['index_N'] and r['omega1']>0 for r in ok))
print('max rows omega0',max(r['omega0'] for r in ok),'max primes',max(r['primes_hyp'] for r in ok),max(r['primes_win'] for r in ok))
big=sorted(ok,key=lambda r:-(r['prove_s'] or 0))[:3]; print('slowest first-211 prove',[(r['entry'],r['prove_s']) for r in big])
f1=[r for r in ok if r['first_method_s'] is not None]; print('first-method slowest',sorted([(r['first_method_s'],r['entry']) for r in f1])[-3:])
