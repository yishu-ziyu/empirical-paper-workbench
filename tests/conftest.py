"""Shared test fixtures.

为避免在测试中真实调用 LLM 端点，所有测试自动注入 chat_completion mock。
mock 命中 Product.backend.wrapper.* 模块中的 chat_completion 本地引用，
确保各 lane 的 wrapper service 调用都被拦截。
"""
import importlib

import pytest

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

    Returns a 4-section brief markdown so the brief-service BDD tests pass
    without any network call. Other lanes' wrappers can extend detection
    later.
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
