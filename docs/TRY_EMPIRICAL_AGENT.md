# 试用：Empirical Agent（书级 harness）

产品是 **Continuous Empirical Loop**，不是逐步门禁员。  
Agent = Model + Harness（上下文 + 工具 + 约束 + 验证 + 纠正）。

## 命令

```bash
cd /Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板
set -a; source .env.local; set +a
export MINIMAX_CN_API_KEY="${MINIMAX_API_KEY}"

# 优先：Pi runtime
PYTHONPATH=. python3 -m Product.cli agent-pi "对 parent_education_wage 执行完整实证 loop，产出论文包"

# Fallback
PYTHONPATH=. python3 -m Product.cli agent "..."
```

## 期望行为

1. 读工作区与当前数据/设计状态。  
2. 调工具跑数据门 / 估计 / 写稿 / 审计 / 复现（或调用 full-pipeline）。  
3. 质量门红灯 → 纠正动作，不是只打印「请人工」。  
4. 轨迹落 `state/runs/` 与 trace log。  
5. 最终指向可打开稿 + 复现路径。

## 身份

- `SOUL.md`  
- `docs/PRODUCT.md`  
- 能力标尺：`/Users/mahaoxuan/Desktop/AI产品经理/ai-agent-book`

## 全流程无 Agent 编排

不经过对话也可：

```bash
PYTHONPATH=. python3 -m Product.cli full-pipeline --llm --model MiniMax-M3
```

见 `docs/TRY_FULL_PIPELINE.md`。
