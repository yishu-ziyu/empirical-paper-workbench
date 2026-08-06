# Structure-Audit Materials · 行动合成清单

Date: 2026-08-06  
Sources: `materials/*.md`（evolution / penguin / AERS / awesome grafts / book / pdf）  
Scope: **现在做什么 vs 以后**；评价器设计；skill 嫁接优先级；反 Goodhart 红线  
Not: 功能 wishlist、UI、整仓 vendoring

---

## 0. 一句话

**现在只做：可版本化的 mutable 切片 + 程序化复合评分 + 严格接受/回滚 + Wave A 诚信门禁。**  
**不做：整套 OpenEvolve/Shinka/EvoAgentX、整 Awesome monorepo、用 LLM 自评刷绿、红灯 completed。**

```text
  目标环:  propose → run → evaluate → learn↻ → package
  材料共识:
    genome/state  = 可版本 mutable（稿/策略/notes）
    fitness       = 程序门禁复合分（repro + quality + 可选 latex）
    accept        = strictly_better；平局/降分 → rollback
    skills        = 薄清单进 gate，不 dump 全文
  红线:   不可用「更像论文」换「更真」
```

---

## 1. 现在 vs 以后

### 1.1 现在实现（Wave 0–A，结构债优先）

按依赖顺序，**做完才算本周/本 sprint 收口**。

| # | 做什么 | 落点（建议） | 怎样算完（可观察） |
|---|--------|--------------|-------------------|
| 1 | **复合 fitness 函数** | `runtime/evolution/score.py` 或先 `score_after_pipeline` 抽到共享模块 | 对既有 `*_full_pipeline_quality.json` fixture 出 `score/repro/quality/latex_pdf`；单测绿 |
| 2 | **Evaluate 主权** | 扩展 `evaluate_after_pipeline`：quality + REPRO + integrity；**红灯禁止 `completed_green`** | 人造 `too_thin` / `evidence_integrity_blocked` 包 → loop 不得标绿 |
| 3 | **Mutable slice + snapshot/rollback** | continuous_loop round 目录：`mutable_snapshot/` + version | reject 后草稿/notes **字节级**复原；单测无 LLM |
| 4 | **`strictly_better` + scoreboard only-accepted** | 写入 `ContinuousEmpiricalLoop` | 降质 accept 路径不存在；scoreboard 无 rejected |
| 5 | **LearnPlan 强制 hypothesis** | `learn.json`：预期灭掉的 verdict + 预期产物 | 缺字段拒绝 apply |
| 6 | **设计 ⊆ 执行 methods** | quality / integrity gate | IV 在 design、仅 OLS 跑 → `evidence_integrity_blocked` + 明确 repair task |
| 7 | **verification_manifest v0** | 主系数 claim 一条链 paper→table→JSON→script | 改表数字不重跑 → FAIL |
| 8 | **dont-lie 薄 skill** | `.claude/skills/dont-lie/SKILL.md`（≤120 行） | 主结果数字无 evidence 路径则拦 |
| 9 | **引用 verified 硬线** | lit/export：claimed cites 且 `verified=0` 不得 ready | 假 bib 不涨分（见 §4） |

**Evolve v0（可与 1–4 同周，但后于 score）：**

- `population_size=1` 的 custom OpenEvolve-style 环（**不** `pip install openevolve`）
- genome = 写策略 / 稿路径 / expand·degrade 开关
- dry-run：`max_generations=1`，只评分上一次 full_pipeline 包，不花 LLM 突变
- 档案：`state/runs/evolve/latest.json` + gen checkpoint

**与 L8 / H8：**

| | 现在 | 说明 |
|--|------|------|
| L8 单 run 回炉 | **必须接好** | evaluate→learn→target_steps→max_rounds；Penguin 五件套最小集 |
| H8 跨 run 进化 | 档案骨架即可 | scoreboard + best draft 路径；**不**自动写回 canonical Skill |

### 1.2 下一阶段（Wave B–C，L8 绿之后）

