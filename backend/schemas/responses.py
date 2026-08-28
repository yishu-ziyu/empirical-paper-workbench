"""Pydantic v2 response models for the econpaper backend (Stage D).

These models are the single source of truth for the JSON shape returned by
each endpoint. FastAPI uses them to generate OpenAPI schemas, which the
frontend consumes via ``openapi-typescript`` to produce ``types/api.ts``.

Naming convention: ``XxxResponse`` for endpoint return types.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared / nested models
# ---------------------------------------------------------------------------


class DatasetMetaResponse(BaseModel):
    """单个数据集的元信息（upload 返回 / state.uploaded_datasets[]）。"""

    name: Optional[str] = None
    path: Optional[str] = None
    format: Optional[str] = None
    columns: List[str] = Field(default_factory=list)
    rows: Optional[int] = None
    dtypes: Dict[str, Any] = Field(default_factory=dict)
    missing_count: Optional[int] = None
    session_id: Optional[str] = None
    status: Optional[str] = None


class ChapterResponse(BaseModel):
    """论文章节（generate_title / generate_chapter 写入）。

    status 枚举：``generated`` | ``approved`` | ``edited`` | ``rolled_back``。
    前端可在本地临时态再加 ``streaming`` / ``done``。
    """

    type: str = ""
    title: str = ""
    content: Optional[str] = None
    status: Optional[str] = None
    versions: List[str] = Field(default_factory=list)
    chapter_index: Optional[int] = None

    model_config = {"extra": "allow"}


class OutlineChapterResponse(BaseModel):
    """大纲章节项（outline 列表元素，DirectionResponse / ResumeResponse 引用）。

    放在共享区，避免 DirectionResponse 引用时出现前向引用。
    """

    type: str = ""
    title: str = ""
    research_question: Optional[str] = None

    model_config = {"extra": "allow"}


# ---------------------------------------------------------------------------
# sessions.py
# ---------------------------------------------------------------------------


class UploadResponse(BaseModel):
    """POST /upload 返回体。"""

    session_id: str
    dataset_meta: DatasetMetaResponse


class CreateSessionResponse(BaseModel):
    """POST /sessions 返回体。"""

    session_id: str


class SessionInfoResponse(BaseModel):
    """GET /sessions/{id} 返回体：会话存在性 + 刷新后要保住的读数。"""

    session_id: str
    exists: bool
    has_dataset: bool = False
    claim: Optional[str] = None
    star_rating: Optional[int] = None
    identification_failed: bool = False
    identification_report: Optional[str] = None
    results: Optional[str] = None
    estimate: Any = None
    literature_source: Optional[str] = None
    write_blockers: List[str] = Field(default_factory=list)
    robustness_status: Optional[str] = None
    outline: List[OutlineChapterResponse] = Field(default_factory=list)
    body_chapters: List[ChapterResponse] = Field(default_factory=list)
    research_direction: Any = None


# ---------------------------------------------------------------------------
# outline.py
# ---------------------------------------------------------------------------


class DirectionResponse(BaseModel):
    """POST /sessions/{id}/direction 返回体。"""

    outline: List[OutlineChapterResponse] = Field(default_factory=list)
    research_direction: Any = None
    star_rating: Optional[int] = None
    identification_failed: bool = False
    identification_report: Optional[str] = None
    results: Optional[str] = None
    estimate: Any = None
    claim: Optional[str] = None
    literature_source: Optional[str] = None
    degradations: List[Any] = Field(default_factory=list)
    write_blockers: List[str] = Field(default_factory=list)
    robustness_status: Optional[str] = None


class ResumeResponse(BaseModel):
    """POST /sessions/{id}/resume 返回体。"""

    ok: bool
    outline: List[OutlineChapterResponse] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# chapter.py
# ---------------------------------------------------------------------------


class GenerateChapterResponse(BaseModel):
    """POST /sessions/{id}/generate-chapter 返回体。"""

    chapter: ChapterResponse
    body_chapters: List[ChapterResponse] = Field(default_factory=list)
    score: Optional[float] = None
    auto_decision: Optional[str] = None  # "pass" | "fail"
    review_source: Optional[str] = None
    review_degraded: bool = False
    grounding_failures: List[str] = Field(default_factory=list)


class ApproveChapterResponse(BaseModel):
    """POST /sessions/{id}/approve-chapter 返回体。"""

    ok: bool
    chapter: ChapterResponse
    body_chapters: List[ChapterResponse] = Field(default_factory=list)


class RollbackResponse(BaseModel):
    """POST /sessions/{id}/rollback 返回体。"""

    chapter: ChapterResponse
    body_chapters: List[ChapterResponse] = Field(default_factory=list)


class RegenerateResponse(BaseModel):
    """POST /sessions/{id}/regenerate 返回体。"""

    chapter: ChapterResponse
    body_chapters: List[ChapterResponse] = Field(default_factory=list)
    score: Optional[float] = None
    auto_decision: Optional[str] = None  # "pass" | "fail"
    review_source: Optional[str] = None
    review_degraded: bool = False
    grounding_failures: List[str] = Field(default_factory=list)


class EditChapterResponse(BaseModel):
    """POST /sessions/{id}/edit-chapter 返回体。

    与 regenerate 同形：改过的章 + 全表。instruction 走 generate_chapter
    时附带评审字段；content 落盘不审，评审字段为空。
    """

    chapter: ChapterResponse
    body_chapters: List[ChapterResponse] = Field(default_factory=list)
    score: Optional[float] = None
    auto_decision: Optional[str] = None  # "pass" | "fail"
    review_source: Optional[str] = None
    review_degraded: bool = False
    grounding_failures: List[str] = Field(default_factory=list)


class ChapterVersionItem(BaseModel):
    """单个版本预览项。"""

    index: int
    preview: str


class VersionsResponse(BaseModel):
    """GET /sessions/{id}/chapters/{chapter_index}/versions 返回体。"""

    chapter_index: int
    count: int
    versions: List[ChapterVersionItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# progress.py
# ---------------------------------------------------------------------------


class ProgressChapterSummary(BaseModel):
    """progress 端点返回的章节概要。"""

    type: Optional[str] = None
    title: Optional[str] = None
    status: Optional[str] = None


class ProgressResponse(BaseModel):
    """GET /sessions/{id}/progress 返回体。"""

    total: int
    completed: int
    current: Optional[Union[int, str]] = None
    body_chapters: List[ProgressChapterSummary] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# journey.py (8-stage research journey)
# ---------------------------------------------------------------------------


class JourneyStageItem(BaseModel):
    """8 阶段研究旅程的单个阶段状态。"""

    status: str  # pending / active / completed / interrupt
    canIntervene: bool = False


class JourneyResponse(BaseModel):
    """GET /sessions/{id}/journey 返回体：8 阶段旅程整体进度。

    阶段（0-index）：
    0 选题 1 文献 2 数据清洗 3 识别策略 4 估计建模 5 稳健性审计 6 写作评审 7 降AIGC导出
    可介入：{0, 2, 3, 5, 6}
    """

    currentStage: int
    stages: List[JourneyStageItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# sample.py
# ---------------------------------------------------------------------------


class TransformResponse(BaseModel):
    """POST /sessions/{id}/transform 返回体。"""

    constructed_vars: List[str] = Field(default_factory=list)


class FilterCondition(BaseModel):
    """filter 条件项。"""

    col: str
    op: str
    val: Any = None

    model_config = {"extra": "allow"}


class FilterResultResponse(BaseModel):
    """POST /sessions/{id}/filter 返回体。"""

    n_before: int
    n_after: int
    conditions: List[Any] = Field(default_factory=list)


class BalanceResponse(BaseModel):
    """POST /sessions/{id}/balance 返回体。

    修复漂移 1：统一字段名为 ``balanced`` / ``unbalanced`` / ``n_periods``
    / ``attrition_rate``。后端 BalanceStep 的 step report 只含
    ``balanced`` / ``n_periods`` / ``attrition_rate``，``unbalanced`` 在
    router 层补算（balanced 减去总 panel 数，或在 facade 层补）。
    """

    balanced: int = 0
    unbalanced: int = 0
    n_periods: int = 0
    attrition_rate: float = 0.0


# ---------------------------------------------------------------------------
# charls.py
# ---------------------------------------------------------------------------


class CharlsDetectResponse(BaseModel):
    """GET /sessions/{id}/charls/detect 返回体。"""

    dataset_type: str
    charls_config: Optional[Dict[str, Any]] = None


class CharlsConfirmResponse(BaseModel):
    """POST /sessions/{id}/charls/confirm 返回体。"""

    ok: bool
    charls_config: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# eda.py
# ---------------------------------------------------------------------------


class EdaResponse(BaseModel):
    """POST /sessions/{id}/eda 返回体。

    EDA 动作返回的 shape 因 action 而异（describe / corr / missing /
    placeholder），统一用 ``Any`` 承载具体字段，但保留 ``action`` 标识。
    describe / corr / missing 的结构由各 action 的实现决定，前端按
    ``action`` 分支渲染。
    """

    action: Optional[str] = None
    result: Any = None

    model_config = {"extra": "allow"}


# ---------------------------------------------------------------------------
# Cleaning-related shared models (用于前端 codegen 引用)
# ---------------------------------------------------------------------------
# 这些模型没有直接的 endpoint 暴露，但通过 ``ProgressResponse`` /
# ``GenerateChapterResponse`` 等间接引用，或作为 OpenAPI components.schemas
# 出现，前端 codegen 会生成对应类型。


class VariableInfoResponse(BaseModel):
    """profiling 的单变量信息。"""

    dtype: str = ""
    missing_rate: float = 0.0
    n_unique: int = 0
    is_numeric: bool = False


class ProfileResponse(BaseModel):
    """profiling 报告。

    修复漂移 3：补 ``dataset_type`` 和 ``charls_config`` 字段（后端
    ``agent/cleaning/profiling.py`` 已经写入，前端原本缺失）。
    """

    n_rows: int = 0
    n_cols: int = 0
    variables: Dict[str, VariableInfoResponse] = Field(default_factory=dict)
    dataset_type: Optional[str] = None
    charls_config: Optional[Dict[str, Any]] = None

    model_config = {"extra": "allow"}


class DistStatsResponse(BaseModel):
    """outlier 缩尾前后的单变量分布统计。"""

    min: Optional[float] = None
    max: Optional[float] = None
    mean: Optional[float] = None


class OutlierDatasetReport(BaseModel):
    """单数据集的 outlier 报告（dataset-level，Record 结构）。

    后端 ``OutliersStep`` 在 ``ds["outliers"]`` 写入此结构；step report
    的 ``before`` / ``after`` 是 ``list[dict]``（多数据集聚合），前端
    CleanWizard 目前消费 dataset-level 的 Record 结构。
    """

    before: Dict[str, DistStatsResponse] = Field(default_factory=dict)
    after: Dict[str, DistStatsResponse] = Field(default_factory=dict)
    iqr_outliers: Dict[str, int] = Field(default_factory=dict)
    winsorized: bool = False


class OutlierStepReportResponse(BaseModel):
    """outlier step report（与后端 step report 一致，list 结构）。

    修复漂移 2：step report 的 ``before`` / ``after`` 是 ``list[dict]``，
    每个元素是该数据集的 ``Record<string, DistStats>``。前端若直接消费
    step report 应使用 list 结构。
    """

    before: List[Dict[str, DistStatsResponse]] = Field(default_factory=list)
    after: List[Dict[str, DistStatsResponse]] = Field(default_factory=list)
    iqr_outliers: List[Dict[str, int]] = Field(default_factory=list)
    winsorized: List[bool] = Field(default_factory=list)
