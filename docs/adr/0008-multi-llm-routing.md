# ADR 0008 — 多 LLM 路由（评审 LLM 与生成 LLM 使用不同模型）

- **Status:** Accepted
- **Date:** 2026-07-28
- **Supersedes:** —
- **Superseded by:** —
- **Related:** ADR 0003（Agent Contract / NodeResult 协议）、ADR 0004（Sakana 评审与文献节点）

## 1. Context

### 1.1 问题：同模型自评偏差

当前所有节点共用同一个 LLM 调用通道：

| 节点 | 模块级 LLM 函数 | 实际指向 |
| --- | --- | --- |
| `generate_chapter` | `nodes.generate_chapter.call_llm` | 同一 LLM（`LLM_PROVIDER` / `LLM_MODEL`） |
| `generate_title` | `nodes.generate_title.call_llm` | 同一 LLM |
| `generate_outline` | `nodes.generate_outline.call_llm` | 同一 LLM |
| `review_chapter` | `nodes.review_chapter.call_review_llm` | 同一 LLM（Stage 3 默认 `mock_review_llm`） |

Sakana AI Scientist 报告 §3.4 指出：**同模型自评存在系统性偏差**——生成模型倾向于给自己产出的内容打高分，对自身盲区（如内生性、识别策略）缺乏批判力。用不同模型评审能显著提高评审质量与迭代收敛性（Sakana 实验中跨模型评审的评分方差比自评低 ~30%）。

ADR 0004 §8 Non-Goal 明确："评审节点复用 `call_llm`，与 `generate_chapter` 同一 LLM 调用通道"。本 ADR 取消该 Non-Goal，支持评审 LLM 与生成 LLM 配置分离。

### 1.2 现有 monkeypatch 模式不能破坏

`generate_chapter.call_llm` / `review_chapter.call_review_llm` 都是模块级函数，测试通过 `monkeypatch.setattr("nodes.xxx.call_llm", ...)` 替换。这一模式（ADR 0003 Stage C 的 `mock_llm_for` fixture）被 27 个测试文件复用，是测试侧的核心接缝。多 LLM 路由必须保持该模式不变。

### 1.3 配置缺失时的降级要求

生产环境可能只配了一个 LLM（如只有 OpenAI key），或两个都没配（开发/CI 用 mock）。路由器在配置缺失时必须降级为单 LLM 或全 mock，不能抛异常阻断 graph。

### 1.4 与 ADR 0004 mock 评审的关系

ADR 0004 Stage 3 的 `mock_review_llm` 是确定性的规则评分器（不调真实 LLM），用于开发/测试。本 ADR 不替换 `mock_review_llm`，而是在 `call_review_llm` 内部增加路由层：`provider == "mock"` 时仍调 `mock_review_llm`，`provider == "anthropic"` / `"openai"` 时调真实 LLM。这样 ADR 0004 的测试与 mock baseline 完全不受影响。

## 2. Goals And Non-Goals

| Type | Statement | Evidence | Owner |
| --- | --- | --- | --- |
| Goal | 新建 `LLMRouter`，按节点类型（generate / review / title / outline）分发到不同 LLM 配置 | 新增 `agent/llm/router.py`，模块级单例 `router` | agent owner |
| Goal | 通过环境变量配置不同节点的 LLM（`GENERATE_LLM_*` / `REVIEW_LLM_*`） | 新增 `backend/.env.example` 配置项 | agent owner |
| Goal | 向后兼容：未配置环境变量时所有节点用 mock，行为同现状 | `LLMConfig.from_env` 默认 `provider="mock"` | agent owner |
| Goal | `review_chapter.call_review_llm` 接入路由器，支持评审用不同 LLM | `call_review_llm` 读 `router.get_config("review")` | agent owner |
| Goal | 路由器不破坏现有 `call_llm` / `call_review_llm` 的 monkeypatch 模式 | 现有测试 0 改动通过 | test owner |
| Non-Goal | 不引入真实 LLM SDK 依赖（langchain-anthropic / openai） | 生产环境通过 monkeypatch 注入真实调用，保持轻量 | — |
| Non-Goal | 不强制启用多 LLM | `is_multi_llm()` 返回 False 时行为同现状 | — |
| Goal | 统一 LLM 调用入口 `llm.call_llm`，为 Stage 3 generate_chapter 接入做准备 | 新增 `agent/llm/call_llm.py` | agent owner |
| Non-Goal | 不在 Stage 1 修改 `generate_chapter.call_llm` | generate_chapter 接入留 Stage 3，降低本 ADR blast radius | — |
| Non-Goal | 不改 graph 拓扑、不改 `EconPaperState` 字段 | 路由器是 LLM 调用层的变化，不影响 graph 编排 | — |

