"""ADR-0008: 多 LLM 路由器。

配置优先级：
1. ECONPAPER_LLM=mock → 全 mock（最高优先级：所有角色一律 mock，
   不读取真实 SSOT/凭据，reload 与子进程同样生效）
2. GENERATE_LLM_* / REVIEW_LLM_* 显式环境变量
3. pytest → mock（单测不打网、不读 SSOT）
4. 本机 SSOT 有 MiniMax key → MiniMax
5. mock（无 key）
"""
import os
from typing import Optional, Dict

from .ssot import in_pytest, load_ssot

MINIMAX_BASE_URL = "https://api.minimaxi.com/v1"
MINIMAX_MODEL = "MiniMax-M3"


def _env(*names: str) -> Optional[str]:
    for name in names:
        value = (os.environ.get(name) or "").strip()
        if value:
            return value
    return None


class LLMConfig:
    """单个 LLM 配置。"""

    def __init__(
        self,
        provider: str,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    @classmethod
    def from_env(cls, prefix: str) -> "LLMConfig":
        """prefix=GENERATE → GENERATE_LLM_PROVIDER / MODEL / API_KEY / BASE_URL。"""
        if os.environ.get("ECONPAPER_LLM") == "mock":
            # 显式 mock 是最高优先级：直接返回，不读取真实 SSOT/凭据。
            return cls(provider="mock", model="default")
        if in_pytest() and not _env(f"{prefix}_LLM_PROVIDER"):
            # 单测默认 mock：不读 SSOT，不打网。
            return cls(provider="mock", model="default")
        load_ssot()
        explicit = _env(f"{prefix}_LLM_PROVIDER")
        if explicit:
            provider = explicit
        elif _env("MINIMAX_API_KEY", "MINIMAX_TOKEN_PLAN_KEY"):
            provider = "minimax"
        else:
            provider = "mock"

        if provider == "mock":
            return cls(provider="mock", model="default")

        model = _env(f"{prefix}_LLM_MODEL")
        if not model or model == "default":
            model = _env("MINIMAX_MODEL") or MINIMAX_MODEL
        api_key = _env(
            f"{prefix}_LLM_API_KEY",
            "MINIMAX_API_KEY",
            "MINIMAX_TOKEN_PLAN_KEY",
            "OPENAI_API_KEY",
        )
        base_url = _env(
            f"{prefix}_LLM_BASE_URL",
            "MINIMAX_OPENAI_BASE_URL",
        ) or MINIMAX_BASE_URL
        if provider == "openai" and not _env(f"{prefix}_LLM_BASE_URL"):
            if _env("OPENAI_API_KEY") and not _env("MINIMAX_API_KEY", "MINIMAX_TOKEN_PLAN_KEY"):
                base_url = _env("OPENAI_BASE_URL") or "https://api.openai.com/v1"
                api_key = _env("OPENAI_API_KEY")
        return cls(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
        )


class LLMRouter:
    """按节点类型分发 LLM 配置。"""

    def __init__(self) -> None:
        self._configs: Dict[str, LLMConfig] = {}
        self._load_from_env()

    def _load_from_env(self) -> None:
        self._configs["generate"] = LLMConfig.from_env("GENERATE")
        self._configs["review"] = LLMConfig.from_env("REVIEW")
        self._configs["title"] = self._configs["generate"]
        self._configs["outline"] = self._configs["generate"]
        self._configs["desk"] = LLMConfig.from_env("DESK")
        if self._configs["desk"].provider == "mock":
            self._configs["desk"] = self._configs["generate"]
        self._configs["default"] = self._configs["generate"]
        self.assert_mock_isolation()

    def assert_mock_isolation(self) -> None:
        """启动配置断言：显式 mock 下任何角色都不得解析出真实供应商/凭据。"""
        if os.environ.get("ECONPAPER_LLM") != "mock":
            return
        for role, config in self._configs.items():
            if config.provider != "mock" or config.api_key:
                raise RuntimeError(
                    "ECONPAPER_LLM=mock 但 LLM 角色解析为非 mock 配置: " + role
                )

    def reload(self) -> None:
        """Re-read env. Backend startup calls this after process env is ready."""
        self._load_from_env()

    def get_config(self, node_type: str) -> LLMConfig:
        return self._configs.get(node_type, self._configs["default"])

    def is_multi_llm(self) -> bool:
        gen = self._configs["generate"]
        rev = self._configs["review"]
        return gen.provider != rev.provider or gen.model != rev.model


router = LLMRouter()
