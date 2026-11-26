#!/usr/bin/env python3
"""Foundation0 site gate. Standard library only, no network unless --external.

  1  ledger:   docs/data/ledger.json validates against the rules in
               docs/data/ledger.schema.json (types, enums, lengths, dates, ids)
  2  projects: docs/data/projects.json and docs/data/writing.json are well formed; every open project (kind
               "repository") names a listed field, a question, a status, its README commit, its Foundation-0
               repository and that repository's good-first-issue list; docs/data/discussions.json
               (the forum index) is well formed, holds titles and counts only, and every URL in it is one of
               this repository's discussions or a GitHub account
  3  links:    every relative href/src/fetch in docs/**/*.html resolves to a file
               inside docs/, and every same-page #anchor exists
  4  pages:    every page has <title>, a description, lang, a viewport, and an og:image that
               resolves to a file inside docs/ (relative, or absolute under SITE); og:url and
               rel=canonical, where present, are the page's own address under SITE; a relative og:image
               or a missing og:url is a warning (share cards need absolute URLs)
  5  scripts:  no third-party script origins (the site must run with no CDN)
  6  record:   every ledger/#<id> link in pages, scripts and data names a ledger.json id; every key of the
               Ledger page's CREDIT map is a ledger id; founding members' items carry foundation0_note and
               known foundation0_members; Home and the Ledger state the same role-over-time numbers

Usage: python3 scripts/check_site.py [--external]   (exit 0 = clean)
  --external also checks every external URL in the pages, page scripts and data files (*.json): any 2xx
  passes; doi.org links resolve through api.crossref.org, then api.datacite.org; links into this
  repository (github.com/Foundation-0/f0/blob|tree/main/...) are checked against the local
  checkout; preconnect and dns-prefetch hints are skipped.
"""
import datetime
import html.parser
import json
import os
import posixpath
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
SITE = 'https://fdn0.org/'   # the published site (GitHub Pages, at its own domain; foundation-0.github.io/f0/ redirects here)
# The original frontier-math site, kept as it was: links are checked, page metadata is not.
ARCHIVE = 'legacy-site/'
THIS_REPO = 'https://github.com/Foundation-0/f0/'
errs = []
warns = []


def err(check, msg):
    errs.append(f'{check}: {msg}')


def warn(check, msg):
    warns.append(f'{check}: {msg}')


# ---------------- 1 ledger -------------------------------------------------------
def load(rel):
    path = os.path.join(DOCS, rel)
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        err('json', f'{rel}: {e}')
        return None


def valid_date(s):
    for fmt in ('%Y-%m-%d', '%Y-%m', '%Y'):
        try:
            datetime.datetime.strptime(s, fmt)
            return True
        except (TypeError, ValueError):
            pass
    return False


def check_value(where, v, spec):
    """Validate v against the small JSON-Schema subset ledger.schema.json uses."""
    t = spec.get('type')
    types = t if isinstance(t, list) else [t]
    pytypes = {'string': str, 'integer': int, 'boolean': bool, 'array': list,
               'object': dict, 'null': type(None)}
    if t and not any(isinstance(v, pytypes[x]) and not (x == 'integer' and isinstance(v, bool))
                     for x in types):
        err('ledger', f'{where}: expected {t}, got {type(v).__name__}')
        return
    if 'enum' in spec and v not in spec['enum']:
        err('ledger', f'{where}: {v!r} not in {spec["enum"]}')
    if isinstance(v, str):
        if 'minLength' in spec and len(v) < spec['minLength']:
            err('ledger', f'{where}: shorter than {spec["minLength"]}')
        if 'maxLength' in spec and len(v) > spec['maxLength']:
            err('ledger', f'{where}: {len(v)} chars > {spec["maxLength"]}')
        if 'pattern' in spec and not re.search(spec['pattern'], v):
            err('ledger', f'{where}: {v!r} does not match {spec["pattern"]}')
    if isinstance(v, int) and not isinstance(v, bool):
        if 'minimum' in spec and v < spec['minimum']:
            err('ledger', f'{where}: {v} < {spec["minimum"]}')
        if 'maximum' in spec and v > spec['maximum']:
            err('ledger', f'{where}: {v} > {spec["maximum"]}')
    if isinstance(v, list):
        if 'minItems' in spec and len(v) < spec['minItems']:
            err('ledger', f'{where}: fewer than {spec["minItems"]} items')
        if 'maxItems' in spec and len(v) > spec['maxItems']:
            err('ledger', f'{where}: more than {spec["maxItems"]} items')
        for i, x in enumerate(v):
            check_value(f'{where}[{i}]', x, spec.get('items', {}))
    if isinstance(v, dict):
        check_object(where, v, spec)


