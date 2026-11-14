#!/usr/bin/env bash
# List force pushes in Foundation0's repositories and check whether the commits they overwrote can
# still be recovered from GitHub (see REPO-PROTECTION.md).
#
# Needs the GitHub CLI logged in with read access; an owner also sees private repositories.
# Read-only unless you pass --rescue.
#
#   scripts/org/find_force_pushes.sh                      # every repository, as far back as GitHub keeps
#   scripts/org/find_force_pushes.sh --since 2026-11-01   # only force pushes on or after this date (UTC)
#   scripts/org/find_force_pushes.sh --repo gravity       # one repository (repeatable)
#   scripts/org/find_force_pushes.sh --org NAME           # another organisation (default Foundation-0)
#   scripts/org/find_force_pushes.sh --rescue             # also create a branch rescue/<date>-<sha> at each
#                                                         # overwritten commit that is still on GitHub and not on
#                                                         # the default branch, so it can't be garbage-collected
#
# Output is tab-separated, one row per force push:
#   repo  ref  pushed_at  actor  before  after  lost_vs_branch  lost_vs_default  recoverable
# lost_vs_branch:  commits in the overwritten tip that the new tip doesn't have.
# lost_vs_default: of those, commits the default branch doesn't have either (the real loss).
# recoverable:     yes if GitHub still serves the overwritten commit; no if it is gone.
set -euo pipefail

ORG=Foundation-0
SINCE=""
REPOS=()
RESCUE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --since) SINCE="$2"; shift ;;
    --repo) REPOS+=("$2"); shift ;;
    --org) ORG="$2"; shift ;;
    --rescue) RESCUE=1 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
  shift
done

command -v gh >/dev/null || { echo "needs the GitHub CLI (gh)" >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "log in first: gh auth login" >&2; exit 1; }

if [ ${#REPOS[@]} -eq 0 ]; then
  mapfile -t REPOS < <(gh api "orgs/$ORG/repos" --paginate --jq '.[].name')
fi

found=0; lost_total=0; gone=0; rescued=0
printf 'repo\tref\tpushed_at\tactor\tbefore\tafter\tlost_vs_branch\tlost_vs_default\trecoverable\n'
for repo in "${REPOS[@]}"; do
  default=$(gh api "repos/$ORG/$repo" --jq .default_branch 2>/dev/null) || { echo "cannot read $repo" >&2; continue; }
  events=$(gh api "repos/$ORG/$repo/activity?activity_type=force_push&per_page=100" --paginate \
    --jq '.[] | [.ref, .timestamp, (.actor.login // "?"), .before, .after] | @tsv' 2>/dev/null) || {
    echo "cannot list activity for $repo" >&2; continue; }
  [ -z "$events" ] && continue
  while IFS=$'\t' read -r ref when actor before after; do
    if [ -n "$SINCE" ] && [[ "$when" < "$SINCE" ]]; then continue; fi
    found=$((found + 1))
    # compare/BASE...HEAD: ahead_by counts commits in HEAD that BASE doesn't have.
    if vs_branch=$(gh api "repos/$ORG/$repo/compare/$after...$before" --jq .ahead_by 2>/dev/null); then
      recoverable=yes
      vs_default=$(gh api "repos/$ORG/$repo/compare/$default...$before" --jq .ahead_by 2>/dev/null || echo "?")
    else
      recoverable=no; vs_branch="?"; vs_default="?"; gone=$((gone + 1))
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
      "$repo" "$ref" "$when" "$actor" "$before" "$after" "$vs_branch" "$vs_default" "$recoverable"
    if [ "$recoverable" = yes ] && [ "$vs_default" != "?" ] && [ "$vs_default" -gt 0 ]; then
      lost_total=$((lost_total + 1))
      if [ "$RESCUE" = 1 ]; then
        name="rescue/${when:0:10}-${before:0:7}"
        if gh api -X POST "repos/$ORG/$repo/git/refs" -f ref="refs/heads/$name" -f sha="$before" >/dev/null 2>&1; then
          echo "rescued $repo $before as $name" >&2; rescued=$((rescued + 1))
        else
          echo "could not create $name in $repo (it may exist already)" >&2
        fi
      fi
    fi
  done <<< "$events"
done

{
  echo "force pushes found: $found"
  echo "overwritten work still on GitHub and not on the default branch: $lost_total"
  echo "overwritten commits GitHub no longer serves: $gone (look in agents' local clones: find_lost_local.sh)"
  if [ "$RESCUE" = 1 ]; then echo "rescue branches created: $rescued"; fi
} >&2
