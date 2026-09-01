---
date: 2026-08-31
mode: repo
status: draft
---

# econpaper 运行执行与进度推送架构

来源：[design.json](./design.json)。渲染报告由 skill 脚本生成于 `$TMPDIR/system-design-econpaper-run-execution.html`。

## Context

econpaper 是实验室级实证论文工作台（上传数据→清洗→识别与稳健→逐章 HITL 写作→导出）。LangGraph 管道与 FastAPI 同进程，`POST /upload` 在 async 路由内同步跑完预写管道（20-60 分钟量级），独占事件循环使全服务停摆；进度推送依赖 5 秒轮询，WebSocket 链路三处断裂成为死代码；run 工件有四层记录但进程重启后无自动恢复通道。

约束：实验室级单机 Docker Compose（≤50 人）；渐进演进，不引入 Redis/Celery/Temporal；拓扑特性优先级 **可信 > 可查可恢复 > 省**（user）；ADR-0008（多 LLM 路由）/ ADR-0010（单产品合并）/ ADR-0002（清洗 Step 协议）为已接受约束。

## Architectural debt

审计经独立红队驳斥后幸存 7 条（候选发现 11 条，4 条被驳倒删除）：

- **[blocking]** 单个事件循环同时服务交互请求与 40 分钟同步管道，无任何舱壁隔离（failure-containment · agent-engine + api · sessions.py:149 / call_llm.py:86 / Dockerfile:40 单 worker）— 由候选 A/B/C 解决
- **[blocking]** Postgres 承载全部权威状态但恢复路径未经演练，且无自动化备份（failure-containment · pg · 仅 deployment.md 手动 tar 指引，`make docker-clean` 会连卷销毁；且 pg 与 MinIO 同机同卷，备份必须落异机/云）— 无候选解决，需先行动作 M1
- **[medium]** LLM 边界无重试 Owner：瞬时错误直接击穿核心写作节点成全局 500（dependency-contracts · call_llm.py:85-97 单次 urlopen）
- **[medium]** sessions.json 全量写穿且无锁：def 端点线程池与 async 端点存在读-改-写竞态（data-ownership · session_store.py:78-93）
- **[medium]** WS 链路三处断裂成为死代码，而 deployment.md 仍宣称其工作（obsolescence · ws-hub）
- **[medium]** trace/checkpoint 无限增长且 tail 全量读盘，无保留期机制（failure-containment · run_store.py:164-181）
- **[low]** deployment.md 写 80 端口，compose 实际映射 127.0.0.1:8080:80（obsolescence · 文档漂移）

被红队驳倒（已删除）：「请求内管道无持久化记录」（实有 manifest/trace/checkpoint/PostgresSaver 四层记录，且断开不取消同步执行）、「session 双写无排序权威」（session_store.py 模块文档与 paper-engine.md:525 已明确命名 Facade store 为权威）、「默认 thread_id 脚枪」（已记录为开发便利，生产路径显式传 session_id）、「Postgres 零备份机制」（文档有手动指引）。

观察项（非结构债）：导出路径（doc_export.py:48 → export_docx.py:600）不读审批记录也不检查章节 status——devlog 北极星「审批硬证据门」在导出链路无实现，已列为 fr-3 由候选 B 补齐；agent/pyproject.toml 未声明 dependencies。

## Requirements

- **fr-1（core）** 上传→8 步清洗→预写→逐章 HITL→导出
- **fr-2（core）** 每一步可查：manifest/trace/checkpoint/工件按 Run Directory 组织
- **fr-3（core）** 审批硬证据门：无审批记录的章节内容不得通过导出交付（现状缺失）
- **fr-4（core）** 真实进度实时推送：事件 2s 内到达浏览器（user 裁定为核心需求）
- **fr-5（core）** 多 LLM 路由（ADR-0008）；**fr-6（core）** 防编造证据链（bind.py）；**fr-7（stretch）** 多模板导出与代码翻译
- **nfr** 交互 p99 < 500ms（run 运行期间也成立）；**接受并发 ≥ 5 个 run（同时执行 3 + 排队 ≥ 2，队列容量 20）**，超限 429；进度事件 ≤ 2s；审批 RPO=0 / 整机 RPO ≤ 24h、RTO ≤ 4h（备份须跨故障域）；可用性 99.9%
- **outOfScope** 多副本横向扩展、多区域、离线同步、协作共编、公开 SaaS

## Core entities and invariants

- **Run** — INV-1 每个被接受的 run 必达七态之一（PENDING/RUNNING/WAITING_INPUT/RECONCILING/SUCCEEDED/FAILED/CANCELLED），状态只能由租约持有者推进；INV-1b 效果提交必须校验 lease_epoch，旧租约只能产出暂存结果；INV-2 从 checkpoint + 事件日志可恢复
- **Session** — 同一 session 至多一个活跃 run（租约互斥）；thread_id = session_id 恒等
- **ChapterVersion** — versions 只 prepend 不覆写；内容以 sha256 标识
- **Approval** — 审批行与 run 事件同事务落库；force 必留 bypass 标记；无审批的版本不得导出
- **Dataset** — 原始 CSV 不可覆写，清洗产物为 sidecar 副本

