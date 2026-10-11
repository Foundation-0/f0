#!/usr/bin/env python3
"""frontier-math v1 fetch: upstream PR poll + kappa parse + append-only records + emit feed/chart.

Data model / pipeline per leo/ARCHITECTURE.md (STABLE). stdlib only.
Usage: python3 scripts/fetch.py [--repo R] [--snapshot DIR] [--requests-out FILE]
  --snapshot: read PR list + certificate + main-ref from local JSON files instead of
              the network (offline determinism testing). Snapshot layout:
                pulls_page1.json.. pulls_pageN.json (arrays of PR objects)
                selected-result.json  (contents API response, content=base64)
                main_ref.json         (git ref response)
Env: GH_TOKEN or GITHUB_TOKEN for authenticated REST (anonymous allowed but tiny budget).
"""
import argparse
import base64
import hashlib
import json
import math
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal, getcontext

getcontext().prec = 100

API = "https://api.github.com"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
DOCS = os.path.join(ROOT, "docs")

TIER_ENUM = ("claimed", "human-verified", "lean-verified")

# ---------------- kappa parser (golden-file-gated; see tests/golden_kappa_parse.json) ----
SUP = {'\u2070': '0', '\u00b9': '1', '\u00b2': '2', '\u00b3': '3', '\u2074': '4',
       '\u2075': '5', '\u2076': '6', '\u2077': '7', '\u2078': '8', '\u2079': '9',
       '\u207b': '-', '\u207a': '+'}
SUPRUN = re.compile('[' + ''.join(SUP) + ']+')
TOK = re.compile(r'(?:\u03ba|\\kappa|[Kk]appa)')
SEP_RE = re.compile(r'\s*(?:=|:)\s*|\s+is\s+|\s+equal(?:s|sto)\s+')
FRAC_LATEX = re.compile(r'\\frac\s*\{\s*(\d{2,})\s*\}\s*\{\s*([\d\.\*\^\s]{2,40}?)\s*\}')
FRAC_SLASH = re.compile(r'(\d{2,})\s*/\s*([\d\^\*\.\s]{1,40})')
WIT = re.compile(r'(\d+)\s*\*\s*(\d+)\s*\^\s*(-?\d+)')
DEC_RE = re.compile(r'(?<![\w./])(\d*\.\d+|\d+\.\d+)'
                    r'(?:\s*(?:\*\s*10\s*\^?|[eE])\s*(-?\d+))?')


def normalize(text):
    """2·10¹⁷ -> 2*10^17, 10^{18} -> 10^18 etc.
    (ARCHITECTURE parse rules: normalize denominators.)"""
    text = SUPRUN.sub(lambda m: '^' + ''.join(SUP[c] for c in m.group(0)), text)
    text = text.replace('\\dfrac', '\\frac').replace('\\tfrac', '\\frac')
    text = text.replace('\\cdot', '*').replace('\\times', '*')
    text = text.replace('·', '*').replace('×', '*')
    text = text.replace('\\approx', '=').replace('≈', '=')
    text = text.replace('\\left', '').replace('\\right', '').replace('\\!', '').replace('\\,', '')
    text = text.replace('**', ' ').replace('`', ' ')
    text = re.sub(r'\^\s*\{\s*(-?\d+)\s*\}', r'^\1', text)  # 10^{18} -> 10^18
    text = re.sub(r'\s+', ' ', text)
    return text


def den_int(s):
    """Denominator forms: 500000000000000000 | 10^18 | 2*10^17 | 2.5*10^23 | 5e17."""
    s = re.sub(r'\s+', '', s).strip('.,;').replace('{', '').replace('}', '')
    if not s:
        return None
    m = re.match(r'^10\^(-?\d+)$', s)
    if m:
        e = int(m.group(1))
        return 10 ** e if 0 <= e <= 80 else None
    m = re.match(r'^(\d+(?:\.\d+)?)(?:\*10\^?(-?\d+)|[eE](-?\d+))?$', s)
    if not m:
        return None
    try:
        v = Decimal(m.group(1)) * (Decimal(10) ** int(m.group(2) or m.group(3) or 0))
    except Exception:
        return None
    if v != v.to_integral_value() or v < 10 ** 6:
        return None
    return int(v)


def dec_expansion(num, den):
    return format((Decimal(num) / Decimal(den)).normalize(), 'f')


