"""Tests for scripts/install-hooks.sh (activation of the .tooltempest.lock guard, ADR-0025).

The real installer is run with real bash against disposable repositories under
tmp_path. This repository's .git/hooks is never read or written, and nothing
here uses the network. The failure of a mid-install rename is simulated with a
PATH shim for `mv`; the process-kill window between the two renames is not
simulated (documented limitation), only the printed manual restore commands.
"""
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
LOCK = ".tooltempest.lock"
REL = "scripts/doc_sync.py"
VENDORED = b"# fixture vendored file\nprint('vendored')\n"
VENDORED_SHA = hashlib.sha256(VENDORED).hexdigest()
SUFFIX = ".pre-lockguard-backup"
HOOKS = ("pre-commit", "pre-push")
BASHES = sorted({os.path.realpath(p) for p in (shutil.which("bash"), shutil.which("/bin/bash")) if p})


def text(result):
    return result.stdout + result.stderr


def ok(result):
    assert result.returncode == 0, text(result)
    return result


def blocked(result):
    assert result.returncode != 0, text(result)
    return result


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def env_for(base, extra=None):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(base / "home"),
        "TMPDIR": str(base / "tmp"),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "PYTHONDONTWRITEBYTECODE": "1",
        "LC_ALL": "C",
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@t",
    }
    env.update(extra or {})
    return env


class Project:
    def __init__(self, base, materialized=True):
        self.base = Path(base)
        (self.base / "home").mkdir()
        (self.base / "tmp").mkdir()
        self.root = self.base / "proj"
        self.root.mkdir()
        self.git("init", "-q", "-b", "main")
        (self.root / "scripts" / "hooks").mkdir(parents=True)
        shutil.copy2(REPO / "scripts" / "check_tooltempest_lock.py", self.root / "scripts")
        shutil.copy2(REPO / "scripts" / "install-hooks.sh", self.root / "scripts")
        for hook in HOOKS:
            shutil.copy2(REPO / "scripts" / "hooks" / hook, self.root / "scripts" / "hooks" / hook)
        (self.root / LOCK).write_text(json.dumps({
            "repository": "file:///nonexistent",
            "commit": "a" * 40,
            "path": REL,
            "sha256": VENDORED_SHA,
        }, indent=2) + "\n")
        if materialized:
            (self.root / REL).write_bytes(VENDORED)
        self.hooks = self.root / ".git" / "hooks"

    def run(self, argv, extra=None):
        return subprocess.run(
            argv, cwd=str(self.root), env=env_for(self.base, extra),
            stdin=subprocess.DEVNULL, capture_output=True, text=True,
        )

    def git(self, *args):
        result = self.run(["git", *args])
        assert result.returncode == 0, text(result)
        return result

    def install(self, bash="bash", extra=None):
        return self.run([bash, "scripts/install-hooks.sh"], extra)

    def source(self, hook):
        return self.root / "scripts" / "hooks" / hook

    def write_hook(self, name, body):
        path = self.hooks / name
        path.write_text(body)
        path.chmod(0o755)
        return path

    def snapshot(self):
        """Every entry in the hooks directory (including temporaries and backups) with its content hash."""
        state = {}
        for path in sorted(self.hooks.iterdir()):
            if path.is_symlink():
                state[path.name] = ("symlink", os.readlink(path))
            elif path.is_file():
                state[path.name] = ("file", sha(path), stat.S_IMODE(path.stat().st_mode))
            else:
                state[path.name] = ("other",)
        return state

    def temporaries(self):
        return [p.name for p in self.hooks.iterdir() if ".new." in p.name or ".restore." in p.name]


@pytest.fixture
def proj(tmp_path):
    return Project(tmp_path)


def old_body(hook):
    return f"#!/bin/sh\necho previous {hook}\n"


def seed_old_hooks(proj):
    for hook in HOOKS:
        proj.write_hook(hook, old_body(hook))


def install_shim(base, fail_on):
    shim = base / "shim"
    shim.mkdir()
    script = shim / "mv"
    script.write_text(
        "#!/bin/sh\n"
        'n=$(cat "$COUNTER" 2>/dev/null || echo 0)\n'
        "n=$((n + 1))\n"
        'echo "$n" > "$COUNTER"\n'
        'if [ "$n" = "$FAIL_ON" ]; then echo "shim: simulated mv failure" >&2; exit 1; fi\n'
        'exec /bin/mv "$@"\n'
    )
    script.chmod(0o755)
    return {
        "PATH": f"{shim}{os.pathsep}{os.environ.get('PATH', '/usr/bin:/bin')}",
        "COUNTER": str(base / "mv-count"),
        "FAIL_ON": str(fail_on),
    }


def test_i1_an_existing_different_backup_is_never_overwritten(proj):
    seed_old_hooks(proj)
    proj.write_hook("pre-commit" + SUFFIX, "#!/bin/sh\necho an older backup\n")
    before = proj.snapshot()
    result = blocked(proj.install())
    assert "already exists and differs" in text(result)
    assert proj.snapshot() == before


def test_i1_a_backup_equal_to_the_current_hook_is_reused(proj):
    seed_old_hooks(proj)
    proj.write_hook("pre-commit" + SUFFIX, old_body("pre-commit"))
    ok(proj.install())
    assert sha(proj.hooks / "pre-commit") == sha(proj.source("pre-commit"))
    assert (proj.hooks / ("pre-commit" + SUFFIX)).read_text() == old_body("pre-commit")


