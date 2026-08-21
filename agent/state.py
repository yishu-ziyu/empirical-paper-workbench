from typing import Any, Dict, List, Optional, TypedDict


class DatasetMeta(TypedDict, total=False):
    """单个数据集的元信息（upload_data 节点写入）。"""

    name: str
    path: str
    format: str
    columns: List[str]
    rows: int
    dtypes: dict
    missing_count: int
    session_id: str   # ADR-0003: upload 占位分支写入
    status: str       # ADR-0003: upload 占位分支写入


class Chapter(TypedDict, total=False):
    """论文章节（generate_title / generate_chapter 写入）。

    versions[0] 是最新版本，regenerate 时新版本 prepend；
    rollback 用 version_index 取回旧版本。
    """

    type: str
    title: str
    content: str
    status: str  # "generated" | "approved" | "edited" | "rolled_back"
    versions: List[str]  # 版本历史，versions[0] 是最新
    chapter_index: int  # 0-5，body_chapters 索引


class EconPaperState(TypedDict, total=False):
    """LangGraph 状态 schema。

    所有字段均为可选（total=False），节点按需写入子集，向后兼容占位阶段。
    """

    session_id: Optional[str]
    csv_path: Optional[str]
    uploaded_datasets: List[DatasetMeta]
    # T-04/T-05: clean_data 子步骤（HITL 策略 + 清洗报告）
    missing_strategy: Optional[str]
    # ADR-0002: cleaning_report = {"steps": list[StepReport]}，每步含 name/status/started_at/duration/report
    cleaning_report: Optional[Any]
    cleaned_datasets: List[DatasetMeta]  # ADR-0002: clean_data 写入的清洗后 datasets
    # T-05: clean_data 后 4 子步骤的配置（可选，缺失时跳过对应子步骤）
    transform_config: Optional[Any]
    filter_conditions: Optional[List[Any]]
    panel_id: Optional[str]
    time_col: Optional[str]
    workspace: Optional[str]
    title_chapter: Chapter           # 由 generate_title 写入，单数
    body_chapters: List[Chapter]     # 由 generate_chapter 按 idx 写入，6 项
    # T-08a: 章节循环 + 版本历史
    current_chapter_index: int  # body_chapters 索引（0-5）
    chapter_statuses: List[str]  # 6 章的审批状态
    # 以下为占位字段，后续 ticket 逐步填充
    eda_results: List[Any]
    research_direction: Optional[dict]
    main_specification: Optional[dict]  # robustness_check / spec_curve 主设定
    spec_curve: Optional[dict]  # 探索臂设定表（全部规格留在桌上）
    outline: Optional[Any]
    # T-06: 用户在前端拖拽调整后的 outline (HITL resume 路径写入)
    user_adjusted_outline: Optional[Any]
    code_translations: List[Any]
    latex_source: Optional[str]
    export_formats: List[Any]
    # ADR-0003: HITL 顶层入参（approve/rollback/export 节点读，backend 写入）
    chapter_index: Optional[int]      # approve/rollback 目标章节索引
    version_index: Optional[int]     # rollback 目标版本索引
    # ADR-0003: export_docx 配置与产出（HITL 入参 + 节点产出）
    export_template: Optional[str]   # 默认 "cn_journal"
    author: Optional[str]
    abstract: Optional[str]
    pdf_path: Optional[str]
    docx_path: Optional[str]
    degraded: bool
    # ADR-0003: clean_data 高级配置
    outliers_cuts: tuple  # (low, high) 百分位，默认 (5, 95)
    # ADR-0003: generate_chapter render kwargs（模板占位符，backend 或 EDA 写入）
    research_question: Optional[str]
    data_summary: Optional[str]
    key_references: Optional[str]
    results: Optional[str]
    # ADR-0004: 文献检索（search_literature 节点写入）
    literature_entries: List[Any]  # List[LiteratureEntry]，见 protocols.py
    literature_query: Optional[str]
    literature_source: Optional[str]  # "mock" | "semantic_scholar" | "disabled"
    literature_produced_by: Optional[str]
    literature_actions: List[str]  # #11: keyword / method_anchor / threat / citation_hop
    write_blocked: bool
    write_blockers: List[str]
    claim: Optional[str]
    degradations: List[Any]
    # ADR-0004: 章节评审（review_chapter 节点写入）
    review_feedback: List[str]
    revision_suggestions: List[str]
    review_scores: List[float]
    review_rubrics: List[Any]  # List[ReviewRubric]，见 protocols.py
    review_iteration: int
    review_chapter_index: Optional[int]
    review_enabled: bool
    max_review_iterations: int
    review_source: str  # "llm" | "mock" | "mock_fallback"
    review_degraded: bool
    grounding_failures: List[str]
    # ADR-0007: HITL 人工评审（叠加层，默认关闭）
    hitl_review_enabled: bool           # 是否启用人工评审暂停点（默认 False）
    hitl_decision: Optional[str]        # "accept" | "reject" | "force_pass"
    hitl_reviewer: Optional[str]        # 评审人标识（用户名 / open_id）
    hitl_comment: Optional[str]         # 评审人备注（可选）
    learning_labels: List[Any]  # #11: 真事件标签，不含 mock 分数
    # ADR-0009: 引用图谱
    citation_graph: Optional[Any]  # {entries: [...], edges: [{from, to}], indices: {doi: int}}
    references_list: List[Any]  # 最终参考文献列表 [{index, text, doi, entry}]
    citation_indices: Dict[str, int]  # doi → 引用编号 [1] [2] ...
    # 识别策略验证（identification_verify 节点写入）
    identification_diag: Optional[dict]  # {strategy: str, diagnostics: list[dict], passed: bool, report: str, star_rating: int}
    identification_failed: Optional[bool]  # True = 诊断不通过，需用户调整
    star_rating: Optional[int]  # 0-3 星：0=完全不可信（0星截断），1-2=继续但标注，3=最佳
    # HITL_pause：0星截断后等待用户调整研究方向的图内中断点
    hitl_pause_reason: Optional[str]  # "identification_0star" 等
    # 稳健性检验（robustness_check 节点写入）
    robustness_results: Optional[dict]  # {robustness: list[dict], heterogeneity: list[dict], placebos: list[dict], summary_table: str}
    # 主估计（estimate 节点写入）。results 是结果章 prompt 的 {results}。
    results: Optional[str]
    estimate: Optional[dict]
