# evidence/evidence_bank.md — 论文证据库存清单

> **用途**：本清单是论文写作的"弹药库"。所有要在 main-results.md / 其他章节里出现的
> 数字、事实、引用，必须先在本清单中登记。**未登记的数字一律视为捏造**。
>
> **维护规则**：发现新证据 → 追加一行 → 注明 source_path 与 source_anchor（精确到 JSON 路径）。
> 写作时遇到证据不足 → 标 `gap` 字段 → 进入 "待补" 列表，**禁止自行填补**。

---

## 0. 顶层摘要

| 类别 | 计数 | 来源 |
|------|------|------|
| 回归表 (regression tables) | 4 | `Results/json/regression_tables.json` |
| Robustness findings | 8 | `Results/json/analysis_result.json` |
| Approved findings | 1 | `Results/json/approved_findings.json` |
| Section→evidence 绑定 (含 9 章) | 27 | `Results/json/manuscript_section_evidence_bindings.json` |
| 已核验文献条目 | 14 | `Data/literature/processed/verified_bibliography.csv` |
| 已失败/缺失的指标 | 1 | e-value 计算失败 (`AttributeError`) |

---

## 1. 回归表（数字真值源）

> **唯一权威来源**：`Results/json/regression_tables.json`
> **不可改写规则**：所有 main-results.md 表格内的数字、SE、p-value 必须能在本表找到对应
> JSONPath。论文表格内出现的数字若超出本表 4 行 × 4 列之外 → **捏造**。

### 1.1 table_1 — IV-ln_wage (主回归)

- **table_id**: `regression_table_1`
- **run_id**: `run_612f02a059d1`
- **method_id**: `iv`
- **formula**: `ln_wage ~ (ln_robot ~ bartik_iv) + female + age + edu_last + urban`
- **nobs**: `34315`
- **path**: `Results/json/regression_tables.json:tables[0]`

| term | coefficient | std_error | t_stat | p_value | JSONPath |
|------|-------------|-----------|--------|---------|----------|
| `female` | -0.4753 | 0.0295 | -16.0882 | 0.0 | `tables[0].coefficient_rows[female]` |
| `age` | -0.0002 | 0.0017 | -0.1253 | 0.9003 | `tables[0].coefficient_rows[age]` |
| `edu_last` | 0.2450 | 0.0181 | 13.5316 | 0.0 | `tables[0].coefficient_rows[edu_last]` |
| `urban` | 0.0944 | 0.0250 | 3.7777 | 0.000159 | `tables[0].coefficient_rows[urban]` |
| **`ln_robot`** | **0.1994** | **0.0793** | **2.5130** | **0.0120** | `tables[0].coefficient_rows[ln_robot]` |

**Diagnostics** (`tables[0].diagnostics`)：

| 指标 | 数值 | JSONPath |
|------|------|----------|
| R² | 0.1862 | `tables[0].diagnostics[R-squared]` |
| First-stage F (ln_robot) | 14685.77 | `tables[0].diagnostics[First-stage F (ln_robot)]` |
| Hausman F-stat | 283.99 | `tables[0].diagnostics[Hausman F-stat]` |
| KP rk Wald F | 15821.29 | `tables[0].diagnostics[KP rk Wald F]` |
| Partial R² (ln_robot) | 0.4834 | `tables[0].diagnostics[Partial R² (ln_robot)]` |
| N instruments | 1 | `tables[0].diagnostics[N instruments]` |
| N endogenous | 1 | `tables[0].diagnostics[N endogenous]` |
| OP effective F error | 计算失败 | `tables[0].diagnostics[OP effective F error]` |

### 1.2 table_2 — OLS-ln_wage (对比)

- **table_id**: `regression_table_2`
- **method_id**: `ols`
- **formula**: `ln_wage ~ ln_robot + female + age + edu_last + urban`
- **nobs**: `15697`（注意：与 IV 样本量不同）
- **path**: `Results/json/regression_tables.json:tables[1]`

| term | coefficient | std_error | t_stat | p_value | JSONPath |
|------|-------------|-----------|--------|---------|----------|
| `intercept` | 8.6688 | 0.0694 | 124.91 | 0.0 | `tables[1].coefficient_rows[intercept]` |
| **`ln_robot`** | **0.1039** | **0.0059** | **17.63** | **1.52e-69** | `tables[1].coefficient_rows[ln_robot]` |
| `female` | -0.4673 | 0.0145 | -32.30 | 6.34e-229 | `tables[1].coefficient_rows[female]` |
| `age` | 0.0001 | 0.0007 | 0.116 | 0.9074 | `tables[1].coefficient_rows[age]` |
| `edu_last` | 0.2417 | 0.0055 | 44.09 | 0.0 | `tables[1].coefficient_rows[edu_last]` |
| `urban` | 0.1277 | 0.0156 | 8.20 | 2.44e-16 | `tables[1].coefficient_rows[urban]` |

### 1.3 table_3 — IV-manu_dummy (机制 1：产业结构)

