"""L4-design: 方法设计 (Design) wrapper service.

端到端流程：
1. load_variables 解析 variables.yaml
2. build_candidates 调 LLM + sp_fn 生成 3 个 DesignCandidate
3. verify_design verdict gate
4. generate_code_stub 根据推荐方法生成 Python 模板
5. write_design 落盘 design.json

依赖：
- Product.backend.llm_client.chat_completion（真实 LLM 调用，可注入 mock）
- sp_fn 抽象（默认走 Product.backend.statspai_adapter 或返回占位）
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

import yaml

from Product.backend.llm_client import chat_completion
from Product.types.research import (
    DesignCandidate,
    DesignRequest,
    DesignResponse,
    Variable,
)


ALLOWED_METHODS = {"DID", "IV", "RDD", "PSM", "DML"}

DEFAULT_MODEL = "MiniMax-M3"
DEFAULT_PROVIDER = "minimax"
DEFAULT_LLM_MODEL = "MiniMax-M3"


# ============== 1. load_variables ==============

def load_variables(variables_path: Path | str) -> list[Variable]:
    """解析 variables.yaml → list[Variable]。

    容错：YAML 结构必须含 `variables` 列表，每项至少有 role/dataset_column。
    """
    path = Path(variables_path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or "variables" not in raw:
        raise ValueError(f"variables.yaml missing 'variables' key: {path}")
    items = raw["variables"]
    if not isinstance(items, list):
        raise ValueError(f"variables.yaml 'variables' must be list: {path}")
    result: list[Variable] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        result.append(
            Variable(
                role=item.get("role", "control"),
                dataset_column=item.get("dataset_column", ""),
                semantic_label=item.get("semantic_label", ""),
                description=item.get("description", ""),
                reference_papers=item.get("reference_papers", []) or [],
            )
        )
    return result


# ============== 2. build_candidates ==============

def _default_sp_fn(method: str, variables: list) -> dict[str, Any]:
    """默认 sp_fn：尝试 import StatsPAI，否则返回占位 dict。

    真实生产环境会从 Product.backend.statspai_adapter 拉取 estimator 推荐；
    测试环境可注入自定义 sp_fn。
    """
    sp_output: dict[str, Any] = {
        "estimator": method.lower(),
        "n_variables": len(variables),
        "source": "placeholder",
    }
    try:
        import sys
        stats_pai_path = "/Users/mahaoxuan/Desktop/经济学论文/StatsPAI/src"
        if stats_pai_path not in sys.path:
            sys.path.insert(0, stats_pai_path)
        import statspai  # type: ignore[import-untyped]
        spec = statspai.describe_function(method.lower())
        sp_output["source"] = "statspai"
        sp_output["statspai_category"] = spec.get("category", "unknown")
        sp_output["statspai_description"] = spec.get("description", "")
    except Exception:
        # StatsPAI 不可用时降级到 placeholder
        pass
    return sp_output


def _parse_llm_candidates(llm_text: str) -> tuple[list[dict[str, Any]], str]:
    """从 LLM 文本中解析 JSON（容忍 markdown fence / 前言后语）。"""
    text = llm_text.strip()
    # 尝试剥离 ```json ... ``` 围栏
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    # 找首个 { 到末尾最后一个 }
    if "{" in text:
        start = text.index("{")
        end = text.rfind("}")
        if end > start:
            text = text[start : end + 1]
    parsed = json.loads(text)
    candidates = parsed.get("candidates", [])
    recommended = parsed.get("recommended", "")
    if not isinstance(candidates, list):
        raise ValueError("LLM JSON missing 'candidates' list")
    if not recommended:
        raise ValueError("LLM JSON missing 'recommended' field")
    return candidates, recommended


def build_candidates(
    brief_text: str,
    variables: list[Variable],
    sp_fn: Optional[Callable[[str, list], dict[str, Any]]] = None,
    prompt_loader: Optional[Callable[[], str]] = None,
    *,
    provider_id: str = DEFAULT_PROVIDER,
    model: str = DEFAULT_LLM_MODEL,
) -> tuple[list[DesignCandidate], str]:
    """调 LLM 评估 + sp_fn 推荐 → (candidates, recommended)。

    返回：长度为 3-5 的 DesignCandidate 列表 + LLM 推荐的 method 字符串。

    - brief_text: 简报内容（可含 markdown）
    - variables: load_variables 返回的 list[Variable]
    - sp_fn: 可注入的 StatsPAI 适配函数，签名 (method: str, variables: list) -> dict
    - prompt_loader: 加载 design prompt 模板
    """
    if prompt_loader is None:
        from Program.prompts.design.v1 import load_prompt_v1 as _loader
        prompt_loader = _loader

    variables_yaml = yaml.safe_dump(
        {"variables": [v.model_dump() for v in variables]},
        allow_unicode=True,
        sort_keys=False,
    )

    sp_fn = sp_fn or _default_sp_fn

    # 先调 sp_fn 对 5 个方法逐一预评估，作为 sp_candidates_json 喂给 LLM
    sp_candidates: list[dict[str, Any]] = []
    for m in ALLOWED_METHODS:
        sp_candidates.append({"method": m, "sp_output": sp_fn(m, variables)})
    sp_candidates_json = json.dumps(sp_candidates, ensure_ascii=False)

    template = prompt_loader()
    user_prompt = (
        template
        .replace("{research_question}", brief_text[:1500])
        .replace("{variables_yaml}", variables_yaml)
        .replace("{sp_candidates_json}", sp_candidates_json)
    )

    text, _usage = chat_completion(
        messages=[{"role": "user", "content": user_prompt}],
        provider_id=provider_id,
        model=model,
        temperature=0.3,
    )

    raw_candidates, llm_recommended = _parse_llm_candidates(text)

    # 还原成 Pydantic 模型；同时让 sp_fn 覆盖 sp_output（sp_fn 是真实推荐源）
    candidates: list[DesignCandidate] = []
    for item in raw_candidates:
        method = str(item.get("method", "")).upper()
        if method not in ALLOWED_METHODS:
            continue
        candidates.append(
            DesignCandidate(
                method=method,
                rationale=str(item.get("rationale", "")),
                fits_data=bool(item.get("fits_data", True)),
                sp_output=sp_fn(method, variables),
            )
        )

    if len(candidates) < 3:
        # LLM 不足 3 个时，用 sp_fn 补足剩余方法
        existing = {c.method for c in candidates}
        for m in ALLOWED_METHODS:
            if len(candidates) >= 3:
                break
            if m in existing:
                continue
            candidates.append(
                DesignCandidate(
                    method=m,
                    rationale=f"由 StatsPAI 估算 {m} 的 estimand 候选，由 wrapper 自动补足。",
                    fits_data=True,
                    sp_output=sp_fn(m, variables),
                )
            )

    # 决定 recommended：优先 LLM 推荐的方法；若 LLM 推荐不在 candidates 中，
    # fallback 到第一个 candidate 的 method
    candidate_methods = {c.method for c in candidates}
    recommended = llm_recommended.upper() if llm_recommended.upper() in candidate_methods else (
        candidates[0].method if candidates else "DID"
    )
    return candidates[:5], recommended


# ============== 3. verify_design ==============

def verify_design(candidates: list[DesignCandidate], recommended: str) -> bool:
    """verdict gate: candidates >= 3 且 recommended ∈ {c.method for c in candidates}."""
    if len(candidates) < 3:
        return False
    methods = {c.method for c in candidates}
    return recommended in methods


# ============== 4. generate_code_stub ==============

_CODE_STUB_TEMPLATES: dict[str, str] = {
    "DID": """# {method} 双重差分估计模板
