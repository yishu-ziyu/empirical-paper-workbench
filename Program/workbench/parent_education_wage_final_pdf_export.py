from __future__ import annotations

import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import markdown
from weasyprint import HTML


SCHEMA_VERSION = "parent_education_wage_final_pdf_export.v1"
TOPIC = "父母受教育水平对子女工资收入的影响"

P16_PATH = Path("Results/json/parent_education_wage_p16_user_acceptance_packet.json")
P14_PATH = Path("Results/json/parent_education_wage_p14_execution_evidence_ledger.json")
DRAFT_MARKDOWN_PATH = Path("Manuscripts/generated/parent_education_wage_complete_paper_draft.md")
FINAL_PDF_PATH = Path("Submissions/parent_education_wage_final_paper.pdf")
FINAL_HTML_PATH = Path("Submissions/parent_education_wage_final_paper.html")
REPORT_PATH = Path("Results/json/parent_education_wage_final_pdf_export.json")
REVIEW_PATH = Path("Reviews/parent_education_wage_final_pdf_export.md")


def run_parent_education_wage_final_pdf_export(project_root: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    report = build_parent_education_wage_final_pdf_export(project_root, write_pdf=True)
    write_json(project_root / REPORT_PATH, report)
    write_text(project_root / REVIEW_PATH, render_review(report))
    return report


def get_parent_education_wage_final_pdf_export(project_root: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    report_path = project_root / REPORT_PATH
    if report_path.exists():
        payload = load_json(report_path)
        payload["artifact_exists"] = (project_root / FINAL_PDF_PATH).exists()
        return payload
    return build_parent_education_wage_final_pdf_export(project_root, write_pdf=False)


def build_parent_education_wage_final_pdf_export(project_root: Path, write_pdf: bool) -> dict[str, Any]:
    p16_path = project_root / P16_PATH
    if not p16_path.exists():
        return blocked_packet("blocked_missing_p16_acceptance_packet", ["missing_p16_acceptance_packet"])
    p16 = load_json(p16_path)
    if p16.get("can_claim_complete_paper") is not True:
        return blocked_packet("blocked_complete_draft_not_ready", ["p16_can_claim_complete_paper_false"])

    draft_path = project_root / DRAFT_MARKDOWN_PATH
    if not draft_path.exists():
        return blocked_packet("blocked_missing_complete_draft_markdown", ["missing_complete_draft_markdown"])

    p14 = load_optional_json(project_root / P14_PATH) or {}
    markdown_text = draft_path.read_text(encoding="utf-8")
    html_text = render_html(markdown_text, p14)
    if not write_pdf:
        return ready_packet(
            status="final_pdf_ready_to_generate",
            artifact_exists=False,
            p14=p14,
        )

    html_path = project_root / FINAL_HTML_PATH
    pdf_path = project_root / FINAL_PDF_PATH
    write_text(html_path, html_text)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_text, base_url=str(project_root)).write_pdf(str(pdf_path))

    return {
        **ready_packet(
            status="final_pdf_ready",
            artifact_exists=True,
            p14=p14,
        ),
        "final_html": FINAL_HTML_PATH.as_posix(),
        "final_pdf": FINAL_PDF_PATH.as_posix(),
        "final_pdf_size": pdf_path.stat().st_size,
        "final_pdf_sha256": sha256(pdf_path),
    }


def ready_packet(status: str, artifact_exists: bool, p14: dict[str, Any]) -> dict[str, Any]:
    model_results = p14.get("model_results") or {}
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "topic": TOPIC,
        "stage": "FinalPdfExport",
        "status": status,
        "artifact_exists": artifact_exists,
        "source_markdown": DRAFT_MARKDOWN_PATH.as_posix(),
        "final_html": FINAL_HTML_PATH.as_posix(),
        "final_pdf": FINAL_PDF_PATH.as_posix(),
        "final_pdf_size": 0,
        "final_pdf_sha256": None,
        "can_claim_final_pdf_ready": status == "final_pdf_ready",
        "can_claim_submission_ready": False,
        "paper_quality_status": "pdf_export_smoke_only",
        "not_submission_ready_reasons": [
            "missing_literature_review",
            "missing_identification_strategy",
            "missing_robustness_checks",
            "missing_references",
            "missing_claim_audit",
            "missing_reproducibility_gate",
            "draft_too_thin_for_course_paper",
        ],
        "run_id": p14.get("run_id"),
        "model_summary": {
            "status": p14.get("status"),
            "nobs": model_results.get("nobs"),
            "treatment_variable": model_results.get("treatment_variable"),
            "treatment_coefficient": (model_results.get("coefficients") or {}).get("parent_education"),
        },
        "evidence": [
            P16_PATH.as_posix(),
            P14_PATH.as_posix(),
            DRAFT_MARKDOWN_PATH.as_posix(),
        ],
        "blocking_reasons": [],
        "next_action": "open_final_pdf",
    }


