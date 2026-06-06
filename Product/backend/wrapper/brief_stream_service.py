"""MiniMax-M3 通过 chat_completion_stream 走流式, 4 步思考 + await_user checkpoint.

Source restored 2026-06-05 from __pycache__/brief_stream_service.cpython-314.pyc
(dis/marshal 反编译 → 字节码逻辑 → 重新按公开契约还原).

Public event / request models live here because Product/types/research.py
does not yet define BriefEvent / BriefResumeRequest (deferred to a follow-up
hygiene task; route module re-exports them).
"""
from __future__ import annotations

import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterator, Literal, Optional

import yaml
from pydantic import BaseModel, Field

from Product.backend.llm_client import chat_completion_stream

# ── Public event / request models (re-exported from Product.api.brief_stream) ─

BriefEventType = Literal[
    "step_start",
    "step_delta",
    "step_done",
    "await_user",
    "heartbeat",
    "final_brief",
    "done",
    "error",
]


class BriefEvent(BaseModel):
    """SSE event for brief stream. Mirrors the union type in
    docs/superpowers/specs/2026-06-04-brief-step-cards-design.md §1.
    """

    event: BriefEventType
    step_index: Optional[int] = None
    title: Optional[str] = None
    text: Optional[str] = None
    summary: Optional[str] = None
    markdown: Optional[str] = None
    brief_path: Optional[str] = None
    verdict_passed: Optional[bool] = None
    message: Optional[str] = None
    critique: Optional[list[str]] = None  # step 3 only: LLM 自我疑虑 (≤3 短句)


class BriefResumeRequest(BaseModel):
    """Resume from await_user checkpoint."""

    topic: str
    topic_slug: Optional[str] = None
    action: Literal["continue", "modify", "reselect"] = "continue"
    prior_steps: dict[str, str] = Field(default_factory=dict)
    user_input: Optional[str] = None


# ── Constants ────────────────────────────────────────────────────────────────

_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-M2.7")
_PROVIDER_ID = "minimax"
_STEP_MARKER_RE = re.compile(r"### STEP_(\d+)_DONE ###")
# Critique 段 header (中英文, 启发式, 不命中 → [])
_CRITIQUE_HEADER_RE = re.compile(
    r"(?im)^#{1,3}\s*(?:自(?:我)?(?:评|审视|评估|批评)|我(?:最)?不放心(?:的\s*\d+\s*点)?|最不放心(?:的\s*\d+\s*点)?|我不确定(?:的点?|的)?|不确定(?:性|的点?)?|Self[- ]?Critique(?:s|ism)?|Limitations?|Caveats?|Risks?)\s*$"
)
_SECTION_END_RE = re.compile(r"(?m)^#{1,3}\s+")
_BULLET_RE = re.compile(r"^\s*(?:[-*]|\d+\.)\s+")
_CONCERN_HINTS = (
    "不放心",
    "不确定",
    "可能",
    "是否",
    "需要",
    "风险",
    "偏误",
    "遗漏",
    "限制",
    "缺",
    "口径",
    "测量",
    "识别",
    "因果",
    "样本",
    "变量",
    "数据",
)
STEP_TITLES = (
    None,  # index 0 占位, step 1-4 直接用索引
    "分析研究问题",
    "映射文献缺口",
    "拟定贡献点",
    "写出研究简报",
)
HEARTBEAT_INTERVAL_SEC = 15.0
PROMPT_V4_LOADER: Optional[Callable[[], str]] = None  # lazy


# ── Prompt loading (lazy to avoid circular import) ───────────────────────────


def _get_prompt_v4() -> str:
    """Lazy import to avoid circular dependency."""
    global PROMPT_V4_LOADER
    if PROMPT_V4_LOADER is None:
        from Program.prompts.brief.v4 import load_prompt_v4

        PROMPT_V4_LOADER = load_prompt_v4
    return PROMPT_V4_LOADER()


# ── Helpers ──────────────────────────────────────────────────────────────────


