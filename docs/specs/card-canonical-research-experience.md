# Card Canonical Research Experience

| 字段 | 值 |
| --- | --- |
| 文档 | Product spec |
| 日期 | 2026-09-06 |
| 状态 | Active |
| 产品 | `econpaper/` |
| 契约 | `docs/acceptance/card-canonical-research-experience.md` |
| 前置 | ADR-0013 / ADR-0014，Workbench v2 三份 closed 契约 |

econpaper 是 **AI-native empirical research workbench**。核心对象是 Research Project，不是 Paper。

Agent 寻找结论的脆弱点，而不是帮助研究者寻找显著性。

本规格是产品真相。实现路线、进度和证据写在 `docs/plans/2026-09-06-card-canonical-research-experience.md`。

---

## 1. 要证明什么

研究者可以从一个问题开始，经历真实判断、意外、比较、挑战和结论收缩，最后写出有证据边界的论文。

不是「上传数据 → 选择模型 → 自动写论文」。

循环：

Question → Expectation → Admissible Specification Space → real execution → Surprise → Diagnose → Challenge → Claim → Paper

Paper 是 Claim + Evidence + Decisions 的 render，不是第二份数字真相。

---

## 2. Canonical demo

命题：Does education increase earnings? / 教育是否提高工资？

数据：Card / Wooldridge teaching extract，N=3010。

| 字段 | 值 |
| --- | --- |
| Outcome | `lwage` |
| Treatment | `educ` |
| Instrument | `nearc4` |
| 必有列 | `exper`, `expersq`, `black`, `smsa`, `south` |
| 若 extract 含 34 列 | 再纳入 `smsa66` 与 `reg661`–`reg669` 作为 region 维度 |

数据不得进前端 mock。参考复现值只作验证 anchor，不是 UI 常量。

**Comparable full-controls spec**（34 列 extract；`reg669` 不进公式以免与其他 region dummy 共线）：

```
lwage ~ educ + exper + expersq + black + smsa + south + smsa66 + reg661 + … + reg668
lwage ~ (educ ~ nearc4) + exper + expersq + black + smsa + south + smsa66 + reg661 + … + reg668
```

本机 StatsPAI 实测（记录，不是 UI 常量）：

| 量 | 实测 | 公开 anchor |
| --- | --- | --- |
| OLS `educ` HC1 | 0.07469 | ≈ 0.0747 |
| IV/2SLS `educ` | 0.13150 | ≈ 0.1315 |
| first-stage F（同公式、同质方差） | 13.26 | |
| effective / HC1 partial F | 14.14 | ≈ 14.214 |

9 列建模子集上，无 region/`smsa66` 的短公式是 OLS ≈ 0.0740、IV ≈ 0.1323、无条件 `iv_diag` F ≈ 63.9。那不是 comparable spec。Evidence Lab 必须展示 **该 spec 的 partial / effective F**，禁止用无控制的 `iv_diag` 冒充 instrument strength。

允许因 covariance / 实现细节有可解释小差异；必须记录实际 formula / estimator / covariance。数字对不上时先查设定，不得改结果去贴 anchor。

### 数据 provenance

不把 CSV 再 vendoring 进 `frontend/public/`。

Boot 时后端 loader 按顺序取：

1. 环境变量 / 显式路径
2. StatsPAI sibling `papers/data_card1995.csv`（34 列教学 extract）
3. `statspai.datasets.card_1995(simulated=False)`（9 列建模子集，已随依赖分发）

写入 session 的 provenance 至少含：source、citation（Card 1995）、checksum、redistribution decision、extract_kind（`wooldridge_card_34` 或 `statspai_card_9`）。

Region / `smsa66` 规格仅在对应列存在时标为 admissible。9 列 extract 仍必须能跑通 OLS vs IV 主比较。

Citation：Card, D. (1995). Using Geographic Variation in College Proximity to Estimate the Return to Schooling.

Redistribution：econpaper 运行时从已有 StatsPAI 依赖加载，不在产品仓另发一份数据副本。StatsPAI 将原 extract 标为可再分发教学数据；本产品不独立主张新的数据版权。

