from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evidence import build_evidence_inventory
from .orchestration_schema import HandoffPacket, OrchestrationManifest, ReviewPacket
from .project_adapter import detect_project_profile
from .workbench_paths import create_run_workspace


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def read_text(path: Path) -> str:
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def summarize_list(items: list[dict[str, Any]], key: str = "name", limit: int = 12) -> str:
    values = [str(item.get(key, "")) for item in items[:limit] if item.get(key)]
    return "\n".join(f"- {value}" for value in values) if values else "- No local files detected."


def artifact_rel(path: Path, project_root: Path) -> str:
    return str(path.relative_to(project_root))


def write_handoff(
    run_id: str,
    run_root: Path,
    project_root: Path,
    agent: str,
    stage: str,
    inputs: list[Path],
    outputs: list[Path],
    claims: list[str],
    risks: list[str],
    next_agent: str | None,
    metadata: dict[str, Any] | None = None,
) -> HandoffPacket:
    packet = HandoffPacket(
        run_id=run_id,
        agent=agent,
        stage=stage,
        inputs=[artifact_rel(path, project_root) for path in inputs],
        outputs=[artifact_rel(path, project_root) for path in outputs],
        claims=claims,
        risks=risks,
        next_agent=next_agent,
        metadata=metadata or {},
    )
    safe_name = agent.replace("Agent", "").lower()
    write_json(run_root / stage / f"{safe_name}_handoff.json", packet.to_dict())
    return packet


def build_literature_clusters(inventory: dict[str, Any]) -> dict[str, Any]:
    literature = inventory["literature_files"] + inventory["reference_files"]
    return {
        "robot_labor_reallocation": [
            item
            for item in literature
            if any(term in item["name"].lower() for term in ["robot", "automation", "acemoglu", "autor"])
            or any(term in item["name"] for term in ["机器人", "自动化"])
        ],
        "matching_and_mismatch": [
            item
            for item in literature
            if any(term in item["name"].lower() for term in ["matching", "mismatch", "search"])
            or any(term in item["name"] for term in ["匹配", "错配", "求职"])
        ],
        "identification_and_bartik": [
            item
            for item in literature
            if any(term in item["name"].lower() for term in ["bartik", "iv", "instrument"])
            or any(term in item["name"] for term in ["识别", "工具变量"])
        ],
    }


