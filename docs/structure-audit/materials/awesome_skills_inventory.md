# Awesome-Agent-Skills 嫁接清单（empirical-paper-workbench）

> 源仓：`/Users/mahaoxuan/Desktop/经济学论文/Awesome-Agent-Skills-for-Empirical-Research`  
> 目标：`实证论文项目模板` / empirical-paper-workbench  
> 范围：LaTeX · 写作 · 因果 · 验证（verify）  
> 抽样日期：2026-08-06  
> 方法：通读源仓 README；枚举 `skills/00`–`48`；对有 `SKILL.md` / 顶层 README 的包做抽样精读

---

## 1. 一句结论

源仓本地收录 **49 个 skill 包（00–48）**，是实证研究全流程的「方法论操作手册」索引，不是可直接整仓依赖的 runtime。

workbench **已有**：StatsPAI 工作流编排、`integrity-audit`（6 维反捏造）、claim register、reproduction_verify 适配器、写作/复现子代理骨架。

**应嫁接的是薄 skill（流程 + 检查清单 + 代码模板），不是巨型 monorepo。** 优先四条线：

| 线 | 优先嫁接 | 作用 |
|----|----------|------|
| 因果 | 00 StatsPAI · 10 Mixtape · 20 python-econ · 40 pyfixest · 39 marginaleffects · 27 event-studies | 估计算法 + 稳健性电池 + 解释层 |
| 写作 | 27 econ-intro · 06 stat-writing · 01 composer/strategist · 48 中文降 AIGC · 44/45 英文 humanizer | 章节结构 + 去 AI 味 |
| LaTeX | 08 latex-document · 09 latex-tables · 06 check_tex/check_bib · 12 compile-latex | 编译/表格/审计 |
| 验证 | 27 paper_verification · 27 dont-lie · 38 proofreader · 21 review-paper · 已有 integrity-audit | 表文数字对齐 + 反幻觉 |

---

## 2. 源仓是什么

- **定位**：CoPaper.AI / Stanford REAP 维护的 Awesome 列表；宣称覆盖 119 仓库 / 23,000+ skills（本目录为**精选本地副本** 00–48）。
- **组织逻辑**：按实证研究 10 步（选题→文献→精读→数据→统计因果→写作→修改→引用排版→复现→审稿答辩）。
- **Skill 定义**：把「完整 DID 应包含哪些步骤」编码成可触发工作流，避免 AI 只给基准回归就停。
- **一站式推荐（README）**：CoPaper.AI、StatsPAI、Claude Scholar、K-Dense、AI-Research-SKILLs。
- **2026-04 重点**：StatsPAI agent-native 计量；中英文降 AIGC（44–48）。

本地 `skills/` 是 monorepo 摘录：多数包含 `SKILL.md` + `README-original.md`；部分是整仓 `.claude` 工作流（12/14/16/17 等）。

---

## 3. 包一览（00–48）

图例：**P0 必嫁接** · **P1 应嫁接** · **P2 可选/参考** · **P3 不优先** · **已有/重叠**

