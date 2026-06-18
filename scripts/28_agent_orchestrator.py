#!/usr/bin/env python3
"""Policy-gated orchestrator for the empirical paper workflow layer."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "workflows" / "tool_adapters.json"
POLICY_PATH = ROOT / "workflows" / "orchestrator_policy.json"
RUNBOOK_STATE_PATH = ROOT / "artifacts" / "workflow_runbook_state.json"


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the policy-gated workflow orchestrator.")
    parser.add_argument("--mode", choices=["dry-run", "execute"], default=None)
    parser.add_argument("--adapter", action="append", default=[], help="Adapter id to plan or execute.")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--no-trace", action="store_true", help="Do not append JSONL trace events.")
    parser.add_argument("--write-artifacts", action="store_true", help="Allow dry-run to write report and state.")
    return parser.parse_args()


def adapter_map() -> dict[str, dict]:
    registry = load_json(ADAPTER_PATH)
    return {adapter["id"]: adapter for adapter in registry["adapters"]}


def default_adapters(policy: dict, adapters: dict[str, dict], mode: str) -> list[str]:
    if mode == "dry-run":
        return sorted(adapters)
    return [adapter_id for adapter_id in policy["allow_execute_adapters"] if adapter_id in adapters]


def safety_reasons(adapter_id: str, adapter: dict, policy: dict, mode: str) -> list[str]:
    reasons: list[str] = []
    command_allowlist = set(policy["command_allowlist"])

    if adapter_id in policy["blocked_adapters"]:
        reasons.append("adapter_not_allowed")
    if mode == "execute" and adapter_id not in policy["allow_execute_adapters"]:
        reasons.append("adapter_not_allowed")
    if adapter_id == "workflow_preflight" and not policy["allow_recursive_preflight"]:
        reasons.append("recursive_preflight")
    if adapter["network_required"] and not policy["allow_network"]:
        reasons.append("network_required")
    if adapter["human_auth_required"] and not policy["allow_human_auth"]:
        reasons.append("human_auth_required")
    if adapter["side_effect_level"] in policy["blocked_side_effect_levels"]:
        reasons.append("blocked_side_effect")
    if adapter["side_effect_level"] not in policy["allowed_side_effect_levels"]:
        reasons.append("blocked_side_effect")

    for command in adapter["commands"]:
        if "<" in command or ">" in command:
            reasons.append("placeholder_command")
        if command not in command_allowlist:
            reasons.append("command_not_allowlisted")

    return sorted(set(reasons))


def run_command(command: str) -> dict:
    argv = shlex.split(command)
    started_at = datetime.now().astimezone().isoformat(timespec="seconds")
    completed = subprocess.run(
        argv,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    ended_at = datetime.now().astimezone().isoformat(timespec="seconds")
    return {
        "command": command,
        "argv": argv,
        "returncode": completed.returncode,
        "started_at": started_at,
        "ended_at": ended_at,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "stdout_summary": summarize(completed.stdout),
        "stderr_summary": summarize(completed.stderr),
    }


def summarize(text: str, limit: int = 500) -> str:
    compact = " ".join(text.strip().split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def trace_event(
    run_id: str,
    index: int,
    mode: str,
    adapter_id: str,
    decision: str,
    action: str,
    status: str,
    adapter: dict,
    reason: list[str],
    failure_code: str | None,
    command_results: list[dict],
    evidence: list[str],
) -> dict:
    return {
        "run_id": run_id,
        "event_id": f"{run_id}-{index:03d}",
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "mode": mode,
        "actor": "AgentOrchestrator",
        "workflow_id": "runtime_gap_p3",
        "adapter_id": adapter_id,
        "decision": decision,
        "action": action,
        "status": status,
        "reason": reason,
        "failure_code": failure_code,
        "commands": adapter["commands"],
        "command_results": compact_command_results(command_results),
        "inputs": adapter["inputs"],
        "outputs": adapter["outputs"],
        "verification": adapter["verification"],
        "evidence": evidence,
    }


def compact_command_results(results: list[dict]) -> list[dict]:
    return [
        {
            "command": result["command"],
            "argv": result["argv"],
            "returncode": result["returncode"],
            "started_at": result["started_at"],
            "ended_at": result["ended_at"],
            "stdout_summary": result["stdout_summary"],
            "stderr_summary": result["stderr_summary"],
        }
        for result in results
    ]


def write_trace(policy: dict, events: list[dict]) -> None:
    trace_path = ROOT / policy["trace_path"]
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with trace_path.open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_outputs(policy: dict, state: dict, command_results: dict[str, list[dict]]) -> None:
    report_path = ROOT / policy["report_path"]
    state_path = ROOT / policy["state_path"]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Agent Orchestrator Report",
        "",
        f"Status: {state['status'].upper()}",
        f"Mode: `{state['mode']}`",
        f"Run id: `{state['run_id']}`",
        f"Generated: {state['generated_at']}",
        "",
        "## Summary",
        "",
        f"- Selected adapters: {len(state['selected_adapters'])}",
        f"- Executed commands: {len(state['executed_commands'])}",
        f"- Blocked adapters: {len(state['blocked_adapters'])}",
        f"- Trace path: `{state['trace_path']}`",
        "",
        "## Events",
        "",
    ]

    for event in state["events"]:
        lines.extend(
            [
                f"### `{event['adapter_id']}`",
                "",
                f"- status: `{event['status']}`",
                f"- reason: {', '.join(event['reason']) if event['reason'] else 'none'}",
                f"- commands: {', '.join(f'`{command}`' for command in event['commands'])}",
                "",
            ]
        )
        for result in command_results.get(event["adapter_id"], []):
            lines.extend(
                [
                    f"command `{result['command']}` exit {result['returncode']}",
                    "",
                ]
            )
            if result["stdout"]:
                lines.extend(["stdout:", "", "```text", result["stdout"], "```", ""])
            if result["stderr"]:
                lines.extend(["stderr:", "", "```text", result["stderr"], "```", ""])

    report_path.write_text("\n".join(lines), encoding="utf-8")
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    policy = load_json(POLICY_PATH)
    adapters = adapter_map()
    runbook_state = load_json(RUNBOOK_STATE_PATH)

    mode = args.mode or policy["default_mode"]
    run_id = args.run_id or f"p3-{mode}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    selected = args.adapter or default_adapters(policy, adapters, mode)

    events: list[dict] = []
    trace_events: list[dict] = []
    executed_commands: list[str] = []
    blocked_adapters: list[str] = []
    command_results: dict[str, list[dict]] = {}
    failures = 0

    for index, adapter_id in enumerate(selected, start=1):
        adapter = adapters.get(adapter_id)
        if not adapter:
            blocked_adapters.append(adapter_id)
            events.append(
                {
                    "adapter_id": adapter_id,
                    "decision": "blocked",
                    "status": "blocked",
                    "reason": ["adapter_not_registered"],
                    "failure_code": "adapter_not_registered",
                    "commands": [],
                    "command_results": [],
                    "inputs": [rel(ADAPTER_PATH)],
                    "outputs": [policy["state_path"], policy["report_path"]],
                    "verification": ["adapter id must exist in workflows/tool_adapters.json"],
                }
            )
            trace_events.append(
                {
                    "run_id": run_id,
                    "event_id": f"{run_id}-{index:03d}",
                    "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
                    "mode": mode,
                    "actor": "AgentOrchestrator",
                    "workflow_id": "runtime_gap_p3",
                    "adapter_id": adapter_id,
                    "decision": "blocked",
                    "action": "block unknown adapter",
                    "status": "blocked",
                    "reason": ["adapter_not_registered"],
                    "failure_code": "adapter_not_registered",
                    "commands": [],
                    "command_results": [],
                    "inputs": [rel(ADAPTER_PATH)],
                    "outputs": [policy["state_path"], policy["report_path"]],
                    "verification": ["adapter id must exist in workflows/tool_adapters.json"],
                    "evidence": ["adapter_not_registered"],
                }
            )
            continue

        reasons = safety_reasons(adapter_id, adapter, policy, mode)
        if reasons:
            blocked_adapters.append(adapter_id)
            event = {
                "adapter_id": adapter_id,
                "decision": "blocked",
                "status": "blocked",
                "reason": reasons,
                "failure_code": reasons[0],
                "commands": adapter["commands"],
                "command_results": [],
                "inputs": adapter["inputs"],
                "outputs": adapter["outputs"],
                "verification": adapter["verification"],
            }
            events.append(event)
            trace_events.append(
                trace_event(
                    run_id,
                    index,
                    mode,
                    adapter_id,
                    "blocked",
                    "block adapter by policy",
                    "blocked",
                    adapter,
                    reasons,
                    reasons[0],
                    [],
                    reasons,
                )
            )
            continue

        if mode == "dry-run":
            events.append(
                {
                    "adapter_id": adapter_id,
                    "decision": "planned",
                    "status": "planned",
                    "reason": [],
                    "failure_code": None,
                    "commands": adapter["commands"],
                    "command_results": [],
                    "inputs": adapter["inputs"],
                    "outputs": adapter["outputs"],
                    "verification": adapter["verification"],
                }
            )
            trace_events.append(
                trace_event(
                    run_id,
                    index,
                    mode,
                    adapter_id,
                    "planned",
                    "plan adapter execution",
                    "recorded",
                    adapter,
                    [],
                    None,
                    [],
                    ["dry-run"],
                )
            )
            continue

        results = [run_command(command) for command in adapter["commands"]]
        command_results[adapter_id] = results
        executed_commands.extend(result["command"] for result in results)
        failed_results = [result for result in results if result["returncode"] != 0]
        if failed_results:
            failures += len(failed_results)
            status = "fail"
            evidence = [f"{result['command']} exit {result['returncode']}" for result in failed_results]
        else:
            status = "pass"
            evidence = [f"{result['command']} exit 0" for result in results]
        reason = ["command_failed"] if failed_results else []
        failure_code = "command_failed" if failed_results else None
        events.append(
            {
                "adapter_id": adapter_id,
                "decision": "failed" if failed_results else "executed",
                "status": status,
                "reason": reason,
                "failure_code": failure_code,
                "commands": adapter["commands"],
                "command_results": compact_command_results(results),
                "inputs": adapter["inputs"],
                "outputs": adapter["outputs"],
                "verification": adapter["verification"],
            }
        )
        trace_events.append(
            trace_event(
                run_id,
                index,
                mode,
                adapter_id,
                "failed" if failed_results else "executed",
                "execute adapter commands",
                status,
                adapter,
                reason,
                failure_code,
                results,
                evidence,
            )
        )

    if failures:
        status = "fail"
    elif blocked_adapters and mode == "execute":
        status = "blocked"
    else:
        status = "pass"

    state = {
        "version": "0.1",
        "run_id": run_id,
        "mode": mode,
        "status": status,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "selected_adapters": selected,
        "executed_commands": executed_commands,
        "blocked_adapters": blocked_adapters,
        "events": events,
        "report_path": policy["report_path"],
        "trace_path": policy["trace_path"],
    }

    should_write = mode == "execute" or args.write_artifacts
    if should_write:
        write_outputs(policy, state, command_results)
    if should_write and not args.no_trace:
        write_trace(policy, trace_events)

    route = runbook_state["current_route"]["next_workflow_id"] or "none"
    print(f"{status.upper()} mode={mode} selected={len(selected)} executed={len(executed_commands)} blocked={len(blocked_adapters)} route={route} report={policy['report_path']}")
    if not should_write:
        print("dry-run wrote no artifacts; pass --write-artifacts to persist a plan")
        for event in events:
            reason = ",".join(event["reason"]) if event["reason"] else "none"
            print(f"{event['adapter_id']}: {event['status']} reason={reason}")
    if status == "fail":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
