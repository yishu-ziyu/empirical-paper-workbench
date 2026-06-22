#!/usr/bin/env python3
"""Install the StatspAI workflow registration layer into a target project."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PLUGIN_ROOT / "package_manifest.json"


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def copy_file(source: Path, target: Path, overwrite: bool) -> str:
    if target.exists() and not overwrite:
        return "skip-existing"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return "copied"


def copy_directory(source: Path, target: Path, overwrite: bool) -> str:
    if target.exists() and not overwrite:
        return "skip-existing"
    if target.exists():
        shutil.rmtree(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target)
    return "copied"


def install(target_root: Path, apply: bool, overwrite: bool) -> tuple[list[str], list[str]]:
    manifest = load_manifest()
    actions: list[str] = []
    errors: list[str] = []

    for required in manifest["target_requirements"]:
        required_path = target_root / required
        if not required_path.exists():
            errors.append(f"missing target requirement: {required}")

    for item in manifest["install_map"]:
        source = PLUGIN_ROOT / item["source"]
        target = target_root / item["target"]
        if not source.exists():
            errors.append(f"missing package source: {item['source']}")
            continue
        if not apply:
            state = "would-copy" if overwrite or not target.exists() else "would-skip-existing"
        elif item["kind"] == "directory":
            state = copy_directory(source, target, overwrite)
        else:
            state = copy_file(source, target, overwrite)
        actions.append(f"{state}: {item['source']} -> {rel(target, target_root)}")

    return actions, errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Target project root")
    parser.add_argument("--apply", action="store_true", help="Write files. Default only prints planned actions.")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing installed files.")
    args = parser.parse_args()

    target_root = Path(args.target).expanduser().resolve()
    if not target_root.exists():
        raise SystemExit(f"target does not exist: {target_root}")
    if not target_root.is_dir():
        raise SystemExit(f"target is not a directory: {target_root}")

    actions, errors = install(target_root, args.apply, args.overwrite)
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"{mode} target={target_root}")
    for action in actions:
        print(f"- {action}")

    if errors:
        print("ERRORS:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("PASS")


if __name__ == "__main__":
    main()
