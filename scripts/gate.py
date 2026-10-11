#!/usr/bin/env python3
"""frontier-math v1 staging gate (leo/ARCHITECTURE.md §Staging gate).

Checks (all must pass for the update workflow to commit):
  1. feed.schema.json validation: required fields, SHA format, fraction==decimal
     agreement to 15 significant digits, tier/verify consistency, the per-(pr,
     head_sha) identity/uniqueness invariant, and an up-to-date schema copy in
     the Pages docroot (F1/F2).
  2. Determinism: re-emit feed+chart from data/records.json must be byte-identical
     to docs/feed.json / docs/chart-data.json (idempotent pipeline).
  3. Selected-result binding: feed.selected_result must bind the byte-captured
     certificate artifact (F4): recompute sha256 over the mirror + raw-capture
     bytes, and verify every human-verified record's verify.certificate_sha256
     equals the digest recomputed from the authoritative certificate bytes.
  4. Claimed-vs-verified separation: no claimed record in chart.verified[] and
     vice versa; verified[] rows must bind the selected result.

Exit 0 = pass, nonzero = block commit. stdlib only.
Usage: python3 scripts/gate.py [--root DIR]   (DIR defaults to repo root)
"""
import argparse
import base64
import hashlib
import json
import os
import re
import sys
from decimal import Decimal, getcontext

getcontext().prec = 100


def load(path):
    with open(path) as f:
        return json.load(f)


# ---------------- minimal draft-07 validator (subset used by feed.schema.json) --------
def resolve_ref(schema, root, ref):
    node = root
    for part in ref.lstrip('#/').split('/'):
        node = node[part]
    return node


def validate(instance, schema, root, path='$'):
    """Yield error strings."""
    if '$ref' in schema:
        schema = resolve_ref(schema, root, schema['$ref'])
    t = schema.get('type')
    if t:
        types = t if isinstance(t, list) else [t]
        ok = False
        for tt in types:
            if tt == 'object' and isinstance(instance, dict):
                ok = True
            elif tt == 'array' and isinstance(instance, list):
                ok = True
            elif tt == 'string' and isinstance(instance, str):
                ok = True
            elif tt == 'integer' and isinstance(instance, int) and not isinstance(instance, bool):
                ok = True
            elif tt == 'number' and isinstance(instance, (int, float)) and not isinstance(instance, bool):
                ok = True
            elif tt == 'boolean' and isinstance(instance, bool):
                ok = True
            elif tt == 'null' and instance is None:
                ok = True
        if not ok:
            yield f"{path}: type {type(instance).__name__} not in {types}"
            return
    if 'const' in schema and instance != schema['const']:
        yield f"{path}: not const {schema['const']!r}"
    if 'enum' in schema and instance not in schema['enum']:
        yield f"{path}: {instance!r} not in enum"
    if 'pattern' in schema and isinstance(instance, str) and not re.search(schema['pattern'], instance):
        yield f"{path}: {instance!r} does not match {schema['pattern']!r}"
    if 'minimum' in schema and isinstance(instance, (int, float)) and instance < schema['minimum']:
        yield f"{path}: {instance} < minimum {schema['minimum']}"
    if isinstance(instance, dict):
        for req in schema.get('required', []):
            if req not in instance:
                yield f"{path}: missing required '{req}'"
        props = schema.get('properties', {})
        for k, v in instance.items():
            if k in props:
                yield from validate(v, props[k], root, f"{path}.{k}")
            elif schema.get('additionalProperties') is False:
                yield f"{path}: additional property '{k}' not permitted"
    if isinstance(instance, list) and 'items' in schema:
        for i, item in enumerate(instance):
            yield from validate(item, schema['items'], root, f"{path}[{i}]")
    if 'anyOf' in schema:
        errs = []
        for sub in schema['anyOf']:
            e = list(validate(instance, sub, root, path))
            if not e:
                errs = []
                break
            errs.append(e)
        if errs:
            for e in errs[0]:
                yield e


def sig15(x):
    if x == 0:
        return Decimal(0)
    return x.quantize(Decimal('1e' + str(x.adjusted() - 14)))


def agrees(num, den, decimal_str):
    return sig15(Decimal(num) / Decimal(den)) == sig15(Decimal(decimal_str))


