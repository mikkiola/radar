#!/usr/bin/env bash
# Installs the versioned git hooks from scripts/hooks/ into this repository's
# hooks directory and thereby activates the .tooltempest.lock integrity guard
# (docs/adr/0025-tooltempest-lock-integrity-guard.md). Human-triggered only;
# nothing runs it automatically.
#
# Safety properties (each is covered by tests/test_install_hooks.py):
#   - Preflight first: nothing is written until every check has passed,
#     including "the vendored file is materialized and matches the lock".
#   - An existing hook that differs is backed up as <hook>.pre-lockguard-backup.
#     An existing backup is never overwritten: if it differs from the hook it
#     would protect, the install is refused.
#   - New hook bodies are staged as temporary files first; any failure removes
#     them and changes nothing.
#   - If replacing the second hook fails after the first was replaced, the
#     first is restored from its backup (or removed if it did not exist).
#   - Re-running when everything is already installed changes nothing.
#   - Hooks that are not managed here are never read or modified.
# Limitation: the two renames are not one atomic step. If the process is killed
# between them, the previous hooks are in the backups; the manual restore
# commands are printed before any change is made.
set -euo pipefail

SELF_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SELF_DIR/.." && pwd)"
SOURCE_DIR="$REPO_ROOT/scripts/hooks"
HOOKS=(pre-commit pre-push)
SUFFIX=".pre-lockguard-backup"

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

hooks_dir="$(git -C "$REPO_ROOT" rev-parse --git-path hooks)" || fail "not a git repository: $REPO_ROOT"
case "$hooks_dir" in
  /*) ;;
  *) hooks_dir="$REPO_ROOT/$hooks_dir" ;;
esac

# --- preflight (no writes) -------------------------------------------------
[ -d "$hooks_dir" ] || fail "hooks directory not found: $hooks_dir"
[ ! -L "$hooks_dir" ] || fail "hooks directory is a symlink: $hooks_dir"
[ -w "$hooks_dir" ] || fail "hooks directory is not writable: $hooks_dir (no hooks were changed)"

if ! python3 "$SELF_DIR/check_tooltempest_lock.py" --repo-root "$REPO_ROOT"; then
  fail "the guard cannot be activated: the vendored file named by .tooltempest.lock must be materialized and match the lock first. See docs/adr/0025-tooltempest-lock-integrity-guard.md (Materialization procedure). No hooks were changed."
fi

STATES=()
for hook in "${HOOKS[@]}"; do
  src="$SOURCE_DIR/$hook"
  target="$hooks_dir/$hook"
  backup="$target$SUFFIX"
  [ -f "$src" ] || fail "versioned hook source not found: $src"
  for path in "$target" "$backup"; do
    [ ! -L "$path" ] || fail "refusing to touch a symlink: $path"
    if [ -e "$path" ] && [ ! -f "$path" ]; then
      fail "refusing to touch a non-regular file: $path"
    fi
  done
  if [ ! -e "$target" ]; then
    STATES+=("absent")
  elif cmp -s "$src" "$target"; then
    STATES+=("identical")
  else
    STATES+=("differs")
    if [ -e "$backup" ] && ! cmp -s "$target" "$backup"; then
      fail "backup $backup already exists and differs from the current $hook; refusing to overwrite it (inspect both, move one aside, then re-run). No hooks were changed."
    fi
  fi
done

pending=0
for state in "${STATES[@]}"; do
  [ "$state" = "identical" ] || pending=$((pending + 1))
done
if [ "$pending" -eq 0 ]; then
  echo "OK: hooks already installed; nothing changed."
  exit 0
fi

echo "Installing hooks into $hooks_dir"
echo "To restore a previous hook manually: cp -p <hook>$SUFFIX <hook>   (or delete the hook for Git's default behavior)"
for i in "${!HOOKS[@]}"; do
  if [ "${STATES[$i]}" = "differs" ]; then
    echo "  cp -p '$hooks_dir/${HOOKS[$i]}$SUFFIX' '$hooks_dir/${HOOKS[$i]}'"
  fi
done

# --- stage new bodies (temp files only) ------------------------------------
TMPS=()
cleanup() {
  if [ "${#TMPS[@]}" -gt 0 ]; then
    rm -f "${TMPS[@]}"
  fi
}
trap cleanup EXIT

for i in "${!HOOKS[@]}"; do
  [ "${STATES[$i]}" = "identical" ] && continue
  tmp="$hooks_dir/.${HOOKS[$i]}.new.$$"
  TMPS+=("$tmp")
  cp "$SOURCE_DIR/${HOOKS[$i]}" "$tmp" || fail "could not stage ${HOOKS[$i]}; no hooks were changed"
  chmod 755 "$tmp" || fail "could not chmod the staged ${HOOKS[$i]}; no hooks were changed"
done

# --- backups (never overwrite) ---------------------------------------------
for i in "${!HOOKS[@]}"; do
  [ "${STATES[$i]}" = "differs" ] || continue
  target="$hooks_dir/${HOOKS[$i]}"
  backup="$target$SUFFIX"
  if [ ! -e "$backup" ]; then
    cp -p "$target" "$backup" || fail "could not create backup $backup; no hooks were changed"
    cmp -s "$target" "$backup" || { rm -f "$backup"; fail "backup of ${HOOKS[$i]} did not verify; no hooks were changed"; }
  fi
done

# --- replace, with rollback --------------------------------------------------
INSTALLED=()
rollback() {
  echo "ROLLBACK: restoring the previous hooks" >&2
  local n=${#INSTALLED[@]} j k hook target backup restore
  for ((j = 0; j < n; j++)); do
    hook="${INSTALLED[$j]}"
    target="$hooks_dir/$hook"
    backup="$target$SUFFIX"
    for k in "${!HOOKS[@]}"; do
      [ "${HOOKS[$k]}" = "$hook" ] || continue
      if [ "${STATES[$k]}" = "absent" ]; then
        rm -f "$target" || echo "ROLLBACK FAILED for $hook: remove $target manually" >&2
      else
        restore="$hooks_dir/.$hook.restore.$$"
        if cp -p "$backup" "$restore" && mv -f "$restore" "$target"; then
          echo "restored $hook from $backup" >&2
        else
          rm -f "$restore"
          echo "ROLLBACK FAILED for $hook: run: cp -p '$backup' '$target'" >&2
        fi
      fi
    done
  done
}

for i in "${!HOOKS[@]}"; do
  [ "${STATES[$i]}" = "identical" ] && continue
  hook="${HOOKS[$i]}"
  if ! mv -f "$hooks_dir/.$hook.new.$$" "$hooks_dir/$hook"; then
    if [ "${#INSTALLED[@]}" -gt 0 ]; then
      rollback
    fi
    fail "could not install $hook; previous hooks were restored (backups kept)"
  fi
  INSTALLED+=("$hook")
done

echo "OK: lock integrity guard hooks installed and active in $hooks_dir."
exit 0
