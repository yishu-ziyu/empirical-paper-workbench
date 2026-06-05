"""POST /api/auto-research/start — SSE endpoint for auto-research mode.

Mirrors /api/brief/stream but for the `auto-research` mode picked at intake.
The frontend (AutoResearchStream.tsx) consumes 4 step events and the
final_brief event, then auto-advances to the search tab without user
intervention.

Event types match BriefEvent so the same consumer shape works:
  - step_start  {step_index, title}
  - step_delta  {step_index, text}
  - step_done   {step_index, summary}
  - final_brief {markdown, brief_path, verdict_passed}
  - done
  - error       {message}

In a real LLM environment this would call chat_completion_stream. For
intake-time preview we emit synthetic step events derived from the topic
(plus the 4 brief sections), so the SSE plumbing is exercised end-to-end
without waiting for variable roles / design specs to be confirmed.
"""
from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import AsyncIterator

import yaml
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from Product.api._paths import TASKS_ROOT

router = APIRouter()


class AutoResearchStartRequest(BaseModel):
    topic: str = Field(min_length=1)
    topic_slug: str | None = None
    max_steps: int = Field(default=4, ge=1, le=8)


STEP_TITLES = {
    1: "扫描题目意图",
    2: "匹配本地数据与文献",
    3: "拟定方法与变量",
    4: "写出研究简报",
}


def _slugify(topic: str) -> str:
    ascii_part = re.sub(r"[^a-zA-Z0-9]+", "-", topic).strip("-").lower()[:50]
    return ascii_part or "untitled"


def _render_step_text(step_index: int, topic: str) -> str:
    """Synthetic step text. Kept short and topical."""
    if step_index == 1:
        return f"题目意图分析: 围绕『{topic}』抽取核心因变量、处理变量、识别假说与边界。\n"
    if step_index == 2:
        return (
            "本地数据匹配: 扫描 Data/ 与 final/ 目录, 优先选取含 `ln_wage` / `robot` 字段的 CSV.\n"
            "文献线索: 暂无本地文献, 计划在 search 阶段调 arxiv.\n"
        )
    if step_index == 3:
        return (
            "方法候选: OLS baseline + DID/IV 上行升级, 视数据时点分布决定具体识别方程.\n"
            "变量角色: outcome=ln_wage, treatment=robot_exposure, control=age/edu/gender/urban.\n"
        )
    if step_index == 4:
        return (
            f"## 研究问题\n\n本研究关注『{topic}』的核心因果识别问题。\n\n"
            "## 边际贡献\n\n- 利用本地数据提供新证据\n- 提供可复现的代码 + 流程\n\n"
            "## 研究边界\n\n- 仅使用本地可用数据, 暂不纳入全国样本\n- 识别策略在数据确认后决定\n\n"
            "## 成功标准\n\n- 主要系数显著 (p<0.05) 且方向符合理论\n- 稳健性检验通过 ≥ 1 项\n"
        )
    return ""


def _write_brief_disk(content: str, topic: str, topic_slug: str) -> Path:
    """落盘 Tasks/{slug}/brief.md with YAML frontmatter (same shape as brief_stream_service)."""
    topic_dir = TASKS_ROOT / topic_slug
    topic_dir.mkdir(parents=True, exist_ok=True)
    path = topic_dir / "brief.md"
    frontmatter = yaml.safe_dump(
        {
            "topic": topic,
            "topic_slug": topic_slug,
            "generated_by": "auto-research-sse",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model": "auto-research-preview",
            "prompt_version": "auto-research-v1",
            "upstream": False,
            "downstream_consumers": ["literature.md", "variables.yaml"],
        },
        allow_unicode=True,
        sort_keys=False,
    )
    path.write_text(f"---\n{frontmatter}---\n\n{content}\n", encoding="utf-8")
    return path


def _sse_format(event_dict: dict) -> str:
    return f"data: {json.dumps(event_dict, ensure_ascii=False)}\n\n"


async def _stream_auto_research(req: AutoResearchStartRequest) -> AsyncIterator[str]:
    topic = req.topic
    slug = req.topic_slug or _slugify(topic)
    max_steps = min(req.max_steps, 4)
    try:
        # Step 1-3 with synthetic streaming chunks
        for step_index in range(1, max_steps):
            title = STEP_TITLES[step_index]
            yield _sse_format(
                {"event": "step_start", "step_index": step_index, "title": title}
            )
            text = _render_step_text(step_index, topic)
            # Chunk in 8-char pieces so the consumer's step_delta path is exercised
            for i in range(0, len(text), 8):
                yield _sse_format(
                    {"event": "step_delta", "step_index": step_index, "text": text[i : i + 8]}
                )
            summary = text.strip().split("\n", 1)[0][:80]
            yield _sse_format(
                {"event": "step_done", "step_index": step_index, "summary": summary}
            )

        # Step 4 = write the brief
        step_index = 4
        yield _sse_format(
            {"event": "step_start", "step_index": step_index, "title": STEP_TITLES[step_index]}
        )
        final_markdown = _render_step_text(step_index, topic)
        for i in range(0, len(final_markdown), 12):
            yield _sse_format(
                {"event": "step_delta", "step_index": step_index, "text": final_markdown[i : i + 12]}
            )
        summary = "完成 4 步自动跑批并落盘"
        yield _sse_format(
            {"event": "step_done", "step_index": step_index, "summary": summary}
        )

        brief_path = _write_brief_disk(final_markdown, topic, slug)
        verdict_passed = all(
            (f"## {sec}" in final_markdown or f"# {sec}" in final_markdown)
            for sec in ("研究问题", "边际贡献", "研究边界", "成功标准")
        )
        yield _sse_format(
            {
                "event": "final_brief",
                "markdown": final_markdown,
                "brief_path": str(brief_path),
                "verdict_passed": verdict_passed,
            }
        )
        yield _sse_format({"event": "done"})
    except Exception as exc:  # noqa: BLE001 — endpoint boundary
        yield _sse_format({"event": "error", "message": f"auto-research failed: {exc}"})


@router.post("/api/auto-research/start")
async def post_auto_research_start(req: AutoResearchStartRequest) -> StreamingResponse:
    """SSE endpoint for the auto-research mode. No await_user checkpoint —
    the client auto-advances to the next stage after `done`.
    """
    return StreamingResponse(
        _stream_auto_research(req),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )
