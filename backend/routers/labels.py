"""学习标签导出。点过的通过/否决写在文件里，不跟 session 内存一起丢。"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from schemas.labels import LabelEventResponse, LabelExportResponse

router = APIRouter()


@router.get("/labels", response_model=LabelExportResponse)
async def export_labels(
    session_id: Optional[str] = Query(default=None),
    reviewer_kind: Optional[str] = Query(default=None),
    ab_arm: Optional[str] = Query(default=None),
) -> LabelExportResponse:
    from agent.nodes.label_store import read_events, summarize

    events = read_events(
        session_id=session_id,
        reviewer_kind=reviewer_kind,
        ab_arm=ab_arm,
    )
    parsed = []
    for item in events:
        parsed.append(
            LabelEventResponse(
                event_id=str(item.get("event_id") or ""),
                ts=str(item.get("ts") or ""),
                session_id=item.get("session_id"),
                chapter_index=item.get("chapter_index"),
                chapter_type=item.get("chapter_type"),
                reviewer=item.get("reviewer"),
                reviewer_kind=str(item.get("reviewer_kind") or "human"),
                persona=item.get("persona"),
                ab_arm=str(item.get("ab_arm") or "human"),
                decision=str(item.get("decision") or ""),
                comment=item.get("comment"),
                auto_decision=item.get("auto_decision"),
                agreed_with_auto=item.get("agreed_with_auto"),
                labels=list(item.get("labels") or []),
                packet_id=item.get("packet_id"),
                judge_source=item.get("judge_source"),
            )
        )
    return LabelExportResponse(
        n=len(parsed),
        events=parsed,
        summary=summarize(events),
    )
