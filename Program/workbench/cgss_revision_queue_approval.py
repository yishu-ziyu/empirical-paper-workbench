from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_revision_queue_approval.v1"
DEFAULT_QUEUE_PATH = Path("Results/json/cgss_social_capital_happiness_revision_task_queue.json")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_revision_queue_approval.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_revision_queue_approval.md")
DEFAULT_APPROVED_QUEUE_PATH = Path("Results/json/cgss_social_capital_happiness_revision_task_queue_approved.json")
APPROVAL_DECISION = "human_approve_cgss_revision_task_queue"
VALID_DECISIONS = {"defer", "approve", "revise", "reject"}


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_revision_queue_approval(
    queue: dict[str, Any],
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
        "topic": queue.get("topic", ""),
        "decision": decision,
        "reviewer": reviewer,
        "note": note,
        "approved": False,
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "can_write_product_state": False,
        "source_queue": {
            "schema_version": queue.get("schema_version", ""),
            "status": queue.get("status", ""),
            "task_count": len(queue.get("agent_task_queue", [])),
            "required_decision": queue.get("promotion", {}).get("required_decision", ""),
        },
        "approved_queue": {},
    }

    if decision == "defer":
        record.update(
            {
                "status": "pending_human_revision_queue_decision",
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
        approved_queue = make_approved_queue(queue, reviewer, note)
        record.update(
            {
                "status": "revision_queue_approved_for_agent_work_orders",
                "approved": True,
                "blocking_reasons": [],
                "approved_queue": approved_queue,
                "promotion": {
                    "allowed": True,
                    "would_enable": ["cgss_revision_work_orders"],
                },
            }
        )
        return record

    if decision == "revise":
        record.update(
            {
                "status": "revision_queue_needs_changes",
                "blocking_reasons": ["revision_queue_needs_changes_before_agent_work_orders"],
                "promotion": {"allowed": False, "required_decision": "revise_cgss_revision_task_queue"},
            }
        )
        return record

    record.update(
        {
            "status": "revision_queue_rejected",
            "blocking_reasons": ["revision_queue_rejected_by_human_reviewer"],
            "promotion": {"allowed": False, "required_decision": "rebuild_cgss_revision_task_queue"},
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


def make_approved_queue(queue: dict[str, Any], reviewer: str, note: str) -> dict[str, Any]:
    approved_queue = deepcopy(queue)
    approved_queue["status"] = "approved_for_agent_work_orders"
    approved_queue["human_approval"] = {
        "status": "approved",
        "decision": APPROVAL_DECISION,
        "approved_by": reviewer,
        "note": note,
        "approved_at": datetime.now(timezone.utc).isoformat(),
    }
    approved_queue["promotion"] = dict(approved_queue.get("promotion", {}))
    approved_queue["promotion"]["allowed"] = True
    approved_queue["promotion"]["required_decision"] = "human_review_agent_work_order_outputs"
    approved_queue["formal_writeback_allowed"] = False
    approved_queue["draft_layer_only"] = True
    return approved_queue


def write_revision_queue_approval_outputs(
    project_root: Path,
    record: dict[str, Any],
    result_path: Path,
    review_path: Path,
    approved_queue_path: Path,
) -> tuple[Path, Path, Path | None]:
    absolute_result = project_root / result_path
    absolute_result.parent.mkdir(parents=True, exist_ok=True)
    absolute_result.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    absolute_review = project_root / review_path
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.write_text(render_review(record), encoding="utf-8")

    if not record.get("approved_queue"):
        return absolute_result, absolute_review, None

    absolute_approved_queue = project_root / approved_queue_path
    absolute_approved_queue.parent.mkdir(parents=True, exist_ok=True)
    absolute_approved_queue.write_text(
        json.dumps(record["approved_queue"], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return absolute_result, absolute_review, absolute_approved_queue


def render_review(record: dict[str, Any]) -> str:
    lines = [
        "# CGSS 修订任务队列人工决策记录",
        "",
        f"- 题目：{record.get('topic', '')}",
        f"- schema：`{record['schema_version']}`",
        f"- 状态：`{record['status']}`",
        f"- 决策：`{record['decision']}`",
        f"- 审阅人：{record.get('reviewer') or '未记录'}",
        "- 草案层：是",
        "- 写入正式论文：否",
        "- 写入 state/product：否",
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
                "- `Program/cgss_revision_work_orders.py --queue Results/json/cgss_social_capital_happiness_revision_task_queue_approved.json`",
            ]
        )
    lines.extend(["", "## 决策 JSON", "```json", json.dumps(record, ensure_ascii=False, indent=2), "```"])
    return "\n".join(lines) + "\n"
