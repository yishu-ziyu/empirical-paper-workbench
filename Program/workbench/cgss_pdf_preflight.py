from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


SCHEMA_VERSION = "p6.cgss_pdf_preflight.v1"
DEFAULT_PAPER_PATH = Path("Manuscripts/generated/cgss_social_capital_happiness_paper.md")
DEFAULT_PDF_PATH = Path("Submissions/cgss_social_capital_happiness/paper.pdf")
DEFAULT_HTML_PATH = Path("Submissions/cgss_social_capital_happiness/paper.html")
DEFAULT_RESULT_PATH = Path("Results/json/cgss_social_capital_happiness_pdf_preflight.json")
DEFAULT_REVIEW_PATH = Path("Reviews/cgss_social_capital_happiness_pdf_preflight.md")

Renderer = Callable[[Path, Path, Path], dict[str, Any]]


def build_cgss_pdf_preflight(
    project_root: Path,
    paper_path: Path = DEFAULT_PAPER_PATH,
    pdf_path: Path = DEFAULT_PDF_PATH,
    *,
    html_path: Path = DEFAULT_HTML_PATH,
    renderer: Renderer | None = None,
) -> dict[str, Any]:
    renderer = renderer or render_pdf_with_pandoc
    absolute_paper = project_root / paper_path
    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "paper_source": str(paper_path),
        "pdf": {
            "path": str(pdf_path),
            "exists": False,
            "bytes": 0,
        },
        "html": {
            "path": str(html_path),
            "exists": False,
            "bytes": 0,
        },
        "boundary_flags": {
            "modified_formal_manuscript": False,
            "modified_verified_bibliography": False,
            "modified_formal_package": False,
            "modified_product_state": False,
        },
    }
    if not absolute_paper.exists():
        return {
            **base,
            "status": "blocked_missing_exploratory_paper",
            "blocking_reasons": ["exploratory_paper_missing"],
            "renderer": {},
            "next_tasks": ["assemble_exploratory_paper_draft"],
        }

    render_result = renderer(project_root, paper_path, pdf_path)
    pdf_info = file_info(project_root / pdf_path)
    if render_result.get("ok") and pdf_info["exists"]:
        return {
            **base,
            "status": "pdf_preflight_ready",
            "blocking_reasons": [],
            "renderer": render_result,
            "pdf": {"path": str(pdf_path), **pdf_info},
            "next_tasks": [
                "human_review_pdf_candidate",
                "build_aer_like_method_gate",
                "generate_reviewer_report_and_revision_queue",
            ],
            "agent_team_schedule": agent_team_schedule("pdf_preflight_ready"),
        }

    html_result = render_html_with_pandoc(project_root, paper_path, html_path)
    html_info = file_info(project_root / html_path)
    return {
        **base,
        "status": "html_preflight_ready_pdf_failed" if html_info["exists"] else "blocked_pdf_and_html_preflight_failed",
        "blocking_reasons": [] if html_info["exists"] else ["pdf_renderer_failed", "html_renderer_failed"],
        "renderer": {
            "pdf": render_result,
            "html": html_result,
        },
        "pdf": {"path": str(pdf_path), **pdf_info},
        "html": {"path": str(html_path), **html_info},
        "next_tasks": [
            "inspect_pdf_renderer_error",
            "human_review_html_candidate",
            "repair_pdf_export_environment",
        ],
        "agent_team_schedule": agent_team_schedule("html_fallback"),
    }


def render_pdf_with_pandoc(project_root: Path, paper_path: Path, pdf_path: Path) -> dict[str, Any]:
    absolute_pdf = project_root / pdf_path
    absolute_pdf.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "pandoc",
        str(paper_path),
        "-o",
        str(pdf_path),
        "--pdf-engine=xelatex",
        "-V",
        "CJKmainfont=Songti SC",
        "-V",
        "geometry:margin=1in",
    ]
    return run_renderer(command, project_root, "pandoc+xelatex")


def render_html_with_pandoc(project_root: Path, paper_path: Path, html_path: Path) -> dict[str, Any]:
    absolute_html = project_root / html_path
    absolute_html.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "pandoc",
        str(paper_path),
        "-s",
        "-o",
        str(html_path),
        "--metadata",
        "title=CGSS 社会资本与幸福感探索性论文",
    ]
    return run_renderer(command, project_root, "pandoc-html")


def run_renderer(command: list[str], project_root: Path, engine: str) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=project_root,
        text=True,
        capture_output=True,
    )
    return {
        "ok": completed.returncode == 0,
        "engine": engine,
        "returncode": completed.returncode,
        "stdout": completed.stdout[-2000:],
        "stderr": completed.stderr[-4000:],
    }


def file_info(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False, "bytes": 0}
    return {"exists": True, "bytes": path.stat().st_size}


def agent_team_schedule(status: str) -> dict[str, Any]:
    return {
        "call_when": "after_pdf_or_html_preflight_artifact_is_created",
        "called_agents": ["VerifierAgent", "ManuscriptAgent", "ExportAgent"],
        "recall_when": "after_human_opens_rendered_artifact",
        "next_call_when": "before_formal_package_or_revision_round",
        "boundary": f"当前渲染状态为 {status}；只做草案预检，不提升正式层。",
    }


def write_cgss_pdf_preflight_outputs(
    project_root: Path,
    package: dict[str, Any],
    result_path: Path = DEFAULT_RESULT_PATH,
    review_path: Path = DEFAULT_REVIEW_PATH,
) -> tuple[Path, Path]:
    absolute_result = project_root / result_path
    absolute_review = project_root / review_path
    absolute_result.parent.mkdir(parents=True, exist_ok=True)
    absolute_review.parent.mkdir(parents=True, exist_ok=True)
    absolute_result.write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    absolute_review.write_text(render_review(package), encoding="utf-8")
    return absolute_result, absolute_review


def render_review(package: dict[str, Any]) -> str:
    lines = [
        "# CGSS PDF 预检",
        "",
        f"- 状态：`{package.get('status')}`",
        f"- Markdown 来源：`{package.get('paper_source')}`",
        f"- PDF：`{package.get('pdf', {}).get('path')}`",
        f"- PDF 存在：`{str(package.get('pdf', {}).get('exists')).lower()}`",
        f"- PDF 字节：{package.get('pdf', {}).get('bytes', 0)}",
        f"- HTML：`{package.get('html', {}).get('path')}`",
        f"- HTML 存在：`{str(package.get('html', {}).get('exists')).lower()}`",
        f"- 正式层写回：`{str(package.get('formal_writeback_allowed', False)).lower()}`",
    ]
    if package.get("blocking_reasons"):
        lines.extend(["", "## 阻断原因"])
        for reason in package["blocking_reasons"]:
            lines.append(f"- `{reason}`")
    lines.extend(["", "## 渲染器"])
    renderer = package.get("renderer", {})
    if "pdf" in renderer:
        lines.append(f"- pdf: `{renderer.get('pdf', {}).get('engine')}` returncode={renderer.get('pdf', {}).get('returncode')}")
        lines.append(f"- html: `{renderer.get('html', {}).get('engine')}` returncode={renderer.get('html', {}).get('returncode')}")
    else:
        lines.append(f"- `{renderer.get('engine', '')}` returncode={renderer.get('returncode', '')}")
    lines.extend(["", "## Agent Team 调用节奏"])
    for key, value in package.get("agent_team_schedule", {}).items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## 下一步"])
    for task in package.get("next_tasks", []):
        lines.append(f"- `{task}`")
    return "\n".join(lines).rstrip() + "\n"