## 3. Bounded Contexts

| Context | Responsibility | Model/Language | Interfaces | Owned Data |
| --- | --- | --- | --- | --- |
| LLM Routing | 按节点类型分发 LLM 配置 | Python（`LLMConfig` / `LLMRouter`） | `router.get_config(node_type) -> LLMConfig`、`router.is_multi_llm() -> bool` | `LLMConfig`（provider / model / api_key） |
| LLM Call Entry | 统一 LLM 调用入口（生产/测试接缝） | Python（`call_llm` 函数） | `call_llm(prompt, node_type) -> str` | — |
| Node — Review | 章节评审节点（已存在，本 ADR 仅改 `call_review_llm` 内部） | TypedDict（`ReviewOutput`） | `call_review_llm(...)` 读 router | — |
| Config — Env | 环境变量驱动的 LLM 配置 | `.env` / 环境变量 | `GENERATE_LLM_PROVIDER` / `REVIEW_LLM_PROVIDER` 等 | env vars |

| Context | Upstream | Downstream | Translation Surface |
| --- | --- | --- | --- |
| LLM Routing | 环境变量（配置源） | LLM Call Entry / Node — Review | `LLMConfig.from_env(prefix)` 把 env 字符串转 `LLMConfig` |
| LLM Call Entry | LLM Routing（读 config） | 真实 LLM / mock（被 monkeypatch 替换） | `call_llm` 根据 `config.provider` 分发 |
| Node — Review | LLM Routing（读 review config） | mock_review_llm / 真实 LLM | `call_review_llm` 内部 if/else 分发 |
| Config — Env | `.env` 文件 / 进程环境 | LLM Routing | env → `LLMConfig` 字段 |

## 4. System Map

| Element | Data Flow | Dependency | Trust Boundary | Responsibility |
| --- | --- | --- | --- | --- |
| `backend/.env` | → 进程环境变量 | 无 | internal | 声明 `GENERATE_LLM_*` / `REVIEW_LLM_*` |
| `LLMRouter` | ← `os.environ` → `LLMConfig` dict | `os` 标准库 | internal | 启动时读 env，按 node_type 分发 config |
| `LLMConfig` | ← `LLMRouter.get_config` | 无 | internal | 持有单个 LLM 的 provider/model/api_key |
| `llm.call_llm` | ← `router.get_config(node_type)` | `llm.router` | internal | 统一入口，根据 provider 分发（mock 占位 / 真实由 monkeypatch 注入） |
| `review_chapter.call_review_llm` | ← `router.get_config("review")` | `llm.router`、`nodes.review_sources.mock_review` | internal | provider=mock 时调 mock_review_llm；其他 provider 暂仍调 mock（占位） |
| 测试 `monkeypatch.setattr` | → 替换 `call_review_llm` / `call_llm` | pytest monkeypatch | test | 测试侧接缝，不受 router 影响 |

**关键数据流**：

```
┌─────────────┐   env vars    ┌──────────────┐  get_config("review")   ┌──────────────────────┐
│ backend/.env │ ────────────▶ │  LLMRouter   │ ──────────────────────▶ │  call_review_llm     │
│ (GENERATE_*  │               │  (单例 router)│                         │  (review_chapter.py) │
│  REVIEW_*)   │               └──────────────┘  get_config("generate") └──────────────────────┘
└─────────────┘                       │                                   │ provider == "mock"?
                                      │ get_config(node_type)             │  Y → mock_review_llm
                                      ▼                                   │  N → 占位（仍 mock）
                              ┌──────────────────┐                       └──────────────────────┘
                              │  llm.call_llm     │
                              │  (统一入口)        │
                              └──────────────────┘
                                      │
                                      │ 测试通过 monkeypatch.setattr 替换
                                      ▼
                              ┌──────────────────┐
                              │  mock / 真实 LLM  │
                              └──────────────────┘
```

