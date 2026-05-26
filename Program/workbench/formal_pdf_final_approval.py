from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.export import relative_or_absolute
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


VALID_ACTIONS = {
    "approve": "approved",
    "needs_revision": "needs_revision",
    "reject": "rejected",
}

APPROVAL_KEY = "formal_pdf_candidate"
DEFAULT_FINAL_PREFLIGHT = "Results/json/formal_pdf_final_writeback_preflight.json"
DEFAULT_APPROVAL_PATH = "state/product/writeback_approvals.json"
DEFAULT_APPROVAL_REPORT = "Results/json/formal_pdf_final_approval.json"
DEFAULT_APPROVAL_REVIEW = "Reviews/formal_pdf_final_approval.md"


def build_formal_pdf_final_approval(
    project_root: Path,
    final_preflight: dict[str, Any],
    final_preflight_path: Path,
    *,
    action: str,
    note: str,
    actor: str,
    approval_path: Path,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], int]:
    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid final PDF approval action: {action}")

    before = formal_state_before or snapshot_formal_state(project_root)
    candidate_pdf_path = resolve_project_path(project_root, str(final_preflight.get("candidate_pdf") or ""))
    candidate_qmd_path = resolve_project_path(project_root, str(final_preflight.get("candidate_qmd") or ""))
    blocking_reasons = build_blocking_reasons(
        final_preflight,
        candidate_pdf_path=candidate_pdf_path,
        candidate_qmd_path=candidate_qmd_path,
    )
    if blocking_reasons:
        after = snapshot_formal_state(project_root)
        return {
            "schema_version": "p5.formal_pdf_final_approval.v1",
            "generated_at": utc_now(),
            "source_final_preflight": relative_or_absolute(final_preflight_path, project_root),
            "approval_path": relative_or_absolute(approval_path, project_root),
            "status": "blocked_by_final_preflight",
            "action": action,
            "actor": actor,
            "note": note,
            "candidate_pdf": relative_or_absolute(candidate_pdf_path, project_root) if candidate_pdf_path else None,
            "candidate_qmd": relative_or_absolute(candidate_qmd_path, project_root) if candidate_qmd_path else None,
            "blocking_reasons": blocking_reasons,
            "can_enter_p6": False,
            "final_writeback_authorized": False,
            "this_command_wrote_formal_state": False,
            "this_command_wrote_final_outputs": False,
            "formal_state_guard": diff_formal_state(before, after),
            "next_action": {
                "id": "rerun_pdf_candidate_review",
                "label": "重新审阅 PDF 候选稿",
                "description": "最终写回预检未 ready，先修复候选 PDF 或重新生成 P5-E4 预检。",
            },
        }, 2

    status = VALID_ACTIONS[action]
    can_enter_p6 = status == "approved"
    entry = build_approval_entry(
        project_root,
        final_preflight,
        final_preflight_path,
        approval_path,
        action=action,
        status=status,
        note=note,
        actor=actor,
        can_enter_p6=can_enter_p6,
    )
    state = load_writeback_approval_state(approval_path)
    state.setdefault("final_pdf_approvals", {})
    state["final_pdf_approvals"][APPROVAL_KEY] = entry
    approval_path.parent.mkdir(parents=True, exist_ok=True)
    approval_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    after = snapshot_formal_state(project_root)
    return {
        "schema_version": "p5.formal_pdf_final_approval.v1",
        "generated_at": utc_now(),
        "source_final_preflight": relative_or_absolute(final_preflight_path, project_root),
        "approval_path": relative_or_absolute(approval_path, project_root),
        "status": "approved_for_final_writeback" if can_enter_p6 else status,
        "action": action,
        "actor": actor,
        "note": note,
        "candidate_pdf": final_preflight.get("candidate_pdf"),
        "candidate_qmd": final_preflight.get("candidate_qmd"),
        "blocking_reasons": [],
        "can_enter_p6": can_enter_p6,
        "final_writeback_authorized": can_enter_p6,
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
        "approval_entry": entry,
        "formal_state_guard": diff_formal_state(before, after),
        "next_action": build_next_action(status),
    }, 0


