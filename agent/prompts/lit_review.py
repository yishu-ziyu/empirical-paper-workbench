"""Literature review (文献综述) chapter prompt template (T-07).

引导写"文献回顾 + 研究空白 + 本文定位"。

ADR-0009 Stage 3: 在 prompt 中注入 citation_indices，要求 LLM 在叙述中
插入 [1][2] 引用标记，与 generate_references 节点产出的参考文献列表对应。
"""
from __future__ import annotations

from typing import Any, Dict

from prompts.revision import REVISION_BLOCK, fill_revision

SYSTEM_PROMPT = (
    "你是一位经济学论文写作助手，现在为用户撰写论文的【文献综述】章节。"
    "文献综述不是文献罗列，而是有逻辑地组织已有研究，凸显本文的研究空白与定位。"
    "必须包含以下三个部分，按顺序展开：\n"
    "1. 文献回顾：按主题 / 方法 / 结论三条线索之一组织，分 2-3 个子主题。"
    "每个子主题引用 2-4 篇代表性文献，简要说明其方法与核心结论。\n"
    "2. 研究空白：明确指出已有文献未充分回答的问题（数据局限 / 识别不足 / "
    "样本狭窄 / 机制不清等），为本文研究问题做铺垫。\n"
    "3. 本文定位：相对已有文献，本文在数据、方法、识别策略或机制检验上做了"
    "什么新的工作，与最相近的 1-2 篇文献做对比。\n\n"
    "写作风格：中文学术写作；引用用 (Author, Year) 格式；二级标题用 `## `；"
    "段落之间用空行分隔；不要写一级标题。\n\n"
    "引用标记规则（ADR-0009 Stage 3）：\n"
    "- 在叙述中提及某篇文献时，**必须**在作者与年份后附加方括号引用编号，"
    "如 \"Smith (2020) [1] 指出...\"、\"Lee and Chen (2021) [2][3] 发现...\"\n"
    "- 引用编号必须与下方「引用编号表」中的 [N] 一一对应，不得编造编号\n"
    "- 若引用编号表为空（无 citation_indices），则不附加 [N] 标记，"
    "仍使用 (Author, Year) 格式"
)

USER_TEMPLATE = (
    "请为以下经济学论文撰写【文献综述】章节，约 1000-1500 字。\n\n"
    "研究问题：{research_question}\n\n"
    "关键参考文献：\n{key_references}\n\n"
    "引用编号表（[N] 对应参考文献序号）：\n{citation_indices}\n\n"
    "要求：按【文献回顾 → 研究空白 → 本文定位】三段式展开，"
    "至少分 2 个子主题；明确写出研究空白与本文定位；"
    "叙述中提及文献时按引用编号表附加 [N] 标记。"
    + REVISION_BLOCK
)


def _format_citation_indices(citation_indices: Any) -> str:
    """把 citation_indices dict 格式化为 LLM 可读的引用编号表。

    输入：{"10.1/a": 1, "10.1/b": 2, "Some Title": 3}
    输出：
        [1] DOI: 10.1/a
        [2] DOI: 10.1/b
        [3] Title: Some Title

    输入为空 / None / 非 dict 时返回 "（暂无引用编号）"。
    """
    if not citation_indices or not isinstance(citation_indices, dict):
        return "（暂无引用编号）"

    # 按 [N] 升序排列
    sorted_items = sorted(citation_indices.items(), key=lambda kv: kv[1])
    lines = []
    for key, num in sorted_items:
        if key.startswith("10."):  # 启发式判断是 DOI
            lines.append(f"[{num}] DOI: {key}")
        else:
            lines.append(f"[{num}] Title: {key}")
    return "\n".join(lines)


def render(**kwargs: Any) -> tuple[str, str]:
    """Render system + user prompts with the given kwargs.

    Required kwargs: research_question, key_references, citation_indices.

    citation_indices 可以是 dict（state 原始形式）或已格式化的 str。
    dict 会被 _format_citation_indices 转为可读文本。
    """
    # 复制 kwargs 避免修改调用方传入的 dict
    fmt_kwargs: Dict[str, Any] = fill_revision(dict(kwargs))
    ci = fmt_kwargs.get("citation_indices")
    if isinstance(ci, dict):
        fmt_kwargs["citation_indices"] = _format_citation_indices(ci)
    elif ci is None or ci == "":
        fmt_kwargs["citation_indices"] = _format_citation_indices(ci)

    return SYSTEM_PROMPT, USER_TEMPLATE.format(**fmt_kwargs)
