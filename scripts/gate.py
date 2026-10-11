#!/usr/bin/env python3
"""frontier-math v1 staging gate (leo/ARCHITECTURE.md §Staging gate).

Checks (all must pass for the update workflow to commit):
  1. feed.schema.json validation: required fields, SHA format, fraction==decimal
     agreement to 15 significant digits, tier/verify consistency.
  2. Determinism: re-emit feed+chart from data/records.json must be byte-identical
     to docs/feed.json / docs/chart-data.json (idempotent pipeline).
  3. Selected-result binding: feed.selected_result must match upstream
     certificates/selected-result.json bytes (kappa, decimal, certificate_sha256).
  4. Claimed-vs-verified separation: no claimed record in chart.verified[] and
     vice versa; verified[] rows must bind the selected result.

Exit 0 = pass, nonzero = block commit. stdlib only.
Usage: python3 scripts/gate.py [--root DIR]   (DIR defaults to repo root)
"""
import argparse
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


def check1(feed, schema):
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
    return errs


def check2(root, feed):
    """Determinism: re-emit from records.json; must be byte-identical."""
    sys.path.insert(0, os.path.join(root, 'scripts'))
    from fetch import emit_views  # same code path the producer used
    recs = load(os.path.join(root, 'data', 'records.json'))['records']
    cert = feed['selected_result'] or {}
    f2, c2 = emit_views(recs, cert if cert else None, feed['upstream_main_sha'],
                        feed['generated_at'])
    errs = []
    with open(os.path.join(root, 'docs', 'feed.json'), 'rb') as fh:
        if json.dumps(f2, indent=2, sort_keys=True, ensure_ascii=False).encode() + b'\n' != fh.read():
            errs.append("determinism: docs/feed.json differs from re-emit of data/records.json")
    with open(os.path.join(root, 'docs', 'chart-data.json'), 'rb') as fh:
        if json.dumps(c2, indent=2, sort_keys=True, ensure_ascii=False).encode() + b'\n' != fh.read():
            errs.append("determinism: docs/chart-data.json differs from re-emit of data/records.json")
    return errs


def check3(root, feed):
    """Selected-result binding: feed block must match upstream certificate bytes."""
    errs = []
    cert_path = os.path.join(root, 'data', 'selected-result.json')
    if not os.path.exists(cert_path):
        return ["binding: data/selected-result.json missing (fetch never captured upstream cert)"]
    with open(cert_path, 'rb') as f:
        raw = f.read()
    try:
        sel = json.loads(raw.decode())
    except Exception as e:
        return [f"binding: upstream certificate unparsable: {e}"]
    fb = feed.get('selected_result') or {}
    for field in ('kappa', 'decimal'):
        if fb.get(field) != sel.get(field):
            errs.append(f"binding: selected_result.{field} {fb.get(field)!r} != upstream {sel.get(field)!r}")
    if fb.get('certificate_sha256') != sel.get('certificate_sha256'):
        errs.append("binding: selected_result.certificate_sha256 differs from upstream certificate")
    # every human-verified record must equal the bound kappa exactly
    ck, cd = sel.get('kappa'), sel.get('decimal')
    if ck and cd:
        kn, kd = (int(x) for x in ck.split('/'))
        for r in feed.get('records', []):
            if r['tier'] == 'human-verified' and (r['kappa_num'] != kn or r['kappa_den'] != kd
                                                  or r['kappa_decimal'] != cd):
                errs.append(f"binding: pr {r['pr']} human-verified but does not match certificate kappa/decimal")
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
        '1-schema+agreement': check1(feed, schema),
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
