#!/usr/bin/env python3
"""Validate the local StatspAI runtime plugin package shape."""

from __future__ import annotations

import json
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PLUGIN_ROOT / "package_manifest.json"
PLUGIN_JSON_PATH = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"


def read_json(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path.relative_to(PLUGIN_ROOT)}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path.relative_to(PLUGIN_ROOT)}: {exc}")
    return {}


def main() -> None:
    errors: list[str] = []
    package = read_json(MANIFEST_PATH, errors)
    plugin = read_json(PLUGIN_JSON_PATH, errors)

    if plugin.get("skills") != "./skills/":
        errors.append(".codex-plugin/plugin.json must expose ./skills/")
    if not plugin.get("interface", {}).get("defaultPrompt", "").startswith("Use $statspai-empirical-workflow"):
        errors.append("plugin defaultPrompt must point to $statspai-empirical-workflow")

    for key in ["plugin_manifest", "install_script"]:
        if package and not (PLUGIN_ROOT / package[key]).exists():
            errors.append(f"missing package path: {package[key]}")

    for group in package.get("package_assets", {}).values():
        paths = group if isinstance(group, list) else [group]
        for path_text in paths:
            if not (PLUGIN_ROOT / path_text).exists():
                errors.append(f"missing asset: {path_text}")

    for item in package.get("install_map", []):
        if item["kind"] not in {"file", "directory"}:
            errors.append(f"bad install kind for {item['source']}: {item['kind']}")
        if not (PLUGIN_ROOT / item["source"]).exists():
            errors.append(f"install source missing: {item['source']}")

    text_files = [
        PLUGIN_JSON_PATH,
        MANIFEST_PATH,
        PLUGIN_ROOT / "references" / "install.md",
    ]
    for path in text_files:
        if path.exists() and "TODO" in path.read_text(encoding="utf-8"):
            errors.append(f"{path.relative_to(PLUGIN_ROOT)} contains TODO")

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print("PASS")


if __name__ == "__main__":
    main()
