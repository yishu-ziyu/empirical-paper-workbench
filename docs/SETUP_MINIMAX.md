# LLM 接入说明：MiniMax Token Plan

## 真实模型

**统一标准**：`MiniMax-M3`（Anthropic-compatible 协议，**官方默认模型**，1M context window）

**回退链**（按优先级）：`MiniMax-M3` → `MiniMax-M2.7` → `MiniMax-M2.5`

**端点**：`https://api.minimax.io/anthropic/v1/messages`（**官方当前 host**）
**Headers**：`x-api-key: ${MINIMAX_API_KEY}`, `anthropic-version: 2023-06-01`

## 接入步骤

1. **获取 Token Plan Key**（注意是 Token Plan 类型，key 前缀是 `sk-cp-`，不是按量 API Key，否则 401）
2. **写入 `.env.local`**（**不要**进 git，已在 `.gitignore` 排除）：
   ```bash
   echo "MINIMAX_API_KEY=sk-cp-..." > .env.local
   chmod 600 .env.local
   ```
3. **确认 `.gitignore` 排除 `.env.local`**（已配置）
4. **重启后端**：`PYTHONPATH=. python -m uvicorn Product.app:app --port 8765`

## Provider preset 位置

`Product/backend/llm_client.py` → `PROVIDER_PRESETS["minimax"]`

所有 5 个 wrapper service 用统一调用：
```python
chat_completion(
    messages=[...],
    provider_id="minimax",
    model="MiniMax-M3",
    temperature=0.3,
)
```

Env var 解析顺序：
1. `chat_completion(api_key=...)` 显式参数
2. `MINIMAX_API_KEY`（新名，**推荐**）
3. `MINIMAX_TOKEN_PLAN_KEY`（旧名，向后兼容）

## 测试 vs 生产

- **测试**：`tests/conftest.py` 的 autouse `mock_llm` fixture 会 patch 每个 wrapper 命名空间里的 `chat_completion`，不需真实 key
- **生产 / 本地端到端**：必须 `.env.local` 里配真实 `MINIMAX_API_KEY`，否则会抛 `LLMError(missing_api_key)`

## 烟雾测试（验证 live 端点真通）

```bash
PYTHONPATH=. python -c "
from Product.backend.llm_client import chat_completion
text, usage = chat_completion(
    [{'role': 'user', 'content': '用一句话回答：1+1=?'}],
    provider_id='minimax', model='MiniMax-M3', temperature=0,
)
print('OK:', text, usage)
"
```

预期：HTTP 200，返回中文/英文简短回答，含 `input_tokens` / `output_tokens` usage。

## 来源 / 参考文献

- **官方文档**：[MiniMax Anthropic-compatible API](https://platform.minimax.io/docs/api-reference/text-anthropic-api)
- **跨项目接入规范**（你的电脑里）：
  - `~/Desktop/AI组件工作流库/components/minimax-token-plan-real-service/WORKFLOW.md`
  - `~/Desktop/ai组件工作流/Node-LLM-Provider-Bridge/`（已验证可工作的真实实现）
  - `~/Desktop/ai组件工作流/模型配置方法论.md` §11（多 Provider 配置方法论）

## 历史修正

| 日期 | 改动 | 原因 |
|---|---|---|
| 2026-06-04 | base_url `api.minimaxi.com` → `api.minimax.io` | 旧 host 已 stale；agentmemory CHANGELOG #289 同症状 |
| 2026-06-04 | env `MINIMAX_TOKEN_PLAN_KEY` → `MINIMAX_API_KEY` | 用户 `Node-LLM-Provider-Bridge` 与 agentmemory upstream 统一用 `MINIMAX_API_KEY` |
| 2026-06-04 | 默认模型 `M2.7` → `M3` | 用户指定统一 M3 标准；官方文档也以 M3 为默认 |
| 2026-06-04 | env 旧名保留为 backward-compat alias | 不破坏已部署环境的旧 key 名 |
