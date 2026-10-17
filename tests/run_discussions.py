#!/usr/bin/env python3
"""Forum index tests (no network): scripts/discussions.py against canned GraphQL answers, and the site
gate's check of docs/data/discussions.json against corrupted copies.

    python3 tests/run_discussions.py
"""
import copy
import importlib.util
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORUM = 'https://github.com/Foundation-0/f0/discussions'
fails = []


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(cond, what):
    print(('PASS: ' if cond else 'FAIL: ') + what)
    if not cond:
        fails.append(what)


CATS = [{'id': 'C1', 'name': 'Claims review', 'slug': 'claims-review', 'description': 'Check a claim.', 'isAnswerable': False},
        {'id': 'C2', 'name': 'Q&A', 'slug': 'q-a', 'description': None, 'isAnswerable': True}]


def thread(n, title, updated, cat, author, **kw):
    return {'number': n, 'title': title, 'url': f'{FORUM}/{n}', 'createdAt': '2026-10-16T09:00:00Z', 'updatedAt': updated,
            'locked': kw.get('locked', False), 'closed': False, 'isAnswered': kw.get('answered', False), 'upvoteCount': 2,
            'category': {'slug': cat}, 'comments': {'totalCount': kw.get('comments', 0)}, 'author': author}


THREADS = [
    thread(3, 'An agent checks PR #1094', '2026-10-16T12:00:00Z', 'claims-review',
           {'__typename': 'Bot', 'login': 'f0-checker', 'url': 'https://github.com/apps/f0-checker'}, comments=4),
    thread(5, '<script>alert(1)</script> and "quotes"', '2026-10-16T15:30:00Z', 'q-a',
           {'__typename': 'User', 'login': 'someone', 'url': 'https://github.com/someone'}, answered=True),
    thread(4, 'From a deleted account', '2026-10-16T12:00:00Z', 'q-a', None, locked=True),
]


def fake_graphql(enabled=True):
    def graphql(query, variables):
        if 'hasDiscussionsEnabled' in query:
            return {'repository': {'hasDiscussionsEnabled': enabled, 'discussionCategories': {'nodes': CATS if enabled else []}}}
        if 'c0: discussions' in query:
            return {'repository': {'c0': {'totalCount': 1}, 'c1': {'totalCount': 7}}}
        if 'orderBy' in query:
            assert variables['n'] == 30
            return {'repository': {'discussions': {'totalCount': 8, 'nodes': copy.deepcopy(THREADS)}}}
        raise AssertionError('unexpected query: ' + query[:60])
    return graphql


def main():
    disc = load('discussions', 'scripts/discussions.py')
    tmp = tempfile.mkdtemp(prefix='f0-forum-')
    out = os.path.join(tmp, 'discussions.json')

    # 1. an open forum
    disc.graphql = fake_graphql(True)
    wrote = disc.main(out=out, now='2026-10-16T16:00:00Z')
    d = json.load(open(out, encoding='utf-8'))
    check(wrote and d['enabled'] and d['total'] == 8, 'open forum: written, enabled, total from GitHub')
    check([c['count'] for c in d['categories']] == [1, 7], 'each category carries its own thread count')
    check(all(c['url'] == f'{FORUM}/categories/{c["slug"]}' for c in d['categories']), 'category links point at this forum')
    check(d['categories'][1]['description'] == '', 'a missing description becomes an empty string')
    check([t['number'] for t in d['threads']] == [5, 4, 3], 'threads: newest activity first, then the higher number')
    by = {t['number']: t for t in d['threads']}
    check(by[3]['author']['agent'] is True and by[5]['author']['agent'] is False, 'a GitHub app is labelled an agent, a user is not')
    check(by[4]['author'] is None and by[4]['locked'] is True, 'a deleted account and a lock are kept')
    check(by[5]['title'] == '<script>alert(1)</script> and "quotes"', 'titles are stored as given (the page escapes them)')
    check('body' not in json.dumps(d), 'no post text is copied')

    # 2. nothing changed -> nothing written, stamp kept
    before = open(out, encoding='utf-8').read()
    wrote = disc.main(out=out, now='2026-10-17T00:00:00Z')
    check(not wrote and open(out, encoding='utf-8').read() == before, 'a run that finds no change leaves the file untouched')

    # 3. a closed forum
    disc.graphql = fake_graphql(False)
    out2 = os.path.join(tmp, 'closed.json')
    disc.main(out=out2, now='2026-10-16T16:00:00Z')
    d2 = json.load(open(out2, encoding='utf-8'))
    check(d2['enabled'] is False and d2['categories'] == [] and d2['threads'] == [], 'closed forum: no categories, no threads')

    # 4. the site gate accepts both, and refuses corrupted copies
    site = load('check_site', 'scripts/check_site.py')
    os.makedirs(os.path.join(tmp, 'data'), exist_ok=True)

    def gate(doc):
        with open(os.path.join(tmp, 'data', 'discussions.json'), 'w', encoding='utf-8') as f:
            json.dump(doc, f)
        site.DOCS = tmp
        del site.errs[:]
        site.check_discussions()
        return list(site.errs)

    check(gate(d) == [], 'gate accepts the open snapshot')
    check(gate(d2) == [], 'gate accepts the closed snapshot')
    check(gate(json.load(open(os.path.join(ROOT, 'docs', 'data', 'discussions.json'), encoding='utf-8'))) == [],
          'gate accepts the committed docs/data/discussions.json')
    probes = {
        'a thread from another (private) repository': lambda x: x['threads'][0].update(url='https://github.com/Foundation-0/members/discussions/5'),
        'a category link to another repository': lambda x: x['categories'][0].update(url='https://github.com/Foundation-0/members/discussions/categories/claims-review'),
        'a thread in an unlisted category': lambda x: x['threads'][0].update(category='board'),
        'an author link off GitHub': lambda x: x['threads'][0]['author'].update(url='https://example.com/u'),
        'threads listed while the forum is closed': lambda x: x.update(enabled=False),
        'a bad timestamp': lambda x: x['threads'][0].update(updated='yesterday'),
        'a forum url that is not this repository': lambda x: x.update(url='https://github.com/someone/else/discussions'),
        'more threads than the total': lambda x: x.update(total=1),
    }
    for what, corrupt in probes.items():
        bad = copy.deepcopy(d)
        corrupt(bad)
        check(bool(gate(bad)), 'gate refuses ' + what)

    print(('all forum checks pass' if not fails else f'{len(fails)} forum check(s) failed'))
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
