from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workbench.export import relative_or_absolute, run_export_command
from workbench.paper_revision_round import diff_formal_state, snapshot_formal_state


DEFAULT_PREFLIGHT_REPORT = "Results/json/formal_docx_export_preflight.json"
DEFAULT_OUTPUT_REPORT = "Results/json/formal_docx_export.json"
DEFAULT_OUTPUT_REVIEW = "Reviews/formal_docx_export.md"
DEFAULT_OUTPUT_DOCX = "Submissions/formal_package/paper.docx"
DEFAULT_LOG_PATH = "Results/logs/formal_docx_export.log"
DEFAULT_GENERIC_MANIFEST = "Submissions/export_manifest.json"


def build_formal_docx_export(
    project_root: Path,
    *,
    repo_root: Path,
    preflight_report_path: Path,
    output_docx_path: Path,
    log_path: Path,
    generic_manifest_path: Path,
    formal_state_before: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], int]:
    before = formal_state_before or snapshot_formal_state(project_root)
    preflight = load_json(preflight_report_path)
    source_qmd = resolve_project_path(project_root, str(preflight.get("source_candidate_qmd") or ""))
    final_pdf = resolve_project_path(project_root, str(preflight.get("final_pdf") or ""))
    expected_docx = resolve_project_path(project_root, str(preflight.get("expected_docx") or ""))
    blocking_reasons = build_blocking_reasons(
        preflight=preflight,
        source_qmd=source_qmd,
        final_pdf=final_pdf,
        expected_docx=expected_docx,
        output_docx_path=output_docx_path,
    )

    export_command = build_export_command(
        project_root=project_root,
        source_qmd=source_qmd,
        output_docx_path=output_docx_path,
    )
    wrote_docx = False
    export_returncode = None
    export_stdout = None
    export_stderr = None

    if not blocking_reasons:
        output_docx_path.parent.mkdir(parents=True, exist_ok=True)
        result = run_export_command(export_command, log_path, cwd=repo_root)
        export_returncode = result.returncode
        export_stdout = result.stdout
        export_stderr = result.stderr
        if result.returncode != 0:
            blocking_reasons.append("pandoc_docx_export_failed")
        elif not output_docx_path.exists():
            blocking_reasons.append("docx_missing_after_export")
        else:
            wrote_docx = True

    after = snapshot_formal_state(project_root)
    status = build_status(blocking_reasons)
    docx_exists = output_docx_path.exists()
    return {
        "schema_version": "p6.formal_docx_export.v1",
        "generated_at": utc_now(),
        "status": status,
        "source_preflight_report": relative_or_absolute(preflight_report_path, project_root),
        "source_candidate_qmd": relative_or_absolute(source_qmd, project_root) if source_qmd else None,
        "final_pdf": relative_or_absolute(final_pdf, project_root) if final_pdf else None,
        "docx": relative_or_absolute(output_docx_path, project_root),
        "docx_exists": docx_exists,
        "docx_sha256": sha256_file(output_docx_path) if docx_exists else None,
        "docx_bytes": output_docx_path.stat().st_size if docx_exists else None,
        "generic_export_manifest": relative_or_absolute(generic_manifest_path, project_root),
        "generic_export_manifest_exists": generic_manifest_path.exists(),
        "log_path": relative_or_absolute(log_path, project_root),
        "export_command": export_command,
        "export_returncode": export_returncode,
        "export_stdout": export_stdout,
        "export_stderr": export_stderr,
        "blocking_reasons": blocking_reasons,
        "this_command_wrote_docx": wrote_docx,
        "this_command_wrote_pdf": False,
        "this_command_wrote_formal_state": False,
        "formal_state_guard": diff_formal_state(before, after),
        "next_action": build_next_action(blocking_reasons),
    }, 0 if not blocking_reasons else 2


