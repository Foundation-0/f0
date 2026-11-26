#!/usr/bin/env bash
# Apply Foundation0's branch and tag rulesets (see REPO-PROTECTION.md).
#
# Run by a human organisation owner, with the GitHub CLI logged in as that owner. The organisation
# rulesets API needs the admin:org scope, which a default `gh auth login` does not grant. Add it with:
#   gh auth refresh -h github.com -s admin:org
# Dry run by default: it prints what it would do and changes nothing.
#
#   scripts/org/apply_rulesets.sh                 # dry run
#   scripts/org/apply_rulesets.sh --apply         # create or update the rulesets
#   scripts/org/apply_rulesets.sh --verify        # report what is in force; exit 1 if anything is wrong
#   scripts/org/apply_rulesets.sh --per-repo      # one ruleset per repository instead (with or without --apply)
#   scripts/org/apply_rulesets.sh --org NAME      # another organisation (default Foundation-0)
#   scripts/org/apply_rulesets.sh --help          # this text
#
# Organisation-level rulesets cover every repository, including ones created later, and only
# organisation owners can change them. Per-repository rulesets can be edited or deleted by any
# repository admin, so they protect nothing against an agent account that holds admin: use --per-repo
# only if the plan does not offer organisation rulesets, and demote agent accounts to Write first
# (REPO-PROTECTION.md section 2). The script never switches to per-repository rulesets by itself: if
# it cannot read the organisation's rulesets, it stops and says why. A 404/403 while the login lacks
# admin:org is the missing scope (gh auth refresh -h github.com -s admin:org); only a refusal with the
# scope present is a plan limitation.
# Re-running is safe: a ruleset with the same name is updated, not duplicated.
# To roll back, set "enforcement" to "disabled" in the JSON files and run --apply again.
set -euo pipefail

usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; }
value() { [ -n "${2:-}" ] || { echo "$1 needs a value" >&2; usage >&2; exit 2; }; }

ORG=Foundation-0
MODE=dry-run
PER_REPO=0
while [ $# -gt 0 ]; do
  case "$1" in
    --apply) MODE=apply ;;
    --verify) MODE=verify ;;
    --per-repo) PER_REPO=1 ;;
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

# Why the organisation rulesets endpoint refused, and what to do about it. Stops the script: a
# refusal is either the missing admin:org scope or a genuine plan limitation, never a silent
# switch to per-repository rulesets.
org_refused() {
  local err=${1:-no answer} auth scopes status
  echo "cannot read the rulesets of organisation $ORG:" >&2
  sed 's/^/  /' <<<"$err" >&2
  auth=$(gh auth status 2>&1 || true)
  scopes=$(grep -i 'token' <<<"$auth" || true)
  status=$(grep -oE 'HTTP [0-9]{3}' <<<"$err" | head -n1)
  if grep -qiE 'admin:org|scope' <<<"$err" || { [ -n "$scopes" ] && ! grep -q 'admin:org' <<<"$auth"; }; then
    # A default gh login grants gist, read:org, repo and workflow, not admin:org, and this endpoint
    # answers 404/403 either way: without the scope the refusal is the scope, not the plan.
    echo "That refusal is the missing admin:org scope, not the organisation's plan: this API needs" >&2
    echo "admin:org, which a default gh auth login does not grant. Add the scope and run again:" >&2
    echo "  gh auth refresh -h github.com -s admin:org" >&2
  elif [ -n "$scopes" ] && grep -q 'admin:org' <<<"$auth" && { [ "$status" = "HTTP 404" ] || [ "$status" = "HTTP 403" ]; }; then
    # The scope is present, so a 404/403 is a real limitation: the plan offers no organisation
    # rulesets, or this login is not an organisation owner.
    echo "The login carries admin:org, so this $status is not the scope: the organisation's plan does" >&2
    echo "not offer organisation rulesets, or the login is not an organisation owner. Organisation" >&2
    echo "rulesets are the only kind a repository admin cannot edit or delete. If the plan truly" >&2
    echo "lacks them, the fallback is per-repository rulesets, which any repository admin can remove:" >&2
    echo "pass --per-repo explicitly, after demoting agent accounts to Write (REPO-PROTECTION.md" >&2
    echo "section 2). This script never switches on its own." >&2
  else
    echo "If the login lacks the admin:org scope, add it and run again:" >&2
    echo "  gh auth refresh -h github.com -s admin:org" >&2
    echo "Otherwise the organisation's plan does not offer organisation rulesets; the only fallback is" >&2
    echo "--per-repo (any repository admin can edit those), and this script never switches on its own." >&2
  fi
  exit 3
}