@pytest.mark.parametrize("bash", BASHES)
def test_i2_rerunning_changes_nothing(proj, bash):
    assert "installed and active" in text(ok(proj.install(bash)))
    first = {h: ((proj.hooks / h).read_bytes(), (proj.hooks / h).stat().st_mtime_ns) for h in HOOKS}
    result = ok(proj.install(bash))
    assert "already installed" in text(result)
    second = {h: ((proj.hooks / h).read_bytes(), (proj.hooks / h).stat().st_mtime_ns) for h in HOOKS}
    assert first == second
    assert proj.temporaries() == []


def test_i3_a_differing_hook_is_backed_up_before_it_is_replaced(proj):
    seed_old_hooks(proj)
    ok(proj.install())
    for hook in HOOKS:
        assert (proj.hooks / (hook + SUFFIX)).read_text() == old_body(hook)
        assert sha(proj.hooks / hook) == sha(proj.source(hook))
        assert os.access(proj.hooks / hook, os.X_OK)
    assert proj.temporaries() == []


@pytest.mark.skipif(os.geteuid() == 0, reason="a read-only directory does not stop root")
def test_i4_an_unwritable_hooks_directory_is_refused_before_any_change(proj):
    seed_old_hooks(proj)
    before = proj.snapshot()
    proj.hooks.chmod(0o555)
    try:
        result = blocked(proj.install())
    finally:
        proj.hooks.chmod(0o755)
    assert "not writable" in text(result)
    assert proj.snapshot() == before


def test_i5_failure_of_the_second_rename_rolls_back_to_the_previous_hooks(proj):
    seed_old_hooks(proj)
    extra = install_shim(proj.base, fail_on=2)
    result = blocked(proj.install(extra=extra))
    assert "simulated mv failure" in text(result)
    assert "ROLLBACK" in text(result)
    for hook in HOOKS:
        assert (proj.hooks / hook).read_text() == old_body(hook)
        assert (proj.hooks / (hook + SUFFIX)).read_text() == old_body(hook)
    assert proj.temporaries() == []


def test_i5_rollback_removes_a_hook_that_did_not_exist_before(proj):
    extra = install_shim(proj.base, fail_on=2)
    blocked(proj.install(extra=extra))
    assert not (proj.hooks / "pre-commit").exists()
    assert not (proj.hooks / "pre-push").exists()
    assert proj.temporaries() == []


def test_i6_unmanaged_hooks_are_untouched_and_local_edits_survive_in_the_backup(proj):
    foreign = proj.write_hook("post-commit", "#!/bin/sh\necho foreign\n")
    foreign_before = (foreign.read_bytes(), foreign.stat().st_mtime_ns)
    proj.write_hook("pre-commit", old_body("pre-commit") + "# my local edit\n")
    ok(proj.install())
    assert (foreign.read_bytes(), foreign.stat().st_mtime_ns) == foreign_before
    assert "# my local edit" in (proj.hooks / ("pre-commit" + SUFFIX)).read_text()


def test_i7_the_printed_restore_commands_bring_the_previous_hooks_back(proj):
    seed_old_hooks(proj)
    result = ok(proj.install())
    commands = re.findall(r"^\s+(cp -p '[^']+' '[^']+')$", result.stdout, re.M)
    assert len(commands) == 2, result.stdout
    by_hook = {("pre-commit" if cmd.rstrip("'").endswith("/pre-commit") else "pre-push"): cmd for cmd in commands}
    assert sorted(by_hook) == ["pre-commit", "pre-push"]
    # a mixed state (one hook restored, one still the new one) is recoverable step by step
    subprocess.run(by_hook["pre-push"], shell=True, check=True, cwd=str(proj.root))
    assert (proj.hooks / "pre-push").read_text() == old_body("pre-push")
    assert sha(proj.hooks / "pre-commit") == sha(proj.source("pre-commit"))
    subprocess.run(by_hook["pre-commit"], shell=True, check=True, cwd=str(proj.root))
    assert (proj.hooks / "pre-commit").read_text() == old_body("pre-commit")


def test_i8_a_clone_without_the_file_is_refused_and_nothing_is_created(tmp_path):
    proj = Project(tmp_path, materialized=False)
    before = proj.snapshot()
    result = blocked(proj.install())
    assert "materialized" in text(result)
    assert "No hooks were changed" in text(result)
    assert proj.snapshot() == before
    assert not (proj.hooks / "pre-commit").exists() and not (proj.hooks / "pre-push").exists()


def test_a_file_that_does_not_match_the_lock_is_refused(proj):
    (proj.root / REL).write_bytes(VENDORED + b"# drift\n")
    before = proj.snapshot()
    result = blocked(proj.install())
    assert VENDORED_SHA in text(result)
    assert proj.snapshot() == before


def test_a_malformed_lock_is_refused(proj):
    (proj.root / LOCK).write_text("{not json")
    before = proj.snapshot()
    blocked(proj.install())
    assert proj.snapshot() == before


def test_a_symlinked_hook_is_not_touched(proj):
    target = proj.base / "elsewhere-hook"
    target.write_text("#!/bin/sh\necho elsewhere\n")
    (proj.hooks / "pre-commit").symlink_to(target)
    before = proj.snapshot()
    result = blocked(proj.install())
    assert "symlink" in text(result)
    assert proj.snapshot() == before
    assert target.read_text() == "#!/bin/sh\necho elsewhere\n"
