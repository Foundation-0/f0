"""Parse Hardin's 'some element plus some ... neighbor totalling T exactly/not more than once' names
and the 'Empirical: a(n) = ...' recurrence lines. Own code, no dependency on the repository."""
import re, json, glob, os
HERE = os.path.dirname(os.path.abspath(__file__))
NUM = {'zero':0,'one':1,'two':2,'three':3,'four':4,'five':5,'six':6}
DIRS = {'horizontally':'H','vertically':'V','diagonally':'D','antidiagonally':'A'}
NAME_RE = re.compile(
    r'^Number of (?P<shape>n[ _]?X[ _]?(?P<k1>\d+)|(?P<k2>\d+)[ _]?X[ _]?n|n[ _]?X[ _]?n) '
    r'(?P<alpha>binary|0\.\.(?P<top>\d+)) arrays with some element plus some '
    r'(?P<dirs>[a-z, ]+?) adjacent neighbor totalling (?P<tot>\w+) '
    r'(?P<mode>exactly once|not more than once|no more than once)\.?$')
def parse_name(name):
    name = re.sub(r'\s+', ' ', name.strip())
    m = NAME_RE.match(name)
    if not m: return None
    if re.sub(r'[ _]','',m['shape']) == 'nXn': return None
    if m['k1']: orient, k = 'nxk', int(m['k1'])      # n rows grow, k columns fixed
    else: orient, k = 'kxn', int(m['k2'])           # k rows fixed, n columns grow
    q = 2 if m['alpha'] == 'binary' else int(m['top']) + 1
    ds = [DIRS[w] for w in re.findall(r'[a-z]+', m['dirs']) if w in DIRS]
    if not ds or m['tot'] not in NUM: return None
    return dict(orient=orient, k=k, q=q, nbrs=''.join(sorted(set(ds))), total=NUM[m['tot']],
                mode='exact' if m['mode'] == 'exactly once' else 'atmost')
TERM_RE = re.compile(r'([+-]?)\s*(?:(\d+)\s*\*\s*)?a\(n\s*-\s*(\d+)\)')
def parse_recurrence(formulas):
    """Return (coeffs list c_1..c_k, text) from a line 'Empirical: a(n) = ...' or None. Coefficients as ints."""
    for f in formulas:
        if not f.lstrip().lower().startswith('empirical: a(n)'): continue
        m = re.match(r'\s*Empirical:\s*a\(n\)\s*=\s*(.*?)(?:\.|\s+for\s+n|\s+-\s+_|$)', f, re.I)
        if not m: continue
        body = m.group(1)
        # reject anything but sums of c*a(n-i)
        rest = TERM_RE.sub('', body).replace(' ', '')
        if rest not in ('',): continue
        co = {}
        for sgn, c, i in TERM_RE.findall(body):
            v = int(c) if c else 1
            co[int(i)] = co.get(int(i), 0) + (-v if sgn == '-' else v)
        if not co: continue
        k = max(co)
        sm = re.search(r'for\s+n\s*(>=|>|\u2265)\s*(\d+)', f)
        stated = None if not sm else (int(sm.group(2)) + (1 if sm.group(1) == '>' else 0))
        return [co.get(i, 0) for i in range(1, k + 1)], f, stated
    return None
def load_cache():
    out = {}
    for fn in glob.glob(os.path.join(HERE, '..', 'sources', 'q_*.json')):
        try: d = json.load(open(fn))
        except Exception: continue
        if isinstance(d, dict): d = d.get('results') or []
        for e in d or []: out[e['number']] = e
    return out

def recurrence_for(a, e):
    """Recurrence of entry a: from its formula lines, else from Hardin's linked a<id>.txt (cached by fetch_links.py).
    Returns (coeffs, line, stated_start, origin) or None."""
    r = parse_recurrence(e.get('formula', []))
    if r: return r + ('entry formula line',)
    path = os.path.join(HERE, '..', 'sources', 'a%06d.txt' % a)
    if os.path.exists(path):
        txt = open(path, errors='replace').read().strip()
        r = parse_recurrence([txt])
        if r: return r + ('linked file /A%06d/a%06d.txt' % (a, a),)
    return None
