from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


def render_template(template_path: Path, context: dict[str, Any]) -> str:
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(template_path.name)
    return template.render(**context)


def build_draft_context(
    paper_config: dict[str, Any],
    dataset_exists: bool,
    mode: str,
) -> dict[str, Any]:
    return {
        "title": paper_config["project"]["title"],
        "research_question": paper_config["research"]["question"],
        "contribution": paper_config["research"]["contribution"],
        "current_stage": paper_config["research"]["current_stage"],
        "baseline_candidates": paper_config["methods"]["baseline"]["candidates"],
        "robustness_checks": paper_config["methods"]["robustness"],
        "dataset_path": paper_config["data"]["final_dataset"],
        "dataset_exists": dataset_exists,
        "mode": mode,
    }


def build_qmd_content(title: str, markdown_content: str) -> str:
    quoted_title = json.dumps(title, ensure_ascii=False)
    stable_markdown = stabilize_markdown_for_pdf(markdown_content)
    return "\n".join(
        [
            "---",
            f"title: {quoted_title}",
            "lang: zh",
            "format:",
            "  pdf:",
            "    pdf-engine: xelatex",
            "documentclass: ctexart",
            "keep-tex: true",
            "---",
            "",
            stable_markdown.rstrip(),
            "",
        ]
    )


def stabilize_markdown_for_pdf(markdown_content: str) -> str:
    replacements = {
        "## Question": "## 研究问题",
        "## Data": "## 数据",
        "## Identification": "## 识别策略",
        "## Estimator": "## 估计方法",
        "## Results": "## 结果",
        "## Robustness": "## 稳健性检查",
        "## References": "## 参考文献",
        "**Outcome**": "**结果变量**",
        "**Treatment**": "**处理变量**",
        "**Design (auto-detected)**": "**自动识别设计**",
        "Sample size": "样本规模",
        "Missingness (top 5)": "缺失值最高的 5 个字段",
        "Verdict": "判断",
        "**Method**": "**方法**",
        "**Function**": "**函数**",
        "**Rationale**": "**理由**",
        "**Key assumptions**": "**关键假设**",
        "**Coefficient on": "**系数：",
        "ℹ️": "Info:",
        "✅": "Pass:",
        "⚙️": "Note:",
        "≈": "approximately",
        "≥": ">=",
        "≤": "<=",
        "ε": "epsilon",
        "β": "beta",
        "δ": "delta",
        "α": "alpha",
    }
    stable = markdown_content
    for source, target in replacements.items():
        stable = stable.replace(source, target)
    return stable
