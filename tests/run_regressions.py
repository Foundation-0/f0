#!/usr/bin/env python3
"""Regression tests for Shaka QA findings F1-F5 (local, no network writes).

Each finding gets a focused test:
  F1  the dashboard's links resolve inside the Pages docroot (docs/ only), and the
      docroot copy is byte-identical to the authoritative root schema.
  F2  per-(pr, head_sha) identity/uniqueness invariant: duplicate composite keys
      in the ledger (records.json) must NOT propagate to feed/chart (emit raises),
      and the gate rejects a feed with the same composite key twice, while
      distinct PRs sharing one head_sha remain legal (composite, NOT global).
  F3  force-push supersession: an advanced head marks the old row stale + superseded
      and excludes it from feed.records[]/chart; a reversion to that head re-resolves
      it (quarantine lifted); state is deterministic across two identical runs.
  F4  verify.certificate_sha256 is RECOMPUTED over the authoritative certificate
      artifact bytes (data/certificate.artifact.json), and feed.selected_result
      binds the actual mirror bytes; a nibble-flip or an unverifiable fake digest
      no longer passes when the authoritative bytes are present.
  F5  the parser rejects non-construction frames (model / ceiling / pricing model /
      no-new-k / would-need / hypothetical) as claims, while keeping valid
      construction forms (golden 419/425/431/433 + a real #442 live form).

Usage: python3 tests/run_regressions.py   (exit 0 = every regression passes)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The live kappa-race dashboard (moved from docs/index.html when the site became Foundation0).
DASHBOARD = 'research/integer-multiplication/live/index.html'
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from fetch import (parse_kappa, build_record, merge_records, emit_views,
                   DOC_FRAME_RE)  # noqa: E402

FAILS = []


def check(name, cond, detail=''):
    if cond:
        print(f"ok  {name}")
    else:
        FAILS.append(name)
        print(f"FAIL {name}: {detail}")


def run_gate(root):
    return subprocess.run([sys.executable, os.path.join(root, 'scripts', 'gate.py'),
                           '--root', root], capture_output=True, text=True)


# ---------------- Fixtures ------------------------------------------------------
def make_pr(num, head, title, body, updated='2026-10-11T00:00:00Z', draft=False):
    return {
        "number": num, "title": title, "body": body, "draft": draft,
        "updated_at": updated, "html_url": f"https://github.com/x/y/pull/{num}",
        "head": {"sha": head, "repo": {"html_url": "https://github.com/x/y"}},
        "base": {"sha": "0" * 40},
    }


CERT_KAPPA = ("90446448750933", "125000000000000000")
CERT_DEC = "0.000723571590007464"
CERT_SHA = "6a457a34b4db57417e5b253cf1c169da2bd6aff4c21363a31fd85dc931d49589"


def _snapshot_root(feed_fn=None):
    """Copy the live repo to a temp dir and let a test mutate feed.json."""
    td = tempfile.mkdtemp()
    dst = os.path.join(td, 'repo')
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns('.git', '__pycache__'))
    if feed_fn:
        feed_path = os.path.join(dst, 'docs', 'feed.json')
        feed = json.load(open(feed_path))
        feed_fn(feed)
        with open(feed_path, 'w') as f:
            json.dump(feed, f, indent=2, sort_keys=True, ensure_ascii=False)
            f.write('\n')
    return dst


# ---------------- F1 -------------------------------------------------------------
def test_f1_docroot():
    root = _snapshot_root()
    import functools
    import http.server
    import threading
    import urllib.error
    import urllib.request
    docroot = os.path.join(root, 'docs')
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=docroot)
    httpd = http.server.HTTPServer(('127.0.0.1', 0), handler)
    port = httpd.server_address[1]
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    import posixpath
    import re
    def serves(rel):
        try:
            return urllib.request.urlopen(f'http://127.0.0.1:{port}/{rel}').status
        except urllib.error.HTTPError as e:
            return e.code
    try:
        for rel in ('index.html', 'feed.json', 'chart-data.json', 'feed.schema.json',
                    DASHBOARD, posixpath.join(posixpath.dirname(DASHBOARD), 'method.html')):
            code = serves(rel)
            check(f"F1 docroot serves {rel}", code == 200, f"got {code}")
        # every relative link and fetch in the dashboard must stay inside the docroot
        # and resolve (the old bug: ../feed.schema.json escaped it from docs/index.html)
        html = open(os.path.join(docroot, DASHBOARD)).read()
        refs = re.findall(r'(?:href|src)="([^"#:${}]+)"', html)
        refs += re.findall(r"fetch\('([^']+)'\)", html)
        check("F1 dashboard links feed.schema.json", any(r.endswith('feed.schema.json') for r in refs))
        base = posixpath.dirname(DASHBOARD)
        for ref in refs:
            target = posixpath.normpath(posixpath.join(base, ref))
            check(f"F1 {ref} stays inside docroot", not target.startswith('..'), target)
            code = serves(target)
            check(f"F1 {ref} resolves", code == 200, f"{target} got {code}")
    finally:
        httpd.shutdown()
    # byte-identical schema copy
    with open(os.path.join(root, 'feed.schema.json'), 'rb') as a, \
         open(os.path.join(root, 'docs', 'feed.schema.json'), 'rb') as b:
        check("F1 docroot schema == root schema", a.read() == b.read())


# ---------------- F2 -------------------------------------------------------------
def test_f2_composite_uniqueness():
    # (a) emit path rejects a records list with a duplicated (pr, head_sha)
    base = load_sample_records()
    rec = dict(base[0])
    dup = list(base) + [rec]
    raised = False
    try:
        emit_views(dup, None, '0' * 40, '2026-10-11T00:00:00Z')
    except ValueError:
        raised = True
    check("F2 emit raises on duplicate (pr, head_sha)", raised)

    # (b) gate rejects a feed whose records[] holds the same key twice
    def corrupt(feed):
        r = feed['records'][0]
        dup = dict(r)
        feed['records'].append(dup)
    root = _snapshot_root(corrupt)
    p = run_gate(root)
    check("F2 gate blocks duplicate composite key",
          p.returncode != 0, p.stdout[:200])

    # (c) distinct PRs sharing one head_sha is LEGAL (composite invariant, not
    # global head uniqueness)
    def uncorrupt(feed):
        h = feed['records'][0]['head_sha']
        seen_orig = [(r['pr'], r['head_sha']) for r in feed['records']]
        # pick two distinct pr rows and force the same head_sha
        for r in feed['records'][:2]:
            r['head_sha'] = h
        feed['records'][:2] = feed['records'][:2]
    root = _snapshot_root(uncorrupt)
    # rebuild chart from the mutated records via the real emit path (like QA)
    records = json.load(open(os.path.join(root, 'data', 'records.json')))['records']
    # Make the whole repo mutually coherent by re-emitting views from records.json
    recs = json.load(open(os.path.join(root, 'data', 'records.json')))['records']
    h = recs[0]['head_sha']
    for r in recs[:2]:
        r['head_sha'] = h
    feed = json.load(open(os.path.join(root, 'docs', 'feed.json')))
    cert = feed['selected_result']
    views = emit_views(recs, cert, feed['upstream_main_sha'], feed['generated_at'])
    with open(os.path.join(root, 'docs', 'feed.json'), 'w') as f:
        json.dump(views[0], f, indent=2, sort_keys=True, ensure_ascii=False); f.write('\n')
    with open(os.path.join(root, 'docs', 'chart-data.json'), 'w') as f:
        json.dump(views[1], f, indent=2, sort_keys=True, ensure_ascii=False); f.write('\n')
    with open(os.path.join(root, 'data', 'records.json'), 'w') as f:
        json.dump({'records': recs}, f, indent=2, sort_keys=True, ensure_ascii=False); f.write('\n')
    p = run_gate(root)
    check("F2 shared head across distinct PRs is NOT blocked (composite key)",
          p.returncode == 0, p.stdout[:200])


def load_sample_records():
    return json.load(open(os.path.join(ROOT, 'data', 'records.json')))['records']


# ---------------- F3 -------------------------------------------------------------
def test_f3_supersede_and_resolve():
    head_a = 'a' * 40
    head_b = 'b' * 40
    _claim_body = ("This construction claims conditional kappa = "
                   "560432476129139/500000000000000000 = 0.001120864952258278.")
    pulls_v1 = [make_pr(9001, head_a, "Conditional kappa",
                        _claim_body, updated='2026-10-11T00:00:00Z')]
    recs1, stats1 = merge_records([], pulls_v1, '2026-10-11T00:00:00Z',
                                  CERT_KAPPA, CERT_DEC, CERT_SHA)
    check("F3 v1 creates clean row", recs1 and not recs1[0].get('stale'))
    # force-push: head advances to B
    pulls_v2 = [make_pr(9001, head_b, "Conditional kappa",
                        _claim_body, updated='2026-10-11T01:00:00Z')]
    recs2, stats2 = merge_records(recs1, pulls_v2, '2026-10-11T01:00:00Z',
                                  CERT_KAPPA, CERT_DEC, CERT_SHA)
    by_key = {(r['pr'], r['head_sha']): r for r in recs2}
    old = by_key[(9001, head_a)]
    new = by_key[(9001, head_b)]
    check("F3 old row marked stale on head advance",
          old.get('stale') is True and old.get('stale_reason') == 'superseded-head')
    check("F3 new row clean", new.get('stale') is not True)
    check("F3 superseded_by recorded",
          old.get('superseded_by') == head_b, str(old))
    # stale row excluded from feed.records[]/chart
    feed, chart = emit_views(recs2, None, '0' * 40, '2026-10-11T01:00:00Z')
    check("F3 stale row excluded from feed.records[]",
          all((r['pr'], r['head_sha']) != (9001, head_a) for r in feed['records']))
    check("F3 stale row surfaced under quarantined",
          any(r.get('pr') == 9001 and r['head_sha'] == head_a for r in feed['quarantined']))
    # reversion: head returns to A -> row A re-resolved (quarantine lifted)
    pulls_rev = [make_pr(9001, head_a, "Conditional kappa",
                         _claim_body, updated='2026-10-11T02:00:00Z')]
    recs3, stats3 = merge_records(recs2, pulls_rev, '2026-10-11T02:00:00Z',
                                  CERT_KAPPA, CERT_DEC, CERT_SHA)
    by_key3 = {(r['pr'], r['head_sha']): r for r in recs3}
    check("F3 reversion re-resolves head A (stale lifted)",
          by_key3[(9001, head_a)].get('stale') is not True)
    check("F3 reversion supersedes head B",
          by_key3[(9001, head_b)].get('stale') is True)
    # determinism: two identical runs at identical inputs -> same output
    r1, s1 = merge_records([], pulls_rev, 'X', CERT_KAPPA, CERT_DEC, CERT_SHA)
    r2, s2 = merge_records([], pulls_rev, 'X', CERT_KAPPA, CERT_DEC, CERT_SHA)
    check("F3 deterministic across identical runs", r1 == r2)


# ---------------- F4 -------------------------------------------------------------
def test_f4_certificate_digest_bound():
    root = _snapshot_root()
    # authoritative artifact is present in the live tree
    art = os.path.join(root, 'data', 'certificate.artifact.json')
    import hashlib
    if os.path.exists(art):
        real = hashlib.sha256(open(art, 'rb').read()).hexdigest()
        check("F4 recomputed artifact digest == declared",
              real == CERT_SHA)
        # nibble-flip the feed's certificate_sha256 -> gate must block
        def corrupt(feed):
            s = feed['selected_result']['certificate_sha256']
            feed['selected_result']['certificate_sha256'] = ('0' if s[0] != '0' else '1') + s[1:]
        root2 = _snapshot_root(corrupt)
        p = run_gate(root2)
        check("F4 gate blocks nibble-flipped certificate_sha256",
              p.returncode != 0, p.stdout[:160])
        # unverifiable fake digest -> blocked as well
        def corrupt2(feed):
            feed['selected_result']['certificate_sha256'] = 'c' * 64
        root3 = _snapshot_root(corrupt2)
        p = run_gate(root3)
        check("F4 gate blocks unverifiable fake digest",
              p.returncode != 0, p.stdout[:160])
        # mutate the mirror bytes: feed binds the actual mirror bytes, so a
        # self-consistent two-field swap can't fool the sha256(mirror) binding
        def corrupt3(feed):
            feed['selected_result']['selected_result_sha256'] = 'd' * 64
        root4 = _snapshot_root(corrupt3)
        p = run_gate(root4)
        check("F4 gate blocks selected_result_sha256 != sha256(mirror bytes)",
              p.returncode != 0, p.stdout[:160])
    else:
        check("F4 authoritative artifact absent (live tree missing data/artifact)",
              False, "data/certificate.artifact.json not present")


# ---------------- F5 -------------------------------------------------------------
def test_f5_frame_rejection():
    # Reject: model / ceiling / pricing model / no new k / would need / hypothetical
    bad = [
        (100, "A kappa ceiling of 0.001 for every word (no new k)",
         "kappa = 0.001; unchanged construction"),
        (101, "Some model that would need kappa = 0.0005",
         "the pricing model gives kappa = 0.0005, not a construction"),
        (102, "Structural barriers for kappa = 0.01 (no new exponent)",
         "conditional kappa = 0.01 hypothetical"),
        (103, "Replays of the verifiers (no new kappa)",
         "kappa = 0.002 is the banked value"),
    ]
    for num, title, body in bad:
        r = parse_kappa(f"{title}\n{body}", title=title)
        check(f"F5 rejects frame claim #{num}", r is None,
              f"parsed {r}")
    # PR 229 real body (live contamination) must now be rejected
    for page in (1, 2, 3):
        path = os.path.join(ROOT, 'data', f'pulls_page{page}.json')
        if os.path.exists(path):
            for p in json.load(open(path)):
                if p['number'] == 229:
                    r = parse_kappa((p.get('title') or '') + '\n' + (p.get('body') or ''),
                                    title=p.get('title'))
                    check("F5 rejects real PR 229 (model, no new k)",
                          r is None, f"parsed {r}")
    # build_record doc-veto returns None for a frame-declaring PR
    rec = build_record(make_pr(200, 'c' * 40,
                               "A kappa ceiling for every word (no new k)",
                               "kappa = 0.0003"), '2026-10-11T00:00:00Z',
                       CERT_KAPPA, CERT_DEC, CERT_SHA)
    check("F5 build_record vetoes doc-frame PR", rec is None)

    # Accept: valid construction forms (real #442 + golden forms still parse)
    ok_cases = [
        # #442 real form
        (442, "Conditional κ ≈ 1.2375517e-3: idle-axis hosting of helper residuals",
         "This construction achieves conditional κ = 0.001237551733247294 exactly.\n"
         "The exact fraction is κ = 1237551733247294/1000000000000000000.\n"
         "Verified by our 47 strict outer inequalities."),
    ]
    for num, title, body in ok_cases:
        r = parse_kappa(f"{title}\n{body}", title=title)
        check(f"F5 accepts real construction #{num}", r is not None, f"None for {num}")
    goldens = json.load(open(os.path.join(ROOT, 'tests', 'golden_kappa_parse.json')))['cases']
    for c in goldens:
        r = parse_kappa((c['title'] or '') + '\n' + (c['body'] or ''), title=c.get('title'))
        exp = c['expected']
        got = r is not None and (r['num'], r['den'], r['decimal']) == \
            (exp['kappa_num'], exp['kappa_den'], exp['kappa_decimal']) and r['agree']
        check(f"F5 golden #{c['pr']} still parses", got, f"got {r}")


def main():
    test_f1_docroot()
    test_f2_composite_uniqueness()
    test_f3_supersede_and_resolve()
    test_f4_certificate_digest_bound()
    test_f5_frame_rejection()
    print()
    if FAILS:
        print(f"{len(FAILS)} regression(s) failed: {FAILS}")
        sys.exit(1)
    print("all regressions pass")


if __name__ == '__main__':
    main()