| # | 做什么 | 触发条件 |
|---|--------|----------|
| 10 | Manuscript outline→prose；econ-academic-writing skill | Wave A 诚信门已挡假数字 |
| 11 | Intro 幅度只绑 manifest PASS；否则 placeholder | 同上 |
| 12 | econometrics-check 4-phase + `strategy_memo.md` | method gate 有写入契约 |
| 13 | claim 级 REPRO / 10-check package 清单 | REPRO_OK 已稳 |
| 14 | AERS P0 grader 镜像 → `runtime/aers_eval/` | score 与 continuous_loop 已 SSOT |
| 15 | method_trap_* 码 → learn 回 **05** 不单扩写 | AERS scenarios grade 可跑 |
| 16 | Evolve `population_size>1` + 跨日 archive | 单 lineage score 可动且成本可控 |

### 1.3 以后再说（明确延后）

| 项 | 原因 |
|----|------|
| `pip install openevolve` 当产品环 | 论文 run 分钟级；genome 不是单文件快 bench |
| ShinkaEvolve | 仅当估计/replication 代码有**便宜 verifier** 时 |
| EvoAgentX 工作流拓扑进化 | 10 步 spine 仍是 SSOT；拓扑搜索 thrash 大 |
| 整 Awesome / AERS skills 拷仓 | 上下文爆炸；只拷 checklist + grader 闭包 |
| 生物医学配图配额 / 第二套 manuscript OS | 与实证发表与 L1 SSOT 冲突 |
| 后训练改权重 | 事实走 evidence/repro；默认 Harness |
| H7 大规模并行 multi-agent 产品面 | 真增益需独立 IO；成本 15× 量级；先把 evaluate 真 |
| LaTeX 全能 skill / 简历发票模板 | 仅 export 时 thin compile |
| 中英 de-aigc 全套 skill | Wave D；不挡诚信与 L8 |

### 1.4 决策表（材料对齐）

```text
  Now     custom score loop + Penguin accept/rollback + Wave A integrity
  Next    archive best drafts; AERS method traps in evaluate; writing skills
  Later   openevolve/shinka/evoagentx only if genome unit matches
  Never   LLM-only grade; fake cites as fitness; red completed_green
```

---

## 2. 评价器设计（evolution_landscape + penguin）

### 2.1 架构原则（必须变成代码不变量）

```text
                    ┌─ IMMUTABLE ─────────────────────────┐
                    │ estimates, tables, hashes, repro log │
                    │ traces, evaluate 输入快照            │
                    └──────────────────────────────────────┘
  Produce (writer)       Evaluate (scorer)        Search (optimizer)
  ───────────────        ─────────────────        ─────────────────
  只改 MUTABLE           程序 gate 为主            单 Candidate / 轮
  不见 rubric/Gold       私有规则不进写稿 prompt    有界 edit + 可证伪假设
  独立 run_id/路径       协议化分数 + 工件指针       accept iff strictly_better
                         失败≠质量 0（infra 另码）  else snapshot rollback
```

**Penguin 五件套 → 本仓：**

| 件 | 本仓最小形态 |
|----|--------------|
| Mutable object | 稿草稿、write plan、learn notes、policy 内 method 选择；`version` 仅 accepted ++ |
| Evaluator | `evaluate_after_pipeline` + integrity +（后）AERS；**无 LLM 独断 fitness** |
| Search | 一 LearnPlan / 轮；hypothesis；target_steps；禁止同时互扰大改 |
| Archive | `round_k/evaluate.json` + `learn.json` + snapshot；**scoreboard 仅 ACCEPTED** |
| Rollback | 改前 snapshot；reject 字节恢复；runtime freeze 变 → 矩阵无效 |

### 2.2 Fitness v0（OpenEvolve-style 复合分）

权重（可调，变更必须写 changelog 且 **不** 由 optimizer 改）：

