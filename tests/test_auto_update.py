import tempfile
import subprocess
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import Mock, call, patch

from dotfiles_installer.auto_update import (
    ManagedRepo,
    RepoSyncResult,
    UpdateError,
    default_repo_path,
    main,
    run_install,
    should_run_install,
    sync_repo,
)


@contextmanager
def captured_stdio():
    with patch("sys.stdout.write") as stdout_write, patch("sys.stderr.write") as stderr_write:
        yield stdout_write, stderr_write


class SyncRepoTests(unittest.TestCase):
    def test_sync_repo_returns_current_when_head_matches_upstream(self) -> None:
        repo = ManagedRepo(name="public", path=Path("/tmp/public"))
        with patch("dotfiles_installer.auto_update.run_git") as run_git:
            run_git.side_effect = [
                "",
                "origin/main",
                "",
                "0\t0",
            ]

            result = sync_repo(repo, dry_run=False)

        self.assertEqual(result.status, "current")
        self.assertFalse(result.changed)
        self.assertFalse(result.applied)
        self.assertEqual(
            run_git.call_args_list,
            [
                call(repo.path, "status", "--porcelain"),
                call(repo.path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"),
                call(repo.path, "fetch", "--quiet"),
                call(repo.path, "rev-list", "--left-right", "--count", "HEAD...origin/main"),
            ],
        )

    def test_sync_repo_returns_updated_when_fast_forward_is_available(self) -> None:
        repo = ManagedRepo(name="public", path=Path("/tmp/public"))
        with patch("dotfiles_installer.auto_update.run_git") as run_git:
            run_git.side_effect = [
                "",
                "origin/main",
                "",
                "0\t3",
                "",
            ]

            result = sync_repo(repo, dry_run=False)

        self.assertEqual(result.status, "updated")
        self.assertTrue(result.changed)
        self.assertTrue(result.applied)
        self.assertEqual(
            run_git.call_args_list,
            [
                call(repo.path, "status", "--porcelain"),
                call(repo.path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"),
                call(repo.path, "fetch", "--quiet"),
                call(repo.path, "rev-list", "--left-right", "--count", "HEAD...origin/main"),
                call(repo.path, "merge", "--ff-only", "origin/main"),
            ],
        )

    def test_sync_repo_returns_distinguishable_dry_run_update(self) -> None:
        repo = ManagedRepo(name="public", path=Path("/tmp/public"))
        with patch("dotfiles_installer.auto_update.run_git") as run_git:
            run_git.side_effect = [
                "",
                "origin/main",
                "",
                "0\t3",
            ]

            result = sync_repo(repo, dry_run=True)

        self.assertEqual(result.status, "updated")
        self.assertTrue(result.changed)
        self.assertFalse(result.applied)
        self.assertEqual(
            run_git.call_args_list,
            [
                call(repo.path, "status", "--porcelain"),
                call(repo.path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"),
                call(repo.path, "fetch", "--quiet"),
                call(repo.path, "rev-list", "--left-right", "--count", "HEAD...origin/main"),
            ],
        )

    def test_sync_repo_raises_for_dirty_worktree(self) -> None:
        repo = ManagedRepo(name="public", path=Path("/tmp/public"))
        with patch("dotfiles_installer.auto_update.run_git", return_value=" M install\n"):
            with self.assertRaises(UpdateError) as ctx:
                sync_repo(repo, dry_run=False)

        self.assertIn("dirty", str(ctx.exception))

    def test_sync_repo_raises_for_diverged_branch(self) -> None:
        repo = ManagedRepo(name="public", path=Path("/tmp/public"))
        with patch("dotfiles_installer.auto_update.run_git") as run_git:
            run_git.side_effect = [
                "",
                "origin/main",
                "",
                "2\t1",
            ]

            with self.assertRaises(UpdateError) as ctx:
                sync_repo(repo, dry_run=False)

        self.assertIn("diverged", str(ctx.exception))

    def test_sync_repo_raises_for_ahead_only_branch_without_merging(self) -> None:
        repo = ManagedRepo(name="public", path=Path("/tmp/public"))
        with patch("dotfiles_installer.auto_update.run_git") as run_git:
            run_git.side_effect = [
                "",
                "origin/main",
                "",
                "1\t0",
            ]

            with self.assertRaises(UpdateError) as ctx:
                sync_repo(repo, dry_run=False)

        self.assertIn("ahead", str(ctx.exception))
        self.assertEqual(
            run_git.call_args_list,
            [
                call(repo.path, "status", "--porcelain"),
                call(repo.path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"),
                call(repo.path, "fetch", "--quiet"),
                call(repo.path, "rev-list", "--left-right", "--count", "HEAD...origin/main"),
            ],
        )

    def test_sync_repo_raises_for_missing_upstream(self) -> None:
        repo = ManagedRepo(name="public", path=Path("/tmp/public"))
        error = subprocess.CalledProcessError(
            128,
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
            stderr="fatal: no upstream configured",
        )
        with patch("dotfiles_installer.auto_update.run_git") as run_git:
            run_git.side_effect = ["", error]

            with self.assertRaises(UpdateError) as ctx:
                sync_repo(repo, dry_run=False)

        self.assertIn("upstream", str(ctx.exception))

    def test_sync_repo_normalizes_fetch_failure(self) -> None:
        repo = ManagedRepo(name="public", path=Path("/tmp/public"))
        error = subprocess.CalledProcessError(1, ["git", "fetch", "--quiet"], stderr="fetch failed")
        with patch("dotfiles_installer.auto_update.run_git") as run_git:
            run_git.side_effect = [
                "",
                "origin/main",
                error,
            ]

            with self.assertRaises(UpdateError) as ctx:
                sync_repo(repo, dry_run=False)

        self.assertIn("fetch", str(ctx.exception))
        self.assertEqual(
            run_git.call_args_list,
            [
                call(repo.path, "status", "--porcelain"),
                call(repo.path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"),
                call(repo.path, "fetch", "--quiet"),
            ],
        )

    def test_sync_repo_normalizes_merge_failure(self) -> None:
        repo = ManagedRepo(name="public", path=Path("/tmp/public"))
        error = subprocess.CalledProcessError(1, ["git", "merge", "--ff-only", "origin/main"], stderr="merge failed")
        with patch("dotfiles_installer.auto_update.run_git") as run_git:
            run_git.side_effect = [
                "",
                "origin/main",
                "",
                "0\t3",
                error,
            ]

            with self.assertRaises(UpdateError) as ctx:
                sync_repo(repo, dry_run=False)

        self.assertIn("merge", str(ctx.exception))
        self.assertEqual(
            run_git.call_args_list,
            [
                call(repo.path, "status", "--porcelain"),
                call(repo.path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"),
                call(repo.path, "fetch", "--quiet"),
                call(repo.path, "rev-list", "--left-right", "--count", "HEAD...origin/main"),
                call(repo.path, "merge", "--ff-only", "origin/main"),
            ],
        )


class InstallDecisionTests(unittest.TestCase):
    def test_should_run_install_only_when_any_repo_was_applied(self) -> None:
        unchanged = RepoSyncResult(name="public", status="current", changed=False, applied=False)
        dry_run_update = RepoSyncResult(name="private", status="updated", changed=True, applied=False)
        applied_update = RepoSyncResult(name="private", status="updated", changed=True, applied=True)

        self.assertFalse(should_run_install([unchanged]))
        self.assertFalse(should_run_install([unchanged, dry_run_update]))
        self.assertTrue(should_run_install([unchanged, applied_update]))


class RunInstallCommandTests(unittest.TestCase):
    def test_run_install_passes_context_through_to_installer_command(self) -> None:
        base_root = Path("/tmp/dev/dotfiles-public")
        private_root = Path("/tmp/dev/dotfiles-private")
        hosts_root = Path("/tmp/dev/dotfiles-hosts")

        with patch("dotfiles_installer.auto_update.subprocess.run", return_value=Mock(returncode=0)) as run:
            exit_code = run_install(base_root, private_root, hosts_root, context="remote", dry_run=False)

        self.assertEqual(exit_code, 0)
        run.assert_called_once_with(
            [
                str(base_root / "install"),
                "--yes",
                "--context",
                "remote",
                "--private",
                str(private_root),
                "--hosts",
                str(hosts_root),
            ],
            cwd=base_root,
            check=False,
        )


class PathResolutionTests(unittest.TestCase):
    def test_default_repo_path_uses_main_repo_parent_for_dot_worktrees_layout(self) -> None:
        base_root = Path("/tmp/dev/dotfiles-public/.worktrees/feature-dotfiles-auto-update")

        resolved = default_repo_path(base_root, "dotfiles-private")

        self.assertEqual(resolved, Path("/tmp/dev/dotfiles-private"))

    def test_default_repo_path_uses_main_repo_parent_for_worktrees_layout(self) -> None:
        base_root = Path("/tmp/dev/dotfiles-public/worktrees/feature-dotfiles-auto-update")

        resolved = default_repo_path(base_root, "dotfiles-hosts")

        self.assertEqual(resolved, Path("/tmp/dev/dotfiles-hosts"))

    def test_default_repo_path_does_not_misclassify_unrelated_worktrees_ancestor(self) -> None:
        base_root = Path("/tmp/dev/worktrees/archive/dotfiles-public")

        resolved = default_repo_path(base_root, "dotfiles-private")

        self.assertEqual(resolved, Path("/tmp/dev/worktrees/archive/dotfiles-private"))

    def test_default_repo_path_does_not_misclassify_direct_parent_worktrees_clone(self) -> None:
        base_root = Path("/tmp/dev/worktrees/dotfiles-public")

        resolved = default_repo_path(base_root, "dotfiles-private")

        self.assertEqual(resolved, Path("/tmp/dev/worktrees/dotfiles-private"))


class AutoUpdateCliTests(unittest.TestCase):
    def test_main_skips_install_when_no_repo_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            public = root / "dotfiles-public"
            private = root / "dotfiles-private"
            hosts = root / "dotfiles-hosts"
            for repo in (public, private, hosts):
                repo.mkdir()

            with patch("dotfiles_installer.auto_update.sync_repo") as sync_repo, patch(
                "dotfiles_installer.auto_update.run_install"
            ) as run_install, captured_stdio():
                sync_repo.side_effect = [
                    RepoSyncResult(name="public", status="current", changed=False),
                    RepoSyncResult(name="private", status="current", changed=False),
                    RepoSyncResult(name="hosts", status="current", changed=False),
                ]

                exit_code = main(
                    [
                        "--base",
                        str(public),
                        "--private",
                        str(private),
                        "--hosts",
                        str(hosts),
                        "--dry-run",
                    ]
                )

        self.assertEqual(exit_code, 0)
        run_install.assert_not_called()

    def test_main_runs_install_once_when_any_repo_changed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            public = root / "dotfiles-public"
            private = root / "dotfiles-private"
            hosts = root / "dotfiles-hosts"
            for repo in (public, private, hosts):
                repo.mkdir()

            with patch("dotfiles_installer.auto_update.detect_context", return_value="local"), patch(
                "dotfiles_installer.auto_update.sync_repo"
            ) as sync_repo, patch(
                "dotfiles_installer.auto_update.run_install",
                return_value=0,
            ) as run_install, captured_stdio():
                sync_repo.side_effect = [
                    RepoSyncResult(name="public", status="updated", changed=True, applied=True),
                    RepoSyncResult(name="private", status="current", changed=False),
                    RepoSyncResult(name="hosts", status="current", changed=False),
                ]

                exit_code = main(["--base", str(public), "--private", str(private), "--hosts", str(hosts)])

        self.assertEqual(exit_code, 0)
        run_install.assert_called_once_with(public, private, hosts, context="local", dry_run=False)

    def test_main_reports_dry_run_installer_when_updates_are_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            public = root / "dotfiles-public"
            private = root / "dotfiles-private"
            hosts = root / "dotfiles-hosts"
            for repo in (public, private, hosts):
                repo.mkdir()

            with patch("dotfiles_installer.auto_update.sync_repo") as sync_repo, patch(
                "dotfiles_installer.auto_update.run_install"
            ) as run_install, captured_stdio() as (stdout_write, _stderr_write):
                sync_repo.side_effect = [
                    RepoSyncResult(name="public", status="updated", changed=True, applied=False),
                    RepoSyncResult(name="private", status="current", changed=False),
                    RepoSyncResult(name="hosts", status="current", changed=False),
                ]

                exit_code = main(
                    [
                        "--base",
                        str(public),
                        "--private",
                        str(private),
                        "--hosts",
                        str(hosts),
                        "--dry-run",
                    ]
                )

        self.assertEqual(exit_code, 0)
        run_install.assert_not_called()
        self.assertIn(call("dry-run: installer would run"), stdout_write.call_args_list)
        self.assertIn(call("\n"), stdout_write.call_args_list)

    def test_main_returns_zero_when_lock_is_already_held(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            public = root / "dotfiles-public"
            private = root / "dotfiles-private"
            hosts = root / "dotfiles-hosts"
            for repo in (public, private, hosts):
                repo.mkdir()

            @contextmanager
            def locked_out(_path: Path):
                yield None

            with patch("dotfiles_installer.auto_update.acquire_lock", locked_out), captured_stdio():
                exit_code = main(["--base", str(public), "--private", str(private), "--hosts", str(hosts)])

        self.assertEqual(exit_code, 0)

    def test_main_returns_non_zero_when_lock_path_setup_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            public = root / "dotfiles-public"
            private = root / "dotfiles-private"
            hosts = root / "dotfiles-hosts"
            for repo in (public, private, hosts):
                repo.mkdir()

            lock_path = root / "locks" / "update.lock"
            with patch("pathlib.Path.mkdir", side_effect=OSError("permission denied")), captured_stdio() as (
                _stdout_write,
                stderr_write,
            ):
                exit_code = main(
                    [
                        "--base",
                        str(public),
                        "--private",
                        str(private),
                        "--hosts",
                        str(hosts),
                        "--lock-file",
                        str(lock_path),
                    ]
                )

        self.assertEqual(exit_code, 1)
        self.assertIn(call("lock file setup failed"), stderr_write.call_args_list)
        self.assertIn(call("\n"), stderr_write.call_args_list)

    def test_main_does_not_misclassify_later_oserror_as_lock_setup_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            public = root / "dotfiles-public"
            private = root / "dotfiles-private"
            hosts = root / "dotfiles-hosts"
            for repo in (public, private, hosts):
                repo.mkdir()

            with patch(
                "dotfiles_installer.auto_update.sync_repo",
                side_effect=OSError("unexpected os error"),
            ), captured_stdio() as (_stdout_write, stderr_write):
                with self.assertRaises(OSError):
                    main(["--base", str(public), "--private", str(private), "--hosts", str(hosts)])

        stderr_text = "".join(call.args[0] for call in stderr_write.call_args_list)
        self.assertNotIn("lock file setup failed", stderr_text)

    def test_main_returns_non_zero_when_git_status_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            public = root / "dotfiles-public"
            private = root / "dotfiles-private"
            hosts = root / "dotfiles-hosts"
            for repo in (public, private, hosts):
                repo.mkdir()

            error = subprocess.CalledProcessError(1, ["git", "status", "--porcelain"], stderr="status failed")
            with patch("dotfiles_installer.auto_update.run_git", side_effect=error), captured_stdio() as (
                _stdout_write,
                stderr_write,
            ):
                exit_code = main(["--base", str(public), "--private", str(private), "--hosts", str(hosts)])

        self.assertEqual(exit_code, 1)
        self.assertIn(call("public repository status check failed"), stderr_write.call_args_list)
        self.assertIn(call("\n"), stderr_write.call_args_list)

    def test_main_returns_non_zero_when_rev_list_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            public = root / "dotfiles-public"
            private = root / "dotfiles-private"
            hosts = root / "dotfiles-hosts"
            for repo in (public, private, hosts):
                repo.mkdir()

            error = subprocess.CalledProcessError(1, ["git", "rev-list", "--left-right", "--count"], stderr="rev-list failed")
            with patch("dotfiles_installer.auto_update.run_git") as run_git, captured_stdio() as (
                _stdout_write,
                stderr_write,
            ):
                run_git.side_effect = [
                    "",
                    "origin/main",
                    "",
                    error,
                ]

                exit_code = main(["--base", str(public), "--private", str(private), "--hosts", str(hosts)])

        self.assertEqual(exit_code, 1)
        self.assertIn(call("public repository sync state check failed"), stderr_write.call_args_list)
        self.assertIn(call("\n"), stderr_write.call_args_list)

    def test_main_returns_non_zero_when_installer_launch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            public = root / "dotfiles-public"
            private = root / "dotfiles-private"
            hosts = root / "dotfiles-hosts"
            for repo in (public, private, hosts):
                repo.mkdir()

            with patch("dotfiles_installer.auto_update.sync_repo") as sync_repo, patch(
                "dotfiles_installer.auto_update.subprocess.run",
                side_effect=OSError("exec format error"),
            ), captured_stdio() as (_stdout_write, stderr_write):
                sync_repo.side_effect = [
                    RepoSyncResult(name="public", status="updated", changed=True, applied=True),
                    RepoSyncResult(name="private", status="current", changed=False),
                    RepoSyncResult(name="hosts", status="current", changed=False),
                ]

                exit_code = main(["--base", str(public), "--private", str(private), "--hosts", str(hosts)])

        self.assertEqual(exit_code, 1)
        self.assertIn(call("installer launch failed"), stderr_write.call_args_list)
        self.assertIn(call("\n"), stderr_write.call_args_list)


if __name__ == "__main__":
    unittest.main()
