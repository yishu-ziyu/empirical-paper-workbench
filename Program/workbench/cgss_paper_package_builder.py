from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "p6.cgss_paper_package.v1"
DEFAULT_PACKAGE_DIR = Path("workspace/paper_packages/cgss_social_capital_happiness")


SOURCE_FILES = [
    {
        "source": Path("Manuscripts/generated/cgss_social_capital_happiness_paper_rev1.md"),
        "fallback_source": Path("Manuscripts/generated/cgss_social_capital_happiness_paper.md"),
        "target": "paper.md",
        "kind": "draft_layer",
        "required": True,
    },
    {
        "source": Path("Results/json/cgss_social_capital_happiness_results_evidence_package.json"),
        "target": "results_evidence_package.json",
        "kind": "real_run",
        "required": True,
    },
    {
        "source": Path("Results/json/cgss_social_capital_happiness_literature_review_draft_packet.json"),
        "target": "literature_review_packet.json",
        "kind": "draft_layer",
        "required": True,
    },
    {
        "source": Path("Reviews/cgss_social_capital_happiness_method_gate.md"),
        "target": "method_gate.md",
        "kind": "human_review_required",
        "required": True,
    },
    {
        "source": Path("Reviews/cgss_social_capital_happiness_reviewer_report.md"),
        "target": "reviewer_report.md",
        "kind": "human_review_required",
        "required": True,
    },
    {
        "source": Path("Reviews/cgss_social_capital_happiness_revision_task_queue.md"),
        "target": "revision_task_queue.md",
        "kind": "human_review_required",
        "required": True,
    },
]


def build_cgss_paper_package(
    project_root: Path,
    package_dir: Path = DEFAULT_PACKAGE_DIR,
) -> dict[str, Any]:
    files = resolve_source_files(project_root)
    rendered, warnings = rendered_artifact(project_root)
    if rendered:
        files.append(rendered)
    files.append(
        {
            "source": None,
            "target": "reproducibility_readme.md",
            "kind": "generated_package_metadata",
            "required": True,
        }
    )
    files.append(
        {
            "source": None,
            "target": "manifest.json",
            "kind": "generated_package_metadata",
            "required": True,
        }
    )
    missing_targets = [file["target"] for file in files if file.get("required") and file.get("source") and not file["source"].exists()]
    if not rendered:
        missing_targets.append("paper.pdf_or_preview.html")

    base = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "topic": "社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
        "package_dir": str(package_dir),
        "draft_layer_only": True,
        "formal_writeback_allowed": False,
        "boundary_flags": {
            "modified_formal_manuscript": False,
            "modified_verified_bibliography": False,
            "modified_product_state": False,
        },
        "files": [
            {
                "source": str(file["source"]) if file.get("source") else "",
                "target": file["target"],
                "kind": file["kind"],
            }
            for file in files
        ],
        "warnings": warnings,
        "rendered_artifact": rendered["target"] if rendered else "",
        "real_run_artifacts": [file["target"] for file in files if file["kind"] == "real_run"],
        "draft_layer_artifacts": [file["target"] for file in files if file["kind"] == "draft_layer"],
        "human_review_required": [file["target"] for file in files if file["kind"] == "human_review_required"],
    }
    if missing_targets:
        return {
            **base,
            "status": "blocked_missing_package_inputs",
            "missing_targets": missing_targets,
            "next_tasks": ["repair_missing_package_inputs"],
        }
    return {
        **base,
        "status": "needs_human_paper_package_review",
        "missing_targets": [],
        "next_tasks": [
            "human_open_paper_md_and_pdf",
            "human_review_method_gate_reviewer_report_revision_queue",
            "decide_formal_layer_promotion_or_next_revision",
        ],
    }


def resolve_source_files(project_root: Path) -> list[dict[str, Any]]:
    files = []
    for item in SOURCE_FILES:
        source = project_root / item["source"]
        fallback = item.get("fallback_source")
        if fallback and not source.exists() and (project_root / fallback).exists():
            source = project_root / fallback
        files.append({**item, "source": source})
    return files


def rendered_artifact(project_root: Path) -> tuple[dict[str, Any] | None, list[str]]:
    pdf = project_root / "Submissions/cgss_social_capital_happiness/paper.pdf"
    html = project_root / "Submissions/cgss_social_capital_happiness/paper.html"
    if pdf.exists():
        return (
            {
                "source": pdf,
                "target": "paper.pdf",
                "kind": "real_run",
                "required": True,
            },
            [],
        )
    if html.exists():
        return (
            {
                "source": html,
                "target": "preview.html",
                "kind": "real_run",
                "required": True,
            },
            ["pdf_missing_html_preview_used"],
        )
    return None, ["missing_pdf_and_html_preview"]


def write_cgss_paper_package(
    project_root: Path,
    package: dict[str, Any],
) -> Path:
    package_dir = project_root / package["package_dir"]
    package_dir.mkdir(parents=True, exist_ok=True)
    if package["status"] == "blocked_missing_package_inputs":
        (package_dir / "manifest.json").write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
        return package_dir

    for file in package["files"]:
        target = package_dir / file["target"]
        if file["target"] == "manifest.json":
            continue
        if file["target"] == "reproducibility_readme.md":
            target.write_text(render_reproducibility_readme(package), encoding="utf-8")
            continue
        source = Path(file["source"])
        shutil.copyfile(source, target)
    (package_dir / "manifest.json").write_text(json.dumps(package, ensure_ascii=False, indent=2), encoding="utf-8")
    return package_dir


def render_reproducibility_readme(package: dict[str, Any]) -> str:
    lines = [
        "# CGSS Paper Package Reproducibility README",
        "",
        "## Scope",
        "- Topic: 社会资本对居民主观幸福感的影响研究--基于 CGSS 数据的实证分析",
        "- Package status: `needs_human_paper_package_review`",
        "- Draft layer only: `true`",
        "- Formal writeback allowed: `false`",
        "",
        "## Real Run Artifacts",
    ]
    for artifact in package.get("real_run_artifacts", []):
        lines.append(f"- `{artifact}`")
    lines.extend(["", "## Draft Layer Artifacts"])
    for artifact in package.get("draft_layer_artifacts", []):
        lines.append(f"- `{artifact}`")
    lines.extend(["", "## Human Review Required"])
    for artifact in package.get("human_review_required", []):
        lines.append(f"- `{artifact}`")
    lines.extend(
        [
            "",
            "## Rebuild Commands",
            "- `python3 Program/cgss_exploratory_paper_assembler.py`",
            "- `python3 Program/cgss_pdf_preflight.py`",
            "- `python3 Program/cgss_method_gate.py --profile aer_like`",
            "- `python3 Program/cgss_reviewer_revision_loop.py`",
            "- `python3 Program/cgss_paper_package_builder.py`",
            "",
            "## Boundary",
            "This package is for human acceptance review. It does not promote any content into the formal manuscript, formal bibliography, or product state.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"
