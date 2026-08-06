# 书精读材料：评估 · Skills · 记忆 · 多 Agent · 持续进化（按主题映射 ch6/2/3/10/8/1）

来源根：`/Users/mahaoxuan/Desktop/AI产品经理/ai-agent-book`  
正文 SSOT：`book/chapter{1,2,3,6,8,10}.md`  
产品对象：`/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板` Continuous Loop  
原则：**不发明**；章号与文件名不一致时按主题映射（见 §0）。

---

## 0. 顶层结构与路径映射（事实）

### 0.1 仓库顶层（读时所见）

| 路径 | 内容 |
|------|------|
| `README.md` | 全书入口：10 章 · 95 实验 · 公式 **Agent = LLM + 上下文 + 工具** |
| `book/` | 中文正文：`chapter1.md`…`chapter10.md` + `introduction.md` + `afterword.md` |
| `book-en/` 等 | 多语言译本（可能滞后） |
| `chapter1/`…`chapter10/` | 配套实验代码 |
| `docs/` | 学习建议 / 实验状态 / i18n README；**无**独立设计原则长文 |

### 0.2 缺失文件（勿脑补）

- **`docs/agent-design-principles.md` 不存在**（本仓库 `docs/` 仅有 LEARNING、EXPERIMENT_*、i18n 等）。  
- **Harness / Agent 定义**落在 `book/chapter1.md` §「Harness 工程」与 README 公式，而非单独 principles 文件。  
- **全书仅 10 章，无 ch11–15**。本文件文件名 `book_ch11-15_or_eval` 表示「后半能力带 / 评估与进化主题包」，**按主题映射**如下：

| 用户关心的主题 | 真实章 | 正文路径 |
|----------------|--------|----------|
| Agent = Model+Harness；Loop 工程 | ch1 | `book/chapter1.md` |
| Skills 渐进披露；上下文工程 | ch2 | `book/chapter2.md` |
| 用户记忆 / 知识库 | ch3 | `book/chapter3.md` |
| **评估 / Judge / Rubric** | **ch6** | `book/chapter6.md` |
| **持续进化 / 评价器可信根** | **ch8** | `book/chapter8.md` |
| **多 Agent** | **ch10** | `book/chapter10.md` |

已有并行材料：`book_ch1-3.md`、`book_ch4-6.md`、`book_ch7-10.md`。本文件专收 **对 Continuous Loop 可执行的规则 + 直接可挂到 runtime 的 graft**，不重复全章流水账。

### 0.3 与产品的一句话对齐

```text
Demo:   Agent = LLM + 上下文 + 工具
Prod:   Agent = Model + Harness
Harness = 上下文 + 工具 + 约束 + 验证 + 纠正
Loop:   在线执行(记录证据) ∥ 离线进化(候选→验证→发布)   ← ch8 双环
论文台: design → estimate → write → reproduce → revise↻
                 evaluate ──learn──┘   SSOT: runtime/continuous_loop.py
```

产品侧已有摘要：`docs/BOOK_HARNESS.md`（与本书一致，不替代正文引用）。

---

## 1. What is an Agent：Model + Harness

### 1.1 双公式（必须同时记住）

**组成视角（Demo / 内部）：**

> **Agent = LLM + 上下文 + 工具**  
> 路径：`book/chapter1.md` §「现代 Agent = LLM + 上下文 + 工具」；`README.md` 开篇同式。

- LLM = 大脑；上下文 = 眼睛（决策点可见的全部信息）；工具 = 手脚（可做之事，含 Skills / 子 Agent / 事件）。

**工程视角（生产）：**

> **Agent = LLM + [上下文 + 工具 + 约束 + 验证 + 纠正] = Model + Harness**  
> 路径：`book/chapter1.md` 约 L250–L256。

