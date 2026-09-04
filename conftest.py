"""ADR-0003 Stage C: 根级共享测试工厂。

被 agent/tests/ 和 backend/tests/ 同时发现（pytest conftest 向上查找机制）。
提供：
- make_state(**overrides): 构造 EconPaperState，复用 TypedDict 类型
- make_body_chapters(n=6): 构造 n 章节列表
- make_title_chapter(): 构造标题章节
- make_six_chapter_outline(): 构造 6 章大纲
- make_cleaning_report(): 构造清洗报告
- mock_llm_for(node_name): 通用 LLM mock 工厂，支持 generate_title/outline/chapter 三种签名
- charls_csv / generic_csv / workspace: 跨文件复用的数据 fixture
"""
import os
import tempfile
from pathlib import Path

_TEST_STATE_ROOT = Path(tempfile.mkdtemp(prefix="ep-test-state-"))

# Backend tests import config at collection time. Local/demo tests rely on
# anonymous sessions; production (DEBUG=false) rejects those with 401.
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-only-jwt-secret-key-32chars-min",
)
# 旧 SessionStore JSON 迁移入口：测试进程必须无条件改用系统临时目录。
# 不能用 setdefault：开发者终端可能已配置真实数据路径，测试不得写入它们。
os.environ["SESSIONS_PATH"] = str(
    _TEST_STATE_ROOT / "sessions" / "sessions.json"
)
os.environ["ECONPAPER_LOCAL_STATE_ROOT"] = str(_TEST_STATE_ROOT)
_POSTGRES_TEST_URL = os.getenv("TEST_POSTGRES_DATABASE_URL")
os.environ["DATABASE_URL"] = _POSTGRES_TEST_URL or (
    f"sqlite+aiosqlite:///{_TEST_STATE_ROOT / 'db' / 'econpaper.db'}"
)
os.environ["UPLOAD_DIR"] = str(_TEST_STATE_ROOT / "uploads")
os.environ["RUNS_DIR"] = str(_TEST_STATE_ROOT / "runs")
os.environ["S3_CACHE_DIR"] = str(_TEST_STATE_ROOT / "cache" / "s3")
os.environ["LEARNING_LABELS_PATH"] = str(
    _TEST_STATE_ROOT / "learning" / "learning_labels.jsonl"
)

import pytest


def make_state(**overrides) -> dict:
    """构造 EconPaperState dict，支持任意字段 override。

    用法：
        state = make_state()  # 最小空 state
        state = make_state(current_chapter_index=3, body_chapters=make_body_chapters())
        state = make_state(research_direction="test direction")
    """
    base = {
        "session_id": "test-session",
        "csv_path": "/tmp/test.csv",
        "uploaded_datasets": [{"path": "/tmp/test.csv", "format": "csv"}],
    }
    base.update(overrides)
    return base


def make_title_chapter(title: str = "Test Paper Title") -> dict:
    """构造标题章节（generate_title 输出）。"""
    return {
        "type": "title",
        "title": title,
        "content": f"\\title{{{title}}}",
        "status": "generated",
    }


def make_body_chapters(n: int = 6) -> list:
    """构造 n 个正文章节（generate_chapter 输出）。

    type 顺序与 CHAPTER_TYPES 一致：intro/lit_review/data_desc/methods/results/conclusion
    """
    types = ["intro", "lit_review", "data_desc", "methods", "results", "conclusion"]
    chapters = []
    for i in range(min(n, 6)):
        chapters.append({
            "type": types[i],
            "title": f"Chapter {i+1}: {types[i].replace('_', ' ').title()}",
            "content": f"Content for chapter {i+1}.",
            "status": "generated",
            "versions": [f"Content for chapter {i+1}."],
            "chapter_index": i,
        })
    return chapters


def make_six_chapter_outline() -> list:
    """构造 6 章大纲（generate_outline 输出）。

    title 用中文（与 generate_outline 节点输出 + 现有测试断言一致）。
    """
    return [
        {"type": "intro", "title": "引言"},
        {"type": "lit_review", "title": "文献综述"},
        {"type": "data_desc", "title": "数据描述"},
        {"type": "methods", "title": "方法", "method": "OLS"},
        {"type": "results", "title": "结果"},
        {"type": "conclusion", "title": "结论"},
    ]


def make_write_ready_state(**overrides) -> dict:
    """State that may write any of the six chapter slots."""
    treatment_row = "| age | 0.1234 | 0.0456 | 0.0078 |"
    ready = make_state(
        research_direction={
            "question": "年龄与收入",
            "dv": "income",
            "iv": "age",
            "method": "ols",
            "claim": "association",
        },
        identification_diag={
            "strategy": None,
            "diagnostics": [],
            "passed": True,
            "report": "OLS 无识别套餐，按相关表述。",
            "star_rating": None,
        },
        star_rating=None,
        claim="association",
        estimate={
            "status": "ok",
            "produced_by": "estimate",
            "method": "ols",
            "estimator": "statspai.feols",
            "treatment": "age",
            "coef": 0.1234,
            "se": 0.0456,
            "p": 0.0078,
            "n": 5,
            "treatment_row": treatment_row,
            "formula": "income ~ age",
        },
        results=(
            "# 主结果\n\n| 变量 | 系数 | SE | p |\n"
            "|------|------|----|---|\n" + treatment_row
        ),
        robustness_results={
            "produced_by": "robustness_check",
            "diagnostics": [],
            "degraded": True,
            "reason": "no_cluster_or_groups",
            "summary_table": "# 稳健性",
        },
        literature_produced_by="search_literature",
        literature_source="mock",
        literature_query="q",
        literature_entries=[
            {
                "title": "T",
                "authors": ["A"],
                "year": 2020,
                "doi": "10.1/x",
                "source": "mock",
            }
        ],
        citation_indices={"10.1/x": 1},
        outline=make_six_chapter_outline(),
        current_chapter_index=0,
    )
    ready.update(overrides)
    return ready