Demo 必须标明 **teaching / reproduction case**，不得伪装成用户自己的研究。

---

## 3. 体验形态

不是 8 步向导。左侧仍是研究对象。Canonical journey 只是 Agent 在正确时刻引导注意力；用户随时可点 sidebar。

空桌一键：`Try a real study · Card`。

英文研究术语第一次出现可附短中文，例如 `Admissible Space（合理规格空间）`。不要把页面做成双语教科书。

---

## 4. 研究语义（用户看见的）

### Question / Estimand

确认五件事，不要一上来 20 个统计软件字段：

- Outcome
- Treatment
- 主要 causal threat（能力、家庭背景同时影响教育和收入）
- candidate identification（大学邻近 `nearc4` 作为工具变量）
- estimand（OLS：条件关联；IV：邻近大学边际上的局部因果回报）

Agent 短句：普通比较首先给出 association。若讨论 causal effect，需要处理同时影响教育和收入的因素。

### Expectation

第一次关键运行前，极低摩擦记录：

> I expect OLS to be positive. If ability creates upward bias, IV may be smaller.
> 预计 OLS 为正；如果能力造成向上偏误，IV 可能比 OLS 更小。

可编辑、可接受建议、confidence = low / medium / high。Backend-owned，有 decision history。不是聊天消息。

### Admissible Specification Space

第一版 6–12 个真正值得比较的 specification，禁止组合爆炸。Card 空间建议 ids（34 列时；缺列则该条 `admissible=false`）：

| id | method | experience | demographics | region |
| --- | --- | --- | --- | --- |
| `ols.quad.demo.region` | OLS | quad | black | south+smsa+smsa66+reg661–668 |
| `iv.quad.demo.region` | IV nearc4 | quad | black | 同上（comparable / 默认 canonical 候选） |
| `ols.linear.demo.region` | OLS | linear | black | 同上 |
| `iv.linear.demo.region` | IV nearc4 | linear | black | 同上 |
| `ols.quad.demo.noregion` | OLS | quad | black | south+smsa only |
| `iv.quad.demo.noregion` | IV nearc4 | quad | black | south+smsa only |
| `ols.quad.nodemo.region` | OLS | quad | none | full region |
| `iv.quad.nodemo.region` | IV nearc4 | quad | none | full region |

Canonical 默认候选：`iv.quad.demo.region`。主比较：`ols.quad.demo.region` vs `iv.quad.demo.region`。

每个 choice：semantic id、label、rationale、dimension、value、admissible status、user decision。

用户在看到比较结果前确认 `Freeze admissible space`。冻结后仍可改，但必须成为新的 decision event，并标记发生在结果揭晓前还是揭晓后。

AI 不得把所有可运行组合都称为合理。

---

## 5. 对象模型

Truth owner = 后端。不建新数据库。对象进既有 `ResearchSession.state` 的 `research_lab` blob，经 Snapshot / 专用 read model 投影。不把 LangGraph raw state 暴露给 UI。

`state.estimate` 仍是 **canonical estimate**（Workbench v2 契约不变）。

| 对象 | 作用 |
| --- | --- |
| `ResearchQuestion` | 命题、outcome、treatment、threat、identification、estimand |
| `Expectation` | 运行前预期 + confidence + 版本历史 |
| `SpecificationSpace` | 可纳入规格、冻结状态、揭晓前后标记 |
| `SpecificationDefinition` | 一条可运行设定（semantic id + 研究选择） |
| `SpecificationRun` | 一次真实执行的不可变结果 |
| `ResearchChallenge` | Next best challenge |
| `ClaimRecord` | Claim Ledger 一条主张 |
| `DecisionEvent` | 任何改变研究选择的用户决定 |

`SpecificationRun` 至少：spec id/version、exact choices、estimator、formula、covariance、analysis dataset identity、producer run、coef/se/p/n、diagnostics、status、provenance、created_at、relation ∈ {canonical, preview, exploratory}。

### Preview 不得偷改主研究状态

`preview` → 新的 immutable SpecificationRun。canonical spec、canonical `state.estimate`、Paper、Claim 都不自动变。