def sig15(x):
    if x == 0:
        return Decimal(0)
    return x.quantize(Decimal('1e' + str(x.adjusted() - 14)))


def _wit_value(r):
    """Base-2 witness form: num * 2^exp (e.g. 17*2^-63)."""
    wm = WIT.match(r)
    if not wm:
        return None
    num, base, exp = int(wm.group(1)), int(wm.group(2)), int(wm.group(3))
    if base != 2 or exp >= 0 or exp < -200:
        return None
    den = 2 ** (-exp)
    tail = r[wm.end():]
    am = re.match(r'\s*(?:=|is|:)?\s*', tail)
    cm = DEC_RE.match(tail, am.end() if am else 0)
    if cm:
        v = Decimal(cm.group(1)) * (Decimal(10) ** int(cm.group(2) or 0))
        if 0 < v <= 1:
            agree = sig15(Decimal(num) / Decimal(den)) == sig15(v)
            return ('pair', num, den, format(v.normalize(), 'f'), agree)
    return ('fraction', num, den, dec_expansion(num, den), True)


def _try_anchor(rest):
    r = rest[:160].replace('(', ' ').replace(')', ' ')
    fm = FRAC_LATEX.match(r) or FRAC_SLASH.match(r)
    if fm:
        n = int(fm.group(1))
        d = den_int(fm.group(2))
        fm_end = fm.end()
        if d is None:  # greedy slash-run may overshoot into the trailing decimal: shrink
            g = fm.group(2)
            for cut in range(len(g), 0, -1):
                d = den_int(g[:cut])
                if d is not None:
                    fm_end = fm.start(2) + cut
                    break
        if d is None:
            wv = _wit_value(r)
            if wv:
                return wv
        if d is not None:
            tail = r[fm_end:]
            am = re.match(r'\s*(?:=|is|:)?\s*', tail)
            cm = DEC_RE.match(tail, am.end())
            if cm:
                v = Decimal(cm.group(1)) * (Decimal(10) ** int(cm.group(2) or 0))
                if 0 < v <= 1:
                    # agreement to 15 significant digits; the STATED decimal (full
                    # precision) is preserved verbatim for audit
                    agree = sig15(Decimal(n) / Decimal(d)) == sig15(v)
                    return ('pair', n, d, format(v.normalize(), 'f'), agree)
            return ('fraction', n, d, dec_expansion(n, d), True)
    wv = _wit_value(r)
    if wv:
        return wv
    cm = DEC_RE.match(r)
    if cm:
        v = Decimal(cm.group(1)) * (Decimal(10) ** int(cm.group(2) or 0))
        if 0 < v <= 1:
            vn = v.normalize()
            t = vn.as_tuple()
            dn = 10 ** (-t.exponent) if t.exponent < 0 else 1
            return ('decimal', int(vn * dn), dn, format(vn, 'f'), True)
    return None


RANK = {'pair': 0, 'fraction': 1, 'decimal': 2}

# ---- F5 (Shaka QA-VERDICT): non-construction frame exclusions -------------------
# A κ value stated inside a model/ceiling/pricing-model/advance/no-new-κ/no-witness
# frame is NOT a construction claim. Document level: the PR title declares the
# package's own status, so a title marker vetoes the whole PR (re-validated live
# per PR head, same discipline as tier promotion). Anchor level: a marker in the
# claim clause (sentence span around token+value) rejects that anchor only.
# Measured on the full pinned snapshot (QA probe + mozi sizing): kills exactly the
# 9 contaminated non-construction rows (229, 203, 221, 214, 204, 201, 192, 233, 304);
# all four golden constructions, the certificate-bound #279 row, and the current
# frontier leaders (#442/#441/#440/#433...) keep their exact values. Ambiguity note
# (per Leo's F5 brief): keyword frames cannot be perfect; this set is conservative
# on the documented upstream framing vocabulary, not a general NLP classifier.
# DOC set stays on DECLARATORY phrases only (bare "model"/"pricing"/"unchanged"
# are legitimate construction prose here, e.g. "exact pricing gives", "unchanged
# bit supplier"; measured false-kill of #383 and of valid low-k rows 82/98/106).
DOC_FRAME_RE = re.compile(
    r"no new|no additional|not a construction|would need|would take|"
    r"\bceiling\b|hypothetical|\bpricing model\b", re.I)
