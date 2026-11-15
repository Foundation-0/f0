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
#   scripts/org/apply_rulesets.sh --help          # this text
#
# It first checks whether the organisation's plan offers organisation-level rulesets, which cover every
# repository, including ones created later. If it does not, or a ruleset fails at that level, that
# ruleset is applied to each repository instead.
# Re-running is safe: a ruleset with the same name is updated, not duplicated.
# To roll back, set "enforcement" to "disabled" in the JSON files and run --apply again.
set -euo pipefail

usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; }
value() { [ -n "${2:-}" ] || { echo "$1 needs a value" >&2; usage >&2; exit 2; }; }

ORG=Foundation-0
MODE=dry-run
while [ $# -gt 0 ]; do
  case "$1" in
    --apply) MODE=apply ;;
    --verify) MODE=verify ;;
    --org) value "$@"; ORG="$2"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
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

# 1. Organisation-level rulesets, if the organisation's plan offers them. Check that first, so a dry
#    run prints only the plan it would follow.
PENDING=("${FILES[@]}")
if gh api "orgs/$ORG/rulesets" >/dev/null 2>&1; then
  PENDING=()
  for f in "${FILES[@]}"; do
    upsert "orgs/$ORG" "$f" || PENDING+=("$f")
  done
  if [ ${#PENDING[@]} -eq 0 ]; then
    if [ "$MODE" = apply ]; then
      echo "organisation-level rulesets: done. Check with --verify."
    else
      echo "dry run: organisation-level rulesets are available. Run with --apply to create them."
    fi
    exit 0
  fi
  # Only the rulesets that failed at organisation level go on to each repository.
  echo "could not apply at organisation level: $(for f in "${PENDING[@]}"; do jq -r .name "$f"; done | paste -sd, -); applying those per repository."
else
  echo "organisation-level rulesets not available here; applying per repository."
fi

# 2. Fallback: one ruleset per repository (repository rulesets take no repository_name condition).
for f in "${PENDING[@]}"; do
  jq 'del(.conditions.repository_name)' "$f" > "$TMP/$(basename "$f")"
done
failed=()
while IFS=$'\t' read -r name branch visibility; do
  for f in "${PENDING[@]}"; do
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
