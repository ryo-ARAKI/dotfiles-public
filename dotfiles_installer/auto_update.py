from __future__ import annotations

import argparse
from dataclasses import dataclass
import fcntl
import os
from pathlib import Path
import subprocess
import sys
from contextlib import ExitStack, contextmanager

from dotfiles_installer.context import detect_context


class UpdateError(RuntimeError):
    """Raised when automatic repo synchronization cannot proceed safely."""


@dataclass(frozen=True)
class ManagedRepo:
    name: str
    path: Path


@dataclass(frozen=True)
class RepoSyncResult:
    name: str
    status: str
    changed: bool
    applied: bool = False


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def should_run_install(results: list[RepoSyncResult]) -> bool:
    return any(result.applied for result in results)


def default_repo_path(base_root: Path, repo_name: str) -> Path:
    if (
        len(base_root.parts) >= 2
        and base_root.parent.name in {".worktrees", "worktrees"}
        and base_root.parent.parent.name == "dotfiles-public"
    ):
        return base_root.parent.parent.parent / repo_name
    return base_root.parent / repo_name


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--private", type=Path)
    parser.add_argument("--hosts", type=Path)
    parser.add_argument("--context", choices=("local", "remote"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--lock-file", type=Path)
    return parser.parse_args(argv)


@contextmanager
def acquire_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_file = lock_path.open("w", encoding="utf-8")
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        lock_file.close()
        yield None
        return

    try:
        yield lock_file
    finally:
        lock_file.close()


def ensure_repo_exists(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.is_dir():
        raise UpdateError(f"{label} repository path does not exist: {resolved}")
    return resolved


def run_install(
    base_root: Path,
    private_root: Path,
    hosts_root: Path,
    *,
    context: str | None,
    dry_run: bool,
) -> int:
    command = [
        str(base_root / "install"),
        "--yes",
    ]
    if context is not None:
        command.extend(["--context", context])
    command.extend([
        "--private",
        str(private_root),
        "--hosts",
        str(hosts_root),
    ])
    if dry_run:
        command.insert(1, "--dry-run")

    try:
        result = subprocess.run(command, cwd=base_root, check=False)
    except OSError as exc:
        raise UpdateError("installer launch failed") from exc
    return result.returncode


def sync_repo(repo: ManagedRepo, *, dry_run: bool) -> RepoSyncResult:
    try:
        dirty = run_git(repo.path, "status", "--porcelain")
    except subprocess.CalledProcessError as exc:
        raise UpdateError(f"{repo.name} repository status check failed") from exc
    if dirty:
        raise UpdateError(f"{repo.name} repository is dirty: {repo.path}")

    try:
        upstream = run_git(repo.path, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    except subprocess.CalledProcessError as exc:
        raise UpdateError(f"{repo.name} repository has no upstream tracking branch") from exc

    try:
        run_git(repo.path, "fetch", "--quiet")
    except subprocess.CalledProcessError as exc:
        raise UpdateError(f"{repo.name} repository fetch failed") from exc

    try:
        counts = run_git(repo.path, "rev-list", "--left-right", "--count", f"HEAD...{upstream}")
        ahead_str, behind_str = counts.split()
        ahead = int(ahead_str)
        behind = int(behind_str)
    except (subprocess.CalledProcessError, ValueError) as exc:
        raise UpdateError(f"{repo.name} repository sync state check failed") from exc

    if behind and ahead:
        raise UpdateError(f"{repo.name} repository has diverged from {upstream}")
    if ahead:
        raise UpdateError(f"{repo.name} repository is ahead of {upstream}")
    if not behind:
        return RepoSyncResult(name=repo.name, status="current", changed=False, applied=False)

    if not dry_run:
        try:
            run_git(repo.path, "merge", "--ff-only", upstream)
        except subprocess.CalledProcessError as exc:
            raise UpdateError(f"{repo.name} repository merge failed") from exc
        return RepoSyncResult(name=repo.name, status="updated", changed=True, applied=True)

    return RepoSyncResult(name=repo.name, status="updated", changed=True, applied=False)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        base_root = ensure_repo_exists(args.base, "base")
        private_root = ensure_repo_exists(args.private or default_repo_path(base_root, "dotfiles-private"), "private")
        hosts_root = ensure_repo_exists(args.hosts or default_repo_path(base_root, "dotfiles-hosts"), "hosts")
        context = args.context or detect_context(None, os.environ)
    except UpdateError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    lock_path = (args.lock_file or (Path.home() / ".cache" / "dotfiles-public" / "update.lock")).expanduser()
    repos = [
        ManagedRepo(name="public", path=base_root),
        ManagedRepo(name="private", path=private_root),
        ManagedRepo(name="hosts", path=hosts_root),
    ]

    try:
        with ExitStack() as stack:
            try:
                lock_handle = stack.enter_context(acquire_lock(lock_path))
            except OSError:
                print("lock file setup failed", file=sys.stderr)
                return 1

            if lock_handle is None:
                print("dotfiles updater already running")
                return 0

            results = [sync_repo(repo, dry_run=args.dry_run) for repo in repos]
            pending_updates = any(result.changed for result in results)
            if args.dry_run and pending_updates:
                print("dry-run: installer would run")
                return 0

            if not should_run_install(results):
                print("no repository updates detected")
                return 0

            install_code = run_install(base_root, private_root, hosts_root, context=context, dry_run=False)
            if install_code != 0:
                print("installer run failed", file=sys.stderr)
            return install_code
    except UpdateError as exc:
        print(str(exc), file=sys.stderr)
        return 1
