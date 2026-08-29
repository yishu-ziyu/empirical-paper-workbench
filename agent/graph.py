"""预写段 LangGraph 图。

本图**只覆盖预写段**（upload → clean → set_direction → identification →
estimate∥literature → robustness∥citation → title → outline）。章节生成 /
评审 / 导出等后续阶段**不在图中**，由 backend Facade 以 HITL 单点调用驱动
（如 ``facade.set_direction_and_outline`` 走 ``run_prewrite``、``generate_chapter``
节点按章就绪检查）。因此状态机里没有 ``generate_chapter`` / ``review_chapter`` /
``export_docx`` 等节点，也没有章节循环条件路由。

预写步骤的顺序规则（nodes 与顺序）统一来自 ``engine.prewrite.PRWRITE_SEQUENCE``：
- 本模块的 ``wire_prewrite_edges`` 用它的 ``dependencies`` 派生图边（并行扇入等）；
- ``engine.prewrite.run_prewrite``（Facade HITL 路径）按同一清单串行执行，
  二者收敛到单一真相，不再各自维护一份顺序。
"""
import logging
import os
from typing import Any

import psycopg
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph

from .engine.prewrite import PRWRITE_SEQUENCE, PRWRITE_NODES
from .nodes.clean_data import clean_data
from .nodes.hitl_pause import hitl_pause
from .nodes.upload_data import upload_data
# 以下预写节点名保留在模块命名空间，作为测试 monkeypatch 接缝
# （如 tests/test_graph_fanin.py 的 ``agent.graph.generate_title``）。
# 真正的节点注册来自 PRWRITE_NODES（单一真相），此处只作兼容别名。
from .nodes.citation_graph import build_citation_graph
from .nodes.estimate import estimate
from .nodes.generate_outline import generate_outline
from .nodes.generate_title import generate_title
from .nodes.identification_verify import identification_verify
from .nodes.robustness_check import robustness_check
from .nodes.search_literature import search_literature
from .nodes.set_direction import set_direction
from .state import EconPaperState


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
# Checkpointer: MemorySaver only when CHECKPOINT_DB_URL is unset/empty.
# URL set → PostgresSaver. Connect/setup failure fails loudly (no MemorySaver
# cache). Local boot must not require a live Postgres.
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

_CHECKPOINTER: Any = None


def _memory_saver() -> MemorySaver:
    return MemorySaver()


def _get_checkpointer() -> Any:
    """Return the module-level checkpointer singleton.

    - ``CHECKPOINT_DB_URL`` unset/empty → ``MemorySaver`` (local boot / tests).
    - URL set and Postgres reachable → ``PostgresSaver`` (connection kept open
      for the process; not ``from_conn_string``, which closes on exit).
      ``psycopg.connect`` uses ``connect_timeout=5`` so an unreachable host
      fails fast instead of blocking on TCP timeout.
    - URL set but connect/setup fails → raise; do not cache MemorySaver.

    Does not connect at import; first call builds the singleton.
    """
    global _CHECKPOINTER
    if _CHECKPOINTER is not None:
        return _CHECKPOINTER

    url = (os.getenv("CHECKPOINT_DB_URL") or "").strip()
    if not url:
        _CHECKPOINTER = _memory_saver()
        return _CHECKPOINTER
    conn = None
    try:
        conn = psycopg.connect(
            url,
            autocommit=True,
            prepare_threshold=0,
            connect_timeout=5,
        )
        saver = PostgresSaver(conn)
        saver.setup()  # create checkpoint/writes tables if missing
        _CHECKPOINTER = saver
        return _CHECKPOINTER
    except Exception:
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
        raise


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def wire_prewrite_edges(builder: StateGraph) -> None:
    """预写边，拓扑派生自 ``PRWRITE_SEQUENCE``。

    识别后 estimate∥search_literature 并行、robustness_check∥build_citation_graph
    并行，两边结束后只进一次 generate_title。扇入必须用 add_edge([a, b], join)，
    两条独立边会让标题跑两次。
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

    # 预写核心边：全部派生自 PRWRITE_SEQUENCE（单一真相）。两类由本图
    # 特有的结构接管，不在普通 `add_edge` 里重复：
    #  - identification_verify 的出边走条件路由（estimate∥literature / hitl_pause）；
    #  - generate_title 的入边合成等待边（waiting_edges），避免标题跑两次。
    _waiting: dict[str, list[str]] = {}
    for node_id, _fn, deps in PRWRITE_SEQUENCE:
        for dep in deps:
            # identification_verify 的出边由条件路由表达，不建普通边。
            if dep == "identification_verify":
                continue
            _waiting.setdefault(node_id, []).append(dep)

    # generate_title 是多前驱扇入点 → 用 waiting_edges 合成，不用独立边。
    for _node_id, preds in _waiting.items():
        joined = list(preds)
        if _node_id == "generate_title":
            builder.add_edge(joined, _node_id)
        else:
            for pred in joined:
                builder.add_edge(pred, _node_id)

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
    builder.add_edge("generate_outline", END)


def build_graph():
    """预写图：上传清洗后无方向即停；有方向则识别后估计∥文献，再标题→大纲。

    预写节点与顺序统一来自 ``engine.prewrite.PRWRITE_SEQUENCE``（单一真相，
    Facade 的 ``run_prewrite`` 走同一条清单）。本函数只补上传／清洗／HITL 暂停
    等命令行式路径不承载的节点与边。
    章节、评审、导出不编进这张图，由 Facade 调用。
    """
    builder = StateGraph(EconPaperState)

    builder.add_node("upload_data", upload_data)
    builder.add_node("clean_data", clean_data)
    for node_id, callable_fn in PRWRITE_NODES.items():
        builder.add_node(node_id, callable_fn)
    builder.add_node("hitl_pause", hitl_pause)

    wire_prewrite_edges(builder)

    checkpointer = _get_checkpointer()
    compiled = builder.compile(checkpointer=checkpointer)
    return compiled


class _Graph:
    """对编译后 graph 的轻量封装。

    默认惰性编译：``from graph import graph`` 不连接 Postgres。首次
    invoke/stream/属性访问才 ``build_graph()``。checkpointer 要求调用时
    提供 thread_id；此处在不传 config 时注入默认 thread_id，使
    graph.invoke(...) 可直接跑通（开发阶段便利）。

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

    def __init__(self, compiled=None):
        self._compiled = compiled

    def _ensure_compiled(self):
        if self._compiled is None:
            self._compiled = build_graph()
        return self._compiled

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
        return self._ensure_compiled().invoke(input, config=config, **kwargs)

    def stream(self, input, config=None, **kwargs):
        config = self._with_recursion_limit(config)
        return self._ensure_compiled().stream(input, config=config, **kwargs)

    def __getattr__(self, name):
        return getattr(self._ensure_compiled(), name)


# Public handle. Compiling at import used to open Postgres and 503 /upload
# when CHECKPOINT_DB_URL was unset. Compile on first use instead.
graph = _Graph()


def _reset_runtime() -> None:
    """Drop cached checkpointer/graph so tests can change CHECKPOINT_DB_URL."""
    global _CHECKPOINTER
    _CHECKPOINTER = None
    graph._compiled = None
