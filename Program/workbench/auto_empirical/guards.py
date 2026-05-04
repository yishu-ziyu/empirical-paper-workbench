from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .registry import SourceRegistry


@dataclass(frozen=True)
class RawDataManifest:
    files: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {"files": self.files}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build_raw_data_manifest(paths: list[Path]) -> RawDataManifest:
    return RawDataManifest(files={str(path.resolve()): file_sha256(path) for path in sorted(paths)})


def verify_raw_data_manifest(manifest: RawDataManifest) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    for raw_path, expected_hash in manifest.files.items():
        path = Path(raw_path)
        if not path.exists():
            violations.append({"path": raw_path, "violation": "missing"})
            continue
        observed_hash = file_sha256(path)
        if observed_hash != expected_hash:
            violations.append({"path": raw_path, "violation": "hash_changed"})
    return violations


def validate_registered_inputs(paths: list[Path], registry: SourceRegistry) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    for path in paths:
        if registry.find_owner(path) is None:
            violations.append({"path": str(path), "violation": "unregistered_source"})
    return violations


def validate_no_readonly_writes(changed_paths: list[Path], registry: SourceRegistry) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    for path in changed_paths:
        owner = registry.find_owner(path)
        if owner is not None and not owner.mutable:
            violations.append({"path": str(path), "violation": "readonly_source_modified", "source": owner.key})
    return violations
