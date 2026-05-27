from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_run_plan_seed_approval.v1"
DEFAULT_RUN_PLAN_SEED_PATH = Path("Results/json/cgss_social_capital_happiness_run_plan_seed.json")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_run_plan_seed_approval.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_run_plan_seed_approval.md")
DEFAULT_APPROVED_SEED_PATH = Path("Results/json/cgss_social_capital_happiness_run_plan_seed_approved.json")
APPROVAL_DECISION = "human_approve_cgss_run_plan_seed"
VALID_DECISIONS = {"defer", "approve", "revise", "reject"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_cgss_run_plan_seed_approval(
    run_plan_seed_report: dict[str, Any],
    decision: str,
    reviewer: str,
    note: str,
) -> dict[str, Any]:
    decision = decision.strip().lower()
    reviewer = reviewer.strip()
    note = note.strip()
    if decision not in VALID_DECISIONS:
        decision = "defer"

    record = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": run_plan_seed_report.get("topic", ""),
        "decision": decision,
        "reviewer": reviewer,
        "note": note,
        "approved": False,
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "can_write_product_state": False,
        "source_run_plan_seed": {
            "schema_version": run_plan_seed_report.get("schema_version", ""),
            "status": run_plan_seed_report.get("status", ""),
            "task_count": len(run_plan_seed_report.get("run_plan_seed", {}).get("tasks", [])),
            "required_decision": run_plan_seed_report.get("promotion", {}).get("required_decision", ""),
        },
        "approved_run_plan_seed": {},
    }

    if decision == "defer":
        record.update(
            {
                "status": "pending_human_run_plan_seed_decision",
                "blocking_reasons": [APPROVAL_DECISION],
                "promotion": {"allowed": False, "required_decision": APPROVAL_DECISION},
            }
        )
        return record

    metadata_reasons = missing_metadata_reasons(reviewer, note)
    if metadata_reasons:
        record.update(
            {
                "status": "blocked_missing_human_approval_metadata",
                "blocking_reasons": metadata_reasons,
                "promotion": {"allowed": False, "required_decision": "record_reviewer_and_decision_note"},
            }
        )
        return record

    if decision == "approve":
        approved_seed = make_approved_seed(run_plan_seed_report, reviewer, note)
        record.update(
            {
                "status": "run_plan_seed_approved_for_draft_execution",
                "approved": True,
                "blocking_reasons": [],
                "approved_run_plan_seed": approved_seed,
                "promotion": {"allowed": True, "would_enable": ["execute_cgss_run_plan_seed"]},
            }
        )
        return record

    if decision == "revise":
        record.update(
            {
                "status": "run_plan_seed_needs_changes",
                "blocking_reasons": ["run_plan_seed_needs_changes_before_execution"],
                "promotion": {"allowed": False, "required_decision": "revise_cgss_run_plan_seed"},
            }
        )
        return record

    record.update(
        {
            "status": "run_plan_seed_rejected",
            "blocking_reasons": ["run_plan_seed_rejected_by_human_reviewer"],
            "promotion": {"allowed": False, "required_decision": "rebuild_cgss_run_plan_seed"},
        }
    )
    return record


def missing_metadata_reasons(reviewer: str, note: str) -> list[str]:
    reasons = []
    if not reviewer:
        reasons.append("reviewer_required")
    if not note:
        reasons.append("approval_note_required")
    return reasons


def make_approved_seed(run_plan_seed_report: dict[str, Any], reviewer: str, note: str) -> dict[str, Any]:
    approved_seed = deepcopy(run_plan_seed_report.get("run_plan_seed", {}))
    approved_seed["status"] = "approved_for_draft_execution"
    approved_seed["human_approval"] = {
        "status": "approved",
        "decision": APPROVAL_DECISION,
        "approved_by": reviewer,
        "note": note,
        "approved_at": datetime.now(timezone.utc).isoformat(),
    }
    approved_seed["promotion"] = {
        "allowed": True,
        "required_decision": "human_review_cgss_execution_results",
    }
    approved_seed["formal_writeback_allowed"] = False
    approved_seed["draft_layer_only"] = True
    return approved_seed


def write_cgss_run_plan_seed_approval_outputs(
    project_root: Path,
    record: dict[str, Any],
    result_path: Path,
    review_path: Path,
    approved_seed_path: Path,
) -> tuple[Path, Path, Path | None]:
    absolute_result = project_root / result_path
    absolute_result.parent.mkdir(parents=True, exist_ok=True)
    absolute_result.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    absolute_review = project_root / review_path
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.write_text(render_review(record), encoding="utf-8")

    if not record.get("approved_run_plan_seed"):
        return absolute_result, absolute_review, None

    absolute_approved_seed = project_root / approved_seed_path
    absolute_approved_seed.parent.mkdir(parents=True, exist_ok=True)
    absolute_approved_seed.write_text(
        json.dumps(record["approved_run_plan_seed"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return absolute_result, absolute_review, absolute_approved_seed


def render_review(record: dict[str, Any]) -> str:
    lines = [
        "# CGSS RunPlan seed 审阅决策",
        "",
        f"- 题目：{record.get('topic', '')}",
        f"- schema：`{record['schema_version']}`",
        f"- 状态：`{record['status']}`",
        f"- 决策：`{record['decision']}`",
        f"- 审阅人：{record.get('reviewer') or '未记录'}",
        "- 草案层：是",
        "- 写入正式 RunPlan：否",
        "- 写入 state/product：否",
        "- 执行模型：否，本节点只记录审阅决策",
    ]
    if record.get("note"):
        lines.extend(["", "## 决策说明", record["note"]])
    if record.get("blocking_reasons"):
        lines.extend(["", "## 当前阻断"])
        for reason in record["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    if record.get("approved"):
        lines.extend(
            [
                "",
                "## 批准后可进入",
                "- `Program/cgss_run_plan_seed_executor.py --run-plan-seed Results/json/cgss_social_capital_happiness_run_plan_seed_approved.json`",
            ]
        )
    lines.extend(["", "## 决策 JSON", "```json", json.dumps(record, ensure_ascii=False, indent=2), "```"])
    return "\n".join(lines) + "\n"