| Harness 功能 | 职责（书） | 论文 Continuous Loop 落点 |
|--------------|------------|---------------------------|
| Context | 感知信息 | design/variables/表路径/证据指针注入；Skills 元数据 |
| Tools | 行动手段 | Stata/读写稿/复现脚本；`run_continuous_loop` 工具 |
| Constrain | 能/不能做 | 无证据 claim 否决；路径白名单；因果 claim 纪律 |
| Verify | 结果对错 | quality gate · citation · REPRO · integrity |
| Correct | 修正/回退 | learn 的 rewrite/degrade/halt；max_rounds 熔断 |

书明确：最小公式能跑 Demo；生产必须补全约束/验证/纠正。同一模型有无 Harness 结果天壤之别（退款示例，`chapter1.md` L260）。

### 1.2 竞争力与 Loop

> 「行业正在从『能做事』向『可靠地做事』转变，Harness 工程因此成为 Agent 系统的核心竞争力。」  
> — `book/chapter1.md` L286

工程范式链：提示工程 ⊂ 上下文工程 ⊂ Harness 工程 ⊂ **Loop 工程**（跨轮：谁发现下一件事、何时验证、何时算完成）。  
— `book/chapter1.md` L288–L298

**可操作规则：**

1. 评测/迭代对象是 **Model+Harness 组合**，不是裸模型（ch6 开篇同义）。  
2. 「完成」由 **环境状态 + 门禁** 裁定，不是模型自称 done。  
3. 长任务：初始化 vs 执行、交接产物、防过早宣称完成（ch1 表：Anthropic 长时 Agent 实践）。

---

## 2. Evaluator：不能自评过门

### 2.1 评估对象与归因（ch6）

> 「评估的对象不应只是模型，而应是模型与 Harness 的组合体。」  
> — `book/chapter6.md` 开篇段（约 L15）

手段：

- **消融**：关 Harness 某组件 → 定位部件。  
- **模型替换（model swap）**：固定 Harness 换模型 → 瓶颈在模型还是 Harness。

### 2.2 结果 vs 过程；轨迹 vs outcome

> 结果正确不代表过程正确（删失败用例也能「通过」）。  
> — `book/chapter8.md` L23；`book/chapter6.md` L268–L269（trajectory vs outcome）

三层验证（**越下层越应代码/环境真值**）：

| 层 | 问题 | 书路径 | 论文台 |
|----|------|--------|--------|
| 结果 | 是否真的办成 | ch8 图8-2 / L27 | REPRO 绿；表 JSON 存在且可重跑 |
| 过程 | 是否以允许方式办成 | 同上 | integrity / claim 证据链 / 禁止改测试式假绿 |
| 质量 | 是否办得合适 | Rubric + 证据轮次 | paper 结构、诚实因果表述 |

> 「验证器负责给出评价和证据，至于应修改 Agent 的哪个部分，则应由**独立的**诊断与进化模块决定，避免同一个模型既当裁判又直接改写规则。」  
> — `book/chapter8.md` L49

### 2.3 Rubric 四准则 + 否决（ch6）— 反自夸

路径：`book/chapter6.md` L289–L341（Scale AI “Rubrics as Rewards”）。

1. **基于专家指导** — 领域真事实与推理步骤，非「流畅度」。  
2. **全面覆盖** — 含 **陷阱（Pitfall）**。  
3. **权重 + 一票否决（Veto）** — 幻觉等否决项：其他满分也归零。  
4. **自包含评估** — 禁止「展示了深刻理解」；改为可验证行为描述。

额外：

- 长度偏差 / 关键词堆砌 / 讨好用户 = **Reward Hacking** 必在 Rubric 中惩罚。  
- **同源模型问题**：Agent 与 Judge 同家族会共盲点；缓解 = 多源异构评判（`chapter6.md` L380–L388）。  
- **Goodhart**：指标一旦成优化目标即失效 — 同段。

### 2.4 「自评」在书中的具体禁止形态

