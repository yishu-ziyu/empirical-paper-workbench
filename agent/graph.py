from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from nodes.clean_data import clean_data
from nodes.citation_graph import build_citation_graph
from nodes.export_docx import export_docx
from nodes.generate_chapter import generate_chapter
from nodes.generate_outline import generate_outline
from nodes.generate_references import generate_references
from nodes.generate_title import generate_title
from nodes.review_chapter import review_chapter
from nodes.route_after_review import route_after_review
from nodes.search_literature import search_literature
from nodes.set_direction import set_direction
from nodes.translate_code import translate_code
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


def build_graph():
    """构建 LangGraph 骨架（含 T-08a 6 章条件边循环 + ADR-0004 评审 + ADR-0009 引用图谱）。

    流转：START -> upload_data -> clean_data -> generate_title -> set_direction
          -> search_literature -> build_citation_graph -> generate_outline
          -> generate_chapter -> review_chapter
          -(条件边 route_after_review)->
            评审不通过且未达迭代上限: 回 generate_chapter（重生成当前章）
            评审通过或达上限: route_after_chapter 决定
              current_chapter_index < 6: 回 generate_chapter（下一章）
              current_chapter_index >= 6: translate_code -> generate_references -> export_docx -> END
    使用 InMemorySaver 作为 checkpointer（开发阶段）。
    """
    builder = StateGraph(EconPaperState)

    builder.add_node("upload_data", upload_data)
    builder.add_node("clean_data", clean_data)
    builder.add_node("generate_title", generate_title)
    builder.add_node("set_direction", set_direction)
    builder.add_node("search_literature", search_literature)
    builder.add_node("build_citation_graph", build_citation_graph)
    builder.add_node("generate_outline", generate_outline)
    builder.add_node("generate_chapter", generate_chapter)
    builder.add_node("review_chapter", review_chapter)
    builder.add_node("translate_code", translate_code)
    builder.add_node("generate_references", generate_references)
    builder.add_node("export_docx", export_docx)

    builder.add_edge(START, "upload_data")
    builder.add_edge("upload_data", "clean_data")
    builder.add_edge("clean_data", "generate_title")
    builder.add_edge("generate_title", "set_direction")
    builder.add_edge("set_direction", "search_literature")
    # ADR-0009: search_literature 后构建引用图谱，再进 generate_outline
    builder.add_edge("search_literature", "build_citation_graph")
    builder.add_edge("build_citation_graph", "generate_outline")
    builder.add_edge("generate_outline", "generate_chapter")
    # ADR-0004: generate_chapter 后顺序进入 review_chapter（评审节点只读不写 body_chapters）
    builder.add_edge("generate_chapter", "review_chapter")
    # ADR-0004: review_chapter 后条件边 route_after_review
    #   评审不通过且未达上限 → "generate_chapter"（重生成，review_chapter 已回退 idx）
    #   评审通过或达上限 → "translate_code"（route_after_review 内部委托 route_after_chapter）
    builder.add_conditional_edges(
        "review_chapter",
        route_after_review,
        {
            "generate_chapter": "generate_chapter",
            "translate_code": "translate_code",
        },
    )
    # ADR-0009: translate_code 后生成参考文献列表，再进 export_docx
    builder.add_edge("translate_code", "generate_references")
    builder.add_edge("generate_references", "export_docx")
    builder.add_edge("export_docx", END)

    checkpointer = InMemorySaver()
    graph = builder.compile(checkpointer=checkpointer)
    return graph


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
