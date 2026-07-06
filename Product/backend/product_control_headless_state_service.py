from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Product.backend.product_control_phase_service import project_summary
from Product.backend.registry import get_project_by_id


SCHEMA_VERSION = "product_control_headless_state.v1"
P13_PATH = Path("Results/json/parent_education_wage_p13_run_plan_approval.json")
P14_PATH = Path("Results/json/parent_education_wage_p14_execution_evidence_ledger.json")
P15_PATH = Path("Results/json/parent_education_wage_p15_draft_export_package.json")
P16_PATH = Path("Results/json/parent_education_wage_p16_user_acceptance_packet.json")
P17_PATH = Path("Results/json/parent_education_wage_p17_data_repair_preflight.json")
P18_PATH = Path("Results/json/parent_education_wage_p18_data_repair_apply.json")
DELIVERY_MANIFEST_PATH = Path("Submissions/parent_education_wage_delivery_manifest.json")
DELIVERY_README_PATH = Path("Submissions/parent_education_wage_delivery_README.md")
DELIVERY_ZIP_PATH = Path("Submissions/parent_education_wage_delivery_package.zip")
FINAL_PDF_REPORT_PATH = Path("Results/json/parent_education_wage_final_pdf_export.json")
FINAL_PDF_REVIEW_PATH = Path("Reviews/parent_education_wage_final_pdf_export.md")
FINAL_PDF_PATH = Path("Submissions/parent_education_wage_final_paper.pdf")
FINAL_HTML_PATH = Path("Submissions/parent_education_wage_final_paper.html")
COURSE_PAPER_QUALITY_PATH = Path("Results/json/course_paper_quality_report.json")


DEFAULT_ARTIFACT_PATHS = {
    "p13": P13_PATH,
    "p14": P14_PATH,
    "p15": P15_PATH,
    "p16": P16_PATH,
    "p17": P17_PATH,
    "p18": P18_PATH,
    "delivery": DELIVERY_MANIFEST_PATH,
    "final_pdf": FINAL_PDF_REPORT_PATH,
    "course_paper_quality": COURSE_PAPER_QUALITY_PATH,
}


def get_project_product_control_headless_state(
    product_root: Path,
    repo_root: Path,
    project_id: str,
) -> dict[str, Any]:
    project = get_project_by_id(product_root, repo_root, project_id)
    project_root = Path(project.get("project_root") or project["root"]).resolve()
    paths = artifact_paths_for_project(project)
    artifacts = {
        key: load_optional_json(project_root / path)
        for key, path in paths.items()
    }
    components = [
        data_repair_component(artifacts, paths),
        execution_run_component(artifacts, paths),
        draft_package_component(artifacts, paths),
        delivery_package_component(artifacts, paths),
        final_pdf_component(artifacts, paths),
        course_paper_quality_component(artifacts, paths),
        review_export_component(artifacts, paths),
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now(),
        "project": project_summary(project, project_root),
        "status": overall_status(artifacts),
        "user_summary": overall_summary(artifacts),
        "primary_action": overall_primary_action(artifacts),
        "components": components,
        "artifacts": artifact_index(artifacts, paths),
        "audit": [
            {
                "source": "local_artifacts",
                "note": "Headless state only summarizes existing files; it does not run stages or write artifacts.",
            }
        ],
    }


def artifact_paths_for_project(project: dict[str, Any]) -> dict[str, Path]:
    prefix = project.get("artifact_prefix")
    paths = dict(DEFAULT_ARTIFACT_PATHS)
    if prefix:
        paths.update(
            {
                "p13": Path(f"Results/json/{prefix}_run_plan_seed_approved.json"),
                "p14": Path(f"Results/json/{prefix}_results_evidence_package.json"),
                "p15": Path(f"Results/json/{prefix}_paper_assembly.json"),
                "p16": Path(f"Results/json/{prefix}_revision_task_queue.json"),
                "p17": Path(f"Results/json/{prefix}_data_discovery.json"),
                "p18": Path(f"Results/json/{prefix}_dataset_bound_variable_role_draft.json"),
                "delivery": Path(f"Submissions/{prefix}/manifest.json"),
                "final_pdf": Path(f"Results/json/{prefix}_pdf_preflight.json"),
                "course_paper_quality": Path(f"Results/json/{prefix}_course_paper_quality_report.json"),
            }
        )
    return paths