| 禁止 | 书证 | 对 Loop 的硬规则 |
|------|------|------------------|
| 模型自我审查同一输出当「多 Agent」 | ch10 表10-2：通常无效甚至有害 | 不可用「我再读一遍自己的 paper」当 claim audit |
| 只看最终回复不看工具状态 | ch8 L45 承诺—行动一致性 | 「已复现」必须有脚本/报告/退出码，非散文 |
| 模糊总分掩盖否决项 | ch8 实验 8-1：高总分不能掩盖隐私/规则失败 | `evidence_integrity_blocked` → quality 与总分强制 0 |
| 验证器被业务 Agent 改掉 | ch8 L295：安全机制不可自我修改 | `evolve_evaluator` / 门禁代码不在可 mutate 面 |
| 用 Pass@k 当回归稳定性 | ch6 表6-3 | 课程论文包验收看「每次绿」类硬门槛，不是「五次里成功一次」 |

### 2.5 开放科研的额外警告（ch8）

> Harness 可能把流程跑得很完整，却只稳定产出「像成果的东西」。  
> — `book/chapter8.md` L272–L274

处方（同节）：结论与证据分离；保留负面结果；搜索多样性；人在高层定义评价标准与何时停。

**论文台直译：** 字数/章节齐全 ≠ 可复现与 claim 真值；`substance` 分量权重不得压过 `repro`+`integrity`。

---

## 3. Skills 渐进披露（ch2）

路径：`book/chapter2.md` §「动态提示词与 Agent Skills」（约 L708–L769）。

### 3.1 三层

| 层 | 内容 | Token 意图 |
|----|------|------------|
| L1 元数据 | `SKILL.md` frontmatter：`name` + `description` | 启动注入目录，仅数百 token |
| L2 核心流程 | 判定需要时用 Skill 工具加载完整 `SKILL.md` | 进入轨迹 tool result |
| L3 资源 | 脚本/模板/样例按需再读 | 不全量预载 |

> 「不是把所有知识一次性塞给 Agent，而是让它按需加载。」  
> — `book/chapter2.md` L717

> Skills 采用**渐进式披露（Progressive Disclosure）**——先给目录摘要，需要时再加载完整内容。  
> — `book/chapter2.md` L721

生产实现要点（方式三，Claude Code 类）：**路由与执行分离**；元数据可见 ≠ 全文可见；完整 schema/Skill 追加到上下文末尾以保 KV Cache（L749–L753；工具侧同理 L646）。

### 3.2 安全

Skill = 「把外部内容当指令加载」的制度化形式；来源不明 Skill 须审查（`chapter2.md` L687）。

### 3.3 与进化的衔接（ch8）

Skill 候选须含：何时加载、前置条件、步骤、陷阱、验证方法、来源轨迹；优先 patch 已有 Skill，防库膨胀（`chapter8.md` L128）。  
发布门槛：边界集改善 + 保留集不退化 → 仅 `release_to_canary`，不直接覆盖稳定版（实验 8-3）。

**论文台规则：**

- 识别/估计/写作/复现/ integrity 技能 → **L1 注册表常驻，L2 按阶段加载**。  
- 禁止把全部 empirical skills 全文塞进 system prompt。  
- 新 Skill 只进候选区，经门禁与 held-out 后再「正式」。

---

## 4. Memory（ch3）— 与「学习」区分

路径：`book/chapter3.md`；对比 `book/chapter8.md` L7–L8。

| 概念 | 书义 | 论文台 |
|------|------|--------|
| 轨迹 Trajectory | 单次 append-only 原始记录 | `state/runs/continuous_loop_*/`、step 日志 |
| 用户长期记忆 | 跨会话偏好/事实卡片 | 项目级 paper.yaml / lessons（非每轮改权重） |
| 经验学习（ch8） | 评价→对照→归纳→验证后的行动策略 | learn 产物：expand flags、降级 claim、候选规则 |

> 「保存经历不等于从经历中学习。」  
> — `book/chapter8.md` L7

记忆评估三层次：基础回忆 → 多会话消歧 → 主动服务（`chapter3.md` L62–L66）。  
Judge 仍应用 Rubric + 幻觉否决（实验 3-1 / 6-3）。

