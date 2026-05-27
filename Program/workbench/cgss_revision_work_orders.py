from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_revision_work_orders.v1"
DEFAULT_QUEUE_PATH = Path("Results/json/cgss_social_capital_happiness_revision_task_queue.json")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_revision_work_orders.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_revision_work_orders.md")
APPROVAL_DECISION = "human_approve_cgss_revision_task_queue"


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_cgss_revision_work_orders(queue: dict[str, Any]) -> dict[str, Any]:
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": queue.get("topic", ""),
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "can_write_product_state": False,
        "source_queue": {
            "schema_version": queue.get("schema_version", ""),
            "status": queue.get("status", ""),
            "required_decision": queue.get("promotion", {}).get("required_decision", ""),
        },
    }

    if not is_queue_approved(queue):
        manifest.update(
            {
                "status": "blocked_revision_queue_not_approved",
                "blocking_reasons": [APPROVAL_DECISION],
                "work_orders": [],
                "written_work_orders": [],
                "promotion": {
                    "allowed": False,
                    "required_decision": APPROVAL_DECISION,
                },
            }
        )
        return manifest

    work_orders = [adapt_task_to_work_order(queue, task) for task in queue.get("agent_task_queue", [])]
    manifest.update(
        {
            "status": "ready_for_agent_draft_execution",
            "blocking_reasons": [],
            "work_orders": work_orders,
            "written_work_orders": [],
            "promotion": {
                "allowed": False,
                "required_decision": "human_review_agent_work_order_outputs",
            },
        }
    )
    return manifest


def is_queue_approved(queue: dict[str, Any]) -> bool:
    approval = queue.get("human_approval", {})
    return (
        queue.get("status") == "approved_for_agent_work_orders"
        and approval.get("status") == "approved"
        and approval.get("decision") == APPROVAL_DECISION
        and queue.get("promotion", {}).get("allowed") is True
    )


def adapt_task_to_work_order(queue: dict[str, Any], task: dict[str, Any]) -> dict[str, Any]:
    agent = task.get("agent", "")
    return {
        "id": task.get("task_id", ""),
        "task_id": task.get("task_id", ""),
        "agent": agent,
        "title": task.get("title", ""),
        "action_item": task.get("objective", ""),
        "reason": task.get("objective", ""),
        "inputs": task.get("evidence_inputs", []),
        "draft_output_path": task.get("output_target", ""),
        "status": "ready_for_agent_draft_execution",
        "requires_human_confirmation": True,
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "can_write_product_state": False,
        "acceptance_checks": [
            "draft_output_written",
            "evidence_inputs_referenced",
            "formal_layer_not_modified",
            "human_review_required_before_promotion",
        ],
        "write_boundary": agent_write_boundary(queue, agent),
        "source_artifacts": queue.get("source_artifacts", {}),
    }


def agent_write_boundary(queue: dict[str, Any], agent: str) -> dict[str, Any]:
    packets = queue.get("agent_packets", [])
    for packet in packets:
        if packet.get("agent") == agent:
            boundary = packet.get("write_boundary", {})
            must_not_write = list(boundary.get("must_not_write", []))
            if "state/product" not in must_not_write:
                must_not_write.append("state/product")
            return {
                "draft_layer_only": True,
                "formal_writeback_allowed": False,
                "must_not_write": must_not_write,
            }
    return {
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "must_not_write": ["DesignSpec", "RunPlan", "state/product", "formal manuscript"],
    }


def write_revision_work_order_outputs(
    project_root: Path,
    manifest: dict[str, Any],
    result_path: Path,
    review_path: Path,
) -> tuple[Path, Path, list[Path]]:
    written_files: list[Path] = []
    if manifest.get("status") == "ready_for_agent_draft_execution":
        for work_order in manifest.get("work_orders", []):
            output_path = project_root / work_order["draft_output_path"]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(render_work_order(work_order), encoding="utf-8")
            written_files.append(output_path)

    manifest = dict(manifest)
    manifest["written_work_orders"] = [
        str(path.relative_to(project_root)) for path in written_files
    ]

    absolute_result = project_root / result_path
    absolute_result.parent.mkdir(parents=True, exist_ok=True)
    absolute_result.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    absolute_review = project_root / review_path
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.write_text(render_review(manifest), encoding="utf-8")
    return absolute_result, absolute_review, written_files


def render_work_order(work_order: dict[str, Any]) -> str:
    lines = [
        "# CGSS Agent 草案工单",
        "",
        f"- 任务：`{work_order['id']}`",
        f"- Agent：`{work_order['agent']}`",
        f"- 标题：{work_order['title']}",
        f"- 输出：`{work_order['draft_output_path']}`",
        "- draft_layer_only: true",
        "- formal_writeback_allowed: false",
        "- can_write_product_state: false",
        "- requires_human_confirmation: true",
        "",
        "## 任务目标",
        work_order["action_item"],
        "",
        "## 输入证据",
    ]
    for item in work_order.get("inputs", []):
        lines.append(f"- `{item}`")
    lines.extend(["", "## 验收条件"])
    for item in work_order.get("acceptance_checks", []):
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "## 写入边界",
            "```json",
            json.dumps(work_order["write_boundary"], ensure_ascii=False, indent=2),
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def render_review(manifest: dict[str, Any]) -> str:
    lines = [
        "# CGSS Agent 草案工单门禁",
        "",
        f"- 题目：{manifest.get('topic', '')}",
        f"- schema：`{manifest['schema_version']}`",
        f"- 状态：`{manifest['status']}`",
        "- 草案层：是",
        "- 写入正式论文：否",
        "- 写入 state/product：否",
    ]
    if manifest.get("blocking_reasons"):
        lines.extend(["", "## 当前阻断"])
        for reason in manifest["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    if manifest.get("work_orders"):
        lines.extend(["", "## 将生成的草案工单"])
        for order in manifest["work_orders"]:
            lines.append(f"- `{order['id']}` -> `{order['draft_output_path']}`")
    if manifest.get("written_work_orders"):
        lines.extend(["", "## 已写入工单文件"])
        for path in manifest["written_work_orders"]:
            lines.append(f"- `{path}`")
    lines.extend(["", "## 工单 Manifest", "```json", json.dumps(manifest, ensure_ascii=False, indent=2), "```"])
    return "\n".join(lines) + "\n"