## 5. Interaction Style

| Interaction | Style | Why This Style | Failure Behavior | Backward Compatibility |
| --- | --- | --- | --- | --- |
| 环境变量 → `LLMRouter` | 启动时一次性读取（`__init__`） | 配置不应在每次调用时重复读 env；路由器是模块级单例 | 环境变量缺失时 `from_env` 返回默认 `provider="mock"`，不抛异常 | 新增环境变量不影响现有 `LLM_PROVIDER` / `LLM_MODEL`（独立前缀） |
| `call_review_llm` → `router.get_config` | 同步函数调用（每次评审读一次 config） | 路由器是内存对象，零 IO 开销 | router 未初始化时返回 default config（mock） | `call_review_llm` 签名不变，测试 monkeypatch 模式不变 |
| `call_review_llm` → `mock_review_llm` | 同步函数调用 | 开发/测试环境确定性评分 | mock 按规则评分，不抛异常 | ADR 0004 的 mock baseline 完全保留 |
| `llm.call_llm` → 真实 LLM | 同步函数调用（占位） | Stage 1 不接真实 SDK；生产通过 monkeypatch 注入 | provider 非 mock 但未 monkeypatch 时返回占位字符串 | — |
| 测试 → `monkeypatch.setattr` | pytest monkeypatch | 现有测试接缝，不改 | — | 现有 27 个测试文件 0 改动 |

**配置优先级矩阵**：

| 配置来源 | 优先级 | 说明 |
| --- | --- | --- |
| 环境变量 `GENERATE_LLM_*` / `REVIEW_LLM_*` | 1（最高） | 显式配置，覆盖默认 |
| 默认 `provider="mock"` | 2（兜底） | 环境变量缺失时 |
| 测试 `monkeypatch.setattr` | 0（覆盖一切） | 测试侧直接替换模块级函数，绕过 router |

## 6. Risks

| Risk | Likelihood | Impact | Mitigation | Responsibility Path | Evidence | Decision Record |
| --- | --- | --- | --- | --- | --- | --- |
| 路由器单例在测试间状态泄漏（一个测试 setenv 影响下一个） | 中 | 中 | 测试用 `monkeypatch.setenv` 自动还原；`LLMRouter` 在 `__init__` 读 env，每个测试 new 新实例 | test owner | pytest monkeypatch 隔离 | 本 ADR §7 |
| `call_review_llm` 内部 import `llm.router` 导致循环依赖 | 低 | 高 | `llm.router` 不 import 任何 `nodes.*`；`call_review_llm` 用函数内延迟 import | agent owner | `agent/llm/` 无节点依赖 | 本 ADR §8 Decision B |
| `from llm.router import router` 在生产环境失败（sys.path 未含 agent/） | 低 | 高 | `backend/main.py` 已 `sys.path.append(agent/)`（ADR 0003 §Exceptions 记录）；`conftest.py` 测试环境已加 | agent owner | backend/main.py:11-13 | 本 ADR §8 Decision A |
| 环境变量配错（如 `REVIEW_LLM_PROVIDER=anthropic` 但无 API key）导致评审失败 | 中 | 中 | Stage 1 不接真实 SDK，provider 非 mock 时仍降级调 mock（占位）；Stage 3 接真实 SDK 时加 key 存在性校验 | agent owner | `call_review_llm` 占位逻辑 | 本 ADR §9 Stage 3 |
| 模块级单例 `router = LLMRouter()` 在 import 时读 env，CI 环境变量未设置导致全 mock | 低 | 低 | 这正是期望行为（CI 用 mock）；生产环境 `.env` 加载后再 import | agent owner | `LLMConfig.from_env` 默认 mock | 本 ADR §8 Decision C |
| 多 LLM 启用后评审成本翻倍（生成 + 评审各一次 LLM 调用） | 中 | 低 | 1. mock 模式零成本；2. 生产环境可配 `REVIEW_LLM_MODEL` 用便宜模型（如 gpt-4o-mini 评审、gpt-4o 生成） | agent owner | Sakana 报告 §3.4 成本分析 | 本 ADR §8 Decision D |

## 7. Fitness Functions

