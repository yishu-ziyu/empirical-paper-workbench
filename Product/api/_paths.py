"""共享路径常量 — 5 个 api router 共用.

来源: 后端解耦审计报告 (2026-06-05) Phase A M2 项.
原本 5 个 router 各自硬编码 _TASKS_ROOT / _REPO_ROOT / _DATA_ROOT 等, 真相源分散.
"""
from pathlib import Path

# 仓库根目录 (Product/api/_paths.py 的 parents[2] 即 /<repo>)
REPO_ROOT: Path = Path(__file__).resolve().parents[2]

# 4 个常用子目录
TASKS_ROOT: Path = REPO_ROOT / "Tasks"
DATA_ROOT: Path = REPO_ROOT / "data"
MANUSCRIPTS_ROOT: Path = REPO_ROOT / "Manuscripts"
RESULTS_ROOT: Path = REPO_ROOT / "Results"
