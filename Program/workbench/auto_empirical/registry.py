from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RegisteredSource:
    key: str
    path: Path
    source_type: str
    status: str
    mutable: bool
    notes: tuple[str, ...] = ()

    @property
    def exists(self) -> bool:
        return self.path.exists()

    def contains(self, candidate: Path) -> bool:
        candidate_resolved = candidate.expanduser().resolve()
        source_resolved = self.path.expanduser().resolve()
        return candidate_resolved == source_resolved or source_resolved in candidate_resolved.parents

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "path": str(self.path),
            "type": self.source_type,
            "status": self.status,
            "mutable": self.mutable,
            "exists": self.exists,
            "notes": list(self.notes),
        }


class SourceRegistry:
    def __init__(self, sources: list[RegisteredSource]) -> None:
        self.sources = sources

    @classmethod
    def from_file(cls, path: Path) -> "SourceRegistry":
        payload = json.loads(path.read_text(encoding="utf-8"))
        sources: list[RegisteredSource] = []
        for key, config in payload.get("sources", {}).items():
            sources.append(
                RegisteredSource(
                    key=key,
                    path=Path(config["path"]).expanduser(),
                    source_type=config.get("type", "unknown"),
                    status=config.get("status", "unknown"),
                    mutable=bool(config.get("mutable", False)),
                    notes=tuple(config.get("notes", [])),
                )
            )
        return cls(sources)

    def allowed_roots(self) -> list[Path]:
        return [source.path for source in self.sources]

    def readonly_roots(self) -> list[Path]:
        return [source.path for source in self.sources if not source.mutable]

    def find_owner(self, candidate: Path) -> RegisteredSource | None:
        for source in self.sources:
            if source.exists and source.contains(candidate):
                return source
        return None

    def is_registered_path(self, candidate: Path) -> bool:
        return self.find_owner(candidate) is not None

    def to_dict(self) -> dict[str, Any]:
        return {"sources": [source.to_dict() for source in self.sources]}
