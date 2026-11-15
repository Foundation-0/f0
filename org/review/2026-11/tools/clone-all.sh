#!/bin/bash
# Mirror every public Foundation-0 repository at its default-branch head.
set -u
cd "$(dirname "$0")"
mkdir -p mirrors
gh repo list Foundation-0 --limit 200 --json name,isPrivate,defaultBranchRef \
  --jq '.[] | select(.isPrivate==false) | "\(.name)\t\(.defaultBranchRef.name)"' > repos.tsv

clone_one() {
  name="$1"; branch="$2"
  dest="mirrors/$name"
  if [ -d "$dest/.git" ]; then echo "have $name"; return 0; fi
  git clone --quiet --branch "$branch" "https://github.com/Foundation-0/$name.git" "$dest" 2>&1 | tail -2
  echo "cloned $name"
}
export -f clone_one
# modest parallelism
cat repos.tsv | awk -F'\t' '{print $1" "$2}' | xargs -P 6 -n 2 bash -c 'clone_one "$0" "$1"'

: > heads.tsv
while IFS=$'\t' read -r name branch; do
  sha=$(git -C "mirrors/$name" rev-parse HEAD 2>/dev/null || echo MISSING)
  printf '%s\t%s\t%s\n' "$name" "$branch" "$sha" >> heads.tsv
done < repos.tsv
cat heads.tsv