| Invariant | Metric Or Rule | Threshold | Measurement Source | Cadence | Failure Response | Local Check Path |
| --- | --- | --- | --- | --- | --- | --- |
| 路由器向后兼容 | 未设环境变量时 `router.get_config("generate").provider == "mock"` 且 `is_multi_llm() == False` | 100% | `agent/tests/test_llm_router.py::test_default_config_is_mock` | 每次 commit | 阻止合并 | `make verify` |
| 多 LLM 检测正确 | `GENERATE_LLM_PROVIDER != REVIEW_LLM_PROVIDER` 时 `is_multi_llm() == True` | 100% | `agent/tests/test_llm_router.py::test_multi_llm_detection` | 每次 commit | 阻止合并 | `make verify` |
| 未知节点降级 | `router.get_config("unknown_node")` 返回 default config（非 None） | 100% | `agent/tests/test_llm_router.py::test_unknown_node_uses_default` | 每次 commit | 阻止合并 | `make verify` |
| 环境变量解析 | `LLMConfig.from_env("REVIEW")` 正确读 `REVIEW_LLM_PROVIDER/MODEL/API_KEY` | 100% | `agent/tests/test_llm_router.py::test_config_from_env` | 每次 commit | 阻止合并 | `make verify` |
| monkeypatch 模式不破坏 | 现有 `test_review_chapter.py` 0 改动通过 | 100% | `agent/tests/test_review_chapter.py` 全绿 | 每次 commit | 阻止合并 | `make verify` |
| 路由器不 import 节点 | `agent/llm/` 下文件 0 处 `from nodes` / `import nodes` | 0 命中 | `grep -rn "from nodes\|import nodes" agent/llm/` | 每次 commit | 阻止合并 | `make verify` |
| 全量测试不回归 | `agent/tests/` 全绿 | 100% | `python -m pytest tests/ -q` | 每次 commit | 阻止合并 | `make verify` |

## 8. Decision Table

| Decision | Default | Rejected Alternatives | Exception Conditions |
| --- | --- | --- | --- |
| **A. 模块级单例 `router = LLMRouter()`**：import 时读 env，全局共享 | ✅ 采纳 | 1. 每次调用 new 新 `LLMRouter`（重复读 env，开销高）；2. 依赖注入 `router` 参数透传（侵入所有节点签名，破坏 monkeypatch 模式）；3. 把 config 存 `EconPaperState`（state 是 graph 编排数据，非 LLM 调用配置，职责混淆） | 测试用 `LLMRouter()` new 新实例，避免单例污染 |
| **B. `call_review_llm` 函数内延迟 import `llm.router`**：避免循环依赖与 import 时副作用 | ✅ 采纳 | 1. 模块顶部 import（`nodes.review_chapter` import 时触发 `llm.router` 读 env，若 env 未就绪可能读到空值）；2. 把 router 注入为模块级变量（测试 monkeypatch 困难） | — |
| **C. 环境变量前缀 `GENERATE_LLM_*` / `REVIEW_LLM_*`**：按节点角色分前缀 | ✅ 采纳 | 1. 单一 `LLM_PROVIDER` + `REVIEW_LLM_PROVIDER` 覆盖（语义不对称）；2. JSON 配置文件（过重，env 已是 12-factor 标准）；3. `EconPaperState` 字段配置（state 不应持 LLM 配置） | 其他节点（title/outline）暂用 generate 配置，未来可加 `TITLE_LLM_*` 前缀 |
| **D. provider=mock 时调 `mock_review_llm`，非 mock 时占位仍调 mock**：Stage 1 不接真实 SDK | ✅ 采纳 | 1. Stage 1 直接接 langchain-anthropic（引入重依赖、API key 需求、CI 不稳定）；2. provider 非 mock 时抛 NotImplementedError（破坏 graph 运行） | Stage 3 接真实 SDK 时替换占位为真实调用 |
| **E. `LLMConfig.from_env(prefix)` 默认 `provider="mock"`**：配置缺失即 mock | ✅ 采纳 | 1. 默认 `provider="openai"`（无 key 时崩溃）；2. 默认抛异常（违背"降级"原则） | 生产 `.env` 显式配置后覆盖默认 |
| **F. `is_multi_llm()` 比较 provider + model**：两者任一不同即视为多 LLM | ✅ 采纳 | 1. 只比较 provider（同 provider 不同 model 也算多 LLM，如 gpt-4o vs gpt-4o-mini）；2. 比较 api_key（同 model 不同 key 不算多 LLM，是同模型） | — |