def data_repair_component(artifacts: dict[str, dict[str, Any] | None], paths: dict[str, Path]) -> dict[str, Any]:
    p18 = artifacts["p18"] or {}
    p17 = artifacts["p17"] or {}
    if p18.get("status") == "data_repair_applied_ready_for_p13_p16":
        status = "completed"
        summary = f"修复数据已生成：{p18.get('repaired_dataset_path')}。"
        primary_action = {"id": "rerun_p13_p16", "label": "重新运行 P13-P16", "enabled": True}
        blockers: list[dict[str, Any]] = []
    elif p17.get("status") == "data_repair_preflight_ready_for_review":
        status = "waiting_review"
        summary = "已找到数据修复候选，等待确认后写入 Data/Interim。"
        primary_action = {"id": "apply_data_repair", "label": "确认并应用修复", "enabled": True}
        blockers = []
    else:
        status = "blocked"
        summary = "还没有可应用的数据修复候选。"
        primary_action = {"id": "run_p17_preflight", "label": "生成修复候选", "enabled": True}
        blockers = [{"id": "missing_p17", "message": "缺少 P17 数据修复预检。"}]
    return component(
        "data_repair",
        "数据修复",
        status,
        summary,
        primary_action,
        blockers,
        [paths["p17"], paths["p18"]],
    )


def execution_run_component(artifacts: dict[str, dict[str, Any] | None], paths: dict[str, Path]) -> dict[str, Any]:
    p14 = artifacts["p14"] or {}
    p13 = artifacts["p13"] or {}
    if p14.get("executed_regression") is True:
        status = "completed"
        summary = f"模型已执行，run id：{p14.get('run_id')}。"
        primary_action = {"id": "review_model_result", "label": "审阅模型结果", "enabled": True}
        blockers: list[dict[str, Any]] = []
    elif p13.get("missing_dataset_columns"):
        status = "blocked"
        missing = ", ".join(p13.get("missing_dataset_columns") or [])
        summary = f"模型未执行，缺少字段：{missing}。"
        primary_action = {"id": "repair_data", "label": "修复数据", "enabled": True}
        blockers = [{"id": "missing_dataset_columns", "message": missing}]
    else:
        status = "not_started"
        summary = "模型执行尚未开始。"
        primary_action = {"id": "run_p13_p16", "label": "运行 P13-P16", "enabled": True}
        blockers = []
    return component(
        "execution_run",
        "模型执行",
        status,
        summary,
        primary_action,
        blockers,
        [paths["p13"], paths["p14"]],
    )


def draft_package_component(artifacts: dict[str, dict[str, Any] | None], paths: dict[str, Path]) -> dict[str, Any]:
    p15 = artifacts["p15"] or {}
    if p15.get("can_export_complete_paper") is True:
        status = "completed"
        summary = f"完整初稿已生成：{p15.get('paper_draft_docx')}。"
        primary_action = {"id": "open_draft_package", "label": "查看初稿包", "enabled": True}
        blockers: list[dict[str, Any]] = []
    elif p15.get("paper_path"):
        status = "waiting_review"
        summary = f"论文草稿已组装：{p15.get('paper_path')}。"
        primary_action = {"id": "human_review_paper_draft", "label": "人工审阅论文草稿", "enabled": True}
        blockers = []
    elif p15.get("red_flag_issues"):
        status = "blocked"
        summary = "只能交付半成品论文和红标问题清单。"
        primary_action = {"id": "review_issues", "label": "查看问题清单", "enabled": True}
        blockers = [{"id": issue.get("id"), "message": issue.get("title")} for issue in p15.get("red_flag_issues", [])]
    else:
        status = "not_started"
        summary = "论文初稿包尚未生成。"
        primary_action = {"id": "run_p13_p16", "label": "运行 P13-P16", "enabled": True}
        blockers = []
    return component(
        "draft_package",
        "论文初稿",
        status,
        summary,
        primary_action,
        blockers,
        [paths["p15"]],
    )


