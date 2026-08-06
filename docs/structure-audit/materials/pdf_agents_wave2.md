# AI-Agents-in-Depth · Wave2 合成：实证论文闭环现在该实现什么

| 字段 | 值 |
|------|-----|
| 来源 | 李博杰《深入理解 AI Agent》v1.4（2026-08-04）`AI-Agents-in-Depth-zh-CN.pdf` |
| 覆盖 | Ch1 ReAct/Harness · Ch4 Tools · Ch6 Evaluation · Ch10 Multi-Agent · 编排/规划 |
| 对照仓 | `实证论文项目模板`：`runtime/continuous_loop.py` · `runtime/full_pipeline.py` · 10-step spine |
| 用途 | structure-audit Wave2：**现在实现**清单（非通用 chatbot 教程） |
| 日期 | 2026-08-06 |
| 与 p1/p2/p3 | p1=公式/Harness 原则；p2=上下文/Skills；本文件=ReAct·工具·规划·多 Agent·评估 → **实证环动作** |

---

## 0. 一句结论

**实证论文 Agent 不是「聊天写稿」。**  
书中生产公式 `Agent = Model + Harness(Context + Tools + Constrain + Verify + Correct)` 映射到本仓，就是：

```text
  full_pipeline (10 步确定性骨架)
       +  步内/跨步 ReAct（需要探索时才开）
       +  工具：估计/读表/写稿/审计（结果自包含）
       +  continuous_loop：evaluate → learn → target_steps 回炉
       +  程序化 Verify（REPRO / integrity / claim 链），幻觉一票否决
```

**现在只做：** 把书里已证有效、且本仓已有半成品的几条闭合；**不做：** 通用多 Agent 产品面、LLM-only 自评刷绿、后训练改权重、A2A 社交。

---

## 1. ReAct：轨迹 = 静态前缀 + 消息历史

### 1.1 书中机制（Ch1.1.5）

- 循环：`Thought → Action(tool_calls) → Observation(tool result)` 直至退出。
- 每次 LLM 调用看到：**静态前缀**（system + tool defs）+ **轨迹**（user / assistant / tool）。
- 消融事实：无 tool defs → 不能动；无 tool results → **盲目循环**；无历史 → 重复步骤；无 reasoning → 决策断裂。
- 退出条件（自主环）：`final_answer` 类工具 / 无 tool_calls / 错误超限 / **max rounds**。

### 1.2 对本仓的含义（现在）

| 层 | 现状 | Wave2 动作 |
|----|------|------------|
| 外环 | `continuous_loop`：propose→run→evaluate→learn↻ | **已是 Loop 工程**；保持为 SSOT |
| 内环 | `full_pipeline` 线性 10 步 | **工作流主干保留**（合规/顺序硬约束） |
| 步内 ReAct | `empirical_agent` 有碎片；主 E2E 不靠它 | **只在开放步挂 ReAct**：文献检索、变量诊断、写作修订；**估计/REPRO 步仍走确定性 runner** |

**实现清单（NOW）：**

1. **统一轨迹格式**（JSONL）：每轮 `round` 写入 `state/runs/<id>/trajectory.jsonl`，字段至少 `role, reasoning?, content?, tool_calls?, tool_result?, step_id`。
2. **无 tool_result 禁止再调同工具**：框架层硬挡「盲目循环」（书消融结论 → 代码不变量）。
3. **max_tool_rounds / max_loop_rounds** 已有则接上；缺则默认：步内 12、环外 `max_rounds` 已存在。
4. **不要**把整篇论文塞进单次 ReAct 上下文；长任务用「初始化 Agent + 执行 Agent + handoff 产物」（Anthropic 长时模式，Ch1 末）。

```text
  [用户/课题] → full_pipeline step_i
                    │
         ┌──────────┴──────────┐
         │ 固定步：脚本/Stata   │  开放步：ReAct + tools
         │ 写 artifacts        │  读/读/改 → 写 artifacts
         └──────────┬──────────┘
                    ▼
              evaluate (程序门)
                    │ red → learn → target_steps
                    │ green → package
```

---

## 2. 规划：工作流 × 自主 = 混合（Ch1.2.5）

### 2.1 书中选择规则

