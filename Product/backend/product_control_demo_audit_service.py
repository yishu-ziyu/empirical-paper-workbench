from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from Product.backend.project_service import utc_now
from Product.backend.registry import get_project_by_id


EXPECTED_DEMO_TOPIC = "父母受教育水平对子女工资收入的影响"
EXPECTED_DEMO_SLUG = "parent-education-wage"
TOPIC_BINDING_PATH = Path("state/product/topic_binding.json")
AUDIT_JSON_PATH = Path("Results/json/product_control_demo_topic_binding_audit.json")
AUDIT_REVIEW_PATH = Path("Reviews/product_control_demo_topic_binding_audit.md")

STALE_TOPIC_PATTERNS = [
    ("industrial_robot_cn", "工业机器人"),
    ("industrial_robot_en", "industrial robot"),
    ("robot_density", "robot_density"),
    ("ln_robot", "ln_robot"),
    ("year_robot", "year_robot"),
    ("cgss", "cgss"),
    ("charls", "charls"),
    ("medical_insurance_cn", "城乡居民医保"),
    ("happiness_cn", "幸福感"),
    ("social_capital_cn", "社会资本"),
    ("trained_on_wage", "effect of trained on wage"),
    ("trained_wage", "trained on wage"),
    ("training_wage_arrow", "training → wage"),
]

