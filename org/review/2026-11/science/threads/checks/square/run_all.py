import sys, json, glob, os, time
sys.path.insert(0,'.')
from multiprocessing import Pool
from sqprove import prove
S0='../oeis/certs/'
os.makedirs('certs',exist_ok=True)
def work(a):
    c=json.load(open(S0+a+'.json'))
    t=time.time()
    try:
        r=prove(c['name'],c['recurrence']['coefficients'],c['data_terms'])
    except Exception as e:
        r=dict(status='error: %r'%e)
    r['oeis_id']=a; r['first_cert_start']=c['proof']['min_start']; r['first_cert_kind']=c['proof']['kind']
    r['order']=len(c['recurrence']['coefficients']); r['wall']=round(time.time()-t,2)
    json.dump(r,open('certs/%s.json'%a,'w'))
    return a,r
if __name__=='__main__':
    ids=sorted(os.path.basename(f)[:-5] for f in glob.glob(S0+'A*.json'))
    # biggest first-pass state counts last
    with Pool(2) as p:
        for a,r in p.imap_unordered(work,ids):
            print(a,r['status'],r.get('start'),r['first_cert_start'],r.get('theorem_index'),r.get('rows'),r['wall'],flush=True)
