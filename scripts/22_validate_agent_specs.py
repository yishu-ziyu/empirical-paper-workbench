#!/usr/bin/env python3
"""Validate second-layer agent specs."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = ROOT / "workflows" / "agents"
SCHEMA_PATH = ROOT / "workflows" / "schemas" / "workflow_io.schema.json"
EVAL_PATH = ROOT / "workflows" / "evals" / "charls_agent_eval.md"
REPORT_PATH = ROOT / "artifacts" / "agent_spec_validation_report.md"

AGENT_FILES = [
    "01_design.agent.md",
    "02_literature.agent.md",
    "03_paper_reading.agent.md",
    "04_data_gate.agent.md",
    "05_causal_analysis.agent.md",
    "06_writing.agent.md",
    "07_revision.agent.md",
    "08_format_citation.agent.md",
    "09_replication.agent.md",
    "10_defense.agent.md",
]

REQUIRED_HEADINGS = [
    "## Workflow",
    "## Mission",
    "## Inputs",
    "## Tools",
    "## Actions",
    "## Outputs",
    "## Gates",
    "## Failure Codes",
    "## Human Checkpoints",
    "## Current CHARLS Eval",
]

REQUIRED_SCHEMA_KEYS = {
    "$schema",
    "title",
    "type",
    "required",
    "additionalProperties",
    "properties",
    "definitions",
}


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT))


def validate_agent_file(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"missing agent spec: {relative(path)}"]

    text = path.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"{relative(path)} missing heading: {heading}")

    codes = re.findall(r"`([A-Z][A-Z0-9_]+)`", text)
    if not codes:
        errors.append(f"{relative(path)} has no backticked failure codes")
    if "## Failure Codes" in text and len(codes) < 3:
        errors.append(f"{relative(path)} should define at least 3 failure codes")

    return errors


def validate_schema() -> tuple[list[str], dict]:
    errors: list[str] = []
    if not SCHEMA_PATH.exists():
        return [f"missing schema: {relative(SCHEMA_PATH)}"], {}

    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{relative(SCHEMA_PATH)} invalid JSON: {exc}"], {}

    missing = REQUIRED_SCHEMA_KEYS - set(schema)
    if missing:
        errors.append(f"{relative(SCHEMA_PATH)} missing keys: {', '.join(sorted(missing))}")

    properties = schema.get("properties", {})
    for key in ("workflow_id", "inputs", "outputs", "gates", "status", "provenance"):
        if key not in properties:
            errors.append(f"{relative(SCHEMA_PATH)} missing property: {key}")

    return errors, schema


def validate_eval() -> list[str]:
    errors: list[str] = []
    if not EVAL_PATH.exists():
        return [f"missing eval: {relative(EVAL_PATH)}"]

    text = EVAL_PATH.read_text(encoding="utf-8")
    workflow_ids = [
        "01_design",
        "02_literature",
        "03_paper_reading",
        "04_data_gate",
        "05_causal_analysis",
        "06_writing",
        "07_revision",
        "08_format_citation",
        "09_replication",
        "10_defense",
    ]
    for workflow_id in workflow_ids:
        if workflow_id not in text:
            errors.append(f"{relative(EVAL_PATH)} missing workflow id: {workflow_id}")
    for expected in ["PASS", "Failure Injection", "Current Verdict"]:
        if expected not in text:
            errors.append(f"{relative(EVAL_PATH)} missing section/content: {expected}")

    return errors


def main() -> None:
    errors: list[str] = []
    agent_paths = [AGENT_DIR / name for name in AGENT_FILES]

    for path in agent_paths:
        errors.extend(validate_agent_file(path))

    schema_errors, schema = validate_schema()
    errors.extend(schema_errors)
    errors.extend(validate_eval())

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    if errors:
        lines = [
            "# Agent Spec Validation",
            "",
            "Status: FAIL",
            "",
            *[f"- {error}" for error in errors],
            "",
        ]
        REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
        raise SystemExit(1)

    lines = [
        "# Agent Spec Validation",
        "",
        "Status: PASS",
        "",
        f"- Agent specs: {len(agent_paths)}",
        f"- Schema: `{relative(SCHEMA_PATH)}`",
        f"- Eval: `{relative(EVAL_PATH)}`",
        f"- Schema required fields: {', '.join(schema.get('required', []))}",
        "",
        "Validated files:",
        *[f"- `{relative(path)}`" for path in agent_paths],
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"PASS agent_specs={len(agent_paths)} report={relative(REPORT_PATH)}")


if __name__ == "__main__":
    main()