def blocked_packet(status: str, blocking_reasons: list[str]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "topic": TOPIC,
        "stage": "FinalPdfExport",
        "status": status,
        "artifact_exists": False,
        "source_markdown": DRAFT_MARKDOWN_PATH.as_posix(),
        "final_html": FINAL_HTML_PATH.as_posix(),
        "final_pdf": FINAL_PDF_PATH.as_posix(),
        "final_pdf_size": 0,
        "final_pdf_sha256": None,
        "can_claim_final_pdf_ready": False,
        "can_claim_submission_ready": False,
        "evidence": [P16_PATH.as_posix(), P14_PATH.as_posix(), DRAFT_MARKDOWN_PATH.as_posix()],
        "blocking_reasons": blocking_reasons,
        "next_action": "complete_p13_p16_before_final_pdf",
    }


def render_html(markdown_text: str, p14: dict[str, Any]) -> str:
    body = markdown.markdown(
        markdown_text,
        extensions=["extra", "tables", "sane_lists"],
        output_format="html5",
    )
    run_id = html.escape(str(p14.get("run_id") or "not-recorded"))
    generated_at = html.escape(now())
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>父母受教育水平如何影响子女的工资水平？</title>
  <style>
    @page {{ size: A4; margin: 24mm 22mm; }}
    body {{
      color: #171717;
      font-family: "PingFang SC", "Songti SC", "Noto Serif CJK SC", "Heiti SC", sans-serif;
      font-size: 11.5pt;
      line-height: 1.72;
    }}
    h1 {{ font-size: 22pt; line-height: 1.25; margin: 0 0 18pt; }}
    h2 {{ font-size: 15pt; margin: 20pt 0 8pt; border-bottom: 0.5pt solid #d6d3d1; padding-bottom: 3pt; }}
    p {{ margin: 0 0 8pt; }}
    ul {{ margin: 0 0 8pt 18pt; padding: 0; }}
    code {{
      font-family: "SFMono-Regular", "Menlo", monospace;
      font-size: 9.5pt;
      background: #f5f5f4;
      padding: 1pt 3pt;
      border-radius: 2pt;
    }}
    .meta {{
      margin-top: 26pt;
      padding-top: 8pt;
      border-top: 0.5pt solid #d6d3d1;
      color: #57534e;
      font-size: 9pt;
    }}
  </style>
</head>
<body>
{body}
<section class="meta">
  <p>PDF generated at: {generated_at}</p>
  <p>Model run id: {run_id}</p>
</section>
</body>
</html>
"""


def render_review(report: dict[str, Any]) -> str:
    lines = [
        "# Parent Education Wage Final PDF Export",
        "",
        f"- Status: `{report.get('status')}`",
        f"- Final PDF: `{report.get('final_pdf')}`",
        f"- PDF size: `{report.get('final_pdf_size')}`",
        f"- PDF sha256: `{report.get('final_pdf_sha256')}`",
        f"- Can claim final PDF ready: `{report.get('can_claim_final_pdf_ready')}`",
        f"- Can claim submission ready: `{report.get('can_claim_submission_ready')}`",
        "",
        "## Evidence",
        "",
    ]
    for item in report.get("evidence", []):
        lines.append(f"- `{item}`")
    if report.get("blocking_reasons"):
        lines.extend(["", "## Blocking Reasons", ""])
        lines.extend(f"- `{item}`" for item in report["blocking_reasons"])
    lines.append("")
    return "\n".join(lines)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return load_json(path)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()
