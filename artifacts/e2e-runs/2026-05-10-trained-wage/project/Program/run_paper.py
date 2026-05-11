from __future__ import annotations

import argparse
from pathlib import Path

from workbench.config import read_yaml, resolve_project_paths
from workbench.drafts import build_draft_context, render_template
from workbench.results import artifact_record, build_results_index
from workbench.state import build_project_state, write_json
from workbench.statspai_runner import run_statspai_paper


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Phase A econ workbench pipeline.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument("--dry-run", action="store_true", help="Skip analysis execution and only emit artifacts.")
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


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()

    paper_config = read_yaml(project_root / "paper.yaml")
    analysis_config = read_yaml(project_root / "Program" / "config" / "analysis_config.yaml")
    paths = resolve_project_paths(project_root, paper_config)
    ensure_directories(paths)

    mode = "dry-run" if args.dry_run else "live"
    dataset_exists = paths["final_dataset"].exists()

    draft_context = build_draft_context(paper_config, dataset_exists=dataset_exists, mode=mode)
    markdown_template = project_root / analysis_config["drafting"]["markdown_template"]
    latex_template = project_root / analysis_config["drafting"]["latex_template"]
    analysis_payload = None

    if mode == "live" and dataset_exists:
        analysis_payload = run_statspai_paper(paper_config, paths["final_dataset"])
        markdown_content = analysis_payload["draft"].to_markdown()
        latex_content = analysis_payload["draft"].to_tex()
    else:
        markdown_content = render_template(markdown_template, draft_context)
        latex_content = render_template(latex_template, draft_context)

    write_text(paths["markdown_draft"], markdown_content)
    write_text(paths["latex_draft"], latex_content)

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
    snapshot_path = paths["results_json_dir"] / "project_snapshot.json"
    write_json(snapshot_path, snapshot_payload)

    log_path = paths["results_logs_dir"] / "run_paper.log"
    write_text(
        log_path,
        "\n".join(
            [
                f"mode={mode}",
                f"project_root={project_root}",
                f"dataset_exists={dataset_exists}",
                f"engine={analysis_config['execution']['engine']}",
                f"analysis_executed={analysis_payload is not None}",
            ]
        )
        + "\n",
    )

    analysis_result_path = paths["results_json_dir"] / "analysis_result.json"
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

    artifacts = [
        artifact_record(snapshot_path, project_root, "json", "Structured project snapshot"),
        artifact_record(paths["markdown_draft"], project_root, "markdown", "Generated draft in Markdown"),
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

    results_index = build_results_index(
        project_slug=paper_config["project"]["slug"],
        mode=mode,
        stage=paper_config["research"]["current_stage"],
        artifacts=artifacts,
    )
    write_json(paths["results_index"], results_index)

    print(f"[econ-workbench] mode={mode}")
    print(f"[econ-workbench] state={paths['state_file'].relative_to(project_root)}")
    print(f"[econ-workbench] index={paths['results_index'].relative_to(project_root)}")
    print(f"[econ-workbench] markdown={paths['markdown_draft'].relative_to(project_root)}")
    print(f"[econ-workbench] latex={paths['latex_draft'].relative_to(project_root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