def check_object(where, obj, spec):
    props = spec.get('properties', {})
    for k in spec.get('required', []):
        if k not in obj:
            err('ledger', f'{where}: missing {k}')
    if spec.get('additionalProperties') is False:
        for k in obj:
            if k not in props:
                err('ledger', f'{where}: unexpected field {k}')
    for k, v in obj.items():
        if k in props:
            check_value(f'{where}.{k}', v, props[k])


def words(s):
    return len(s.split())


_logins = None


def member_logins():
    global _logins
    if _logins is None:
        d = load('data/members.json') or {}
        _logins = {m.get('login') for m in d.get('members', [])}
    return _logins


def check_ledger():
    schema = load('data/ledger.schema.json')
    ledger = load('data/ledger.json')
    if schema is None or ledger is None:
        return
    items = ledger.get('milestones') if isinstance(ledger, dict) else None
    if not isinstance(items, list) or not items:
        err('ledger', 'ledger.json must be {"milestones": [...]} and non-empty')
        return
    item_spec = schema['properties']['milestones']['items']
    seen = set()
    today = datetime.date.today().isoformat()
    for i, m in enumerate(items):
        where = f'milestones[{i}]({m.get("id", "?") if isinstance(m, dict) else "?"})'
        if not isinstance(m, dict):
            err('ledger', f'{where}: not an object')
            continue
        check_object(where, m, item_spec)
        mid = m.get('id')
        if mid in seen:
            err('ledger', f'{where}: duplicate id')
        seen.add(mid)
        d = m.get('date', '')
        if not valid_date(d):
            err('ledger', f'{where}: bad date {d!r}')
        elif d > today:
            err('ledger', f'{where}: date {d} is in the future')
        if words(m.get('summary', '')) > 60:
            err('ledger', f'{where}: summary over 60 words')
        if words(m.get('why_it_matters', '')) > 40:
            err('ledger', f'{where}: why_it_matters over 40 words')
        if m.get('contested') and not m.get('contested_note'):
            err('ledger', f'{where}: contested without contested_note')
        for s in m.get('sources', []):
            if not str(s.get('url', '')).startswith('https://'):
                err('ledger', f'{where}: source url must be https: {s.get("url")}')
        page = m.get('page')
        if page and not resolve_internal('data/ledger.json', '../' + page.lstrip('/')):
            err('ledger', f'{where}: page {page} does not exist')
        if m.get('foundation0'):
            if not m.get('foundation0_note'):
                err('ledger', f'{where}: foundation0 item without foundation0_note (who did what)')
            unknown = [x for x in m.get('foundation0_members', []) if x not in member_logins()]
            if not m.get('foundation0_members') or unknown:
                err('ledger', f'{where}: foundation0_members must list data/members.json logins (unknown: {unknown})')
    dates = [m.get('date', '') for m in items if isinstance(m, dict)]
    if dates != sorted(dates):
        err('ledger', 'milestones must be sorted by date ascending')


