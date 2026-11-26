#!/bin/bash
# Screen Logan assemblies of SRA runs for marker k-mers (e.g. HPV18, the HeLa marker).
# Usage: screen_runs.sh RUNS.txt OUTDIR REF1.fa [REF2.fa ...]
#   RUNS.txt: one SRA run accession per line. Each run's unitigs are fetched from the public Logan bucket,
#   scanned with kmer_hits.py, and deleted. Results: OUTDIR/results.tsv (run, then per reference: hits/total, fraction).
# Needs: curl, python3 with zstandard.
set -u
RUNS="$1"; OUT="$2"; shift 2
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"; : > "$OUT/results.tsv"
while read -r acc; do
  [ -z "$acc" ] && continue
  f="$OUT/$acc.unitigs.fa.zst"
  if ! curl -sS -f -o "$f" "https://logan-pub.s3.amazonaws.com/u/$acc/$acc.unitigs.fa.zst"; then echo -e "$acc\tNA" >> "$OUT/results.tsv"; continue; fi
  r=$(python3 -I "$HERE/kmer_hits.py" "$f" "$@" | tr '\n' ' ')
  echo -e "$acc\t$r" >> "$OUT/results.tsv"
  rm -f "$f"
done < "$RUNS"
