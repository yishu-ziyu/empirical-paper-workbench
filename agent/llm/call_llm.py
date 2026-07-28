"""ADR-0008: 统一 LLM 调用入口。

保持与现有 call_llm 的 monkeypatch 模式兼容。

设计要点：
- 生产环境根据 router 配置调真实 LLM（Stage 2 接 SDK）
- 开发/测试通过 monkeypatch 替换为 mock
- provider=mock 时返回占位字符串
- 不 import nodes.*，避免循环依赖
"""
from typing import Optional

from .router import router, LLMConfig


def call_llm(prompt: str, node_type: str = "default") -> str:
    """统一 LLM 调用入口。

    Args:
        prompt: LLM prompt
        node_type: "generate" | "review" | "title" | "outline" | ...
            未知 node_type 用 default 配置（= generate）。

    Returns:
        LLM 响应文本

    生产环境根据 router 配置调真实 LLM；开发/测试通过 monkeypatch 替换。
    Stage 1：provider=mock 返回占位；非 mock 返回占位（Stage 2 接真实 SDK）。
    """
    config = router.get_config(node_type)
    if config.provider == "mock":
        return "Mock LLM response"
    # 生产环境接真实 LLM（langchain-anthropic / openai）
    # Stage 2 将在此分支调真实 LLM；当前占位
    return f"[{config.provider}/{config.model}] Placeholder response"
