from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class CapabilitySource:
    name: str
    path: Path
    role: str
    required: bool = True

    @property
    def exists(self) -> bool:
        return self.path.exists()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "path": str(self.path),
            "role": self.role,
            "required": self.required,
            "exists": self.exists,
        }


def load_capability_sources(path: Path) -> list[CapabilitySource]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    sources = payload.get("capability_sources", {})
    loaded: list[CapabilitySource] = []
    for name, config in sources.items():
        loaded.append(
            CapabilitySource(
                name=name,
                path=Path(config["path"]).expanduser(),
                role=config["role"],
                required=bool(config.get("required", True)),
            )
        )
    return loaded


def missing_required_capabilities(sources: list[CapabilitySource]) -> list[CapabilitySource]:
    return [source for source in sources if source.required and not source.exists]