| 分量 | 权重 | 来源 | 语义 |
|------|------|------|------|
| **repro** | 0.40 | step_09：`REPRO_OK` + 主结果系数对齐 | 0 或 1 |
| **quality** | 0.40 | quality JSON verdict | 映射 float |
| **latex_pdf** | 0.20 | paper.pdf 存在且 >1KB；或 tex 可编译 | 0 / 0.5 / 1；CI 不稳时可暂 `w_pdf=0` |

**Quality 映射：**

```text
ready_for_review（无 blocking）     → 1.00
仅 soft residual                   → 0.65
blocking 但 pipeline 跑完          → 0.35
pipeline 失败 / repro 失败          → 0.00
evidence_integrity_blocked         → 总分强制 0.00  （integrity floor）
```

Blocking 对齐 `continuous_loop.BLOCKING_VERDICTS`：  
`too_thin` · `missing_sections` · `section_length_gate_required` · `evidence_integrity_blocked` · `format_gate_required`  

Soft：`needs_literature_review` · `method_gate_required` · `needs_review_loop` · `evidence_integrity_needs_review`

**可选只记 log、不进 v0 标量：**  
`char_count`、`citation.verified_count`、`claim_bind_ok`、token/墙钟成本。  
**禁止**用 verified 假计数抬分（见 §4）。

### 2.3 Strictly better（接受门，字典序）

1. `completed_green` 优于一切非绿  
2. 否则：blocking 集合 **真子集缩小** 且无更高等级新阻塞  
3. 否则：复合 `score` 严格上升 **且** repro 不退化  
4. **平局 → reject**（防噪声爬升）

相对 Reference（最佳已接受 round），不是「感觉更好」。

### 2.4 AERS 并入 evaluate 的目标形态（接 Wave 后）

并集，任一类 hard red 禁绿：

| 系统 | 抓什么 |
|------|--------|
| paper_quality | 章节/长度/格式 |
| integrity_audit | 稿内数字 bind evidence |
| REPRO | 端到端复跑 |
| AERS harness | 方法陷阱叙述（weak-IV / TWFE / bad control…） |
| AERS benchmark | 数字 = 数据重算（仅 method profile 匹配时 enforce；否则 skip 不假绿） |

扩展 verdict 示例 → learn `target_steps`：  
`method_trap_*` → **含 `05_causal_analysis`**，不能只 rewrite 06–10。

### 2.5 评价器落地顺序（验收）

1. [ ] `score_after_pipeline` + fixture 单测  
2. [ ] continuous_loop：红灯 ≠ completed_green  
3. [ ] snapshot + strictly_better + scoreboard  
4. [ ] LearnPlan.hypothesis 必填  
5. [ ] dry-run evolve gen=1（只打分）  
6. [ ] （后）AERS P0 mirror + method 码进 learn  
7. [ ] （后）population / 跨 run archive = 真 H8 可见

**Falsifiers：**  
- 人为降质仍 accept  
- reject 后文件与 snapshot 不一致  
- scoreboard 含 rejected  
- 写稿上下文可读 gate 源码当「答案」  
- 分数行打不开 evaluate 工件路径  

---

## 3. Skill 嫁接优先级

### 3.1 总规则

```text
  优先级: integrity/numbers > ID-code align > lit verify > writing structure > latex package
  形态:   薄 SKILL.md + 必要 references；机制进 gate 代码
  加载:   progressive（按 pipeline step），禁止 49 包一次塞
  SSOT:   integrity-audit 保留并扩展，不平行第二套审计
```

### 3.2 分期清单（可勾选）

#### Wave A — 停 integrity 红（**现在**）

| 优先级 | Skill / 机制 | 来源 | 动作 |
|--------|--------------|------|------|
| P0 | **dont-lie** | 27 | 新建 `.claude/skills/dont-lie/SKILL.md` + 进 SOUL/agent 一行政策 |
| P0 | **design ⊆ executed methods** | graft/live red | gate 代码，非 skill  alone |
| P0 | **verification_manifest v0** | 27 paper_verification | `evidence/` + full_pipeline 写出主 claim |
| P0 | **citation verify / verified=0 block ready** | 04 + 41 + AERS citation-hygiene | lit step 或 `evidence/verify_citations.py` |
| P0 | integrity-audit 保留 | 已有 | post_tool hook 不拆 |

