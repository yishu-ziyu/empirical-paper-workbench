"""Shared test fixtures.

为避免在测试中真实调用 LLM 端点，提供两层 mock：
1. `mock_llm`（autouse）：拦截所有 wrapper service 的 LLM 调用。
   只对已存在的 wrapper 模块打 patch（`importlib.import_module` + `ModuleNotFoundError` catch），
   并行 build 中其他 lane 的 wrapper 可能尚未到位。
2. `mock_llm_chat_completion`（非 autouse）：供需要显式控制 mock 行为的测试使用
   （如 L4 design tab 的测试用 `unittest.mock.patch` 直接替换
   `Product.backend.wrapper.design_service.chat_completion`）。
"""
from __future__ import annotations

import importlib
from unittest.mock import patch

import pytest


# ── 1. Autouse: 拦截所有 wrapper service 的 LLM 调用 ────────────────────────
#
# The set of wrapper modules that re-export chat_completion from llm_client.
# Other lanes' wrappers (search/variables/design/execute) live in this same
# namespace — patching at the namespace level keeps tests independent.
_WRAPPER_MODULES = (
    "Product.backend.wrapper.brief_service",
    "Product.backend.wrapper.search_service",
    "Product.backend.wrapper.variables_service",
    "Product.backend.wrapper.design_service",
    "Product.backend.wrapper.execute_service",
)


_FAKE_BRIEF_TEXT = (
    "## 研究问题\n"
    "工业机器人是否影响城市制造业就业结构？\n\n"
    "## 边际贡献\n"
    "- 新证据\n- 新方法\n\n"
    "## 研究边界\n"
    "- 不包括服务业\n- 不包括农村\n- 限于 2010-2022\n\n"
    "## 成功标准\n"
    "- 系数显著 p<0.05\n- 平衡性检验通过\n"
)


def _fake_chat(messages, **kwargs):  # noqa: ARG001
    """Drop-in replacement for llm_client.chat_completion.

    Returns a 4-section brief markdown so brief-service BDD tests pass without
    any network call. Other lanes' wrappers can extend detection later.
    """
    return _FAKE_BRIEF_TEXT, {"input_tokens": 100, "output_tokens": 200}


@pytest.fixture(autouse=True)
def mock_llm(monkeypatch):
    """Autouse: 拦截所有 wrapper service 的 LLM 调用。

    只对已存在的 wrapper 模块打 patch —— 在并行 build 中，每个 lane 的 wrapper
    可能尚未到位；import 不存在的模块只会让其他 lane 的测试崩掉。
    """
    for module_name in _WRAPPER_MODULES:
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        monkeypatch.setattr(f"{module_name}.chat_completion", _fake_chat, raising=False)
    yield


# ── 2. 非 autouse：供显式需要 mock 行为的测试使用 ──────────────────────────


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