# ---------------- 2 projects / writing -------------------------------------------
def check_lists():
    for rel, key, need in (('data/projects.json', 'projects', ('slug', 'title', 'kind', 'links')),
                           ('data/writing.json', 'posts', ('title', 'url', 'date'))):
        data = load(rel)
        if data is None:
            continue
        rows = data.get(key) if isinstance(data, dict) else None
        if not isinstance(rows, list) or not rows:
            err('lists', f'{rel}: expected non-empty "{key}" array')
            continue
        for i, r in enumerate(rows):
            for k in need:
                if k not in r:
                    err('lists', f'{rel}[{i}]: missing {k}')
            if 'date' in r and not valid_date(r['date']):
                err('lists', f'{rel}[{i}]: bad date {r["date"]!r}')


def check_repositories():
    """Open projects in data/projects.json (kind "repository"): one Foundation-0 repository each, in a field the file
    lists, with the question, the status as its README states it, the README commit that status was read at, and
    links to the repository and to its open good-first-issue list."""
    rel = 'data/projects.json'
    d = load(rel)
    if not isinstance(d, dict):
        return
    fields = d.get('fields') or []
    names = [f.get('name') for f in fields if isinstance(f, dict)]
    for f in fields:
        hub = f.get('hub') if isinstance(f, dict) else None
        if not isinstance(f, dict) or not f.get('name') or not (hub is None or re.fullmatch(r'[a-z0-9][a-z0-9-]*', str(hub))):
            err('lists', f'{rel}: fields entries need a name and a hub (a Foundation-0 repository name, or null): {f!r}')
    slugs = [r.get('slug') for r in d.get('projects', []) if isinstance(r, dict)]
    if len(slugs) != len(set(slugs)):
        err('lists', f'{rel}: a slug is used twice')
    for r in d.get('projects', []):
        if not isinstance(r, dict) or r.get('kind') != 'repository':
            continue
        slug = str(r.get('slug', ''))
        where = f'{rel}: repository {slug}'
        for k in ('field', 'question', 'status', 'source'):
            if not isinstance(r.get(k), str) or not r[k].strip():
                err('lists', f'{where}: missing {k}')
        if r.get('field') not in names:
            err('lists', f'{where}: field {r.get("field")!r} is not one of the fields listed in {rel}')
        if not re.fullmatch(r'README\.md at [0-9a-f]{7,40}', str(r.get('source', ''))):
            err('lists', f'{where}: source must read "README.md at <commit>"')
        home = 'https://github.com/Foundation-0/' + slug
        urls = [l.get('url') for l in r.get('links', []) if isinstance(l, dict)]
        if not urls or urls[0] != home:
            err('lists', f'{where}: its first link must be {home}')
        if home + '/issues?q=is%3Aopen+label%3A%22good+first+issue%22' not in urls:
            err('lists', f'{where}: needs a link to its open good-first-issue list')
        if r.get('page') and not resolve_internal('index.html', r['page']):
            err('lists', f'{where}: page {r["page"]} does not exist')