#### Wave B — 写厚但不编造（L8/诚信后）

| 优先级 | Skill / 机制 | 来源 |
|--------|--------------|------|
| P1 | econ-academic-writing（intro 蓝图 + claim→support→implication） | 27 + 04 two-stage |
| P1 | ManuscriptAgent outline→prose；禁 bullet 当终稿 | 04 |
| P1 | 因果动词 ↔ design 对齐 | 21 / 38 / academic_writing |
| P1 | chinese-de-aigc / en humanizer（按语种分流） | 48 / 44–45 |

#### Wave C — 计量 + package

| 优先级 | Skill / 机制 | 来源 |
|--------|--------------|------|
| P0–P1 | econometrics-check 4-phase + design_families | 41 |
| P1 | strategy_memo（method gate 产物） | 41 identify |
| P1 | audit-replication 10-check；claim 级 REPRO | 41 + 27 phase 6 |
| P1 | Mixtape / DID 11-step / pyfixest-ref（渐进） | 10 / 20 / 40 |
| P1 | AERS method scenarios 进 evaluate | auto_empirical |

#### Wave D — export 抛光

| 优先级 | Skill / 机制 | 来源 |
|--------|--------------|------|
| P2 | latex-compile 精简 + pdf→images QA | 08 |
| P2 | latex-tables booktabs | 09 |
| P2 | paper-excellence 聚合现有 quality JSON | 41 |
| P2 | peer-review-internal 报告形 | 04 |

### 3.3 Progressive 加载树（运行时）

```text
Always:     dont-lie
Intent:     econ-academic-writing（仅 outline）
Literature: lit-review-econ + validate-bib
Method:     econometrics-check + strategy_memo
Execution:  dont-lie + 真跑代码
Results:    paper-verification phases 2–3
Manuscript: writing two-stage
Review:     peer-review-internal + integrity-audit --all
Package:    audit-replication + latex-compile
```

### 3.4 明确不嫁接

- 整 Awesome 00–48 monorepo  
- 生物医学 graphical abstract / 强制 AI 配图  
- sewage 项目路径常量  
- 平行 `writing_outputs/` OS 顶替 full_pipeline  
- 口号 skill 不绑 gate（map ≠ territory）  
- 写作 agent 默认 `latex_compile` 全权限（export 专用 adapter）

---

## 4. Must-not · 反 Goodhart

Goodhart：当指标变成目标，它就不再是好指标。下列 **禁止用实现绕过**。

### 4.1 分数与接受

| 禁止 | 原因 |
|------|------|
| 用 LLM 自评代替 structured quality / REPRO / integrity | 可被话术刷分 |
| 红灯仍 `completed` / `completed_green` | 无接受门 = 无进化 |
| 平局/降分仍 accept | 噪声爬升 |
| rejected Candidate 进 scoreboard | 历史不可信 |
| optimizer 改 gate 阈值、改 gold 数据、改权重刷绿 | 改 Benchmark 当优化 |
| 失败记质量 0（infra crash） | 惩罚基础设施，扭曲搜索 |
| 无 snapshot 改草稿 | 无法诚实 rollback |
| 多 Candidate 同时改同一 State | 不可归因 |

### 4.2 诚信与证据

| 禁止 | 原因 |
|------|------|
| 为抬 `verified_count` 伪造 DOI/bib | integrity floor 必须 0 分 |
| 假 verified bibliography 进 fitness | 直接 reward 捏造 |
| OLS-only 跑却用因果动词涨「像 paper」分 | 语言-设计错位 |
| 字数/「像论文」主导 quality 而无 claim bind | 奖励灌水 → too_thin 假绿 |
| 表数字与 Results JSON 脱钩仍过门 | 表文谎言 |
| 评价器与写稿同上下文且可见 Gold | 污染；Penguin 规则：停 |

