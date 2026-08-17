"""generate_chapter 节点 (T-07 / T-08a).

按 ``state['current_chapter_index']`` + ``state['outline']`` 取章节 type，
加载对应 prompt 模板，用 ``state`` 里的字段渲染占位符，调
``call_llm(system, user)`` 生成章节内容，写回 ``state['body_chapters'][idx]``。

重跑同一章（regenerate）时新版本 prepend 到 ``chapter['versions']`` 前面
（versions[0] 是最新）。``current_chapter_index`` 自增到下一章。

HITL 简化策略 (同 T-04 / T-06): 此节点**不调 interrupt()**。LangGraph 的
interrupt 在单元测试里不好模拟，故采用 state-driven 简化：
- 节点完成后把章节 status 设为 ``"generated"``；
- 后续审批 / 重新生成由 backend ``POST /sessions/{id}/approve-chapter`` 与
  ``POST /sessions/{id}/generate-chapter`` 触发，graph 集成阶段在节点后
  加 ``interrupt()`` 由调用方控制。

``call_llm`` 是模块级函数，测试通过
``monkeypatch.setattr(nodes.generate_chapter, "call_llm", fake)`` 替换。
注意签名是 ``call_llm(system, user)``（两参数），区别于 generate_title /
generate_outline 的单 prompt 参数——章节生成需要 system prompt 与 user
prompt 分离。
"""
from __future__ import annotations

from typing import Any

from engine.bind import bind_chapter_kwargs
from engine.readiness import paper_ready_to_write, resolve_slot
from prompts import get_prompt
from protocols import GenerateChapterOutput
from state import EconPaperState

_NUM_CHAPTERS = 6


def invoke_generate_llm(config: Any, system: str, user: str) -> str:
    """非 mock 生成通道。与占位字符串分离，测试可断言走了真通道。"""
    from llm.call_llm import call_llm as unified_call

    return unified_call(user, node_type="generate", system=system)


def call_llm(system: str, user: str) -> str:
    """调 LLM 生成章节内容。

    ADR-0008: 走 ``llm.router``。
    - provider == "mock" → 占位（开发 / 测试，现有单测不破）
    - 其他 provider → ``invoke_generate_llm``
    """
    from llm.router import router

    config = router.get_config("generate")
    if config.provider == "mock":
        return "Placeholder chapter content from LLM"
    return invoke_generate_llm(config, system, user)


def _collect_render_kwargs(state: EconPaperState, user_template: str) -> dict[str, Any]:
    """从 state 收集 user_template 里出现的占位符对应的值。

    模板的占位符在 ``USER_TEMPLATE`` 里以 ``{name}`` 形式出现；render 时
    传入多余 kwargs 是安全的（``str.format`` 不报错），但缺失的占位符会抛
    ``KeyError``。这里只挑模板里实际出现的占位符传给 ``render``，缺失的
    降级为空串，保证节点不会因 state 字段不全而崩。
    """
    from string import Formatter

    field_names = {
        fname
        for _, fname, _, _ in Formatter().parse(user_template)
        if fname
    }
    kwargs: dict[str, Any] = {}
    for name in field_names:
        kwargs[name] = state.get(name, "") or ""
    return kwargs


def _inject_revision_context(
    render_state: dict[str, Any], state: EconPaperState, idx: int
) -> None:
    """把本轮弱维 / 修改意见写成字符串，覆盖 state 里的 list。

    ``revision_suggestions`` 在 state 是按章对齐的 list。若让
    ``_collect_render_kwargs`` 自己发现，format 会把整个 list 打进去。
    首轮（没有评审）两个字段空串，prompt 不出现 ``None``。
    """
    suggestions = state.get("revision_suggestions") or []
    rubrics = state.get("review_rubrics") or []

    suggestion = ""
    if isinstance(suggestions, list) and 0 <= idx < len(suggestions):
        raw = suggestions[idx]
        suggestion = raw if isinstance(raw, str) else ""
    render_state["revision_suggestions"] = suggestion

    rubric: dict[str, Any] = {}
    if (
        isinstance(rubrics, list)
        and 0 <= idx < len(rubrics)
        and isinstance(rubrics[idx], dict)
    ):
        rubric = rubrics[idx]
    render_state["low_dims"] = ",".join(
        str(key)
        for key, value in rubric.items()
        if isinstance(value, (int, float)) and value < 0.5
    )