def review_export_component(artifacts: dict[str, dict[str, Any] | None], paths: dict[str, Path]) -> dict[str, Any]:
    p16 = artifacts["p16"] or {}
    if p16.get("can_claim_complete_paper") is True:
        status = "waiting_review"
        summary = "完整初稿可审阅；仍需人工确认后才能进入投稿格式和 PDF 导出。"
        primary_action = {"id": "human_review_complete_draft", "label": "人工审阅完整初稿", "enabled": True}
        blockers: list[dict[str, Any]] = []
    elif p16.get("status") == "needs_human_revision_queue_approval":
        status = "waiting_review"
        summary = "修订队列已生成，等待人工确认后进入下一轮论文修订。"
        primary_action = {"id": "approve_revision_queue", "label": "审阅修订队列", "enabled": True}
        blockers = [{"id": item, "message": item} for item in p16.get("blocking_reasons", [])]
    elif p16.get("can_accept_blocked_package") is True:
        status = "blocked_package_ready"
        summary = "半成品交付包可验收，但不能声称完整论文。"
        primary_action = {"id": "accept_blocked_package", "label": "验收半成品包", "enabled": True}
        blockers = []
    else:
        status = "not_started"
        summary = "验收包尚未生成。"
        primary_action = {"id": "run_p13_p16", "label": "生成验收包", "enabled": True}
        blockers = []
    return component(
        "review_export",
        "审阅与导出",
        status,
        summary,
        primary_action,
        blockers,
        [paths["p16"]],
    )


def delivery_package_component(artifacts: dict[str, dict[str, Any] | None], paths: dict[str, Path]) -> dict[str, Any]:
    delivery = artifacts["delivery"] or {}
    p16 = artifacts["p16"] or {}
    evidence_paths = [paths["delivery"]]
    if paths["delivery"] == DELIVERY_MANIFEST_PATH:
        evidence_paths.extend([DELIVERY_README_PATH, DELIVERY_ZIP_PATH])
    else:
        append_payload_path(evidence_paths, delivery, "delivery_zip")
        append_payload_path(evidence_paths, delivery, "readme_path")
    if delivery.get("status") == "delivery_package_ready_for_human_review":
        status = "completed"
        summary = f"可审阅交付包已生成：{delivery.get('delivery_zip')}。"
        primary_action = {"id": "open_delivery_package", "label": "查看交付包", "enabled": True}
        blockers: list[dict[str, Any]] = []
    elif p16.get("can_claim_complete_paper") is True:
        status = "ready"
        summary = "完整初稿已就绪，可以生成交付包。"
        primary_action = {"id": "generate_delivery_package", "label": "生成交付包", "enabled": True}
        blockers = []
    else:
        status = "blocked"
        summary = "完整初稿尚未就绪，不能生成交付包。"
        primary_action = {"id": "complete_p13_p16", "label": "完成 P13-P16", "enabled": True}
        blockers = [{"id": "missing_complete_draft", "message": "缺少可交付完整初稿。"}]
    return component(
        "delivery_package",
        "交付包",
        status,
        summary,
        primary_action,
        blockers,
        evidence_paths,
    )


