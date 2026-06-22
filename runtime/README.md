# Runtime Package

Layer 2 的 pipeline engine — 读 `workflows/registry.json`，按 10 步顺序执行，处理 human checkpoint，持久化状态。

## 文件

| 文件 | 作用 |
|---|---|
| `pipeline.py` | 核心引擎：读 registry → 执行 step → human checkpoint → 状态持久化 |
| `state.py` | Pipeline state 读写（`artifacts/pipeline_state.json`） |
| `checkpoints.py` | Human checkpoint 的 prompt + 确认逻辑 |
| `cli.py` | 一条命令入口 |

## 用法

```bash
PYTHONPATH=. python3 runtime/cli.py --mode dry-run    # 预演：看哪些 step 会跑
PYTHONPATH=. python3 runtime/cli.py --mode execute     # 执行：跳过产物已存在的 step
PYTHONPATH=. python3 runtime/cli.py --mode execute --step 05_causal_analysis  # 从指定 step 开始
PYTHONPATH=. python3 runtime/cli.py --mode resume      # 从上次停止的 step 继续
PYTHONPATH=. python3 runtime/cli.py --status           # 查看当前状态
```

## 设计原则

- **产物优先**：每个 step 的 required_outputs 存在磁盘上 → skip（幂等）
- **Human checkpoint 不可绕过**：遇到必须人确认的判断，停下来等 `yes`
- **失败即停**：gate 或 step 失败 → blocked → 写 report → 退出
- **状态可恢复**：`pipeline_state.json` 记录当前 step + 历史，支持 resume

## 与现有脚本的关系

不替换 `scripts/28_agent_orchestrator.py`，而是站在它上面：

```
cli.py (runtime/)
    → pipeline.py (step 调度 + checkpoint)
        → 28_agent_orchestrator.py (policy-gated adapter 执行)
            → scripts/25-33 (具体校验/脚本)
```

runtime 管 **顺序和 checkpoint**，orchestrator 管 **policy 和安全**。
