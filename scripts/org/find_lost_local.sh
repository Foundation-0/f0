#!/usr/bin/env bash
# Find work that never reached GitHub, or that a force push or reset overwrote, in the local clones
# an agent or a person worked in (see REPO-PROTECTION.md). Run it on each machine or workspace
# where agents ran. Read-only: it changes nothing in the clones.
#
#   scripts/org/find_lost_local.sh DIR...                  # every git clone under each DIR
#   scripts/org/find_lost_local.sh --sha256 HASH DIR...    # also look for files with this SHA-256
#                                                          # (repeatable; e.g. a file a manifest certifies)
#   scripts/org/find_lost_local.sh --help                  # this text
#
# Bare repositories and mirrors (directories named *.git) are checked for orphaned commits and, with
# --sha256, stored blobs; they have no working tree, stash or branches of their own to compare.
# A blobless or partial clone holds only the blobs it has fetched, so --sha256 sees only those.
#
# For each clone it reports:
#   unpushed   local branches with commits that no remote branch has
#   orphaned   the newest commit of each line of work that only the reflog or the object store still
#              holds: left behind by a reset, a rebase, or a fetch after someone force-pushed (the old
#              commits stay until git gc removes them, by default after 30 to 90 days)
#   stashed    stash entries
#   dirty      uncommitted changes in the working tree
#   MATCH      (with --sha256) a working-tree file or any stored blob with that hash
#
# To keep something it finds: git branch rescue/<name> <sha>, push that branch, and open a pull request.
set -euo pipefail

usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; }

HASHES=()
DIRS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --sha256)
      [[ "${2:-}" =~ ^[0-9a-fA-F]{64}$ ]] || { echo "--sha256 needs a 64-character hex hash" >&2; usage >&2; exit 2; }
      HASHES+=("$(echo "$2" | tr 'A-F' 'a-f')"); shift ;;
    -h|--help) usage; exit 0 ;;
    -*) echo "unknown argument: $1" >&2; usage >&2; exit 2 ;;
    *) DIRS+=("$1") ;;
  esac
  shift
done
[ ${#DIRS[@]} -gt 0 ] || { usage >&2; exit 2; }
if [ ${#HASHES[@]} -gt 0 ]; then
  command -v python3 >/dev/null || { echo "--sha256 needs python3" >&2; exit 1; }
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

# Hash every working-tree file (unless bare) and every blob in the object store; print matches.
# Files and blobs are hashed in 1 MiB chunks, so memory use does not grow with their size.
# Arguments: repo, "bare" or "worktree", then the wanted hashes.
FIND_HASHES='
import hashlib, os, subprocess, sys
repo, kind, want = sys.argv[1], sys.argv[2], set(sys.argv[3:])
CHUNK = 2**20
if kind == "worktree":
    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in files:
            path = os.path.join(root, name)
            if os.path.islink(path):
                continue
            h = hashlib.sha256()
            try:
                with open(path, "rb") as fh:
                    for block in iter(lambda: fh.read(CHUNK), b""):
                        h.update(block)
            except OSError:
                continue
            if h.hexdigest() in want:
                print(f"MATCH     {h.hexdigest()}  {path}")
ids = subprocess.run(["git", "-C", repo, "cat-file", "--batch-all-objects", "--unordered",
                      "--batch-check=%(objectname) %(objecttype)"],
                     capture_output=True, text=True).stdout.split("\n")
blobs = [l.split()[0] for l in ids if l.endswith(" blob")]
p = subprocess.Popen(["git", "-C", repo, "cat-file", "--batch"], stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE)
for oid in blobs:
    p.stdin.write((oid + "\n").encode()); p.stdin.flush()
    header = p.stdout.readline().split()
    if len(header) < 3:  # "missing": not in this clone
        continue
    left, h = int(header[2]), hashlib.sha256()
    while left:
        block = p.stdout.read(min(CHUNK, left))
        h.update(block); left -= len(block)
    p.stdout.read(1)
    if h.hexdigest() in want:
        print(f"MATCH     {h.hexdigest()}  blob {oid} (save it with: git cat-file blob {oid} > FILE)")
p.stdin.close(); p.wait()
'

while IFS= read -r found; do
  if [ "$(basename "$found")" = .git ]; then
    repo=$(dirname "$found"); kind=worktree
  elif [ "$(git -C "$found" rev-parse --is-bare-repository 2>/dev/null)" = true ]; then
    repo=$found; kind=bare
  else
    continue  # a directory named *.git that is not a bare repository
  fi
  g() { git -C "$repo" "$@"; }
  echo "== $repo ($(g remote get-url origin 2>/dev/null || echo 'no origin'))$([ "$kind" = bare ] && echo ' [bare]')"

  # Local branches with commits no remote-tracking branch contains. A bare repository or mirror has
  # no remote-tracking branches to compare with, so this check is skipped there.
  if [ "$kind" = worktree ]; then
    while IFS= read -r b; do
      n=$(g rev-list --count "$b" --not --remotes 2>/dev/null || echo 0)
      if [ "$n" -gt 0 ]; then
        echo "unpushed  $b: $n commit(s); newest $(g log -1 --format='%h %cI %s' "$b")"
      fi
    done < <(g for-each-ref --format='%(refname:short)' refs/heads)
  fi

  # Commits held only by reflogs or as dangling objects, not reachable from any ref (branch, tag, stash).
  { g reflog show --all --format='%H' 2>/dev/null || true
    g fsck --no-reflogs --unreachable --no-progress 2>/dev/null | awk '$2 == "commit" {print $3}' || true
  } | sort -u > "$TMP/candidates"
  g rev-list --all 2>/dev/null | sort -u > "$TMP/reachable" || true
  comm -23 "$TMP/candidates" "$TMP/reachable" > "$TMP/orphans"
  # Keep only the tips: an orphan that is an ancestor of another orphan is listed through that one.
  while IFS= read -r c; do
    others=$(grep -vx "$c" "$TMP/orphans" | head -n 1000 || true)
    # shellcheck disable=SC2086
    if [ -n "$others" ] && [ -z "$(g rev-list -n1 "$c" --not $others 2>/dev/null)" ]; then continue; fi
    lost=$(g rev-list --count "$c" --not --all 2>/dev/null || echo "?")
    echo "orphaned  $(g log -1 --format='%h %cI %an: %s' "$c" 2>/dev/null) ($lost commit(s) not on any branch; files: $(g diff-tree --no-commit-id --name-only -r "$c" 2>/dev/null | head -n3 | tr '\n' ' '))"
  done < "$TMP/orphans"

  if [ "$kind" = worktree ]; then
    g stash list --format='stashed   %gd %cI %gs' 2>/dev/null || true
    if [ -n "$(g status --porcelain 2>/dev/null || true)" ]; then
      echo "dirty     $(g status --porcelain | wc -l | tr -d ' ') uncommitted path(s)"
    fi
  fi

  if [ ${#HASHES[@]} -gt 0 ]; then
    python3 -I -c "$FIND_HASHES" "$repo" "$kind" "${HASHES[@]}"
  fi
done < <(find "${DIRS[@]}" \( -name .git -prune -print \) -o \( -type d -name '*.git' -print \) 2>/dev/null)
