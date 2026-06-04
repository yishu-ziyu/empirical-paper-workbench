# LLM 接入说明：MiniMax Token Plan

## 真实模型

**统一标准**：`MiniMax-M3`（Anthropic-compatible 协议）

**回退链**（按优先级）：`MiniMax-M3` → `MiniMax-M2.7` → `MiniMax-M2.5`

**端点**：`https://api.minimaxi.com/anthropic/v1/messages`
**Headers**：`x-api-key: ${MINIMAX_TOKEN_PLAN_KEY}`, `anthropic-version: 2023-06-01`

## 接入步骤

1. **获取 Token Plan Key**（不是按量 API Key，type 不同会 401）
2. **写入 `.env.local`**（**不要**进 git）：
   ```bash
   echo "MINIMAX_TOKEN_PLAN_KEY=eyJ..." > .env.local
   chmod 600 .env.local
   ```
3. **确认 `.gitignore` 排除 `.env.local`**
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

## 测试 vs 生产

- **测试**：`tests/conftest.py` 的 autouse `mock_llm` fixture 会 patch 每个 wrapper 命名空间里的 `chat_completion`，不需真实 key
- **生产 / 本地端到端**：必须 `.env.local` 里配真实 `MINIMAX_TOKEN_PLAN_KEY`，否则会抛 `LLMError(missing_api_key)`

## 来源

参考组件库（你电脑里）：
- `~/Desktop/AI组件工作流库/components/minimax-token-plan-real-service/WORKFLOW.md`

> 这是项目间共享的接入规范，新项目接入 MiniMax Token Plan 时直接参考这个 WORKFLOW.md。**注意：M3 升级时间 2026-06-04，AI 组件工作流里的早期 doc 可能写的是 M2.7，要更新。**
