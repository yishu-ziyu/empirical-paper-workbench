from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


# 8-segment stage 名称: code 内仍用 en key (跟 checkpoint id 兼容),
# 实际写盘用中文目录名 (PM 友好). 老 run 的英文目录也认.
STAGE_DIR: dict[str, str] = {
    "00_intake": "00_收件",
    "01_sources": "01_数据源",
    "02_literature": "02_文献",
    "03_strategy": "03_策略",
    "04_modeling": "04_建模",
    "05_results": "05_结果",
    "06_writing": "06_写作",
    "07_review": "07_评审",
    "08_final": "08_终稿",
}

# Stage key -> PM-friendly 中文 label (用于 CLI 展示)
STAGE_DISPLAY: dict[str, str] = {
    "00_intake": "收件",
    "01_sources": "数据源",
    "02_literature": "文献",
    "03_strategy": "策略",
    "04_modeling": "建模",
    "05_results": "结果",
    "06_writing": "写作",
    "07_review": "评审",
    "08_final": "终稿",
}


def stage_dir(stage_key: str) -> str:
    """Stage key -> 实际写盘的目录名 (新 run 中文, 老 run 英文也认)."""
    return STAGE_DIR.get(stage_key, stage_key)


def stage_key_from_dirname(dirname: str) -> str | None:
    """目录名 -> stage key (兼容中英). 找不到返回 None."""
    # 先按 en key 查
    if dirname in STAGE_DIR:
        return dirname
    # 再按中文目录名查
    for k, v in STAGE_DIR.items():
        if v == dirname:
            return k
    return None


def all_known_dirnames() -> set[str]:
    """所有合法目录名 (en + 中文), inspect / demo 扫盘用."""
    return set(STAGE_DIR.keys()) | set(STAGE_DIR.values())


@dataclass(frozen=True)
class RunWorkspace:
    run_id: str
    root: Path

    def stage(self, name: str) -> Path:
        """name 可以是 stage key ('00_intake') 或中文目录名 ('00_收件')."""
        return self.root / stage_dir(name) if name in STAGE_DIR else self.root / name

    def rel(self, path: Path, project_root: Path) -> str:
        return str(path.relative_to(project_root))


def required_run_relative_paths() -> list[Path]:
    """新 run 创建时要建的 9 个目录 (用中文目录名)."""
    return [Path(v) for v in STAGE_DIR.values()]


def runs_base(project_root: Path) -> Path:
    if (project_root / "06_workspace").exists():
        return project_root / "06_workspace" / "runs"
    return project_root / "workspace" / "runs"


def create_run_workspace(project_root: Path, run_id: str) -> RunWorkspace:
    root = runs_base(project_root) / run_id
    for rel in required_run_relative_paths():
        (root / rel).mkdir(parents=True, exist_ok=True)
    return RunWorkspace(run_id=run_id, root=root)