**规则：** 原始对话/网页 ≠ 可写入 Skill 的指令；先总结再候选再审（ch8 安全边界 L291）。

---

## 5. Multi-Agent（ch10）— 真协作 vs 剧场

路径：`book/chapter10.md` L71–L98。

**唯一核心判据：**

> 协作过程是否引入了**单个 Agent 在生成时无法获得的新信息**？  
> — `book/chapter10.md` L73

| 模式 | 新信息？ | 效果（书） |
|------|----------|------------|
| 同一模型自我审查自己的输出 | 否 | 通常无效甚至有害 |
| 不同 Agent 辩论同一段文本 | 否 | 等算力下与单 Agent 持平 |
| Reviewer + 测试/截图/外部工具 | 是 | 显著提升 |

成本：Anthropic 披露多 Agent 研究系统 token ≈ 普通对话 **15×**（`chapter10.md` L98）→ 无新信息则不要加角色。

拓扑维度：共享上下文 vs 不共享；对等 / 管理者 / 去中心化（不共享时才有硬架构决策）。

**论文台规则：**

- 真多 Agent = **独立 IO + 外部验证**（Stata 退出码、表 hash、claim audit 读 evidence 库）。  
- 成文 Agent 与 integrity/claim audit **不共享「请自评通过」的上下文**；审核者只看产物与证据。  
- 禁止 persona 剧场（「你是严格审稿人」却无工具无门禁）。

---

## 6. 持续进化双环（ch8）→ Continuous Loop 骨架

> 在线执行循环只完成任务并记录证据，**不直接改写**正式 Agent；离线进化循环聚合轨迹、诊断、生成候选、验证门槛后发布。  
> — `book/chapter8.md` L231

> 持续进化的起点不是「总结」，而是「评价」。  
> — `book/chapter8.md` L21

可信根三道边界（`chapter8.md` L289–L295）：

1. 证据与指令隔离  
2. 候选能力与正式能力隔离  
3. **安全机制不可自我修改**（验证器、测试、发布门槛、审计日志、稳定备份）

分层评估指标（表8-3）：候选修改有效率 / 产物激活率 / 遵循成功率 / 留出任务增益 — **不能只用端到端总分反推更新器好坏**。

---

## 7. 对 `runtime/continuous_loop.py` 的具体 Graft

文件现状（已实现，与书对齐处）：

- 外环：`propose→run→evaluate→learn↻→package`（模块 docstring L1–L6）  
- `BLOCKING_VERDICTS` / `SOFT_VERDICTS`；`has_blocking_quality` 禁止 `completed_green`（L109–L117, L349–L357）  
- `evaluate_after_pipeline`：quality + citation + REPRO 步骤（L120–L165）  
- `build_learn_plan`：映射 next_action + `target_steps`（L168–L246）  
- `_score_and_archive` 调用 `evolve_evaluator`（L322–L346）

### 7.1 应保持的硬不变量（书 → 代码）

| ID | 规则 | 书锚点 | 代码锚点 |
|----|------|--------|----------|
| CL-1 | 有 blocking 时永不 `completed_green` | ch8 结果/过程；ch1 验证 | `has_blocking_quality` + `_package` 降级 |
| CL-2 | evaluate 输出多维诊断，非模糊总分 | ch8 L47；ch6 Rubric | `evaluate_after_pipeline` 返回 blocking/soft/repro_ok |
| CL-3 | learn 落到 target_steps，非「论文质量差」一句 | ch7/ch8 信用分配精神 | `LearnPlan.target_steps` + `REWRITE_TAIL` |
| CL-4 | max_rounds 熔断 → `halt_honest` | ch1 熔断器；ch5 停止条件 | `build_learn_plan` round_i≥max_rounds |
| CL-5 | 硬步骤失败（数据/估计/复现）不无限 rewrite 糊弄 | ch8 环境真值 | failed_steps ∩ {04,05,09} → halt_honest |
| CL-6 | Pi/LLM assist 只改稿，不改门禁与 score 定义 | ch8 L295 不可自改验证器 | assist 写 paper；score 走 `score_package` |