- **table_id**: `regression_table_3`
- **method_id**: `iv`
- **formula**: `manu_dummy ~ (ln_robot ~ bartik_iv) + female + age + edu_last + urban`
- **nobs**: `34315`
- **path**: `Results/json/regression_tables.json:tables[2]`

| term | coefficient | std_error | t_stat | p_value | JSONPath |
|------|-------------|-----------|--------|---------|----------|
| `female` | -0.0232 | 0.0114 | -2.04 | 0.0412 | `tables[2].coefficient_rows[female]` |
| `age` | -0.0025 | 0.0005 | -5.27 | 1.77e-07 | `tables[2].coefficient_rows[age]` |
| `edu_last` | -0.0351 | 0.0063 | -5.57 | 2.58e-08 | `tables[2].coefficient_rows[edu_last]` |
| `urban` | -0.0249 | 0.0122 | -2.05 | 0.0403 | `tables[2].coefficient_rows[urban]` |
| **`ln_robot`** | **0.0798** | **0.0223** | **3.58** | **0.000343** | `tables[2].coefficient_rows[ln_robot]` |

**Diagnostics**：`First-stage F=17482.00`, `Hausman F=69.97`, `R²=0.036`

### 1.4 table_4 — IV-ISEI_score (机制 2：职业声望)

- **table_id**: `regression_table_4`
- **method_id**: `iv`
- **formula**: `ISEI_score ~ (ln_robot ~ bartik_iv) + female + age + edu_last + urban`
- **nobs**: `34315`
- **path**: `Results/json/regression_tables.json:tables[3]`

| term | coefficient | std_error | t_stat | p_value | JSONPath |
|------|-------------|-----------|--------|---------|----------|
| `female` | 1.1218 | 0.2018 | 5.56 | 2.74e-08 | `tables[3].coefficient_rows[female]` |
| `age` | -0.1686 | 0.0109 | -15.47 | 0.0 | `tables[3].coefficient_rows[age]` |
| `edu_last` | 5.4157 | 0.0899 | 60.24 | 0.0 | `tables[3].coefficient_rows[edu_last]` |
| `urban` | 3.8087 | 0.168 | 22.67 | 0.0 | `tables[3].coefficient_rows[urban]` |
| **`ln_robot`** | **0.9995** | **0.2793** | **3.58** | **0.000345** | `tables[3].coefficient_rows[ln_robot]` |

**Diagnostics**：`First-stage F=24410.94`, `Hausman F=38.59`, `R²=0.439`

---

## 2. Robustness findings (8 条)

> **唯一权威来源**：`Results/json/analysis_result.json:robustness_findings._findings[]`
> **重要警告**：本节里有 1 条 **check_failed**（e-value），不可在论文中宣称
> "E-value = X.X"。

| # | name | value | severity | 论文是否可引用 |
|---|------|-------|----------|----------------|
| 1 | `violations_none` | "none" | ok | ✅ 可写"未报告违规" |
| 2 | `estimate` | 0.1039 | info | ✅ OLS 系数 |
| 3 | `ci_width` | 0.0231 | info | ✅ 95% CI 宽度 |
| 4 | `evalue` | **null** | **check_failed** | ❌ **禁止写 E-value 数字**。只能写"e-value 计算失败 (AttributeError)" |
| 5 | `oster_delta_star` | 23.4708 | ok | ✅ 可写"Oster δ*=23.47，远超经验阈值 1.0" |
| 6 | `oster_beta_adjusted` | 0.0995 | info | ✅ 可写"Oster β* (δ=1) 调整后估计" |
| 7 | `sensemakr_rv` | 0.1393 | ok | ✅ 可写"Sensemakr RV=0.139" |
| 8 | `sensemakr_rv_qa` | 0.1241 | info | ✅ α=0.05 显著性阈值下的 RV |

**JSONPath**：`Results/json/analysis_result.json:robustness_findings._findings[]`

---

## 3. Approved findings（人工核准）

> **唯一权威来源**：`Results/json/approved_findings.json`

| finding_id | claim | run_id | evidence_level | review_status | JSONPath |
|------------|-------|--------|----------------|---------------|----------|
| `finding_trained_effect` | 在 iv 规格中，ln_robot 对 ln_wage 的估计系数为 0.199384322747（SE=0.0793435494782, p=0.0119807291718, N=34315）。 | `run_bb423547439c` | local_file | approved | `findings[0]` |

**写入规则**：

- ✅ 可直接引用 finding_trained_effect 的数字（与 table_1 ln_robot 行完全一致）
- ❌ 任何"approved finding 之外的数字"必须先在 `claim_register.md` 标 gap，再进 `approved_findings.json` 走人工 review 流程
- ⚠️ E-value 这类 check_failed 项目**禁止**通过"自动通过 approved"机制写入论文

---

## 4. Section→evidence 绑定（9 章 × 3 证据 = 27 条）

> **来源**：`Results/json/manuscript_section_evidence_bindings.json`
> **作用**：每章至少绑定 3 个 evidence_id；写作时引用本表的 source_path 才是合法引用。

