"""任务书 (Brief) wrapper service.

行为契约 (BDD ref: spec §6.1 row 1):
- build_brief: 用 LLM 把 topic 扩写为 4 段 markdown
- write_brief: 落盘到 Tasks/{topic_slug}/brief.md，附 provenance frontmatter
- verify_brief: 4 段齐全才返回 True (verdict gate)
- run_brief: 端到端入口 (build + write + verify)

设计要点:
- LLM 入口使用 `Product.backend.llm_client.chat_completion` (与 spec §3.2 一致)
- 真实底层模型走 minimax provider preset (`MiniMax-M3`，Anthropic-compatible)
  参考: ~/Desktop/AI组件工作流库/components/minimax-token-plan-real-service/WORKFLOW.md
- model 字段为 `MiniMax-M3` (而非旧的 MiniMax-M3 — 那是 spec 早期笔误)
- 真实 provider/model 通过 chat_completion 的 provider_id/model 参数注入
- 测试通过 conftest.py 在 `Product.backend.wrapper.brief_service` 命名空间上
  mock `chat_completion` —— 不需要真实 API key
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import yaml

from Product.backend.llm_client import chat_completion
from Product.types.research import BriefRequest, BriefResponse

REQUIRED_SECTIONS = ["研究问题", "边际贡献", "研究边界", "成功标准"]

# 真实底层模型：MiniMax Token Plan (Anthropic-compatible)
_MODEL = "MiniMax-M3"
_PROVIDER_ID = "minimax"


def build_brief(topic: str, prompt_loader: Callable[[], str]) -> str:
    """调 LLM 把研究课题扩写为 4 段 markdown。

    Args:
        topic: 用户输入的研究课题
        prompt_loader: 返回 prompt 模板的 callable，模板需含 {topic} 占位符

    Returns:
        4 段 markdown 字符串
    """
    prompt_template = prompt_loader()
    prompt = prompt_template.replace("{topic}", topic)
    text, _usage = chat_completion(
        messages=[{"role": "user", "content": prompt}],
        provider_id=_PROVIDER_ID,
        model=_MODEL,
        temperature=0.3,
    )
    return text


def write_brief(
    content: str,
    topic: str,
    topic_slug: str,
    tasks_root: Path,
    model: str = _MODEL,
    prompt_version: str = "v1",
) -> Path:
    """落盘到 Tasks/{topic_slug}/brief.md，附 YAML provenance frontmatter。

    Args:
        content: 4 段 markdown 主体
        topic: 用户原始课题
        topic_slug: URL-safe slug (与 Tasks 子目录名一致)
        tasks_root: Tasks/ 目录根
        model: 实际生成用的模型 (默认 MiniMax-M3)
        prompt_version: 使用的 prompt 版本 (默认 v1)

    Returns:
        写入文件的 Path
    """
    topic_dir = tasks_root / topic_slug
    topic_dir.mkdir(parents=True, exist_ok=True)
    path = topic_dir / "brief.md"
    frontmatter = yaml.safe_dump(
        {
            "topic": topic,
            "topic_slug": topic_slug,
            "generated_by": "brief-llm-minimax",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "prompt_version": prompt_version,
            "upstream": [],
            "downstream_consumers": ["literature.md", "variables.yaml"],
        },
        allow_unicode=True,
        sort_keys=False,
    )
    path.write_text(f"---\n{frontmatter}---\n\n{content}\n", encoding="utf-8")
    return path


def verify_brief(content: str) -> bool:
    """verdict gate: 4 段 (## 标题) 齐全才返回 True。

    允许 ## 或 # 两种 heading 层级 (防御 LLM 偶尔用 # 开头)。
    """
    return all(f"## {sec}" in content or f"# {sec}" in content for sec in REQUIRED_SECTIONS)


def run_brief(req: BriefRequest, tasks_root: Path) -> BriefResponse:
    """端到端 brief service 入口: build → write → verify。

    Args:
        req: 包含 topic 和可选 topic_slug
        tasks_root: Tasks/ 目录根

    Returns:
        BriefResponse (含 brief_markdown, brief_path, verdict_passed)
    """
    from Program.prompts.brief.v1 import load_prompt_v1

    content = build_brief(req.topic, load_prompt_v1)
    slug = req.topic_slug or _slugify(req.topic)
    path = write_brief(content, req.topic, slug, tasks_root)
    return BriefResponse(
        brief_markdown=content,
        brief_path=str(path),
        verdict_passed=verify_brief(content),
    )


def _slugify(topic: str) -> str:
    """简化版 slugify: 中英混合 → ASCII-only kebab-case。

    非 ASCII 字符直接丢弃 (中文字段 slug 用拼音/英文别名；这里取保守的 ASCII-only 策略)。
    """
    ascii_part = re.sub(r"[^a-zA-Z0-9]+", "-", topic).strip("-").lower()
    return ascii_part[:50] or "untitled"