def check_discussions():
    """data/discussions.json indexes this repository's public forum and nothing else: every URL in it must be
    one of this repository's discussion pages or a GitHub account, so a private space can never leak into it,
    and it holds titles and counts only (no field outside the ones listed here)."""
    rel = 'data/discussions.json'
    d = load(rel)
    if d is None:
        return
    forum = THIS_REPO + 'discussions'
    stamp = re.compile(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ')
    account = re.compile(r'https://github\.com/(?:apps/)?[A-Za-z0-9][A-Za-z0-9-]*')
    login = re.compile(r'[A-Za-z0-9][A-Za-z0-9-]*(?:\[bot\])?')

    def count(x):
        return isinstance(x, int) and not isinstance(x, bool) and x >= 0

    def extra(obj, allowed, where):
        unknown = sorted(set(obj) - allowed)
        if unknown:
            err('forum', f'{where}: fields not allowed in the index: {unknown}')

    if not isinstance(d, dict):
        err('forum', f'{rel}: expected an object')
        return
    extra(d, {'updated', 'note', 'repository', 'url', 'enabled', 'total', 'categories', 'threads'}, rel)
    if d.get('url') != forum:
        err('forum', f'{rel}: url must be {forum}')
    if not stamp.fullmatch(str(d.get('updated', ''))):
        err('forum', f'{rel}: updated must be a UTC timestamp like 2026-10-16T18:00:00Z')
    cats, threads = d.get('categories'), d.get('threads')
    if not isinstance(d.get('enabled'), bool) or not isinstance(cats, list) or not isinstance(threads, list):
        err('forum', f'{rel}: needs enabled (true/false), categories [] and threads []')
        return
    if not d['enabled'] and (cats or threads):
        err('forum', f'{rel}: lists categories or threads while the forum is not enabled')
    if not count(d.get('total')) or d['total'] < len(threads):
        err('forum', f'{rel}: total must be a whole number, at least the number of threads listed')
    slugs = set()
    for i, c in enumerate(cats):
        slug = c.get('slug') if isinstance(c, dict) else None
        if not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]*', slug):
            err('forum', f'{rel}: categories[{i}] has a bad slug {slug!r}')
            continue
        slugs.add(slug)
        extra(c, {'slug', 'name', 'description', 'answerable', 'count', 'url'}, f'{rel}: category {slug}')
        if c.get('url') != f'{forum}/categories/{slug}':
            err('forum', f'{rel}: category {slug} has url {c.get("url")!r}, not this forum\'s')
        if not isinstance(c.get('name'), str) or not c['name'] or not count(c.get('count')) or not isinstance(c.get('answerable'), bool):
            err('forum', f'{rel}: category {slug} needs a name, a count and answerable (true/false)')
    for i, t in enumerate(threads):
        if not isinstance(t, dict) or not count(t.get('number')) or not t['number']:
            err('forum', f'{rel}: threads[{i}] needs a number')
            continue
        where = f'{rel}: thread #{t["number"]}'
        extra(t, {'number', 'title', 'url', 'category', 'author', 'created', 'updated', 'comments', 'upvotes',
                  'answered', 'locked', 'closed'}, where)
        if t.get('url') != f'{forum}/{t["number"]}':
            err('forum', f'{where} has url {t.get("url")!r}, not this forum\'s')
        if not isinstance(t.get('title'), str) or not t['title'].strip():
            err('forum', f'{where} has no title')
        if t.get('category') not in slugs:
            err('forum', f'{where} names category {t.get("category")!r}, which is not listed')
        for k in ('created', 'updated'):
            if not stamp.fullmatch(str(t.get(k, ''))):
                err('forum', f'{where}: bad {k} {t.get(k)!r}')
        for k in ('comments', 'upvotes'):
            if not count(t.get(k)):
                err('forum', f'{where}: {k} must be a whole number')
        for k in ('answered', 'locked', 'closed'):
            if not isinstance(t.get(k), bool):
                err('forum', f'{where}: {k} must be true or false')
        a = t.get('author')
        if a is not None and not (isinstance(a, dict) and set(a) == {'login', 'url', 'agent'}
                                  and login.fullmatch(str(a['login'])) and account.fullmatch(str(a['url']))
                                  and isinstance(a['agent'], bool)):
            err('forum', f'{where}: author needs a GitHub login, its github.com address and agent (true/false)')
    nums = [t.get('number') for t in threads if isinstance(t, dict)]
    if len(nums) != len(set(nums)):
        err('forum', f'{rel}: a thread is listed twice')
    order = [(str(t.get('updated')), t.get('number')) for t in threads if isinstance(t, dict) and count(t.get('number'))]
    if order != sorted(order, reverse=True):
        err('forum', f'{rel}: threads must run from the most recently active, as the page shows them')