| ID | 包名 | 形态 | 核心能力（抽样） | 四线归类 | 嫁接建议 |
|----|------|------|------------------|----------|----------|
| 00 | StatsPAI_skill | 单 SKILL + README | Agent-native 因果全管线：`causal_question`→估计→诊断→稳健；统一 `CausalResult` | 因果·结果导出 | **P0 已部分集成**（`plugins/statspai-*`）；补全方法 catalog 与诊断 checklist |
| 01 | lishix520-academic-paper-skills | strategist + composer | 7 维审稿人模拟；章节写作 + 质量门 | 写作 | **P1** 取 quality gate / 章节 checklist，不取哲学平台细节 |
| 02 | luwill-research-skills | 3 skills | 提案 / 医学综述 / 幻灯片 | 写作旁路 | **P3**（非实证论文主路径） |
| 03 | K-Dense scientific-skills | hypothesis / lit / grants / scientific-writing | IMRAD 两阶段写作、STROBE 等指南 | 写作 | **P2** 取「outline→散文」与 reporting guidelines 引用；图示强制规则过重可裁 |
| 04 | K-Dense scientific-writer | 多 SKILL 薄壳 | citation / peer-review / critical-thinking | 写作·验证 | **P2** peer-review + critical-thinking 作 review 子代理提示词 |
| 05 | kthorn-research-superpower | 文献工作流 | 检索 / 筛选 rubric / 引用遍历 | 文献（非四主线） | **P2** 可补 02_literature，非本清单主目标 |
| 06 | fuhaoda-stats-paper-writing | stat-writing + refs | LaTeX 统计文：章节 refs、`check_tex`/`check_bib`/`audit_paper` | 写作·LaTeX | **P0** 章节写作手册 + 确定性 TeX/Bib 审计脚本模式 |
| 07 | Orchestra AI-Research-SKILLs | plotting / autoresearch / ml-paper | ML 论文写作、学术作图 | 写作·图 | **P2** academic-plotting 风格；ml-paper 偏 CS |
| 08 | ndpvt latex-document-skill | 巨型 LaTeX skill | 编译、CJK/XeLaTeX、bib、latexdiff、PDF 工具链 | LaTeX | **P1** 取 compile 脚本模式与 CJK/latexmk；丢简历/发票等非学术模板 |
| 09 | meleantonio awesome-econ-ai | 分域 skills | latex-tables、academic-paper-writer、r-econometrics、stata、beamer | 四线均沾 | **P0** `latex-tables`；**P1** academic-paper-writer、r-econometrics |
| 10 | Jill0099 causal-inference-mixtape | SKILL + method-patterns | Mixtape 10 方法三语言模板 + 稳健性表 | 因果 | **P0** `method-patterns` + robustness prompts |
| 11 | James-Traina compound-science | agents + skills 大包 | 科研多代理 | 通用 | **P3** 体量大、与社科实证耦合松 |
| 12 | pedrohcgs my-workflow | 完整 .claude | 编译 LaTeX、多代理审、quality gates、replication | LaTeX·验证·写作 | **P1** 取 `/compile-latex`、`/validate-bib`、adversarial QA 模式、verifier 角色 |
| 13 | scunning1975 MixtapeTools | compiledeck / referee2 等 | 幻灯片修辞、referee | 写作·答辩 | **P2** referee2 作 10_defense 参考 |
| 14 | luischanci research-starter | 完整 .claude | 研究 starter 工作流 | 通用 | **P2** 结构参考 |
| 15 | Felpix social-science-research | 12 skills + agents | write-paper、deep-audit、validate-bib、review-r | 写作·验证 | **P1** write-paper / proofread / quality-gate / validate-bib；deep-audit 思路可并入 integrity |
| 16 | hsantanna88 clo-author | 完整 .claude | 论文中心多代理、AEA 复现 | 写作·验证 | **P1** 盲审模拟 + AEA replication checklist 思想 |
| 17 | DAAF daaf | 超大 .claude | 领域适配框架 | 通用 | **P3** 过大，按需抽 |
| 18 | justi-aalto stata-accounting | SKILL + 126 .do | JAR 实证 Stata 模式库 | 因果·Stata | **P1** 作 Stata 模式索引（非识别顾问） |
| 19 | CuellarC05 vera-econ | ai-augmented-economist | 经济智能体叙事 | 通用 | **P3** |
| 20 | wenddymacro python-econ | 单 SKILL 长手册 | pyfixest / DID 11 步 / IV / RD / SCM / DML | 因果 | **P0** DID 11-step 与方法选择表 |
| 21 | claesbackman AI-research-feedback | review-paper*.md | 因果过度声称检测、顶刊预审 | 验证·写作 | **P0** review-paper 因果语言审计 |
| 22 | christopherkenny skills | 51 skills | 政治学/社科技能集 | 通用 | **P2** 按需抽 |
| 23 | baygent-skills | bayesian + causal-inference | DAG-first 贝叶斯因果、强制 refutation | 因果 | **P1** 假设确认关卡 + refutation 清单（PyMC 栈可选） |
| 24 | Imbad0202 academic-research-skills | paper/review/pipeline | 全管线 + 幻觉检测 | 写作·验证 | **P1** 幻觉检测与 revise 管线片段 |
| 25 | HosungYou Diverga | agents + skills | 研究分叉系统 | 通用 | **P3** |
| 26 | Data-Wise scholar | 17 skills 级 | arXiv/DOI/BibTeX/方法论写作 | 写作·引用 | **P1** BibTeX / DOI 校验与方法论写作 |
| 27 | dariia-m my_claude_skills | 6 个精技能 | **paper_verification**、dont-lie、econ_intro、event-studies | 验证·写作·因果 | **P0 全集** |
| 28 | maxwell2732 paper-replicate | .claude | 论文复现 demo | 验证 | **P1** 复现编排参考 |
| 29 | quarcs-lab project20XXy | skills | 项目模板技能 | 通用 | **P2** |
| 30 | zirui-song claude-skills | 扁平 md | lit-review、robustness、referee-response | 写作·因果 | **P1** robustness.md、referee-response |
| 31 | thalysandratos skills | _skills | 与 09 类似 econ skills | 因果·写作 | **P2** 与 09 去重后取优 |
| 32 | dylantmoore stata-skill | plugins 大包 | Stata 语法全覆盖 | 因果·Stata | **P1** Stata 路径技能（有 stata-mcp 时可联动） |
| 33 | Galaxy-Dawn claude-scholar | 25+ skills 巨包 | 全生命周期 + Zotero | 全流程 | **P2** 作对照蓝图，勿整仓搬 |
| 34 | andrehuang research-companion | 单 skill | 研究伴侣 | 通用 | **P3** |
| 35 | bahayonghang academic-writing | 大包 | 学术写作工具集 | 写作 | **P2** 抽样可用子 skill |
| 36 | taoyunudt literature-review | 中文综述 | 五步综述法 | 写作（文献） | **P1** 中文 lit section 写作 |
| 37 | IlanStrauss ai-skills | 2 skills | 薄包 | 通用 | **P3** |
| 38 | peternka academic-proofreader | 长 system prompt | 应微经济学多 pass 校对 + 表文数字交叉 | 验证·写作 | **P0** 表/图/因果语言/引用子任务拆分 |
| 39 | vincentarelbundock marginaleffects | 包手册 skill | predictions/comparisons/slopes 五问框架 | 因果 | **P1** 解释层与 estimand 语言 |
| 40 | py-econometrics pyfixest | 机器可读 API | feols/DID/etable LaTeX | 因果·LaTeX | **P0** Python FE/回归默认栈手册 |
| 41 | sticerd sewage-econometrics | 项目 CLAUDE | 生产级 R 实证项目惯例 | 工程参考 | **P2** 数据分层与 modelsummary→LaTeX 惯例 |
| 42 | wanshuiyin ARIS | 大量 paper-* | paper-write/compile、auto-review、result-to-claim | 写作·LaTeX·验证 | **P1** paper-compile、result-to-claim、citation-discipline |
| 43 | wentorai research-plugins | 478 md | 插件海 | 通用 | **P3** 过大，按关键词检索抽 |
| 44 | humanizer_academic | SKILL | 23 种英文学术 AI 痕迹 | 写作 | **P0** 英文稿 |
| 45 | skill-deslop | SKILL + refs | 科学写作去 slop、5 维评分 | 写作 | **P0** 英文/双语 |
| 46 | stop-slop | SKILL | 通用三层检测 | 写作 | **P1** 与 45 重叠，取精简 checklist |
| 47 | avoid-ai-writing | SKILL | 审计→重写→二次审计 | 写作 | **P1** 可审计改写流程 |
| 48 | chinese-de-aigc | SKILL + refs | **中文** 17 类痕迹、五步闭环、分章节策略 | 写作 | **P0** 中文稿必选 |