def build_blocking_reasons(
    final_preflight: dict[str, Any],
    *,
    candidate_pdf_path: Path | None,
    candidate_qmd_path: Path | None,
) -> list[str]:
    reasons: list[str] = []
    if final_preflight.get("status") != "ready_for_human_final_approval":
        reasons.extend(final_preflight.get("blocking_reasons") or ["final_preflight_not_ready"])
    if final_preflight.get("can_request_final_approval") is not True:
        reasons.append("final_approval_not_requested_by_preflight")
    if final_preflight.get("requires_human_approval") is not True:
        reasons.append("human_approval_not_required_by_preflight")
    if final_preflight.get("final_writeback_allowed") is True:
        reasons.append("preflight_already_allows_final_writeback")
    if final_preflight.get("formal_state_guard", {}).get("changed"):
        reasons.append("formal_state_changed_before_final_approval")
    if candidate_pdf_path is None or not candidate_pdf_path.exists():
        reasons.append("candidate_pdf_missing")
    if candidate_qmd_path is None or not candidate_qmd_path.exists():
        reasons.append("candidate_qmd_missing")
    return reasons


def build_approval_entry(
    project_root: Path,
    final_preflight: dict[str, Any],
    final_preflight_path: Path,
    approval_path: Path,
    *,
    action: str,
    status: str,
    note: str,
    actor: str,
    can_enter_p6: bool,
) -> dict[str, Any]:
    return {
        "id": f"final_pdf_approval_{APPROVAL_KEY}",
        "preflight_id": "formal_pdf_final_writeback_preflight",
        "status": status,
        "action": action,
        "actor": actor,
        "note": note,
        "timestamp": utc_now(),
        "evidence_level": "local_file",
        "path": relative_or_absolute(approval_path, project_root),
        "source_final_preflight": relative_or_absolute(final_preflight_path, project_root),
        "source_review": final_preflight.get("source_review"),
        "candidate_pdf": final_preflight.get("candidate_pdf"),
        "candidate_qmd": final_preflight.get("candidate_qmd"),
        "approval_contract": final_preflight.get("approval_contract") or {},
        "can_enter_p6": can_enter_p6,
        "final_writeback_authorized": can_enter_p6,
        "this_command_wrote_formal_state": False,
        "this_command_wrote_final_outputs": False,
    }


def load_writeback_approval_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "schema_version": "product.writeback_approvals.v1",
            "approvals": {},
            "formal_preflight_approvals": {},
            "final_pdf_approvals": {},
        }
    state = json.loads(path.read_text(encoding="utf-8"))
    state.setdefault("schema_version", "product.writeback_approvals.v1")
    state.setdefault("approvals", {})
    state.setdefault("formal_preflight_approvals", {})
    state.setdefault("final_pdf_approvals", {})
    return state


def build_next_action(status: str) -> dict[str, str]:
    if status == "approved":
        return {
            "id": "write_final_pdf_and_docx",
            "label": "写入最终 PDF/docx",
            "description": "人工批准已落地，下一节点 P6-A 可以把候选 PDF/docx 写入最终产物层。",
        }
    if status == "needs_revision":
        return {
            "id": "revise_pdf_candidate",
            "label": "修订 PDF 候选稿",
            "description": "按人工意见修订候选 PDF 后，再重新进入最终批准。",
        }
    return {
        "id": "stop_final_writeback",
        "label": "停止最终写回",
        "description": "本轮不写最终 PDF/docx，保留审批账本和原因。",
    }


def write_formal_pdf_final_approval_outputs(
    report_path: Path,
    review_path: Path,
    report: dict[str, Any],
) -> tuple[Path, Path]:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.write_text(render_review_markdown(report), encoding="utf-8")
    return report_path, review_path


def render_review_markdown(report: dict[str, Any]) -> str:
    blockers = report.get("blocking_reasons") or []
    blocker_lines = "\n".join(f"- `{item}`" for item in blockers) if blockers else "- 无"
    return f"""# P5-E5 最终写回人工批准

## 当前状态

- 状态：`{report.get("status")}`
- 动作：`{report.get("action")}`
- 候选 PDF：`{report.get("candidate_pdf")}`
- 候选 QMD：`{report.get("candidate_qmd")}`
- 可进入 P6：`{str(report.get("can_enter_p6")).lower()}`
- 最终写回授权：`{str(report.get("final_writeback_authorized")).lower()}`
- 本命令写正式状态：`{str(report.get("this_command_wrote_formal_state")).lower()}`
- 本命令写最终产物：`{str(report.get("this_command_wrote_final_outputs")).lower()}`

## 阻断原因

{blocker_lines}

## 人工意见

{report.get("note") or "无"}

## 下一步

- `{report.get("next_action", {}).get("id")}`：{report.get("next_action", {}).get("description")}
"""


def resolve_project_path(project_root: Path, value: str) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
