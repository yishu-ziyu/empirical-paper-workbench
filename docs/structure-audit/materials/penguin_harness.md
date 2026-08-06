# PenguinHarness → Continuous Empirical Loop（port materials）

Date: 2026-08-06  
Source (vendor, read-only clone): `vendor/penguin-harness/`  
Primary docs: `README.md`, `packages/docs/content/architecture.en.md`, `self-improvement.en.md`, `agent-loop.en.md`  
Primary skills: `agent-creation`, `benchmark-design`, `agent-evaluation`, `agent-optimization`  
Runnable mini-loop: `examples/self-improving-agent/`  
Product targets: L8 evaluate→learn (in-run) + H8 cross-run evolution (skills/harness); see `docs/BOOK_HARNESS.md`, `docs/structure-audit/01_FINAL_APPROVED.md`, `runtime/continuous_loop.py`

---

## 一句结论

Penguin 可搬的不是桌面产品或 OmniMessage 协议，而是一套**可版本化的可变对象 + 与私有评分隔离的评价器 + 严格接受准则的搜索 + 不可变档案 + 失败即回滚**。  
本仓 Continuous Empirical Loop 已有 L8 骨架；缺的是 Penguin 那套**对象身份、接受门、快照/回滚、评分与优化隔离**的硬结构。

---

## 1. Penguin 是什么（与本仓边界）

| 层 | Penguin 事实 | 对本仓含义 |
|----|--------------|------------|
| 产品 | “Agent 构建 Agent / 自进化”桌面+CLI+Web | **不**整仓移植 UI/Server |
| 内核 | `context_engine` ReAct + OmniMessage + Trace JSONL | 可对齐「环 + 可回放轨迹」，不必抄协议 |
| 进化 | Skill 编排：建 Agent → 设 Benchmark → 评 → 优化 | **核心 port 面** |
| 状态 | 全文件：`agent_state/`、`benchmarks/`、`snapshots/`、`traces/` | 文件即 SSOT 与本仓 run 目录哲学一致 |

```text
Penguin self-improvement (two top-level sessions)
  Builder:  agent-creation → benchmark-design → Formal Baseline on scoreboard
  Optimizer: agent-optimization rounds
                │
                ├─ Reference (best kept State + Evaluation)
                ├─ Candidate (bounded edit of mutable State)
                ├─ Evaluator subagents (case × runs) ── private rubric
                ├─ accept iff complete eval AND score strictly ↑
                └─ else rollback State; never scoreboard rejected candidates

  Files:
    agents/<id>/agent_state/     ← mutable object (versioned)
    agents/<id>/benchmarks/<b>/  ← frozen after design
      statement/  (public to target)
      rubric/     (private; optimizer must not see)
      scoreboard.yaml
    agents/<id>/snapshots/vN.tar.gz
    agents/<id>/traces/...
```

不要混淆三层环：

| 环 | Penguin | 本仓 |
|----|---------|------|
| 内环 | `session.run` turns (tool loop) | step 内 ReAct / tool loop |
| 中环 | Case×Run 评测矩阵 | 一轮 pipeline + `evaluate_after_pipeline` |
| 外环 | Candidate accept/rollback（优化 Session） | L8 learn → target_steps 再跑 |
| 跨 run | version + snapshots + skill 写回 | H8（现仍弱/未接） |

---

## 2. 架构精读（只留可移植决策）

来源：`architecture.en.md`。

**决策可移植：**

1. **可编辑/可记录 → 文件；计算 → 引擎。** Server 索引不与文件事实竞争。本仓应对齐：loop/round JSON、论文工件、gate 结果在 run 目录，不把“是否绿”藏在内存或旁路栈。
2. **三边界：** Human / LLM / Environment。引擎不吞厂商协议；工具错误回灌模型，不在引擎层静默吞。
3. **Trace 双写：** 流给人类 + append-only 磁盘；恢复以 Trace 为唯一真相。
4. **Subagent = 独立 Session + 独立 Trace**，父只拿协议化结果。评测叶 worker 不得改 Target State / Scoreboard。

**刻意不 port：**

