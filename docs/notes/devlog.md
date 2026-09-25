# 开发日志（DEVLOG）

> 记录产品每一步真实进展。规则：一条一个日期，写了什么、为什么、验收数字、
> 还欠什么。决策性内容不在这里展开，指向 docs/adr/ 对应条目。

## 2026-09-26 —— 执行与评审隔离首轮跑通；刷新锁死修复合并

- **流程**：`AGENTS.md` 新增“执行与评审隔离”：执行者在本地候选分支 commit，不 push；评审只拿 SHA、公开要求和自己出的反例，读不到执行者的自评；每轮换新评审，评审不改代码。
- **补审 9e830281**：第 3 轮 ACCEPT 原是修复者自判。新评审判 REJECT，找出一个既存 P1（估计运行中刷新导致 SQLite 写锁死），S1–S5 确认已闭合。见 `docs/reviews/20260925-retro-review-9e830281.md`。
- **修复 66712a63**：新评审判 ACCEPT。评审加重负载后，基线第 73、147 轮出现 500，候选 900 轮 0 次；浏览器估计运行中刷新 32 次全部正常。见 `docs/reviews/20260926-refresh-lock-and-p3-review.md`。已本地合并到 main，未 push。
- **事故**：执行者用 `pkill -f "vite.*5173"` 误杀了另一个项目的 dev server。之后派出的 agent 一律禁止宽匹配 kill，只能停止自己记录了 PID 的进程。
- **还欠**：2 个 P3（key 先记录确认再上传会重复执行；SQLite 没开 WAL 和 busy_timeout），见 `runtime/tasks/20260926-p3-leftovers.md`。

## 2026-09-25 —— 第 3 轮补审修复：SSE 断开泄漏 P1 + 4 个 P3

对象：`docs/reviews/20260925-retro-review-9e830281.md` 列出的 6 项。

- **P1（SSE 断开致 SQLite 写锁死）**：`routers/run_execution.py` 的
  `generate()` 里 `await repo.events_after(...)` / `await repo.get(...)`
  改成 `await asyncio.shield(...)`；`finally` 里释放 `_sse_connections`
  计数同理。根因：Starlette 用 anyio cancel scope 取消断开的生成器，取消
  会在同一个已取消的 scope 里对后续每个 await 重新投递，未加保护时
  DB session 的 close 会被这个重投递打断，连接/aiosqlite 后台线程可能
  半开半关。`asyncio.shield` 把查询+session close 整体挪成独立 task：
  外层立刻停流，内层的 DB 往返总能自己跑完再关连接。
  **诚实记录**：本地用真实 uvicorn + 真实 TCP 断开（顺序 250 次随机时机
  + 20 次强制命中查询窗口的确定性重放 + 300 次并发批量断开）都没能在
  当前依赖版本（SQLAlchemy 2.0.36 / Starlette 0.38.6 / aiosqlite）下复现
  出锁死或连接泄漏——`ROLLBACK` 每次都正常收尾。组件级测试改为直接断言
  "被取消时 DB 往返协程本身有没有被允许跑完"（`asyncio.shield` 的直接
  效果），而不是断言下游的 SQLite 症状；红/绿都已用 `git stash` 单独验证。
- **P3 幂等 key 跨阶段复用**：`services/formal_binding.py` 新增
  `ledger_claims_key`；`run_repository.enqueue()` 用它挡"记录确认"用过的
  key 被 `continue_estimate` 复用；`facade/session_store.py` 的
  `mutate_state(idempotency_key=...)` 反向挡 run 队列用过的 key 被
  `record_confirms` 复用。两个方向都是 409 `idempotency_conflict`。
- **P3 409 清掉别人的运行指示**：`workspace.ts` 的 `continueEstimate` 只在
  自己真正调用了 `trackRun`（本地 `ownsDirectionBusy` 标记）时才在
  `finally` 里清 `directionBusy`；`PrewriteConfirmCard` 新增
  `hasActiveRun` prop，任何 run 在跑（本地或刷新接回）都禁用"开始估计"。
