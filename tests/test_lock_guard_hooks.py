"""Real Git hook-dispatch tests for the .tooltempest.lock integrity guard (ADR-0025).

Every test builds disposable repositories under tmp_path: a fixture "upstream"
(the source of the vendored file), a bare "remote", and a project that carries
the real checker, hook sources and installer copied from this repository. The
hooks are installed with the real installer and exercised through Git itself
(git commit, git push, git hook run), never by calling the hook file directly.

Nothing here touches this repository's .git/hooks, the real lock, the real
vendored file, or the network: the lock's `repository` is file:///nonexistent
and the only remote is a local bare repository. Commits that must carry a state
the hooks would refuse (to prove the push-side check) are built with
core.hooksPath pointed at /dev/null, never with --no-verify.

The "materialize" and "verify-upstream" blocks are extracted from the ADR, so
what is tested is exactly what is documented.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
ADR = REPO / "docs" / "adr" / "0025-tooltempest-lock-integrity-guard.md"
LOCK = ".tooltempest.lock"
REL = "scripts/doc_sync.py"
VENDORED = b"# fixture vendored file\nprint('vendored')\n"
VENDORED_SHA = hashlib.sha256(VENDORED).hexdigest()
OTHER = b"# another version of the vendored file\n"
OTHER_SHA = hashlib.sha256(OTHER).hexdigest()
EMPTY_INPUT_SHA = hashlib.sha256(b"").hexdigest()
BAD_SHA = "0" * 64


def text(result):
    return result.stdout + result.stderr


def ok(result):
    assert result.returncode == 0, text(result)
    return result


def blocked(result):
    assert result.returncode != 0, text(result)
    return result


def adr_block(name):
    match = re.search(r"```sh " + re.escape(name) + r"\n(.*?)\n```", ADR.read_text(encoding="utf-8"), re.S)
    assert match, f"ADR-0025 has no '```sh {name}' block"
    return match.group(1)


class Lab:
    def __init__(self, base):
        self.base = Path(base)
        self.home = self.base / "home"
        self.tmp = self.base / "tmp"
        self.home.mkdir()
        self.tmp.mkdir()
        self.env = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.home),
            "TMPDIR": str(self.tmp),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
            "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
        }
        self.tt = self.base / "tt"
        self.remote = self.base / "remote.git"
        self.proj = self.base / "proj"
        self.clones = 0
        self._build()

    # -- process helpers -----------------------------------------------------
    def run(self, argv, cwd, extra=None, data=None):
        env = dict(self.env)
        env.update(extra or {})
        kwargs = {"input": data} if data is not None else {"stdin": subprocess.DEVNULL}
        return subprocess.run(
            argv, cwd=str(cwd), env=env, capture_output=True, text=True, **kwargs,
        )

    def git(self, cwd, *args, extra=None, check=True, data=None):
        result = self.run(["git", *args], cwd, extra, data)
        if check:
            assert result.returncode == 0, f"git {' '.join(args)} failed:\n{text(result)}"
        return result

    # -- fixture construction ------------------------------------------------
    def lock_text(self, **overrides):
        data = {
            "repository": "file:///nonexistent",
            "commit": self.commit,
            "path": REL,
            "sha256": VENDORED_SHA,
        }
        data.update(overrides)
        return json.dumps(data, indent=2) + "\n"

    def _build(self):
        self.tt.mkdir()
        self.git(self.tt, "init", "-q", "-b", "main")
        (self.tt / "scripts").mkdir()
        (self.tt / REL).write_bytes(VENDORED)
        self.git(self.tt, "add", REL)
        self.git(self.tt, "commit", "-q", "-m", "upstream")
        self.commit = self.git(self.tt, "rev-parse", "HEAD").stdout.strip()

        self.git(self.base, "init", "-q", "--bare", "-b", "main", str(self.remote))

        self.proj.mkdir()
        self.git(self.proj, "init", "-q", "-b", "main")
        (self.proj / "scripts" / "hooks").mkdir(parents=True)
        shutil.copy2(REPO / "scripts" / "check_tooltempest_lock.py", self.proj / "scripts")
        shutil.copy2(REPO / "scripts" / "install-hooks.sh", self.proj / "scripts")
        for hook in ("pre-commit", "pre-push"):
            shutil.copy2(REPO / "scripts" / "hooks" / hook, self.proj / "scripts" / "hooks" / hook)
        (self.proj / LOCK).write_text(self.lock_text())
        (self.proj / "README.md").write_text("readme\n")
        info = self.proj / ".git" / "info"
        info.mkdir(exist_ok=True)
        with open(info / "exclude", "a", encoding="utf-8") as handle:
            handle.write(f"/{REL}\n")  # the vendored file stays untracked, as in Radar
        self.git(self.proj, "add", "-A")
        self.git(self.proj, "commit", "-q", "-m", "init")
        self.git(self.proj, "remote", "add", "origin", str(self.remote))
        self.git(self.proj, "push", "-q", "origin", "main")

    def clone(self):
        self.clones += 1
        target = self.base / f"clone{self.clones}"
        self.git(self.base, "clone", "-q", str(self.remote), str(target))
        return target

    # -- operations ----------------------------------------------------------
    def materialize(self, cwd, data=VENDORED):
        path = Path(cwd) / REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def install(self, cwd):
        return self.run(["bash", "scripts/install-hooks.sh"], cwd)

    def hook_files(self, cwd):
        hooks = Path(cwd) / ".git" / "hooks"
        return sorted(p.name for p in hooks.iterdir() if not p.name.endswith(".sample"))

    def commit_cmd(self, cwd, message, *args, hooks=True):
        prefix = [] if hooks else ["-c", f"core.hooksPath={os.devnull}"]
        return self.run(["git", *prefix, "commit", "-q", "-m", message, *args], cwd)

    def push(self, cwd, *refs, dry_run=False):
        flags = ["--dry-run"] if dry_run else []
        return self.run(["git", "push", *flags, "origin", *refs], cwd)

    def head(self, cwd):
        return self.git(cwd, "rev-parse", "HEAD").stdout.strip()

    def remote_heads(self):
        return self.git(self.proj, "ls-remote", "--heads", "origin").stdout

    def stage_readme(self, cwd, content):
        (Path(cwd) / "README.md").write_text(content)
        self.git(cwd, "add", "README.md")

    def make_orphan(self, cwd, branch, files):
        """Create `branch` through plumbing with an unrelated root commit; it never contains the lock."""
        index = {"GIT_INDEX_FILE": str(self.base / f"idx-{branch}")}
        for name, content in files.items():
            blob = self.git(cwd, "hash-object", "-w", "--stdin", data=content).stdout.strip()
            self.git(cwd, "update-index", "--add", "--cacheinfo", f"100644,{blob},{name}", extra=index)
        tree = self.git(cwd, "write-tree", extra=index).stdout.strip()
        sha = self.git(cwd, "commit-tree", tree, "-m", f"{branch} root").stdout.strip()
        self.git(cwd, "branch", "-f", branch, sha)
        return sha

    def block(self, name, cwd, **extra):
        env = {"TT": str(self.tt)}
        env.update(extra)
        return self.run(["sh", "-c", adr_block(name)], cwd, env)


@pytest.fixture
def lab(tmp_path):
    return Lab(tmp_path)


@pytest.fixture
def active(lab):
    """The project with the vendored file materialized and the guard hooks installed."""
    lab.materialize(lab.proj)
    ok(lab.install(lab.proj))
    return lab


# --- 7.1 fresh clone and ordinary working scenarios ----------------------------

def test_f1_fresh_clone_without_the_guard_commits_and_pushes_as_before(lab):
    c = lab.clone()
    assert lab.hook_files(c) == []
    assert not (c / REL).exists()
    lab.stage_readme(c, "changed\n")
    ok(lab.commit_cmd(c, "doc"))
    ok(lab.push(c, "main"))
    # the documented limit: an unprotected clone accepts a lock that matches no file
    (c / LOCK).write_text(lab.lock_text(sha256=BAD_SHA))
    lab.git(c, "add", LOCK)
    ok(lab.commit_cmd(c, "unprotected"))


def test_f2_installer_refuses_in_a_clone_without_the_file_and_changes_nothing(lab):
    c = lab.clone()
    result = blocked(lab.install(c))
    assert "materialized" in text(result)
    assert lab.hook_files(c) == []
    lab.stage_readme(c, "still works\n")
    ok(lab.commit_cmd(c, "doc"))
    ok(lab.push(c, "main"))


def test_f3_materialize_block_then_install_then_git_runs_the_hook(lab):
    c = lab.clone()
    ok(lab.block("materialize", c))
    assert (c / REL).read_bytes() == VENDORED
    ok(lab.install(c))
    assert lab.hook_files(c) == ["pre-commit", "pre-push"]
    result = ok(lab.git(c, "hook", "run", "pre-commit", check=False))
    assert "nothing to verify" in text(result)


def test_f4_missing_file_blocks_the_push_until_it_is_rematerialized(active):
    lab, p = active, active.proj
    lab.stage_readme(p, "a\n")
    ok(lab.commit_cmd(p, "a"))
    (p / REL).unlink()
    result = blocked(lab.push(p, "main"))
    assert "is not materialized" in text(result)
    assert "docs/adr/0025" in text(result)
    assert "push blocked" in text(result)
    ok(lab.block("materialize", p))
    ok(lab.push(p, "main"))


@pytest.mark.parametrize("file_present", [True, False])
def test_f5_t_del2_branch_that_never_had_the_lock_is_not_applicable(active, file_present):
    lab, p = active, active.proj
    if not file_present:
        (p / REL).unlink()
    lab.make_orphan(p, "vault", {"01_Data/a.md": "data\n"})
    result = ok(lab.push(p, "vault"))
    assert "N/A" in text(result)
    assert "refs/heads/vault" in lab.remote_heads()


def test_f6_linked_worktree_shares_the_hooks_and_checks_its_own_file(active):
    lab, p = active, active.proj
    wt = lab.base / "wt"
    lab.git(p, "worktree", "add", "-q", "-b", "wtb", str(wt))
    assert not (wt / REL).exists()  # an untracked file does not follow into a new worktree
    lab.stage_readme(wt, "worktree\n")
    ok(lab.commit_cmd(wt, "no lock in this commit"))
    (wt / LOCK).write_text(lab.lock_text(repository="file:///other"))
    lab.git(wt, "add", LOCK)
    result = blocked(lab.commit_cmd(wt, "lock without the file"))
    assert "is not materialized" in text(result)
    lab.materialize(wt)
    ok(lab.commit_cmd(wt, "lock with the file"))


def test_f6_data_only_worktree_uses_the_checker_of_the_main_worktree(active):
    lab, p = active, active.proj
    lab.make_orphan(p, "vault", {"d.md": "1\n"})
    vwt = lab.base / "vwt"
    lab.git(p, "worktree", "add", "-q", str(vwt), "vault")
    assert not (vwt / "scripts").exists()
    (vwt / "d.md").write_text("2\n")
    lab.git(vwt, "add", "d.md")
    ok(lab.commit_cmd(vwt, "data"))
    result = ok(lab.push(vwt, "vault"))
    assert "N/A" in text(result)


def test_f7_commit_that_does_not_touch_the_lock_passes_with_an_explicit_message(active):
    lab, p = active, active.proj
    lab.stage_readme(p, "doc\n")
    result = ok(lab.commit_cmd(p, "doc"))
    assert "nothing to verify" in text(result)


# --- 7.2 index, working tree and pushed commit ---------------------------------

def test_x1_bad_lock_in_the_index_good_one_in_the_working_tree_blocks_the_commit(active):
    lab, p = active, active.proj
    head = lab.head(p)
    (p / LOCK).write_text(lab.lock_text(sha256=BAD_SHA))
    lab.git(p, "add", LOCK)
    (p / LOCK).write_text(lab.lock_text())
    result = blocked(lab.commit_cmd(p, "x1"))
    assert BAD_SHA in text(result) and "lock source: index" in text(result)
    assert "commit blocked" in text(result)
    assert lab.head(p) == head


def test_x2_good_lock_in_the_index_bad_one_in_the_working_tree_commits_with_a_warning(active):
    lab, p = active, active.proj
    (p / LOCK).write_text(lab.lock_text(repository="file:///other"))
    lab.git(p, "add", LOCK)
    (p / LOCK).write_text(lab.lock_text(repository="file:///other", sha256=BAD_SHA))
    result = ok(lab.commit_cmd(p, "x2"))
    assert "WARNING" in text(result)
    assert json.loads(lab.git(p, "show", f"HEAD:{LOCK}").stdout)["sha256"] == VENDORED_SHA


def test_x3_commit_a_checks_the_lock_it_is_about_to_stage(active):
    lab, p = active, active.proj
    head = lab.head(p)
    (p / LOCK).write_text(lab.lock_text(sha256=BAD_SHA))
    result = blocked(lab.commit_cmd(p, "x3", "-a"))
    assert BAD_SHA in text(result)
    assert lab.head(p) == head


def test_x4_partial_commit_through_a_temporary_index_is_checked(active):
    lab, p = active, active.proj
    head = lab.head(p)
    (p / LOCK).write_text(lab.lock_text(sha256=BAD_SHA))
    blocked(lab.commit_cmd(p, "x4", "--", LOCK))
    assert lab.head(p) == head
    (p / LOCK).write_text(lab.lock_text(repository="file:///other"))
    ok(lab.commit_cmd(p, "x4 good", "--", LOCK))


def test_x5_staged_removal_of_the_lock_blocks_the_commit(active):
    lab, p = active, active.proj
    head = lab.head(p)
    lab.git(p, "rm", "-q", LOCK)
    result = blocked(lab.commit_cmd(p, "x5"))
    assert "not present in the index" in text(result)
    assert lab.head(p) == head


def test_x5_renaming_the_lock_away_blocks_the_commit(active):
    lab, p = active, active.proj
    head = lab.head(p)
    lab.git(p, "mv", LOCK, "other.json")  # rename detection would list only the new path
    result = blocked(lab.commit_cmd(p, "rename the lock away"))
    assert "not present in the index" in text(result)
    assert lab.head(p) == head


def test_staged_malformed_lock_blocks_the_commit_with_an_error(active):
    lab, p = active, active.proj
    (p / LOCK).write_text(lab.lock_text(extra="x"))
    lab.git(p, "add", LOCK)
    result = blocked(lab.commit_cmd(p, "malformed"))
    assert "unsupported lock field" in text(result)


def test_t_del1_removed_lock_is_a_violation_not_not_applicable(active):
    lab, p = active, active.proj
    lab.git(p, "checkout", "-q", "-b", "gone")
    lab.git(p, "rm", "-q", LOCK)
    ok(lab.commit_cmd(p, "drop the lock", hooks=False))
    lab.stage_readme(p, "later work\n")
    ok(lab.commit_cmd(p, "later work", hooks=False))
    # neither the tip nor its parent carries the lock: a parent-based signal would say N/A
    assert lab.git(p, "ls-tree", "HEAD", "--", LOCK).stdout.strip() == ""
    assert lab.git(p, "ls-tree", "HEAD~1", "--", LOCK).stdout.strip() == ""
    result = blocked(lab.push(p, "gone"))
    assert "was removed" in text(result)
    assert "N/A" not in text(result)
    assert "refs/heads/gone" not in lab.remote_heads()


def test_x6_bad_lock_committed_then_working_lock_fixed_still_blocks_the_push(active):
    lab, p = active, active.proj
    remote_before = lab.remote_heads()
    (p / LOCK).write_text(lab.lock_text(sha256=BAD_SHA))
    lab.git(p, "add", LOCK)
    ok(lab.commit_cmd(p, "bad lock", hooks=False))
    (p / LOCK).write_text(lab.lock_text())  # working copy repaired, commit still carries the bad lock
    result = blocked(lab.push(p, "main"))
    assert "lock source: rev:" in text(result) and BAD_SHA in text(result)
    assert lab.remote_heads() == remote_before


def test_x7_good_lock_committed_working_lock_corrupted_afterwards_still_pushes(active):
    lab, p = active, active.proj
    lab.stage_readme(p, "work\n")
    ok(lab.commit_cmd(p, "work"))
    # keep the keys the hook's advisory freshness step greps for; only the hash is wrong
    (p / LOCK).write_text(lab.lock_text(sha256=BAD_SHA))
    ok(lab.push(p, "main"))


def test_x8_one_bad_ref_blocks_the_whole_push(active):
    lab, p = active, active.proj
    remote_before = lab.remote_heads()
    lab.git(p, "checkout", "-q", "-b", "good")
    lab.stage_readme(p, "good\n")
    ok(lab.commit_cmd(p, "good"))
    lab.git(p, "checkout", "-q", "main")
    lab.git(p, "checkout", "-q", "-b", "bad")
    (p / LOCK).write_text(lab.lock_text(sha256=BAD_SHA))
    lab.git(p, "add", LOCK)
    ok(lab.commit_cmd(p, "bad", hooks=False))
    blocked(lab.push(p, "good", "bad"))
    assert lab.remote_heads() == remote_before


def test_x9_valid_lock_for_a_different_file_version_blocks_until_that_version_is_materialized(active):
    lab, p = active, active.proj
    (p / LOCK).write_text(lab.lock_text(sha256=OTHER_SHA))
    lab.git(p, "add", LOCK)
    ok(lab.commit_cmd(p, "repin without materializing", hooks=False))
    result = blocked(lab.push(p, "main"))
    assert OTHER_SHA in text(result) and VENDORED_SHA in text(result)
    lab.materialize(p, OTHER)
    ok(lab.push(p, "main"))


def test_x10_git_dispatches_the_installed_hooks(active):
    lab, p = active, active.proj
    lab.stage_readme(p, "ahead\n")
    ok(lab.commit_cmd(p, "ahead"))
    result = ok(lab.push(p, "main", dry_run=True))
    assert "[pre-push] All checks passed." in text(result)
    ok(lab.git(p, "hook", "run", "pre-commit", check=False))
    (p / REL).unlink()
    blocked(lab.push(p, "main", dry_run=True))  # the hook, not Git, decides


def test_checker_error_at_the_pushed_tip_blocks_the_push(active):
    lab, p = active, active.proj
    (p / LOCK).write_text(lab.lock_text(extra="x"))
    lab.git(p, "add", LOCK)
    ok(lab.commit_cmd(p, "malformed lock", hooks=False))
    result = blocked(lab.push(p, "main"))
    assert "unsupported lock field" in text(result)
    assert "push blocked" in text(result)


def test_missing_checker_blocks_instead_of_passing_silently(active):
    lab, p = active, active.proj
    lab.stage_readme(p, "work\n")
    ok(lab.commit_cmd(p, "work"))
    (p / "scripts" / "check_tooltempest_lock.py").unlink()
    result = blocked(lab.push(p, "main"))
    assert "not found" in text(result)
    (p / LOCK).write_text(lab.lock_text(repository="file:///other"))
    lab.git(p, "add", LOCK)
    result = blocked(lab.commit_cmd(p, "lock change"))
    assert "not found" in text(result)


def check_out_data_only_branch_in_the_main_worktree(lab, p):
    """Leave the main working copy itself (not a linked worktree) on a data-only branch.

    The checker is tracked on main, so it disappears from this working tree, and
    the main-worktree fallback of the hook then points at the same missing file.
    """
    lab.make_orphan(p, "vault", {"01_Data/a.md": "data\n"})
    lab.git(p, "checkout", "-q", "vault")
    assert not (p / "scripts" / "check_tooltempest_lock.py").exists()
    assert (p / ".git").is_dir()


def test_main_worktree_on_a_data_only_branch_pushes_it_as_not_applicable(active):
    lab, p = active, active.proj
    check_out_data_only_branch_in_the_main_worktree(lab, p)
    result = ok(lab.push(p, "vault"))
    assert "N/A" in text(result)  # the checker cannot run; the hook decides from history alone
    assert "scripts/check_tooltempest_lock.py not found" in text(result)
    assert "refs/heads/vault" in lab.remote_heads()


@pytest.mark.parametrize("refs", [("main",), ("gone",), ("vault", "main")])
def test_missing_checker_in_the_main_worktree_still_blocks_refs_that_had_the_lock(active, refs):
    lab, p = active, active.proj
    lab.stage_readme(p, "work\n")
    ok(lab.commit_cmd(p, "work"))
    lab.git(p, "checkout", "-q", "-b", "gone")
    lab.git(p, "rm", "-q", LOCK)
    ok(lab.commit_cmd(p, "drop the lock", hooks=False))
    lab.git(p, "checkout", "-q", "main")
    check_out_data_only_branch_in_the_main_worktree(lab, p)
    before = lab.remote_heads()
    result = blocked(lab.push(p, *refs))
    assert "not found" in text(result)
    assert "push blocked" in text(result)
    assert lab.remote_heads() == before


def test_missing_checker_and_a_failing_history_lookup_blocks_even_a_data_only_branch(active):
    lab, p = active, active.proj
    check_out_data_only_branch_in_the_main_worktree(lab, p)
    # an invalid log.date makes `git log` (and only it) fail, as a real lookup failure would
    broken_log = {"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "log.date", "GIT_CONFIG_VALUE_0": "bogus"}
    result = blocked(lab.run(["git", "push", "origin", "vault"], p, extra=broken_log))
    assert "cannot verify" in text(result)
    assert "push blocked" in text(result)
    assert "refs/heads/vault" not in lab.remote_heads()


def build_branch_whose_merged_side_branch_carried_and_dropped_the_lock(lab, p):
    """`hist` never has the lock at its tip or on its first-parent line, yet a merged side branch had it."""
    no_hooks = ["-c", f"core.hooksPath={os.devnull}"]
    lab.make_orphan(p, "hist", {"f": "a\n"})
    lab.git(p, "checkout", "-q", "hist")
    lab.git(p, "checkout", "-q", "-b", "side")
    (p / LOCK).write_text(lab.lock_text())
    lab.git(p, "add", LOCK)
    ok(lab.commit_cmd(p, "add the lock", hooks=False))
    lab.git(p, "rm", "-q", LOCK)
    ok(lab.commit_cmd(p, "drop the lock", hooks=False))
    lab.git(p, "checkout", "-q", "hist")
    (p / "f").write_text("b\n")
    lab.git(p, "add", "f")
    ok(lab.commit_cmd(p, "hist moves on", hooks=False))
    lab.git(p, "-c", f"core.hooksPath={os.devnull}", "merge", "-q", "--no-ff", "side", "-m", "merge")
    assert lab.git(p, "ls-tree", "hist", "--", LOCK).stdout.strip() == ""
    lab.git(p, "checkout", "-q", "main")


def test_lock_dropped_on_a_merged_side_branch_blocks_the_push_with_the_checker(active):
    lab, p = active, active.proj
    build_branch_whose_merged_side_branch_carried_and_dropped_the_lock(lab, p)
    result = blocked(lab.push(p, "hist"))
    assert "was removed" in text(result)
    assert "refs/heads/hist" not in lab.remote_heads()


def test_lock_dropped_on_a_merged_side_branch_blocks_the_push_without_the_checker(active):
    lab, p = active, active.proj
    build_branch_whose_merged_side_branch_carried_and_dropped_the_lock(lab, p)
    (p / "scripts" / "check_tooltempest_lock.py").unlink()
    result = blocked(lab.push(p, "hist"))
    assert "cannot verify" in text(result)
    assert "N/A" not in text(result)
    assert "refs/heads/hist" not in lab.remote_heads()


def test_deleting_a_ref_is_not_checked(active):
    lab, p = active, active.proj
    lab.git(p, "branch", "short-lived")
    ok(lab.push(p, "short-lived"))
    result = ok(lab.push(p, ":short-lived"))
    assert "ref deletion" in text(result)
    assert "refs/heads/short-lived" not in lab.remote_heads()


# --- 7.4 the documented recovery blocks (extracted from the ADR) ---------------

def leftovers(lab, cwd):
    found = [p.name for p in (Path(cwd) / "scripts").iterdir() if p.name.startswith(".materialize.")]
    found += [p.name for p in lab.tmp.iterdir()]
    return found


def test_t_rec1_materialize_installs_a_verified_file(lab):
    c = lab.clone()
    ok(lab.block("materialize", c))
    assert hashlib.sha256((c / REL).read_bytes()).hexdigest() == VENDORED_SHA
    result = ok(lab.run(["python3", "scripts/check_tooltempest_lock.py"], c))
    assert "OK" in text(result)
    assert leftovers(lab, c) == []


def test_t_rec2_materialize_with_a_failing_git_show_installs_nothing(lab):
    c = lab.clone()
    (c / LOCK).write_text(lab.lock_text(commit="b" * 40))
    result = blocked(lab.block("materialize", c))
    assert "git show" in text(result)
    assert not (c / REL).exists()
    assert leftovers(lab, c) == []


def test_t_rec3_materialize_with_a_wrong_lock_hash_installs_nothing(lab):
    c = lab.clone()
    (c / LOCK).write_text(lab.lock_text(sha256=BAD_SHA))
    result = blocked(lab.block("materialize", c))
    assert BAD_SHA in text(result) and VENDORED_SHA in text(result)
    assert not (c / REL).exists()
    assert leftovers(lab, c) == []


def test_t_rec4_materialize_never_overwrites_an_existing_file(lab):
    c = lab.clone()
    lab.materialize(c, b"someone's work in progress\n")
    result = blocked(lab.block("materialize", c))
    assert "already exists" in text(result)
    assert (c / REL).read_bytes() == b"someone's work in progress\n"
    assert leftovers(lab, c) == []


def test_t_rec5_verify_upstream_reports_a_match(lab):
    result = ok(lab.block("verify-upstream", lab.proj))
    assert "MATCH" in text(result) and "MISMATCH" not in text(result)
    assert leftovers(lab, lab.proj) == []


def test_t_rec6_verify_upstream_reports_a_mismatch(lab):
    (lab.proj / LOCK).write_text(lab.lock_text(sha256=BAD_SHA))
    result = blocked(lab.block("verify-upstream", lab.proj))
    assert "MISMATCH" in text(result)
    assert leftovers(lab, lab.proj) == []


def test_t_rec7_verify_upstream_does_not_report_a_result_when_git_show_fails(lab):
    (lab.proj / LOCK).write_text(lab.lock_text(commit="b" * 40))
    result = blocked(lab.block("verify-upstream", lab.proj))
    combined = text(result)
    assert "ERROR" in combined
    assert "MATCH" not in combined and "MISMATCH" not in combined
    assert EMPTY_INPUT_SHA not in combined  # the hash of empty input is what a failed pipe would have produced
    assert leftovers(lab, lab.proj) == []