---

## 4. 按四线：应嫁接清单

### 4.1 因果（causal）

| 优先级 | 源路径 | 嫁接到 workbench 的形态 | 备注 |
|--------|--------|-------------------------|------|
| P0 | `00-StatsPAI_skill/SKILL.md` | 已有 plugin；补 **Method Catalog + Step0–6 检查表** 为 progressive skill | 与 `runtime/stats_engine.py` / adapters 对齐 |
| P0 | `10-...-mixtape/` | skill `causal-mixtape`：method-patterns + robustness prompts | 三语言模板；TWFE 陷阱表 |
| P0 | `20-wenddymacro-python-econ-skill/SKILL.md` | skill `did-empirical-workflow`：11 步 DID + 方法选择树 | 与 StatsPAI/pyfixest 互补（流程层） |
| P0 | `40-pyfixest/SKILL.md` | skill `pyfixest-ref`：API 速查 + etable→tex | Python FE 默认 |
| P0 | `27-.../event-studies/` | skill `event-study`：传统 + modern extensions + diagnostics | 事件研究专用 |
| P1 | `39-marginaleffects/SKILL.md` | skill `marginaleffects`：五问 estimand | 结果解释与 CATE/ATE 语言 |
| P1 | `23-.../causal-inference/` | 摘 **DAG 确认关卡 + refutation 强制** 进 05 工作流 | 不强制引入 PyMC |
| P1 | `18-...-stata-accounting/` | 可选 Stata 模式库索引 | 配合 stata-mcp |
| P1 | `32-dylantmoore-stata-skill/` | Stata 语法 skill 子集 | 同上 |
| P1 | `30-.../robustness.md` | 并入稳健性清单 | 薄文件 |
| P2 | `09-.../analysis/*` | r-econometrics / stata-regression 按语言偏好 | |
| 已有 | workbench integrity + claim_register | 数字锚点；**不**替代识别策略审查 | 需与 21/38 因果语言审计拼接 |

