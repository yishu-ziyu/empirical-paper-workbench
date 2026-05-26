from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.paper_package import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


VALID_ACTIONS = {
    "approve": "approved",
    "needs_revision": "needs_revision",
    "reject": "rejected",
}

APPROVAL_KEY = "formal_writeback_preflight"
DEFAULT_APPROVAL_PATH = "state/product/writeback_approvals.json"


def build_formal_writeback_approval(
    project_root: Path,
    preflight: dict[str, Any],
    preflight_path: Path,
    *,
    action: str,
    note: str,
    actor: str = "user",
    approval_path: Path | None = None,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid formal writeback approval action: {action}")

    before = formal_state_before or snapshot_formal_state(project_root)
    approval_state_path = approval_path or project_root / DEFAULT_APPROVAL_PATH
    blocking_reasons = build_blocking_reasons(preflight)
    if blocking_reasons:
        after = snapshot_formal_state(project_root)
        return {
            "schema_version": "p5.formal_writeback_approval.v1",
            "generated_at": utc_now(),
            "source_preflight": relative_or_absolute(preflight_path, project_root),
            "approval_path": relative_or_absolute(approval_state_path, project_root),
            "status": "blocked_by_preflight",
            "action": action,
            "actor": actor,
            "note": note,
            "blocking_reasons": blocking_reasons,
            "can_enter_p5": False,
            "can_write_formal_package": False,
            "this_command_wrote_formal_state": False,
            "writeback_scope_categories": scope_categories(preflight),
            "formal_state_guard": diff_formal_state(before, after),
            "next_action": {
                "id": "rerun_formal_writeback_preflight",
                "label": "重新生成正式写回预检",
                "description": "预检账本还没有 ready，先回到 P4-J 或前置质量门补齐证据。",
            },
        }

    status = VALID_ACTIONS[action]
    can_enter_p5 = status == "approved"
    entry = build_approval_entry(
        project_root,
        preflight,
        preflight_path,
        approval_state_path,
        action=action,
        status=status,
        note=note,
        actor=actor,
        can_enter_p5=can_enter_p5,
    )
    state = load_writeback_approval_state(approval_state_path)
    state.setdefault("approvals", {})
    state.setdefault("formal_preflight_approvals", {})
    state["formal_preflight_approvals"][APPROVAL_KEY] = entry
    approval_state_path.parent.mkdir(parents=True, exist_ok=True)
    approval_state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    after = snapshot_formal_state(project_root)
    return {
        "schema_version": "p5.formal_writeback_approval.v1",
        "generated_at": utc_now(),
        "source_preflight": relative_or_absolute(preflight_path, project_root),
        "approval_path": relative_or_absolute(approval_state_path, project_root),
        "status": "approved_for_p5" if can_enter_p5 else status,
        "action": action,
        "actor": actor,
        "note": note,
        "blocking_reasons": [],
        "can_enter_p5": can_enter_p5,
        "can_write_formal_package": can_enter_p5,
        "this_command_wrote_formal_state": False,
        "writeback_scope_categories": scope_categories(preflight),
        "approval_entry": entry,
        "formal_state_guard": diff_formal_state(before, after),
        "next_action": build_next_action(status),
    }


def build_blocking_reasons(preflight: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if preflight.get("status") != "ready_for_human_approval":
        reasons.extend(preflight.get("blocking_reasons") or ["preflight_not_ready"])
    if not preflight.get("requires_human_approval"):
        reasons.append("human_approval_not_required_by_preflight")
    if preflight.get("formal_writeback_allowed"):
        reasons.append("preflight_already_allows_formal_writeback")
    if not preflight.get("writeback_scope"):
        reasons.append("writeback_scope_missing")
    if preflight.get("formal_state_guard", {}).get("changed"):
        reasons.append("formal_state_changed_before_approval")
    return reasons


def build_approval_entry(
    project_root: Path,
    preflight: dict[str, Any],
    preflight_path: Path,
    approval_state_path: Path,
    *,
    action: str,
    status: str,
    note: str,
    actor: str,
    can_enter_p5: bool,
) -> dict[str, Any]:
    return {
        "id": f"formal_writeback_approval_{APPROVAL_KEY}",
        "preflight_id": APPROVAL_KEY,
        "status": status,
        "action": action,
        "actor": actor,
        "note": note,
        "timestamp": utc_now(),
        "evidence_level": "local_file",
        "path": relative_or_absolute(approval_state_path, project_root),
        "source_preflight": relative_or_absolute(preflight_path, project_root),
        "source_preview": preflight.get("preview_path"),
        "writeback_scope_categories": scope_categories(preflight),
        "can_enter_p5": can_enter_p5,
        "can_write_formal_package": can_enter_p5,
        "this_command_wrote_formal_state": False,
    }


def scope_categories(preflight: dict[str, Any]) -> list[str]:
    return [
        item.get("category")
        for item in preflight.get("writeback_scope", [])
        if item.get("category")
    ]


def build_next_action(status: str) -> dict[str, str]:
    if status == "approved":
        return {
            "id": "build_p5_formal_paper_package",
            "label": "生成 P5 正式 paper package",
            "description": "批准账本已落地，下一节点可以生成正式包 manifest、PDF/docx 预检和复现交付材料。",
        }
    if status == "needs_revision":
        return {
            "id": "revise_formal_writeback_preflight",
            "label": "修订正式写回预检",
            "description": "按人工意见补齐证据或范围后，再重新进入 P5-A 批准。",
        }
    return {
        "id": "stop_formal_package_entry",
        "label": "停止进入正式包",
        "description": "本轮不进入 P5，保留审批账本和原因。",
    }


def load_writeback_approval_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "schema_version": "product.writeback_approvals.v1",
            "approvals": {},
            "formal_preflight_approvals": {},
        }
    state = json.loads(path.read_text(encoding="utf-8"))
    state.setdefault("schema_version", "product.writeback_approvals.v1")
    state.setdefault("approvals", {})
    state.setdefault("formal_preflight_approvals", {})
    return state


def write_formal_writeback_approval_outputs(
    report_path: Path,
    review_path: Path,
    report: dict[str, Any],
) -> tuple[Path, Path]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.write_text(build_review_markdown(report), encoding="utf-8")
    return report_path, review_path


def build_review_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# P5-A 正式包入口批准",
        "",
        f"- Source preflight: `{report.get('source_preflight')}`",
        f"- Status: `{report.get('status')}`",
        f"- Action: `{report.get('action')}`",
        f"- Can enter P5: `{str(report.get('can_enter_p5')).lower()}`",
        f"- Approval path: `{report.get('approval_path')}`",
        "- 本命令写正式层：否",
        "",
        "## 写回范围",
        "",
    ]
    categories = report.get("writeback_scope_categories") or []
    if categories:
        lines.extend(f"- `{category}`" for category in categories)
    else:
        lines.append("- 无")
    lines.extend(
        [
            "",
            "## 人工意见",
            "",
            report.get("note") or "无",
            "",
            "## 下一步",
            "",
            f"- `{report.get('next_action', {}).get('id')}`：{report.get('next_action', {}).get('description')}",
        ]
    )
    return "\n".join(lines) + "\n"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
