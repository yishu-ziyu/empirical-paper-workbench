# 验收契约：渐进研究流的运行事实加固

Status: complete

来源：`docs/reviews/20260917-progressive-flow-review-brief.md` 与独立评审结论。
集成基线：`feat/progressive-research-flow` 已先合入 `origin/main@d2f5533`，本地 merge commit
为 `2d83c2c9c716`。本契约不改研究计算，只修「分析中」披露对真实 run 的归属与表述。

## Change

1. **底栏只属于当前 run。** 短期观测状态显式携带 `sessionId / runId / kind`；旧 run 的
   晚到事件不能写进新 run，切会话、开始另一类 run、运行终结时都会解除旧披露。
2. **六条等待路径共用一个接缝。** 新上传、教学案例、方向 run、刷新恢复、待恢复上传与
   设定跑批都经 `waitForTrackedRun`；刷新后 SSE 回放仍可恢复真实步骤。
3. **blocked 优先于“当前动作”。** 摘要明确写「被拦住」，但不把 `blocked` 擅自解释成
   「轮到用户决定」；后端没有公开 action-required 事实时，前端不补这一层含义。
4. **progress 完成不等于 run 完成。** 已收到步骤均为 done、终态尚未确认时只写
   「已收到的步骤完成，正在等待运行结果」；终态由 `waitForRun` / durable snapshot 决定。
5. **200 条不再静默冻结。** 同一个 `node::specId` 始终接受最新状态；超过容量时优先丢
   最早已完成项，保留 active/blocked，并明确显示省略数量。
6. **设定跑批不重复披露。** `spec_run` 保留自己更诚实的 `k/总数` UI，不再维护不可达的
   generic node 文案，也不会把上一条上传/预写路径留在底栏。
7. **未知节点不隐藏也不裸露。** 摘要使用中性用户文案；展开详情保留原始 node，便于追查。
8. **可访问性与小屏。** 摘要有 live region、动态展开/收起文案；面板限制高度并可滚动，
   小屏使用 viewport 定位，常规屏跟随触发器锚定。现有 reduced-motion 全局闸门继续生效。
9. **实验页与流程闸门。** `/spike` 在开发环境可用，生产环境须显式
   `VITE_ENABLE_AGENT_SPIKE=1`；PR CI 验证真实合并树，并要求填写人工可证的四段交接事实。
10. **短暂探针拥塞不再伪造“失去租约”。** Runner 允许一次小于 650ms 的慢 authority
    probe 返回真实结果；明确 `False` / `LeaseLost` 仍立即停止，持续不可用或卡死仍在 1 秒内
    触发取消。所有 progress / terminal 写入继续以 owner + lease epoch 做最终 fencing。

## Not this

- 不新增持久前端运行状态机；完整历史仍归后端 RunEvent、snapshot 与账本。
- 不把 `spec_run` 强塞进通用步骤列表，也不虚构每个 spec 的 done 事件。
- 不修改后端 progress 词表，不添加百分比、ETA、倒计时或“还剩几步”。
- 不把 `blocked` 自动升级为“需要用户确认”；只有明确产品事实才能使用该措辞。
- 不在本增量重写 `AgentSpikePage` 的实验协议；先阻止它在生产环境默认裸露。
- 不提交或删除 `frontend/public/_tmp-choice-progressive.html`。
- 不推远端。

## Checks

### C1 run 所有权

- 上传 A 后开始另一 run，A 的步骤不再显示。
- A 的迟到 SSE 事件不能写入 B。
- 切换 session / new study 后披露清空。

### C2 恢复一致性

- snapshot 含 active prewrite/upload 时，刷新后 EventSource 回放的 `run.progress` 能进入底栏。
- `spec_run` 恢复继续更新自己的 k/总数，不出现通用步骤披露。

### C3 表述真实性

- blocked 摘要同时包含节点文案与「被拦住」。
- 全部已观察 progress 为 done、terminal 未到时不得出现“运行已完成”。
- 未知节点摘要不显示内部 snake_case，展开详情仍可核对原始 node。

### C4 容量与顺序

- 到达 200 条后，第 201 条若更新既有 active 为 done，必须生效。
- 第 201 个不同节点到来时保留最新事实，并令 `truncated=true / omittedCount=1`。
- 重复或倒序 seq 不得把较新的状态覆盖回旧状态。
- 摘要候选按最后真实更新顺序，而非第一次出现的位置。

### C5 跨层与工程闸门

- App 级测试覆盖 SSE → `workspace.ts` → 底栏组件，而非只测纯函数/组件。
- TypeScript、完整前端测试、lint、生产构建与仓库 `make test` 全部通过。
- PR handoff 校验：完整模板通过，空模板失败；CI YAML 可解析；`git diff --check` 通过。

### C6 Runner authority

- 单次约 350ms、最终返回 `True` 的慢探针不得取消合法 run（旧 200ms timeout 会误杀）。
- 明确失权仍立即停止；持续异常与永不返回的探针仍在 1 秒内置 `lease_lost`。
- 完整 backend 套件不得再随机把已执行成功的方向/确认 run 留在 `RUNNING`。

## Verification evidence

- `make test`: PASS — API drift；Agent `1066 passed, 2 skipped`；Backend
  `636 passed, 8 skipped, 13 subtests passed`；Frontend `68 files / 504 tests`。
- `make test-backend`: PASS — `636 passed, 8 skipped, 13 subtests passed`（最终 authority
  参数下独立复跑）。
- `cd frontend && npx tsc --noEmit && npm run lint && npm run build`: PASS；lint 仅保留
  6 条既有 `react-refresh/only-export-components` warning，0 error；构建仅有既有大 chunk 提示。
- PR handoff 脚本：完整标记块 PASS，空交接 FAIL（预期）；CI YAML 可解析；`git diff --check` PASS。

## Remaining manual evidence

- 浏览器真人复验仍应覆盖 320×568、键盘、VoiceOver，以及一次真实方向 run。
- `make verify` 只有前后端服务已运行时才有意义；未运行服务时不得把静态检查冒充它。