- 单次 LLM 够用 → 不要 Agent。
- 路径可固定 → **Workflow**（节点顺序代码写死）。
- 路径动态、开放 → **Autonomous ReAct**。
- 成功实践多为**混合**：合规/金钱/不可逆用工作流；探索用自主。
- Agent 用延迟和成本换性能；预算无意识时加步数不涨分（Budget-Aware 研究）。

### 2.2 映射 10 步实证 spine

| 步类 | 例子 | 编排 | 原因 |
|------|------|------|------|
| 硬顺序 / 合规 | 数据闸门 → 识别 → 主估计 → REPRO | **纯 Workflow** | 乱序 = 假论文风险 |
| 半开放 | 文献、机制异质性设计 | Workflow 节点内 **有限 ReAct** | 需搜索与综合 |
| 开放修订 | 06_writing / 07_revision | ReAct + **proposer-reviewer** | 质量迭代；结果须绑 evidence |
| 门禁 | evaluate / integrity | **程序**，非 LLM 主裁判 | 反 Goodhart |

**现在实现：**

1. **Stage contract 保持**：每步 I/O 契约（已有 registry）= 工作流边；禁止「跳过 05 直接 06 且标绿」。
2. **LearnPlan.target_steps**（已有）= 图上的回边；learn 必须写清「预期灭掉的 verdict」（与 `00_SYNTHESIS_ACTION` 一致）。
3. **步骤预算**：L8 回炉时，rewrite_tail 给足轮次；数据/估计步 **少** 轮次、**禁止**「为写长而重跑估计」。
4. **过早完成检测**（书 proposer-reviewer / Loop）：`completed_green` 仅当 `ready_for_review + REPRO` 且无 blocking verdict（`continuous_loop` 已禁红灯绿——守住）。

---

## 3. 工具：手脚设计（Ch4）→ 实证工具集

### 3.1 五类工具（调用方向）

| 类 | 书定义 | 实证论文 NOW 工具 |
|----|--------|-------------------|
| 感知 | 读世界 | `read_results_json` · `read_table_csv` · `grep_manuscript` · `search_lit` · data diagnose |
| 执行 | 改世界 | `run_stata_do` / stats_engine · `write_section` · `write_claim` · `run_repro_script` |
| 协作 | 子 Agent / 人 | spawn lit-subagent；HITL 闸（设计审 / 高风险方法变更） |
| 用户沟通 | 进度 | run 事件 / UI 进度卡（已有 SSE 方向） |
| 事件 | 外触发 | **延后**（论文环以人启为主） |

### 3.2 通用原则 → 代码约束

1. **ACI**：命名=目标（`run_main_ols` 优于 `call_api_17`）；描述写「何时用 + **不能做什么**」；参数带真实例子。
2. **粒度**：同类合并（`read_document` 模式）；估计步 **专用工具**（审计/权限），探索步可用 `code_interpreter` 沙盒。
3. **通用 vs 专用**：pandas/Stata 清洗探索 → 通用沙盒；**写 Results/json、改 claim、发 bib** → 专用 + 可审计。
4. **参数保真**：禁止静默改路径/数字/引号（书 Cursor 弯引号反例）；工具返回必须是模型所见世界。
5. **返回自包含**：工具结果含「成功/失败 + 路径 + 摘要 + 如何读全文」；长输出 head/tail + 落盘路径（Ch4 执行工具）。
6. **执行后自动验证**：`write_file` 代码后跑 linter 的类比 → **`run_estimate` 后立刻 schema 校验 + 主系数 claim 链更新**；失败作为 tool_result 回轨迹。
7. **Skill + 少工具**：dont-lie / integrity-audit 用 progressive disclosure，不把 200 个 skill 平铺进 system。

### 3.3 提议者-审核者 & Sidecar（现在能落地的最小版）

| 机制 | 书用途 | 实证 NOW |
|------|--------|----------|
| 事前审批 | 不可逆高风险 | 改 design methods、覆盖主结果 JSON、删除 raw → **HITL 或第二模型** |
| 事后验证 | 跨模态检查 | 写完主结果段 → **程序**核对「正文数字 ⊆ Results/json」 |
| Sidecar | 只看结构化 tool call | `post_tool_audit`：拦截无 evidence 路径的「声称显著」 |

**红线：** 审核器输入 **隔离自由文本话术**（只看 tool name/args 或 claim 结构），防提示注入操纵门禁。

---