## 9. Stage 切分

### Stage 1 — LLMRouter + 配置 + review_chapter 接入（本 ADR 实施范围）

1. 新建 `agent/llm/__init__.py`（空，标记为 Python 包）；
2. 新建 `agent/llm/router.py`，定义 `LLMConfig`（provider/model/api_key + `from_env` 类方法）与 `LLMRouter`（`_load_from_env` / `get_config` / `is_multi_llm`），模块级单例 `router = LLMRouter()`；
3. 新建 `agent/llm/call_llm.py`，定义统一入口 `call_llm(prompt, node_type="default") -> str`，根据 `router.get_config(node_type).provider` 分发（mock 返回占位字符串；非 mock 占位返回 `[provider/model] Placeholder response`）；
4. 修改 `agent/nodes/review_chapter.py` 的 `call_review_llm`：函数内延迟 import `from llm.router import router`，读 `router.get_config("review")`，`provider == "mock"` 时调 `mock_review_llm`，非 mock 时暂仍调 `mock_review_llm`（占位，Stage 3 替换）；
5. 新增 `agent/tests/test_llm_router.py`：覆盖默认 mock、多 LLM 检测、同配置非多 LLM、未知节点降级、env 解析 5 个用例；
6. 更新 `backend/.env.example`：新增 `GENERATE_LLM_PROVIDER/MODEL/API_KEY` 与 `REVIEW_LLM_PROVIDER/MODEL/API_KEY` 6 个配置项；
7. 跑 `python -m pytest tests/test_llm_router.py tests/test_review_chapter.py -x -q` + 全量 `python -m pytest tests/ -x -q`，全绿。

**Stage 1 验收**：
- 未设环境变量时 `router.is_multi_llm() == False`，所有节点用 mock，行为同现状；
- `test_review_chapter.py` 0 改动通过（monkeypatch 模式不破坏）；
- `GENERATE_LLM_PROVIDER=anthropic` + `REVIEW_LLM_PROVIDER=openai` 时 `is_multi_llm() == True`；
- `call_review_llm` 在 `REVIEW_LLM_PROVIDER=anthropic` 时仍调 `mock_review_llm`（占位），不崩溃。

### Stage 2 — review_chapter 接真实 LLM（待后续）

1. `call_review_llm` 在 `provider == "anthropic"` 时调 langchain-anthropic，`provider == "openai"` 时调 langchain-openai；
2. 新增 `agent/llm/providers/anthropic.py` / `openai.py`，封装真实 LLM 调用；
3. 加 API key 存在性校验：key 缺失时降级为 mock 并记录 warning；
4. 新增 `agent/tests/test_review_chapter_real_llm.py`（mock HTTP，不真发请求）；
5. 跑 `make verify`，全绿。

**Stage 2 验收**：`REVIEW_LLM_PROVIDER=anthropic` + `REVIEW_LLM_API_KEY=sk-...` 时 `call_review_llm` 调真实 Claude API；key 缺失时降级 mock。

### Stage 3 — generate_chapter / generate_title / generate_outline 接入路由器（待后续）

1. `generate_chapter.call_llm` 改为读 `router.get_config("generate")`；
2. `generate_title.call_llm` / `generate_outline.call_llm` 同步接入；
3. 验证 `mock_llm_for` fixture 仍能 monkeypatch（保持测试接缝）；
4. 跑 `make verify`，全绿。

**Stage 3 验收**：`GENERATE_LLM_PROVIDER=anthropic` + `REVIEW_LLM_PROVIDER=openai` 时，生成用 Claude、评审用 GPT-4，端到端跑通。

## 10. 配置项

新增环境变量（`backend/.env.example`）：

```dotenv
# ADR-0008: 多 LLM 路由
# 生成节点（generate_chapter / generate_title / generate_outline）
GENERATE_LLM_PROVIDER=mock          # mock | anthropic | openai
GENERATE_LLM_MODEL=default
GENERATE_LLM_API_KEY=

# 评审节点（review_chapter）
REVIEW_LLM_PROVIDER=mock            # mock | anthropic | openai
REVIEW_LLM_MODEL=default
REVIEW_LLM_API_KEY=
```

**配置矩阵**：