- OmniMessage 字面协议、AgentHub 模型表、Web 评估中心 UI、SQLite 多用户、桌面安装器。
- “一句话生成 RAG app” 的 builder 产品面。

---

## 3. 进化 / 评测环（权威行为）

来源：`self-improvement.en.md` + 四个 Agent Tuning Skills + `examples/self-improving-agent`。

### 3.1 角色

| 角色 | 做什么 | 禁止 |
|------|--------|------|
| Builder | 写 Target 行为文件；设计/校准 Benchmark；冻结 Formal Baseline | 不在 design 阶段改 Target 来“刷分” |
| Target | 只在隔离 Workspace 上跑 Case Statement | 看不到 rubric/Gold |
| Evaluator | 单 Case 单 Run：启动 Target → 私有打分 → **纯 YAML 协议** | 不写 scoreboard；不改 Agent；不启优化 |
| Optimizer | 诊断 → 假设 → Candidate → 委托评测 → accept/rollback | **不得读 rubric/Gold**；污染则停 |

### 3.2 Optimizer 一轮（搜索单元）

来源：`agent-optimization/SKILL.md`。

```text
1 Establish Reference (State version + complete Evaluation on frozen bench)
2 Diagnose gaps from public statements + scores + score-linked traces
3 Falsifiable hypothesis (predict which case behavior changes)
4 Build one Candidate from Reference (bounded State edit only)
5 Admissibility: general, no private eval info, only allowed fields
6 Evaluate: full case × runs matrix (parallel subagents); no State edit mid-flight
7 Decide: accept only if every cell valid AND mean score strictly > Reference
8 Persist: append accepted Evaluation to scoreboard; Candidate becomes Reference
   else restore Reference files/version; rejected never on scoreboard
Stop: hit target score OR exhaust valid candidate rounds; keep best Reference
```

硬规则（移植时要变成代码不变量，不能只写 skill 文案）：

- **严格更高分才接受**（`strictly higher`），平分/降分一律回滚。
- **运行时冻结**：`(provider, model_id, thinking_level)` 与 Reference 不一致 → 整矩阵无效，停优化。
- **version 单调**：Candidate = Reference+1；拒绝后版本号不复用。
- **改前必有 snapshot**：`snapshots/v<Reference>.tar.gz`，排除 secrets；同版本不覆盖。
- **协议结果优先**：Evaluator 只输出 plain YAML；格式坏则同 worker 重发 YAML，**不重跑 Target**。
- **失败 ≠ 零分**：`evaluation_failed` 修 cell，不记 0 分。
- **污染即停**：Optimizer 上下文进入 private rubric → 恢复 Candidate 并中止。

### 3.3 Benchmark 校准（评价器如何“长”出来）

来源：`benchmark-design/SKILL.md`。

- Pilot：每 Case 1 Run；未选中的 Pilot **不进** scoreboard。
- 难度校准看 Trace 策略，要求“分离决策”（intended vs shortcut 不同得分结果）。
- Freeze 后 Formal Baseline = 选中 Pilot 的完整矩阵，**不**为对齐 runs 数而补跑。
- 公开 Statement / 私有 Rubric 物理分目录；Gold 永不进 statement。

### 3.4 玩具环证明的是什么

`examples/self-improving-agent`：

```text
score() 是纯代码评价器（10 点：5 内容 + 5 约定）
blank AGENTS.md → 稳定丢约定分（信息缺口，不是能力缺口）
agent 从通过样例写回 AGENTS.md
mean 严格上升才保留，否则 rollback
递归：state_{n+1} = agent.reflect(state_n, new_evidence)
```

对本仓：证明 **评价器在环外、可变对象是行为文件、接受准则是分数门、回滚是默认诚实**。

---

## 4. 五件套：port 进 Empirical Continuous Loop

### 4.1 Mutable object（可变对象）

| Penguin | 本仓应对齐的对象 |
|---------|------------------|
| `agent_state/`：`AGENTS.md` + target Skills + 安全 `system_config` 字段 + `version` | **Paper run state 中允许 learn 改写的切片**，不是整棵 Results 树 |

建议本仓显式切两类对象（现在混在 round JSON / pipeline 状态里）：