def final_pdf_component(artifacts: dict[str, dict[str, Any] | None], paths: dict[str, Path]) -> dict[str, Any]:
    final_pdf = artifacts["final_pdf"] or {}
    p16 = artifacts["p16"] or {}
    nested_pdf = final_pdf.get("pdf") if isinstance(final_pdf.get("pdf"), dict) else {}
    nested_html = final_pdf.get("html") if isinstance(final_pdf.get("html"), dict) else {}
    pdf_path = final_pdf.get("final_pdf") or nested_pdf.get("path")
    evidence_paths = [paths["final_pdf"]]
    if paths["final_pdf"] == FINAL_PDF_REPORT_PATH:
        evidence_paths.extend([FINAL_PDF_REVIEW_PATH, FINAL_HTML_PATH, FINAL_PDF_PATH])
    else:
        append_raw_path(evidence_paths, pdf_path)
        append_raw_path(evidence_paths, nested_html.get("path"))
    if final_pdf.get("status") == "final_pdf_ready" or (
        final_pdf.get("status") == "pdf_preflight_ready" and nested_pdf.get("exists") is True
    ):
        status = "completed"
        summary = f"PDF 导出样稿已生成：{pdf_path}；论文审阅尚未完成。"
        primary_action = {"id": "open_pdf_export_smoke", "label": "打开 PDF 样稿", "enabled": True}
        blockers: list[dict[str, Any]] = [
            {"id": "course_paper_quality_gate_missing", "message": "缺少论文审阅报告。"}
        ]
    elif p16.get("can_claim_complete_paper") is True:
        status = "ready"
        summary = "完整初稿已就绪，可以生成最终 PDF。"
        primary_action = {"id": "generate_final_pdf", "label": "生成最终 PDF", "enabled": True}
        blockers = []
    else:
        status = "blocked"
        summary = "完整初稿尚未就绪，不能生成最终 PDF。"
        primary_action = {"id": "complete_p13_p16", "label": "完成 P13-P16", "enabled": True}
        blockers = [{"id": "missing_complete_draft", "message": "缺少可导出 PDF 的完整初稿。"}]
    return component(
        "final_pdf",
        "最终 PDF",
        status,
        summary,
        primary_action,
        blockers,
        evidence_paths,
    )


def course_paper_quality_component(artifacts: dict[str, dict[str, Any] | None], paths: dict[str, Path]) -> dict[str, Any]:
    quality = artifacts["course_paper_quality"] or {}
    final_pdf = artifacts["final_pdf"] or {}
    verdict = quality.get("verdict") or []
    review_summary = quality.get("review_summary") if isinstance(quality.get("review_summary"), dict) else {}
    review_decision = review_summary.get("decision")
    if verdict == ["ready_for_review"] and review_decision != "needs_revision":
        status = "completed"
        summary = str(review_summary.get("headline") or "论文审阅已完成，可以进入人工终审。")
        primary_action = {"id": "human_review_course_paper", "label": "人工终审论文", "enabled": True}
        blockers: list[dict[str, Any]] = []
    elif quality:
        status = "needs_revision"
        summary = str(review_summary.get("headline") or "论文还需要修订。")
        primary_action = {"id": "route_quality_revisions", "label": "生成修订队列", "enabled": True}
        priorities = review_summary.get("top_priorities") if isinstance(review_summary.get("top_priorities"), list) else []
        blockers = [
            {
                "id": str(priority.get("id") or index),
                "message": f"{priority.get('title')}：{priority.get('detail')}",
            }
            for index, priority in enumerate(priorities)
            if isinstance(priority, dict)
        ]
        if not blockers:
            blockers = [{"id": item, "message": item} for item in verdict]
    elif final_pdf.get("status") in {"final_pdf_ready", "pdf_preflight_ready"}:
        status = "blocked"
        summary = "PDF 已生成，但还没有生成论文审阅报告。"
        primary_action = {"id": "run_course_paper_review_report", "label": "生成论文审阅报告", "enabled": True}
        blockers = [{"id": "review_report_not_run", "message": "缺少论文审阅报告。"}]
    else:
        status = "not_started"
        summary = "最终 PDF 尚未生成，还不能生成论文审阅报告。"
        primary_action = {"id": "generate_final_pdf", "label": "先生成 PDF", "enabled": True}
        blockers = [{"id": "missing_final_pdf", "message": "缺少当前论文 PDF 样稿。"}]
    payload = component(
        "course_paper_quality",
        "论文审阅",
        status,
        summary,
        primary_action,
        blockers,
        [paths["course_paper_quality"]],
    )
    payload["quality_report_path"] = paths["course_paper_quality"].as_posix()
    if review_summary:
        payload["review_summary"] = review_summary
        top_priorities = review_summary.get("top_priorities")
        payload["top_priorities"] = top_priorities if isinstance(top_priorities, list) else []
    return payload