def get_project_product_control_demo_topic_binding_audit(
    product_root: Path,
    repo_root: Path,
    project_id: str,
    persist: bool = True,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    report = run_product_control_demo_topic_binding_audit(project_root, persist=persist)
    report["project"] = {
        "id": project["id"],
        "slug": project["slug"],
        "title": project["title"],
    }
    return report


def run_product_control_demo_topic_binding_audit(project_root: Path, persist: bool = True) -> dict[str, Any]:
    project_root = project_root.resolve()
    topic_binding = load_topic_binding(project_root)
    surfaces_to_audit = current_surfaces(topic_binding["expected_slug"])
    surfaces = [audit_surface(project_root, surface, topic_binding) for surface in surfaces_to_audit]
    critical_issues = [issue for surface in surfaces for issue in surface["issues"] if issue["severity"] == "critical"]
    can_proceed = not critical_issues
    report: dict[str, Any] = {
        "_meta": {
            "evidence_level": "local_file",
            "service": "product_control_demo_audit_service",
            "generated_at": utc_now(),
        },
        "schema_version": "p0a.product_control_demo_topic_binding_audit.v1",
        "status": "ready_for_p0b" if can_proceed else "blocked_by_topic_contamination",
        "topic_binding": topic_binding,
        "expected_topic": topic_binding["expected_topic"],
        "expected_slug": topic_binding["expected_slug"],
        "can_proceed_to_p0b": can_proceed,
        "critical_issue_count": len(critical_issues),
        "critical_issues": critical_issues,
        "surfaces": surfaces,
        "audit_scope": {
            "mode": "current_product_surfaces_only",
            "included_paths": [surface["path"].as_posix() for surface in surfaces_to_audit],
            "excluded_note": "Historical docs and archived proof cases are allowed unless they are referenced by current product surfaces.",
        },
        "artifact_paths": {
            "json": AUDIT_JSON_PATH.as_posix(),
            "review": AUDIT_REVIEW_PATH.as_posix(),
        },
        "next_action": (
            "进入 P0-B：生成当前题目的 Agent Task Queue。"
            if can_proceed
            else "先人工处理 critical issues，再进入 P0-B。"
        ),
    }
    if persist:
        write_product_control_demo_topic_binding_audit_outputs(project_root, report)
    return report


def load_topic_binding(project_root: Path) -> dict[str, Any]:
    path = project_root / TOPIC_BINDING_PATH
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
        expected_topic = str(payload.get("expected_topic") or payload.get("topic") or "").strip()
        expected_slug = str(payload.get("expected_slug") or payload.get("topic_slug") or "").strip()
        if expected_topic and expected_slug:
            return {
                "expected_topic": expected_topic,
                "expected_slug": expected_slug,
                "source": TOPIC_BINDING_PATH.as_posix(),
                "binding_type": str(payload.get("binding_type") or "project_topic_binding"),
            }
    return {
        "expected_topic": EXPECTED_DEMO_TOPIC,
        "expected_slug": EXPECTED_DEMO_SLUG,
        "source": "Tasks/product-control-demo-line.md",
        "binding_type": "demo_line_fallback",
    }


def current_surfaces(expected_slug: str) -> list[dict[str, Any]]:
    return [
        {
            "id": "research_question",
            "path": Path("state/product/research_question.json"),
            "required": True,
            "issue_id": "research_question_mismatch",
            "missing_issue_id": "research_question_missing",
            "requires_expected_topic": True,
        },
        {
            "id": "supervisor_plan",
            "path": Path("state/product/supervisor_plan.json"),
            "required": False,
            "issue_id": "supervisor_plan_stale_topic",
            "requires_expected_topic": True,
        },
        {
            "id": "agent_task_queue",
            "path": Path("state/product/agent_task_queue.json"),
            "required": False,
            "issue_id": "agent_task_queue_stale_topic",
            "requires_expected_topic": True,
        },
        {
            "id": "topic_brief",
            "path": Path(f"Tasks/{expected_slug}/brief.md"),
            "required": True,
            "issue_id": "topic_brief_contamination",
            "missing_issue_id": "topic_brief_missing",
            "requires_expected_topic": True,
        },
        {
            "id": "topic_literature",
            "path": Path(f"Tasks/{expected_slug}/literature.md"),
            "required": False,
            "issue_id": "topic_literature_contamination",
            "requires_expected_topic": False,
        },
        {
            "id": "topic_variables",
            "path": Path(f"Tasks/{expected_slug}/variables.yaml"),
            "required": False,
            "issue_id": "topic_variables_contamination",
            "requires_expected_topic": False,
        },
        {
            "id": "topic_design",
            "path": Path(f"Tasks/{expected_slug}/design.json"),
            "required": False,
            "issue_id": "topic_design_contamination",
            "requires_expected_topic": False,
        },
    ]


def audit_surface(project_root: Path, surface: dict[str, Any], topic_binding: dict[str, Any]) -> dict[str, Any]:
    relative_path = surface["path"]
    path = project_root / relative_path
    issues: list[dict[str, Any]] = []
    if not path.exists():
        if surface.get("required"):
            issues.append(
                build_issue(
                    surface.get("missing_issue_id") or f"{surface['id']}_missing",
                    "critical",
                    surface["id"],
                    relative_path,
                    "Current topic surface is missing.",
                    [],
                )
            )
            status = "critical"
        else:
            status = "not_found"
        return {
            "id": surface["id"],
            "path": relative_path.as_posix(),
            "exists": False,
            "status": status,
            "contains_expected_topic": False,
            "matched_stale_patterns": [],
            "issues": issues,
        }

    text = read_surface_text(path)
    matched_patterns = find_stale_topic_patterns(text)
    contains_expected = contains_current_topic_marker(text, topic_binding)
    if matched_patterns:
        issues.append(
            build_issue(
                surface["issue_id"],
                "critical",
                surface["id"],
                relative_path,
                "Current product surface contains stale topic markers.",
                matched_patterns,
            )
        )
    if surface.get("requires_expected_topic") and not contains_expected:
        issues.append(
            build_issue(
                surface["issue_id"],
                "critical",
                surface["id"],
                relative_path,
                "Current product surface is not bound to the expected demo topic.",
                matched_patterns,
            )
        )
    status = "critical" if any(issue["severity"] == "critical" for issue in issues) else "passed"
    return {
        "id": surface["id"],
        "path": relative_path.as_posix(),
        "exists": True,
        "status": status,
        "contains_expected_topic": contains_expected,
        "matched_stale_patterns": matched_patterns,
        "issues": dedupe_issues(issues),
    }


def read_surface_text(path: Path) -> str:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return raw
        return json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return raw


def find_stale_topic_patterns(text: str) -> list[dict[str, str]]:
    lowered = text.lower()
    matches = []
    for pattern_id, pattern in STALE_TOPIC_PATTERNS:
        if pattern.lower() in lowered:
            matches.append({"id": pattern_id, "pattern": pattern})
    return matches


def contains_current_topic_marker(text: str, topic_binding: dict[str, Any]) -> bool:
    lowered = text.lower()
    return topic_binding["expected_topic"] in text or topic_binding["expected_slug"].lower() in lowered


def build_issue(
    issue_id: str,
    severity: str,
    surface_id: str,
    path: Path,
    message: str,
    matched_patterns: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "id": issue_id,
        "severity": severity,
        "surface_id": surface_id,
        "path": path.as_posix(),
        "message": message,
        "matched_patterns": matched_patterns,
    }


def dedupe_issues(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    deduped = []
    for issue in issues:
        key = (issue["id"], issue["surface_id"], issue["path"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(issue)
    return deduped


def write_product_control_demo_topic_binding_audit_outputs(
    project_root: Path,
    report: dict[str, Any],
) -> tuple[Path, Path]:
    json_path = project_root / AUDIT_JSON_PATH
    review_path = project_root / AUDIT_REVIEW_PATH
    json_path.parent.mkdir(parents=True, exist_ok=True)
    review_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    review_path.write_text(render_review(report), encoding="utf-8")
    return json_path, review_path


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# Product Control Demo Topic Binding Audit",
        "",
        f"- status: {report['status']}",
        f"- expected_topic: {report['expected_topic']}",
        f"- expected_slug: {report['expected_slug']}",
        f"- can_proceed_to_p0b: {str(report['can_proceed_to_p0b']).lower()}",
        f"- critical_issue_count: {report['critical_issue_count']}",
        "",
        "## Critical Issues",
        "",
    ]
    if report["critical_issues"]:
        for issue in report["critical_issues"]:
            patterns = ", ".join(match["pattern"] for match in issue.get("matched_patterns", [])) or "none"
            lines.append(f"- {issue['id']} | {issue['path']} | {issue['message']} | patterns: {patterns}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Surfaces",
            "",
        ]
    )
    for surface in report["surfaces"]:
        lines.append(f"- {surface['id']} | {surface['status']} | {surface['path']}")
    lines.extend(["", f"Next action: {report['next_action']}", ""])
    return "\n".join(lines)