def build_blocking_reasons(
    *,
    preflight: dict[str, Any],
    source_qmd: Path | None,
    final_pdf: Path | None,
    expected_docx: Path | None,
    output_docx_path: Path,
) -> list[str]:
    reasons: list[str] = []
    if preflight.get("status") != "ready_for_docx_export":
        reasons.append("preflight_not_ready")
    if preflight.get("can_export_docx") is not True:
        reasons.append("preflight_cannot_export_docx")
    if preflight.get("blocking_reasons"):
        reasons.append("preflight_has_blocking_reasons")
    if preflight.get("this_command_wrote_docx") is not False:
        reasons.append("preflight_docx_boundary_unclear")
    if preflight.get("formal_state_guard", {}).get("changed"):
        reasons.append("formal_state_changed_in_preflight")
    if final_pdf is None or not final_pdf.exists():
        reasons.append("final_pdf_missing")
    if source_qmd is None or not source_qmd.exists():
        reasons.append("candidate_qmd_missing")
    if expected_docx is None:
        reasons.append("expected_docx_missing")
    elif expected_docx != output_docx_path:
        reasons.append("expected_docx_mismatch")
    if "Submissions/formal_package" not in str(output_docx_path):
        reasons.append("docx_output_not_in_formal_package")
    return reasons


def build_status(blocking_reasons: list[str]) -> str:
    if not blocking_reasons:
        return "docx_exported"
    if any(reason.startswith("preflight_") or reason == "formal_state_changed_in_preflight" for reason in blocking_reasons):
        return "blocked_by_docx_preflight"
    if any(reason.endswith("_missing") or reason.endswith("_mismatch") for reason in blocking_reasons):
        return "blocked_by_docx_inputs"
    if "pandoc_docx_export_failed" in blocking_reasons or "docx_missing_after_export" in blocking_reasons:
        return "blocked_by_docx_export"
    return "blocked_by_docx_inputs"


def build_export_command(project_root: Path, source_qmd: Path | None, output_docx_path: Path) -> list[str]:
    return [
        "python3",
        "Program/export_docx.py",
        "--project-root",
        str(project_root),
        "--source",
        relative_or_absolute(source_qmd, project_root) if source_qmd else "",
        "--output",
        relative_or_absolute(output_docx_path, project_root),
    ]


def build_next_action(blocking_reasons: list[str]) -> dict[str, str]:
    if not blocking_reasons:
        return {
            "id": "assemble_submission_package_manifest",
            "label": "汇总正式投稿包清单",
            "description": "正式 PDF 和 docx 已生成。下一节点可以汇总 manifest、复现命令和人工验收说明。",
        }
    return {
        "id": "repair_formal_docx_export",
        "label": "修复 docx 导出",
        "description": "先修复 docx 预检、候选 QMD、最终 PDF 或 pandoc 导出错误，再重新运行 P6-C。",
    }


def write_formal_docx_export_outputs(
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
    command = " ".join(str(item) for item in report.get("export_command") or [])
    return f"""# P6-C 正式 docx 导出

## 当前状态

- 状态：`{report.get("status")}`
- 候选 QMD：`{report.get("source_candidate_qmd")}`
- 最终 PDF：`{report.get("final_pdf")}`
- 最终 docx：`{report.get("docx")}`
- docx sha256：`{report.get("docx_sha256")}`
- docx bytes：`{report.get("docx_bytes")}`
- 导出日志：`{report.get("log_path")}`
- 通用导出 manifest：`{report.get("generic_export_manifest")}`
- 写入 docx：`{str(report.get("this_command_wrote_docx")).lower()}`
- 写入 PDF：`{str(report.get("this_command_wrote_pdf")).lower()}`
- 写入正式研究状态：`{str(report.get("this_command_wrote_formal_state")).lower()}`

## 执行命令

```bash
{command}
```

## 阻断原因

{blocker_lines}

## 下一步

- `{report.get("next_action", {}).get("id")}`：{report.get("next_action", {}).get("description")}
"""


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_project_path(project_root: Path, value: str) -> Path | None:
    if not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