import pandas as pd
import statsmodels.api as sm
from linearmodels.panel import PanelOLS

df = pd.read_csv("data/cfps.csv")
# TODO: 替换为真实处理组/对照组列名
df["post"] = (df["year"] >= 2014).astype(int)
df["treat"] = df["city_robot_exposure"].apply(lambda x: 1 if x > 0 else 0)
df["did"] = df["post"] * df["treat"]

X = df[["treat", "post", "did"] + ["age", "edu"]]
X = sm.add_constant(X)
y = df["ln_wage"]
model = sm.OLS(y, X).fit()
print(model.summary())
""",
    "IV": """# {method} 工具变量估计模板
import pandas as pd
import statsmodels.api as sm

df = pd.read_csv("data/cfps.csv")
# TODO: 替换为真实内生变量 / 工具变量
endog = df["robot_exposure"]
instruments = df["bartik_iv"]
exog = df[["age", "edu"]]
exog = sm.add_constant(exog)

from linearmodels.iv import IV2SLS
model = IV2SLS(df["ln_wage"], exog, endog, instruments).fit(cov_type="robust")
print(model.summary)
""",
    "RDD": """# {method} 断点回归估计模板
import pandas as pd
import numpy as np

df = pd.read_csv("data/cfps.csv")
# TODO: 替换为真实 forcing variable / cutoff
running = df["forcing_var"]
cutoff = 0.5
df["treat"] = (running >= cutoff).astype(int)
df["centered"] = running - cutoff

from rdrobust import rdrobust
result = rdrobust(df["ln_wage"], running, c=cutoff)
print(result.summary())
""",
    "PSM": """# {method} 倾向得分匹配模板
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors

df = pd.read_csv("data/cfps.csv")
# TODO: 替换为真实 treatment / covariates
treatment = df["high_robot_exposure"]
features = df[["age", "edu", "female"]]

logit = LogisticRegression(max_iter=1000)
pscore = logit.fit(features, treatment).predict_proba(features)[:, 1]

