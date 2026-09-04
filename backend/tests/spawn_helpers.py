"""Importable helpers for subprocess-backed runner tests."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path


def return_requested_state(
    _session_id: str,
    _direction: dict,
    initial_state: dict,
    *,
    progress_callback=None,
    cancellation_check=None,
) -> dict:
    return initial_state["_test_child_result"]


def fail_with_sensitive_text(
    _session_id: str,
    _direction: dict,
    _initial_state: dict,
    *,
    progress_callback=None,
    cancellation_check=None,
) -> dict:
    raise RuntimeError("provider body contains secret-token")


def blocking_prewrite_with_descendant(
    _session_id: str,
    _direction: dict,
    initial_state: dict,
    *,
    progress_callback=None,
    cancellation_check=None,
) -> dict:
    """Block long enough to prove the runner kills this process tree."""
    started_path = Path(initial_state["_test_started_path"])
    finished_path = Path(initial_state["_test_finished_path"])
    started_path.write_text("started", encoding="utf-8")
    if progress_callback:
        progress_callback("blocking_test_node", "started", {})
    subprocess.Popen(
        [
            sys.executable,
            "-c",
            (
                "import pathlib,time; time.sleep(1.5); "
                f"pathlib.Path({str(finished_path)!r}).write_text('finished')"
            ),
        ],
        start_new_session=True,
    )
    time.sleep(10)
    return {"unexpected": "blocking work completed"}


def write_upload_result(
    _session_id: str,
    initial_state: dict,
    *,
    progress_callback=None,
    cancellation_check=None,
) -> dict:
    """Write one readable attempt result with a tolerated step degradation."""
    workspace = Path(initial_state["workspace"])
    workspace.mkdir(parents=True, exist_ok=True)
    cleaned = workspace / "cleaned.csv"
    cleaned.write_text("x,y\n1,2\n", encoding="utf-8")
    if progress_callback:
        progress_callback("clean_data", "completed", {"steps": 8})
    return {
        **initial_state,
        "csv_path": str(cleaned),
        "cleaning_report": {
            "steps": [
                {
                    "name": "audit",
                    "status": "failed",
                    "report": {"error": "audit-only degradation"},
                }
            ]
        },
    }


def return_unreadable_upload_result(
    _session_id: str,
    initial_state: dict,
    *,
    progress_callback=None,
    cancellation_check=None,
) -> dict:
    return {
        **initial_state,
        "csv_path": str(Path(initial_state["workspace"]) / "missing.csv"),
        "cleaning_report": {"steps": []},
    }


def fail_upload_with_sensitive_text(
    _session_id: str,
    _initial_state: dict,
    *,
    progress_callback=None,
    cancellation_check=None,
) -> dict:
    raise RuntimeError("secret-token at /private/upload/source.csv")


def blocking_upload_with_descendant(
    _session_id: str,
    initial_state: dict,
    *,
    progress_callback=None,
    cancellation_check=None,
) -> dict:
    """Block so Session deletion must revoke the upload process tree."""
    started_path = Path(initial_state["_test_started_path"])
    finished_path = Path(initial_state["_test_finished_path"])
    workspace = Path(initial_state["workspace"])
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "partial.csv").write_text("x\n1\n", encoding="utf-8")
    started_path.write_text("started", encoding="utf-8")
    if progress_callback:
        progress_callback("clean_data", "started", {})
    subprocess.Popen(
        [
            sys.executable,
            "-c",
            (
                "import pathlib,time; time.sleep(1.5); "
                f"pathlib.Path({str(finished_path)!r}).write_text('finished')"
            ),
        ],
        start_new_session=True,
    )
    time.sleep(10)
    return {"unexpected": "blocking upload completed"}
