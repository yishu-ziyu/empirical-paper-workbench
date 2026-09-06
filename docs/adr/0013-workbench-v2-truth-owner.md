# ADR 0013 — Workbench v2 收敛：研究状态唯一真相在后端

- **Status:** Accepted（2026-09-05，随验收契约 `docs/acceptance/workbench-v2-golden-path-rescue.md` 实施）
- **Date:** 2026-09-05
- **Supersedes:** —（不推翻 ADR-0010/0012，是读模型与前端状态层的收敛）
- **Related:** ADR-0003（SessionStore 单一真相）、ADR-0010（一个产品）、验收契约 workbench-v2-golden-path-rescue、`docs/specs/design-sources.md`

---

## Context：旧系统为何失控

1. **业务真相双写**。后端 SessionStore（SQLite）是 `facade.get_state/save_state`
   的唯一真相，但前端 `workspace.ts`（1751 行）又维护了一套平行业务状态：
   sessionStorage 存数据集元信息（`econpaper_csv_meta`/`econpaper_data_columns`）、
   localStorage 按 session 存 run 句柄（`econpaper_active_run_id:<sid>`）、
   自带 `DeskSnapshot` 重复类型。后端有而前端无 = 刷新丢；前端有而后端无 = 换设备丢、
   清缓存丢。两套状态必然漂移，且漂移只会在"刷新/恢复"这条低频路径上爆发。
2. **恢复逻辑靠拼装**。刷新恢复 = GET /sessions/{saved} + localStorage run 句柄 +
   待重放 command 三路合并，任何一路过期都产生假空态或假加载。
3. **Evidence 没有读模型**。系数/SE/p/N 散在 state.estimate、treatment_row、results
   三个字段里，前端各自取数拼装；"这个数字从哪来"（哪次 run、哪份数据、哪个估计器）
   没有单一可查入口。
4. **主界面失焦**。App.tsx（901 行）中栏是长滚动堆叠，Evidence 只有一个入口按钮；
   DeskPage 内嵌第二套静态工作台预览（shape/clean/estimate/write 面板），两个"工作台"
   观感互相竞争产品本体。

## Decision

### 1. Truth owner = 后端（SessionStore + Run Engine）

- **Project Snapshot**：`GET /api/sessions/{id}`（`SessionInfoResponse`）是唯一研究
  状态读模型。在既有 instrument 投影之上新增 `dataset`（name/rows/columns，取自
  session 元数据；上传时原文件名落库）、`active_run`（{run_id,kind,status}，来自
  `RunRepository._active_run` 的公开投影）、`degradations`（可见降级摘要，
  `public_degradations` 投影）。
- **Evidence 读模型**：`GET /api/sessions/{id}/evidence` 组合 facade state +
  run_store（trace/manifest/artifacts）+ RunRepository（latest prewrite run），
  返回 estimate 数字、specification、identification、robustness、provenance
  （run_id → dataset → trace/artifacts）。不建第二存储。estimate 缺失 →
  `available=false` + blockers（no_estimate / estimate_failed / no_identification /
  no_robustness），不报 500。
- **失败显式化**：estimate `status=error` 在 evidence 中 `available=false` 且
  blockers 含 `estimate_failed`；results 章 409 write_blocked 的 readiness 门
  （`agent/engine/readiness.py` TRUTH_KEYS）原样保留并补测试覆盖，未弱化。

### 2. 前端允许保存什么（R2 豁免清单）

- 保留：session id 句柄（`econpaper_session_id`，身份缝线）；短期 command 投递
  （`econpaper_pending_run_command:<sid>` 带 idempotency key 的待重放 direction、
  `econpaper_pending_upload`、`econpaper_seen_guide`/`econpaper_sample_direction`
  UI 偏好）。
  豁免理由：请求响应丢失后的重放必须凭客户端侧 key（服务端幂等消费同一 key）；
  这是「投递凭证」，不是「业务真相」。
- 删除：`econpaper_csv_meta`、`econpaper_data_columns`、
  `econpaper_active_run_id:<sid>`（整套 read/write/clear 函数）与 `DeskSnapshot`
  重复类型（改用 openapi 生成的 `SessionInfoResponse`）。数据集、run 生命周期、
  估计、章节、大纲一律从 snapshot 恢复。

### 3. 恢复协议（C3）

```
刷新 → GET /sessions/{id}（snapshot）
     ├─ exists=false → 回空桌
     ├─ active_run 存在 → 订阅 /runs/{run_id}/events（SSE，waitForRun 自带轮询兜底）
     │    └─ 终态后回读 snapshot 应用（durable 终态是唯一权威）
     ├─ 无 active_run 但有 pending command → 原 idempotency key 重放 POST /direction
     └─ 否则结束（已完成的结果已在 snapshot 里）
```

### 4. Workbench v2 布局（C7）

单一 Shell（`App.tsx` + `ThreeColumn`/ResizableWorkspace + 底部状态条）：
- 顶：项目名 + Run（打开问题卡）/ Export（导出对话框）；
- 左：研究对象清单 Question/Data/Design/Evidence/Literature/Paper（`ResearchRail`，
  状态来自 snapshot 投影）+ 章节导航；
- 中：当前 artifact（`WorkbenchArtifact`）。Evidence 升一等视图（`EvidenceView`：
  β/SE/p/N 大数字 + specification + 识别/稳健 + 溯源链
  spec→estimator→run→dataset→trace/artifacts，某层没数据显示「暂无」）；
  失败态显式给下一步，无无限 loading；
- 右：Agent 在做什么/为什么/blocking decision/[Action]（WorkspaceDecisionRail +
  ResearchComputer）；
- 底：run 状态条（运行中/空闲/上次失败 + 降级计数 + trace 提示）。
Desk 退为建项对话入口（移除内嵌工作台预览面板）；Guide 仅显式进入；Spike 仅 /spike。
视觉沿用 design-sources.md 墨纸绿色板，无新渐变/玻璃/发光。

## Consequences

- 前端不再可能展示与后端不一致的数据集元信息或 run 状态；"清掉前端存储刷新"与
  "普通刷新"恢复路径完全一致。
- Snapshot 每次刷新多两次轻查询（dataset 元信息 + active run）+ 一次降级日志读取，
  全部走既有 SessionStore/RunRepository 索引路径。
- 旧 legacy 页面（GuidePage、AgentSpikePage、DeskPage 的对话流）保留代码但从主路径
  退位；后续可按使用数据决定删除。
- openapi 契约变更经 `make gen-api` 重新生成，`check-api-drift` 闸门通过。

## Out of scope（本次明确不做）

- 不重写 StatsPAI/清洗管道/38 种方法 UI；estimate 数值仍由真实统计执行产生。
- 不引入新框架/状态库/数据库；run 事件细粒度进度（逐节点 ms）仍走 trace 端点，
  未在 Snapshot 中展开。
- 不做登录态下的多会话列表 UI（`GET /sessions` 已有，前端入口未建）。
- Evidence 视图的图表化（置信区间微图等 design-sources 手法）留待视觉迭代。
- C3②/C4/C7 的浏览器实弹由主 agent 执行并归档截图；本 ADR 只记录实现契约。
