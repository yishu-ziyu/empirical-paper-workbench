# econpaper Project Instructions

econpaper 是本仓库唯一产品。开发验证以真实的上传数据 → 研究设定 → 识别与稳健 → 分章评审 → 导出路径为准。

## Commands

```bash
make test
make verify
```

`make verify` 需要前后端服务已运行；未运行时要明确报告，不用它替代可执行的静态或测试检查。

## Codex 长任务上下文与 Skill 演进

这套协议本身不要求创建独立分支；沿用当前 checkout，只有用户明确要求时才切换或新建分支。

1. 每个新会话在规划前先读 `runtime/STATE.md`。若用户意图命中其中的活动任务，再读对应的 `runtime/tasks/<task-id>.md`；不要把聊天记忆当恢复依据。新长任务按 `runtime/tasks/TEMPLATE.md` 建独立状态文件并登记，不能覆盖其他会话的任务。
2. 每个里程碑结束、上下文压缩、交接或退出前，更新任务文件及索引中的状态、更新时间和下一步。只保存恢复所需的事实、改动、失败路径和证据位置。
3. 完整 run 工件仍以 `runs/`、`backend/runs/` 及对应 session/run ID 为准。任务状态不复制用户数据集、论文正文或大段日志。
4. 重要任务结束后，按 `agent-learning/raw/TEMPLATE.md` 新建去敏运行记录，并把索引状态改为 `complete`。单次任务可以给 `agent-learning/wiki.md` 增加证据，不得据此直接扩大本文件或创建 Skill。
5. Skill 变更必须作为单独任务：至少比较 4 份相关运行记录，兼看成功与失败；一次只改一个 Skill；运行固定验证案例与 `make test`，涉及运行链路时再跑 `make verify` 和真实用户路径。只有主指标提高且研究可追溯性、人工审批和恢复门槛不退化才接受，否则回滚并记录拒绝原因。
6. 通过验证的 Skill 才进入 `.agents/skills/<skill-name>/SKILL.md`。更换模型、数据类型、计量方法、工具或交互预算后重新验证。

状态与学习记录不得保存凭据、用户原始数据、未公开论文正文、私人对话或隐藏推理；只记录去敏事实、ID 和证据位置。