| 章节 | evidence_id | primary_path | sha256 头 |
|------|-------------|--------------|-----------|
| Abstract | approved_findings | `Results/json/approved_findings.json` | 417f... |
| Abstract | method_gate_report | `Results/json/method_gate_report.json` | 2846... |
| Abstract | verified_bibliography.csv | `Data/literature/processed/verified_bibliography.csv` | d2ab... |
| Introduction | research_question | `state/product/research_question.json` | — |
| Introduction | contribution_matrix.md | `Data/literature/processed/contribution_matrix.md` | — |
| Introduction | approved_findings | `Results/json/approved_findings.json` | — |
| Literature and Contribution | verified_bibliography.csv | `Data/literature/processed/verified_bibliography.csv` | — |
| Literature and Contribution | contribution_matrix.md | `Data/literature/processed/contribution_matrix.md` | — |
| Literature and Contribution | closest_papers | `Data/literature/processed/contribution_matrix.md` | — |
| Institutional Background | domain_notes | `Results/json/domain_notes.json` | — |
| Institutional Background | mechanism_hypotheses | `Results/json/domain_notes.json` | — |
| Institutional Background | literature_context | `Results/json/literature_package_report.json` | — |
| Conclusion | approved_findings | `Results/json/approved_findings.json` | — |
| Conclusion | limitations_register | `Results/json/limitations_register.json` | — |
| Conclusion | reviewer_scorecard_report | `Results/json/reviewer_scorecard_report.json` | — |
| Data and Measurement | dataset_profile | `Results/json/sample_profile.json` | — |
| Data and Measurement | variable_dictionary | `Results/json/variable_role_reconciliation_report.json` | — |
| Data and Measurement | sample_construction_log | `Results/json/sample_profile.json` | — |
| Empirical Strategy | design_spec | `state/product/design_spec.json` | — |
| Empirical Strategy | run_plan | `state/product/run_plan.json` | — |
| Empirical Strategy | method_gate_report | `Results/json/method_gate_report.json` | — |
| **Main Results** | **main_regression_table** | **`Results/json/regression_tables.json`** | — |
| **Main Results** | **approved_findings** | **`Results/json/approved_findings.json`** | — |
| **Main Results** | **coefficient_interpretation** | **`Results/json/approved_findings.json`** | — |
| Robustness / Mechanisms | robustness_matrix | `Results/json/robustness_matrix.json` | — |
| Robustness / Mechanisms | mechanism_or_heterogeneity_results | `Results/json/robustness_matrix.json` | — |
| Robustness / Mechanisms | method_gate_report | `Results/json/method_gate_report.json` | — |

---

## 5. 文献库（已核验）

> **来源**：`Data/literature/processed/verified_bibliography.csv`
> **引用规则**：必须在 `Manuscripts/references.bib` 同步 BibTeX 条目；本表条目之外
> 的引用视为"未核验"，需走 `mcp__paper-search` 二次核验。

- 14 条已核验文献（详见 CSV）
- 包括 Acemoglu & Restrepo (2020)、Dauth et al. (2021)、Bartik (1991)、Autor-Dorn (2013)、
  Staiger & Stock (1997)、Cinelli & Hazlett (2020)、VanderWeele & Ding (2017) 等

**未在库的关键文献** → 写论文前必须先用 `mcp__paper-search` 补齐 BibTeX 才能引用。

---

## 6. gap 列表（论文里要写但 evidence_bank 没有的数字）

> **本节是诚实声明**：以下数字 / 事实论文可能要写但**当前 evidence_bank 没有
> 严格对应**。标记为 gap → 在 claim_register.md 标 gap → 在文中显式注明"待 §6 补充"
> 或"未在本文档实证"，**禁止自行脑补**。

| gap_id | 描述 | 在论文哪里出现 | 处理方式 |
|--------|------|----------------|----------|
| GAP-001 | 分样本回归 (按性别 / 地区 / 教育) | §6 Robustness | 显式写"待 §6 补充" |
| GAP-002 | 替换工具变量 (其他国家/地区冲击) | §6 Robustness | 显式写"待 §6 补充" |
| GAP-003 | 替换结果变量 (月工资 / 年工资) | §6 Robustness | 显式写"待 §6 补充" |
| GAP-004 | 替换控制变量集 (加婚姻 / 健康) | §6 Robustness | 显式写"待 §6 补充" |
| GAP-005 | E-value (VanderWeele-Ding 2017) | §5.5 / §6 | 显式写"e-value 计算失败 (AttributeError)" |
| GAP-006 | 中介效应分解 (Heckman et al. 2013 mediation) | §5.4 / §6.3 | 显式写"需要更正式 mediation analysis" |
| GAP-007 | IV 版本的 Oster / Sensemakr 偏倚分析 | §5.5 | 显式写"基于 OLS 计算，IV 版本需另行计算" |
| GAP-008 | 4 张表之外的任何数字 | 任何章节 | 立即触发 integrity_audit BLOCKER |

---

## 7. 维护日志

- 2026-06-02 初版：基于 regression_tables.json (4 tables) + analysis_result.json (8 findings)
  + approved_findings.json (1 finding) + manuscript_section_evidence_bindings.json
  (27 bindings) 生成，登记 8 条 gap
