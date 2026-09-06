# econpaper Codex Runtime State Index

> 新会话先读本页，再按用户意图打开对应任务文件。这里是短索引，不承载完整运行历史。

| Task ID | State file | Status | Git context | Updated at | Next action |
|---|---|---|---|---|---|
| 20260906-card-research-semantics-consistency | `runtime/tasks/20260906-card-research-semantics-consistency.md` | complete | `review/workbench-v2` | 2026-09-06 | validator ACCEPT；浏览器 S5–S7 过；待 CI |
| 20260906-card-canonical-research-experience | `runtime/tasks/20260906-card-canonical-research-experience.md` | complete | `review/workbench-v2` | 2026-09-06 | validator ACCEPT；CI 待 Card commit |
| 20260902-run-cancellation | `runtime/tasks/20260902-run-cancellation.md` | complete | `chore/local-workspace-cleanup` | 2026-09-02 | Select the next full-stack issue |
| 20260902-upload-event-loop | `runtime/tasks/20260902-upload-event-loop.md` | complete | `chore/local-workspace-cleanup` | 2026-09-02 | Select the next full-stack issue |
| 20260902-durable-upload-recovery | `runtime/tasks/20260902-durable-upload-recovery.md` | complete | `chore/local-workspace-cleanup` | 2026-09-02 | Select the next full-stack issue |

## 启动与写回

1. `active` / `blocked` 且与用户意图匹配：读取对应任务文件后继续。
2. 多个任务都可能匹配：先确认，不覆盖任何状态。
3. 新长任务：复制 `runtime/tasks/TEMPLATE.md` 为 `runtime/tasks/YYYYMMDD-short-slug.md`，再登记一行。
4. 里程碑、压缩、交接或退出前：先更新任务文件，再更新本表。
5. 完成后标为 `complete`，生成不可变去敏运行记录；旧任务文件保留。

不得写入凭据、用户原始数据、未公开论文正文、私人对话或隐藏推理。