只有用户明确 `Promote to canonical` 才把该 run 写入 `state.estimate` 并记 decision。

实现铁律：preview 不得走 `run_prewrite` / `set_direction_and_outline`。新增 run kind `spec_run`，只调用既有 `agent.nodes.estimate` 的 OLS/IV 函数，把结果写进 `research_lab.specification_runs`。

`RunRepository.complete()` 按 key 做 compare-and-swap：worker 返回值里如果带顶层 `estimate`，就会覆盖 canonical。因此 `spec_run` 的 result **不得**包含顶层 `estimate` / `results` / `main_specification` / `body_chapters` / `claim`。lineage 写在 SpecificationRun 自己的字段里。这是 M2 的硬约束，M1 还没有 spec_run。

---

## 6. Read / write API

保持 `GET /sessions/{id}` 与 `GET /sessions/{id}/evidence` 向后兼容。Evidence 端点继续只描述 canonical estimate。

Snapshot 增量字段 `research`（可空）：

- `teaching_case`: `card_1995` \| null
- `question`
- `expectation`
- `specification_space`（status、frozen_at、revealed、definition ids）
- `canonical_spec_id`
- `next_challenge`
- `claim` 摘要

专用读模型 `GET /sessions/{id}/research`：完整 lab（space、runs、compare 输入、surprise、challenge、claim ledger）。

写命令（都走后端，带 decision event）：

| 命令 | 作用 |
| --- | --- |
| `POST /api/demos/card` | 空桌 boot：建 session、真实上传管道吃 Card extract、seed question / expectation 草稿 / 提议 space |
| `PUT .../research/expectation` | 编辑并版本化 expectation |
| `POST .../research/specification-space/freeze` | 冻结 admissible space |
| `POST .../research/specs/{id}/run` | 运行一条 spec；`mode=canonical\|preview` |
| `POST .../research/compare` | 两条 run 的 Δ 与 changed/unchanged choices |
| `POST .../research/preview/promote` | 提升为 canonical |
| `POST .../research/preview/revert` | 撤销提升 |
| `POST .../research/challenges/{id}/accept` | 接受 next challenge |
| `PUT .../research/claims/{id}` | 写入 / 批准 claim |

前端允许保存的仍只有 ADR-0013 R2：session id、短期 command 投递 key、UI 偏好。Expectation / space / runs / claim 一律从 snapshot 恢复。清前端存储不影响业务恢复。

---

## 7. Evidence Lab

不是很多张回归表。三层：

1. **Results space**：admissible specs 下系数分布。point、CI（可靠时）、selected/canonical、method grouping、hover/focus。用现有 SVG/Canvas/Tremor，不引新 chart 框架。
2. **Choice matrix**：每条 spec 改了什么（Method / Experience / Region / Demographics / Covariance）。
3. **Compare**：任两条。βA → βB、Δ abs、Δ %、changed / unchanged choices。重点是 Why did it move?

Card 必须能清楚比较 OLS vs IV，并把主变化解释为 identification strategy（识别策略）。

IV diagnostic 至少展示真实 first-stage strength（来自 identification / spec run diagnostics，不是文案编造）。

---

## 8. Surprise（确定性规则）

LLM 可以解释 surprise，不能生成 surprise。规则：

对当前 expectation 与已完成的 canonical/admissible runs：

1. **direction mismatch**：某方法的期望符号与观测符号相反。
2. **ordering mismatch**：期望「IV 小于 OLS」而观测 IV > OLS（或相反）。容差：相对差 `|βIV − βOLS| / max(|βOLS|, 1e-6) > 0.05` 才算顺序成立。
3. **magnitude**：用户给出了量级/「大致相当」，且相对差 > 0.25。

Card 默认 expectation 触发 ordering mismatch（ability-upward-bias 故事 vs 观测 IV > OLS）。UI 克制显示 `Unexpected`，列出 Expected / Observed，不自动继续。

---

## 9. Challenge（第一版）

只生成 **Next best challenge**。允许 deterministic / scripted。不接 LLM，不做自主科学家。

Card 顺序：

