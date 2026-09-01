"""Methods (方法) chapter prompt template (T-07).

association：写相关 / 条件关联。
只有 causal_with_caveat 且方法是 did/iv/rd/scm 才写识别假设。
"""
from __future__ import annotations

from .revision import REVISION_BLOCK, fill_revision

_CAUSAL_METHODS = {"did", "iv", "rd", "rdd", "scm"}

# 默认（association）：模块级 SYSTEM_PROMPT 不含「解决内生性」。
SYSTEM_PROMPT = (
    "你是一位经济学论文写作助手，现在为用户撰写论文的【方法】章节。"
    "方法章节必须让读者明白本文如何用数据描述研究问题中的条件关联。"
    "核心是相关 / 条件关联，不是把回归系数读成处理效应。"
    "当方法为 OLS 或主张类型为 association 时，禁止因果表述。"
    "必须包含以下三个部分，按顺序展开：\n"
    "1. 模型设定：说明本文用相关回归（如 OLS）描述条件关联，"
    "并写清系数应如何阅读。\n"
    "2. 计量模型：给出主回归方程（用 LaTeX 行内公式 ` $...$ ` 标注），"
    "解释每个变量与系数的含义，下标 i / t 的含义，误差项结构。\n"
    "3. 解释边界：说明本文报告的是相关或条件关联，"
    "不要把估计读成识别成立的处理效应。\n\n"
    "写作风格：中文学术写作；公式用 LaTeX；二级标题用 `## `；"
    "段落之间用空行分隔；不要写一级标题。"
)

USER_TEMPLATE = (
    "请为以下经济学论文撰写【方法】章节，约 800-1200 字。\n\n"
    "计量方法：{method}\n\n"
    "研究问题：{research_question}\n\n"
    "主张模式：association\n\n"
    "{method_execution_notice}\n\n"
    "已绑定估计事实：\n{estimate_facts}\n\n"
    "要求：按【模型设定 → 计量模型 → 解释边界】三段式展开，"
    "主回归方程必须使用上面的真实公式并用 LaTeX 行内公式标注；"
    "控制变量、估计器、N 和协方差/标准误设定按绑定事实原样说明；"
    "未提供的设定必须写未提供，不得自行补写 HC1 或聚类标准误；"
    "禁止因果表述；把系数解释为相关或条件关联，不要写成处理效应。"
    + REVISION_BLOCK
)

CAUSAL_SYSTEM_PROMPT = (
    "你是一位经济学论文写作助手，现在为用户撰写论文的【方法】章节。"
    "方法章节必须让读者明白本文如何用数据回答研究问题，核心是识别策略。"
    "识别策略只表示所依赖的假设，不自动意味假设已满足或内生性已解决。"
    "必须包含以下三个部分，按顺序展开：\n"
    "1. 识别策略：开篇用一两段话交代本文的识别策略（OLS / IV / DID / RDD / "
    "PSM / FE 等），并说明该策略在哪些未验证假设下才可用于处理内生性或选择性偏误。\n"
    "2. 计量模型：给出主回归方程（用 LaTeX 行内公式 ` $...$ ` 标注），"
    "解释每个变量与系数的经济学含义，下标 i / t 的含义，误差项结构。\n"
    "3. 假设条件：列出识别策略成立的关键假设（外生性、平行趋势、SUTVA 等），"
    "并严格区分理论上需要的假设与 state 中已验证的事实。"
    "只有 state 明确提供相应识别或稳健性证据且状态已通过时，"
    "才可说明已检验或已满足；证据缺失、未运行、degraded 或 failed 时，"
    "必须写“未验证/不能据此判断”，禁止用推测或填补性叙述补齐检验结果。\n\n"
    "写作风格：中文学术写作；公式用 LaTeX；二级标题用 `## `；"
    "段落之间用空行分隔；不要写一级标题。"
)

CAUSAL_USER_TEMPLATE = (
    "请为以下经济学论文撰写【方法】章节，约 800-1200 字。\n\n"
    "计量方法：{method}\n\n"
    "研究问题：{research_question}\n\n"
    "主张模式：causal_with_caveat\n\n"
    "{method_execution_notice}\n\n"
    "已绑定估计事实：\n{estimate_facts}\n\n"
    "识别证据状态：{identification_status}\n\n"
    "识别验真报告：{identification_report}\n\n"
    "稳健性状态：{robustness_status}\n\n"
    "要求：按【识别策略 → 计量模型 → 假设条件】三段式展开，"
    "主回归方程必须使用上面的真实公式并用 LaTeX 行内公式标注；"
    "控制变量、估计器、N 和协方差/标准误设定按绑定事实原样说明；"
    "未提供的设定必须写未提供，不得自行补写 HC1 或聚类标准误；"
    "可列出该方法所依赖的识别假设，但必须与是否已验证分开；"
    "只能根据上面的识别验真报告与稳健性状态说明检验；"
    "没有对应结果时必须写“未提供/未运行”，不得声称已满足或已检验。"
    + REVISION_BLOCK
)


def _norm_method(method: str) -> str:
    return str(method or "").strip().lower()


def _uses_ident_prompt(claim: str, method: str) -> bool:
    """Only causal_with_caveat + did/iv/rd/scm writes identification assumptions."""
    claim_l = str(claim or "").strip().lower()
    if claim_l != "causal_with_caveat":
        return False
    method_l = _norm_method(method)
    if method_l in _CAUSAL_METHODS:
        return True
    return any(token in method_l for token in _CAUSAL_METHODS)


def render(**kwargs) -> tuple[str, str]:
    """Render system + user prompts with the given kwargs.

    Required kwargs: method, research_question.
    Optional: claim, low_dims, revision_suggestions.
    """
    filled = fill_revision(kwargs)
    filled.setdefault("estimate_facts", "未提供")
    filled.setdefault("method_execution_notice", "执行边界：未提供")
    filled.setdefault("identification_report", "未提供")
    filled.setdefault("identification_status", "未验证/未提供")
    filled.setdefault("robustness_status", "未运行")
    claim = filled.get("claim") or ""
    method = filled.get("method") or ""
    if _uses_ident_prompt(claim, method):
        return CAUSAL_SYSTEM_PROMPT, CAUSAL_USER_TEMPLATE.format(**filled)
    return SYSTEM_PROMPT, USER_TEMPLATE.format(**filled)
