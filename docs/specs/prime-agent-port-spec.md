# Prime Agent → econpaper Python 移植规格

> 来源：除特别标注外均为【一手】——`architecture.md`、`rlm-runtime.md`（255 行）、`compaction.md`（395 行）经 curl 拉取原文精读；README 为【一手】。调研日期 2026-08-29。
> 目标栈：FastAPI + LangGraph 0.2 骨架 + Pydantic AI v2.35 节点内循环 + jupyter_client/ipykernel 持久内核 + minimax/OpenAI 兼容端点。
> 状态：Phase A ✅（KernelSession / EstimateAgent / eval 基线 6/6 已落地）；本文档指导 Phase B/C。

## 0. 原系统速览

Prime Agent（PrimeIntellect-ai，MIT，TypeScript，底座 earendil-works/pi）：自改进 RLM agent。
进程边界五分【architecture.md】：Client（只渲染）→ Daemon supervisor（路由/attach/跨 agent 消息）
→ Session worker（根会话树 = AgentSessionRuntime + Scheduler + 根内核 + RLM 子运行时）→
AgentSession（provider 调用/队列/工具/compaction/goals/transcript）→ Persistence（JSONL + artifacts）。
**worker 与内核是独立进程，为了生命周期与故障隔离，不是安全沙箱**（同 OS 权限执行）。

## 1. 持久内核

**原设计**【一手 rlm-runtime.md】：内核懒创建；stdio JSON-lines 协议——
requests: `execute, interrupt, host_reply, snapshot, restore, list_names, shutdown`；
events: `ready, stdout, stderr, result, display, host_request, error, done`。
要点：
- **串行执行**：一个内核一个共享命名空间，普通 cell 不并发；输出事件携带发起 cell 的 id
  （asyncio 分离任务归属正确）。
- **命名空间快照复活**：`snapshot/restore` 请求 + 会话工件里的 `kernel-state.dill`（dill 序列化
  整个命名空间）+ `kernel-state.json`——持久会话靠它跨进程复活变量。
- 管理环境用 uv 引导（Python 3.11 + dill + runtime 包）；shutdown 先礼貌请求再兜底 kill。

**我们的对应物**：`agent/engine/sandbox.py` `KernelSession`（已落地，实测变量跨调用存活）。
- **缺口（Phase B）**：checkpoint↔内核对齐。移植设计（现在有一手依据了）：每个 LangGraph
  super-step 边界发 `snapshot` 等价物——用 dill 把内核命名空间 dump 到会话工件目录
  （`{session_dir}/kernel-state.dill`），checkpoint 元数据记录该路径；断点续跑时起新内核 →
  `restore` 回放。jupyter_client 原生支持 `execute_interactive`，dill dump 用内核内
  `%run` 一段快照脚本即可，无需改协议。
- **缺口（Phase B）**：无 daemon 层，内核寄生 uvicorn 进程。他们的 daemon 解决 attach/断线/多会话
  路由；空桌多会话时再建。

## 2. RLM：上下文当变量

**原设计**【一手 rlm-runtime.md】：
- 数据/中间产物活在内核命名空间；模型上下文只见代码、截断输出、摘要。
- **compaction【一手 compaction.md】**：触发条件 `contextTokens > contextWindow - reserveTokens`
  （reserve 默认 16384）；保留最近 `keepRecentTokens`（默认 20000）；切点只落在
  user/assistant/bash/自定义消息上，**永远不切在工具结果上**（工具结果必须跟工具调用同生共死）；
  单轮超预算时"拆轮"出两份摘要合并。摘要用**结构化模板**：
  `## Goal / ## Constraints & Preferences / ## Progress(Done/In Progress/Blocked) /
  ## Key Decisions / ## Next Steps / ## Critical Context + <read-files><modified-files>`，
  文件清单跨多次 compaction 累积。**序列化时工具结果截断 2000 字符**（工具输出是上下文最大
  来源，ipython 尤甚）。重复 compaction 从上一次的 kept 边界起算，token 数重建。
- 分支摘要：`/tree` 换分支时对被放弃分支做公共祖先摘要注入。

**我们的对应物**：EstimateAgent 已实现启发式版（head 5 行 / 输出截 80 行 / 超长落盘回传路径）。
- **校准（Phase A 收尾，数字现成）**：轮次上下文管理照抄他们模板——iterations 日志超阈值时
  按 `Goal/Progress/Key Decisions/Next Steps/Critical Context` 六段结构化摘要压缩，工具输出
  序列化截 2000 字符；阈值用 token 估算（contextWindow − 16384 reserve、保留最近 20k）。

## 3. 子代理 rlm() 句柄

