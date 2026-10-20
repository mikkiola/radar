"""Tests for scripts/check_tooltempest_lock.py (the .tooltempest.lock integrity guard).

All fixtures live in tmp_path; nothing here touches the real lock, the real
vendored file, the network, or the real Git configuration.
"""
import ast
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
CHECKER = REPO / "scripts" / "check_tooltempest_lock.py"
LOCK_NAME = ".tooltempest.lock"
VENDORED = b"# fixture vendored file\nprint('vendored')\n"
VENDORED_SHA = hashlib.sha256(VENDORED).hexdigest()
COMMIT = "a" * 40


def _load_module():
    spec = importlib.util.spec_from_file_location("check_tooltempest_lock", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _env(tmp_path):
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(tmp_path),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "PYTHONDONTWRITEBYTECODE": "1",
        "LC_ALL": "C",
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }


def lock_text(**overrides):
    data = {
        "repository": "file:///nonexistent",
        "commit": COMMIT,
        "path": "scripts/doc_sync.py",
        "sha256": VENDORED_SHA,
    }
    data.update(overrides)
    return json.dumps({k: v for k, v in data.items() if v is not None}, indent=2) + "\n"


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "proj"
    (root / "scripts").mkdir(parents=True)
    (root / "scripts" / "doc_sync.py").write_bytes(VENDORED)
    (root / LOCK_NAME).write_text(lock_text())
    return root


def run_checker(root, *args, cwd=None, tmp_path=None):
    env = _env(tmp_path or root)
    return subprocess.run(
        [sys.executable, "-B", str(CHECKER), "--repo-root", str(root), *args],
        cwd=str(cwd or root), env=env, capture_output=True, text=True,
    )


def git(root, *args, tmp_path):
    return subprocess.run(
        ["git", *args], cwd=str(root), env=_env(tmp_path),
        capture_output=True, text=True, check=True,
    )


def git_project(project, tmp_path):
    git(project, "init", "-q", tmp_path=tmp_path)
    git(project, "add", LOCK_NAME, tmp_path=tmp_path)
    git(project, "commit", "-q", "-m", "init", tmp_path=tmp_path)
    return project


# --- 1. synchronized file passes -------------------------------------------

def test_synchronized_file_passes(project, tmp_path):
    r = run_checker(project, tmp_path=tmp_path)
    assert r.returncode == 0, r.stderr
    assert "OK" in r.stdout and "scripts/doc_sync.py" in r.stdout


# --- 2. modified file fails with expected-vs-actual ------------------------

def test_modified_file_fails_with_expected_and_actual(project, tmp_path):
    (project / "scripts" / "doc_sync.py").write_bytes(VENDORED + b"# drift\n")
    actual = hashlib.sha256(VENDORED + b"# drift\n").hexdigest()
    r = run_checker(project, tmp_path=tmp_path)
    assert r.returncode == 1
    assert VENDORED_SHA in r.stderr and actual in r.stderr
    assert "docs/adr/0025" in r.stderr


# --- 3. missing file fails -------------------------------------------------

def test_missing_file_fails(project, tmp_path):
    (project / "scripts" / "doc_sync.py").unlink()
    r = run_checker(project, tmp_path=tmp_path)
    assert r.returncode == 1
    assert "not materialized" in r.stderr


def test_directory_in_place_of_file_fails(project, tmp_path):
    (project / "scripts" / "doc_sync.py").unlink()
    (project / "scripts" / "doc_sync.py").mkdir()
    r = run_checker(project, tmp_path=tmp_path)
    assert r.returncode == 1


def test_symlinked_parent_directory_pointing_outside_the_root_fails(project, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "doc_sync.py").write_bytes(VENDORED)  # matching bytes, but outside the repository
    (project / "scripts" / "doc_sync.py").unlink()
    (project / "scripts").rmdir()
    (project / "scripts").symlink_to(outside)
    r = run_checker(project, tmp_path=tmp_path)
    assert r.returncode == 1
    assert "outside the repository root" in r.stderr


def test_symlinked_file_fails(project, tmp_path):
    target = tmp_path / "outside.py"
    target.write_bytes(VENDORED)
    (project / "scripts" / "doc_sync.py").unlink()
    (project / "scripts" / "doc_sync.py").symlink_to(target)
    r = run_checker(project, tmp_path=tmp_path)
    assert r.returncode == 1
    assert "symlink" in r.stderr


