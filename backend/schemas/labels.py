"""学习标签落盘后的导出模型。"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LabelEventResponse(BaseModel):
    event_id: str
    ts: str
    session_id: Optional[str] = None
    chapter_index: Optional[int] = None
    chapter_type: Optional[str] = None
    reviewer: Optional[str] = None
    reviewer_kind: str
    persona: Optional[str] = None
    ab_arm: str
    decision: str
    comment: Optional[str] = None
    auto_decision: Optional[str] = None
    agreed_with_auto: Optional[bool] = None
    labels: List[Dict[str, Any]] = Field(default_factory=list)
    packet_id: Optional[str] = None
    judge_source: Optional[str] = None


class LabelExportResponse(BaseModel):
    n: int
    events: List[LabelEventResponse]
    summary: Dict[str, Any]
