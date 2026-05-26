from __future__ import annotations

import argparse
from pathlib import Path

from workbench.config import read_yaml, resolve_project_paths
from workbench.drafts import build_draft_context, build_qmd_content, render_template
from workbench.observability import ObservableRun, generate_run_id
from workbench.results import artifact_record, build_results_index
from workbench.state import build_project_state, write_json
from workbench.statspai_runner import run_statspai_paper


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Phase A econ workbench pipeline.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--paper-config",
        default="paper.yaml",
        help="Project-relative or absolute paper configuration file.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Skip analysis execution and only emit artifacts.")
    parser.add_argument("--run-id", default=None, help="Stable run id for observable execution files.")
    return parser.parse_args()


def ensure_directories(paths: dict[str, Path]) -> None:
    for key in ("results_json_dir", "results_logs_dir", "generated_dir", "state_file"):
        target = paths[key]
        if key == "state_file":
            target.parent.mkdir(parents=True, exist_ok=True)
        else:
            target.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def resolve_config_path(project_root: Path, value: str) -> Path:
    configured = Path(value)
    if configured.is_absolute():
        return configured.resolve()
    return (project_root / configured).resolve()


def display_path(path: Path, project_root: Path) -> str:
    try:
        return str(path.relative_to(project_root))
    except ValueError:
        return str(path)


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    mode = "dry-run" if args.dry_run else "live"
    observable = ObservableRun(project_root, args.run_id or generate_run_id(), mode)
    observable.start_run()

    try:
        observable.start_step("config_load")
        paper_config_path = resolve_config_path(project_root, args.paper_config)
        paper_config = read_yaml(paper_config_path)
        analysis_config = read_yaml(project_root / "Program" / "config" / "analysis_config.yaml")
        paths = resolve_project_paths(project_root, paper_config, paper_config_path)
        ensure_directories(paths)
        observable.complete_step(
            "config_load",
            "Project configuration loaded.",
            metadata={
                "paper_config": display_path(paper_config_path, project_root),
                "analysis_config": "Program/config/analysis_config.yaml",
            },
        )

        observable.start_step("dataset_intake", {"dataset_path": str(paths["final_dataset"].relative_to(project_root))})
        dataset_exists = paths["final_dataset"].exists()
        dataset_metadata = {
            "dataset_path": str(paths["final_dataset"].relative_to(project_root)),
            "dataset_exists": dataset_exists,
            "unit_of_analysis": paper_config["data"].get("unit_of_analysis"),
            "sample_definition": paper_config["data"].get("sample_definition"),
            "key_variables": paper_config["data"].get("key_variables", {}),
        }
        observable.complete_step(
            "dataset_intake",
            "Configured dataset was inspected." if dataset_exists else "Configured dataset is missing.",
            metadata=dataset_metadata,
        )
        observable.open_gate(
            "gate_dataset_fields",
            "dataset_intake",
            "Confirm detected dataset fields",
            "The system detected outcome, treatment, and controls from the active paper config. A user can correct them before trusting downstream analysis.",
            "analysis_execution",
            ["accept_detected_fields", "edit_variable_roles", "pause_run"],
            metadata=dataset_metadata,
            blocking=False,
        )

        observable.start_step("topic_confirmation")
        observable.open_gate(
            "gate_research_question",
            "topic_confirmation",
            "Confirm research question",
            "The current pipeline is using the configured research question. A user can accept it or request a new candidate topic before execution.",
            "draft_generation",
            ["accept_question", "request_topic_regeneration", "edit_question"],
            metadata={"research_question": paper_config["research"]["question"]},
            blocking=False,
        )
        observable.complete_step(
            "topic_confirmation",
            "Research question was exposed for user confirmation.",
            metadata={"research_question": paper_config["research"]["question"]},
        )

        draft_context = build_draft_context(paper_config, dataset_exists=dataset_exists, mode=mode)
        markdown_template = project_root / analysis_config["drafting"]["markdown_template"]
        latex_template = project_root / analysis_config["drafting"]["latex_template"]
        analysis_payload = None

        observable.start_step("analysis_execution")
        if mode == "live" and dataset_exists:
            analysis_payload = run_statspai_paper(paper_config, paths["final_dataset"])
            markdown_content = analysis_payload["draft"].to_markdown()
            latex_content = analysis_payload["draft"].to_tex()
            observable.complete_step(
                "analysis_execution",
                "StatsPAI empirical analysis completed.",
                metadata={
                    "workflow_design": analysis_payload["workflow_design"],
                    "workflow_verdict": analysis_payload["workflow_verdict"],
                },
            )
            if analysis_payload["workflow_design"] == "observational":
                observable.open_gate(
                    "gate_identification_boundary",
                    "analysis_execution",
                    "Confirm identification boundary",
                    "The executed design is observational. The user should confirm that the report will not overstate causal claims.",
                    "draft_generation",
                    ["accept_as_exploratory", "revise_identification", "supply_more_data"],
                    metadata={
                        "workflow_design": analysis_payload["workflow_design"],
                        "workflow_verdict": analysis_payload["workflow_verdict"],
                    },
                    blocking=False,
                )
        else:
            markdown_content = render_template(markdown_template, draft_context)
            latex_content = render_template(latex_template, draft_context)
            observable.complete_step(
                "analysis_execution",
                "Analysis execution skipped because the run is dry-run or the dataset is missing.",
                metadata={"mode": mode, "dataset_exists": dataset_exists},
                status="skipped",
            )

        observable.start_step("draft_generation")
        write_text(paths["markdown_draft"], markdown_content)
        observable.artifact_written("draft_generation", paths["markdown_draft"], "Markdown draft written.")
        qmd_content = build_qmd_content(paper_config["project"]["title"], markdown_content)
        write_text(paths["qmd_draft"], qmd_content)
        observable.artifact_written("draft_generation", paths["qmd_draft"], "Quarto manuscript source written.")
        write_text(paths["latex_draft"], latex_content)
        observable.artifact_written("draft_generation", paths["latex_draft"], "LaTeX draft written.")
        observable.complete_step(
            "draft_generation",
            "Draft artifacts were generated.",
            artifacts=[
                str(paths["markdown_draft"].relative_to(project_root)),
                str(paths["qmd_draft"].relative_to(project_root)),
                str(paths["latex_draft"].relative_to(project_root)),
            ],
        )

        observable.start_step("state_index")
        snapshot_payload = {
            "project": paper_config["project"],
            "research": paper_config["research"],
            "data": {
                **paper_config["data"],
                "dataset_exists": dataset_exists,
            },
            "methods": paper_config["methods"],
            "mode": mode,
        }
        if analysis_payload is not None:
            snapshot_payload["analysis"] = {
                "workflow_design": analysis_payload["workflow_design"],
                "workflow_verdict": analysis_payload["workflow_verdict"],
                "robustness_findings": analysis_payload["robustness_findings"],
                "result_payload": analysis_payload["result_payload"],
            }
        snapshot_path = paths["project_snapshot"]
        write_json(snapshot_path, snapshot_payload)
        observable.artifact_written("state_index", snapshot_path, "Structured project snapshot written.")

        log_path = paths["run_log"]
        write_text(
            log_path,
            "\n".join(
                [
                    f"mode={mode}",
                    f"project_root={project_root}",
                    f"dataset_exists={dataset_exists}",
                    f"engine={analysis_config['execution']['engine']}",
                    f"analysis_executed={analysis_payload is not None}",
                    f"observable_run_id={observable.run_id}",
                ]
            )
            + "\n",
        )
        observable.artifact_written("state_index", log_path, "Pipeline execution log written.")

        analysis_result_path = paths["analysis_result"]
        if analysis_payload is not None:
            write_json(
                analysis_result_path,
                {
                    "draft": analysis_payload["draft_dict"],
                    "workflow_design": analysis_payload["workflow_design"],
                    "workflow_verdict": analysis_payload["workflow_verdict"],
                    "robustness_findings": analysis_payload["robustness_findings"],
                    "result_payload": analysis_payload["result_payload"],
                },
            )
            observable.artifact_written("state_index", analysis_result_path, "StatsPAI analysis result written.")

        artifacts = [
            artifact_record(snapshot_path, project_root, "json", "Structured project snapshot"),
            artifact_record(paths["markdown_draft"], project_root, "markdown", "Generated draft in Markdown"),
            artifact_record(paths["qmd_draft"], project_root, "qmd", "Generated Quarto manuscript source"),
            artifact_record(paths["latex_draft"], project_root, "latex", "Generated draft in LaTeX"),
            artifact_record(log_path, project_root, "log", "Pipeline execution log"),
        ]
        if analysis_payload is not None:
            artifacts.append(
                artifact_record(
                    analysis_result_path,
                    project_root,
                    "json",
                    "StatsPAI paper workflow output",
                )
            )

        state_payload = build_project_state(paper_config, paths, mode=mode, artifacts=artifacts)
        write_json(paths["state_file"], state_payload)
        observable.artifact_written("state_index", paths["state_file"], "Project state written.")

        results_index = build_results_index(
            project_slug=paper_config["project"]["slug"],
            mode=mode,
            stage=paper_config["research"]["current_stage"],
            artifacts=artifacts,
        )
        write_json(paths["results_index"], results_index)
        observable.artifact_written("state_index", paths["results_index"], "Results index written.")
        observable.complete_step(
            "state_index",
            "State and result index artifacts were persisted.",
            artifacts=[
                str(snapshot_path.relative_to(project_root)),
                str(paths["state_file"].relative_to(project_root)),
                str(paths["results_index"].relative_to(project_root)),
            ],
        )

        observable.start_step("finalization")
        observable.complete_step(
            "finalization",
            "Observable run summary is ready for frontend polling.",
            artifacts=[
                str(observable.manifest_path.relative_to(project_root)),
                str(observable.steps_path.relative_to(project_root)),
                str(observable.events_path.relative_to(project_root)),
                str(observable.gates_path.relative_to(project_root)),
            ],
        )
        observable.succeed_run()

        print(f"[econ-workbench] mode={mode}")
        print(f"[econ-workbench] run_id={observable.run_id}")
        print(f"[econ-workbench] events={observable.events_path.relative_to(project_root)}")
        print(f"[econ-workbench] state={paths['state_file'].relative_to(project_root)}")
        print(f"[econ-workbench] index={paths['results_index'].relative_to(project_root)}")
        print(f"[econ-workbench] markdown={paths['markdown_draft'].relative_to(project_root)}")
        print(f"[econ-workbench] qmd={paths['qmd_draft'].relative_to(project_root)}")
        print(f"[econ-workbench] latex={paths['latex_draft'].relative_to(project_root)}")
        return 0
    except Exception as exc:
        observable.fail_run(str(exc))
        raise


if __name__ == "__main__":
    raise SystemExit(main())
