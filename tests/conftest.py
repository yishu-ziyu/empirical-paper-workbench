"""全局 test fixtures: 隔离 LLM 调用 + 隔离 LLM 客户端。

设计原则：
- L4 design tab 的测试用 `unittest.mock.patch` 直接替换
  `Product.backend.wrapper.design_service.chat_completion`，
  因此 conftest 只在测试需要默认 fallback mock 时生效。
- 这里提供一个 `mock_llm_chat_completion` fixture 供其他 lane 的 wrapper 测试复用。
"""
from __future__ import annotations

from unittest.mock import patch

import pytest


@pytest.fixture
def mock_llm_chat_completion():
    """默认 mock LLM chat_completion 返回固定 markdown（兜底）。"""
    def _fake(messages, **kwargs):
        text = (
            "## 研究问题\n工业机器人对就业结构的影响。\n\n"
            "## 边际贡献\n1. 新数据 2. 新方法 3. 新结论\n\n"
            "## 研究边界\n1. 不含服务业 2. 不含农村 3. 不含小企业\n\n"
            "## 成功标准\nX 系数 p < 0.05\n"
        )
        return text, {"input_tokens": 100, "output_tokens": 200}
    with patch("Product.backend.llm_client.chat_completion", side_effect=_fake):
        yield _fake