def check1(root, feed, schema):
    errs = []
    for e in validate(feed, schema, schema):
        errs.append(f"schema: {e}")
    for key in ('records', 'quarantined'):
        for r in feed.get(key, []):
            pr = r['pr']
            if r.get('kappa_num') is not None:
                if not agrees(r['kappa_num'], r['kappa_den'], r['kappa_decimal']):
                    errs.append(f"schema: pr {pr} fraction/decimal disagree at 15 sig digits")
            else:
                if not r.get('stale'):
                    errs.append(f"schema: pr {pr} unparseable kappa must be stale:true")
            if r['tier'] == 'human-verified' and not r.get('verify'):
                errs.append(f"schema: pr {pr} tier human-verified requires verify object")
            if r['tier'] == 'claimed' and r.get('verify'):
                errs.append(f"schema: pr {pr} tier claimed must not carry verify object")
            if r['tier'] == 'lean-verified':
                errs.append(f"schema: pr {pr} lean-verified not populating in v1")
    # F2 (Shaka QA-VERDICT / ARCHITECTURE data model): one record per (PR x head
    # SHA). The composite key (pr, head_sha) is THE ledger identity; a duplicate
    # composite key anywhere in the feed (records[] OR quarantined[], and no key
    # straddling both) is corruption that must block. This is deliberately the
    # composite-key invariant, NOT global head_sha uniqueness: distinct PRs may
    # share a head_sha (staged branches) and must not be blocked for it.
    buckets = {}
    for bucket in ('records', 'quarantined'):
        for r in feed.get(bucket, []):
            key = (r['pr'], r['head_sha'])
            buckets.setdefault(key, []).append(bucket)
    for key, where in sorted(buckets.items()):
        if len(where) > 1:
            errs.append(f"identity: duplicate (pr, head_sha) #{key[0]}@"
                        f"{key[1][:8]} in {sorted(set(where))}")
    # F1 (Shaka QA-VERDICT / publish readiness): the Pages docroot is docs/, so
    # index.html's feed.schema.json link resolves to a schema copy that must be
    # byte-identical to the authoritative repo-root schema.
    doc_schema = os.path.join(root, 'docs', 'feed.schema.json')
    if not os.path.exists(doc_schema):
        errs.append(f"F1: docs/feed.schema.json missing (index.html schema link 404s "
                    f"on Pages docroot)")
    else:
        with open(os.path.join(root, 'feed.schema.json'), 'rb') as a, \
             open(doc_schema, 'rb') as b:
            if a.read() != b.read():
                errs.append("F1: docs/feed.schema.json differs from root feed.schema.json "
                            "(re-emit or index.html schema link is stale)")
    return errs


def check2(root, feed):
    """Determinism: re-emit from records.json; must be byte-identical."""
    sys.path.insert(0, os.path.join(root, 'scripts'))
    from fetch import emit_views  # same code path the producer used
    recs = load(os.path.join(root, 'data', 'records.json'))['records']
    cert = feed['selected_result'] or {}
    try:
        f2, c2 = emit_views(recs, cert if cert else None, feed['upstream_main_sha'],
                            feed['generated_at'])
    except ValueError as e:
        return [f"determinism: F2 identity violation in records.json -> {e}"]
    errs = []
    with open(os.path.join(root, 'docs', 'feed.json'), 'rb') as fh:
        if json.dumps(f2, indent=2, sort_keys=True, ensure_ascii=False).encode() + b'\n' != fh.read():
            errs.append("determinism: docs/feed.json differs from re-emit of data/records.json")
    with open(os.path.join(root, 'docs', 'chart-data.json'), 'rb') as fh:
        if json.dumps(c2, indent=2, sort_keys=True, ensure_ascii=False).encode() + b'\n' != fh.read():
            errs.append("determinism: docs/chart-data.json differs from re-emit of data/records.json")
    return errs


