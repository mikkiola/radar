#!/usr/bin/env python3
"""Integrity guard for ToolTempest-sourced files pinned in .tooltempest.lock.

Checks one property only: the lock's `sha256` equals the SHA-256 of the file
the lock's `path` names, as materialized in this working tree. It does not
check that the lock's hash equals the upstream file at the pinned commit, and
it does not check whether the pin is current relative to ToolTempest's main.
See docs/adr/0025-tooltempest-lock-integrity-guard.md.

The lock can be read from three places, because Git keeps them independently:
  worktree    the file on disk (default; used for ad-hoc checks)
  index       the staged version (what a commit in progress will contain)
  rev:<sha>   the version in a given commit (what a push will publish)

The vendored file itself is always read from the working tree: it is
deliberately untracked, so there is no other place it can be.

Exit codes:
  0  OK
  1  integrity violation (hash mismatch, vendored file missing/not a regular
     file/a symlink, or the lock was removed: absent from the index, or absent
     at a revision whose history contained it)
  2  error (lock file missing in worktree mode, lock unreadable or malformed,
     unsupported lock schema, git failure, unexpected exception) -- fails
     closed, never treated as a pass
  3  not applicable: rev:<sha> only, and no commit in that revision's history
     ever contained the lock (e.g. the data-only `vault` branch)

Standard library only. No network access. Writes nothing.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

LOCK_NAME = ".tooltempest.lock"
ADR = "docs/adr/0025-tooltempest-lock-integrity-guard.md"
KNOWN_KEYS = {"repository", "commit", "path", "sha256"}
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REV_RE = re.compile(r"^[0-9a-f]{7,64}$")

EXIT_OK, EXIT_VIOLATION, EXIT_ERROR, EXIT_NA = 0, 1, 2, 3


class LockError(Exception):
    """Lock unreadable/malformed or git failed: exit 2."""


class Violation(Exception):
    """Integrity violation: exit 1."""


class NotApplicable(Exception):
    """The revision never carried a lock: exit 3."""


def run_git(root, *args):
    try:
        return subprocess.run(
            ["git", *args], cwd=str(root), capture_output=True, text=True, check=False,
        )
    except OSError as exc:
        raise LockError(f"cannot run git: {exc}")


def read_lock_text(root, source, lock_path=None):
    """Return (lock_text, label) for the requested lock source."""
    if source == "worktree":
        path = Path(lock_path) if lock_path else root / LOCK_NAME
        try:
            return path.read_text(encoding="utf-8"), "worktree"
        except FileNotFoundError:
            raise LockError(f"{path} does not exist")
        except (OSError, UnicodeDecodeError) as exc:
            raise LockError(f"cannot read {path}: {exc}")

    if source == "index":
        staged = run_git(root, "ls-files", "--stage", "--", LOCK_NAME)
        if staged.returncode != 0:
            raise LockError(f"git ls-files failed: {staged.stderr.strip()}")
        if not staged.stdout.strip():
            raise Violation(f"{LOCK_NAME} is not present in the index (staged removal?)")
        shown = run_git(root, "show", f":{LOCK_NAME}")
        if shown.returncode != 0:
            raise LockError(f"cannot read the staged {LOCK_NAME}: {shown.stderr.strip()}")
        return shown.stdout, "index"

    rev = source[len("rev:"):]
    if not REV_RE.match(rev):
        raise LockError(f"invalid revision {rev!r}: expected 7-64 lowercase hex characters")
    tree = run_git(root, "ls-tree", rev, "--", LOCK_NAME)
    if tree.returncode != 0:
        raise LockError(f"cannot resolve revision {rev[:7]}: {tree.stderr.strip()}")
    if not tree.stdout.strip():
        # --full-history: the default simplification can skip a merged side branch that carried the lock
        history = run_git(root, "log", "-1", "--format=%H", "--full-history", rev, "--", LOCK_NAME)
        if history.returncode != 0:
            raise LockError(f"cannot inspect history of {rev[:7]}: {history.stderr.strip()}")
        if history.stdout.strip():
            raise Violation(
                f"{LOCK_NAME} was removed: it exists in the history of {rev[:7]} "
                f"but is absent at the tip"
            )
        raise NotApplicable(
            f"{rev[:7]} has no {LOCK_NAME} anywhere in its history; nothing to verify"
        )
    shown = run_git(root, "show", f"{rev}:{LOCK_NAME}")
    if shown.returncode != 0:
        raise LockError(f"cannot read {LOCK_NAME} at {rev[:7]}: {shown.stderr.strip()}")
    return shown.stdout, f"rev:{rev[:7]}"


def check_relative_path(value):
    if not isinstance(value, str) or not value:
        raise LockError("lock field 'path' must be a non-empty string")
    if value.startswith("/") or "\\" in value or "\0" in value:
        raise LockError(f"lock field 'path' must be a relative POSIX path, got {value!r}")
    if any(part in ("", ".", "..") for part in value.split("/")):
        raise LockError(f"lock field 'path' must not contain empty, '.' or '..' components: {value!r}")


def parse_lock(text):
    """Validate the lock and return its dict. Fails closed on anything unexpected."""
    try:
        data = json.loads(text)
    except ValueError as exc:
        raise LockError(f"lock is not valid JSON: {exc}")
    if not isinstance(data, dict):
        raise LockError("lock must be a JSON object")
    unknown = sorted(set(data) - KNOWN_KEYS)
    if unknown:
        raise LockError(
            f"unsupported lock field(s) {', '.join(unknown)}: this checker verifies only "
            f"{', '.join(sorted(KNOWN_KEYS))}; extend it before extending the lock schema"
        )
    for key in sorted(KNOWN_KEYS):
        if key not in data:
            raise LockError(f"lock field '{key}' is missing")
    if not isinstance(data["repository"], str) or not data["repository"]:
        raise LockError("lock field 'repository' must be a non-empty string")
    if not isinstance(data["commit"], str) or not COMMIT_RE.match(data["commit"]):
        raise LockError("lock field 'commit' must be 40 lowercase hex characters")
    check_relative_path(data["path"])
    if not isinstance(data["sha256"], str) or not SHA256_RE.match(data["sha256"]):
        raise LockError("lock field 'sha256' must be 64 lowercase hex characters")
    return data


def lock_entries(lock):
    """(path, sha256) for every file the lock covers. Today the schema covers one."""
    return [(lock["path"], lock["sha256"])]


def verify_entries(root, entries, label, commit):
    """Return a list of failure messages, one per covered file that does not verify."""
    failures = []
    root = Path(root)
    for rel, expected in entries:
        target = root / rel
        if target.is_symlink():
            failures.append(f"{rel} is a symlink; the guard does not follow symlinks (lock source: {label})")
            continue
        if not target.exists():
            failures.append(
                f"{rel} is not materialized in this working tree (lock source: {label}, pin {commit[:7]})"
            )
            continue
        if not target.is_file():
            failures.append(f"{rel} is not a regular file (lock source: {label})")
            continue
        try:
            resolved = target.resolve()
            resolved.relative_to(root.resolve())
        except ValueError:
            failures.append(f"{rel} resolves outside the repository root (lock source: {label})")
            continue
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        if actual != expected:
            failures.append(
                f"{rel} sha256 {actual} != lock {expected} (lock source: {label}, pin {commit[:7]})"
            )
    return failures


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--repo-root", type=Path, default=None,
        help="repository root (default: the parent of this script's directory)",
    )
    parser.add_argument(
        "--lock-source", default="worktree",
        help="worktree (default), index, or rev:<sha>",
    )
    parser.add_argument(
        "--lock-path", type=Path, default=None,
        help="read the lock from this file instead of <root>/.tooltempest.lock (worktree mode only)",
    )
    args = parser.parse_args(argv)
    if args.lock_source not in ("worktree", "index") and not args.lock_source.startswith("rev:"):
        parser.error("--lock-source must be worktree, index, or rev:<sha>")
    return args


def run(args):
    root = (args.repo_root or Path(__file__).resolve().parent.parent)
    if not Path(root).is_dir():
        raise LockError(f"repository root {root} is not a directory")
    root = Path(root).resolve()
    text, label = read_lock_text(root, args.lock_source, args.lock_path)
    lock = parse_lock(text)
    failures = verify_entries(root, lock_entries(lock), label, lock["commit"])
    if failures:
        for message in failures:
            print(f"FAIL: {message}", file=sys.stderr)
        print(
            f"See {ADR} (\"Materialization procedure\"). Do not edit the lock to match the file.",
            file=sys.stderr,
        )
        return EXIT_VIOLATION
    paths = ", ".join(rel for rel, _ in lock_entries(lock))
    print(f"OK: {paths} sha256 matches {LOCK_NAME} (lock source: {label}, pin {lock['commit'][:7]})")
    return EXIT_OK


def main(argv=None):
    try:
        args = parse_args(sys.argv[1:] if argv is None else argv)
        return run(args)
    except NotApplicable as exc:
        print(f"N/A: {exc}")
        return EXIT_NA
    except Violation as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return EXIT_VIOLATION
    except LockError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_ERROR
    except Exception as exc:  # fail closed: a crash must never read as a pass or as a mismatch
        print(f"ERROR: unexpected failure: {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