# ---------------- 3 links, 4 pages, 5 scripts ------------------------------------
class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.ids, self.scripts = [], set(), []
        self.title = self.desc = self.viewport = self.lang = False
        self.og_images = []
        self.og_url = self.canonical = None
        self.hints = set()
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.add(a['id'])
        if tag == 'a' and 'name' in a:
            self.ids.add(a['name'])
        if tag == 'html' and a.get('lang'):
            self.lang = True
        if tag == 'title':
            self._in_title = True
        if tag == 'meta' and a.get('name') == 'description' and a.get('content'):
            self.desc = True
        if tag == 'meta' and a.get('name') == 'viewport':
            self.viewport = True
        if tag == 'meta' and a.get('property') == 'og:image' and a.get('content'):
            self.og_images.append(a['content'])
        if tag == 'meta' and a.get('property') == 'og:url' and a.get('content'):
            self.og_url = a['content']
        if tag == 'link' and a.get('href') and 'canonical' in (a.get('rel') or '').split():
            self.canonical = a['href']
        if tag == 'link' and a.get('href') and set((a.get('rel') or '').split()) & {'preconnect', 'dns-prefetch'}:
            self.hints.add(a['href'])
        for attr in ('href', 'src', 'data-src', 'poster'):
            if a.get(attr):
                self.refs.append((tag, a[attr]))
        if tag == 'script' and a.get('src'):
            self.scripts.append(a['src'])

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False

    def handle_data(self, data):
        if self._in_title and data.strip():
            self.title = True


def resolve_internal(from_rel, ref):
    """Path inside docs/ that ref points to from the page at from_rel, or None."""
    ref = ref.split('#', 1)[0].split('?', 1)[0]
    if not ref:
        return from_rel
    target = posixpath.normpath(posixpath.join(posixpath.dirname(from_rel), ref))
    if target.startswith('..'):
        return None
    full = os.path.join(DOCS, target)
    if os.path.isdir(full):
        full = os.path.join(full, 'index.html')
    return target if os.path.isfile(full) else None


EXTERNAL = re.compile(r'^(?:[a-z][a-z0-9+.-]*:|//)', re.I)


def html_pages():
    for dirpath, _, files in os.walk(DOCS):
        for fn in sorted(files):
            if fn.endswith('.html'):
                yield posixpath.relpath(os.path.join(dirpath, fn), DOCS).replace(os.sep, '/')


def check_pages(external_urls):
    pages = sorted(html_pages())
    if 'index.html' not in pages:
        err('pages', 'docs/index.html (home) is missing')
    ids_by_page = {}
    parsed = {}
    for rel in pages:
        p = Page()
        with open(os.path.join(DOCS, rel), encoding='utf-8') as f:
            src = f.read()
        p.feed(src)
        parsed[rel] = (p, src)
        ids_by_page[rel] = p.ids
    for rel, (p, src) in parsed.items():
        if rel.startswith(ARCHIVE):
            check_refs(rel, p, src, ids_by_page, external_urls)
            continue
        for flag, what in ((p.title, '<title>'), (p.desc, 'meta description'),
                           (p.viewport, 'meta viewport'), (p.lang, '<html lang>')):
            if not flag:
                err('pages', f'{rel}: missing {what}')
        if not p.og_images:
            err('pages', f'{rel}: missing og:image')
        for og in p.og_images:
            if og.startswith(SITE):
                if resolve_internal('index.html', og[len(SITE):]) is None:
                    err('pages', f'{rel}: og:image {og} does not map to a file in docs/')
            elif EXTERNAL.match(og):
                err('pages', f'{rel}: og:image {og} is not on this site ({SITE})')
            elif resolve_internal(rel, og) is None:
                err('pages', f'{rel}: og:image {og} does not resolve to a file in docs/')
            else:
                warn('pages', f'{rel}: og:image {og} is relative; share cards need {SITE}...')
        if not p.og_url and 'noindex' not in src:
            warn('pages', f'{rel}: no og:url')
        # A share card or canonical link must name this page at the published address. 404.html is
        # served at any missing path, so it names home.
        own = SITE + ('' if rel in ('index.html', '404.html') else rel[:-len('index.html')] if rel.endswith('/index.html') else rel)
        for what, u in (('og:url', p.og_url), ('canonical', p.canonical)):
            if u and u != own:
                err('pages', f'{rel}: {what} {u} is not this page\'s address {own}')
        check_refs(rel, p, src, ids_by_page, external_urls)