## 4. 多 Agent（Ch10）：何时上、怎么上

### 4.1 唯一有效判据

> **协作是否引入单 Agent 生成时得不到的新信息？**

- 同一模型自评改稿 → **通常无效/有害**。
- Reviewer 看 **测试执行 / 渲染 / 工具验证事实** → **显著有效**。
- 成本：Anthropic 多 Agent 研究约 **15× token**；收益不够大就别上。

### 4.2 上下文共享 vs 不共享

| | 共享轨迹 | 不共享 + 文件系统 |
|--|----------|-------------------|
| 适合 | 2–3 角色、信息零损硬需求 | 并行、窗口爆、隔离审查 |
| 实证默认 | **阶段角色切换**（设计→估计→写→审）可共享 handoff 摘要 | **integrity / REPRO 审阅** 不共享思考，只读 artifacts |
| 通信 | 隐式历史 | `workspace/` 产物路径 + progress.md + trajectory.jsonl |

### 4.3 拓扑选择（NOW）

```text
  推荐：管理者式「薄编排」
    continuous_loop / supervisor  = Manager（分配 target_steps、预算）
    full_pipeline step runners    = 专业子能力（多数仍是函数，不是完整 LLM Agent）
    integrity-audit / REPRO       = 带「新信息」的 Reviewer（程序优先）

  延后：去中心化 peer 辩论、A2A、Agent 社会
```

**文件系统四区（书 10.4.1）映射本仓：**

| 区 | 路径习惯 |
|----|----------|
| Scratch | `state/runs/<id>/scratch/` |
| Shared | `Results/` `Manuscripts/generated/` `evidence/` |
| External | `Data/Raw`（只读约束） |
| Built-in | `.claude/skills/` `workflows/` |

**并发：** 共享区写产物用原子写 / run 隔离目录；禁止多 Agent 同时改同一 `results.json` 无锁。

**子 Agent 返回：** 结构化摘要 + 路径，**不**回灌全量轨迹（隔离优于压缩，Ch2 结论）。

---

## 5. 评估（Ch6）：验证在 Harness 中的主权

### 5.1 评估对象

- 评的是 **Model + Harness**，不是裸模型。
- 区分瓶颈：**model swap**（固定 Harness 换模型）vs **消融**（关组件）。
- 本仓瓶颈当前更像 **Harness/门禁/证据链**，不是「再接一个聊天前端」。

### 5.2 环境类型 → 实证

| 书类型 | 实证对应 |
|--------|----------|
| ToolEnv / SandboxEnv | 跑 do-file / repro 脚本；**可执行验证器** |
| StatefulToolEnv | 写 Results 后状态可变；每次 run 可重置 |
| 人机交互 τ-bench | 课题澄清 UI（次优先）；**不是**主 fitness |

### 5.3 指标：过程 + 结果双覆盖

- **Outcome：** REPRO_OK、表数字存在、claim 链完整、设计⊆执行 methods。
- **Trajectory：** 是否跳过 integrity、是否无 tool_result 循环、是否编造 cite。
- **Pass^k 思维：** 稳定性（回归）用「多次绿」；探索上限用 Pass@k。发表级更要 **Pass^k 式可靠**。
- **Veto 维度（Rubric 四准则）：** 幻觉 / 假 bib / 数字无 evidence → **总分 0**，不与文采加权平均。

### 5.4 LLM-as-Judge：能用边界

书承认开放任务需要 Judge，但 **生产 fitness 不能只靠它**。

| 维度 | 程序门（NOW 主权） | LLM 辅评（可选、永不单飞） |
|------|-------------------|---------------------------|
| 数字/表 | JSON schema + 表对照 | — |
| 引用 verified | bib 字段硬线 | — |
| 章节过薄 | 长度/结构 gate | 可辅 |
| 论证流畅 | — | 可辅，**不抬 fitness 过绿线** |

与 `00_SYNTHESIS_ACTION` 对齐：**禁止 LLM-only grade；禁止红灯 completed_green。**

### 5.5 数据集设计原则 → 本仓 eval 包

1. **边界与陷阱用例**：设计含 IV 但只跑 OLS → 必须 `evidence_integrity_blocked`。
2. **可验证性**：像 SWE FAIL_TO_PASS / PASS_TO_PASS → 改表不重跑 FAIL；重跑后数字一致 PASS。
3. **verification_manifest v0**：主系数一条链 paper→table→JSON→script（行动清单 #7）。
4. **分层难度**：smoke 1 表；full 10 步；hostile 假 cite / 数字漂移。