**因果嫁接后的最小闭环：**

```text
识别问题 (causal_question / DAG 确认)
    → 选方法 (20 方法树 + 10 Mixtape)
    → 估计 (StatsPAI / pyfixest)
    → 稳健电池 (10 robustness + 27 event-study diagnostics)
    → 解释 (39 marginaleffects 语言)
    → 写作约束 (21 禁止过度因果声称)
```

### 4.2 写作（writing）

| 优先级 | 源路径 | 嫁接形态 | 备注 |
|--------|--------|----------|------|
| P0 | `27-.../econ_intro_writing/` | skill `econ-intro` | Keith Head / Evans 结构；对 06_writing 引言段 |
| P0 | `06-.../stat-writing/` | skill `stat-writing`：refs 按需加载 + audit 脚本思路 | 摘要/方法/结果/讨论 LaTeX 向 |
| P0 | `48-chinese-de-aigc/` | skill `chinese-de-aigc` | 中文降 AIGC；分章节策略 |
| P0 | `44-humanizer_academic/` | skill `humanizer-academic-en` | 英文 |
| P0 | `45-skill-deslop/` | skill `deslop` 或与 44 合并 references | 科学写作向 |
| P1 | `01-.../composer` + `strategist` | 章节 quality gate（5/7 维评分） | 裁剪人文平台部分 |
| P1 | `15-.../write-paper` + `proofread` | 社科写稿/校对协议 | |
| P1 | `36-literature-review` | 中文 lit 五步 | 02/写作 lit 段 |
| P1 | `21-.../review-paper.md` | 投稿前自审 skill | 因果声称 + 识别评估 |
| P1 | `27-.../academic_writing` + `abstract` | 摘要与通用学术句式 | |
| P1 | `47-avoid-ai-writing` | 可审计改写报告格式 | 与 integrity 输出格式对齐 |
| P1 | `42-.../shared-references/writing-principles.md` + `citation-discipline.md` | 写作原则薄引用 | |
| P2 | `03-scientific-writing` | IMRAD + STROBE 清单 | 医学味重，取框架 |
| P2 | `46-stop-slop` | 与 45 去重后保留短 checklist | |
| 旁路 | 13 MixtapeTools / 02 slides | 答辩幻灯片 | 10_defense 再开 |

**写作管线建议：**

```text
大纲 (strategist 思想 / paper.yaml sections)
  → 分节起草 (stat-writing refs + econ-intro)
  → 数字只能来自 Results/ (dont-lie + claim_register)
  → 中文 de-aigc / 英文 humanizer+deslop
  → 投稿前 review-paper (21) + proofreader (38)
  → integrity-audit --all
```

### 4.3 LaTeX

