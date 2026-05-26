from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from Product.backend.codex_provider import local_codex_status, run_local_codex_prompt  # noqa: E402
from workbench.paper_supervisor import (  # noqa: E402
    build_supervisor_execution_prompt,
    build_supervisor_run,
    load_supervisor_context,
    write_supervisor_run,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local Codex Supervisor for a paper package context.")
    parser.add_argument("--project-root", default=".", help="Absolute or relative project root.")
    parser.add_argument(
        "--context",
        default="Results/json/paper_supervisor_context.json",
        help="Supervisor context path relative to project root.",
    )
    parser.add_argument(
        "--output-run",
        default="Results/json/paper_supervisor_run.json",
        help="Supervisor run JSON path relative to project root.",
    )
    parser.add_argument(
        "--output-raw",
        default="docs/workflows/paper_package_supervisor/supervisor_round.md",
        help="Raw local Codex Supervisor Markdown output path relative to project root.",
    )
    parser.add_argument("--timeout-seconds", type=int, default=300)
    return parser.parse_args()


def resolve_path(project_root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else project_root / path


def fail(code: str, message: str) -> int:
    print(json.dumps({"error": {"code": code, "message": message}}, ensure_ascii=False), file=sys.stderr)
    return 1


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    context_path = resolve_path(project_root, args.context)
    output_run = resolve_path(project_root, args.output_run)
    output_raw = resolve_path(project_root, args.output_raw)

    try:
        context = load_supervisor_context(context_path)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        return fail("invalid_supervisor_context", str(exc))

    provider_status = local_codex_status()
    if not provider_status.get("execution_enabled"):
        return fail(
            "local_codex_execution_not_enabled",
            f"Set {provider_status.get('execution_env')}=1 to allow local Codex supervisor execution.",
        )
    if not provider_status.get("available"):
        return fail("local_codex_not_found", "Local Codex CLI is not available.")

    prompt = build_supervisor_execution_prompt(context)
    try:
        provider_result = run_local_codex_prompt(
            project_root,
            prompt,
            output_raw,
            timeout_seconds=args.timeout_seconds,
        )
    except (FileNotFoundError, RuntimeError, OSError) as exc:
        return fail("local_codex_execution_failed", str(exc))

    if provider_result.get("returncode") != 0:
        return fail("local_codex_execution_failed", provider_result.get("stderr") or "Local Codex returned non-zero.")

    run = build_supervisor_run(
        project_root=project_root,
        context_path=context_path,
        raw_output_path=output_raw,
        context=context,
        provider_result=provider_result,
        provider_status=provider_status,
    )
    run_path = write_supervisor_run(output_run, run)
    print(f"[econ-workbench] paper_supervisor_run={run_path.relative_to(project_root)}")
    print(f"[econ-workbench] supervisor_round={output_raw.relative_to(project_root)}")
    print(f"[econ-workbench] agent_tasks={len(run.get('agent_task_queue', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
