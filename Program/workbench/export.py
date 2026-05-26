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
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    checks = "\n".join(
        f"- `{check['id']}`: {check['status']} ({check.get('path')})" for check in preflight.get("checks", [])
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

## 如何复跑 PDF

```bash
{relative_or_absolute(reproduce_script, project_root)}
```

## 如何从真实配置完整复跑

```bash
{relative_or_absolute(full_reproduce_script, project_root) if full_reproduce_script else "# 本次导出未提供 paper_config，因此未生成完整链路复跑脚本"}
```

## 人工审阅重点

- 这份 PDF 是探索性研究包，不是正式论文。
- 变量角色、识别策略和模型设定仍需要人工确认后才能进入正式层。
- PDF 复跑脚本验证排版链路；完整链路复跑脚本验证真实配置、草案源和 PDF 导出可以串起来执行。
"""
    path.write_text(content, encoding="utf-8")
