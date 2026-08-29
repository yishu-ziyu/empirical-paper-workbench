"""Pydantic AI 估计 Agent（Phase A：给 LLM 装上"手"）。

与 ``nodes/estimate.py`` 的固定分派（StatsPAI feols/ivreg/rdrobust/...）并行
的一条 "Agent 臂"：LLM 通过工具（read_data_head / read_profiling / run_python）
在沙箱里对清洗后的数据**真实地**跑回归，再映射回与固定分派完全一致的
state 契约（``{"results": 表, "estimate": payload}``）。

启用条件（estimate 节点先看 ``config.ESTIMATE_AGENT_ENABLED``，再看这里）：
- provider 为 OpenAI 兼容通道（minimax / openai）且配了 api_key；
- provider=="mock" 或未配 key 时 ``run_estimate_agent`` 返回 None，
  由节点静默走固定分派（不算 degradation）。

RLM 风格上下文纪律：数据只进沙箱内核，进模型上下文的只有 head/摘要/
回归表这类摘要。``run_python`` 截断输出（前 80 行），大结果落盘为
workdir 文件并把路径返回给模型。沙箱只依赖 ``engine.sandbox.SandboxSession``
接口（dev 主后端 = 持久 IPython 内核，回退 = 一次性 subprocess；生产换 E2B）。
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field
from pydantic_ai import RunContext

from engine.sandbox import SandboxResult, SandboxSession, SubprocessSession, open_session
from llm.router import MINIMAX_BASE_URL, router
from state import EconPaperState

logger = logging.getLogger(__name__)

MAX_REQUESTS = 10              # 迭代预算：模型请求次数封顶（含产出最终结果的请求）
SANDBOX_TIMEOUT_S = 60         # 单次 run_python 沙箱超时（回归比普通脚本慢）
MAX_TOOL_OUTPUT_CHARS = 2000   # RLM/compaction 纪律：进模型上下文的工具输出上限（字符）

# provider 白名单：都是 OpenAI 兼容 Chat Completions，可直连
_OPENAI_COMPAT_PROVIDERS = ("minimax", "minimax_openai", "openai")


class EstimateAgentOutput(BaseModel):
    """Agent 结构化输出（pydantic-ai output_type 校验）。

    ``coefficient/se/pvalue`` 必须来自沙箱真实运行输出；数据或方法不可行时
    ``verdict="fail"`` 且允许留空，**禁止编造数字**。
    """

    method: str = Field(description="实际使用的方法，如 ols / did / iv / rd / scm")
    final_code: str = Field(description="最终跑通并产出系数的那段 Python 代码")
    coefficient: Optional[float] = Field(default=None, description="处理变量系数（真实运行结果）")
    se: Optional[float] = Field(default=None, description="标准误（真实运行结果）")
    pvalue: Optional[float] = Field(default=None, description="p 值（真实运行结果）")
    n_obs: Optional[int] = Field(default=None, description="样本量")
    stars: int = Field(default=0, ge=0, le=3, description="显著性星级 0-3（按 p 值惯例）")
    verdict: Literal["pass", "fail"] = Field(description="pass=成功产出可信主结果；fail=不可行/失败")
    iterations: int = Field(default=1, ge=1, description="沙箱代码迭代次数（含失败尝试）")
    summary: str = Field(default="", description="一两句话说明估计做了什么、结论是否可信")


@dataclass
class EstimateAgentDeps:
    """工具依赖：数据路径、profiling 摘要、沙箱会话（只依赖接口）。"""

    csv_path: str
    workdir: str
    profiling_text: str
    spec: dict
    session: SandboxSession
    sandbox_timeout_s: int = SANDBOX_TIMEOUT_S


# ---------------------------------------------------------------------------
# Agent 工具（带类型标注的普通函数；docstring 即工具说明）
# ---------------------------------------------------------------------------

def read_data_head(ctx: RunContext[EstimateAgentDeps]) -> str:
    """读取数据前 5 行、列类型与形状。数据在当前工作目录。"""
    import pandas as pd  # noqa: PLC0415

    df = pd.read_csv(ctx.deps.csv_path)
    return (
        f"shape: {df.shape[0]} 行 x {df.shape[1]} 列\n\n"
        f"前 5 行:\n{df.head(5).to_string()}\n\n"
        f"列类型:\n{df.dtypes.to_string()}"
    )


def read_profiling(ctx: RunContext[EstimateAgentDeps]) -> str:
    """读取清洗阶段 profiling 摘要（每列缺失率、唯一值数、是否数值型等）。"""
    return ctx.deps.profiling_text or "(无 profiling 摘要：本数据集没有清洗报告)"


def run_python(ctx: RunContext[EstimateAgentDeps], code: str) -> str:
    """在沙箱里执行 Python 代码并返回 stdout/stderr（pandas/statsmodels/statspai 可直接 import）。

    当前目录即数据目录，中间产物写成文件后可跨调用复用。
    输出最多返回前 2000 字符（对齐 Prime Agent compaction 的工具结果序列化上限），
    超长部分落盘并把文件路径返回给你。
    """
    deps: EstimateAgentDeps = ctx.deps
    result = deps.session.run(code, timeout_s=deps.sandbox_timeout_s)
    text = _format_result(result)
    return _truncate_to_file(text, deps.workdir, deps.session.attempts)


def _format_result(result) -> str:
    lines: list[str] = []
    if result.stdout.strip():
        lines.append(result.stdout.rstrip())
    if result.result_repr.strip():
        lines.append(f"[最后表达式] {result.result_repr}")
    if result.stderr.strip():
        lines.append(f"[stderr]\n{result.stderr.rstrip()}")
    if result.error:
        lines.append(f"[error] {result.error}")
    if not lines:
        lines.append("(执行成功，无输出)")
    if not result.ok:
        lines.append("执行失败：请根据上方错误修正代码后重试。")
    return "\n".join(lines)


def _truncate_to_file(text: str, workdir: str, attempts: int) -> str:
    """RLM/compaction 纪律：超 2000 字符的输出不进上下文，落盘成 workdir 文件并回传路径。"""
    if len(text) <= MAX_TOOL_OUTPUT_CHARS:
        return text
    head = text[:MAX_TOOL_OUTPUT_CHARS]
    filename = f"sandbox_output_attempt{attempts}.txt"
    path = os.path.join(workdir, filename)
    try:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        note = (
            f"...[已截断，共 {len(text)} 字符；完整输出写入文件 {filename}，可用 open() 读取]"
        )
    except OSError:
        note = f"...[已截断，共 {len(text)} 字符；落盘失败]"
        logger.warning("沙箱输出落盘失败", exc_info=True)
    return head + "\n" + note


# ---------------------------------------------------------------------------
# 轮次上下文 compaction（移植 Prime Agent compaction.md 的序列化与结构化摘要）
# ---------------------------------------------------------------------------

def _clip(text: str, limit: int = MAX_TOOL_OUTPUT_CHARS) -> str:
    text = str(text)
    if len(text) <= limit:
        return text
    return text[:limit] + f"...[截断，原长 {len(text)} 字符]"


def serialize_conversation(messages: list, max_result_chars: int = MAX_TOOL_OUTPUT_CHARS) -> str:
    """把 pydantic-ai 的 ModelMessage 列表序列化成纯文本（供 compaction/审计）。

    对齐 compaction.md 的 serializeConversation 语义：工具结果截
    ``max_result_chars``（他们用 2000），防止长输出把摘要请求撑爆。
    """
    lines: list[str] = []
    for msg in messages or []:
        role = getattr(msg, "kind", "")
        for part in getattr(msg, "parts", []) or []:
            cls = type(part).__name__
            if cls == "UserPromptPart":
                lines.append(f"[User]: {_clip(part.content, max_result_chars)}")
            elif cls == "SystemPromptPart":
                continue
            elif cls == "ToolReturnPart":
                lines.append(
                    f"[Tool result] {getattr(part, 'tool_name', '')}: "
                    f"{_clip(getattr(part, 'content', ''), max_result_chars)}"
                )
            elif cls == "RetryPromptPart":
                lines.append(f"[Retry]: {_clip(getattr(part, 'content', ''), max_result_chars)}")
            elif cls == "TextPart":
                lines.append(f"[Assistant]: {_clip(part.content, max_result_chars)}")
            elif cls == "ToolCallPart":
                args = getattr(part, "args", None)
                args = getattr(args, "args_json", None) or str(args)
                lines.append(f"[Assistant tool calls]: {getattr(part, 'tool_name', '')}({_clip(args)})")
            elif getattr(part, "content", None):
                lines.append(f"[{cls}]: {_clip(part.content, max_result_chars)}")
        if role and not (getattr(msg, "parts", None) or []):
            lines.append(f"[{role}]")
    return "\n".join(lines)


def compact_history_six_section(
    messages: list, *, method: str = "", treatment: str = ""
) -> str:
    """把本轮 agent 消息压成 Prime Agent compaction 的六段结构化摘要（确定性抽取，不生成）。

    模板：Goal / Constraints & Preferences / Progress(Done·Blocked) / Key Decisions /
    Next Steps / Critical Context。只填可从消息里确定抽出的事实（沙箱执行次数、成功/失败、
    最终代码、最后一次关键输出），抽不出的段落如实写"（无）"——禁止编造。
    """
    serialized = serialize_conversation(messages)
    lines = serialized.splitlines()
    runs = [ln for ln in lines if "[Tool result] run_python" in ln]
    ok_runs = [ln for ln in runs if "[error]" not in ln]
    fail_runs = [ln for ln in runs if ln not in ok_runs]
    code_calls = [
        ln for ln in lines
        if ln.startswith("[Assistant tool calls]: run_python")
    ]
    last_code = ""
    if code_calls:
        last = code_calls[-1]
        last_code = last.split('code=', 1)[1].rstrip(")") if "code=" in last else last
        last_code = _clip(last_code, 600)
    last_output = _clip(runs[-1].split(": ", 1)[1], 600) if runs else "(无)"
    done: list[str] = []
    blocked: list[str] = []
    if ok_runs:
        done.append(f"[x] 沙箱执行 {len(ok_runs)} 次成功（共 {len(runs)} 次）")
    if fail_runs:
        blocked.append(f"[-] {len(fail_runs)} 次执行报错（已按错误修正重试）" if ok_runs
                       else f"[-] 全部 {len(fail_runs)} 次执行报错，未产出可信结果")
    decisions = f"- 最终代码采用：{last_code}" if last_code else "-（无）"
    out = [
        "## Goal",
        f"完成 {method or '主'} 估计"
        + (f"（处理变量：{treatment}）" if treatment else ""),
        "",
        "## Constraints & Preferences",
        "- 数字必须来自沙箱真实输出；不可行时 verdict=fail，禁止编造",
        "",
        "## Progress",
        "### Done",
        *(done or ["-（无）"]),
        "### Blocked",
        *(blocked or ["-（无）"]),
        "",
        "## Key Decisions",
        decisions,
        "",
        "## Next Steps",
        "-（本轮已收敛：结果见 output_type 字段）",
        "",
        "## Critical Context",
        f"- 最后一次执行输出：{last_output}",
    ]
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Agent 构建
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """你是计量经济学估计 Agent，在一个带沙箱的研究环境里完成论文主结果的估计。

