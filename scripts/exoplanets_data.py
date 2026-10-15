#!/usr/bin/env python3
"""Rebuild docs/research/exoplanets/candidates.json from eumemic/exoplanets at one commit.

The exoplanets page draws its sky map, tier counts and table from this compact file. It holds the
counted candidates only (tiers A, B, N and L1, the ones the project's README counts), one column per
field, read straight from the project's own published tables:

  results_public/candidates_allsky.csv        the full-sky search          (set 0)
  results_public/tiers_earlier_candidates.csv the earlier searches         (set 1)
  candidates/ephemerides.csv                  ra, dec, Tmag and depth for each candidate_id

Usage (needs a clone of https://github.com/eumemic/exoplanets with the commit fetched):
  git -C /path/to/exoplanets fetch --depth 50 origin main
  python3 scripts/exoplanets_data.py /path/to/exoplanets 58c6318
then run `node scripts/prerender.mjs` so the page's no-JavaScript copy follows.

Files are read with `git show COMMIT:path`, so the clone's working tree does not matter.
Data CC BY 4.0, eumemic. Standard library only.
"""
import csv
import io
import json
import os
import statistics
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'research', 'exoplanets', 'candidates.json')
TIERS = ['A', 'B', 'N', 'L1']


def git(repo, *args):
    return subprocess.run(['git', '-C', repo] + list(args), check=True, capture_output=True, text=True).stdout


def table(repo, commit, path):
    return list(csv.DictReader(io.StringIO(git(repo, 'show', f'{commit}:{path}'))))


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    repo, commit = sys.argv[1], sys.argv[2]
    full = git(repo, 'rev-parse', commit).strip()
    date = git(repo, 'show', '-s', '--format=%cs', full).strip()
    allsky = table(repo, full, 'results_public/candidates_allsky.csv')
    earlier = table(repo, full, 'results_public/tiers_earlier_candidates.csv')
    eph_rows = table(repo, full, 'candidates/ephemerides.csv')
    eph = {r['candidate_id']: r for r in eph_rows if r.get('candidate_id')}
    by_tic = {}
    for r in eph_rows:
        by_tic.setdefault(int(r['TIC']), []).append(r)

    def ephemeris(r):
        """(ephemeris row, same fit?). By candidate_id where both tables have it (from 14 Oct 2026);
        older commits have no candidate_id, so the same star's row with the nearest period. If that
        period differs (another fit of the signal), only the star's own values (ra, dec, Tmag) are used."""
        if r.get('candidate_id') in eph:
            return eph[r['candidate_id']], True
        P = float(r['P_d'])
        near = sorted(by_tic.get(int(r['TIC']), []), key=lambda e: abs(float(e['period_d']) - P))
        if not near:
            return None, False
        return near[0], abs(float(near[0]['period_d']) - P) < 1e-3 * P

    rows = [(0, r) for r in allsky if r['tier'] in TIERS] + [(1, r) for r in earlier if r['tier'] in TIERS]
    cols = {k: [] for k in ('tic', 'tier', 'ra', 'dec', 'P', 'rp', 'depth', 'tmag', 'set')}
    missing = []
    for s, r in rows:
        e, same = ephemeris(r)
        if e is None or not (same or r.get('depth_ppm')):
            missing.append(r.get('candidate_id') or f"TIC{r['TIC']} P={r['P_d']}")
            continue
        cols['tic'].append(int(r['TIC']))
        cols['tier'].append(TIERS.index(r['tier']))
        cols['ra'].append(round(float(e['ra']), 3))
        cols['dec'].append(round(float(e['dec']), 3))
        cols['P'].append(round(float(r['P_d']), 4))
        cols['rp'].append(round(float(r['Rp_Re']), 2))
        cols['depth'].append(int(round(float(e['depth_ppm'] if same else r['depth_ppm']))))
        cols['tmag'].append(round(float(e['Tmag']), 2))
        cols['set'].append(s)
    if missing:
        sys.exit(f'{len(missing)} counted candidates have no row in candidates/ephemerides.csv: {missing[:5]}')

    n = len(cols['tic'])
    by_set = [cols['set'].count(0), cols['set'].count(1)]
    d = {
        'about': (f'The {n} counted candidates (tiers A, B, N, L1) of eumemic/exoplanets at commit {full[:7]} ({date}): '
                  'results_public/candidates_allsky.csv (set 0) and results_public/tiers_earlier_candidates.csv (set 1); '
                  'ra, dec (degrees, J2000), Tmag and depth (ppm) from candidates/ephemerides.csv. tier indexes A,B,N,L1. '
                  'Built by scripts/exoplanets_data.py. Data CC BY 4.0, eumemic.'),
        'commit': full[:7],
        'date': date,
        'tiers': TIERS,
        'n': n,
        'by_set': by_set,
        'by_tier': [cols['tier'].count(i) for i in range(len(TIERS))],
        'stars': len(set(cols['tic'])),
        'median_depth': int(round(statistics.median(cols['depth']))),
    }
    d.update(cols)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, separators=(',', ':'))
    print(f'{os.path.relpath(OUT, ROOT)}: {n} candidates ({by_set[0]} full-sky + {by_set[1]} earlier) on {d["stars"]} stars, '
          f'tiers {dict(zip(TIERS, d["by_tier"]))}, median depth {d["median_depth"]} ppm; eumemic/exoplanets {full[:7]}, {date}')


if __name__ == '__main__':
    main()
