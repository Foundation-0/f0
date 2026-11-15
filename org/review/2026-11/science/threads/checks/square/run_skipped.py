import sys, json, os, time
sys.path.insert(0,'.')
from multiprocessing import Pool
from sqprove import prove, sqrt_form, charpoly
from sqlib import parse
os.makedirs('certs_skipped',exist_ok=True)
inp=json.load(open('skipped_inputs.json'))
def work(a):
    r0=inp[a]; t=time.time()
    try:
        r=prove(r0['name'],r0['coeffs'],r0['data'])
    except Exception as e:
        import traceback; r=dict(status='error: %r'%e, tb=traceback.format_exc())
    r['oeis_id']=a; r['stated_start']=r0['stated_start']; r['order']=len(r0['coeffs']); r['wall']=round(time.time()-t,1)
    r['coeffs']=r0['coeffs']; r['name']=r0['name']
    json.dump(r,open('certs_skipped/%s.json'%a,'w'))
    return a,r
if __name__=='__main__':
    def size(a):
        sp=parse(inp[a]['name']); return sp['q']**sp['k']
    ids=sorted(inp,key=size)
    if len(sys.argv)>1: ids=sys.argv[1:]
    with Pool(2) as p:
        for a,r in p.imap_unordered(work,ids,chunksize=1):
            print(a,r['status'],'start',r.get('start'),'stated',r['stated_start'],'N',r.get('theorem_index'),'rows',r.get('rows'),'wall',r['wall'],'primes',r.get('hypothesis_primes'),r.get('window_primes'),flush=True)