if [ "$MODE" = verify ]; then
  problems=0
  warn() { echo "  PROBLEM: $*"; problems=$((problems + 1)); }

  echo "== organisation rulesets ($ORG)"
  if org_list=$(gh api "orgs/$ORG/rulesets" --paginate --jq '.[] | [.id, .name, .target, .enforcement] | @tsv' 2>"$TMP/err"); then
    [ -n "$org_list" ] || warn "no organisation rulesets"
    while IFS=$'\t' read -r id name target enforcement; do
      [ -n "$id" ] || continue
      bypass=$(gh api "orgs/$ORG/rulesets/$id" --jq '[.bypass_actors[]? | "\(.actor_type)/\(.actor_id // "-")/\(.bypass_mode)"] | join(" ")' 2>/dev/null || echo "?")
      printf '  %-24s target=%-7s enforcement=%-8s bypass=[%s]\n' "$name" "$target" "$enforcement" "$bypass"
      [ "$enforcement" = active ] || warn "'$name' is not active"
      [ -z "$bypass" ] || warn "'$name' has bypass actors: $bypass"
    done <<<"$org_list"
  else
    warn "cannot read organisation rulesets: $(head -n1 "$TMP/err") (needs the admin:org scope)"
  fi

  owners=$(gh api "orgs/$ORG/members?role=admin" --paginate --jq '.[].login' 2>/dev/null || true)
  echo "== default branches"
  while IFS=$'\t' read -r name branch visibility; do
    echo "$name ($visibility, $branch)"
    rules=$(gh api "repos/$ORG/$name/rules/branches/$branch" \
      --jq '[.[] | "\(.type)[\(.ruleset_source_type // "?")]"] | unique | join(",")' 2>/dev/null || echo "?")
    echo "  rules in force: ${rules:-none}"
    case ",$rules," in *",pull_request[Organization],"*) ;; *) warn "no organisation-level pull_request rule on $branch" ;; esac
    case "$rules" in *"[Repository]"*) warn "rules from a repository ruleset, which a repository admin can remove" ;; esac
    while IFS=$'\t' read -r id rname enforcement; do
      [ -n "$id" ] || continue
      bypass=$(gh api "repos/$ORG/$name/rulesets/$id" --jq '[.bypass_actors[]? | "\(.actor_type)/\(.actor_id // "-")/\(.bypass_mode)"] | join(" ")' 2>/dev/null || echo "?")
      echo "  repository ruleset: $rname enforcement=$enforcement bypass=[$bypass]"
      [ -z "$bypass" ] || warn "repository ruleset '$rname' has bypass actors"
    done < <(gh api "repos/$ORG/$name/rulesets?includes_parents=false" --jq '.[] | [.id, .name, .enforcement] | @tsv' 2>/dev/null || true)
    admins=$(gh api "repos/$ORG/$name/collaborators?permission=admin" --paginate --jq '.[].login' 2>/dev/null \
      | while IFS= read -r login || [ -n "$login" ]; do grep -qx "$login" <<<"$owners" || echo "$login"; done \
      | paste -sd, - || true)
    if [ -n "$admins" ]; then warn "admins who are not organisation owners: $admins"; fi
  done < <(repos)

  if [ "$problems" -gt 0 ]; then echo "verify: $problems problem(s)"; exit 1; fi
  echo "verify: no problems found"
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

# 1. Organisation-level rulesets (the default). Read them first, so a dry run prints only a plan it
#    can follow, and a missing scope stops the run instead of silently switching to per-repository.
if [ "$PER_REPO" = 0 ]; then
  gh api "orgs/$ORG/rulesets" >/dev/null 2>"$TMP/err" || org_refused "$(cat "$TMP/err")"
  failed=()
  for f in "${FILES[@]}"; do
    upsert "orgs/$ORG" "$f" || failed+=("$(jq -r .name "$f")")
  done
  if [ ${#failed[@]} -gt 0 ]; then
    echo "could not apply at organisation level: $(printf '%s\n' "${failed[@]}" | paste -sd, -). Nothing was applied per repository." >&2
    exit 1
  fi
  if [ "$MODE" = apply ]; then
    echo "organisation-level rulesets: done. Check with --verify."
  else
    echo "dry run: organisation-level rulesets. Run with --apply to create them."
  fi
  exit 0
fi

# 2. --per-repo: one ruleset per repository (repository rulesets take no repository_name condition).
echo "per-repository rulesets (--per-repo). Any repository admin can edit or delete these:"
echo "demote agent accounts to Write first (REPO-PROTECTION.md section 2), and check with --verify."
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