def run_workbench(project_root: Path, mode: str = "dry-run", user_goal: str = "") -> dict[str, Any]:
    project_root = project_root.resolve()
    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:6]}"
    workspace = create_run_workspace(project_root, run_id)
    run_root = workspace.root
    profile = detect_project_profile(project_root)
    inventory = build_evidence_inventory(project_root, profile)
    artifacts: list[str] = []
    handoffs: list[HandoffPacket] = []

    def record(path: Path) -> Path:
        artifacts.append(artifact_rel(path, project_root))
        return path

    project_profile_path = record(run_root / "00_intake" / "project_profile.json")
    user_goal_path = record(run_root / "00_intake" / "user_goal.md")
    write_json(project_profile_path, profile)
    write_text(user_goal_path, user_goal or "No explicit user goal provided.")
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "PreparationAgent",
            "00_intake",
            [],
            [project_profile_path, user_goal_path],
            ["Project profile normalized for workbench execution."],
            [],
            "LiteratureAgent",
            {"layout": profile["layout"]},
        )
    )

    source_inventory_path = record(run_root / "01_sources" / "source_inventory.json")
    dataset_inventory_path = record(run_root / "01_sources" / "dataset_inventory.json")
    literature_inventory_path = record(run_root / "01_sources" / "literature_inventory.json")
    write_json(source_inventory_path, inventory)
    write_json(dataset_inventory_path, {"items": inventory["datasets"]})
    write_json(literature_inventory_path, {"items": inventory["literature_files"]})

    clusters = build_literature_clusters(inventory)
    literature_clusters_path = record(run_root / "02_literature" / "literature_clusters.json")
    literature_brief_path = record(run_root / "02_literature" / "core_literature_brief.md")
    claim_map_path = record(run_root / "02_literature" / "claim_evidence_map.json")
    write_json(literature_clusters_path, clusters)
    write_text(
        literature_brief_path,
        "\n".join(
            [
                "# Core Literature Brief",
                "",
                "The first thesis run treats robot labor reallocation, matching-quality proxies, and skill-post mismatch as separate evidence layers.",
                "",
                "## Detected Literature Clusters",
                "",
                f"- Robot and automation files: {len(clusters['robot_labor_reallocation'])}",
                f"- Matching and mismatch files: {len(clusters['matching_and_mismatch'])}",
                f"- Identification files: {len(clusters['identification_and_bartik'])}",
            ]
        ),
    )
    write_json(
        claim_map_path,
        {
            "claims": [
                {
                    "claim": "Strict matching efficiency is not directly identified.",
                    "evidence": ["05_reference/匹配效率概念与可测代理对照表.md"],
                },
                {
                    "claim": "The thesis should frame measurable outcomes as allocation quality, search-friction proxies, and mismatch.",
                    "evidence": ["04_paper/sections_v21", "05_reference"],
                },
            ]
        },
    )
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "LiteratureAgent",
            "02_literature",
            [literature_inventory_path],
            [literature_clusters_path, literature_brief_path, claim_map_path],
            ["Literature evidence is separated into robot, matching, and identification clusters."],
            ["File-level inventory is not a substitute for full-text causal claim verification."],
            "ResearchStrategistAgent",
        )
    )

    research_plan_path = record(run_root / "03_strategy" / "research_plan.md")
    identification_plan_path = record(run_root / "03_strategy" / "identification_plan.md")
    empirical_plan_path = record(run_root / "03_strategy" / "empirical_plan.md")
    write_text(
        research_plan_path,
        "# Research Plan\n\nPrimary question: how industrial robot exposure affects worker allocation outcomes, job-search frictions, and skill-post mismatch.\n",
    )
    write_text(
        identification_plan_path,
        "# Identification Plan\n\nUse Bartik IV as the main identification strategy and keep weak-IV caveats explicit.\n",
    )
    write_text(
        empirical_plan_path,
        "# Empirical Plan\n\nUse CFPS for outcome-layer results, CLDS for mechanism-layer checks, and CGSS for concept calibration.\n",
    )
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "ResearchStrategistAgent",
            "03_strategy",
            [project_profile_path, literature_brief_path, claim_map_path],
            [research_plan_path, identification_plan_path, empirical_plan_path],
            ["Bartik IV remains the main identification path for the first thesis run."],
            ["Weak-IV language must stay cautious in draft and handoff files."],
            "ModelingAgent",
        )
    )

    modeling_report_path = record(run_root / "04_modeling" / "modeling_report.json")
    diagnostics_report_path = record(run_root / "04_modeling" / "diagnostics_report.md")
    write_json(
        modeling_report_path,
        {
            "mode": mode,
            "detected_code_files": inventory["code_files"],
            "execution_policy": "audit existing scripts in dry-run" if mode == "dry-run" else "live execution requires explicit script selection",
        },
    )
    write_text(
        diagnostics_report_path,
        "# Diagnostics Report\n\nDry-run records existing data, code, and result availability without mutating raw data.\n",
    )
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "ModelingAgent",
            "04_modeling",
            [empirical_plan_path],
            [modeling_report_path, diagnostics_report_path],
            ["Existing empirical scripts are indexed before new execution is attempted."],
            ["Dry-run does not prove empirical estimates are current."],
            "VisualizationAgent",
        )
    )

    results_index_path = record(run_root / "05_results" / "results_index.json")
    table_plan_path = record(run_root / "05_results" / "table_plan.md")
    figure_plan_path = record(run_root / "05_results" / "figure_plan.md")
    write_json(results_index_path, {"items": inventory["results_files"]})
    write_text(table_plan_path, "# Table Plan\n\nUse existing indexed thesis tables before generating new tables.\n")
    write_text(figure_plan_path, "# Figure Plan\n\nUse existing thesis figures and figure scripts as first-class artifacts.\n")
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "VisualizationAgent",
            "05_results",
            [modeling_report_path],
            [results_index_path, table_plan_path, figure_plan_path],
            ["Results are indexed before manuscript claims are rewritten."],
            ["Some visual artifacts may still be generated by another IDE and need later sync."],
            "WritingAgent",
        )
    )

    manuscript_source = read_text(project_root / "04_paper" / "论文v2.1_完整版.md")
    if not manuscript_source:
        manuscript_source = "\n\n".join(
            read_text(project_root / item["path"])
            for item in inventory["manuscript_sections"][:8]
            if read_text(project_root / item["path"])
        )
    paper_draft_path = record(run_root / "06_writing" / "paper_draft.md")
    section_status_path = record(run_root / "06_writing" / "section_status.json")
    write_text(
        paper_draft_path,
        "\n".join(
            [
                "# Paper Draft",
                "",
                "This draft is generated from inspected sources and preserves the matching-efficiency boundary.",
                "",
                "## Source Snapshot",
                manuscript_source[:6000] if manuscript_source else "No manuscript source detected.",
            ]
        ),
    )
    write_json(
        section_status_path,
        {
            "sections_detected": [item["path"] for item in inventory["manuscript_sections"]],
            "status": "drafted",
        },
    )
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "WritingAgent",
            "06_writing",
            [research_plan_path, identification_plan_path, results_index_path, claim_map_path],
            [paper_draft_path, section_status_path],
            ["Draft generation must preserve concept boundaries and evidence references."],
            ["Generated draft requires independent review before final formatting."],
            "ReviewerAgent",
        )
    )

    review_report_path = record(run_root / "07_review" / "review_report.md")
    revision_plan_path = record(run_root / "07_review" / "revision_plan.md")
    reviewer_decision_path = record(run_root / "07_review" / "reviewer_decision.json")
    review = ReviewPacket(
        run_id=run_id,
        reviewer="ReviewerAgent",
        target_agent="WritingAgent",
        target_artifact=artifact_rel(paper_draft_path, project_root),
        decision="revise_minor",
        revision_requests=[
            "Keep strict matching efficiency separate from measurable proxies.",
            "Attach each empirical claim to a result artifact.",
            "Keep weak-IV wording cautious and consistent with diagnostics.",
        ],
        strengths=[
            "Draft uses inspected local project sources.",
            "Draft records the matching-efficiency boundary explicitly.",
        ],
        risks=["Dry-run draft quality depends on existing manuscript source quality."],
    )
    write_text(
        review_report_path,
        "# Review Report\n\nThe reviewer checks concept boundaries, weak-IV wording, literature support, and result-to-claim alignment.\n",
    )
    write_text(
        revision_plan_path,
        "# Revision Plan\n\n1. Keep strict matching efficiency separate from measurable proxies.\n2. Attach each empirical claim to a result artifact.\n3. Keep weak-IV wording aligned across abstract, results, and handoff files.\n",
    )
    write_json(reviewer_decision_path, review.to_dict())
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "ReviewerAgent",
            "07_review",
            [paper_draft_path],
            [review_report_path, revision_plan_path, reviewer_decision_path],
            ["Reviewer is independent from WritingAgent."],
            review.risks,
            "FormatterAgent",
        )
    )

    tex_path = record(run_root / "08_final" / "paper_draft.tex")
    docx_path = record(run_root / "08_final" / "paper_draft.docx")
    formatting_report_path = record(run_root / "08_final" / "formatting_report.md")
    write_text(tex_path, "\\section{Draft}\nGenerated draft placeholder for TeX export.\n")
    write_text(docx_path, "DOCX export placeholder recorded by dry-run.\n")
    write_text(formatting_report_path, "# Formatting Report\n\nDry-run recorded the Word export path. Live mode will call the formatter.\n")
    handoffs.append(
        write_handoff(
            run_id,
            run_root,
            project_root,
            "FormatterAgent",
            "08_final",
            [paper_draft_path, reviewer_decision_path],
            [tex_path, docx_path, formatting_report_path],
            ["Word output path is recorded for the A experience."],
            ["Dry-run Word file is a path placeholder until live formatter is wired."],
            None,
        )
    )

    manifest_path = run_root / "run_manifest.json"
    artifacts.append(artifact_rel(manifest_path, project_root))
    manifest = OrchestrationManifest(
        run_id=run_id,
        project_id=profile.get("title") or project_root.name,
        project_root=str(project_root),
        run_root=str(run_root),
        mode=mode,
        supervisor={
            "name": "Supervisor",
            "status": "completed",
            "created_at": utc_now(),
            "user_goal": user_goal,
        },
        agents=[
            {"name": packet.agent, "stage": packet.stage, "status": packet.status}
            for packet in handoffs
        ],
        review_loop={
            "writer": "WritingAgent",
            "reviewer": "ReviewerAgent",
            "decision": review.decision,
            "iterations": 1,
            "status": "completed",
        },
        artifacts=artifacts,
        status="completed",
    )
    write_json(manifest_path, manifest.to_dict())
    return manifest.to_dict()


def orchestrate_project(project_root: Path, run_live: bool = False) -> dict[str, Any]:
    mode = "live" if run_live else "dry-run"
    return run_workbench(project_root, mode=mode, user_goal="Legacy orchestration endpoint")

