"""Contracts for the pure, cancellable upload computation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from agent.engine.cancellation import ExecutionCancelled
from agent.engine.upload import run_upload
from agent.nodes.clean_data import clean_data
from agent.nodes.upload_data import upload_data


def _without_timing(state: dict) -> dict:
    state = deepcopy(state)
    for step in (state.get("cleaning_report") or {}).get("steps", []):
        step.pop("started_at", None)
        step.pop("duration", None)
    return state


def test_run_upload_matches_existing_two_node_semantics(tmp_path):
    csv_path = tmp_path / "input.csv"
    csv_path.write_text("id,value\n1,10\n2,\n", encoding="utf-8")
    initial_state = {
        "session_id": "upload-equivalence",
        "csv_path": str(csv_path),
        "uploaded_datasets": [{"path": str(csv_path), "format": "csv"}],
        "workspace": str(tmp_path / "attempts" / "run-1" / "epoch-1"),
    }
    original = deepcopy(initial_state)

    after_upload = {**initial_state, **upload_data(initial_state)}
    expected = {**after_upload, **clean_data(after_upload)}
    events: list[tuple[str, str]] = []
    actual = run_upload(
        initial_state,
        progress=lambda node, status, _detail: events.append((node, status)),
    )

    assert initial_state == original
    assert _without_timing(actual) == _without_timing(expected)
    assert len(actual["cleaning_report"]["steps"]) == 8
    assert events == [
        ("upload_data", "started"),
        ("upload_data", "completed"),
        ("clean_data", "started"),
        ("clean_data", "completed"),
    ]


def test_run_upload_checks_cancellation_between_nodes(monkeypatch, tmp_path):
    checks = iter((False, False, True))
    clean_called = False

    def fake_upload(_state):
        return {"uploaded_datasets": [{"path": "parsed.csv"}]}

    def fake_clean(_state):
        nonlocal clean_called
        clean_called = True
        return {}

    monkeypatch.setattr("agent.engine.upload.upload_data", fake_upload)
    monkeypatch.setattr("agent.engine.upload.clean_data", fake_clean)

    with pytest.raises(ExecutionCancelled):
        run_upload(
            {"workspace": str(tmp_path)},
            should_cancel=lambda: next(checks),
        )

    assert not clean_called


def test_distinct_attempt_workspaces_isolate_cleaning_outputs(tmp_path):
    csv_path = tmp_path / "source.csv"
    csv_path.write_text("id,value\n1,10\n2,20\n", encoding="utf-8")

    results = []
    for epoch in (1, 2):
        results.append(
            run_upload(
                {
                    "session_id": "workspace-isolation",
                    "csv_path": str(csv_path),
                    "uploaded_datasets": [{"path": str(csv_path)}],
                    "workspace": str(
                        tmp_path / "attempts" / "run-1" / f"epoch-{epoch}"
                    ),
                }
            )
        )

    first_path = Path(results[0]["csv_path"])
    second_path = Path(results[1]["csv_path"])
    assert first_path.exists() and second_path.exists()
    assert first_path != second_path
    assert "epoch-1" in first_path.parts
    assert "epoch-2" in second_path.parts