```text
IMMUTABLE per round (archive only)
  estimates, tables, hashes, repro logs, raw traces, evaluate.json inputs

MUTABLE under version control (the "Target State" analogue)
  design notes / method choice within policy
  write plan, section drafts, claim map bindings
  learn notes, skill patches, harness config knobs allowed by policy
  version: integer, ++ only on accepted candidate
```

**Port 规则：**

- 一次 Candidate **只改** MUTABLE 切片；IMMUTABLE 工件只追加，不就地改历史。
- 每个 accepted learn 推进 `version`；rejected 恢复文件 + 版本。
- 禁止“优化器”直接改评价阈值或 gate 阈值来刷绿（对标：Optimizer 不改 frozen Benchmark）。

映射到现状：`runtime/continuous_loop.py` 的 `LearnPlan.target_steps` 已是“改哪段”的粗粒度搜索算子；缺的是 **versioned mutable blob + 改前快照**。

### 4.2 Evaluator（评价器）

Penguin 评价器 = **隔离执行 + 私有 rubric + 协议化分数 + session_id 回链**。

| Penguin 机制 | 本仓对应 | Port 要求 |
|--------------|----------|-----------|
| statement vs rubric 分目录 | 任务输入 vs quality/citation/REPRO 规则 | **写稿/估计 agent 不得加载 gate 实现细节当 prompt 作弊面** |
| leaf Evaluator skill | `evaluate_after_pipeline` + 未来 claim audit | 评价过程与 produce 过程分上下文（提议者-审核者） |
| score 0..100 固定尺 | quality verdicts / integrity / REPRO | 统一 **可比较标量或字典序**，accept 规则可判定 |
| `session_id` on each run | round evaluate JSON + run paths | 每个分数字段能指回工件路径 |
| wrong artifact still scored | too_thin / integrity_blocked 仍是评价结果 | 红灯是分数，不是异常吞掉 |
| evaluation_failed ≠ 0 | 管道 crash / 缺文件 | 基础设施失败 → 修 cell，不记质量分 0 |

**不要 port 的：** 用 LLM 当唯一打分器且无字段锚点。本仓优势是 **可验证任务**（表 hash、REPRO、claim↔table）；评价器应以程序 gate 为主，LLM 审阅为辅且独立上下文。

**Accept 门（移植自 strictly higher）：**

```text
completed_green 仅当：
  quality ready_for_review
  AND REPRO (or honest degrade recorded)
  AND claim integrity not blocked
否则：learn 或 halted_honest —— 禁止红灯 completed
```

（与 `02_L8_IMPLEMENTATION.md` 已落地方向一致；Penguin 补的是 **相对 Reference 的严格改进**，不只是绝对绿灯。）

### 4.3 Search（搜索）

Penguin 搜索 = **单 Candidate / 轮 · 有界编辑 · 可证伪假设 · 全矩阵评测 · 并行 cell**。

| 机制 | Port 到论文环 |
|------|----------------|
| 每轮一个 Candidate | 每 learn 轮一个 `LearnPlan`（一组 target_steps + 明确假设），禁止同时互扰的大改 |
| falsifiable hypothesis | learn JSON 必须写：预期改变的 step 产物 / 预期灭掉的 verdict |
| admissibility | 只允许 policy 内编辑（路径白名单、不得改 gold data、不得改 gate 代码） |
| case × runs | 多 seed REPRO / 多 section quality；或至少对 **失败 verdict 相关** 子集重评 |
| parallel subagents | 独立 claim audit / REPRO / section rewrite 可并行，结果协议合并 |
| 拒绝结果作证据 | rejected plan 写入 archive，供下一假设，但不上“绿板” |

**与 L8b Correct ladder 对齐（书级）：**

```text
retry (same step, no state rewrite)
  → expand/rewrite (mutable draft)
  → degrade (honest narrower claim)
  → respec (design/method change — higher cost Candidate)
  → fuse (halted_honest)
```

Penguin 的 “bounded general change” = 优先 **可复用行为写回**（AGENTS/Skill），不是 case-hardcode。本仓 H8 对应：跨 run 写 Skill/程序/Harness + canary；L8 只做单 run 内回炉。

