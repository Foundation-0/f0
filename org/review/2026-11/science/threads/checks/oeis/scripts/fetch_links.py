import sys, os, re, time, urllib.request; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import spec
SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sources')
c = spec.load_cache(); last = 0
for a, e in sorted(c.items()):
    f = e.get('formula') or []
    if not any('Empirical recurrence of order' in x for x in f): continue
    if not spec.parse_name(e['name']): continue
    order = int(re.search(r'order (\d+)', f[0]).group(1))
    path = os.path.join(SRC, 'a%06d.txt' % a)
    if not os.path.exists(path):
        time.sleep(max(0, 1.1 - (time.time() - last)))
        url = 'https://oeis.org/A%06d/a%06d.txt' % (a, a)
        try: data = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'recurrence-check/0.1'}), timeout=40).read()
        except Exception as ex: data = b''; print('fail', a, ex)
        last = time.time(); open(path, 'wb').write(data)
    txt = open(path, errors='replace').read()
    r = spec.parse_recurrence([txt.strip()])
    print(a, 'order stated', order, 'bytes', len(txt), 'parsed order', len(r[0]) if r else None, 'complete' if r and len(r[0]) == order else 'INCOMPLETE')