CLAUSE_FRAME_RE = re.compile(
    r"no new|not a construction|would need|would take|\bceiling\b|hypothetical",
    re.I)
CLAUSE_BACK_BOUND = re.compile(r"[.!?\n]")
CLAUSE_FWD_BOUND = re.compile(r"[.!?:;\n]")


def _clause_span(text, start, end):
    """Sentence-ish span around an anchor: back to a clause boundary (decimals'
    interior dots included), forward to the next boundary (decimal dots skipped).
    Hard caps (back 100 / fwd 120) keep the span on the claim sentence: a frame
    word in the NEXT sentence must not veto a clean construction anchor (measured
    false-rejection of #262's fraction anchor at wider caps)."""
    i, steps = start, 0
    while i > 0 and steps < 100:
        if CLAUSE_BACK_BOUND.match(text[i - 1]):
            break
        i -= 1
        steps += 1
    j, steps = end, 0
    while j < len(text) and steps < 120:
        c = text[j]
        if c == "." and j + 1 < len(text) and text[j + 1].isdigit():
            j += 1
            steps += 1
            continue
        if CLAUSE_FWD_BOUND.match(c):
            break
        j += 1
        steps += 1
    return text[i:j + 1]


def parse_kappa(raw, title=None):
    """Scan every kappa-claim anchor; prefer fraction+decimal pair agreement.
    -> dict(num, den, decimal, agree, kind) | None.
    A document-level frame marker in `title` vetoes the whole claim set (F5)."""
    if title is not None and DOC_FRAME_RE.search(title):
        return None
    text = normalize(raw)
    best = mismatch = None
    for m in TOK.finditer(text):
        tail = text[m.end():m.end() + 200]
        sm = SEP_RE.match(tail)
        if not sm:
            continue
        cand = _try_anchor(tail[sm.end():])
        if not cand:
            continue
        vend = min(m.end() + sm.end() + 90, len(text))
        if CLAUSE_FRAME_RE.search(_clause_span(text, m.start(), vend)):
            continue
        kind, n, d, s, agree = cand
        rec = dict(num=n, den=d, decimal=s, agree=agree, kind=kind)
        if agree and (best is None or RANK[kind] < RANK[best['kind']]):
            best = rec
        if not agree and mismatch is None:
            mismatch = rec
    return best if best is not None else mismatch


# ---------------- HTTP plumbing (conditional requests, budget log) ----------------
class Api:
    def __init__(self, token, etags):
        self.token = token
        self.etags = etags  # url -> etag
        self.requests = 0
        self.not_modified = 0
        self.remaining = None

    def get(self, url, etag_key=None):
        key = etag_key or url
        req = urllib.request.Request(url)
        req.add_header('Accept', 'application/vnd.github+json')
        req.add_header('User-Agent', 'frontier-math-dashboard')
        if self.token:
            req.add_header('Authorization', 'Bearer ' + self.token)
        if key in self.etags:
            req.add_header('If-None-Match', self.etags[key])
        self.requests += 1
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode('utf-8'))
                etag = resp.headers.get('ETag')
                if etag:
                    self.etags[key] = etag
                self.remaining = resp.headers.get('X-RateLimit-Remaining', self.remaining)
                return body, 200
        except urllib.error.HTTPError as e:
            if e.code == 304:
                self.not_modified += 1
                self.remaining = e.headers.get('X-RateLimit-Remaining', self.remaining)
                return None, 304
            raise


def utcnow():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def load_json(path, default=None):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return default


