"""ADR-0003 Stage A: NodeResult 协议类型。

每个节点入口函数返回一个 partial state dict（LangGraph 语义：只含该节点
写入的键）。这里为每个节点定义对应的 *Output TypedDict，让 mypy/pyright
能检查返回值的键名，消除裸 ``dict`` 带来的魔法字符串。

约束：
- 所有 *Output 字段集 ⊆ EconPaperState.__annotations__.keys()（由
  ``tests/test_schema_consistency.py`` 强制）
- ``total=False``：节点按需返回子集
- ``NodeResult`` 是 TypeVar，bound=Mapping[str, Any]，兼容 LangGraph 的
  partial state dict 语义，供后续 Stage B/C 做 Protocol/泛型收窄
"""
from typing import Any, Dict, List, Mapping, Optional, TypeVar, TypedDict

from state import Chapter, DatasetMeta

# NodeResult 协议类型：所有节点返回值的基类型
# 用 Mapping[str, Any] 作为 bound，兼容 LangGraph 的 partial state dict 语义
NodeResult = TypeVar("NodeResult", bound=Mapping[str, Any])


class UploadDataOutput(TypedDict, total=False):
    uploaded_datasets: List[DatasetMeta]


class CleanDataOutput(TypedDict, total=False):
    csv_path: Optional[str]
    uploaded_datasets: List[DatasetMeta]
    cleaned_datasets: List[DatasetMeta]
    cleaning_report: Any  # {"steps": list[StepReport]}


class GenerateTitleOutput(TypedDict, total=False):
    title_chapter: Chapter


class SetDirectionOutput(TypedDict, total=False):
    research_direction: Any
    main_specification: Any


class EstimateOutput(TypedDict, total=False):
    results: str
    estimate: Any


class GenerateOutlineOutput(TypedDict, total=False):
    outline: Any
    current_chapter_index: int


class GenerateChapterOutput(TypedDict, total=False):
    body_chapters: List[Chapter]
    current_chapter_index: int
    write_blocked: bool
    write_blockers: List[str]


class TranslateCodeOutput(TypedDict, total=False):
    code_translations: List[Any]


class ExportDocxOutput(TypedDict, total=False):
    latex_source: str
    pdf_path: str
    docx_path: str
    degraded: bool


class ApproveChapterOutput(TypedDict, total=False):
    body_chapters: List[Chapter]
    chapter_statuses: List[str]


class RollbackOutput(TypedDict, total=False):
    body_chapters: List[Chapter]


# ADR-0004: 文献检索节点输出
class LiteratureEntry(TypedDict, total=False):
    """单条文献条目（search_literature 写入 literature_entries 列表）。"""

    title: str
    authors: List[str]
    year: int
    abstract: str
    doi: Optional[str]
    source: str  # "mock" | "semantic_scholar"
    relevance_score: float  # 0-1


class LiteratureOutput(TypedDict, total=False):
    """search_literature 节点返回值（NodeResult 协议）。"""

    literature_entries: List[LiteratureEntry]
    literature_query: str
    literature_source: str
    literature_produced_by: str
    literature_actions: List[str]


# ADR-0004: 章节评审节点输出
class ReviewRubric(TypedDict, total=False):
    """经济学论文评审 5 维 rubric（每维度 0-1）。"""

    endogeneity: float  # 内生性处理（IV/DID/RD/自然实验）
    identification: float  # 识别策略清晰度
    robustness: float  # 稳健性（样本/设定/安慰剂）
    contribution: float  # 贡献度（理论/实证/政策）
    readability: float  # 可读性（结构/逻辑/表达）


class ReviewOutput(TypedDict, total=False):
    """review_chapter 节点返回值（NodeResult 协议）。

    注意：不含 body_chapters 字段 —— 评审节点不改正文。
    #8：文献综述章可回写 literature_entries 的 relevance_score。
    """

    review_feedback: List[str]
    revision_suggestions: List[str]
    review_scores: List[float]
    review_rubrics: List[ReviewRubric]
    review_iteration: int
    review_chapter_index: int
    current_chapter_index: int  # 仅在判定不通过、需回退时写入
    review_source: str  # "llm" | "mock" | "mock_fallback"
    review_degraded: bool
    grounding_failures: List[str]
    literature_entries: List[LiteratureEntry]
    learning_labels: List[Any]


# ADR-0009: 引用图谱与参考文献列表
class CitationEntry(TypedDict, total=False):
    """参考文献条目（含引用编号）。"""

    entry: LiteratureEntry  # 原文献
    citation_index: int  # [1] [2] ...
    cited_in_chapters: List[int]  # 在哪些章节被引用


class CitationGraphOutput(TypedDict, total=False):
    """build_citation_graph 节点返回值。"""

    citation_graph: Any
    citation_indices: Dict[str, int]
    literature_entries: List[LiteratureEntry]
    literature_actions: List[str]


class ReferencesOutput(TypedDict, total=False):
    """generate_references 节点返回值。"""

    references_list: List[Any]
