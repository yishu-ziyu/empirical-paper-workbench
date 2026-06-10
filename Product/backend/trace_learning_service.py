from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id


TRACE_LEARNING_BAD_CASES_PATH = Path("state/product/trace_learning_bad_cases.jsonl")
ALLOWED_TRACE_LEARNING_FIX_LAYERS = [
    "prompt",
    "skill_playbook",
    "decision_rule",
    "knowledge_base",
    "retrieval",
    "tool_interface",
    "memory",
    "output_format",
    "clarification_flow",
    "product_boundary",
    "eval_set",
]


def trace_learning_bad_cases_path(project_root: Path) -> Path:
    return project_root / TRACE_LEARNING_BAD_CASES_PATH


def capture_project_trace_learning_bad_case(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    path = trace_learning_bad_cases_path(project_root)
    existing_cases = load_trace_learning_bad_cases(path)
    timestamp = utc_now()
    fix_layer = normalize_fix_layer(payload.get("fix_layer"))
    record: dict[str, Any] = {
        "id": build_bad_case_id(existing_cases, payload.get("stage")),
        "trace_learning_version": 1,
        "status": "captured",
        "created_at": timestamp,
        "project_id": project["id"],
        "stage": str(payload.get("stage") or "unknown"),
        "surface": str(payload.get("surface") or "unknown"),
        "page_url": str(payload.get("page_url") or ""),
        "target_text": str(payload.get("target_text") or ""),
        "agent_output": str(payload.get("agent_output") or ""),
        "user_feedback": str(payload.get("user_feedback") or "").strip(),
        "expected_behavior": str(payload.get("expected_behavior") or ""),
        "fix_layer": fix_layer,
        "severity": str(payload.get("severity") or "medium"),
        "related_files": normalize_string_list(payload.get("related_files")),
        "writes_formal_layer": False,
        "next_action": "turn_into_regression_test",
        "regression_target": {
            "kind": "contract_test",
            "status": "pending",
            "suggested_test_name": f"test_trace_learning_bad_case_{slugify(payload.get('stage') or 'unknown')}",
        },
    }
    original_fix_layer = str(payload.get("fix_layer") or "")
    if original_fix_layer and original_fix_layer != fix_layer:
        record["original_fix_layer"] = original_fix_layer

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    return {
        "project_id": project["id"],
        "bad_case": record,
        "trace_learning": build_trace_learning_summary(path, len(existing_cases) + 1),
    }


def get_project_trace_learning_bad_cases(product_root: Path, repo_root: Path, project_id: str) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    path = trace_learning_bad_cases_path(project_root)
    cases = load_trace_learning_bad_cases(path)
    summary = build_trace_learning_summary(path, len(cases))
    summary["bad_cases"] = cases
    return {"project_id": project["id"], "trace_learning": summary}


def load_trace_learning_bad_cases(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    cases: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            cases.append(json.loads(line))
    return cases


def build_trace_learning_summary(path: Path, case_count: int) -> dict[str, Any]:
    return {
        "path": TRACE_LEARNING_BAD_CASES_PATH.as_posix(),
        "case_count": case_count,
        "absolute_path": str(path),
        "allowed_fix_layers": ALLOWED_TRACE_LEARNING_FIX_LAYERS,
    }


def normalize_fix_layer(value: Any) -> str:
    fix_layer = str(value or "").strip()
    if fix_layer in ALLOWED_TRACE_LEARNING_FIX_LAYERS:
        return fix_layer
    return "eval_set"


def normalize_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


def build_bad_case_id(existing_cases: list[dict[str, Any]], stage: Any) -> str:
    return f"bad_case_{len(existing_cases) + 1:04d}_{slugify(stage or 'unknown')}"


def slugify(value: Any) -> str:
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unknown"