## Data and consistency model

- **Session/Run/RunEvent/Approval** 全部落 Postgres：排序权威 = 行级事务；每 session 单租约 → 单写者，无冲突解决需求；租约带 `lease_epoch` 栅栏令牌
- **权威来源分层（评审修订）**：`runs / approvals` = 应用权威状态；LangGraph checkpoint = 执行恢复权威；`run_events` = 持久审计日志与进度游标；**章节读模型 = 从已提交 checkpoint 投影的派生视图**，禁止与 session JSON 双向写入形成两个数据真相
- **提交顺序（禁止宣称跨 Saver 原子提交）**：checkpoint 先提交 → run_events/approvals 后写 → runner 启动与认领时对账（比对 checkpoint 步进与 runs 状态）
- **RunEvent** append-only，`(run_id, seq)` 复合主键；trace.jsonl 降级为其派生镜像（重建源 = run_events 回放，游标 = seq；fail-open 语义保留）
- **ChapterVersion** 权威在 LangGraph PostgresSaver checkpoint（thread_id=session_id）
- **Dataset** 本地卷为工作副本 + S3 异步镜像（失败记录 Degradation，现状 F7 模式保留）
- 排序是 per-session 而非全局；checkpoint ≈200MB/run 是 pg 磁盘压力主项，需保留策略

## Database schemas

- **users**（现状保留）— id PK / uuid / email uniq / username uniq / hashed_password / is_active
- **sessions** — session_id PK / user_id→users / title / status / timestamps；(user_id, updated_at DESC)
- **runs** — run_id PK / session_id→sessions / kind / status(七态) / attempt / lease_owner / lease_expires_at / lease_epoch / thread_id / error；(status, lease_expires_at) 认领索引；runs 行 commit 即「run 被接受」
- **run_events** — (run_id, seq) 复合 PK / ts / type / payload jsonb；append-only，30 天保留
- **approvals** — id PK / (session_id, chapter_index, version_sha256) 唯一 / decision / reviewer_id / evidence；导出硬门读取
- **checkpoints**（LangGraph 管理）— thread_id = session_id；权威承载 ChapterVersion 与管道 state

## System interfaces

1. **提交 run**（HTTPS POST command）— runs 行 commit 先于 202；Idempotency-Key（24h）；队列 20 满 → 429+Retry-After；失败结果 202/4xx/429/5xx 可区分
2. **进度事件流**（SSE GET /events）— at-least-once + 客户端按 seq 去重；Last-Event-ID 续传；≤2s + 15s 心跳；每连接缓冲 1000 事件；流断开 ≠ run 失败
3. **提交审批决定**（command）— approvals + run_events 同事务；(session, chapter, version_sha) 唯一约束幂等；版本不匹配 → 409
4. **认领 run**（内部，Postgres SKIP LOCKED）— 租约 60s / 心跳 20s；lease_epoch 栅栏；并发上限 3

## Estimates

| 指标 | 数值 | 推导 |
|---|---|---|
| 交互 API 负载 | 6 QPS 均值 / ~20 峰值 | 30 页签 × 5s 轮询；峰值 ×3 |
| 并发 run 容量（现状） | **1** | async 路由内同步 invoke 独占事件循环；单 worker |
| 并发 run 需求 | 5 | user 实验室级 |
| 单 run 时长 | ≈40 min | 40 次 LLM 调用 × 60s |
| LLM 并发 | ≈6 | 3 run × 2；provider 配额未知，待测量 |
| checkpoint 存储 | ≈200MB/run，≈20GB/月 | 40 超级步 × 5MB × 100 run/月 |
| 工件存储 | ≤5GB/月 | 100 run × 50MB |
| run_events | ≈2MB/run；30 天稳态 ≈200MB | ~2000 事件 × 1KB |
| 并发连接 | 30 | SSE 每连接 1 协程；现状 WS 会占满 DB 池（15） |

## Candidates

- **Architecture 0（现状，layered-monolith）** — 单进程同步管道；容量 1；重启杀 run；轮询 + 断链 WS
- **候选 A（modular-monolith）** — 单进程有界执行器：管道移出事件循环（to_thread + 信号量并发 3/队列 20），runs 表做准入，SSE 替代 WS。零新增容器；但 api 重启仍杀 run（dev --reload 高频踩雷）
- **候选 B（service-based，推荐）** — **模块化单体 + 独立 Runner 进程 + Postgres 持久化任务队列 + SSE 进度流传输**：runner 独立容器 SKIP LOCKED 认领租约，api 重启不杀 run；checkpoint 先提交、run_events/approvals 后写 + 启动对账；approvals 审批权威 + 导出硬门。零新中间件，迁移 M（三步各自可发布）。系统保持单代码库、统一领域模型、单数据库实例，仅进程隔离，严禁向微服务演进
- **候选 C（event-driven）** — 事件溯源 run 日志：trace 升级为权威日志，状态全部回放重建。**评审结论：正式关闭**——checkpoint 已覆盖主要恢复需求，全面事件溯源缺必要性论证
- 已关闭选项：Redis/Celery/Temporal（反过度工程门 1）；WS 连接织物（anti-gate：30 << 数千）；多副本 + LB（扩展阶梯触发条件未到）；S3 作状态存储（blob 字节不需要）

