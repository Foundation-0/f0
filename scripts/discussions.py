#!/usr/bin/env python3
"""Snapshot the public forum (GitHub Discussions on this repository) into docs/data/discussions.json.

The forum itself lives on GitHub: https://github.com/Foundation-0/f0/discussions. This script writes the
small index the site's forum page renders: the categories with their thread counts, and the most recently
active threads (title, category, author, replies, state). It never copies the text of a post.

    GH_TOKEN=... python3 scripts/discussions.py        # .github/workflows/discussions.yml runs this

Standard library only. It reads this repository and nothing else, so a private space can never leak into
the public snapshot (the site gate checks every URL in the file as well). The file is rewritten only when
something in it changed, so its "updated" stamp is the time of the last change the snapshot saw, and a
run that finds nothing new commits nothing.
"""
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

OWNER, NAME = 'Foundation-0', 'f0'
FORUM = f'https://github.com/{OWNER}/{NAME}/discussions'
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'data', 'discussions.json')
API = 'https://api.github.com/graphql'
THREADS = 30          # most recently active threads kept in the snapshot
NOTE = ('Index of the public forum (GitHub Discussions on Foundation-0/f0), written by scripts/discussions.py. '
        'Titles and counts only; the posts themselves stay on GitHub. "updated" is when this index last changed.')

META = """query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    hasDiscussionsEnabled
    discussionCategories(first: 25) { nodes { id name slug description isAnswerable } }
  }
}"""

THREADS_Q = """query($owner: String!, $name: String!, $n: Int!) {
  repository(owner: $owner, name: $name) {
    discussions(first: $n, orderBy: {field: UPDATED_AT, direction: DESC}) {
      totalCount
      nodes {
        number title url createdAt updatedAt locked closed isAnswered upvoteCount
        category { slug }
        comments { totalCount }
        author { __typename login url }
      }
    }
  }
}"""


def graphql(query, variables):
    """POST one GraphQL query with the token in GH_TOKEN; return its data or exit with the API's message."""
    token = os.environ.get('GH_TOKEN')
    if not token:
        sys.exit('discussions: set GH_TOKEN (the workflow passes its GITHUB_TOKEN)')
    body = json.dumps({'query': query, 'variables': variables}).encode()
    req = urllib.request.Request(API, data=body, method='POST', headers={
        'Authorization': f'bearer {token}', 'Content-Type': 'application/json',
        'User-Agent': 'foundation0-discussions'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            out = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f'discussions: GitHub answered HTTP {e.code}')
    except (urllib.error.URLError, TimeoutError) as e:
        sys.exit(f'discussions: could not reach GitHub ({e})')
    if out.get('errors'):
        sys.exit('discussions: ' + '; '.join(str(x.get('message')) for x in out['errors']))
    return out['data']


def snapshot():
    meta = graphql(META, {'owner': OWNER, 'name': NAME})['repository']
    snap = {'note': NOTE, 'repository': f'{OWNER}/{NAME}', 'url': FORUM,
            'enabled': bool(meta['hasDiscussionsEnabled']), 'total': 0, 'categories': [], 'threads': []}
    if not snap['enabled']:
        return snap
    cats = meta['discussionCategories']['nodes']
    if cats:   # one count per category, in one request
        fields = ' '.join(f'c{i}: discussions(categoryId: {json.dumps(c["id"])}, first: 1) {{ totalCount }}'
                          for i, c in enumerate(cats))
        counts = graphql(f'query($owner: String!, $name: String!) {{ repository(owner: $owner, name: $name) {{ {fields} }} }}',
                         {'owner': OWNER, 'name': NAME})['repository']
    for i, c in enumerate(cats):
        snap['categories'].append({
            'slug': c['slug'], 'name': c['name'], 'description': c['description'] or '',
            'answerable': bool(c['isAnswerable']), 'count': counts[f'c{i}']['totalCount'],
            'url': f'{FORUM}/categories/{c["slug"]}'})
    d = graphql(THREADS_Q, {'owner': OWNER, 'name': NAME, 'n': THREADS})['repository']['discussions']
    snap['total'] = d['totalCount']
    for t in d['nodes']:
        a = t.get('author')   # None when the account was deleted
        snap['threads'].append({
            'number': t['number'], 'title': t['title'], 'url': t['url'],
            'category': (t.get('category') or {}).get('slug'),
            'author': None if not a else {'login': a['login'], 'url': a['url'], 'agent': a['__typename'] == 'Bot'},
            'created': t['createdAt'], 'updated': t['updatedAt'],
            'comments': t['comments']['totalCount'], 'upvotes': t['upvoteCount'],
            'answered': bool(t.get('isAnswered')), 'locked': bool(t['locked']), 'closed': bool(t.get('closed'))})
    snap['threads'].sort(key=lambda t: (t['updated'], t['number']), reverse=True)
    return snap


def main(out=OUT, now=None):
    snap = snapshot()
    try:
        with open(out, encoding='utf-8') as f:
            old = json.load(f)
    except (OSError, ValueError):
        old = None
    if old is not None and {k: v for k, v in old.items() if k != 'updated'} == snap:
        print(f'discussions: no change ({len(snap["threads"])} threads, enabled={snap["enabled"]})')
        return False
    stamp = now or datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({'updated': stamp, **snap}, f, ensure_ascii=False, indent=1)
        f.write('\n')
    print(f'discussions: wrote {os.path.relpath(out)} ({len(snap["threads"])} of {snap["total"]} threads, '
          f'{len(snap["categories"])} categories, enabled={snap["enabled"]})')
    return True


if __name__ == '__main__':
    main()
