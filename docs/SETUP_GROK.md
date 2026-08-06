# Grok 4.5 接入（产品默认 / 开发测试强制）

## 规则

- **产品默认 LLM** = `provider_id=grok` · `model=grok-4.5`
- **本仓库开发与自动化测试中的真实 LLM 调用** 一律用 Grok 4.5，不要默默退回 MiniMax（除非显式 `--provider minimax` 做对照）
- MiniMax / StepFun 等保留为 fallback，不是主身份

## 鉴权（二选一）

1. **Grok CLI 会话（推荐本机）**  
   - 已 `grok login`  
   - 自动读 `~/.grok/auth.json` 的 session key  
   - 自动带 `x-grok-client-version`（来自 `~/.grok/version.json`）  
   - base：`https://cli-chat-proxy.grok.com/v1`

2. **显式 Key**  
   - `GROK_API_KEY` 或 `XAI_API_KEY`  
   - 官方 API 可用 `provider_id=xai` + `https://api.x.ai/v1`

## 环境变量（`.env.local`）

```bash
EMPIRICAL_LLM_PROVIDER=grok
EMPIRICAL_LLM_MODEL=grok-4.5
GROK_BASE_URL=https://cli-chat-proxy.grok.com/v1
GROK_MODEL=grok-4.5
# 可选：不设则用 ~/.grok/auth.json
# GROK_API_KEY=
# XAI_API_KEY=
```

## 冒烟

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板
set -a; source .env.local; set +a
PYTHONPATH=. python3 - <<'PY'
from Product.backend.llm_client import chat_completion
text, usage = chat_completion(
    [{"role":"user","content":"Reply with exactly GROK45_OK"}],
    provider_id="grok",
    model="grok-4.5",
    temperature=0,
)
print(text, usage)
PY
```

## CLI 默认

```bash
PYTHONPATH=. python3 -m Product.cli continuous-loop --llm --max-rounds 3
# 默认 --provider grok --model grok-4.5

PYTHONPATH=. python3 -m Product.cli agent "..."
# 默认 provider=grok model=grok-4.5
```

## 实现位置

- `Product/backend/llm_client.py`：`PROVIDER_PRESETS["grok"]` / `["xai"]` · `DEFAULT_PROVIDER=grok`
- 外环：`runtime/continuous_loop.py`
- 内环：`runtime/full_pipeline.py`