- **P3 会话忙时上传提示成"处理失败"**：`uploadResponse()` 对 409 先走
  `parseAdmissionConflict`，`handleUploadRunError` 对 `session_busy` 显示
  忙碌文案（`app.uploadBusy`），不再套用"请重新选择文件"。
- **P3 换数据后右栏不提示重查方向**：`applySnapshot` 新增
  `mainSpecification` 状态（`supersede_dataset` 清空这个字段但保留
  `research_direction` 摘要，是唯一能分辨"方向仍对着当前数据"的后端信号）；
  `App.tsx` 据此加一条 `decision.directionStale` 分支。
- **`git diff --check` 失败**：`services/formal_chain.py:139` 与
  `20260918-formal-confirmation-chain-3-closeout.md` 末尾各多一个空行，删掉。

**验收数字**：agent 1088 passed + 2 skipped；backend 736 passed + 8
skipped + 13 subtests；frontend 562 passed（75 files）；`tsc -b` 0 error；
`oxlint` 0 error（既有 warning 不算）；`git diff --check` 0；`make
docs-check` / `check_docs.py --changed main` 均 0 未处理项。

**已知缺口**：VoiceOver、完整 Tab 顺序、P1 在 Postgres 下的行为、真实数据
验收——均不在本轮范围内，原样留给下一轮。

## 2026-08-27（夜）—— 分支大清理：全仓只留 main

合流后的分支考古（`git branch -a` + `git cherry` 内容级比对）收尾：

- **删**：6 条零损失空壳（squash 合并的原型分支、north-star 存档、
  本地 backup）+ 4 条真实分支（转 tag 后删除，见下）
- **tag 存档**（内容永久可达，非分支不占位）：
  - `archive/blind-hitl-review-panel`——盲审 UX 2 补丁，与核对分权
    理念同源，收编时从此起步
  - `archive/ship-empirical-paper-runtime`——老运行时线尖端（490 补丁）
  - `archive/yishuship-review-line`——shipped 管线尖端（484 补丁）
  - `archive/concurrent-stance-wip`——并发会话未提交现场（456 行）
- 终态：本地与远端均只有 `main` 一条分支。

## 2026-08-27 —— 北极星落地日：从"陪聊半成品"到"替你干完 + 每一步可查"

今日基调：确立产品北极星——**替你干完 + 每一步可查**（功能取舍判据：
不同时推进这两条的，砍）。参照系：Apodex（Self-Evolving Heavy-Duty Solver）
的产品架构与开源件。全天五刀 + 一条真接口实弹验证，全部先红测试后实现。

### 1. `b2c6579` 修地基 + 审批硬证据门

- **backend 14 个失败清零**（此前挂的全是用户面）：
  - 根因一：passlib(2020 停维护) × bcrypt 5.x 不兼容，连合法密码都炸。
    弃用 passlib，auth.py 直连 bcrypt，72 字节截断与旧 $2b$ 哈希互通。
  - 根因二：WS 流式测试停留在三个月前的流程假设（upload 跑全图），
    现按真实路径走：上传 → 设方向（HITL 暂停）→ 预写 → 开流。
- **废除"必放行"**：approve-chapter 端点对未过审章节返回
  409 `{review_gate, score, threshold, needs_force}`；唯一旁路是显式
  `force:true` 且章节永久带 `approved_forced` 标记。

### 2. `e66429f` run 目录工件化

"可查"从 state 字段升格为磁盘事实。每个会话：

```
runs/<session_id>/manifest.json    trace.jsonl   checkpoints/(+latest.json)
                    workspace/     outputs/export/
```

- facade 全节点追踪（上传管线/预写/生成/再生成/评审/回滚/导出），
  事件含毫秒耗时与关键 detail（评审分数、接地失败、降级原因、blockers）