### 7.2 建议增量 Graft（尚未完备时按此做）

1. **每轮落盘结构化评价 artifact**  
   - 已有方向：`round_*_evaluate.json` / `round_*_learn.json`（见 `docs/TRY_CONTINUOUS_LOOP.md`）。  
   - 书要求：维度 + **证据指针**（文件路径、step_id、claim id），不确定时显式 `uncertain`（ch8 L25）。

2. **evaluate 与 revise 模型分离（可选但书推荐）**  
   - 写稿/扩写 provider ≠ Judge/审计 provider（ch6 多源；ch8 独立诊断模块）。  
   - 实现：`ContinuousEmpiricalLoop` 增加 `judge_provider_id`，仅 quality/citation LLM 路径使用；确定性门禁仍优先代码。

3. **三层信号显式字段**  
   ```text
   evaluation = {
     result: {repro_ok, main_results_hash?, exit_codes},
     process: {blocking, integrity_*, citation_status},
     quality: {verdict, rubric_dims?},
     is_green
   }
   ```  
   下层失败时上层分数不参与「绿」判定（ch8 图8-2）。

4. **held-out / 种子题隔离**  
   - demo slug 不可泄漏进「进化验收」题集（ch6 L234；ch8 实验 8-2 学习集≠迁移集）。  
   - Loop 配置：`eval_slug_set` 与 `train_or_demo_slug_set` 分离字段。

5. **负面结果同等可检索**  
   - `halted_honest` / 失败 round 写入与 green 同级 index（ch8 L281），供离线睡眠学习，避免只学幸存路径。

6. **预算意识**  
   - max_rounds 外增加 token/墙钟预算；耗尽 → halt 并打包诚实降级（ch10 预算意识；ch6 预算—能力曲线）。

---

## 8. 对 `runtime/evolve_evaluator.py` 的具体 Graft

文件现状（已实现）：

- docstring：`cannot bluff past numeric gates`；mutable = 写作/expand/latex 参数，**非**门禁本身（L1–L5）  
- `score_package`：repro / quality / substance / latex_pdf / honesty / loop_status 加权  
- **integrity_floor**：`evidence_integrity_blocked` → quality=0 且 total=0（L97–L100, L177–L183）  
- `maybe_update_best`：仅当分数更高更新 `state/evolve_archive/best.json` + history.jsonl

### 8.1 已与书对齐的点

| 点 | 书 | 代码 |
|----|-----|------|
| 程序化分数，防口头自夸 | ch6 可执行验证；ch8 环境真值 | 读文件/JSON/REPRO 标记，非 LLM 自评 |
| 否决项压倒「像论文」 | ch6 Veto；ch8 高分不掩规则失败 | integrity_floor total=0 |
| 档案 best + history | ch8 候选/正式隔离雏形 | `maybe_update_best` |
| honesty 降权过因果表述 | ch8 认识论过度乐观 | causal 词启发式 |

### 8.2 建议增量 Graft

1. **评分器代码权限**  
   - 任何「进化写文件」白名单 **排除** `runtime/evolve_evaluator.py`、quality gate 脚本、`BLOCKING_VERDICTS` 定义处（ch8 第三道边界）。  
   - 可测：试图 patch 评分器的 candidate → 自动 `reject_candidate`。

2. **组件级证据表**  
   - `PackageScore.notes` 扩为 `evidence: [{component, path, predicate, pass}]`，满足 ch8「结构化诊断 + 证据位置」。

3. **拆开「更新有效」vs「激活有效」**（表8-3）  
   - 若未来写入 Skill/规则：分别记录 `candidate_accepted`、`skill_loaded_in_run`、`followed`；禁止只报总分上涨。

4. **反 Goodhart：substance 上限**  
   - 书：长度偏差（ch6 L285）。  
   - Graft：`substance` 达 1.0 后不再加分；或 `total` 在 `repro<0.85` 时 cap（例如 ≤40），防止「万字无复现」赢 archive。

