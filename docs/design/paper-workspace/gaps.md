# 现状差距与落地顺序

> 上级：[创作台方案](README.md)

## 已经有的

| 能力 | 位置 | 可以直接用吗 |
|---|---|---|
| 持久化运行 + 有序事件 + 断点续传 SSE | `backend/run_repository.py`、`/runs/{id}/events` | 可以；扩展成会话级 |
| 语义目标注册表 + 光标播放器 | `frontend/src/lib/agentCursor/` | 可以；补 select / type 两个动作 |
| 研究台账：设定运行、比较、主张批准 | `backend/routers/research.py` | 可以；Ref 指向其中的设定运行 |
| 证据版本与主张过时 | evidence revision / claim stale | 可以；粒度下沉到 Ref |
| 助手对话 + 暂停审批 | `backend/routers/agent_spike.py`（LangGraph v1） | 原型级；需要换工具集并接入正式鉴权 |
| 命令读回原则 | `frontend/src/lib/confirmationCommands.ts` | 可以 |

## 要新建的

| 缺口 | 为什么要 | 规模 |
|---|---|---|
| Document / Block / Ref | 章节现在是整块文本，数字写死在文字里，过时了无从得知 | 大：新表、迁移、渲染器 |
| ChangeSet + 撤销 | 目前没有“一组改动”的概念，也无法撤销 | 中 |
| ReviewNote 锚定到块 | 现有评审是整章打分，没有位置 | 中 |
| 会话级事件流 + outbox | 现在只有按 run 的流；WebSocket 流是假流 | 中 |
| 前端会话 store（快照 + 归约） | 现在的状态分散在 `workspace.ts` 的多个轮询里 | 中 |
| 光标 select / type 动作 | 现有播放器只会移动和高亮 | 小 |

## 建议顺序

每一步都能单独上线、单独验收：

1. **会话事件流**：先把现有的 run 事件和主张 / 证据变化接到 `/sessions/{id}/events`，前端改成快照 + 归约。界面不变，先换管道。
2. **Document + Ref（只读）**：把现有章节转成块，数字转成 Ref；稿子能显示“过时”。还不允许助手改。
3. **ChangeSet + 撤销（用户手改）**：用户能在稿子里改字，有版本、能撤销。
4. **助手改稿 + 光标**：接上 `propose_change`、`point_at`、`ask_user`，对话线程出现工具卡、询问卡、改动卡。
5. **审稿批注锚定**：现有自动评审的输出落成 ReviewNote，助手可以处理。

## 已定的决策

见 [README](README.md#已定的决策2026-09-24)：多线程；第一版支持段落手改；Notebook 只读但代码完整披露。

据此对顺序的影响：

- 第 3 步（用户手改 + 撤销）保留在助手改稿之前。
- 新增一步，排在第 2 步之后：**计算记录与复现包**。把每次设定运行的实际调用落成 ComputationRecord，Notebook 只读展示，并可下载 `analysis.py`。现有 `/code-export` 的 Stata / R 翻译接进来，但在做完数值核对之前一律标“未核对”。

## 进展

- 2026-09-24：复现脚本与复现包已落地（研究台账的设定运行），见 [验收契约](../../acceptance/replication-script.md)。导出对话框第一项改为“实际运行的代码”。尚未做：Notebook 界面、`used_by` 反查、正式估计主流程的计算记录。

## 与现行基线的冲突（实施创作台前要定）

- [前端交互基线](../../specs/frontend-interaction-current.md#结果出现) 写明“数字不做老虎机式 count-up”；创作台原型里数字会从旧值滚到新值。两者只能留一个，需要在实施创作台时明确取舍。