def _first_sentence(text: str, max_len: int = 80) -> str:
    """提取第一句作为 summary. 中文按 '。' 切."""
    if not text:
        return ""
    for sep in ("。", ". ", "！", "?"):
        idx = text.find(sep)
        if idx >= 0:
            return text[: idx + len(sep)].strip()
    return text[:max_len].strip()


def _extract_critique(text: str, max_items: int = 3) -> list[str]:
    """启发式: 从 LLM 文本抓 self-critique 段, 返 ≤ N 短句. 无 → []."""
    if not text:
        return []
    m = _CRITIQUE_HEADER_RE.search(text)
    if not m:
        return []
    nxt = _SECTION_END_RE.search(text, m.end())
    section = text[m.end() : nxt.start() if nxt else len(text)].strip()
    if not section:
        return []
    items: list[str] = [
        re.sub(r"\s+", " ", _BULLET_RE.sub("", l).strip())[:160]
        for l in section.splitlines() if l.strip()
    ]
    if not items:  # 没 bullet → 按中英句号切
        for sent in re.split(r"(?<=[。!?;；\n])\s*", section):
            s = re.sub(r"\s+", " ", sent.strip().lstrip("-*·• ").strip())[:160]
            if len(s) > 4:
                items.append(s)
            if len(items) >= max_items:
                break
    concerns = [it for it in items if any(hint in it for hint in _CONCERN_HINTS)]
    if concerns:
        items = concerns
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        if it in seen:
            continue
        seen.add(it)
        out.append(it)
        if len(out) >= max_items:
            break
    return out


def _slugify(topic: str) -> str:
    ascii_part = re.sub(r"[^a-zA-Z0-9]+", "-", topic).strip("-").lower()[:50]
    return ascii_part or "untitled"


def _write_brief_disk(content: str, topic: str, topic_slug: str, tasks_root: Path) -> Path:
    """落盘 Tasks/{slug}/brief.md, 带 YAML frontmatter."""
    topic_dir = tasks_root / topic_slug
    topic_dir.mkdir(parents=True, exist_ok=True)
    path = topic_dir / "brief.md"
    frontmatter = yaml.safe_dump(
        {
            "topic": topic,
            "topic_slug": topic_slug,
            "generated_by": "brief-llm-sse",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": _MODEL,
            "prompt_version": "v4",
            "upstream": False,
            "downstream_consumers": ["literature.md", "variables.yaml"],
        },
        allow_unicode=True,
        sort_keys=False,
    )
    path.write_text(f"---\n{frontmatter}---\n\n{content}\n", encoding="utf-8")
    return path


def _heartbeat_check(last_heartbeat: list[float]) -> Optional[BriefEvent]:
    """Returns a heartbeat event if 15s have passed; else None. Uses list for closure mutation."""
    now = time.monotonic()
    if now - last_heartbeat[0] >= HEARTBEAT_INTERVAL_SEC:
        last_heartbeat[0] = now
        return BriefEvent(event="heartbeat")
    return None


# ── Public API ───────────────────────────────────────────────────────────────


def run_brief_stream(topic: str) -> Iterator[BriefEvent]:
    """Generate events for steps 1-3, then await_user.

    Yields step_start → step_delta* → step_done in order, holding at
    step 3 with await_user. Resumption is handled by resume_brief_stream.
    """
    prompt = _get_prompt_v4().replace("{topic}", topic)
    messages = [{"role": "user", "content": prompt}]
    last_heartbeat = [time.monotonic()]

    for step_index in (1, 2, 3):
        yield BriefEvent(
            event="step_start",
            step_index=step_index,
            title=STEP_TITLES[step_index],
        )
        live_text = ""
        stream_ended_normally = False
        for chunk in chat_completion_stream(
            messages=messages,
            provider_id=_PROVIDER_ID,
            model=_MODEL,
        ):
            hb = _heartbeat_check(last_heartbeat)
            if hb:
                yield hb
            yield BriefEvent(event="step_delta", step_index=step_index, text=chunk)
            live_text += chunk
            m = _STEP_MARKER_RE.search(live_text)
            if m and int(m.group(1)) == step_index:
                messages.append({"role": "assistant", "content": live_text})
                stream_ended_normally = True
                break
        if not stream_ended_normally and live_text:
            # stream ended without marker; still append for context
            messages.append({"role": "assistant", "content": live_text})
        yield BriefEvent(
            event="step_done",
            step_index=step_index,
            summary=_first_sentence(live_text),
            critique=_extract_critique(live_text) if step_index == 3 else None,
        )

    yield BriefEvent(event="await_user", step_index=3)


