"""Results (结果) chapter prompt template (T-07).

主表已在文末。SYSTEM 只解读，禁止再画表，禁止「见表 2」。
"""
from __future__ import annotations

from .revision import REVISION_BLOCK, fill_revision

SYSTEM_PROMPT = (
    "你是一位经济学论文写作助手，现在为用户撰写论文的【结果】章节。"
    "主表已在文末。只解读文末主表与用户提供的数字，禁止再画表，"
    "禁止用「见表 2」另造基准表。"
    "任何具体数字只能来自用户提示中的回归结果、已绑定估计事实、稳健性表或异质性证据；"
    "禁止写入未绑定数字。当方法为 OLS 或主张类型为 association 时，禁止因果表述。"
    "必须包含以下三个部分，按顺序展开：\n"
    "1. 基准回归：报告主回归结果，给出系数符号、显著性、经济学含义。"
    "直接解读文末主表，不要另画一张基准回归表。\n"
    "2. 稳健性：只解读已绑定的稳健性结果。状态为未运行、降级或证据不足时，"
    "必须如实说明，不得宣称稳健。\n"
    "3. 异质性：只有用户提示中存在异质性结果时才能讨论。没有结果时写“未运行/未提供”，"
    "不得生成地区、行业、性别或其他分组差异与数字。\n\n"
    "写作风格：中文学术写作；不要写「见表 2」；"
    "二级标题用 `## `；段落之间用空行分隔；不要写一级标题。"
)

USER_TEMPLATE = (
    "请为以下经济学论文撰写【结果】章节，约 1000-1500 字。\n\n"
    "回归结果（StatsPAI 输出，主表将附在文末，此处仅供解读）：\n{results}\n\n"
    "稳健性表：\n{robustness_table}\n\n"
    "稳健性状态：{robustness_status}\n\n"
    "异质性证据：{heterogeneity_evidence}\n\n"
    "已绑定估计事实：\n{estimate_facts}\n\n"
    "计量方法：{method}\n\n"
    "要求：按【基准回归 → 稳健性 → 异质性】三段式展开，"
    "基准回归部分必须解读上面的回归结果与系数；"
    "只解读，禁止再画表，禁止写「见表 2」另造基准表；"
    "稳健性状态是未运行、降级或证据不足时，不得宣称稳健；"
    "异质性证据是未运行/未提供时，不得生成地区、行业、性别差异或数字。"
    "任何具体数字必须能在上述绑定输入中逐字找到；禁止未绑定数字；"
    "主张类型为 association 或计量方法为 OLS 时，禁止因果表述。"
    "\n\nClaim Ledger（写作边界，禁止改写）："
    "\n允许主张：{claim_supported_wording}"
    "\n有条件主张：{claim_conditionally_supported_wording}"
    "\n禁止主张（写入则不得标 grounded）：{claim_unsupported_wording}"
    "\n支撑规格数字：{claim_run_facts}"
    + REVISION_BLOCK
)


def render(**kwargs) -> tuple[str, str]:
    """Render system + user prompts with the given kwargs.

    Required kwargs: results, method.
    Optional: robustness_table, low_dims, revision_suggestions.
    """
    filled = fill_revision(kwargs)
    filled.setdefault("robustness_table", "")
    filled.setdefault("robustness_status", "未运行")
    filled.setdefault("heterogeneity_evidence", "未运行/未提供")
    filled.setdefault("estimate_facts", "未提供")
    filled.setdefault("claim_supported_wording", "未提供")
    filled.setdefault("claim_conditionally_supported_wording", "未提供")
    filled.setdefault("claim_unsupported_wording", "未提供")
    filled.setdefault("claim_run_facts", "未提供")
    return SYSTEM_PROMPT, USER_TEMPLATE.format(**filled)
