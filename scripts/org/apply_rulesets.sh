#!/usr/bin/env bash
# Apply Foundation0's branch and tag rulesets (see REPO-PROTECTION.md).
#
# Run by a human organisation owner, with the GitHub CLI logged in as that owner.
# Dry run by default: it prints what it would do and changes nothing.
#
#   scripts/org/apply_rulesets.sh                 # dry run
#   scripts/org/apply_rulesets.sh --apply         # create or update the rulesets
#   scripts/org/apply_rulesets.sh --verify        # show the rules now in force on each default branch
#   scripts/org/apply_rulesets.sh --org NAME      # another organisation (default Foundation-0)
#
# It first tries organisation-level rulesets, which cover every repository, including ones created
# later. If the organisation's plan does not offer them, it falls back to one ruleset per repository.
# Re-running is safe: a ruleset with the same name is updated, not duplicated.
# To roll back, set "enforcement" to "disabled" in the JSON files and run --apply again.
set -euo pipefail

ORG=Foundation-0
MODE=dry-run
while [ $# -gt 0 ]; do
  case "$1" in
    --apply) MODE=apply ;;
    --verify) MODE=verify ;;
    --org) ORG="$2"; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

command -v gh >/dev/null || { echo "needs the GitHub CLI (gh)" >&2; exit 1; }
command -v jq >/dev/null || { echo "needs jq" >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "log in first: gh auth login" >&2; exit 1; }

DIR=$(cd "$(dirname "$0")" && pwd)
FILES=("$DIR/ruleset-default-branch.json" "$DIR/ruleset-release-tags.json")
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

repos() {
  gh api "orgs/$ORG/repos" --paginate \
    --jq '.[] | select(.archived | not) | [.name, .default_branch, .visibility] | @tsv'
}

if [ "$MODE" = verify ]; then
  repos | while IFS=$'\t' read -r name branch visibility; do
    rules=$(gh api "repos/$ORG/$name/rules/branches/$branch" --jq '[.[].type] | unique | join(",")' 2>/dev/null || echo "?")
    printf '%-28s %-8s %-7s %s\n' "$name" "$visibility" "$branch" "${rules:-NONE}"
  done
  exit 0
fi

# upsert BASE FILE: create the ruleset named in FILE under BASE (orgs/X or repos/X/Y), or update it.
upsert() {
  local base=$1 file=$2 name id
  name=$(jq -r .name "$file")
  id=$(gh api "$base/rulesets" --paginate --jq ".[] | select(.name == \"$name\") | .id" 2>/dev/null | head -n1 || true)
  if [ "$MODE" != apply ]; then
    echo "dry run: would $([ -n "$id" ] && echo "update ruleset $id" || echo create) '$name' on $base"
    return 0
  fi
  if [ -n "$id" ]; then
    gh api -X PUT "$base/rulesets/$id" --input "$file" >/dev/null && echo "updated '$name' on $base"
  else
    gh api -X POST "$base/rulesets" --input "$file" >/dev/null && echo "created '$name' on $base"
  fi
}

# 1. Organisation-level rulesets.
org_ok=1
for f in "${FILES[@]}"; do
  if ! upsert "orgs/$ORG" "$f"; then org_ok=0; break; fi
done
if [ "$MODE" != apply ] && ! gh api "orgs/$ORG/rulesets" >/dev/null 2>&1; then org_ok=0; fi

if [ "$org_ok" = 1 ]; then
  if [ "$MODE" = apply ]; then
    echo "organisation-level rulesets: done. Check with --verify."
  else
    echo "dry run: organisation-level rulesets look available. Run with --apply to create them."
  fi
  exit 0
fi

# 2. Fallback: one ruleset per repository (repository rulesets take no repository_name condition).
echo "organisation-level rulesets not available here; applying per repository."
for f in "${FILES[@]}"; do
  jq 'del(.conditions.repository_name)' "$f" > "$TMP/$(basename "$f")"
done
failed=()
while IFS=$'\t' read -r name branch visibility; do
  for f in "${FILES[@]}"; do
    upsert "repos/$ORG/$name" "$TMP/$(basename "$f")" || failed+=("$name ($visibility)")
  done
done < <(repos)

if [ ${#failed[@]} -gt 0 ]; then
  printf 'could not apply to: %s\n' "${failed[@]}" | sort -u
  echo "Private repositories may need a paid plan for rulesets; protect them by hand or make the plan change."
  exit 1
fi
if [ "$MODE" = apply ]; then
  echo "per-repository rulesets: done. Check with --verify."
else
  echo "dry run complete. Run with --apply to create them."
fi
