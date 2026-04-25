from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RunWorkspace:
    run_id: str
    root: Path

    def stage(self, name: str) -> Path:
        return self.root / name

    def rel(self, path: Path, project_root: Path) -> str:
        return str(path.relative_to(project_root))


def required_run_relative_paths() -> list[Path]:
    return [
        Path("00_intake"),
        Path("01_sources"),
        Path("02_literature"),
        Path("03_strategy"),
        Path("04_modeling"),
        Path("05_results"),
        Path("06_writing"),
        Path("07_review"),
        Path("08_final"),
    ]


def runs_base(project_root: Path) -> Path:
    if (project_root / "06_workspace").exists():
        return project_root / "06_workspace" / "runs"
    return project_root / "workspace" / "runs"


def create_run_workspace(project_root: Path, run_id: str) -> RunWorkspace:
    root = runs_base(project_root) / run_id
    for rel in required_run_relative_paths():
        (root / rel).mkdir(parents=True, exist_ok=True)
    return RunWorkspace(run_id=run_id, root=root)

