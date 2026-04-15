"""Git context helpers: recent logs, diffs, and change-frequency data."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any

log = logging.getLogger("ai-indexer.git")


def _run(args: list[str], cwd: Path) -> str:
    """Run a git command and return stdout, or empty string on failure."""
    try:
        result = subprocess.run(
            args, cwd=str(cwd),
            capture_output=True, text=True, timeout=15,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception as e:
        log.debug("git command failed %s: %s", args, e)
        return ""


def is_git_repo(root: Path) -> bool:
    return (_run(["git", "rev-parse", "--is-inside-work-tree"], root) == "true")


def get_recent_logs(root: Path, count: int = 10) -> list[dict[str, str]]:
    """Return the last *count* commit log entries as dicts."""
    fmt = "%H\x1f%an\x1f%ae\x1f%ai\x1f%s"
    raw = _run(
        ["git", "log", f"--max-count={count}", f"--format={fmt}"],
        root,
    )
    entries: list[dict[str, str]] = []
    for line in raw.splitlines():
        parts = line.split("\x1f")
        if len(parts) == 5:
            entries.append({
                "hash":    parts[0][:12],
                "author":  parts[1],
                "email":   parts[2],
                "date":    parts[3],
                "message": parts[4],
            })
    return entries


def get_staged_diff(root: Path) -> str:
    """Return the git diff of staged changes (HEAD vs working tree)."""
    diff = _run(["git", "diff", "--stat", "HEAD"], root)
    return diff


def get_file_change_counts(root: Path, max_commits: int = 100) -> dict[str, int]:
    """Map relative file path → number of commits that touched it (last N commits)."""
    raw = _run(
        ["git", "log", f"--max-count={max_commits}", "--name-only", "--format="],
        root,
    )
    counts: dict[str, int] = {}
    for line in raw.splitlines():
        line = line.strip()
        if line:
            counts[line] = counts.get(line, 0) + 1
    return counts


def build_git_context(
    root: Path,
    include_logs: bool = True,
    logs_count: int = 10,
    include_diffs: bool = False,
    sort_by_changes: bool = False,
    sort_max_commits: int = 100,
) -> dict[str, Any]:
    """Build a git context dict for inclusion in the output payload."""
    ctx: dict[str, Any] = {}

    if not is_git_repo(root):
        log.debug("Not a git repository: %s", root)
        return ctx

    if include_logs:
        ctx["recent_commits"] = get_recent_logs(root, logs_count)

    if include_diffs:
        ctx["diff_stat"] = get_staged_diff(root)

    if sort_by_changes:
        ctx["change_frequency"] = get_file_change_counts(root, sort_max_commits)

    return ctx