treated_idx = df[treatment == 1].index
control_idx = df[treatment == 0].index
nn = NearestNeighbors(n_neighbors=1).fit(pscore[control_idx].reshape(-1, 1))
distances, indices = nn.kneighbors(pscore[treated_idx].reshape(-1, 1))
matched_control = control_idx[indices.flatten()]
print(f"matched pairs: {len(matched_control)}")
print(df.loc[treated_idx, "ln_wage"].mean() - df.loc[matched_control, "ln_wage"].mean())
""",
    "DML": """# {method} Double Machine Learning 模板
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from doubleml import DoubleMLPLR

df = pd.read_csv("data/cfps.csv")
# TODO: 替换为真实 Y / D / X
dml_data = DoubleMLPLR.from_arrays(
    x=df[["age", "edu"]].values,
    y=df["ln_wage"].values,
    d=df["robot_exposure"].values,
    ml_l=GradientBoostingRegressor(),
    ml_m=GradientBoostingClassifier(),
)
result = dml_data.fit()
print(result.summary)
""",
}


def generate_code_stub(method: str, variables: list[Variable]) -> str:
    """根据方法名返回对应的 Python 代码模板。"""
    method = method.upper()
    template = _CODE_STUB_TEMPLATES.get(method, _CODE_STUB_TEMPLATES["DID"])
    # 使用 str.replace 避免与模板内 f-string 形式的 {} 冲突
    return template.replace("{method}", method)


# ============== 5. write_design ==============

def write_design(
    *,
    candidates: list[DesignCandidate],
    recommended: str,
    code_stub: str,
    topic: str,
    topic_slug: str,
    tasks_root: Path | str,
    model: str = DEFAULT_MODEL,
    prompt_version: str = "v1",
) -> Path:
    """落盘 design.json 到 Tasks/{topic_slug}/design.json。

    结构（顶层 JSON）：
    {
      "topic": str,
      "topic_slug": str,
      "generated_by": "design-llm-m3",
      "timestamp": str,
      "model": str,
      "prompt_version": str,
      "upstream": ["brief.md", "variables.yaml"],
      "candidates": [{method, rationale, fits_data, sp_output}, ...],
      "recommended": str,
      "code_stub": str
    }
    """
    tasks_root = Path(tasks_root)
    topic_dir = tasks_root / topic_slug
    topic_dir.mkdir(parents=True, exist_ok=True)
    path = topic_dir / "design.json"
    payload = {
        "topic": topic,
        "topic_slug": topic_slug,
        "generated_by": "design-llm-minimax",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "prompt_version": prompt_version,
        "upstream": ["brief.md", "variables.yaml"],
        "candidates": [c.model_dump() for c in candidates],
        "recommended": recommended,
        "code_stub": code_stub,
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


# ============== 6. run_design 端到端 ==============

def _slugify(topic: str) -> str:
    ascii_part = re.sub(r"[^a-zA-Z0-9]+", "-", topic).strip("-").lower()
    return ascii_part[:50] or "untitled"


def run_design(
    req: DesignRequest,
    tasks_root: Path | str,
    *,
    sp_fn: Optional[Callable[[str, list], dict[str, Any]]] = None,
) -> DesignResponse:
    """端到端 design service 入口。

    1. 从 req.variables_path 加载 variables
    2. 从 req.brief_path 读简报（缺则用 topic_slug 替代）
    3. build_candidates
    4. 选择 recommended = 第一个 candidate 的 method
       （也可根据 LLM 返回的 recommended 选择，sp_fn 覆盖后该字段已失效，
        简单起见取第 1 个）
    5. generate_code_stub
    6. write_design
    7. 构造 DesignResponse
    """
    tasks_root_path = Path(tasks_root)
    variables = load_variables(req.variables_path)

    brief_text = ""
    if req.brief_path:
        bp = Path(req.brief_path)
        if bp.exists():
            brief_text = bp.read_text(encoding="utf-8")
    if not brief_text:
        brief_text = f"研究主题：{req.topic_slug}"

    candidates, recommended = build_candidates(
        brief_text=brief_text,
        variables=variables,
        sp_fn=sp_fn,
    )

    code_stub = generate_code_stub(recommended, variables)

    # 读取 topic（从 variables.yaml 推断不出 topic，从 brief frontmatter 推断）
    topic = req.topic_slug
    brief_path = Path(req.brief_path)
    if brief_path.exists():
        first_line = brief_path.read_text(encoding="utf-8").split("\n", 1)[0]
        # 简报 frontmatter 内含 topic: ...
        for line in brief_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("topic:"):
                topic = line.split(":", 1)[1].strip()
                break

    path = write_design(
        candidates=candidates,
        recommended=recommended,
        code_stub=code_stub,
        topic=topic,
        topic_slug=req.topic_slug,
        tasks_root=tasks_root_path,
    )

    design_json = path.read_text(encoding="utf-8")
    return DesignResponse(
        design_json=design_json,
        design_path=str(path),
        candidates=candidates,
        recommended=recommended,
        code_stub=code_stub,
        verdict_passed=verify_design(candidates, recommended),
    )
