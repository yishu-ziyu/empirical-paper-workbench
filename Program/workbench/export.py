from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def build_export_manifest(
    project_root: Path,
    markdown_path: Path,
    docx_path: Path,
    reference_doc: Path | None,
    command: list[str],
) -> dict[str, Any]:
    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source_markdown": str(markdown_path.relative_to(project_root)),
        "output_docx": str(docx_path.relative_to(project_root)),
        "reference_doc": str(reference_doc.relative_to(project_root)) if reference_doc else None,
        "command": command,
        "docx_exists": docx_path.exists(),
    }


def write_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def relative_or_absolute(path: Path, project_root: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def load_json_report(path: Path, invalid_payload: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return invalid_payload


def normalize_review_tasks(tasks: Any, source: str) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    if not isinstance(tasks, list):
        return normalized
    for index, task in enumerate(tasks, start=1):
        if isinstance(task, dict):
            item = dict(task)
        else:
            item = {
                "id": f"{source}_task_{index}",
                "action": str(task),
            }
        item.setdefault("source", source)
        normalized.append(item)
    return normalized


def build_pdf_export_review_gate(project_root: Path) -> dict[str, Any]:
    quality_report = project_root / "Results" / "json" / "paper_quality_report.json"
    scorecard_report = project_root / "Results" / "json" / "reviewer_scorecard_report.json"
    quality_payload = load_json_report(quality_report, {"verdict": ["invalid_quality_report"]})
    scorecard_payload = load_json_report(
        scorecard_report,
        {
            "overall_verdict": "invalid_reviewer_scorecard",
            "blocks_export_or_formal_claims": True,
            "revision_tasks": [{"id": "repair_reviewer_scorecard", "action": "修复审稿评分卡 JSON"}],
        },
    )
    gate: dict[str, Any] = {
        "agent_team_schedule": {
            "call_when": "before_pdf_export_preflight",
            "called_agents": ["ExportAgent", "ReviewerAgent", "VerifierAgent"],
            "recall_when": "after_pdf_export_manifest_written",
            "next_call_when": "before_formal_writeback_or_final_export",
            "integration_owner": "MainAgent",
            "boundary": "Agent Team 只读取质量门和评分卡，写入 manifest/review doc 后收回；不改写正式层。",
        },
        "next_review_tasks": [],
    }
    blocking_reasons: list[str] = []

    if quality_payload:
        verdict = quality_payload.get("verdict", [])
        if not isinstance(verdict, list):
            verdict = [str(verdict)]
        gate["paper_quality_report"] = {
            "path": relative_or_absolute(quality_report, project_root),
            "verdict": verdict,
            "recommended_next_tasks": quality_payload.get("recommended_next_tasks", []),
        }
        gate["next_review_tasks"].extend(
            normalize_review_tasks(quality_payload.get("recommended_next_tasks", []), "paper_quality_report")
        )
        blocking_verdicts = {
            "invalid_quality_report",
            "too_thin",
            "format_gate_required",
            "needs_literature_review",
            "method_gate_required",
            "needs_review_loop",
        }
        blocking_reasons.extend(f"quality:{item}" for item in verdict if item in blocking_verdicts)

    if scorecard_payload:
        blocks_export = bool(scorecard_payload.get("blocks_export_or_formal_claims"))
        gate["reviewer_scorecard"] = {
            "path": relative_or_absolute(scorecard_report, project_root),
            "overall_score": scorecard_payload.get("overall_score"),
            "overall_verdict": scorecard_payload.get("overall_verdict"),
            "blocks_export_or_formal_claims": blocks_export,
            "revision_tasks": scorecard_payload.get("revision_tasks", []),
        }
        gate["next_review_tasks"].extend(
            normalize_review_tasks(scorecard_payload.get("revision_tasks", []), "reviewer_scorecard")
        )
        if blocks_export:
            blocking_reasons.append("reviewer_scorecard:blocks_export_or_formal_claims")

    gate["export_gate"] = {
        "status": "needs_review" if blocking_reasons else "ready",
        "can_export_pdf": not blocking_reasons,
        "blocking_reasons": blocking_reasons,
    }
    return gate


def run_pandoc(command: list[str], log_path: Path) -> subprocess.CompletedProcess[str]:
    return run_export_command(command, log_path)


def run_export_command(
    command: list[str],
    log_path: Path,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        "\n".join(
            [
                "COMMAND:",
                " ".join(command),
                "",
                "STDOUT:",
                result.stdout,
                "",
                "STDERR:",
                result.stderr,
            ]
        ),
        encoding="utf-8",
    )
    return result


def pdf_export_preflight(project_root: Path, source_qmd: Path, output_pdf: Path) -> dict[str, Any]:
    checks = [
        {
            "id": "source_qmd_exists",
            "status": "passed" if source_qmd.exists() else "failed",
            "path": relative_or_absolute(source_qmd, project_root),
            "required": True,
        },
        {
            "id": "quarto_available",
            "status": "passed" if shutil.which("quarto") else "failed",
            "path": shutil.which("quarto"),
            "required": True,
        },
        {
            "id": "xelatex_available",
            "status": "passed" if shutil.which("xelatex") else "failed",
            "path": shutil.which("xelatex"),
            "required": True,
        },
        {
            "id": "output_pdf_declared",
            "status": "passed" if output_pdf.suffix.lower() == ".pdf" else "failed",
            "path": relative_or_absolute(output_pdf, project_root),
            "required": True,
        },
    ]
    status = "ready" if all(check["status"] == "passed" for check in checks if check["required"]) else "blocked"
    return {
        "status": status,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
    }


def build_pdf_export_manifest(
    project_root: Path,
    source_qmd: Path,
    output_pdf: Path,
    command: list[str],
    preflight: dict[str, Any],
    log_path: Path,
    review_doc: Path | None = None,
    reproduce_script: Path | None = None,
    full_reproduce_script: Path | None = None,
) -> dict[str, Any]:
    manifest = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "export_format": "pdf",
        "source_qmd": relative_or_absolute(source_qmd, project_root),
        "output_pdf": relative_or_absolute(output_pdf, project_root),
        "log_path": relative_or_absolute(log_path, project_root),
        "engine": "quarto",
        "command": command,
        "preflight": preflight,
        "pdf_exists": output_pdf.exists(),
    }
    if review_doc is not None:
        manifest["review_doc"] = relative_or_absolute(review_doc, project_root)
    if reproduce_script is not None:
        manifest["reproduce_script"] = relative_or_absolute(reproduce_script, project_root)
    if full_reproduce_script is not None:
        manifest["full_reproduce_script"] = relative_or_absolute(full_reproduce_script, project_root)
    review_gate = build_pdf_export_review_gate(project_root)
    for key in (
        "paper_quality_report",
        "reviewer_scorecard",
        "export_gate",
        "next_review_tasks",
        "agent_team_schedule",
    ):
        if key in review_gate:
            manifest[key] = review_gate[key]
    return manifest


def write_pdf_reproduce_script(
    path: Path,
    project_root: Path,
    source_qmd: Path,
    output_pdf: Path,
    manifest_path: Path,
    review_doc: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    source_arg = relative_or_absolute(source_qmd, project_root)
    output_arg = relative_or_absolute(output_pdf, project_root)
    manifest_arg = relative_or_absolute(manifest_path, project_root)
    review_arg = relative_or_absolute(review_doc, project_root)
    reproduce_arg = relative_or_absolute(path, project_root)
    content = "\n".join(
        [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            'cd "$(dirname "$0")/.."',
            "",
            "python3 Program/paper_quality.py \\",
            "  --project-root .",
            "",
            "if [ -f Results/json/method_diagnostics_report.json ] && [ -f Results/json/method_gate_report.json ]; then",
            "  python3 Program/reviewer_scorecard.py \\",
            "    --project-root .",
            "fi",
            "",
            "python3 Program/export_pdf.py \\",
            f"  --project-root . \\",
            f"  --source {source_arg} \\",
            f"  --output {output_arg} \\",
            f"  --manifest {manifest_arg} \\",
            f"  --review-doc {review_arg} \\",
            f"  --reproduce-script {reproduce_arg}",
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | 0o111)


def write_pdf_full_chain_reproduce_script(
    path: Path,
    project_root: Path,
    paper_config: Path,
    source_qmd: Path,
    output_pdf: Path,
    manifest_path: Path,
    review_doc: Path,
    reproduce_script: Path,
    full_reproduce_script: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    paper_config_arg = relative_or_absolute(paper_config, project_root)
    source_arg = relative_or_absolute(source_qmd, project_root)
    output_arg = relative_or_absolute(output_pdf, project_root)
    manifest_arg = relative_or_absolute(manifest_path, project_root)
    review_arg = relative_or_absolute(review_doc, project_root)
    reproduce_arg = relative_or_absolute(reproduce_script, project_root)
    full_reproduce_arg = relative_or_absolute(full_reproduce_script, project_root)
    content = "\n".join(
        [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            'cd "$(dirname "$0")/.."',
            'RUN_ID="${RUN_ID:-run_pdf_first_reproduce_$(date -u +%Y%m%dT%H%M%SZ)}"',
            "",
            "python3 Program/run_paper.py \\",
            "  --project-root . \\",
            f"  --paper-config {paper_config_arg} \\",
            '  --run-id "$RUN_ID"',
            "",
            "python3 Program/paper_quality.py \\",
            "  --project-root .",
            "",
            "if [ -f Results/json/method_diagnostics_report.json ] && [ -f Results/json/method_gate_report.json ]; then",
            "  python3 Program/reviewer_scorecard.py \\",
            "    --project-root .",
            "fi",
            "",
            "python3 Program/export_pdf.py \\",
            "  --project-root . \\",
            f"  --source {source_arg} \\",
            f"  --output {output_arg} \\",
            f"  --manifest {manifest_arg} \\",
            f"  --review-doc {review_arg} \\",
            f"  --reproduce-script {reproduce_arg} \\",
            f"  --paper-config {paper_config_arg} \\",
            f"  --full-reproduce-script {full_reproduce_arg}",
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | 0o111)


def write_pdf_review_doc(
    path: Path,
    project_root: Path,
    source_qmd: Path,
    output_pdf: Path,
    manifest_path: Path,
    log_path: Path,
    reproduce_script: Path,
    full_reproduce_script: Path | None,
    preflight: dict[str, Any],
    manifest: dict[str, Any] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    checks = "\n".join(
        f"- `{check['id']}`: {check['status']} ({check.get('path')})" for check in preflight.get("checks", [])
    )
    manifest = manifest or {}
    quality_report = manifest.get("paper_quality_report", {})
    reviewer_scorecard = manifest.get("reviewer_scorecard", {})
    export_gate = manifest.get("export_gate", {})
    review_tasks = manifest.get("next_review_tasks", [])
    if review_tasks:
        next_tasks = "\n".join(
            f"- `{task.get('id')}`："
            f"{task.get('action') or task.get('recommended_action') or task.get('reason') or task.get('owner') or task.get('agent') or '待补充'}"
            f"（来源：{task.get('source')}）"
            for task in review_tasks
        )
    else:
        next_tasks = "- 当前没有写入下一轮审阅任务。"
    quality_line = (
        f"- Paper Quality Report：`{quality_report.get('path')}`，verdict={quality_report.get('verdict')}"
        if quality_report
        else "- Paper Quality Report：未发现"
    )
    scorecard_line = (
        "- Reviewer Scorecard："
        f"`{reviewer_scorecard.get('path')}`，score={reviewer_scorecard.get('overall_score')}，"
        f"verdict={reviewer_scorecard.get('overall_verdict')}"
        if reviewer_scorecard
        else "- Reviewer Scorecard：未发现"
    )
    gate_line = (
        f"- Export Gate：{export_gate.get('status')}，can_export_pdf={export_gate.get('can_export_pdf')}，"
        f"blocking_reasons={export_gate.get('blocking_reasons')}"
        if export_gate
        else "- Export Gate：未生成"
    )
    content = f"""# PDF-first 探索性研究包

## 当前状态

- 证据等级：exploratory / draft / needs_human_review
- PDF 预检：{preflight.get("status")}
- QMD 稿源：`{relative_or_absolute(source_qmd, project_root)}`
- PDF 审阅稿：`{relative_or_absolute(output_pdf, project_root)}`
- 导出 manifest：`{relative_or_absolute(manifest_path, project_root)}`
- 导出日志：`{relative_or_absolute(log_path, project_root)}`
- 复跑脚本：`{relative_or_absolute(reproduce_script, project_root)}`
- 完整链路复跑脚本：`{relative_or_absolute(full_reproduce_script, project_root) if full_reproduce_script else "未生成"}`

## 预检结果

{checks}

## 论文包审阅入口

{quality_line}
{scorecard_line}
{gate_line}

## 下一轮任务

{next_tasks}

## Agent Team 调用节奏

- 调用点：PDF 预检前由 ExportAgent 调用 ReviewerAgent / VerifierAgent。
- 收回点：manifest、review doc 和复跑脚本写出后收回，由主线程集成状态。
- 再调用点：用户批准正式层写回或最终导出前，再次调用 ReviewerAgent / VerifierAgent。

## 如何复跑 PDF

```bash
{relative_or_absolute(reproduce_script, project_root)}
```

## 如何从真实配置完整复跑

```bash
{relative_or_absolute(full_reproduce_script, project_root) if full_reproduce_script else "# 本次导出未提供 paper_config，因此未生成完整链路复跑脚本"}
```

## 人工审阅重点

- 当前处于草稿审阅阶段：可以继续扩写、复跑和补证据。
- 变量角色、识别策略和模型设定在正式层写回前需要人工确认。
- PDF 复跑脚本验证排版链路；完整链路复跑脚本验证真实配置、草案源和 PDF 导出可以串起来执行。
"""
    path.write_text(content, encoding="utf-8")