def check_refs(rel, p, src, ids_by_page, external_urls):
    """Links, anchors and script origins of one page."""
    refs = [r for _, r in p.refs if r not in p.hints]
    refs += re.findall(r"""fetch\(\s*['"]([^'"$`]+)['"]""", src)
    for ref in refs:
        if ref.startswith(('mailto:', 'tel:', 'data:', 'javascript:')):
            continue
        if EXTERNAL.match(ref):
            if ref.startswith('http'):
                external_urls.add(ref)
            continue
        if '${' in ref or '{{' in ref:
            continue
        target = resolve_internal(rel, ref)
        if target is None:
            err('links', f'{rel}: broken link {ref}')
            continue
        if '#' in ref:
            frag = ref.split('#', 1)[1]
            if frag and target.endswith('.html') and target in ids_by_page \
                    and frag not in ids_by_page[target]:
                err('links', f'{rel}: {ref} -> no id "{frag}" in {target}')
    for s in p.scripts:
        if EXTERNAL.match(s):
            err('scripts', f'{rel}: third-party script {s} (vendor it under docs/assets/)')


# ---------------- 6 record consistency -------------------------------------------
def text_files():
    for dirpath, _, files in os.walk(DOCS):
        for fn in sorted(files):
            if fn.endswith(('.html', '.js', '.json')):
                full = os.path.join(dirpath, fn)
                yield posixpath.relpath(full, DOCS).replace(os.sep, '/'), full


def check_record():
    led = load('data/ledger.json') or {}
    ids = {m.get('id') for m in led.get('milestones', [])}
    for rel, full in text_files():
        if rel == 'data/ledger.json':
            continue
        with open(full, encoding='utf-8') as f:
            src = f.read()
        for mid in sorted(set(re.findall(r'ledger/#([a-z0-9][a-z0-9-]*[a-z0-9])', src))):
            if mid not in ids:
                err('record', f'{rel}: link ledger/#{mid} names no ledger.json id')
    page_js = os.path.join(DOCS, 'ledger', 'page.js')
    if os.path.isfile(page_js):
        with open(page_js, encoding='utf-8') as f:
            m = re.search(r'var CREDIT = \{(.*?)\};', f.read(), re.S)
        for key in re.findall(r"'([a-z0-9-]+)'\s*:", m.group(1) if m else ''):
            if key not in ids:
                err('record', f'ledger/page.js: CREDIT key {key} is not a ledger.json id (stale credit line)')

    def insight(rel, name):
        try:
            with open(os.path.join(DOCS, rel), encoding='utf-8') as f:
                m = re.search(rf'<!--prerender:{name}-->(.*?)<!--/prerender:{name}-->', f.read(), re.S)
        except OSError:
            return None
        return m and m.group(1)
    home, ledg = insight('index.html', 'role-insight-p'), insight('ledger/index.html', 'insight-role-p')
    if home and ledg:
        nums = lambda t: (re.findall(r'\d{4}(?:–\d{2,4})?', t), re.findall(r'\d+%', t))
        if nums(home) != nums(ledg):
            err('record', f'Home and the Ledger state different role-over-time numbers: {nums(home)} vs {nums(ledg)} (both must use F0.rolePeriods)')