def check3(root, feed):
    """Selected-result binding (F4): recompute the digest over the AUTHORITATIVE
    certificate artifact bytes and bind feed.selected_result to the MIRROR bytes,
    not to two mutually-consistent JSON fields.

    Trust root per ARCHITECTURE staging-gate #3 + data model: human-verified
    promotion is valid only when the certificate bytes from upstream match. Chain
    verified here, all arithmetic recomputed at gate time:
      a. mirror bytes == base64 decode of the stored contents-API capture
         (data/selected-result.raw.json), and the capture's git-blob sha1 + size
         must match (proves the mirror is the artifact upstream actually served);
      b. sha256(mirror bytes) == feed.selected_result.selected_result_sha256
         (the feed block binds the mirror's byte content, not two JSON fields);
      c. if the deeper certificate artifact is captured (data/certificate.artifact
         .json, the file the mirror's `certificate`/`certificate_sha256` names):
         sha256(artifact bytes) == feed.selected_result.certificate_sha256 AND
         == the mirror-declared certificate_sha256;
      d. every human-verified record's verify.certificate_sha256 must equal the
         same recomputed digest, and its kappa/decimal must equal the mirror's.
    When (c)'s authoritative bytes are unavailable, the gate reports the exact
    blocker (a claimed digest with no recomputable byte source cannot pass).
    """
    errs = []
    mirror_path = os.path.join(root, 'data', 'selected-result.json')
    if not os.path.exists(mirror_path):
        return ["binding: data/selected-result.json missing (fetch never captured upstream cert)"]
    with open(mirror_path, 'rb') as f:
        mirror_bytes = f.read()
    try:
        sel = json.loads(mirror_bytes.decode())
    except Exception as e:
        return [f"binding: upstream certificate unparsable: {e}"]
    fb = feed.get('selected_result') or {}

    # (a) mirror bytes == contents-API capture, blob-verified
    raw_path = os.path.join(root, 'data', 'selected-result.raw.json')
    if os.path.exists(raw_path):
        raw = load(raw_path)
        decoded = base64.b64decode(raw.get('content') or '')
        if decoded != mirror_bytes:
            errs.append("binding: mirror bytes differ from base64 content of "
                        "selected-result.raw.json capture (mirror is not the "
                        "artifact upstream served)")
        if raw.get('sha'):
            blob = hashlib.sha1(b'blob %d\0' % len(decoded) + decoded).hexdigest()
            if blob != raw['sha']:
                errs.append(f"binding: capture git-blob sha {raw['sha']} does not "
                            f"recompute from mirror bytes ({blob})")
        if raw.get('size') is not None and raw['size'] != len(decoded):
            errs.append(f"binding: capture size {raw['size']} != mirror bytes "
                        f"{len(decoded)}")

    # (b) feed.selected_result binds the mirror byte content
    feed_mirror_sha = fb.get('selected_result_sha256')
    recomputed_mirror_sha = hashlib.sha256(mirror_bytes).hexdigest()
    if feed_mirror_sha != recomputed_mirror_sha:
        errs.append(f"binding: selected_result.selected_result_sha256 "
                    f"{feed_mirror_sha!r} != sha256(mirror bytes) "
                    f"{recomputed_mirror_sha!r}")

    # (b2) feed kappa/decimal must equal the values parsed from the mirror bytes
    for field in ('kappa', 'decimal'):
        if fb.get(field) != sel.get(field):
            errs.append(f"binding: selected_result.{field} {fb.get(field)!r} != "
                        f"mirror {sel.get(field)!r}")

    # (c) the deeper certificate artifact digest is recomputed from its bytes
    declared_digest = sel.get('certificate_sha256')
    artifact_path = os.path.join(root, 'data', 'certificate.artifact.json')
    if os.path.exists(artifact_path):
        with open(artifact_path, 'rb') as f:
            art_bytes = f.read()
        recomputed = hashlib.sha256(art_bytes).hexdigest()
        if recomputed != fb.get('certificate_sha256'):
            errs.append(f"binding: selected_result.certificate_sha256 "
                        f"{fb.get('certificate_sha256')!r} != sha256(named "
                        f"certificate artifact bytes) {recomputed}")
        if declared_digest and recomputed != declared_digest:
            errs.append(f"binding: sha256(named certificate artifact) {recomputed} "
                        f"!= mirror-declared certificate_sha256 {declared_digest}")
        if not fb.get('certificate_sha256'):
            errs.append("binding: selected_result missing certificate_sha256 "
                        "(human-verified can't be bound)")
    else:
        # authoritative bytes unavailable: a claimed digest with no recomputable
        # byte source must not silently pass (F4 blocker, not an invented check)
        if fb.get('certificate_sha256') or declared_digest:
            errs.append(
                "binding: certificate artifact bytes not captured "
                "(data/certificate.artifact.json); certificate_sha256 cannot be "
                "recomputed against authoritative bytes -> blocked")

    # (d) every human-verified record binds the same digest + mirror kappa/decimal
    ck, cd = sel.get('kappa'), sel.get('decimal')
    if ck and cd:
        kn, kd = (int(x) for x in ck.split('/'))
    art_exists = os.path.exists(os.path.join(root, 'data', 'certificate.artifact.json'))
    for r in feed.get('records', []):
        if r['tier'] != 'human-verified':
            continue
        verify = r.get('verify') or {}
        if ck and cd:
            if r['kappa_num'] != kn or r['kappa_den'] != kd or r['kappa_decimal'] != cd:
                errs.append(f"binding: pr {r['pr']} human-verified but kappa/dec "
                            f"!= certificate ({kn}/{kd}, {cd})")
        vdigest = verify.get('certificate_sha256')
        if art_exists:
            with open(os.path.join(root, 'data', 'certificate.artifact.json'), 'rb') as f:
                rca = hashlib.sha256(f.read()).hexdigest()
            if vdigest != rca:
                errs.append(f"binding: pr {r['pr']} verify.certificate_sha256 "
                            f"{vdigest!r} != recomputed artifact digest {rca}")
            if vdigest != fb.get('certificate_sha256'):
                errs.append(f"binding: pr {r['pr']} verify.certificate_sha256 "
                            f"{vdigest!r} != selected_result.certificate_sha256 "
                            f"{fb.get('certificate_sha256')!r}")
        elif vdigest != fb.get('certificate_sha256') or vdigest != declared_digest:
            errs.append(f"binding: pr {r['pr']} verify.certificate_sha256 "
                        f"{vdigest!r} not bound to any recomputable certificate bytes")
    return errs