| 配置 | `is_multi_llm()` | 行为 |
| --- | --- | --- |
| 全 mock（默认） | False | 所有节点用 mock，行为同 ADR 0004 |
| `GENERATE=anthropic` + `REVIEW=anthropic` 同 model | False | 所有节点用同一真实 LLM（单 LLM 模式） |
| `GENERATE=anthropic/claude-3-opus` + `REVIEW=openai/gpt-4` | True | 生成用 Claude，评审用 GPT-4（多 LLM 模式） |
| `GENERATE=mock` + `REVIEW=openai/gpt-4` | True | 生成用 mock，评审用真实 GPT-4（混合模式） |

## 11. 模块结构

```
agent/llm/
├── __init__.py          # 空包标记
├── router.py            # LLMConfig + LLMRouter + 模块级单例 router
├── call_llm.py          # 统一 LLM 调用入口 call_llm(prompt, node_type)
└── providers/           # Stage 2 新增
    ├── __init__.py
    ├── anthropic.py     # langchain-anthropic 封装
    └── openai.py        # langchain-openai 封装
```

## 12. 关键代码契约

```python
# agent/llm/router.py
class LLMConfig:
    """单个 LLM 配置。"""
    def __init__(self, provider: str, model: str, api_key: Optional[str] = None): ...
    
    @classmethod
    def from_env(cls, prefix: str) -> "LLMConfig":
        """prefix=GENERATE → GENERATE_LLM_PROVIDER/MODEL/API_KEY。默认 provider=mock。"""

class LLMRouter:
    """按节点类型分发 LLM 配置。"""
    def __init__(self): ...                          # 读 env 填 _configs
    def get_config(self, node_type: str) -> LLMConfig: ...   # 未知 node_type → default
    def is_multi_llm(self) -> bool: ...              # generate 与 review 配置不同时 True

router = LLMRouter()  # 模块级单例

# agent/llm/call_llm.py
def call_llm(prompt: str, node_type: str = "default") -> str:
    """统一入口。provider=mock 返回占位；非 mock 占位（Stage 2 接真实 SDK）。"""

# agent/nodes/review_chapter.py（修改 call_review_llm 内部）
def call_review_llm(chapter_content, rubric_template, research_direction, literature_entries) -> dict:
    """ADR-0008: 通过 LLMRouter 调用评审 LLM。"""
    from llm.router import router
    config = router.get_config("review")
    if config.provider == "mock":
        from nodes.review_sources.mock_review import mock_review_llm
        return mock_review_llm(...)
    # Stage 2 将在此分支调真实 LLM；当前占位仍调 mock
    from nodes.review_sources.mock_review import mock_review_llm
    return mock_review_llm(...)
```

## Exceptions

- **环境变量全缺失**：`LLMConfig.from_env` 返回 `provider="mock"`，`is_multi_llm() == False`，行为同 ADR 0004 现状。这是 CI / 开发环境的默认路径。
- **`provider` 值非法**（如 `REVIEW_LLM_PROVIDER=foobar`）：Stage 1 不校验，落入 `call_review_llm` 的非 mock 分支，仍调 `mock_review_llm`（占位），不崩溃。Stage 2 接真实 SDK 时加 provider 白名单校验。
- **`llm.router` import 失败**（sys.path 未含 agent/）：`call_review_llm` 内部延迟 import 会抛 `ImportError`。生产环境由 `backend/main.py` 的 `sys.path.append` 保证；测试环境由根 `conftest.py` 保证。
- **模块级单例 `router` 在测试间状态泄漏**：测试用 `LLMRouter()` new 新实例（不导入单例），或用 `monkeypatch.setenv` 自动还原环境变量。单例本身仅在 生产环境使用。

## Follow-Up Routes

- **ADR 0009**（待评估）：文献检索结果去重 / 引用图谱构建（继承自 ADR 0004 follow-up）。
- **Stage 2**（本 ADR）：`call_review_llm` 接真实 LLM SDK，加 provider 白名单与 API key 校验。
- **Stage 3**（本 ADR）：`generate_chapter` / `generate_title` / `generate_outline` 接入路由器，实现生成与评审用不同模型。
- **ADR 0010**（待评估）：LLM 调用成本监控与配额管理 —— 多 LLM 启用后按 provider 分别计费、限流。
