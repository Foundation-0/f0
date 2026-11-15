"""Rate-limited cached OEIS JSON fetcher (<=1 request/second). Cache in ../sources/."""
import json, os, sys, time, urllib.request, urllib.parse, hashlib
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sources')
os.makedirs(SRC, exist_ok=True)
_last = [0.0]
def fetch_url(url):
    key = hashlib.sha1(url.encode()).hexdigest()[:16]
    path = os.path.join(SRC, 'q_' + key + '.json')
    if os.path.exists(path):
        return json.load(open(path))
    wait = 1.1 - (time.time() - _last[0])
    if wait > 0: time.sleep(wait)
    req = urllib.request.Request(url, headers={'User-Agent': 'recurrence-check/0.1'})
    for attempt in range(4):
        try:
            data = urllib.request.urlopen(req, timeout=40).read()
            _last[0] = time.time()
            break
        except Exception as e:
            _last[0] = time.time(); time.sleep(5 * (attempt + 1)); data = None
    if data is None: return None
    open(path, 'wb').write(data)
    return json.loads(data)
def search(q, start=0):
    url = 'https://oeis.org/search?q=' + urllib.parse.quote(q) + '&fmt=json&start=%d' % start
    return fetch_url(url)
def entry(a):
    r = search('id:A%06d' % a if isinstance(a, int) else 'id:' + a)
    if isinstance(r, dict): r = r.get('results')
    return r[0] if r else None
if __name__ == '__main__':
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    for a in range(lo, hi + 1):
        e = entry(a)
        print(a, (e or {}).get('name', 'NONE')[:110], flush=True)
