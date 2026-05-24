"""Git experiment logger: auto-commit after each orchestrator stage."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def _ensure_git_repo(project_root: Path) -> None:
    """Initialize git repo if not exists."""
    git_dir = project_root / ".git"
    if not git_dir.exists():
        subprocess.run(
            ["git", "init"],
            cwd=project_root,
            capture_output=True,
            check=True,
        )


def commit_stage(
    project_root: Path,
    stage: str,
    agent_name: str,
    status: str,
) -> dict[str, Any]:
    """Commit stage changes to git.

    Returns {"committed": bool, "message": str, "commit_hash": str}.
    """
    _ensure_git_repo(project_root)

    # Stage only relevant directories
    for directory in ["Manuscripts", "Results", "state"]:
        target = project_root / directory
        if target.exists():
            subprocess.run(
                ["git", "add", directory],
                cwd=project_root,
                capture_output=True,
            )

    message = f"experiment: stage={stage} agent={agent_name} status={status}"

    # Check if there are changes to commit
    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=project_root,
        capture_output=True,
    )
    if diff.returncode == 0:
        # No changes staged
        return {"committed": False, "message": message, "commit_hash": "", "reason": "no_changes"}

    result = subprocess.run(
        ["git", "commit", "-m", message],
        cwd=project_root,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        )
        commit_hash = hash_result.stdout.strip()
        return {"committed": True, "message": message, "commit_hash": commit_hash}

    return {"committed": False, "message": message, "commit_hash": "", "reason": result.stderr}


def get_experiment_history(project_root: Path, limit: int = 50) -> list[dict[str, Any]]:
    """Return list of experiment commits from git log."""
    _ensure_git_repo(project_root)

    result = subprocess.run(
        [
            "git", "log",
            f"--max-count={limit}",
            "--pretty=format:%H|%ci|%s",
            "--grep=experiment:",
        ],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=True,
    )

    experiments = []
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|", 2)
        if len(parts) < 3:
            continue
        commit_hash, timestamp, message = parts
        # Parse experiment message
        # Format: experiment: stage=XX agent=YY status=ZZ
        info = {"commit_hash": commit_hash, "timestamp": timestamp, "message": message}
        for segment in message.replace("experiment: ", "").split(" "):
            if "=" in segment:
                key, value = segment.split("=", 1)
                info[key] = value
        experiments.append(info)

    return experiments


def revert_to_commit(
    project_root: Path,
    commit_hash: str,
) -> dict[str, Any]:
    """Revert project state to a specific commit.

    Restores Manuscripts/, Results/, state/ from the commit.
    """
    _ensure_git_repo(project_root)

    # Checkout specific directories from the commit
    for directory in ["Manuscripts", "Results", "state"]:
        target = project_root / directory
        if target.exists():
            result = subprocess.run(
                ["git", "checkout", commit_hash, "--", directory],
                cwd=project_root,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                # Skip if directory is not tracked by git (empty dir)
                if "did not match any file(s) known to git" in result.stderr:
                    continue
                return {"reverted": False, "reason": result.stderr}

    return {"reverted": True, "commit_hash": commit_hash}
