"""L3-variables: 数据变量 (Variables) wrapper service。

端到端流程：
1. load_schema — 读取数据集 schema（已知数据集返回固定 stub）
2. build_mapping — LLM 解析 schema + brief → list[Variable]
3. write_variables — 落盘 Tasks/{topic}/variables.yaml 含 provenance
4. verify_variables — verdict gate: 变量数 >= min_count 且每条 role ∈ 5 枚举
5. run_variables — 端到端入口（API 层调用）

约定：
- LLM 调用走 `Product.backend.llm_client.chat_completion`（真实 MiniMax-M3）
- test 时用 `unittest.mock.patch("Product.backend.wrapper.variables_service.chat_completion", ...)`
- 产物路径: Tasks/{topic_slug}/variables.yaml
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

import yaml

from Product.backend.llm_client import chat_completion
from Product.types.research import (
    Variable,
    VariablesRequest,
    VariablesResponse,
)


# ── 已知数据集的 stub schema（用于离线/无 schema.yaml 场景） ────────────────

# 5 个 role 枚举：与 Product.types.research.Variable.role 对齐
_VALID_ROLES = {"X", "Y", "control", "mediator", "moderator"}

# 已知数据集的 stub 列名（按工业机器人/就业/工资研究最常见变量排序）
_DATASET_STUBS: dict[str, list[dict[str, str]]] = {
    "CFPS": [
        {"name": "pid", "type": "int", "desc": "个体 id"},
        {"name": "urban", "type": "int", "desc": "城乡虚拟变量"},
        {"name": "ln_wage", "type": "float", "desc": "对数小时工资"},
        {"name": "manu_dummy", "type": "int", "desc": "是否制造业"},
        {"name": "ISEI_score", "type": "int", "desc": "国际职业地位评分"},
        {"name": "part_time", "type": "int", "desc": "是否兼职"},
        {"name": "female", "type": "int", "desc": "性别虚拟变量"},
        {"name": "age", "type": "int", "desc": "年龄"},
        {"name": "edu_last", "type": "int", "desc": "受教育年限"},
        {"name": "year", "type": "int", "desc": "调查年份"},
        {"name": "year_robot", "type": "int", "desc": "IFR 行业机器人年份"},
        {"name": "robot_density", "type": "float", "desc": "Bartik 工业机器人渗透率"},
        {"name": "ln_robot", "type": "float", "desc": "对数机器人装机量"},
        {"name": "bartik_iv", "type": "float", "desc": "Bartik 工具变量"},
        {"name": "provcd", "type": "int", "desc": "省份代码"},
    ],
    "CHIP": [
        {"name": "hid", "type": "int", "desc": "家庭 id"},
        {"name": "urban", "type": "int", "desc": "城乡虚拟变量"},
        {"name": "ln_income", "type": "float", "desc": "对数家庭收入"},
        {"name": "house_size", "type": "int", "desc": "家庭规模"},
        {"name": "age", "type": "int", "desc": "户主年龄"},
        {"name": "edu", "type": "int", "desc": "户主教育年限"},
        {"name": "industry", "type": "int", "desc": "行业代码"},
        {"name": "year", "type": "int", "desc": "调查年份"},
    ],
    "CHARLS": [
        {"name": "id", "type": "str", "desc": "个体 id"},
        {"name": "urban", "type": "int", "desc": "城乡虚拟变量"},
        {"name": "ln_wage", "type": "float", "desc": "对数工资"},
        {"name": "age", "type": "int", "desc": "年龄"},
        {"name": "edu", "type": "int", "desc": "教育年限"},
        {"name": "female", "type": "int", "desc": "性别"},
        {"name": "year", "type": "int", "desc": "调查年份"},
    ],
    "custom": [
        {"name": "id", "type": "str", "desc": "主键"},
        {"name": "y", "type": "float", "desc": "被解释变量"},
        {"name": "x", "type": "float", "desc": "核心解释变量"},
        {"name": "control_1", "type": "float", "desc": "控制变量 1"},
        {"name": "control_2", "type": "float", "desc": "控制变量 2"},
    ],
}


# ── 1. load_schema ──────────────────────────────────────────────────────────


def load_schema(
    dataset_name: str,
    data_root: Path,
    custom_dataset_path: Optional[str] = None,
) -> str:
    """读取数据集 schema YAML 字符串。

    优先尝试 data/{dataset_name}/schema.yaml；找不到则返回内置 stub。
    """
    if custom_dataset_path:
        custom = Path(custom_dataset_path)
        if custom.is_file() and custom.suffix.lower() in {".yaml", ".yml"}:
            return custom.read_text(encoding="utf-8")

    schema_path = data_root / dataset_name / "schema.yaml"
    if schema_path.is_file():
        return schema_path.read_text(encoding="utf-8")

    # 兜底 stub
    columns = _DATASET_STUBS.get(dataset_name, _DATASET_STUBS["custom"])
    return yaml.safe_dump(
        {"dataset": dataset_name, "columns": columns},
        allow_unicode=True,
        sort_keys=False,
    )


# ── 2. build_mapping ───────────────────────────────────────────────────────


def build_mapping(
    brief_text: str,
    schema_yaml: str,
    prompt_loader: Callable[[], str],
    *,
    model: str = "MiniMax-M3",
    provider_id: str = "openrouter",
    temperature: float = 0.3,
) -> list[Variable]:
    """调 LLM 解析 schema + brief → list[Variable]。

    LLM 返回 YAML（Program/prompts/variables/v1.md 约定），本函数：
    1. 抽取 ```yaml ... ``` 代码块（容错：整段也接受）
    2. 解析为 dict
    3. 转换为 list[Variable]（Pydantic 校验 role 枚举）
    """
    # prompt 模板填充
    template = prompt_loader()
    research_question, required = _split_brief(brief_text)
    prompt = template.format(
        dataset_name="(see schema)",
        schema_yaml=schema_yaml,
        research_question=research_question,
        required_variables=required,
    )

    text, _usage = chat_completion(
        messages=[{"role": "user", "content": prompt}],
        provider_id=provider_id,
        model=model,
        temperature=temperature,
    )

    payload = _parse_yaml_payload(text)
    raw_vars = payload.get("variables", [])
    if not isinstance(raw_vars, list):
        raise ValueError("LLM 输出不含 variables 列表")

    variables: list[Variable] = []
    for item in raw_vars:
        if not isinstance(item, dict):
            continue
        # Pydantic 会校验 role 枚举；非法时抛 ValidationError
        variables.append(Variable(**item))
    return variables


def _split_brief(brief_text: str) -> tuple[str, str]:
    """从 brief markdown 中提取研究问题 + 推断所需变量。

    简化版：用最常见的关键词识别；若 brief 为空则返回占位。
    """
    text = (brief_text or "").strip()
    if not text:
        return "（未提供）", "（未指定）"

    # 抽取 ## 研究问题 段
    m = re.search(r"##\s*研究问题\s*\n+([\s\S]*?)(?=\n##|\Z)", text)
    question = m.group(1).strip() if m else text.splitlines()[0]

    # 推断所需变量关键词（粗启发式）
    keywords: list[str] = []
    for kw, var in (
        ("机器人", "X: 工业机器人渗透率"),
        ("工资", "Y: 对数小时工资"),
        ("就业", "Y: 是否就业 / 就业状态"),
        ("职业", "Y: ISEI 职业地位评分"),
        ("教育", "control: 受教育年限"),
        ("年龄", "control: 年龄"),
    ):
        if kw in text:
            keywords.append(var)
    required = "\n".join(f"- {k}" for k in keywords) or "- X: 核心解释变量\n- Y: 被解释变量"
    return question, required


def _parse_yaml_payload(text: str) -> dict:
    """从 LLM 输出中抽 YAML 块并解析。"""
    # 优先抽取 ```yaml ... ``` 代码块
    fence_match = re.search(r"```(?:yaml|yml)?\s*\n([\s\S]*?)```", text)
    yaml_text = fence_match.group(1).strip() if fence_match else text.strip()

    # 容错：去掉首行的 "yaml" 标记
    yaml_text = re.sub(r"^yaml\s*\n", "", yaml_text, flags=re.MULTILINE)

    parsed = yaml.safe_load(yaml_text)
    if not isinstance(parsed, dict):
        raise ValueError(f"LLM 输出不是 YAML dict: {type(parsed).__name__}")
    return parsed


# ── 3. write_variables ─────────────────────────────────────────────────────


def write_variables(
    variables: list[Variable],
    topic: str,
    topic_slug: str,
    tasks_root: Path,
    *,
    model: str = "MiniMax-M3",
    prompt_version: str = "v1",
) -> Path:
    """落盘 Tasks/{topic_slug}/variables.yaml，附 provenance frontmatter。"""
    topic_dir = tasks_root / topic_slug
    topic_dir.mkdir(parents=True, exist_ok=True)
    path = topic_dir / "variables.yaml"

    # 序列化变量为 YAML body
    body = yaml.safe_dump(
        {"variables": [v.model_dump() for v in variables]},
        allow_unicode=True,
        sort_keys=False,
    )

    frontmatter = yaml.safe_dump(
        {
            "topic": topic,
            "topic_slug": topic_slug,
            "generated_by": "variables-llm-m3",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "prompt_version": prompt_version,
            "n_variables": len(variables),
            "roles": sorted({v.role for v in variables}),
            "upstream": ["brief.md"],
            "downstream_consumers": ["design.json", "execution"],
        },
        allow_unicode=True,
        sort_keys=False,
    )
    path.write_text(f"---\n{frontmatter}---\n\n{body}\n", encoding="utf-8")
    return path


# ── 4. verify_variables ────────────────────────────────────────────────────


def verify_variables(variables: list, min_count: int = 3) -> bool:
    """verdict gate。

    返回 True 当且仅当：
    - len(variables) >= min_count
    - 每条都有合法 role ∈ {X, Y, control, mediator, moderator}
    - 每条都有非空的 dataset_column + semantic_label
    """
    if len(variables) < min_count:
        return False
    for v in variables:
        role = getattr(v, "role", None)
        if role not in _VALID_ROLES:
            return False
        col = getattr(v, "dataset_column", None)
        label = getattr(v, "semantic_label", None)
        if not col or not label:
            return False
    return True


# ── 5. run_variables (端到端) ──────────────────────────────────────────────


def run_variables(
    req: VariablesRequest,
    *,
    data_root: Path,
    tasks_root: Path,
    prompt_loader: Optional[Callable[[], str]] = None,
    model: str = "MiniMax-M3",
) -> VariablesResponse:
    """端到端：load_schema → build_mapping → write_variables → verify。"""
    from Program.prompts.variables.v1 import load_prompt_v1 as _default_loader

    loader = prompt_loader or _default_loader

    # 读取 brief 文本
    brief_path = Path(req.brief_path)
    brief_text = brief_path.read_text(encoding="utf-8") if brief_path.is_file() else ""

    # 1. 加载 schema
    schema_yaml = load_schema(
        dataset_name=req.dataset_name,
        data_root=data_root,
        custom_dataset_path=req.custom_dataset_path,
    )

    # 2. 调 LLM 映射
    variables = build_mapping(
        brief_text=brief_text,
        schema_yaml=schema_yaml,
        prompt_loader=loader,
        model=model,
    )

    # 3. 落盘
    topic = brief_text.splitlines()[0] if brief_text else req.topic_slug
    path = write_variables(
        variables=variables,
        topic=topic,
        topic_slug=req.topic_slug,
        tasks_root=tasks_root,
        model=model,
    )

    # 4. verdict
    passed = verify_variables(variables, min_count=3)

    # 5. 构造响应（复用 variables_yaml 字段供前端回显）
    body = yaml.safe_dump(
        {"variables": [v.model_dump() for v in variables]},
        allow_unicode=True,
        sort_keys=False,
    )
    return VariablesResponse(
        variables_yaml=body,
        variables_path=str(path),
        variables=variables,
        verdict_passed=passed,
    )