def generate_chapter(state: EconPaperState) -> GenerateChapterOutput:
    """生成章节内容并写回 ``body_chapters[idx]``。

    1. 从 ``outline[current_chapter_index]`` 取章节 type / title 等。
    2. ``get_prompt(chapter_type)`` 加载模板；未知 type 抛 ``ValueError``。
    3. ``call_llm(system, user)`` 生成内容。
    4. 新版本 prepend 到 ``versions``（versions[0] 是最新）。
    5. 写到 ``body_chapters[idx]``（列表不存在或不足 6 项时 pad 到 6 项）。
    6. 返回 ``current_chapter_index + 1``（推进到下一章）。

    缺 ``current_chapter_index`` 或 ``outline`` 时返回 ``{}``（no-op）。
    未就绪返回 ``write_blocked``，不写 ``body_chapters``。
    """
    idx, chapter_spec = resolve_slot(state)
    if idx < 0 or not chapter_spec:
        return {}

    chapter_spec = dict(chapter_spec)
    chapter_spec["chapter_index"] = idx
    chapter_type = chapter_spec.get("type", "intro")
    ready, blockers = paper_ready_to_write(state, str(chapter_type))
    if not ready:
        return {"write_blocked": True, "write_blockers": blockers}

    # 加载模板（未知 type 在此抛 ValueError）
    prompt_mod = get_prompt(chapter_type)

    # 章节特有字段（如 method）覆盖 state 顶层字段
    render_state = {**state, **chapter_spec}
    _inject_revision_context(render_state, state, idx)
    kwargs = _collect_render_kwargs(render_state, prompt_mod.USER_TEMPLATE)
    bound = bind_chapter_kwargs(state, chapter_spec)
    for key, value in bound.items():
        current = kwargs.get(key, "")
        if key not in kwargs or current in ("", None):
            kwargs[key] = value
    system, user = prompt_mod.render(**kwargs)

    from nodes.review_sources.threat_cards import (
        active_threat_cards,
        format_threat_constraints,
    )

    threat_text = format_threat_constraints(active_threat_cards(state))
    if threat_text:
        user = f"{user}\n\n识别威胁约束（必须在正文处理）：\n{threat_text}"

    prose = call_llm(system, user)
    if str(chapter_type) == "intro":
        from prompts.intro import strip_contribution

        prose = strip_contribution(prose)
    est = state.get("estimate") or {}
    if (
        str(chapter_type) == "results"
        and isinstance(est, dict)
        and est.get("status") == "ok"
    ):
        table = (state.get("results") or "").strip()
        content = prose + "\n\n" + table if table else prose
    else:
        content = prose

    body_chapters: list = list(state.get("body_chapters", []) or [])
    while len(body_chapters) < _NUM_CHAPTERS:
        body_chapters.append({})

    # regenerate：已有章节的 versions 保留，新版本 prepend。
    # versions[0] 已含当时拼上的主表；rollback 不要再拼一次。
    existing = body_chapters[idx] if isinstance(body_chapters[idx], dict) else {}
    existing_versions = list(existing.get("versions", []) or [])
    versions = [content] + existing_versions

    new_chapter = {
        **chapter_spec,
        "content": content,
        "status": "generated",
        "versions": versions,
        "chapter_index": idx,
    }
    body_chapters[idx] = new_chapter

    return {
        "body_chapters": body_chapters,
        "current_chapter_index": idx + 1,
    }