# --- 4. malformed lock fails closed ----------------------------------------

@pytest.mark.parametrize("text, needle", [
    ("{not json", "not valid JSON"),
    ("[1, 2]", "JSON object"),
    (lock_text(sha256=None), "sha256"),
    (lock_text(sha256="abc"), "sha256"),
    (lock_text(sha256="A" * 64), "sha256"),
    (lock_text(path=None), "path"),
    (lock_text(path=""), "path"),
    (lock_text(path="../escape.py"), "path"),
    (lock_text(path="/abs/doc_sync.py"), "path"),
    (lock_text(path="scripts\\doc_sync.py"), "path"),
    (lock_text(commit="abc"), "commit"),
    (lock_text(repository=""), "repository"),
    (lock_text(repository=7), "repository"),
    (lock_text(extra="x"), "unsupported"),
    (lock_text(files=["a", "b"]), "unsupported"),
])
def test_malformed_lock_exits_2_with_clear_message(project, tmp_path, text, needle):
    (project / LOCK_NAME).write_text(text)
    r = run_checker(project, tmp_path=tmp_path)
    assert r.returncode == 2, (r.stdout, r.stderr)
    assert needle in r.stderr
    assert "OK" not in r.stdout


def test_missing_lock_exits_2(project, tmp_path):
    (project / LOCK_NAME).unlink()
    r = run_checker(project, tmp_path=tmp_path)
    assert r.returncode == 2
    assert LOCK_NAME in r.stderr


def test_unreadable_lock_path_exits_2(project, tmp_path):
    r = run_checker(project, "--lock-path", str(project / "scripts"), tmp_path=tmp_path)
    assert r.returncode == 2


def test_missing_repo_root_exits_2(tmp_path):
    r = run_checker(tmp_path / "does-not-exist", cwd=tmp_path, tmp_path=tmp_path)
    assert r.returncode == 2


# --- 5. every lock-covered entry is checked --------------------------------

def test_all_entries_are_checked(tmp_path):
    module = _load_module()
    root = tmp_path / "proj"
    (root / "a").mkdir(parents=True)
    (root / "a" / "one.py").write_bytes(b"one")
    (root / "a" / "two.py").write_bytes(b"two-DRIFTED")
    entries = [
        ("a/one.py", hashlib.sha256(b"one").hexdigest()),
        ("a/two.py", hashlib.sha256(b"two").hexdigest()),
    ]
    failures = module.verify_entries(root, entries, "worktree", COMMIT)
    assert len(failures) == 1
    assert "a/two.py" in failures[0]

    (root / "a" / "two.py").write_bytes(b"two")
    assert module.verify_entries(root, entries, "worktree", COMMIT) == []


def test_lock_entries_covers_the_declared_path(project):
    module = _load_module()
    lock = module.parse_lock(lock_text())
    assert module.lock_entries(lock) == [("scripts/doc_sync.py", VENDORED_SHA)]


# --- 6. unrelated project-local files cause no false positives -------------

def test_unrelated_local_files_do_not_trigger(project, tmp_path):
    (project / "scripts" / "verify.py").write_bytes(b"project local, arbitrary bytes")
    (project / "scripts" / "generate_adr_index.py").write_bytes(b"also local")
    r = run_checker(project, tmp_path=tmp_path)
    assert r.returncode == 0, r.stderr


# --- 7. works from another current directory -------------------------------

def test_runs_from_a_different_cwd(project, tmp_path):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    r = run_checker(project, cwd=elsewhere, tmp_path=tmp_path)
    assert r.returncode == 0, r.stderr


