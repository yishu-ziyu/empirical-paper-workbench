"""共享 Pydantic 模型，对应 OpenAPI 规范 v1 (Product/api/openapi.yaml)。

约定：
- 后端 service / endpoint 用这些模型做 IO 校验
- 前端 TypeScript 类型 (Product/web-react/src/types/research.ts) 字段名与之一致
- model 字段约定：MiniMax-M3（spec §3.2 唯一真实模型）
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# ============== 任务书 (Brief) ==============

class BriefRequest(BaseModel):
    """任务书请求。topic 必填，slug 可选（自动生成）。"""
    topic: str
    topic_slug: Optional[str] = None


class BriefResponse(BaseModel):
    """任务书响应。verdict_passed=True 表示 4 段齐全。"""
    brief_markdown: str
    brief_path: str
    verdict_passed: bool


# ============== 递归搜索 (Search) ==============

class Paper(BaseModel):
    """单篇 arxiv 论文。"""
    title: str
    authors: List[str]
    year: int
    abstract: str
    arxiv_id: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    accepted: bool = True


class SearchRequest(BaseModel):
    """递归搜索请求。需要 brief_path 喂入研究简报上下文。"""
    topic_slug: str
    brief_path: str


class SearchResponse(BaseModel):
    """递归搜索响应。verdict_passed=True 表示 paper 数 >= 8 且都有 relevance_score。"""
    literature_markdown: str
    literature_path: str
    papers: List[Paper]
    verdict_passed: bool


# ============== 数据变量 (Variables) ==============

class Variable(BaseModel):
    """单个研究变量。"""
    role: Literal["X", "Y", "control", "mediator", "moderator"]
    dataset_column: str
    semantic_label: str
    description: str
    reference_papers: List[str] = Field(default_factory=list)


class VariablesRequest(BaseModel):
    """数据变量识别请求。dataset_name 指定数据集；custom 时传 custom_dataset_path。"""
    topic_slug: str
    brief_path: str
    dataset_name: Literal["CFPS", "CHIP", "CHARLS", "custom"]
    custom_dataset_path: Optional[str] = None


class VariablesResponse(BaseModel):
    """数据变量识别响应。verdict_passed=True 表示至少 1 个 X + 1 个 Y。"""
    variables_yaml: str
    variables_path: str
    variables: List[Variable]
    verdict_passed: bool


# ============== 方法设计 (Design) ==============

class DesignCandidate(BaseModel):
    """单个方法候选。"""
    method: Literal["DID", "IV", "RDD", "PSM", "DML"]
    rationale: str
    fits_data: bool
    sp_output: dict = Field(default_factory=dict)


class DesignRequest(BaseModel):
    """方法设计请求。需要 variables_path 喂入变量映射。"""
    topic_slug: str
    variables_path: str
    brief_path: str


class DesignResponse(BaseModel):
    """方法设计响应。verdict_passed=True 表示 candidates >= 3 + 有 recommended。"""
    design_json: str
    design_path: str
    candidates: List[DesignCandidate]
    recommended: str
    code_stub: str
    verdict_passed: bool


# ============== 执行实验 (Execution) ==============

class ExecuteRequest(BaseModel):
    """执行实验请求。需要 design_path + variables_path + brief_path 三件套。"""
    topic_slug: str
    design_path: str
    variables_path: str
    brief_path: str


class ExecuteEvent(BaseModel):
    """SSE 流式事件。event 类型见 spec §4.5。"""
    event: Literal["start", "progress", "section_done", "paper_ready", "done", "error"]
    stage: str
    message: str
    section_index: Optional[int] = None
    paper_pdf_path: Optional[str] = None
    results_json_path: Optional[str] = None
