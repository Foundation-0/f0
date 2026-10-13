#!/usr/bin/env python3
"""Foundation0 site gate. Standard library only, no network unless --external.

  1  ledger:   docs/data/ledger.json validates against the rules in
               docs/data/ledger.schema.json (types, enums, lengths, dates, ids)
  2  projects: docs/data/projects.json and docs/data/writing.json are well formed
  3  links:    every relative href/src/fetch in docs/**/*.html resolves to a file
               inside docs/, and every same-page #anchor exists
  4  pages:    every page has <title>, a description, lang, and a viewport
  5  scripts:  no third-party script origins (the site must run with no CDN)

Usage: python3 scripts/check_site.py [--external]   (exit 0 = clean)
  --external also HEAD-checks every external URL in the data files and pages.
"""
import datetime
import html.parser
import json
import os
import posixpath
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, 'docs')
errs = []


def err(check, msg):
    errs.append(f'{check}: {msg}')


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


# ---------------- 3 links, 4 pages, 5 scripts ------------------------------------
class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs, self.ids, self.scripts = [], set(), []
        self.title = self.desc = self.viewport = self.lang = False
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
        for flag, what in ((p.title, '<title>'), (p.desc, 'meta description'),
                           (p.viewport, 'meta viewport'), (p.lang, '<html lang>')):
            if not flag:
                err('pages', f'{rel}: missing {what}')
        refs = [r for _, r in p.refs]
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


def check_external(urls):
    for u in sorted(urls):
        req = urllib.request.Request(u, method='GET', headers={'User-Agent': 'foundation0-linkcheck'})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception as e:  # noqa: BLE001 - report any network failure
            code = repr(e)[:60]
        if code != 200 and code not in (301, 302, 403, 429):
            err('external', f'{u} -> {code}')


def main():
    check_ledger()
    check_lists()
    urls = set()
    check_pages(urls)
    if '--external' in sys.argv:
        led = load('data/ledger.json') or {}
        for m in led.get('milestones', []):
            urls.update(s['url'] for s in m.get('sources', []))
        check_external(urls)
    if errs:
        for e in errs:
            print('FAIL', e)
        print(f'\n{len(errs)} problem(s)')
        sys.exit(1)
    print('site gate: all checks pass')


if __name__ == '__main__':
    main()
