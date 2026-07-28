"""ADR-0007: HITL 人工评审 Pydantic 响应 / 请求模型。

这些模型是 review router 的 response_model 单一来源，FastAPI 据此生成
OpenAPI schema，前端通过 ``openapi-typescript`` codegen 消费
（遵循 ADR 0003 codegen 契约）。
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ReviewRubricResponse(BaseModel):
    """经济学论文评审 5 维 rubric 分项（每维度 0-1，缺失为 None）。"""

    endogeneity: Optional[float] = None      # 内生性处理
    identification: Optional[float] = None   # 识别策略清晰度
    robustness: Optional[float] = None       # 稳健性
    contribution: Optional[float] = None     # 贡献度
    readability: Optional[float] = None      # 可读性


class ReviewInfoResponse(BaseModel):
    """GET /sessions/{id}/review 返回体：当前章评审信息。"""

    chapter_index: int
    feedback: str
    suggestions: str
    score: float
    rubric: ReviewRubricResponse
    review_iteration: int
    max_review_iterations: int
    auto_decision: str  # "pass" | "fail"


class ReviewDecisionRequest(BaseModel):
    """POST /sessions/{id}/review/decision 请求体。"""

    decision: str  # "accept" | "reject" | "force_pass"
    reviewer: Optional[str] = None
    comment: Optional[str] = None


class ReviewDecisionResponse(BaseModel):
    """POST /sessions/{id}/review/decision 返回体。"""

    ok: bool
    decision: str
    chapter_index: int
    next_action: str  # "proceed" | "regenerate"