def component(
    component_id: str,
    label: str,
    status: str,
    user_summary: str,
    primary_action: dict[str, Any],
    blockers: list[dict[str, Any]],
    paths: list[Path],
) -> dict[str, Any]:
    return {
        "component_id": component_id,
        "label": label,
        "status": status,
        "user_summary": user_summary,
        "primary_action": primary_action,
        "actions": [primary_action],
        "blockers": blockers,
        "artifacts": [{"path": path.as_posix()} for path in paths],
        "evidence": [{"path": path.as_posix()} for path in paths],
        "audit": [],
    }


def append_payload_path(paths: list[Path], payload: dict[str, Any], key: str) -> None:
    append_raw_path(paths, payload.get(key))


def append_raw_path(paths: list[Path], value: Any) -> None:
    if isinstance(value, str) and value:
        path = Path(value)
        if path not in paths:
            paths.append(path)


def overall_status(artifacts: dict[str, dict[str, Any] | None]) -> str:
    final_pdf = artifacts["final_pdf"] or {}
    delivery = artifacts["delivery"] or {}
    p16 = artifacts["p16"] or {}
    p18 = artifacts["p18"] or {}
    if final_pdf.get("status") in {"final_pdf_ready", "pdf_preflight_ready"}:
        if (artifacts["course_paper_quality"] or {}).get("verdict") == ["ready_for_review"]:
            return "course_paper_ready_for_human_review"
        return "pdf_export_smoke_ready"
    if delivery.get("status") == "delivery_package_ready_for_human_review":
        return "delivery_package_ready_for_human_review"
    if p16.get("can_claim_complete_paper") is True:
        return "complete_draft_ready_for_human_review"
    if p16.get("can_accept_blocked_package") is True:
        return "blocked_package_ready"
    if p18.get("status") == "data_repair_applied_ready_for_p13_p16":
        return "data_repaired_ready_for_execution"
    return "in_progress"


def overall_summary(artifacts: dict[str, dict[str, Any] | None]) -> str:
    status = overall_status(artifacts)
    if status == "course_paper_ready_for_human_review":
        return "PDF 和论文审阅已完成，等待人工终审。"
    if status == "pdf_export_smoke_ready":
        return "PDF 导出样稿已生成，但论文审阅尚未完成。"
    if status == "delivery_package_ready_for_human_review":
        return "完整初稿、数据修复、模型证据和验收材料已打包，等待人工审阅。"
    if status == "complete_draft_ready_for_human_review":
        return "完整论文初稿和真实模型结果已生成，等待人工审阅。"
    if status == "blocked_package_ready":
        return "当前可交付半成品论文和红标问题清单。"
    if status == "data_repaired_ready_for_execution":
        return "数据已修复，下一步重新运行 P13-P16。"
    return "产品流程仍在推进中。"


def overall_primary_action(artifacts: dict[str, dict[str, Any] | None]) -> dict[str, Any]:
    status = overall_status(artifacts)
    if status == "course_paper_ready_for_human_review":
        return {"id": "human_review_course_paper", "label": "人工终审论文", "enabled": True}
    if status == "pdf_export_smoke_ready":
        return {"id": "run_course_paper_quality_gate", "label": "生成论文审阅报告", "enabled": True}
    if status == "delivery_package_ready_for_human_review":
        return {"id": "open_delivery_package", "label": "查看交付包", "enabled": True}
    if status == "complete_draft_ready_for_human_review":
        return {"id": "human_review_complete_draft", "label": "人工审阅完整初稿", "enabled": True}
    if status == "data_repaired_ready_for_execution":
        return {"id": "rerun_p13_p16", "label": "重新运行 P13-P16", "enabled": True}
    return {"id": "continue_current_gate", "label": "继续当前门禁", "enabled": True}


def artifact_index(
    artifacts: dict[str, dict[str, Any] | None],
    paths: dict[str, Path],
) -> list[dict[str, Any]]:
    return [
        {"id": key, "path": paths[key].as_posix(), "exists": payload is not None}
        for key, payload in artifacts.items()
    ]


def load_optional_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def now() -> str:
    return datetime.now(timezone.utc).isoformat()
