"""ADR-0008: LLM 路由器测试。

契约（见 docs/adr/0008-multi-llm-routing.md §7 Fitness Functions）：
1. 默认配置（无环境变量）provider == "mock"
2. GENERATE/REVIEW 配置不同时 is_multi_llm() == True
3. GENERATE/REVIEW 配置相同时 is_multi_llm() == False
4. 未知 node_type 降级为 default（非 None）
5. LLMConfig.from_env 正确解析环境变量
6. get_config("generate") 与 get_config("default") 返回同一配置
7. call_llm 统一入口在 mock 下返回占位字符串
"""
from __future__ import annotations

import pytest

from llm.router import LLMRouter, LLMConfig
from llm.call_llm import call_llm


# ---------------------------------------------------------------------------
# 默认配置
# ---------------------------------------------------------------------------
def test_default_config_is_mock():
    """未设环境变量时 generate provider 默认 mock（向后兼容）。"""
    router = LLMRouter()
    gen = router.get_config("generate")
    assert gen.provider == "mock"
    rev = router.get_config("review")
    assert rev.provider == "mock"


def test_default_not_multi_llm():
    """默认全 mock 时 is_multi_llm() == False。"""
    router = LLMRouter()
    assert not router.is_multi_llm()


# ---------------------------------------------------------------------------
# 多 LLM 检测
# ---------------------------------------------------------------------------
def test_multi_llm_detection(monkeypatch):
    """GENERATE 与 REVIEW 用不同 provider 时 is_multi_llm() == True。"""
    monkeypatch.setenv("GENERATE_LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("GENERATE_LLM_MODEL", "claude-3-opus")
    monkeypatch.setenv("REVIEW_LLM_PROVIDER", "openai")
    monkeypatch.setenv("REVIEW_LLM_MODEL", "gpt-4")
    router = LLMRouter()
    assert router.is_multi_llm()


def test_multi_llm_detection_same_provider_diff_model(monkeypatch):
    """同 provider 不同 model 也算多 LLM（如 gpt-4o vs gpt-4o-mini）。"""
    monkeypatch.setenv("GENERATE_LLM_PROVIDER", "openai")
    monkeypatch.setenv("GENERATE_LLM_MODEL", "gpt-4o")
    monkeypatch.setenv("REVIEW_LLM_PROVIDER", "openai")
    monkeypatch.setenv("REVIEW_LLM_MODEL", "gpt-4o-mini")
    router = LLMRouter()
    assert router.is_multi_llm()


def test_same_config_not_multi(monkeypatch):
    """provider 与 model 都相同时 is_multi_llm() == False。"""
    monkeypatch.setenv("GENERATE_LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("GENERATE_LLM_MODEL", "claude-3-opus")
    monkeypatch.setenv("REVIEW_LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("REVIEW_LLM_MODEL", "claude-3-opus")
    router = LLMRouter()
    assert not router.is_multi_llm()


# ---------------------------------------------------------------------------
# 未知节点降级
# ---------------------------------------------------------------------------
def test_unknown_node_uses_default():
    """未知 node_type 返回 default 配置（非 None）。"""
    router = LLMRouter()
    config = router.get_config("unknown_node")
    assert config is not None
    assert config.provider == "mock"


def test_default_equals_generate():
    """default 配置与 generate 配置一致。"""
    router = LLMRouter()
    default_cfg = router.get_config("default")
    gen_cfg = router.get_config("generate")
    assert default_cfg.provider == gen_cfg.provider
    assert default_cfg.model == gen_cfg.model


# ---------------------------------------------------------------------------
# 环境变量解析
# ---------------------------------------------------------------------------
def test_config_from_env(monkeypatch):
    """LLMConfig.from_env 正确解析 REVIEW_LLM_* 环境变量。"""
    monkeypatch.setenv("REVIEW_LLM_PROVIDER", "openai")
    monkeypatch.setenv("REVIEW_LLM_MODEL", "gpt-4")
    monkeypatch.setenv("REVIEW_LLM_API_KEY", "sk-test")
    config = LLMConfig.from_env("REVIEW")
    assert config.provider == "openai"
    assert config.model == "gpt-4"
    assert config.api_key == "sk-test"


def test_config_from_env_missing_defaults_mock():
    """环境变量缺失时 from_env 默认 provider=mock。"""
    # 清除可能的环境变量（确保测试隔离）
    import os
    for key in ("GENERATE_LLM_PROVIDER", "GENERATE_LLM_MODEL", "GENERATE_LLM_API_KEY"):
        os.environ.pop(key, None)
    config = LLMConfig.from_env("GENERATE")
    assert config.provider == "mock"
    assert config.model == "default"
    assert config.api_key is None


def test_router_reads_env_on_init(monkeypatch):
    """LLMRouter 在 __init__ 时读 env，新实例反映最新环境变量。"""
    monkeypatch.setenv("REVIEW_LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("REVIEW_LLM_MODEL", "claude-3-opus")
    router = LLMRouter()
    rev = router.get_config("review")
    assert rev.provider == "anthropic"
    assert rev.model == "claude-3-opus"


# ---------------------------------------------------------------------------
# 统一调用入口
# ---------------------------------------------------------------------------
def test_call_llm_mock_returns_placeholder():
    """provider=mock 时 call_llm 返回占位字符串。"""
    # 默认环境（mock）
    result = call_llm("test prompt", node_type="review")
    assert isinstance(result, str)
    assert result  # 非空


def test_call_llm_unknown_node_uses_default():
    """未知 node_type 走 default 配置，不报错。"""
    result = call_llm("test prompt", node_type="nonexistent")
    assert isinstance(result, str)


def test_call_llm_mock_placeholder_by_node():
    """各节点 mock 占位串保持原值，现有单测语义不变。"""
    assert call_llm("p", node_type="title") == "Placeholder Title from LLM"
    assert call_llm("p", node_type="outline") == "Placeholder outline from LLM"
    assert call_llm("p", node_type="generate") == "Placeholder chapter content from LLM"
    assert call_llm("p", node_type="review") == "Mock LLM response"


def test_from_env_uses_minimax_outside_pytest(monkeypatch):
    """非 pytest 且有 MiniMax key 时走 MiniMax，不读死 mock。"""
    monkeypatch.delenv("GENERATE_LLM_PROVIDER", raising=False)
    monkeypatch.delenv("GENERATE_LLM_MODEL", raising=False)
    monkeypatch.delenv("GENERATE_LLM_API_KEY", raising=False)
    monkeypatch.delenv("ECONPAPER_LLM", raising=False)
    monkeypatch.setenv("MINIMAX_API_KEY", "sk-test-minimax")
    monkeypatch.setenv("MINIMAX_MODEL", "MiniMax-M3")
    monkeypatch.setenv("MINIMAX_OPENAI_BASE_URL", "https://api.minimaxi.com/v1")
    monkeypatch.setattr("llm.router.in_pytest", lambda: False)
    config = LLMConfig.from_env("GENERATE")
    assert config.provider == "minimax"
    assert config.model == "MiniMax-M3"
    assert config.api_key == "sk-test-minimax"
    assert config.base_url == "https://api.minimaxi.com/v1"


def test_econpaper_llm_mock_wins_outside_pytest(monkeypatch):
    monkeypatch.setenv("ECONPAPER_LLM", "mock")
    monkeypatch.setenv("MINIMAX_API_KEY", "sk-test-minimax")
    monkeypatch.setattr("llm.router.in_pytest", lambda: False)
    config = LLMConfig.from_env("GENERATE")
    assert config.provider == "mock"


def test_router_reload_rereads_env(monkeypatch):
    router = LLMRouter()
    assert router.get_config("generate").provider == "mock"
    monkeypatch.setenv("GENERATE_LLM_PROVIDER", "minimax")
    monkeypatch.setenv("GENERATE_LLM_MODEL", "MiniMax-M3")
    monkeypatch.setenv("GENERATE_LLM_API_KEY", "sk-reload")
    router.reload()
    gen = router.get_config("generate")
    assert gen.provider == "minimax"
    assert gen.model == "MiniMax-M3"
    assert gen.api_key == "sk-reload"