| 优先级 | 源路径 | 嫁接形态 | 备注 |
|--------|--------|----------|------|
| P0 | `09-.../writing/latex-tables/` | skill `latex-tables` | booktabs 回归表/描述统计 |
| P0 | `06-stat-writing` 的 check_tex/check_bib 模式 | `scripts/` 级确定性检查 | 与 `15_verify_bibliography.py` 对齐增强 |
| P1 | `08-latex-document` | 精简 `compile-latex`：latexmk、XeLaTeX/CJK、preview | 勿搬全模板宇宙 |
| P1 | `12-.../skills` 中 compile-latex / validate-bib | 命令化 skill | 与 `latex_compile` adapter 解禁策略协调 |
| P1 | `40 pyfixest` `etable(..., type="tex")` | 结果→tex 默认路径 | Program 层已有则文档化 |
| P1 | `42-.../paper-compile` + venue templates 子集 | 编译 + 期刊模板可选 | 经济学模板优先于 CS 会场 |
| P2 | `09-.../theory/latex-econ-model` | 理论模型 LaTeX | 实证主路径少用 |
| P2 | `41` modelsummary→tabularray 惯例 | R 路径 | |
| 已有 | `Manuscripts/preamble.tex`、templates、sections/*.md | Markdown-first + 导出 | 嫁接应 **增强编译与表**，不推翻 md section 真相源 |

**注意：** 当前 `statspai-writing-review` 子代理 **blocked** `latex_compile`。嫁接 compile skill 时要明确：人工/专用 adapter 才编译，写作 agent 默认只产 `.tex` 片段与 md。

### 4.4 验证（verify）

| 优先级 | 源路径 | 嫁接形态 | 备注 |
|--------|--------|----------|------|
| P0 | `27-.../paper_verification/` | skill `paper-verification`：6 phase + manifest JSON | **与 claim_register / integrity_audit 对接** |
| P0 | `27-.../dont-lie/` | always-on 规则片段并入 AGENTS / SOUL / integrity | 反幻觉协议 |
| P0 | `38-academic-proofreader` | 拆成子任务：表文数字 / 因果语言 / 引用核验 | 比整段 system prompt 更适合 skill |
| P0 | 已有 `integrity-audit` + `evidence/integrity_audit.py` | **保留为 SSOT 门禁** | 新 skill 产出 feed 进 audit，不平行第二套 |
| P1 | `21-review-paper*` | 识别策略与过度声称审查 | 投稿前 |
| P1 | `15-deep-audit` / `quality-gate` | 仓库一致性审计思想 | 偏工程；可映射 scripts/20–33 |
| P1 | `12-verifier` agent + replication-protocol | 任务完成定义 + 复现协议 | 09_replication |
| P1 | `16-clo-author` AEA 复现合规思想 | replication package checklist | |
| P1 | `28-paper-replicate` | 复现 demo 流程 | |
| P1 | `24` 幻觉检测片段 | 引用/事实层 | |
| P2 | `42-result-to-claim` | 结果→可核验 claim 句 | 与 auto_claim_register 对齐 |
| P2 | `04-peer-review` / scientific-critical-thinking | 审稿人视角 | |

**验证分层（避免重复建设）：**

```text
L0  dont-lie          生成时禁止编造
L1  claim_register    每个数字有源
L2  integrity-audit   section 六维门禁（已有）
L3  paper-verification 表↔代码↔正文 全量交叉（嫁接 27）
L4  proofreader+21    语言/因果声称/引用（嫁接 38/21）
L5  reproduction_verify 端到端复跑（已有 adapter）
```

---

## 5. 不建议整仓搬入

| 包 | 原因 |
|----|------|
| 11, 17, 25, 33, 35, 43 | 体量过大或学科偏离，信噪比差 |
| 02 医学/幻灯片主包 | 非实证论文主路径 |
| 08 全量 templates | 简历/发票等噪声；只取 compile 核心 |
| 20 中 DSGE/HANK 大段 | 宏观计算，与应用微观实证默认路径无关（可另 skill） |
| 03 强制 graphical abstract + 海量 AI 配图 | 与经济学实证发表惯例冲突 |
| 44–47 与 48 混用无套 | 中英分流：中文 48，英文 44+45 |

---

## 6. 与 workbench 现状对照

| workbench 已有 | 缺口 | 用 Awesome 补什么 |
|----------------|------|-------------------|
| StatsPAI plugin + orchestrator | 方法细节与稳健清单分散 | 00 完整 catalog、10、20、27 event-study |
| integrity-audit、claim_register | 缺「表↔脚本全量 manifest」 | 27 paper_verification |
| 写作子代理 blocked latex_compile | 缺精简 compile + 表 skill | 08 精简、09 latex-tables、06 audit |
| 中文 section 流水线 | 缺系统降 AIGC | 48 |
| 英文能力弱于中文流程 | 缺 humanizer | 44、45 |
| review 散落 Reviews/ | 缺因果语言专用审 | 21、38 |
| pyfixest 可能在 Program 使用 | 缺 agent-facing API skill | 40 |
| 引言写作无专用 skill | 结构不稳 | 27 econ-intro |
| 10 步 workflow registry | skill 包只有 statspai 单体 | 按上表拆 progressive skills |

---

## 7. 建议落盘位置（嫁接时）

```text
实证论文项目模板/
  .claude/skills/          # 或 .codex/skills / seeds/skills
    causal-mixtape/
    did-empirical-workflow/
    pyfixest-ref/
    event-study/
    marginaleffects/         # P1
    econ-intro/
    stat-writing/            # 可 symlink refs 自 Awesome 06
    latex-tables/
    compile-latex/           # 精简自 08/12
    paper-verification/
    chinese-de-aigc/
    humanizer-academic-en/
    deslop/                  # 或合并进 humanizer
    review-paper-econ/       # 自 21
    academic-proofreader/    # 拆分自 38
  evidence/                  # 保持 integrity_audit 为门禁
  workflows/skill_subagent_registry.json  # 注册新 skill + 绑定 05/06/07/08/09
```

**原则：**

1. **拷贝 SKILL.md + 必要 references**，不 git submodule 整 Awesome 仓。  
2. **改写 frontmatter** 绑定 workbench 路径（`Manuscripts/sections/`、`Results/json/`、`evidence/`）。  
3. **中文输出默认**；技能正文可保留英文方法论原文。  
4. **禁止** 新 skill 静默改 Results 数字；验证 skill 只读 + 报告。  
5. **渐进披露**：registry 注册；按 workflow_id 加载，避免一次塞 49 包。

---

## 8. 实施顺序（建议）

```text
Wave 1（验证+诚信，堵住捏造）
  27 dont-lie 规则并入
  27 paper-verification 对接 claim_register
  21 + 38 因果语言/表文审

Wave 2（因果执行质量）
  10 Mixtape patterns
  20 DID 11-step
  40 pyfixest-ref
  00 StatsPAI catalog 补全
  27 event-studies

Wave 3（写作与中文发表）
  27 econ-intro
  06 stat-writing refs
  48 chinese-de-aigc
  44+45 英文

Wave 4（LaTeX 投递）
  09 latex-tables
  08/12 compile-latex 精简
  06 check_tex/bib 脚本化
```

---

## 9. 抽样阅读记录（本清单依据）

| 文件 | 结论摘要 |
|------|----------|
| 源 README.md | 10 步分类、StatsPAI、降 AIGC 44–48、多代理系统索引 |
| 00 StatsPAI SKILL | 全管线 agent API；paper() 超出 skill 范围 |
| 08 latex-document | 全能编译；需裁剪 |
| 10 Mixtape | 10 方法 + 稳健表 + 三语言 |
| 06 stat-writing | LaTeX 统计写作 + 确定性 audit |
| 20 python-econ | DID 11 步 + 库选择表（过长含宏观） |
| 27 paper_verification | 6 阶段 + verification_manifest.json |
| 27 dont-lie | always-on 反幻觉 |
| 27 econ_intro | 顶刊引言骨架 |
| 38 proofreader | 应微多代理校对 |
| 40 pyfixest | 机器可读 API |
| 39 marginaleffects | estimand 五问 |
| 44/45/46/48 | 中英文去 AI 味 |
| 12 pedro workflow README | compile/validate-bib/quality gates |
| 15 deep-audit | 并行一致性审计 |
| 09 latex-tables | booktabs 回归表 |
| 18 Stata JAR | 模式库非设计顾问 |
| 23 bayesian causal | DAG + refutation 强制 |
| workbench integrity-audit | 6 维 section 门禁，应保留 SSOT |
| skill_subagent_registry | 目前几乎只有 statspai 单体 skill |

未逐文件打开的巨包（11/17/33/35/42 全量/43）：按 README-original 与目录名归类，标记 P2/P3，实施前再定点读。

---

## 10. 验收标准（怎样算嫁接完成）

1. **因果：** 用户说「做 DID」时，agent 自动走平行趋势→基准→≥4 稳健→异质性，而不是只跑一条回归。  
2. **写作：** 中文稿可走 48 五步并产出痕迹报告；英文稿可走 44/45。  
3. **LaTeX：** 回归表可从 Results 生成 booktabs 片段；可选一键 latexmk（显式权限）。  
4. **验证：** `verification_manifest` 或等价物覆盖主表全部系数；integrity-audit `--all` 与 paper-verification 无双重标准冲突。  
5. **注册：** `skill_subagent_registry.json` 中上述 skill 有 id、path、covers_workflows。

---

## 11. 路径索引

| 用途 | 绝对路径 |
|------|----------|
| Awesome 根 | `/Users/mahaoxuan/Desktop/经济学论文/Awesome-Agent-Skills-for-Empirical-Research` |
| skills 根 | `.../Awesome-Agent-Skills-for-Empirical-Research/skills/` |
| workbench 根 | `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板` |
| 本清单 | `.../实证论文项目模板/docs/structure-audit/materials/awesome_skills_inventory.md` |
| 已有 integrity skill | `.../实证论文项目模板/.claude/skills/integrity-audit/SKILL.md` |
| skill 注册表 | `.../实证论文项目模板/workflows/skill_subagent_registry.json` |