1. instrument strength（first-stage）
2. experience functional form
3. demographic controls
4. region controls（列存在时）

字段：id、target assumption/choice、rationale、proposed specification change、expected information gain reason、status、resulting run(s)。

---

## 10. Agent Cursor

交互机制，不是独立产品。第一版 scripted，不接 LLM。

铁律：Agent 只能操作 semantic product targets。禁止坐标、CSS selector、XPath。

薄层 `SemanticTargetRegistry`：组件注册 semantic id → DOM/ref。Cursor layer 挂在 Workbench Shell 上，不进 EvidenceView 内部。

允许的 primitives：

| primitive | 权限 | 效果 |
| --- | --- | --- |
| `point(target)` | Point | 指向/高亮，不改研究状态 |
| `compare(a, b)` | Point | 高亮并打开已有 compare |
| `preview(command)` | Demonstrate | 进入 Preview proposal，不改 canonical |
| `runPreview()` | Demonstrate | 后端真实 `spec_run` |
| `promote()` | Act | 仅用户确认后走 promote 命令 |
| `cancel()` | — | 立刻退出当前 presentation |

本阶段重点 Point + Demonstrate。大规模自主 Act 不做。

Cursor：项目已有 `motion`，transform 移动，不每帧 React rerender，不引 GSAP。`pointer-events: none`，不伪装系统鼠标，有 Agent 身份，intent label 极短。target 缺失 graceful abort。resize/scroll 后重定位。`prefers-reduced-motion` 降级。用户 pointer/keyboard 开始时 pause / yield。

两条 Card script：

1. Show me：OLS point → IV point → Compare Δ → 指向 estimator choice，unchanged 淡化，intent `Identification strategy changed`，收束。
2. Challenge experience：point Experience → preview linear↔quadratic → 用户确认 Run Preview → 真实执行 → 比较；变化小时 `Little changed`。

---

## 11. Claim Ledger → Paper

Claim 是写作输入契约，不是 LLM 先写再检查。

Card 最少一条真实 Claim：

- Supported：`Education is positively associated with earnings.`
- Conditionally supported：`Under the college-proximity IV assumptions, IV estimates suggest a positive local causal return to schooling.`
- Unsupported：`One more year of education raises everyone's wage by 13%.`

字段：claim text、type、supported / conditionally supported / unsupported wording、supporting runs、counter-evidence、sensitive dimensions、unresolved assumptions、evidence status、approved_by_user、version、provenance links。

用户明确批准后，Results 章消费该 Claim + SpecificationRun 数字。关键句/数字可回跳 Claim / Evidence。措辞超过证据边界不得标 grounded。canonical spec / claim 变更后旧正文标 stale / needs regeneration。既有章节 approve/edit/rollback 保持可用。不重写六章系统。

---

## 12. 视觉

沿用 ADR-0014 与 `docs/specs/design-sources.md`：专业研究工具，workspace first，一个时刻最多一个重要 challenge，无 card soup，无大段 AI 总结占中心，无聊天头像满屏跑，无大面积 glass / glow / particles。Desk / Guide 定稿风格不重做。

---

## 13. 必须保留 / 禁止

保留：backend truth owner、Snapshot 恢复、immutable evidence artifacts、exact producer provenance、真实统计执行、失败显式、Results 写作门、Workbench shell、ResizableWorkspace、Motion、auth/export/chapter。

禁止：前端 hardcode 系数、frontend-only spec space、preview 覆盖 canonical estimate、`latest run` heuristic provenance、Cursor 像素 API、LLM selector、UI 假成功、为 demo 另做一套研究引擎、重写 StatsPAI、全仓设计系统 migration、新 Agent framework、大规模 multi-agent 科研、38 methods UI、specification 组合爆炸。

---

## 14. 里程碑

1. Research objects + Card demo boot（含 freeze，不含 Cursor）
2. Specification space + 真实 multi-run Evidence Lab + Surprise + Challenge
3. Agent Cursor Point / Compare / Preview spike
4. Claim Ledger → grounded Paper
5. 空桌到 grounded paper 的浏览器全程 + 证据包 + ADR 0015