- 清洗 sidecar、clean.py/do、tex/pdf/docx 全部落 workspace，不再散落 /tmp
- 人工动作也是事件：审批 ok|forced、评审决策 accept|reject|force_pass，
  绕过必留 `reviewer_bypassed_review: true`
- fail-open：工件写入失败永不阻断主流程；删会话连目录一起删
- 只读端点：GET /sessions/{id}/artifacts、/trace

### 3. `ac6d2df` 把门亮到界面上（首次执行前端质量协议）

- 先取 shadcn/ui AlertDialog 与 Badge 参考实现的交互契约
  （role=alertdialog、aria、遮罩、安全 vs 破坏性动作分离、pill 变体），
  用项目 Editorial Academic Refined 令牌定制，零新增依赖
- ReviewGateDialog：409 不再是裸报错——显示分数/阈值/评审意见，
  两出口：打回重写（走 regenerate）、强行放行（两步确认）
- ApprovalBadge：绕过核对的章节挂危险徽标，全程可见
- RunTracePanel：右栏接入最近 20 条运行事件
- 顺手清 3 笔历史 TS 债，`tsc -b` 归零；修复批准按钮空回调问题

### 4. `7444511` 综述引用回溯硬规则（ADR-0011 上半）

结构层新增两条拦截（分数上限 0.65）：

- `citation_year_mismatch`：[N] 邻近的作者-年份必须与编号指向条目一致，
  张冠李戴视为编造——此前完全放行
- 编号表非空时，含作者-年份叙述的句子必须带合法 [N]，无从核对的主张
  按 invented_citation 处理

### 5. `8d23d03` Apodex 深搜旁路实弹接通（ADR-0011 下半）

用户申请到两周免费 API key 后实弹联调，暴露三种形态，逐一红转绿：

| 形态 | 解法 |
|---|---|
| 默认 SSE 流（text/event-stream） | 显式 stream:false + 强推时拼装 delta.content |
| 深研模型无视 JSON-only 指令（实测返回 15 万字符中文综述，自调 web_search×4） | 递归收集所有 content 字符串逐段扫描 |
| 连排 JSON + 空 choices:[] 噪声 | Extra-data 安全的对象遍历 + 空数组不算命中 + 文献形状识别 |

**实弹验收**：查询"最低工资 就业 中国 双重差分"，从真实响应解析出
20 条真实中国 DID 文献。启用方式：`LITERATURE_SOURCE=apodex` +
`APODEX_API_KEY`（默认 base=https://api.apodex.ai/v1、模型 apodex-1.1）。
**计费边界（用户勘误后实测）**：两周免费=Apodex 1.1 / 1.1 Mini 两核心模型;
带 deep-research / deep-solve 后缀的属 Deep Research 计费线(限时 8 折,仍收费),
适配器绝不以其为默认。另:1.1 思维链重,max_tokens 需 20000、超时 240s,
数组可能只在 reasoning_content 里。免费窗口过期按 ADR-0011 整体拆除。
已拒绝方案：MiniMax 兼管文献事实层（生成/证据须分权），详见 ADR。

### 验收数字（当日收盘）

| 层 | 结果 |
|---|---|
| agent | 543 passed |
| backend | 188 passed, 7 skipped(环境性) |
| frontend | vitest 204 passed / tsc -b 0 errors / oxlint 0 errors |

### 已知欠账（下次优先级）

1. apodex 条目缺 year/doi 元数据 → 接 Crossref DOI 反查补齐，让
  citation_year_mismatch 门对其生效
2. 20 条条目的 relevance_score 当前恒为 1.0，未利用模型排序信号
3. 免费窗口结束：ADR-0011 到期拆除动作（模块+测试+本日志标注）

---

*维护约定：新条目插在最新日期条目之上，倒序排列；只写事实与数字，判断走 ADR。*
