from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Program.workbench.cgss_revision_work_orders import (
    DEFAULT_RESULT_PATH as DEFAULT_WORK_ORDER_RESULT_PATH,
    DEFAULT_REVIEW_PATH as DEFAULT_WORK_ORDER_REVIEW_PATH,
    build_cgss_revision_work_orders,
    write_revision_work_order_outputs,
)


SCHEMA_VERSION = "p6.cgss_revision_approval_router.v1"
DEFAULT_APPROVAL_PATH = Path("Results/json/cgss_social_capital_happiness_revision_queue_approval.json")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_revision_approval_router.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_revision_approval_router.md")


def load_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_cgss_revision_approval_route(approval_record: dict[str, Any]) -> dict[str, Any]:
    decision = str(approval_record.get("decision", "defer")).strip().lower()
    approved_queue = approval_record.get("approved_queue") or {}
    route = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": approval_record.get("topic", ""),
        "source_approval": {
            "schema_version": approval_record.get("schema_version", ""),
            "status": approval_record.get("status", ""),
            "decision": decision,
            "approved": approval_record.get("approved") is True,
        },
        "decision": decision,
        "approved": approval_record.get("approved") is True,
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "can_write_product_state": False,
        "agent_work_orders_generated": False,
        "work_order_manifest": {},
        "next_actions": [],
    }

    if decision == "approve":
        if approved_queue:
            manifest = build_cgss_revision_work_orders(approved_queue)
            route.update(
                {
                    "status": "approved_queue_routed_to_agent_work_orders",
                    "route": "agent_draft_work_orders",
                    "agent_work_orders_generated": manifest.get("status") == "ready_for_agent_draft_execution",
                    "work_order_manifest": manifest,
                    "next_actions": ["write_draft_layer_agent_work_orders", "human_review_agent_work_order_outputs"],
                }
            )
            return route
        route.update(
            {
                "status": "approved_queue_missing",
                "route": "wait_for_valid_approved_queue",
                "next_actions": ["record_approved_queue_before_agent_work_orders"],
            }
        )
        return route

    if decision == "revise":
        route.update(
            {
                "status": "revision_queue_update_required",
                "route": "revision_queue_update",
                "next_actions": ["revise_cgss_revision_task_queue"],
            }
        )
        return route

    if decision == "reject":
        route.update(
            {
                "status": "revision_queue_rebuild_or_stop_required",
                "route": "rebuild_or_stop",
                "next_actions": ["rebuild_or_stop_cgss_revision_task_queue"],
            }
        )
        return route

    route.update(
        {
            "status": "waiting_for_human_revision_queue_decision",
            "route": "wait_for_human_confirmation",
            "next_actions": ["human_approve_revise_reject_or_defer_cgss_revision_task_queue"],
        }
    )
    return route


def write_cgss_revision_approval_route_outputs(
    project_root: Path,
    route: dict[str, Any],
    review_path: Path = DEFAULT_REVIEW_PATH,
    result_path: Path = DEFAULT_RESULT_PATH,
    work_order_result_path: Path = DEFAULT_WORK_ORDER_RESULT_PATH,
    work_order_review_path: Path = DEFAULT_WORK_ORDER_REVIEW_PATH,
) -> tuple[Path, list[Path]]:
    route = dict(route)
    written_work_orders: list[Path] = []
    manifest = route.get("work_order_manifest") or {}
    if route.get("route") == "agent_draft_work_orders" and manifest:
        _, _, written_work_orders = write_revision_work_order_outputs(
            project_root,
            manifest,
            work_order_result_path,
            work_order_review_path,
        )
        route["written_work_orders"] = [str(path.relative_to(project_root)) for path in written_work_orders]
    else:
        route["written_work_orders"] = []

    absolute_result = project_root / result_path
    absolute_result.parent.mkdir(parents=True, exist_ok=True)
    absolute_result.write_text(json.dumps(route, ensure_ascii=False, indent=2), encoding="utf-8")

    absolute_review = project_root / review_path
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.write_text(render_review(route), encoding="utf-8")
    return absolute_review, written_work_orders


def render_review(route: dict[str, Any]) -> str:
    lines = [
        "# CGSS 修订审批路由记录",
        "",
        f"- 题目：{route.get('topic', '')}",
        f"- schema：`{route['schema_version']}`",
        f"- 审批状态：`{route.get('source_approval', {}).get('status', '')}`",
        f"- 人工决策：`{route['decision']}`",
        f"- 路由状态：`{route['status']}`",
        f"- 下一路由：`{route['route']}`",
        "- 草案层：是",
        "- 写入正式论文：否",
        "- 写入 state/product：否",
        f"- 生成 Agent 工单：{str(route.get('agent_work_orders_generated') is True).lower()}",
    ]
    if route.get("next_actions"):
        lines.extend(["", "## 下一步"])
        for action in route["next_actions"]:
            lines.append(f"- `{action}`")
    if route.get("written_work_orders"):
        lines.extend(["", "## 已写入草案工单"])
        for path in route["written_work_orders"]:
            lines.append(f"- `{path}`")
    lines.extend(["", "## 路由 JSON", "```json", json.dumps(route, ensure_ascii=False, indent=2), "```"])
    return "\n".join(lines) + "\n"