def check4(root, feed):
    """Claimed-vs-verified separation in the derived chart view."""
    errs = []
    chart = load(os.path.join(root, 'docs', 'chart-data.json'))
    rec_by_key = {(r['pr'], r['head_sha']): r for r in feed.get('records', [])}
    for row in chart.get('claimed', []):
        r = rec_by_key.get((row['pr'], row['head_sha']))
        if r is None or r['tier'] != 'claimed':
            errs.append(f"separation: chart.claimed row pr {row['pr']} head {row['head_sha'][:8]} is not a claimed record")
    verified_prs = set()
    for row in chart.get('verified', []):
        r = rec_by_key.get((row['pr'], row['head_sha']))
        if r is None or r['tier'] == 'claimed':
            errs.append(f"separation: chart.verified row pr {row['pr']} head {row['head_sha'][:8]} is not a verified record")
        verified_prs.add(row['pr'])
    # a claimed pr must never also appear as verified
    overlap = verified_prs & {row['pr'] for row in chart.get('claimed', [])}
    if overlap:
        errs.append(f"separation: pr(s) {sorted(overlap)} in both chart arrays")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    args = ap.parse_args()
    root = args.root
    feed = load(os.path.join(root, 'docs', 'feed.json'))
    schema = load(os.path.join(root, 'feed.schema.json'))

    results = {
        '1-schema+agreement': check1(root, feed, schema),
        '2-determinism': check2(root, feed),
        '3-selected-result-binding': check3(root, feed),
        '4-claimed-verified-separation': check4(root, feed),
    }
    failed = False
    for name, errs in results.items():
        if errs:
            failed = True
            print(f"FAIL {name}:")
            for e in errs[:10]:
                print(f"   {e}")
            if len(errs) > 10:
                print(f"   ... {len(errs) - 10} more")
        else:
            print(f"PASS {name}")
    n = len(feed.get('records', []))
    claimed = sum(1 for r in feed.get('records', []) if r['tier'] == 'claimed')
    print(f"feed: records={n} claimed={claimed} quarantined={len(feed.get('quarantined', []))}")
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
