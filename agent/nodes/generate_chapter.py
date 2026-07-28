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

from prompts import get_prompt
from protocols import GenerateChapterOutput
from state import EconPaperState

_NUM_CHAPTERS = 6


def call_llm(system: str, user: str) -> str:
    """调 LLM 生成章节内容。

    生产环境接 langchain-anthropic（system + user 双消息）；开发阶段返回
    占位。测试通过 ``monkeypatch.setattr(nodes.generate_chapter, "call_llm",
    fake)`` 替换为 fake，故必须是模块级函数。
    """
    return "Placeholder chapter content from LLM"


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


def generate_chapter(state: EconPaperState) -> GenerateChapterOutput:
    """生成章节内容并写回 ``body_chapters[idx]``。

    1. 从 ``outline[current_chapter_index]`` 取章节 type / title 等。
    2. ``get_prompt(chapter_type)`` 加载模板；未知 type 抛 ``ValueError``。
    3. ``call_llm(system, user)`` 生成内容。
    4. 新版本 prepend 到 ``versions``（versions[0] 是最新）。
    5. 写到 ``body_chapters[idx]``（列表不存在或不足 6 项时 pad 到 6 项）。
    6. 返回 ``current_chapter_index + 1``（推进到下一章）。

    缺 ``current_chapter_index`` 或 ``outline`` 时返回 ``{}``（no-op）。
    """
    idx = state.get("current_chapter_index")
    outline = state.get("outline")
    if idx is None or not outline:
        return {}

    if idx >= len(outline):
        # 所有章节已生成，无操作
        return {}

    chapter_spec: dict = dict(outline[idx])
    chapter_spec["chapter_index"] = idx
    chapter_type = chapter_spec.get("type", "intro")

    # 加载模板（未知 type 在此抛 ValueError）
    prompt_mod = get_prompt(chapter_type)

    # 章节特有字段（如 method）覆盖 state 顶层字段
    render_state = {**state, **chapter_spec}
    kwargs = _collect_render_kwargs(render_state, prompt_mod.USER_TEMPLATE)
    system, user = prompt_mod.render(**kwargs)

    content = call_llm(system, user)

    body_chapters: list = list(state.get("body_chapters", []) or [])
    while len(body_chapters) < _NUM_CHAPTERS:
        body_chapters.append({})

    # regenerate：已有章节的 versions 保留，新版本 prepend
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