def dump_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        json.dump(obj, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write('\n')
    os.replace(tmp, path)


def fetch_pull_list(api, repo):
    pulls = []
    page = 1
    while True:
        url = f"{API}/repos/{repo}/pulls?state=open&per_page=100&page={page}"
        body, status = api.get(url, etag_key=f"pulls:{page}")
        if body is None:  # 304: reuse cached page
            cached = load_json(os.path.join(DATA, f'pulls_page{page}.json'), [])
            pulls.extend(cached)
            if not cached:
                break
        else:
            dump_json(os.path.join(DATA, f'pulls_page{page}.json'), body)
            pulls.extend(body)
            if len(body) < 100:
                break
        page += 1
        if page > 40:
            break
    # drop cache pages beyond the last
    for stale_page in range(page, page + 12):
        p = os.path.join(DATA, f'pulls_page{stale_page}.json')
        if os.path.exists(p):
            os.remove(p)
        else:
            break
    return pulls


def looks_like_claim(text):
    """A kappa token followed by a separator and a value-like prefix (digit, '(',
    '\\frac'): a claim we must parse. Prose mentions ('κ is unchanged', 'no new κ')
    are not claims -> no record."""
    nrm = normalize(text)
    for m in TOK.finditer(nrm):
        tail = nrm[m.end():m.end() + 60]
        sm = SEP_RE.match(tail)
        if sm and re.match(r'\s*[\d(\\.]', tail[sm.end():sm.end() + 3]):
            return True
    return False


def build_record(pr, fetched_at, cert_kappa, cert_decimal, cert_sha):
    """One record per (pr, head_sha). tier: claimed default; human-verified only on
    exact certificate binding (fraction AND decimal AND sha)."""
    title = pr.get('title') or ''
    # F5 document veto: a PR that frames its package as model/ceiling/pricing-model/
    # advance/no-new-κ is not making a construction claim at all -> no record,
    # exactly like a prose-only tooling PR.
    if DOC_FRAME_RE.search(title):
        return None
    text = title + '\n' + (pr.get('body') or '')
    r = parse_kappa(text, title=title)
    head = pr['head']['sha']
    base = pr['base']['sha']
    href = (pr.get('head') or {}).get('repo')
    refs = {"pr_url": pr['html_url'],
            "head_url": (href['html_url'] + '/tree/' + head) if href else None,
            "certificate_path": None}
    if r is None:
        if not looks_like_claim(text):
            return None  # not a kappa claim (audit/tooling PR) -> no record
        rec = {
            "pr": pr['number'], "head_sha": head, "base_sha": base,
            "kappa_num": None, "kappa_den": None, "kappa_decimal": None,
            "tier": 'claimed', "title": pr.get('title') or '',
            "draft": bool(pr.get('draft')), "pr_updated_at": pr['updated_at'],
            "fetched_at": fetched_at, "stale": True,
            "stale_reason": "unparseable-kappa", "source_refs": refs,
        }
        return rec
    tier = 'claimed'
    verify = None
    quarantined = not r['agree']
    if cert_kappa and (str(r['num']), str(r['den'])) == cert_kappa and r['decimal'] == cert_decimal:
        tier = 'human-verified'
        verify = {"method": "selected-result-binding", "certificate_sha256": cert_sha,
                  "checker_exit": 0}
        refs["certificate_path"] = "certificates/selected-result.json"
    rec = {
        "pr": pr['number'],
        "head_sha": head,
        "base_sha": base,
        "kappa_num": r['num'],
        "kappa_den": r['den'],
        "kappa_decimal": r['decimal'],
        "tier": tier,
        "title": pr.get('title') or '',
        "draft": bool(pr.get('draft')),
        "pr_updated_at": pr['updated_at'],
        "fetched_at": fetched_at,
        "source_refs": refs,
    }
    if verify is not None:
        rec['verify'] = verify
    if quarantined:
        rec['stale'] = True
        rec['stale_reason'] = "fraction-decimal-mismatch"
    return rec


def emit_views(records, cert, main_sha, generated_at):
    """Deterministic (sorted, stable) feed + chart views. Pure function of inputs.
    Quarantined (stale) records are kept in records.json and surfaced under
    feed.quarantined; excluded from records[]/chart arrays until re-resolved.

    Always-on F2 invariant: (pr, head_sha) is the ledger identity, so the emitted
    views must never contain two rows with the same composite key. Any duplicate
    (including a row appearing in both records[] and quarantined[]) raises, which
    the gate (check2 + check1) and the fetch path surface as a blocking error.
    """
    seen = {}
    ok = True
    for r in records:
        k = (r['pr'], r['head_sha'])
        if k in seen:
            ok = False
            seen[k] += 1
        else:
            seen[k] = 1
    if not ok:
        dups = sorted(k for k, n in seen.items() if n > 1)
        raise ValueError(
            "F2 identity violation: duplicate (pr, head_sha) row(s) in records: "
            + ", ".join(f"#{p}@{h[:8]}" for p, h in dups))
    clean = [r for r in records if not r.get('stale')]
    quarantined = [r for r in records if r.get('stale')]
    feed = {
        "feed_version": 1,
        "generated_at": generated_at,
        "upstream_main_sha": main_sha,
        "selected_result": cert,
        "records": clean,
        "quarantined": quarantined,
    }
    chart = {
        "generated_at": generated_at,
        "claimed": [{"pr": r['pr'], "head_sha": r['head_sha'],
                     "kappa_decimal": r['kappa_decimal'], "draft": r['draft'],
                     "pr_updated_at": r['pr_updated_at'],
                     "pr_url": r['source_refs']['pr_url']}
                    for r in clean if r['tier'] == 'claimed'],
        "verified": [{"pr": r['pr'], "head_sha": r['head_sha'],
                      "kappa_decimal": r['kappa_decimal'], "tier": r['tier'],
                      "pr_updated_at": r['pr_updated_at'],
                      "pr_url": r['source_refs']['pr_url']}
                     for r in clean if r['tier'] != 'claimed'],
    }
    return feed, chart


def canonical_bytes(obj):
    return (json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode()


def _capture_cert_artifact(args, selected, artifact_digest):
    """F4: fetch/validate the authoritative certificate artifact (the file named by
    the mirror's `certificate`/`certificate_sha256`) and store its bytes at
    data/certificate.artifact.json for the gate to recompute sha256 over."""
    cert_path = selected.get('certificate')
    if not cert_path or not artifact_digest:
        print('NOTE: mirror declares no certificate artifact path; binding check '
              'will skip byte recompute (still binds mirror+sha256 of mirror bytes)')
        return
    dest = os.path.join(DATA, 'certificate.artifact.json')
    if os.path.exists(dest):
        # reuse a prior capture only if it still re-hashes to the declared digest;
        # otherwise overwrite (the upstream artifact won the digest, not our cache)
        with open(dest, 'rb') as f:
            if hashlib.sha256(f.read()).hexdigest() == artifact_digest:
                return
    try:
        data = None
        if args.snapshot and os.path.exists(os.path.join(args.snapshot, 'certificate.artifact.json')):
            with open(os.path.join(args.snapshot, 'certificate.artifact.json'), 'rb') as f:
                data = f.read()
        else:
            url = f"{API}/repos/{args.repo}/contents/{cert_path.lstrip('/')}"
            req = urllib.request.Request(url)
            req.add_header('Accept', 'application/vnd.github+json')
            req.add_header('User-Agent', 'frontier-math-dashboard')
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = json.loads(resp.read().decode('utf-8'))
                data = base64.b64decode(raw.get('content') or '')
                if raw.get('sha'):
                    blob = hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()
                    if blob != raw['sha']:
                        print(f"FATAL: certificate artifact {cert_path} git-blob "
                              f"sha mismatch", file=sys.stderr)
                        sys.exit(1)
                if raw.get('size') is not None and raw['size'] != len(data):
                    print(f"FATAL: certificate artifact {cert_path} size mismatch",
                          file=sys.stderr)
                    sys.exit(1)
        with open(dest, 'wb') as f:
            f.write(data)
        if hashlib.sha256(data).hexdigest() != artifact_digest:
            print(f"FATAL: certificate artifact {cert_path} sha256 does not match "
                  f"mirror-declared certificate_sha256 (trust root broken)",
                  file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"FATAL: could not capture authoritative certificate artifact "
              f"{cert_path}: {e}", file=sys.stderr)
        sys.exit(1)


def merge_records(old_records, pulls, fetched_at, cert_kappa, cert_decimal, cert_sha):
    """Append-only merge on (pr, head_sha) + F3 supersede/re-resolve pass.

    Returns (records, stats). Pure function of inputs; tests drive it directly.
    - F2: (pr, head_sha) is the ledger identity; a colliding row is never
      overwritten (build_record derives `pr` from the pull object, so collisions
      inside one run mean the same PR arrived twice; the gate enforces composite
      uniqueness over emitted artifacts).
    - F3 (ARCHITECTURE quarantine rule): a head that is no longer that PR's live
      head -> stale:true, stale_reason 'superseded-head', kept with tier
      unchanged, excluded from feed.records[]/chart by emit_views until a re-fetch
      re-resolves it. Force-push reversion (head live again) rebuilds the row from
      the pinned source and lifts the quarantine. A live head whose pinned
      title/body no longer yields a construction claim (F5 re-validated live) ->
      'no-construction-claim', same quarantine.
    """
    index = {}
    n_dup_hist = 0
    for r in old_records:
        k = (r['pr'], r['head_sha'])
        if k in index:
            n_dup_hist += 1  # corrupt history input: first row wins, gate blocks
            continue
        index[k] = r
    live_heads = {}
    live_keys = set()
    stats = dict(new=0, unchanged=0, quarantined=0, superseded=0,
                 declaimed=0, reresolved=0, dup_history=n_dup_hist)
    for pr in pulls:
        live_heads[pr['number']] = pr['head']['sha']
        rec = build_record(pr, fetched_at, cert_kappa, cert_decimal, cert_sha)
        if rec is None:
            continue
        key = (rec['pr'], rec['head_sha'])
        if rec.get('stale'):
            stats['quarantined'] += 1
        live_keys.add(key)
        if key in index:
            stats['unchanged'] += 1
            prev = index[key]
            # head unchanged: keep the ORIGINAL row (append-only, determinism).
            # Exception: a row we quarantined (superseded/non-claim) whose head is
            # live again (force-push reversion) -> re-resolve against the pinned
            # source, per ARCHITECTURE "excluded ... until re-resolved".
            # Parser-stale rows (unparseable/mismatch) keep history.
            if prev.get('stale') and prev.get('stale_reason') in ('superseded-head',
                                                                  'no-construction-claim'):
                index[key] = rec
                stats['reresolved'] += 1
            continue
        index[key] = rec
        stats['new'] += 1

    for (pr_num, head), rec in index.items():
        live = live_heads.get(pr_num)
        # F5 doc-veto re-validation: the row's own pinned title snapshot carries
        # the document frame declaration. This covers both heads that are live
        # this run (re-parsed below via live_keys) and rows for PRs absent from
        # this run's pull set (page cap), so persisted non-construction rows are
        # quarantined deterministically without any hardcoded PR list.
        if not rec.get('stale') and DOC_FRAME_RE.search(rec.get('title') or ''):
            rec['stale'] = True
            rec['stale_reason'] = 'no-construction-claim'
            stats['declaimed'] += 1
            continue
        if live is None:
            continue
        if head != live:
            if not rec.get('stale'):
                stats['superseded'] += 1
            rec['stale'] = True
            rec['stale_reason'] = 'superseded-head'
            rec['superseded_by'] = live
        elif (pr_num, head) not in live_keys and not rec.get('stale'):
            rec['stale'] = True
            rec['stale_reason'] = 'no-construction-claim'
            stats['declaimed'] += 1
    records = [index[k] for k in sorted(index)]
    return records, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default='CrocSwap/integer-mult-bounds')
    ap.add_argument('--snapshot', default=None, help='offline fixture dir')
    ap.add_argument('--as-of', default=None,
                    help='pin fetched_at/generated_at (ISO) for byte-identical re-runs')
    ap.add_argument('--requests-out', default=None)
    args = ap.parse_args()

    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    etags = load_json(os.path.join(DATA, 'etags.json'), {})
    fetched_at = args.as_of or utcnow()
    api = Api(token, etags)

    if args.snapshot:
        snaps = sorted(f for f in os.listdir(args.snapshot) if re.match(r'pulls_page\d+\.json$', f))
        pulls = []
        for s in snaps:
            pulls.extend(load_json(os.path.join(args.snapshot, s), []))
        cert_raw = load_json(os.path.join(args.snapshot, 'selected-result.json'))
        main_ref = load_json(os.path.join(args.snapshot, 'main_ref.json'))
        upstream_main_sha = main_ref['object']['sha']
    else:
        pulls = fetch_pull_list(api, args.repo)
        cert_raw, st = api.get(f"{API}/repos/{args.repo}/contents/certificates/selected-result.json",
                               etag_key='selected-result')
        if st == 304:
            cert_raw = load_json(os.path.join(DATA, 'selected-result.raw.json'))
        main_ref, st = api.get(f"{API}/repos/{args.repo}/git/ref/heads/main", etag_key='main-ref')
        if st == 304:
            main_ref = load_json(os.path.join(DATA, 'main_ref.json'))
        upstream_main_sha = main_ref['object']['sha']

    if cert_raw is None:
        print('FATAL: upstream certificate unavailable', file=sys.stderr)
        sys.exit(1)
    cert_bytes = base64.b64decode(cert_raw['content'])
    # F4 capture integrity (trust root): the pinned mirror must be the bytes the
    # contents API actually served. Verify git-blob SHA1, size and path identity
    # BEFORE the mirror is written, so a tampered or truncated capture can never
    # become the binding artifact the gate and human-verified promotion trust.
    blob_sha1 = hashlib.sha1(b'blob %d\0' % len(cert_bytes) + cert_bytes).hexdigest()
    if cert_raw.get('sha') and cert_raw['sha'] != blob_sha1:
        print('FATAL: certificate capture git-blob sha mismatch (mirror refused)',
              file=sys.stderr)
        sys.exit(1)
    if cert_raw.get('size') is not None and cert_raw['size'] != len(cert_bytes):
        print('FATAL: certificate capture size mismatch (mirror refused)',
              file=sys.stderr)
        sys.exit(1)
    dump_json(os.path.join(DATA, 'selected-result.raw.json'), cert_raw)
    dump_json(os.path.join(DATA, 'main_ref.json'), main_ref)
    selected = json.loads(cert_bytes.decode('utf-8'))
    cert = {"kappa": selected['kappa'], "decimal": selected['decimal'],
            "certificate_sha256": selected['certificate_sha256'],
            # F4 audit fields (additive; schema permits): sha256 of the mirror
            # artifact bytes themselves, plus the pinned upstream blob identity.
            "selected_result_sha256": hashlib.sha256(cert_bytes).hexdigest(),
            "source_blob_sha": cert_raw.get('sha'),
            "source_path": cert_raw.get('path')}
    cert_kappa = tuple(selected['kappa'].split('/'))
    cert_decimal = selected['decimal']
    with open(os.path.join(DATA, 'selected-result.json'), 'wb') as f:
        f.write(cert_bytes)

    # F4: capture the AUTHORITATIVE certificate artifact bytes (the file the
    # mirror's `certificate` + `certificate_sha256` name) so the gate can recompute
    # the digest over real bytes instead of trusting two self-consistent JSON
    # fields. The captured bytes must re-hash to the mirror-declared digest.
    artifact_digest = selected.get('certificate_sha256')
    _capture_cert_artifact(args, selected, artifact_digest)

    # append-only merge on (pr, head_sha)
    old = load_json(os.path.join(DATA, 'records.json'), {"records": []})
    records, stats = merge_records(old['records'], pulls, fetched_at,
                                   cert_kappa, cert_decimal,
                                   selected['certificate_sha256'])
    dump_json(os.path.join(DATA, 'records.json'), {"records": records})
    n_new, n_seen, n_quar = stats['new'], stats['unchanged'], stats['quarantined']
    n_superseded, n_declaimed, n_reresolved = (stats['superseded'],
                                               stats['declaimed'],
                                               stats['reresolved'])

    feed, chart = emit_views(records, cert, upstream_main_sha, fetched_at)
    dump_json(os.path.join(DOCS, 'feed.json'), feed)
    dump_json(os.path.join(DOCS, 'chart-data.json'), chart)
    # F1 (QA-VERDICT): publish readiness. Pages serves only docs/ as docroot, so
    # the schema link in index.html resolves to docs/feed.schema.json. Keep a
    # byte-identical copy of the authoritative repo-root schema in the docroot at
    # emit time; the gate (check1) verifies it matches.
    shutil.copyfile(os.path.join(ROOT, 'feed.schema.json'),
                    os.path.join(DOCS, 'feed.schema.json'))
    dump_json(os.path.join(DATA, 'etags.json'), etags)
    state = {"last_generated_at": fetched_at, "requests": api.requests,
             "not_modified": api.not_modified,
             "rate_limit_remaining": api.remaining}
    dump_json(os.path.join(DATA, 'fetch_state.json'), state)
    if args.requests_out:
        with open(args.requests_out, 'w') as f:
            json.dump(state, f)
            f.write('\n')

    claimed = sum(1 for r in feed['records'] if r['tier'] == 'claimed')
    verified = sum(1 for r in feed['records'] if r['tier'] != 'claimed')
    print(f"records total={len(records)} new={n_new} unchanged={n_seen} "
          f"feed_clean={len(feed['records'])} quarantined={n_quar} "
          f"superseded={n_superseded} declaimed={n_declaimed} reresolved={n_reresolved}")
    print(f"claimed={claimed} verified={verified} upstream_open_prs={len(pulls)}")
    print(f"http requests={api.requests} not_modified={api.not_modified} "
          f"rate_limit_remaining={api.remaining} main_sha={upstream_main_sha}")


if __name__ == '__main__':
    main()