### 4.4 Archive（档案）

Penguin 档案件：

| 件 | 路径/形态 | 作用 |
|----|-----------|------|
| Trace | `traces/...jsonl` append-only | 回放、绑定 session |
| Scoreboard | `benchmarks/<id>/scoreboard.yaml` | **仅 accepted** 评价时间线 |
| Snapshots | `snapshots/vN.tar.gz` | 版本化 State，导出/导入 |
| Workspaces | 每 Run 独立目录 | 执行隔离 |

本仓应对齐的最小档案（建议落在 `state/runs/continuous_loop_*/`）：

```text
loop_meta.json                 # loop_id, max_rounds, runtime freeze
round_k/
  evaluate.json                # full gate vectors + paths
  learn.json                   # hypothesis, target_steps, decision
  candidate_diff.patch or file list
  mutable_snapshot/ or .tar    # pre-edit Reference
  package pointers             # if any
scoreboard.jsonl or.yaml       # only ACCEPTED rounds (version, scores, decision)
traces/                        # existing pipeline/agent traces, immutable
```

规则：

- **rejected Candidate 不进 scoreboard**（可进 `attempts/` 旁路目录）。
- scoreboard 数值以写入时计算为准（Penguin：服务端不重算）；本仓 gate 程序可重算，但 **接受决策以当轮 evaluate 落盘为准**。
- 每个 score/verdict 带 `session_id` 或绝对工件路径。

### 4.5 Rollback（回滚）

Penguin 回滚层次：

1. **In-round fast rollback：** 改前保留原文件内容；reject 时逐文件恢复 + 删 Candidate 新建文件。  
2. **Snapshot restore：** `vN.tar.gz` 整包 State。  
3. **Version pin：** 评测请求带 `expected_version`；中途 version 变 → `version_changed`，矩阵作废。  
4. **Contamination stop：** 私有信息泄漏 → 停，不“半接受”。

本仓最低实现：

```text
before apply(LearnPlan):
  snapshot_mutable(loop_dir, version=R)
  record file inventory

apply edits to drafts / design / notes only

re-run target_steps → evaluate

if not strictly_better(Reference, Candidate):  # define scalar or lexicographic order
  restore snapshot
  decision=reject
  keep attempt log
else:
  version = R+1
  append scoreboard
  Reference = Candidate
```

**Strictly better 建议定义（论文环）：**

1. 主键：`completed_green` 优于一切非绿。  
2. 否则：阻塞 verdict 集合 **真子集** 缩小（例如去掉 `evidence_integrity_blocked`）且无新的更高等级阻塞。  
3. 否则：质量标量/章节完整度严格上升且 REPRO 不退化。  
4. 平局 → reject（与 Penguin 一致，避免噪声爬升）。

弱模型会 regress：玩具例已证明 rollback 是诚实，不是 bug。本仓 demo 的 `halted_honest` 应保留。

---

## 5. 映射图：Penguin 概念 → 本仓符号

```text
Penguin                         Empirical Continuous Loop
──────────────────────────────────────────────────────────
Target Agent State              Mutable paper state (versioned)
AGENTS.md / Skills              section skills, method policy, claim rules
system_config.version           loop/paper state version
Frozen Benchmark                fixed quality+citation+REPRO contracts
statement/                      pipeline inputs + user topic + data cards
rubric/                         gate code + integrity-audit rules (private to scorer)
Formal Baseline                 round-0 or first complete evaluate on frozen gates
Reference                       best accepted round state + evaluate
Candidate                       LearnPlan + applied mutable diff
agent-evaluation worker         evaluate_after_pipeline (+ isolated auditors)
scoreboard.yaml                 accepted-round scoreboard
snapshots/vN.tar.gz             pre-learn mutable snapshot
strictly higher score           strictly_better(verdicts, repro, integrity)
rollback                        restore snapshot; no green on red
contamination rule              writer must not see audit gold / private keys
H8 skill writeback              post-loop canary: promote skill only if accepted
```

L8 vs H8（审计已强调，勿互相顶替）：

