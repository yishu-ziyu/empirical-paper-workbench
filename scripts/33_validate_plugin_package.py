#!/usr/bin/env python3
"""Validate Runtime Gap P5 plugin package portability."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "statspai-empirical-workflow-runtime"
MANIFEST_PATH = PLUGIN_ROOT / "package_manifest.json"
REPORT_PATH = ROOT / "artifacts" / "plugin_package_validation_report.md"
PLUGIN_VALIDATOR = Path("/Users/mahaoxuan/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py")


def run(command: list[str], cwd: Path) -> dict:
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return {
        "command": " ".join(command),
        "cwd": str(cwd),
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def skipped(command: list[str], cwd: Path, reason: str) -> dict:
    return {
        "command": " ".join(command),
        "cwd": str(cwd),
        "returncode": 0,
        "stdout": f"SKIP {reason}",
        "stderr": "",
    }


def copy_required_target_files(target: Path, manifest: dict, errors: list[str]) -> None:
    for path_text in manifest["target_requirements"]:
        source = ROOT / path_text
        target_path = target / path_text
        if not source.exists():
            errors.append(f"source target requirement missing in current repo: {path_text}")
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target_path, dirs_exist_ok=True)
        else:
            shutil.copy2(source, target_path)


def validate_static_package(manifest: dict, errors: list[str]) -> None:
    if not (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").exists():
        errors.append("missing plugin.json")
    for item in manifest.get("install_map", []):
        source = PLUGIN_ROOT / item["source"]
        if not source.exists():
            errors.append(f"missing install source: {item['source']}")
        if item["kind"] not in {"file", "directory"}:
            errors.append(f"invalid install kind: {item['source']} -> {item['kind']}")
    for command in manifest.get("validation_commands", []):
        if not command.startswith("python3 scripts/"):
            errors.append(f"validation command must be local script only: {command}")


def main() -> None:
    errors: list[str] = []
    results: list[dict] = []
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    validate_static_package(manifest, errors)

    plugin_validator_command = ["python3", str(PLUGIN_VALIDATOR), str(PLUGIN_ROOT)]
    if PLUGIN_VALIDATOR.exists():
        results.append(run(plugin_validator_command, ROOT))
    else:
        results.append(
            skipped(
                plugin_validator_command,
                ROOT,
                "optional external plugin-creator validator is not installed on this machine",
            )
        )
    results.append(run(["python3", "scripts/validate_package.py"], PLUGIN_ROOT))

    with tempfile.TemporaryDirectory(prefix="statspai_plugin_target_") as temp_dir:
        target = Path(temp_dir) / "second-project"
        target.mkdir(parents=True)
        copy_required_target_files(target, manifest, errors)

        install_script = PLUGIN_ROOT / "scripts" / "install_into_project.py"
        results.append(run(["python3", str(install_script), "--target", str(target)], ROOT))
        results.append(run(["python3", str(install_script), "--target", str(target), "--apply", "--overwrite"], ROOT))
        results.append(run(["python3", "scripts/31_validate_skill_subagent_registry.py"], target))
        results.append(run(["python3", "scripts/32_test_skill_subagent_negative.py"], target))

    for result in results:
        if result["returncode"] != 0:
            errors.append(f"command failed: {result['command']}")

    status = "PASS" if not errors else "FAIL"
    lines = [
        "# Plugin Package Validation",
        "",
        f"Status: {status}",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Package",
        "",
        f"- Plugin: `{PLUGIN_ROOT.relative_to(ROOT)}`",
        f"- Manifest: `{MANIFEST_PATH.relative_to(ROOT)}`",
        f"- Install map entries: {len(manifest.get('install_map', []))}",
        f"- Target requirements: {len(manifest.get('target_requirements', []))}",
        "",
        "## Commands",
        "",
    ]
    for result in results:
        lines.extend(
            [
                f"### `{result['command']}`",
                "",
                f"- cwd: `{result['cwd']}`",
                f"- exit: {result['returncode']}",
                "",
            ]
        )
        if result["stdout"]:
            lines.extend(["stdout:", "", "```text", result["stdout"], "```", ""])
        if result["stderr"]:
            lines.extend(["stderr:", "", "```text", result["stderr"], "```", ""])

    if errors:
        lines.extend(["## Errors", "", *[f"- {error}" for error in errors], ""])
    else:
        lines.extend(
            [
                "## Checks",
                "",
                "- Optional Codex plugin validator passed or was unavailable on this machine.",
                "- Package manifest sources exist.",
                "- Installer dry-run completed against a temporary second project.",
                "- Installer apply completed against a temporary second project.",
                "- Installed registry validation passed in the temporary second project.",
                "- Installed negative test passed in the temporary second project.",
                "",
            ]
        )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"{status} report={REPORT_PATH.relative_to(ROOT)}")
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
