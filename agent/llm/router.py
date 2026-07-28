"""ADR-0008: 多 LLM 路由器。

支持不同节点用不同 LLM 配置，降低同模型自评偏差。

设计要点（见 docs/adr/0008-multi-llm-routing.md）：
- 配置优先级：环境变量（GENERATE_LLM_*、REVIEW_LLM_*）→ 默认 mock
- 模块级单例 `router` 在 import 时读 env，全局共享
- 未知 node_type 降级为 default（= generate）配置
- `is_multi_llm()` 比较 provider + model，两者任一不同即视为多 LLM
- 不 import 任何 nodes.*，避免循环依赖（Fitness Function）
"""
import os
from typing import Optional, Dict


class LLMConfig:
    """单个 LLM 配置。"""

    def __init__(self, provider: str, model: str, api_key: Optional[str] = None):
        self.provider = provider  # "anthropic" | "openai" | "mock"
        self.model = model
        self.api_key = api_key

    @classmethod
    def from_env(cls, prefix: str) -> "LLMConfig":
        """从环境变量读配置。

        prefix=GENERATE → GENERATE_LLM_PROVIDER, GENERATE_LLM_MODEL, GENERATE_LLM_API_KEY
        prefix=REVIEW   → REVIEW_LLM_PROVIDER,   REVIEW_LLM_MODEL,   REVIEW_LLM_API_KEY

        环境变量缺失时 provider 默认 "mock"（向后兼容，行为同 ADR 0004）。
        """
        return cls(
            provider=os.environ.get(f"{prefix}_LLM_PROVIDER", "mock"),
            model=os.environ.get(f"{prefix}_LLM_MODEL", "default"),
            api_key=os.environ.get(f"{prefix}_LLM_API_KEY"),
        )


class LLMRouter:
    """LLM 路由器，按节点类型分发到不同 LLM。

    配置优先级：
    1. 环境变量（GENERATE_LLM_*、REVIEW_LLM_*）
    2. 默认（所有节点用 mock）
    """

    def __init__(self):
        self._configs: Dict[str, LLMConfig] = {}
        self._load_from_env()

    def _load_from_env(self):
        """从环境变量加载配置。"""
        self._configs["generate"] = LLMConfig.from_env("GENERATE")
        self._configs["review"] = LLMConfig.from_env("REVIEW")
        # 其他节点默认用 generate 配置
        self._configs["default"] = self._configs["generate"]

    def get_config(self, node_type: str) -> LLMConfig:
        """获取节点的 LLM 配置。

        node_type: "generate" | "review" | "title" | "outline" | ...
        未知 node_type 返回 default 配置（= generate）。
        """
        return self._configs.get(node_type, self._configs["default"])

    def is_multi_llm(self) -> bool:
        """是否配置了多 LLM（generate 和 review 用不同配置）。

        provider 或 model 任一不同即视为多 LLM。
        """
        gen = self._configs["generate"]
        rev = self._configs["review"]
        return gen.provider != rev.provider or gen.model != rev.model


# 模块级单例（生产环境使用；测试用 LLMRouter() new 新实例避免状态泄漏）
router = LLMRouter()
