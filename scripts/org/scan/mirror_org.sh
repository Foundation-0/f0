#!/usr/bin/env bash
# Create or update blobless mirrors of an organisation's repositories, including pull request refs.
#
#   scripts/org/scan/mirror_org.sh --org Foundation-0 --dir mirrors            # every public repository
#   scripts/org/scan/mirror_org.sh --org Foundation-0 --dir mirrors --repo gravity --repo f0
#
# Needs git and the GitHub CLI (`gh`, for the repository list). Mirrors are bare and blobless: file
# contents are fetched on demand when a scan reads them. A mirror clone keeps refs/pull/*, which the
# scans use to tell how each commit reached the default branch.
set -euo pipefail

ORG="Foundation-0"; DIR="mirrors"; REPOS=(); PRIVATE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --org) ORG="$2"; shift 2 ;;
    --dir) DIR="$2"; shift 2 ;;
    --repo) REPOS+=("$2"); shift 2 ;;
    --include-private) PRIVATE=1; shift ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [ ${#REPOS[@]} -eq 0 ]; then
  # Search hides forks unless asked, so list sources and forks separately.
  vis='select(.visibility == "public")'
  if [ "$PRIVATE" = 1 ]; then vis='.'; fi
  while IFS= read -r r; do REPOS+=("$r"); done < <(
    { gh api -X GET search/repositories -f q="org:$ORG" -f per_page=100 --paginate --jq ".items[] | $vis | .name"
      gh api -X GET search/repositories -f q="org:$ORG fork:only" -f per_page=100 --paginate --jq ".items[] | $vis | .name"
    } | sort -u)
fi

mkdir -p "$DIR"
for r in "${REPOS[@]}"; do
  m="$DIR/$r.git"
  if [ -d "$m" ]; then
    echo "update $r" >&2
    git -C "$m" fetch --prune --quiet origin
  else
    echo "clone  $r" >&2
    git clone --quiet --mirror --filter=blob:none "https://github.com/$ORG/$r.git" "$m"
  fi
done
echo "${#REPOS[@]} mirrors in $DIR" >&2