5. **校准集钩子**  
   - 小批专家标轨迹上测评分器一致性后再放量（ch6 L273；ch8 L49）。  
   - 函数：`calibrate_score_package(golden_dir) -> kappa_or_agreement`，CI 可跑离线。

6. **回滚指针**  
   - `best_pointers.json` 旁维护 `previous_best.json`；指标恶化时一键回滚（ch8 L247）。

7. **禁止用 loop_status 刷分闭环**  
   - 现状 `loop_status` 权重 5：可接受为弱 bonus。  
   - 书警告：完成≠进步（ch8 L272）。  
   - Graft：`completed_green` bonus 仅在 `repro≥0.85` 且无 integrity_floor 时生效（双重门）。

---

## 9. 可验收检查清单（structure-audit 用）

- [ ] 文档与代码中 Agent 定义同时含 **Model+Harness**，非仅「有个 LLM 聊天」。  
- [ ] 绿包条件：REPRO + 无 blocking + 非模型自称；blocking 时不得 `completed_green`。  
- [ ] Judge/评分：**代码优先**；LLM Judge 若有则异构/校准；**无**「作者模型打自己 100 分」。  
- [ ] Skills：**元数据目录 + 按需全文**；无启动全量灌入。  
- [ ] 多 Agent 仅在有 **执行/检索/独立审阅工具反馈** 时启用。  
- [ ] 进化：候选≠正式；验证器不可被业务轨迹改写。  
- [ ] 轨迹不可变落盘；学习信号来自评价后的归纳，非 raw log 直写规则。  
- [ ] integrity / 幻觉类否决可把总分打到 0。

---

## 10. 关键原句索引（便于跳转）

| 主题 | 原句摘要 | 文件 |
|------|----------|------|
| 双公式 | Agent = Model + Harness；五功能表 | `book/chapter1.md` L250–L272 |
| Loop 工程 | 跨轮：下一件事 / 验证 / 完成 | `book/chapter1.md` L292 |
| 评估对象 | 评 Model+Harness 组合体 | `book/chapter6.md` L15 |
| Rubric 四准则 + Veto | 专家/覆盖/权重否决/自包含 | `book/chapter6.md` L289–L297 |
| Goodhart / 同源 Judge | 度量变目标即失效；多源异构 | `book/chapter6.md` L380–L388 |
| Skills 渐进披露 | 目录 → 按需 SKILL.md | `book/chapter2.md` L717–L729 |
| 保存≠学习 | 轨迹入库≠学会 | `book/chapter8.md` L7 |
| 评价起点 | 进化始于评价非总结 | `book/chapter8.md` L21 |
| 三层验证 | 结果/过程/质量 | `book/chapter8.md` L27 |
| 裁判≠改写者 | 验证器与进化模块分离 | `book/chapter8.md` L49 |
| 双循环 | 在线不改正式；离线候选发布 | `book/chapter8.md` L231 |
| 不可自改验证器 | 第三道安全边界 | `book/chapter8.md` L295 |
| 多 Agent 新信息判据 | 自审/同文辩论无效 | `book/chapter10.md` L73–L86 |
| 产品侧摘要 | 同式 + 反模式 | `docs/BOOK_HARNESS.md` |

---

## 11. 与已有材料的边界

| 文件 | 覆盖 | 本文件增量 |
|------|------|------------|
| `book_ch1-3.md` | 公式、context、memory 全量摘 | 仅可执行规则 + Loop graft |
| `book_ch4-6.md` | ACI + 评估 must-exist 表 | Rubric/否决/反自评 → evaluator 代码级 |
| `book_ch7-10.md` | 后训练、进化、多 Agent 综述 | 收束到 continuous_loop / evolve_evaluator 补丁清单 |
| `docs/agent-design-principles.md` | **不存在** | 以 `chapter1` Harness 节为 SSOT |

---

*读毕条件：本文件 ≥80 行；引用均可在上述绝对路径下的 `book/chapter*.md` 中定位；无 ch11–15 正文可引。*
)