def resume_brief_stream(
    topic: str,
    action: str,
    prior_steps: dict,
    user_input: Optional[str] = None,
    tasks_root: Optional[Path] = None,
) -> Iterator[BriefEvent]:
    """Resume from await_user checkpoint.

    action="continue": use prior steps as context, generate step 4 → final_brief
    action="modify":   rebuild step 3 prompt with user_input constraint, then step 4
    action="reselect": restart from step 1 (delegate to run_brief_stream)
    """
    if action == "reselect":
        yield from run_brief_stream(topic)
        return

    base_prompt = _get_prompt_v4()
    messages = [{"role": "user", "content": base_prompt.replace("{topic}", topic)}]

    if action == "modify":
        modify_constraint = (
            f"用户的额外约束: {user_input or ''}\n请用这个约束重做步骤 3。\n### STEP_3_DONE ###\n"
        )
        for s in (1, 2):
            text = prior_steps.get(str(s), "")
            if text:
                messages.append({"role": "assistant", "content": text})
        messages.append({"role": "user", "content": modify_constraint})
    elif action == "continue":
        for s in (1, 2, 3):
            text = prior_steps.get(str(s), "")
            if text:
                messages.append({"role": "assistant", "content": text})

    last_heartbeat = [time.monotonic()]

    if action == "modify":
        # Redo step 3
        yield BriefEvent(
            event="step_start",
            step_index=3,
            title=STEP_TITLES[3],
        )
        live_text = ""
        stream_ended_normally = False
        for chunk in chat_completion_stream(
            messages=messages,
            provider_id=_PROVIDER_ID,
            model=_MODEL,
        ):
            hb = _heartbeat_check(last_heartbeat)
            if hb:
                yield hb
            yield BriefEvent(event="step_delta", step_index=3, text=chunk)
            live_text += chunk
            m = _STEP_MARKER_RE.search(live_text)
            if m and int(m.group(1)) == 3:
                messages.append({"role": "assistant", "content": live_text})
                stream_ended_normally = True
                break
        if not stream_ended_normally and live_text:
            messages.append({"role": "assistant", "content": live_text})
        yield BriefEvent(
            event="step_done",
            step_index=3,
            summary=_first_sentence(live_text),
            critique=_extract_critique(live_text),
        )

    # Step 4
    yield BriefEvent(event="step_start", step_index=4, title=STEP_TITLES[4])
    live_text = ""
    for chunk in chat_completion_stream(
        messages=messages,
        provider_id=_PROVIDER_ID,
        model=_MODEL,
    ):
        hb = _heartbeat_check(last_heartbeat)
        if hb:
            yield hb
        yield BriefEvent(event="step_delta", step_index=4, text=chunk)
        live_text += chunk
        if "### STEP_4_DONE ###" in live_text:
            break

    final_markdown = re.sub(r"### STEP_4_DONE ###", "", live_text).strip()
    yield BriefEvent(
        event="step_done",
        step_index=4,
        summary=_first_sentence(final_markdown),
    )

    # Verdict: 4 sections present
    verdict_passed = all(
        (f"## {sec}" in final_markdown or f"# {sec}" in final_markdown)
        for sec in ("研究问题", "边际贡献", "研究边界", "成功标准")
    )

    brief_path: Optional[str] = None
    if tasks_root is not None:
        slug = _slugify(topic)
        path = _write_brief_disk(final_markdown, topic, slug, tasks_root)
        brief_path = str(path)

    yield BriefEvent(
        event="final_brief",
        markdown=final_markdown,
        brief_path=brief_path,
        verdict_passed=verdict_passed,
    )
    yield BriefEvent(event="done")