def make_cleaning_report() -> dict:
    """构造清洗报告（clean_data 输出，8 步 StepReport）。"""
    return {
        "steps": [
            {
                "name": f"step_{i}",
                "status": "success",
                "started_at": "2026-01-01T00:00:00",
                "duration": 0.1 * i,
                "report": {},
            }
            for i in range(8)
        ]
    }


class _MockLLMRecorder:
    """记录 LLM 调用，支持断言。"""
    def __init__(self):
        self.calls: list = []
        self.return_value: str = "Mock LLM output"

    def __call__(self, *args, **kwargs):
        self.calls.append({"args": args, "kwargs": kwargs})
        return self.return_value


@pytest.fixture
def mock_llm_for(monkeypatch):
    """通用 LLM mock 工厂 fixture。

    用法：
        def test_x(mock_llm_for):
            recorder = mock_llm_for("generate_title")  # patch nodes.generate_title.call_llm
            # ... 触发节点调用 ...
            assert len(recorder.calls) > 0

    支持的 node_name:
        - "generate_title": patch nodes.generate_title.call_llm，签名 (prompt: str) -> str
        - "generate_outline": patch nodes.generate_outline.call_llm，签名 (prompt: str) -> str
        - "generate_chapter": patch nodes.generate_chapter.call_llm，签名 (system, user) -> str

    返回 _MockLLMRecorder，可通过 .calls 读取调用列表，通过 .return_value 设置返回值。
    """
    def _factory(node_name: str, return_value: str = "Mock LLM output"):
        recorder = _MockLLMRecorder()
        recorder.return_value = return_value
        module_map = {
            "generate_title": "agent.nodes.generate_title",
            "generate_outline": "agent.nodes.generate_outline",
            "generate_chapter": "agent.nodes.generate_chapter",
        }
        if node_name not in module_map:
            raise ValueError(
                f"Unsupported node: {node_name}. Supported: {list(module_map)}"
            )
        monkeypatch.setattr(
            f"{module_map[node_name]}.call_llm", recorder, raising=False
        )
        return recorder
    return _factory


# 公共 fixture，可直接在测试里用
@pytest.fixture
def state():
    """默认最小 state。"""
    return make_state()


@pytest.fixture
def body_chapters():
    """6 个正文章节。"""
    return make_body_chapters()


@pytest.fixture
def six_chapter_outline():
    """6 章大纲。"""
    return make_six_chapter_outline()


@pytest.fixture
def title_chapter():
    """标题章节。"""
    return make_title_chapter()


@pytest.fixture
def cleaning_report():
    """清洗报告。"""
    return make_cleaning_report()


# ---------- 跨文件复用的 CSV / workspace fixture -----------------------------

CHARLS_COLUMNS = [
    "community_id",
    "household_id",
    "pid",
    "wave",
    "rage",
    "ragender",
    "rmarital",
    "redu",
    "qe303_hi",
    "qe304_hi",
    "qe305_hi",
    "qe306_hi",
    "qe307_hi",
    "qe308_hi",
]


@pytest.fixture
def charls_csv(tmp_path) -> Path:
    """Mock CHARLS CSV: community_id + 6 qe*_hi columns + demographics."""
    import pandas as pd

    rows = []
    for i in range(5):
        row = {col: i for col in CHARLS_COLUMNS}
        row["community_id"] = 100 + i
        row["household_id"] = 1000 + i
        row["pid"] = 10000 + i
        row["wave"] = 2018
        row["ragender"] = 1
        row["rmarital"] = 1 if i % 2 == 0 else 2
        rows.append(row)
    df = pd.DataFrame(rows)
    p = tmp_path / "charls_mock.csv"
    df.to_csv(p, index=False)
    return p


@pytest.fixture
def generic_csv(tmp_path) -> Path:
    """Plain non-CHARLS CSV: no community_id, no qe*_hi columns."""
    import pandas as pd

    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "income": [100, 200, 300],
            "city": ["A", "B", "C"],
        }
    )
    p = tmp_path / "generic.csv"
    df.to_csv(p, index=False)
    return p


@pytest.fixture
def workspace(tmp_path) -> str:
    """Workspace root with the Raw/Interim/Final three-tier structure."""
    root = tmp_path / "workspace"
    for tier in ("Raw", "Interim", "Final"):
        (root / tier).mkdir(parents=True, exist_ok=True)
    return str(root)
