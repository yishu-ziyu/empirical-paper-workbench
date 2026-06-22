from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p1c.parent_education_wage_method_execution_ledger.v1"
TOPIC = "父母受教育水平对子女工资收入的影响"
TOPIC_SLUG = "parent-education-wage"
DEFAULT_DATA_FIELD_LEDGER_PATH = Path("Results/json/parent_education_wage_data_field_binding_ledger.json")
DEFAULT_DESIGN_PATH = Path("Tasks/parent-education-wage/design.json")
DEFAULT_LEDGER_PATH = Path("Results/json/parent_education_wage_method_execution_ledger.json")
DEFAULT_REVIEW_PATH = Path("Reviews/parent_education_wage_method_execution_ledger.md")


def build_parent_education_wage_method_execution_ledger(project_root: Path) -> dict[str, Any]:
    data_field_ledger = load_json(project_root / DEFAULT_DATA_FIELD_LEDGER_PATH)
    design = load_json(project_root / DEFAULT_DESIGN_PATH)
    missing_required_fields = sorted(
        {
            str(item.get("dataset_column"))
            for item in data_field_ledger.get("missing_fields", [])
            if item.get("dataset_column")
        }
    )
    design_contaminated = design_has_topic_contamination(design)
    blocking_reasons = []
    if missing_required_fields:
        blocking_reasons.append("missing_required_fields")
    if design_contaminated:
        blocking_reasons.append("design_code_stub_topic_contamination")
    execution_allowed = not blocking_reasons
    status = "ready_for_method_execution_review" if execution_allowed else "blocked_missing_required_fields"
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": TOPIC,
        "topic_slug": TOPIC_SLUG,
        "status": status,
        "execution_allowed": execution_allowed,
        "run_id": None,
        "blocking_reasons": blocking_reasons,
        "missing_required_fields": missing_required_fields,
        "source_artifacts": {
            "data_field_binding_ledger": {
                "path": DEFAULT_DATA_FIELD_LEDGER_PATH.as_posix(),
                "status": data_field_ledger.get("status", ""),
            },
            "design": {
                "path": DEFAULT_DESIGN_PATH.as_posix(),
                "recommended": design.get("recommended", ""),
            },
        },
        "method_candidates": build_method_candidates(design, missing_required_fields, design_contaminated),
        "statspai_boundary": {
            "allowed_after": "analysis_ready_dataframe",
            "allowed_steps": [
                "EDA and descriptive statistics",
                "pre-flight diagnostics",
                "estimand-first identification",
                "estimation only after required fields are bound",
                "diagnostics and robustness",
            ],
            "forbidden_calls": ["sp.paper"],
        },
        "boundary_flags": {
            "executed_regression": False,
            "created_run_id": False,
            "called_statspai_paper": False,
            "modified_formal_run_plan": False,
            "modified_formal_variable_roles": False,
            "modified_formal_manuscript": False,
        },
        "product_control_signal": {
            "phase": "P1-C",
            "label": "方法执行",
            "status": status,
            "next_action": "repair_data_field_binding_before_execution" if not execution_allowed else "human_review_method_execution_plan",
        },
        "outputs": {
            "json": DEFAULT_LEDGER_PATH.as_posix(),
            "review": DEFAULT_REVIEW_PATH.as_posix(),
        },
    }


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def design_has_topic_contamination(design: dict[str, Any]) -> bool:
    code_stub = str(design.get("code_stub", "")).lower()
    return any(term in code_stub for term in ["robot_exposure", "ln_robot", "bartik_iv", "robot_density"])


def build_method_candidates(
    design: dict[str, Any],
    missing_required_fields: list[str],
    design_contaminated: bool,
) -> list[dict[str, Any]]:
    candidates = design.get("candidates") if isinstance(design.get("candidates"), list) else []
    if not candidates:
        candidates = [{"method": design.get("recommended") or "method_to_be_reviewed"}]
    methods = []
    for item in candidates:
        method = str(item.get("method", "method_to_be_reviewed"))
        reasons = []
        if missing_required_fields:
            reasons.append("missing_required_fields")
        if design_contaminated:
            reasons.append("design_code_stub_topic_contamination")
        methods.append(
            {
                "method": method,
                "status": "blocked" if reasons else "ready_for_review",
                "blocking_reasons": reasons,
                "missing_required_fields": missing_required_fields,
                "can_execute": not reasons,
            }
        )
    return methods


def write_parent_education_wage_method_execution_ledger(
    project_root: Path,
    ledger: dict[str, Any],
    ledger_path: Path = DEFAULT_LEDGER_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
) -> tuple[Path, Path]:
    absolute_ledger_path = project_root / ledger_path
    absolute_review_path = project_root / review_path
    absolute_ledger_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_review_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review_path.write_text(render_review(ledger), encoding="utf-8")
    return absolute_ledger_path, absolute_review_path


def render_review(ledger: dict[str, Any]) -> str:
    lines = [
        "# P1-C 方法执行账本",
        "",
        f"- 题目：{ledger['topic']}",
        f"- 状态：`{ledger['status']}`",
        f"- execution_allowed：{str(ledger['execution_allowed']).lower()}",
        "- run id：未创建" if not ledger["run_id"] else f"- run id：`{ledger['run_id']}`",
        "- 正式 RunPlan 写回：否",
        "- 正式论文写回：否",
        "",
        "## 阻塞原因",
    ]
    if ledger["blocking_reasons"]:
        for reason in ledger["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    else:
        lines.append("- 无硬阻塞，等待人工审阅。")
    lines.extend(["", "## 缺失字段"])
    for field in ledger["missing_required_fields"]:
        lines.append(f"- `{field}`")
    lines.extend(["", "## 方法候选"])
    for method in ledger["method_candidates"]:
        lines.append(
            f"- `{method['method']}` | {method['status']} | reasons={', '.join(method['blocking_reasons']) or 'none'}"
        )
    lines.extend(["", "## StatsPAI 边界"])
    lines.append(f"- allowed_after: `{ledger['statspai_boundary']['allowed_after']}`")
    lines.append("- forbidden: `sp.paper`")
    lines.append("")
    return "\n".join(lines)