| | L8 | H8 |
|--|----|----|
| 时间范围 | 单次 loop / 多 round | 跨 loop / 跨论文 run |
| 写回对象 | 本稿 mutable state | Skill / 程序 / Harness |
| Penguin 对标 | Optimizer rounds | accepted State 晋升 + 新 Benchmark canary |
| 本仓现状 | `continuous_loop.py` 已有边 | 基本未接 |

---

## 6. 建议落地顺序（结构，不扩功能 wishlist）

1. **Versioned mutable slice + snapshot/rollback API**（无 LLM 也可测：改文件 → reject → 字节级复原）。  
2. **`strictly_better` + scoreboard only-accepted** 写入 `ContinuousEmpiricalLoop.run`。  
3. **Evaluate 与 Produce 上下文隔离**（claim audit / integrity 不进写稿 prompt）。  
4. **LearnPlan 强制 hypothesis 字段**（预期灭灯 / 预期产物）；reject 进 `attempts/`。  
5. **Runtime freeze 记录**（模型、gate 版本、数据 hash）于 loop_meta；中途变更 → invalid。  
6. **H8 另轨：** 仅当 scoreboard 上连续 accepted 且 canary 过，才晋升 Skill（对标 snapshot 导出）。

非目标：

- 嵌入 Penguin monorepo 运行时。  
- 为“自进化”再开平行 orchestrator 栈（违反 L1 SSOT）。  
- 用 LLM 自评替代 program gates。

---

## 7. 反模式（从 Penguin 反面教材 + 本仓审计）

| 反模式 | 为何坏 |
|--------|--------|
| 红灯仍 `completed` | 无接受门 = 无进化，只有流水线 |
| 评价器与写稿同上下文且可见 Gold | 污染；Penguin 直接停 |
| 无快照改草稿 | 无法 rollback → 噪声累积 |
| 多 Candidate 同时改同一 State | 矩阵不可归因 |
| 把 Pilot/尝试写进正式 scoreboard | 历史不可信 |
| 失败记 0 分 | 惩罚基础设施，扭曲搜索 |
| 为刷分改 gate / 改数据 | 改 Benchmark 当优化 |
| L8 与 H8 混谈“已经自进化” | 结构审计明确禁止互相顶替 |

---

## 8. 验收（falsifiers）

Port 算到位，当且仅当下列可观察：

1. 人为把某一 round 质量改差并 `decision=accept` 的路径 **不存在**（strictly_better 阻断）。  
2. reject 后 mutable 文件与 snapshot 字节一致。  
3. scoreboard 中无 rejected round。  
4. evaluate 红灯时 loop **不能** 标 `completed_green`（已部分满足；需与 version/scoreboard 绑定）。  
5. 写稿 agent 工作区无 rubric/gate 源码作为可读“答案”。  
6. 每个 scoreboard 行能打开对应 evaluate 工件与 session/run 路径。

---

## 9. 源文件索引（深读锚点）

| 主题 | 路径 |
|------|------|
| 产品定位 | `vendor/penguin-harness/README.md` |
| 分层架构 | `vendor/penguin-harness/packages/docs/content/architecture.en.md` |
| 内环 | `.../agent-loop.en.md` |
| 自进化总述 | `.../self-improvement.en.md` |
| 创建可变对象 | `packages/skills/skills/agent-creation/SKILL.md` |
| 评价器设计 | `.../benchmark-design/SKILL.md` |
| 单 cell 评测 | `.../agent-evaluation/SKILL.md` |
| 搜索+回滚 | `.../agent-optimization/SKILL.md` |
| 最小可跑环 | `examples/self-improving-agent/README.md` |
| version 语义 | `packages/core/src/state/default-config.ts` (`version`) |
| snapshot 路径 | `packages/core/src/state/paths.ts` (`snapshotsDir`) |
| 本仓 L8 | `runtime/continuous_loop.py` |
| 书级 harness | `docs/BOOK_HARNESS.md` |

---

## 10. 给实现者的一句话

**把论文 run 收成“可版本化的 Target State”，把 gate 收成“冻结 Benchmark + 私有评分”，把 learn 收成“单 Candidate 搜索”，把 round 目录收成“snapshot + scoreboard + rollback”。**  
其余 Penguin 产品面一律不搬。