**原设计**【一手 rlm-runtime.md】：
- `await rlm("任务", name=..., model=...)` 走 `host_request` 事件到 TS host：深度检查
  （`RLM_DEPTH < RLM_MAX_DEPTH`，**默认最大深度 2**：root→子→孙，孙不可再生）→ 注册表登记 →
  **立即返回 RLMSpawnHandle（只确认受理，永不含答案）**。子结果只经显式
  `agent_message.send(..., receiver_role="parent")` 或文件回传。
- **注册表活过内核重启、compaction、restore**；daemon 化子代理完成后可复活重连；
  删除 = 写墓碑（transcript/artifacts 不抹）。
- **成本归因**：子 usage 异步折叠进发起它的父 assistant turn（`child_usage_attributed` 条目），
  树内各自统计与根聚合可对账，且不虚增父上下文窗口占用。
- 失败语义：模型不可用 ⇒ spawn 直接失败**不静默换模型**；host 断连 ⇒ 等待中的调用抛
  RuntimeError 解除阻塞；父销毁 ⇒ 级联取消全部后代。

**我们的对应物（Phase B，空桌步骤卡后端）**：每张步骤卡 = 一个子运行时；受理即返回句柄（卡片
转"运行中"），产物落盘 + WS 事件更新卡片；usage 按卡归集（对账每一步花了多少 token）；
失败不静默换路、显式报错。深度限制对应"章节不可再派生写作子任务"（写作本来就该串行 HITL）。

## 4. Continual Harness（经验沉淀）

**原设计**【一手 rlm-runtime.md】：`rlm.harness` 是**持久状态账本**（prompt notes、memories、
skill 描述、子代理规格、refinement 事件），"不是第二执行引擎"。会话级存
`{artifacts}/harness/harness_state.json`，全局级存 `~/.prime/agent/harness/`；
**外部修改后 Python store 重新加载**（host 的 /refine 写入与内核写入互不覆盖）。
`/refine` = 对当前轨迹跑一次专门评审 → 小粒度 create/update/delete；**每次更新记录 before/after
快照可回滚；基础 system prompt 不可变**。

**我们的对应物（Phase C）**：改造 `agent/nodes/label_store.py` + `learning_labels.py` +
`threat_cards`：每篇论文完成后对轨迹跑评审（评审维度现成——识别失败原因、AI 评审扣分点），
产出小粒度更新写入 label/threat 账本；base（估计门哲学、串行 HITL）永不改；更新带快照可回滚。
账本文件用 JSON + 外部修改重载语义。

## 5. 有界自治

**原设计**【二手 zicode + 一手 rlm-runtime.md 失败语义】：`/autonomous` 带 turn/token/时间预算 +
用户自定义质量门；goal 技能是薄 host 桥（`goal.create/complete`），状态与记账在 AgentSession。

**我们的对应物**：EstimateAgent `UsageLimits(request_limit=10)` 已落地；质量门 = 估计门 + 串行
HITL（比原版更硬）。可借细节：预算耗尽的显式降级路径（estimate 已回退固定分派；写作侧对齐）。

## 6. 移植优先级表

| 模式 | 价值 | 工作量 | 排期 |
|---|---|---|---|
| 持久内核 KernelSession | 高 | ✅ 已完成 | Phase A |
| RLM 工具纪律（截断/落盘/摘要进上下文） | 高 | ✅ 启发式版 | Phase A |
| EstimateAgent 接入 estimate 节点（开关+回退） | 高 | ✅ 已完成 | Phase A |
| eval 任务基准 undergrad_did_01（6/6） | 高 | ✅ 已完成 | Phase A |
| compaction 结构化摘要（六段模板+2000 截断+token 阈值） | 高 | 小（规格已到手） | **Phase A 收尾** |
| checkpoint↔内核对齐（dill snapshot/restore） | 中高 | 中 | Phase B |
| 内核 daemon + attach（多会话） | 中 | 中 | Phase B（随空桌） |
| rlm() 式子代理编排（步骤卡后端，深度≤2、usage 归集） | 高 | 中 | Phase B（空桌） |
| Continual /refine 精炼管线（账本+快照回滚） | 中 | 中 | Phase C |
| 直接嵌入 Prime Agent 本体 | 低 | 高（TS 跨栈；README 自认"非安全沙箱"） | **不做** |

## 7. 备注

- 本文档 v2：v1 时 rlm-runtime.md/compaction.md 三次抓取失败标了"推断"；现已经 curl 拉取原文
  全文精读，原推断条目全部升级为一手出处，未再保留猜测项。
- "ARC-AGI-3 95.5%" 仅见中文媒体转述，README 与论文页均无此数，视为不可复现承诺。
- 信任边界提醒（他们 README/文档原话）：REPL 执行模型生成的 Python，**进程边界不是安全沙箱**；
  不可信工作区需外接沙箱（E2B 等）——与我们 sandbox.py docstring 的声明一致。