---

## 6. NOW 实现板（按依赖，可观察完成）

```text
  P0  轨迹 JSONL + 无 tool_result 禁循环 + max rounds
  P0  工具返回：路径 + 摘要 + 错误可行动；估计后自动 schema
  P0  evaluate 主权：repro + quality + integrity；veto 幻觉/假 cite
  P0  strictly_better + rollback（mutable snapshot）— 与进化材料一致
  P1  步类型标注 workflow|react|hybrid；仅开放步挂 ReAct
  P1  post_tool_audit Sidecar（结构化 claim/args）
  P1  Reviewer = 程序执行反馈（REPRO/审计），禁止纯同模型互吹
  P2  薄 Manager 预算：target_steps + 步内 tool budget
  P2  子 Agent 仅 lit/检索隔离上下文；产物路径 handoff
  Later  事件驱动、MCP 大生态平铺、多 Agent 辩论、参数后训练
```

**怎样算 Wave2 收口（falsifiable）：**

1. 人造 `too_thin` / 断链数字包 → loop **不得** `completed_green`。
2. 故意丢掉 tool_result → 框架 **停止** 同工具空转（日志可见）。
3. `run_estimate` 成功但缺 claim 链 → evaluate **FAIL** 并 learn 回 05/06，而非只扩写。
4. integrity skill 只读 shared artifacts，不依赖写稿 Agent 的私有思考文本仍能否决假数字。

---

## 7. 与书公式的最终映射表

| 书概念 | 实证论文闭环落点 |
|--------|------------------|
| LLM Policy | Grok/MiniMax via `llm_client`；步内决策 |
| Observation | paper.yaml、Results、evidence、轨迹、状态栏式 run meta |
| Action Space | tool_adapters + stats + write + repro + audit |
| ReAct | 开放步内环；外环是 continuous_loop |
| Workflow | full_pipeline 10 步顺序 |
| Harness Constrain | 权限、Data 只读、红灯禁绿 |
| Harness Verify | evaluate / REPRO / integrity-audit |
| Harness Correct | learn → target_steps；rollback；halt_honest |
| Multi-Agent | 仅「新信息」Reviewer；薄 Manager；FS handoff |
| Eval 驱动迭代 | scoreboard only-accepted；禁止 LLM 刷分 |

---

## 8. 明确不做（书也支持延后）

- 把 10 步拆成对等辩论多 Agent（无新信息、烧 15× token）。
- 用 LLM-as-Judge 替代 REPRO/数字链。
- 为「更像论文」牺牲「更真」（与 integrity / dont-lie 冲突）。
- MCP 一次挂满上下文；应 Skills 索引 + 按需加载。
- 后训练写权重；默认 **Harness + 外部产物**（知识/指令/程序）更新。

---

## 9. 源页锚点（便于回查 PDF）

| 主题 | 约页 | 章节 |
|------|------|------|
| 公式 / 观察·动作空间 | 7–12 | 1.1 |
| ReAct / 轨迹 / 消融 | 13–16 | 1.1.4–1.1.5 |
| Harness / 工作流 vs 自主 | 17–23 | 1.2 |
| 工具分类与 ACI | 103–112 | 4.1–4.2 |
| 执行安全 / 双审 / Sidecar | 110–112 | 4.5 |
| 评估层次 / Verifiers / τ | 162–166 | 6.1–6.2 |
| 数据集 / 可验证 / 指标 | 167–171 | 6.3–6.4 |
| Rubric / Judge / Veto | 171–174 | 6.5 |
| 多 Agent 维度 / 新信息判据 | 277–280 | 10.1–10.2 |
| FS 四区 / 失败模式入口 | 284–287 | 10.4 |

---

## 10. 下一动作（单点）

**实现 P0 中尚未闭合的项：** 在 `continuous_loop` / tool 适配层保证「估计工具返回 → 自动 claim/schema 校验 → 失败进轨迹 → evaluate 可引用」；并补一条 **tool_result 缺失则熔断** 的单测（无 LLM）。  
完成后对照 §6 四条 falsifiable 检查，再开 P1 Sidecar。