## Comparison and recommendation

**推荐候选 B**。证据链：

1. envelope 实测容量 1 vs 需求 5——三个候选都把执行移出请求路径（入场券）
2. 分胜负责的失效模式：api 重启杀 40min run。`uvicorn --reload` 是开发常态而非尾部风险，违反 INV-2；B 用租约隔离执行与 API 可部署性（A 与 B 唯一载荷轴差异，reliability 3 vs 4）
3. 成本：一容器 + 三张表，Postgres SKIP LOCKED 即队列（~6 QPS 场景一个 ACID 库绰绰有余）——满足「渐进演进」
4. 实时：run_events 落库 + SSE 游标 ≤2s（NFR-3），精确匹配单向推送形态
5. C 在可查轴更强但机制超出证据，违反「省」
6. **用户评审结论（2026-08-31）：候选 B 方向批准**，四项修订（容量口径统一 / 效果键幂等 / 提交顺序与读模型 / 备份跨故障域）完成后按五项故障场景验收；A 仅限紧急过渡；C 正式关闭。修订已全部落入本设计，状态保持 draft 待验收

## Critical deep dives

1. **LLM 超时是第三终态** — run → RECONCILING；效果标识 = **(run_id, step_id, attempt)**：执行结果先落 attempt 暂存（不可见），最终提交（章节版本/run_events/工件指针）时在 runs 行校验 lease_epoch，旧租约提交被拒绝；效果键唯一约束去重。LLM 请求本身无法 exactly-once，但重复结果只留存于暂存，不会二次成为权威状态（prepend-only 版本表只提供历史保留，不提供重执行幂等）。重试预算 2 次/调用 + 抖动，唯一 Owner = call_llm；预算耗尽 → FAILED 携证据
2. **进度事件交付** — at-least-once + seq 去重；SSE 不占 DB 会话（修复现状 WS 占池失效模式）；nginx proxy_buffering off；写事件失败 → Degradation（fail-open 保留）
3. **审批权威与导出硬门** — approvals 表同事务落库；导出校验每章节 version_sha256 匹配的审批记录，否则 409 review_gate；宁可拦住不可放行

## Operations and rollout

迁移三步（各自可发布、可回滚）：① 建表 + sessions.json→pg 双写一个发布周期 ② runner 容器 + 认领循环 + call_llm 重试 ③ SSE + 前端切换 + 删除 ws-hub 死链。sessions.json 停写后回滚为一次性窗口。首行动作（与候选选择无关）：pg_dump cron 至**异机/云对象存储（跨故障域；同机 MinIO 与 pg 同故障域，不满足整机 RPO）** + 一次计时恢复演练。

## Risks and what breaks first

- MiniMax 并发配额未知（3×2=6 请求）——先于一切测量 429 率与延迟分布
- checkpoint ≈20GB/月——保留策略落地前持续吞噬 pg 磁盘（3-6 个月）
- 先坏的是：学期截止周提交流激增，PENDING 队列 20 不够——观测队列深度再调

## Measurements that could overturn the decision

- 单 run 实际时长分布（若普遍 <5min，候选 A 的重启风险敞口收窄，A 足够）
- api 重启频率（若团队改为长会话开发模式，B 的核心优势减弱）
- MiniMax 429 率（若配额紧张，租约并发需下调并提前谈配额）

## Next steps

见 design.json `nextSteps` M1-M8：备份演练（异机/云）先行 → 建表双写 → runner + 重试 → SSE + 删死链 → 导出审批硬门 → 文档/打包修正 → 三项测量 → **五项故障场景验收**（① api 重启 run 存活 ② runner 击杀恢复 ③ 旧租约提交被拒 ④ SSE 重连去重 ⑤ 异机备份恢复一致性）。

## Notes

**2026-08-31 用户评审结论**：候选 B 方向批准（精确定义：模块化单体架构 + 独立 Runner 进程 + Postgres 持久化任务队列 + SSE 进度流传输；单代码库、统一领域模型、单一数据库实例，仅进程隔离，严禁向微服务演进）。A 仅适用于紧急临时方案；C 正式关闭。四个阻断性问题（容量口径矛盾 / prepend 误作幂等 / 提交闭环缺失 / 备份未跨故障域）已修订落入本设计；方案自"理论设计合理"提升至"故障场景下仍然可信"的标准，通过 M8 五项故障场景测试后方可标记 decided。