### 4.3 结构与范围

| 禁止 | 原因 |
|------|------|
| L8 与 H8 互相顶替「已经自进化」 | 审计硬线 |
| 再开平行 orchestrator 栈 | L1 SSOT |
| 整仓 Penguin monorepo / EvoAgentX 当外框 | thrash |
| 后训练背系数/文献 | 事实走 evidence |
| 训练题泄漏进 held-out 验收 | 假提升 |
| 无限并行 full pipeline 打爆成本/数据 | isolate run_id |

### 4.4 护栏指标（机制指标 ≠ 目标）

可记录、**不可单独作为 accept 主键**：

- 章节字数、expand 次数、skill 加载次数、token 消耗  
- LLM judge 文采分（若启用，仅 soft + 独立上下文 + 校准）

**唯一可接受的绿：**  
`ready_for_review` + REPRO（或诚实 degrade 已记录）+ 无 integrity/method blocking +（可选）manifest 主 claim PASS。

---

## 5. 可执行检查清单（本周剪裁）

复制到 issue/PR，逐项勾：

### A. 评价器 / L8 硬结构

- [ ] `score_after_pipeline` 存在且 fixture 测过  
- [ ] 复合权重与 quality 映射与本文 §2.2 一致（或文档 diff 说明）  
- [ ] integrity floor：`evidence_integrity_blocked` → score 0  
- [ ] continuous_loop 红灯不能 completed_green  
- [ ] mutable snapshot + reject 字节复原单测  
- [ ] `strictly_better` 实现并阻断降质 accept  
- [ ] scoreboard 仅 accepted；attempts 旁路  
- [ ] LearnPlan 含 hypothesis + 预期灭灯  
- [ ] loop_meta 记录 runtime freeze（模型/gate 版本/数据 hash）  
- [ ] evolve dry-run gen=1 写出 `state/runs/evolve/latest.json`  

### B. Wave A 诚信

- [ ] dont-lie skill 落盘且 ≤120 行  
- [ ] design methods ⊆ executed methods gate  
- [ ] verification_manifest v0 至少 1 条主 claim  
- [ ] claimed cites 且 verified=0 → 不得 ready  
- [ ] 改表数字不重跑 → 审计/manifest FAIL  

### C. 明确未做（避免假完成）

- [ ] **未** 安装 OpenEvolve/Shinka/EvoAgentX 当主环  
- [ ] **未** vendor 全 Awesome skills  
- [ ] **未** 用 LLM 独断 fitness  
- [ ] **未** 自动晋升 H8 Skill 到 canonical（无 canary）  
- [ ] **未** 宣称 H8 完成（仅有 L8 骨架也不算）  

---

## 6. 材料索引（读源不读本文件时）

| 主题 | 文件 |
|------|------|
| Fitness / OpenEvolve-style | `evolution_landscape.md` |
| Snapshot / accept / scoreboard | `penguin_harness.md` |
| AERS grader / method traps | `auto_empirical_skills.md` |
| Skill 优先级与 Wave | `awesome_skills_graft.md` + `awesome_skills_inventory.md` |
| Harness / eval Goodhart | `book_ch1-3.md` · `book_ch4-6.md` · `book_ch7-10.md` |
| 生产公式 / multi-agent 边界 | `pdf_agents_p1.md` · `pdf_agents_p2.md` · `pdf_agents_p3.md` |
| 结构 FAIL 总表 | `../01_FINAL_APPROVED.md` · `../02_L8_IMPLEMENTATION.md` |

---

## 7. 给实现者的收口句

**先让分数诚实、接受严格、回滚真实、诚信门挡住假文献和假系数；再谈写厚、方法 trap 机判和跨 run 档案。**  
任何「分涨了但 REPRO/integrity 更脏」的路径一律当回归失败，不当产品进步。
