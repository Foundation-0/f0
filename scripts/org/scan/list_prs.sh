#!/usr/bin/env bash
# Write the pull request lists the scans read, one TSV per state, for every mirror in --dir.
#
#   scripts/org/scan/list_prs.sh --org Foundation-0 --dir mirrors --out lists
#
# lists/merged.tsv           repo  number  author  created  merged  title
# lists/closed_unmerged.tsv  repo  number  author  created  closed  title
# lists/open.tsv             repo  number  author  created  draft   title
#
# Uses the GitHub search API through `gh`, one query per repository and state, with a pause between
# queries to stay under the search rate limit. Search returns at most 1,000 results per query.
set -euo pipefail

usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; }
value() { [ -n "${2:-}" ] || { echo "$1 needs a value" >&2; usage >&2; exit 2; }; }

ORG="Foundation-0"; DIR="mirrors"; OUT="lists"
while [ $# -gt 0 ]; do
  case "$1" in
    --org) value "$@"; ORG="$2"; shift 2 ;;
    --dir) value "$@"; DIR="$2"; shift 2 ;;
    --out) value "$@"; OUT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done
mkdir -p "$OUT"
: > "$OUT/merged.tsv"; : > "$OUT/closed_unmerged.tsv"; : > "$OUT/open.tsv"

q() {  # repo, query qualifiers, jq expression for column 5, output file
  gh api -X GET search/issues -f q="repo:$ORG/$1 is:pr $2" -f per_page=100 --paginate \
    --jq ".items[] | [\"$1\", .number, .user.login, .created_at[0:10], $3, (.title | gsub(\"[\\t\\n]\"; \" \"))] | @tsv" >> "$4"
  sleep 2.5
}

for m in "$DIR"/*.git; do
  r="$(basename "$m" .git)"
  echo "$r" >&2
  q "$r" "is:merged" '.pull_request.merged_at[0:16]' "$OUT/merged.tsv"
  q "$r" "is:closed is:unmerged" '.closed_at[0:16]' "$OUT/closed_unmerged.tsv"
  q "$r" "is:open" '(.draft | tostring)' "$OUT/open.tsv"
done
wc -l "$OUT"/*.tsv >&2
