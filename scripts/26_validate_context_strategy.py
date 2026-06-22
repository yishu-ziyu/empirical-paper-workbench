#!/usr/bin/env python3
"""Validate the project memory and context loading strategy."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STRATEGY_PATH = ROOT / "Tasks" / "context-loading-strategy.md"
INDEX_PATH = ROOT / "workflows" / "memory_index.json"
SCHEMA_PATH = ROOT / "workflows" / "schemas" / "memory_index.schema.json"
GITIGNORE_PATH = ROOT / ".gitignore"
REPORT_PATH = ROOT / "artifacts" / "context_strategy_validation_report.md"

REQUIRED_MEMORY_CLASSES = {
    "system_instruction",
    "project_instruction",
    "workflow_procedure",
    "project_episode",
    "domain_semantic",
    "local_private",
    "user_global_learning",
    "role_agent_memory",
}

REQUIRED_LOAD_PROFILES = {
    "default_turn",
    "workflow_task",
    "literature_task",
    "data_gate_task",
    "product_api_task",
}

REQUIRED_WRITE_TARGETS = {
    "stable_rules",
    "user_corrections",
    "task_progress",
    "validation_reports",
    "machine_state",
    "local_private_notes",
}


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path, errors: list[str]) -> dict:
    if not path.exists():
        errors.append(f"missing file: {relative(path)}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{relative(path)} invalid JSON: {exc}")
        return {}


def count_lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


def main() -> None:
    errors: list[str] = []
    warnings: list[str] = []

    for path in [STRATEGY_PATH, INDEX_PATH, SCHEMA_PATH, GITIGNORE_PATH]:
        if not path.exists():
            errors.append(f"missing file: {relative(path)}")

    index = read_json(INDEX_PATH, errors)
    schema = read_json(SCHEMA_PATH, errors)

    if schema and schema.get("title") != "StatspAI Memory Index":
        errors.append(f"{relative(SCHEMA_PATH)} has unexpected title")

    if index:
        if index.get("layer") != "second":
            errors.append(f"{relative(INDEX_PATH)} layer must be second")

        class_ids = {item.get("id") for item in index.get("memory_classes", [])}
        missing_classes = REQUIRED_MEMORY_CLASSES - class_ids
        if missing_classes:
            errors.append(f"missing memory classes: {', '.join(sorted(missing_classes))}")

        profile_ids = {item.get("id") for item in index.get("load_profiles", [])}
        missing_profiles = REQUIRED_LOAD_PROFILES - profile_ids
        if missing_profiles:
            errors.append(f"missing load profiles: {', '.join(sorted(missing_profiles))}")

        target_ids = {item.get("id") for item in index.get("write_targets", [])}
        missing_targets = REQUIRED_WRITE_TARGETS - target_ids
        if missing_targets:
            errors.append(f"missing write targets: {', '.join(sorted(missing_targets))}")

        budget = index.get("context_budget", {})
        if budget.get("max_project_instruction_lines", 0) > 200:
            errors.append("max_project_instruction_lines must be <= 200")
        if budget.get("load_raw_pdf_by_default") is not False:
            errors.append("raw PDFs must not load by default")
        if budget.get("load_raw_data_by_default") is not False:
            errors.append("raw data must not load by default")
        if budget.get("load_current_agent_spec_only") is not True:
            errors.append("only the current agent spec should load by default")

        forbidden = {item.lower() for item in index.get("forbidden_memory", [])}
        for required in ["passwords", "api keys", "cookies", "vpn sessions"]:
            if required not in forbidden:
                errors.append(f"forbidden_memory missing {required}")

        validators = set(index.get("validators", []))
        if "scripts/26_validate_context_strategy.py" not in validators:
            errors.append("validator list must include scripts/26_validate_context_strategy.py")
        if "scripts/25_agent_runtime_preflight.py" not in validators:
            errors.append("validator list must include scripts/25_agent_runtime_preflight.py")

    if STRATEGY_PATH.exists():
        strategy = STRATEGY_PATH.read_text(encoding="utf-8")
        for phrase in [
            "少量常驻 + 按需加载 + 明确写回",
            "记忆分层",
            "加载配置",
            "写回配置",
            "上下文预算",
            "Skill 边界",
        ]:
            if phrase not in strategy:
                errors.append(f"{relative(STRATEGY_PATH)} missing section or phrase: {phrase}")

    agents_path = ROOT / "AGENTS.md"
    if agents_path.exists():
        agents_lines = count_lines(agents_path)
        if agents_lines > 200:
            errors.append(f"AGENTS.md too long: {agents_lines} lines")
    else:
        errors.append("missing AGENTS.md")

    if GITIGNORE_PATH.exists():
        gitignore = GITIGNORE_PATH.read_text(encoding="utf-8")
        if ".agent-memory/local/" not in gitignore:
            errors.append(".gitignore must exclude .agent-memory/local/")
        if "*.local" not in gitignore:
            errors.append(".gitignore must exclude *.local")
        if ".env" not in gitignore:
            errors.append(".gitignore must exclude .env")
        if ".claude/" not in gitignore:
            warnings.append(".gitignore should exclude .claude/")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Context Strategy Validation",
        "",
        f"Status: {'FAIL' if errors else 'PASS'}",
        "",
        f"- Strategy: `{relative(STRATEGY_PATH)}`",
        f"- Memory index: `{relative(INDEX_PATH)}`",
        f"- Schema: `{relative(SCHEMA_PATH)}`",
        f"- AGENTS.md lines: {count_lines(ROOT / 'AGENTS.md') if (ROOT / 'AGENTS.md').exists() else 'missing'}",
        "",
    ]

    if warnings:
        lines.extend(["## Warnings", "", *[f"- {warning}" for warning in warnings], ""])
    if errors:
        lines.extend(["## Errors", "", *[f"- {error}" for error in errors], ""])
    else:
        lines.extend(
            [
                "## Checks",
                "",
                f"- Memory classes: {len(index.get('memory_classes', []))}",
                f"- Load profiles: {len(index.get('load_profiles', []))}",
                f"- Write targets: {len(index.get('write_targets', []))}",
                "- Raw PDFs and raw data are not default-loaded.",
                "- Local private memory is ignored by Git.",
                "",
            ]
        )

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    if errors:
        raise SystemExit(1)
    print(f"PASS report={relative(REPORT_PATH)}")


if __name__ == "__main__":
    main()
