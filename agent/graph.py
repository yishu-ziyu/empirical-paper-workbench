import os

import psycopg
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph

from nodes.clean_data import clean_data
from nodes.citation_graph import build_citation_graph
from nodes.estimate import estimate
from nodes.generate_outline import generate_outline
from nodes.generate_title import generate_title
from nodes.hitl_pause import hitl_pause
from nodes.identification_verify import identification_verify
from nodes.robustness_check import robustness_check
from nodes.search_literature import search_literature
from nodes.set_direction import set_direction
from nodes.upload_data import upload_data
from state import EconPaperState

# 6 章固定 type 顺序（与 generate_outline 产出一致）
CHAPTER_TYPES = ["intro", "lit_review", "data_desc", "methods", "results", "conclusion"]


def route_after_chapter(state: EconPaperState) -> str:
    """generate_chapter 后的条件边路由（T-08a）。

    state-driven 简化（不调 interrupt，同 T-04/T-06/T-07）：
    - 无 outline 或无 current_chapter_index（legacy 流）→ translate_code（不循环）
    - ``current_chapter_index`` < 6 → 回到 ``generate_chapter``（生成下一章）
    - ``current_chapter_index`` >= 6 → 进入 ``translate_code``（6 章全部完成）
    """
    outline = state.get("outline")
    idx = state.get("current_chapter_index")
    if not outline or idx is None:
        return "translate_code"
    if idx < len(CHAPTER_TYPES):
        return "generate_chapter"
    return "translate_code"


def route_after_clean(state: EconPaperState) -> str:
    """清洗后：无方向则停；有方向才进预写。"""
    rd = state.get("research_direction") or {}
    if isinstance(rd, dict) and (rd.get("question") or rd.get("dv")):
        return "set_direction"
    return END


def route_after_identification(state: EconPaperState) -> str | list[str]:
    """identification_verify 后的条件边路由。

    - 0 星 → HITL_pause（不进估计、不进文献）
    - 否则 → 估计与文献并行，扇入 generate_title
    """
    if state.get("star_rating") == 0:
        return "hitl_pause"
    return ["run_estimate", "search_literature"]


# ---------------------------------------------------------------------------
# Database-backed checkpointer (PostgresSaver)
# ---------------------------------------------------------------------------
_CHECKPOINTER: PostgresSaver | None = None


def _get_checkpointer() -> PostgresSaver:
    """Return the module-level PostgresSaver singleton.

    Connection string is read from env ``CHECKPOINT_DB_URL`` with a
    PostgreSQL default pointing at localhost.  Uses ``psycopg.connect``
    directly (not ``PostgresSaver.from_conn_string``, which is a context
    manager that closes the connection on exit — unsuitable for a module-
    level singleton).  Tables are created on first call via ``setup()``.
    """
    global _CHECKPOINTER
    if _CHECKPOINTER is not None:
        return _CHECKPOINTER

    url = os.getenv(
        "CHECKPOINT_DB_URL",
        "postgresql://mahaoxuan@localhost:5432/econpaper",
    )
    conn = psycopg.connect(
        url,
        autocommit=True,
        prepare_threshold=0,
    )
    saver = PostgresSaver(conn)
    saver.setup()  # create checkpoint/writes tables if missing
    _CHECKPOINTER = saver
    return _CHECKPOINTER


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def wire_prewrite_edges(builder: StateGraph) -> None:
    """预写边：识别后估计∥文献，两边结束后只进一次 generate_title。

    扇入必须用 add_edge([a, b], join)。两条独立边会让标题跑两次。
    """
    builder.add_edge(START, "upload_data")
    builder.add_edge("upload_data", "clean_data")
    builder.add_conditional_edges(
        "clean_data",
        route_after_clean,
        {
            "set_direction": "set_direction",
            END: END,
        },
    )
    builder.add_edge("set_direction", "identification_verify")
    builder.add_conditional_edges(
        "identification_verify",
        route_after_identification,
        {
            "hitl_pause": "hitl_pause",
            "run_estimate": "run_estimate",
            "search_literature": "search_literature",
        },
    )
    builder.add_edge("hitl_pause", "identification_verify")
    builder.add_edge("run_estimate", "robustness_check")
    builder.add_edge("search_literature", "build_citation_graph")
    builder.add_edge(
        ["robustness_check", "build_citation_graph"],
        "generate_title",
    )
    builder.add_edge("generate_title", "generate_outline")
    builder.add_edge("generate_outline", END)


def build_graph():
    """预写图：上传清洗后无方向即停；有方向则识别后估计∥文献，再标题→大纲。

    章节、评审、导出不编进这张图，由 Facade 调用。
    Facade 的 run_prewrite 仍串行，本函数只改图边。
    """
    builder = StateGraph(EconPaperState)

    builder.add_node("upload_data", upload_data)
    builder.add_node("clean_data", clean_data)
    builder.add_node("set_direction", set_direction)
    builder.add_node("identification_verify", identification_verify)
    builder.add_node("hitl_pause", hitl_pause)
    # Node id cannot equal a state key (LangGraph). State still uses `estimate`.
    builder.add_node("run_estimate", estimate)
    builder.add_node("robustness_check", robustness_check)
    builder.add_node("search_literature", search_literature)
    builder.add_node("build_citation_graph", build_citation_graph)
    builder.add_node("generate_title", generate_title)
    builder.add_node("generate_outline", generate_outline)

    wire_prewrite_edges(builder)

    checkpointer = _get_checkpointer()
    compiled = builder.compile(checkpointer=checkpointer)
    return compiled


class _Graph:
    """对编译后 graph 的轻量封装。

    checkpointer 要求调用时提供 thread_id；此处在不传 config 时
    注入默认 thread_id，使 graph.invoke(...) 可直接跑通（开发阶段便利）。
    底层编译后的 graph 仍携带 InMemorySaver。

    ADR-0004/0009 后 graph 节点数增加（search_literature / build_citation_graph
    / generate_references / review_chapter 迭代），LangGraph 默认 recursion_limit=25
    不够用。此处统一注入 50（6 章 × 2 迭代 × 2 节点 + 7 setup + 3 final = 34，
    留 buffer 给未来 ADR）。调用方传 config 时也合并该默认值，避免遗漏。
    """

    _DEFAULT_CONFIG = {
        "configurable": {"thread_id": "default"},
        "recursion_limit": 50,
    }
    _RECURSION_LIMIT = 50

    def __init__(self, compiled):
        self._compiled = compiled

    def _with_recursion_limit(self, config):
        """合并 recursion_limit 默认值到调用方 config（不覆盖显式设置）。"""
        if config is None:
            return self._DEFAULT_CONFIG
        if "recursion_limit" not in config:
            merged = dict(config)
            merged["recursion_limit"] = self._RECURSION_LIMIT
            return merged
        return config

    def invoke(self, input, config=None, **kwargs):
        config = self._with_recursion_limit(config)
        return self._compiled.invoke(input, config=config, **kwargs)

    def stream(self, input, config=None, **kwargs):
        config = self._with_recursion_limit(config)
        return self._compiled.stream(input, config=config, **kwargs)

    def __getattr__(self, name):
        return getattr(self._compiled, name)


graph = _Graph(build_graph())