可用工具：
- read_data_head：数据前 5 行 + 列类型；
- read_profiling：清洗阶段的逐列 profiling 摘要；
- run_python：在沙箱执行 Python（当前目录就是数据目录，pandas/statsmodels/statspai 可直接 import）。

工作方式：
1. 先 read_data_head / read_profiling 了解数据，再写代码；
2. 用 run_python 真实跑回归并打印系数、标准误、p 值、样本量；
3. 代码报错就修正重试，不要猜输出；
4. 中间产物写当前目录文件即可跨调用复用。

诚实性红线（最重要）：
- 输出的 coefficient/se/pvalue/n_obs 必须逐字来自真实运行输出，禁止编造或四舍五入成"好看"的数；
- 数据缺列、方法不可行、识别失败时 verdict=fail，相关数值留空，并在 summary 说明原因；
- 显著性星级按惯例：p<0.01 → 3，p<0.05 → 2，p<0.1 → 1，否则 0。"""

_USER_PROMPT_TMPL = """请完成本次主估计。

- 方法：{method}
- 公式：{formula}
- 处理变量：{treatment}
- 结局变量：{outcome}
- 控制变量：{controls}
- 聚类列：{cluster}
- 数据文件（相对当前目录）：{csv_name}

沙箱当前目录已就位该数据文件，直接 `pd.read_csv("{csv_name}")` 即可。
跑出主结果后，按 output_type 的字段如实汇报；不可行就 verdict=fail 并说明原因。"""


def build_estimate_agent(model: Optional[Any] = None):
    """构建估计 Agent。``model`` 仅供测试注入（TestModel / FunctionModel），生产走 MiniMax。"""
    from pydantic_ai import Agent  # noqa: PLC0415 — 可选依赖，缺失时由调用方捕获回退

    if model is None:
        model = _model_from_config(router.get_config("estimate"))
    return Agent(
        model,
        output_type=EstimateAgentOutput,
        tools=[read_data_head, read_profiling, run_python],
        instructions=_SYSTEM_PROMPT,
        retries=1,
    )


def _model_from_config(config):
    """router 同源配置 -> OpenAI 兼容 ChatModel（base_url 默认 MINIMAX_BASE_URL）。"""
    from pydantic_ai.models.openai import OpenAIChatModel  # noqa: PLC0415
    from pydantic_ai.providers.openai import OpenAIProvider  # noqa: PLC0415

    provider = OpenAIProvider(
        base_url=config.base_url or MINIMAX_BASE_URL,
        api_key=config.api_key,
    )
    return OpenAIChatModel(config.model, provider=provider)


def provider_ready(config) -> bool:
    """provider 可用判定：OpenAI 兼容白名单 + 有 api_key。mock / 无 key 均不启用。"""
    provider = getattr(config, "provider", None)
    if provider not in _OPENAI_COMPAT_PROVIDERS:
        return False
    return bool(getattr(config, "api_key", None))


# ---------------------------------------------------------------------------
# 入口与输出映射
# ---------------------------------------------------------------------------

def run_estimate_agent(state: EconPaperState) -> Optional[dict]:
    """estimate 节点的 Agent 臂入口。

    开关（ESTIMATE_AGENT_ENABLED）由节点负责；这里只判 provider。
    provider 不可用返回 None（节点静默回退固定分派）；
    其他异常向上抛（节点记 degradation 后回退）。
    """
    config = router.get_config("estimate")  # 不在路由表 → default(generate) 配置，同源
    if not provider_ready(config):
        return None
    agent = build_estimate_agent()
    return run_estimate_via_agent(agent, state)


def run_estimate_via_agent(agent, state: EconPaperState, *, session: Optional[SandboxSession] = None) -> dict:
    """用给定 agent（生产或测试注入）跑一次估计，映射回 state 契约。

    ``session`` 仅供测试注入；生产路径按 dev 主后端（持久内核）优先、
    subprocess 回退自动开一个会话，estimate 结束即关闭（一次估计一次会话）。
    """
    spec = state.get("main_specification") or {}
    if not isinstance(spec, dict):
        spec = {}
    csv_path = str(state.get("csv_path") or "")
    if not csv_path:
        raise ValueError("estimate agent 需要 csv_path")
    method = _method_of(state, spec)

    workdir = os.path.dirname(os.path.abspath(csv_path)) or "."
    owns_session = session is None
    deps = EstimateAgentDeps(
        csv_path=csv_path,
        workdir=workdir,
        profiling_text=profiling_text_from_state(state),
        spec=spec,
        session=session or open_session(workdir),
    )
    # checkpoint↔内核对齐：workdir 里有上次的内核快照就恢复（断点续跑拿回变量）；
    # 跑通后回写快照（KernelSession 支持，SubprocessSession no-op）。
    snapshot_path = os.path.join(workdir, "kernel_state.dill") if owns_session else ""
    if owns_session and snapshot_path and os.path.exists(snapshot_path):
        deps.session.restore(snapshot_path)
    try:
        result = agent.run_sync(
            _user_prompt(method, spec, os.path.basename(csv_path)),
            deps=deps,
            usage_limits=_usage_limits(),
        )
        out: EstimateAgentOutput = result.output
        if owns_session and snapshot_path and out.verdict == "pass":
            deps.session.snapshot(snapshot_path)
    finally:
        if owns_session:
            deps.session.close()
    history_compact = compact_history_six_section(
        result.all_messages(),
        method=method,
        treatment=str(spec.get("treatment") or spec.get("endogenous") or ""),
    )
    logger.info(
        "estimate agent 完成：verdict=%s coef=%s iterations=%s",
        out.verdict, out.coefficient, out.iterations,
    )
    return estimate_output_from_agent(out, method=method, spec=spec, history_compact=history_compact)


def _usage_limits():
    """迭代预算：模型请求封顶 MAX_REQUESTS（UsageLimits 字段名随版本变化，做兼容）。"""
    from pydantic_ai.usage import UsageLimits  # noqa: PLC0415

    fields = getattr(UsageLimits, "__dataclass_fields__", {})
    if "request_limit" in fields:       # pydantic-ai >= 2.x
        return UsageLimits(request_limit=MAX_REQUESTS)
    if "requests_limit" in fields:      # pydantic-ai 0.x/1.x 旧字段名
        return UsageLimits(requests_limit=MAX_REQUESTS)
    return UsageLimits()


def _method_of(state: EconPaperState, spec: dict) -> str:
    """与 nodes.estimate._method_of 同语义（engine 层不反向依赖 nodes）。"""
    from design.spec import norm_method  # noqa: PLC0415

    raw = spec.get("method")
    if not raw:
        rd = state.get("research_direction")
        if isinstance(rd, dict):
            raw = rd.get("method")
    return norm_method(raw)


def _user_prompt(method: str, spec: dict, csv_name: str) -> str:
    controls = spec.get("controls") or []
    return _USER_PROMPT_TMPL.format(
        method=method or "(未指定，请依据 profiling 判断最合适的主流方法)",
        formula=spec.get("feols_formula") or spec.get("formula") or "(未给出，由你根据方法构造)",
        treatment=spec.get("endogenous") or spec.get("treatment") or spec.get("treatment_col") or "(未指定)",
        outcome=spec.get("outcome") or "(未指定)",
        controls=", ".join(str(c) for c in controls) or "(无)",
        cluster=spec.get("cluster") or spec.get("cluster_col") or "(无)",
        csv_name=csv_name,
    )


def profiling_text_from_state(state: EconPaperState) -> str:
    """把 cleaning_report 里 ProfilingStep 的产出压成文本摘要（不进全量数据）。"""
    lines: list[str] = []
    data_summary = state.get("data_summary")
    if isinstance(data_summary, str) and data_summary.strip():
        lines.append(f"data_summary: {data_summary.strip()}")
    report = state.get("cleaning_report")
    steps = report.get("steps") if isinstance(report, dict) else None
    for step in steps or []:
        if not isinstance(step, dict) or step.get("name") != "profiling":
            continue
        step_report = step.get("report") or {}
        profiles = step_report.get("profiles") or []
        for prof in profiles:
            if not isinstance(prof, dict):
                continue
            lines.append(
                f"profile: rows={prof.get('n_rows')}, cols={prof.get('n_cols')}, "
                f"dataset_type={prof.get('dataset_type', 'generic')}"
            )
            variables = prof.get("variables") or {}
            for col, meta in list(variables.items()):
                if not isinstance(meta, dict):
                    continue
                lines.append(
                    f"  - {col}: dtype={meta.get('dtype')}, "
                    f"missing_rate={meta.get('missing_rate')}, "
                    f"n_unique={meta.get('n_unique')}, numeric={meta.get('is_numeric')}"
                )
    return "\n".join(lines)


def _fmt(x: Optional[float]) -> str:
    return "—" if x is None else f"{x:.4f}"


def estimate_output_from_agent(
    out: EstimateAgentOutput, *, method: str, spec: dict, history_compact: str = ""
) -> dict:
    """EstimateAgentOutput -> estimate 节点的 state 契约。

    pass 分支镜像固定分派 ok payload 的键；fail 分支镜像 error payload：
    treatment_row 留空、不写 coef/se/p —— 与"不编造假系数"红线一致。
    ``history_compact`` 为纯增量溯源键（六段结构化轮次摘要，供步骤卡展示）。
    """
    estimator = "estimate_agent"
    method_label = method or str(spec.get("method") or "ols")
    if out.verdict == "pass":
        treatment = str(
            spec.get("endogenous")
            or spec.get("treatment")
            or spec.get("treatment_col")
            or "treat"
        )
        treatment_row = (
            f"| {treatment} | {_fmt(out.coefficient)} | {_fmt(out.se)} | {_fmt(out.pvalue)} |"
        )
        formula = str(spec.get("feols_formula") or spec.get("formula") or "")
        n = None if out.n_obs is None else int(out.n_obs)
        payload: dict = {
            "status": "ok",
            "produced_by": "estimate",
            "estimator": estimator,
            "method": method_label,
            "formula": formula,
            "treatment": treatment,
            "treatment_row": treatment_row,
            "coef": out.coefficient,
            "se": out.se,
            "p": out.pvalue,
            "stars": out.stars,
            "iterations": out.iterations,
            "final_code": out.final_code,
            "summary": out.summary,
        }
        if history_compact:
            payload["history_compact"] = history_compact
        if n is not None:
            payload["n"] = n
        cluster = spec.get("cluster") or spec.get("cluster_col") or None
        if cluster:
            payload["cluster"] = str(cluster)
        lines = ["# 主结果", "", f"估计器：`{estimator}`"]
        if formula:
            lines.append(f"公式：`{formula}`")
        if n is not None:
            lines.append(f"N = {n}")
        lines.extend(
            [
                "",
                "| 变量 | 系数 | SE | p |",
                "|------|------|----|---|",
                treatment_row,
            ]
        )
        return {"results": "\n".join(lines), "estimate": payload}

    return {
        "results": f"# 主结果\n\n主估计未跑：{out.summary or 'estimate agent verdict=fail'}",
        "estimate": {
            "status": "error",
            "produced_by": "estimate",
            "estimator": estimator,
            "method": method_label,
            "treatment_row": "",
            "error": out.summary or "estimate agent verdict=fail",
            "iterations": out.iterations,
            "final_code": out.final_code,
            **(
                {"formula": str(formula)}
                if (formula := spec.get("feols_formula") or spec.get("formula"))
                else {}
            ),
        },
    }


__all__ = [
    "EstimateAgentOutput",
    "EstimateAgentDeps",
    "build_estimate_agent",
    "provider_ready",
    "run_estimate_agent",
    "run_estimate_via_agent",
    "estimate_output_from_agent",
    "profiling_text_from_state",
    "serialize_conversation",
    "compact_history_six_section",
    "MAX_REQUESTS",
    "MAX_TOOL_OUTPUT_CHARS",
]