def test_default_repo_root_is_the_scripts_parent(project, tmp_path):
    copied = project / "scripts" / "check_tooltempest_lock.py"
    copied.write_bytes(CHECKER.read_bytes())
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    r = subprocess.run(
        [sys.executable, "-B", str(copied)], cwd=str(elsewhere),
        env=_env(tmp_path), capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr


# --- 8/10. exit codes and unexpected errors --------------------------------

def test_unexpected_exception_returns_2(project, monkeypatch, capsys):
    module = _load_module()

    def boom(*a, **k):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(module.hashlib, "sha256", boom)
    rc = module.main(["--repo-root", str(project)])
    assert rc == 2
    assert "unexpected" in capsys.readouterr().err.lower()


def test_invalid_lock_source_is_a_usage_error(project, tmp_path):
    r = run_checker(project, "--lock-source", "bogus", tmp_path=tmp_path)
    assert r.returncode == 2


# --- index / rev modes ------------------------------------------------------

def test_index_mode_checks_the_staged_lock_not_the_working_copy(project, tmp_path):
    git_project(project, tmp_path)
    (project / LOCK_NAME).write_text(lock_text(sha256="0" * 64))
    git(project, "add", LOCK_NAME, tmp_path=tmp_path)
    (project / LOCK_NAME).write_text(lock_text())  # working copy is good, index is bad
    r = run_checker(project, "--lock-source", "index", tmp_path=tmp_path)
    assert r.returncode == 1
    assert "0" * 64 in r.stderr
    assert run_checker(project, tmp_path=tmp_path).returncode == 0  # worktree mode is fooled


def test_rev_mode_checks_the_commit_lock(project, tmp_path):
    git_project(project, tmp_path)
    good = git(project, "rev-parse", "HEAD", tmp_path=tmp_path).stdout.strip()
    (project / LOCK_NAME).write_text(lock_text(sha256="1" * 64))
    git(project, "commit", "-qam", "bad lock", tmp_path=tmp_path)
    bad = git(project, "rev-parse", "HEAD", tmp_path=tmp_path).stdout.strip()
    assert run_checker(project, "--lock-source", f"rev:{good}", tmp_path=tmp_path).returncode == 0
    r = run_checker(project, "--lock-source", f"rev:{bad}", tmp_path=tmp_path)
    assert r.returncode == 1 and "1" * 64 in r.stderr


def test_rev_mode_sees_a_lock_that_only_a_merged_side_branch_ever_carried(tmp_path):
    # Git's default history simplification follows one parent of a merge whose tree
    # equals it, so without --full-history the side branch is never visited and the
    # removed lock would read as "never existed" (exit 3) instead of a violation.
    root = tmp_path / "merge"
    root.mkdir()
    git(root, "init", "-q", "-b", "main", tmp_path=tmp_path)
    (root / "f").write_text("a\n")
    git(root, "add", "f", tmp_path=tmp_path)
    git(root, "commit", "-qm", "base", tmp_path=tmp_path)
    git(root, "checkout", "-q", "-b", "side", tmp_path=tmp_path)
    (root / LOCK_NAME).write_text(lock_text())
    git(root, "add", LOCK_NAME, tmp_path=tmp_path)
    git(root, "commit", "-qm", "add the lock", tmp_path=tmp_path)
    git(root, "rm", "-q", LOCK_NAME, tmp_path=tmp_path)
    git(root, "commit", "-qm", "drop the lock", tmp_path=tmp_path)
    git(root, "checkout", "-q", "main", tmp_path=tmp_path)
    (root / "f").write_text("b\n")
    git(root, "commit", "-qam", "main moves on", tmp_path=tmp_path)
    git(root, "merge", "-q", "--no-ff", "side", "-m", "merge", tmp_path=tmp_path)
    tip = git(root, "rev-parse", "HEAD", tmp_path=tmp_path).stdout.strip()
    assert git(root, "ls-tree", tip, "--", LOCK_NAME, tmp_path=tmp_path).stdout.strip() == ""
    r = run_checker(root, "--lock-source", f"rev:{tip}", tmp_path=tmp_path)
    assert r.returncode == 1 and "was removed" in r.stderr, r.stdout + r.stderr


def test_rev_mode_with_unknown_revision_exits_2(project, tmp_path):
    git_project(project, tmp_path)
    r = run_checker(project, "--lock-source", "rev:" + "f" * 40, tmp_path=tmp_path)
    assert r.returncode == 2


# --- 12. stdlib only, no network ------------------------------------------

def test_checker_imports_only_the_standard_library():
    allowed = {"argparse", "hashlib", "json", "re", "subprocess", "sys", "pathlib"}
    tree = ast.parse(CHECKER.read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert imported <= allowed, imported - allowed


def test_real_lock_file_is_well_formed():
    # Parses the real lock only; the vendored file is untracked, so its bytes
    # are deliberately not asserted here (it is absent on a fresh checkout/CI).
    module = _load_module()
    lock = module.parse_lock((REPO / LOCK_NAME).read_text())
    assert module.lock_entries(lock)