# ---------------- --external ---------------------------------------------------------
def fetch_code(u, timeout=20):
    req = urllib.request.Request(u, method='GET', headers={'User-Agent': 'foundation0-linkcheck', 'Accept': 'application/json, text/html;q=0.9, */*;q=0.5'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:  # noqa: BLE001 - report any network failure
        return repr(e)[:60]


def ok(code):
    return isinstance(code, int) and (200 <= code < 300 or code in (301, 302, 303, 307, 308))


def check_url(u):
    if u.startswith(SITE):                            # this site: the file must exist in docs/ (it may not be published yet)
        return 200 if resolve_internal('index.html', u[len(SITE):]) else 'not in docs/'
    if u.startswith(THIS_REPO):                       # this repository: check the local checkout
        m = re.match(re.escape(THIS_REPO) + r'(?:blob|tree)/[^/]+/(.+?)(?:[?#].*)?$', u)
        if m:
            return 200 if os.path.exists(os.path.join(ROOT, m.group(1))) else 'not in this checkout'
    m = re.match(r'https?://(?:dx\.)?doi\.org/(10\.[^?#]+)', u)
    if m:                                             # DOIs: the registries answer reliably, doi.org itself often does not
        doi = urllib.parse.quote(m.group(1), safe='/()')
        codes = [fetch_code(api + doi) for api in ('https://api.crossref.org/works/', 'https://api.datacite.org/dois/')]
        if any(ok(c) for c in codes):
            return 200
        if all(c == 404 for c in codes):
            return 'DOI unknown to Crossref and DataCite'
        warn('external', f'{u} -> registries answered {codes} (could not check)')
        return 200
    code = fetch_code(u)
    if code in (403, 429) or not isinstance(code, int):  # bot walls, rate limits, timeouts, proxy errors: unknown, not dead
        warn('external', f'{u} -> {code} (could not check)')
        return 200
    m = re.match(r'https://github\.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$', u)
    if not ok(code) and m:                            # a file on a branch: try its raw copy
        code = fetch_code('https://raw.githubusercontent.com/%s/%s/%s/%s' % m.groups())
    return code


def collect_urls(urls):
    for rel, full in text_files():
        if rel in ('feed.json', 'chart-data.json'):    # pipeline outputs: checked by the κ pipeline
            continue
        with open(full, encoding='utf-8') as f:
            src = f.read()
        for u in re.findall(r'https?://[^\s"\'<>`\\]+', src):
            u = u.rstrip('.,;:')
            while u.endswith(')') and u.count(')') > u.count('('):   # "(see https://x)" but keep DOIs like 10.1016/S0140-6736(20)30183-5
                u = u[:-1].rstrip('.,;:')
            host = urllib.parse.urlsplit(u).netloc
            if '${' in u or '{' in u or '.' not in host or u.endswith(('/', '=')) and 'api.' in u:
                continue
            if re.search(r'/(blob|tree|commit|commits|pull|issues)/?$', u):   # a prefix that page code completes
                continue
            if re.match(r'https://fonts\.(googleapis|gstatic)\.com/?$', u) or re.match(r'https?://(www\.w3\.org/\d{4}/|json-schema\.org/)', u):
                continue                              # font hosts and XML/JSON namespace names are not links
            urls.add(u)


def check_external(urls):
    for u in sorted(urls):
        code = check_url(u)
        if not ok(code):
            err('external', f'{u} -> {code}')


def main():
    check_ledger()
    check_lists()
    check_repositories()
    check_discussions()
    urls = set()
    check_pages(urls)
    check_record()
    if '--external' in sys.argv:
        led = load('data/ledger.json') or {}
        for m in led.get('milestones', []):
            urls.update(s['url'] for s in m.get('sources', []))
        collect_urls(urls)
        check_external(urls)
    if warns:
        for w in warns:
            print('WARN', w)
        print()
    if errs:
        for e in errs:
            print('FAIL', e)
        print(f'\n{len(errs)} problem(s)')
        sys.exit(1)
    print('site gate: all checks pass')


if __name__ == '__main__':
    main()
