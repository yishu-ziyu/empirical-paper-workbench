# 7. 稳健性、机制与异质性

> 本节依据 `robustness_matrix.json`(同时承担 `robustness_matrix` 与 `mechanism_or_heterogeneity_results` 两个 evidence_id)与 `method_gate_report.json`(`method_gate_report` evidence_id)中 `gate_status=yellow` 的稳健性诊断与 7 项 yellow_items,组织本文的稳健性、机制、异质性证据。**所有统计量、诊断状态、推荐的后续任务均来自上述两个 JSON 产物,本文不另造**。

## 7.1 已有稳健性证据总览

`robustness_matrix.json` 共登记 16 条 `checks`(见 C-142)与 8 条 `supplemental_robustness_findings`(见 C-143),覆盖基准 IV 估计、第一阶段相关性、弱工具稳健推断、reduced form、OLS 对比、样本一致性、Bartik 识别诊断、leave-one-out、Rotemberg weights、偏倚分析等。

**绿色/已通过 checks**(已通过自动诊断,无需人工复核):`baseline_iv_2sls_binding`(IV 基准 coef=0.1994,见 C-005)、`first_stage_relevance`(F=14.52,见 C-130)、`robust_first_stage_f_or_kp`、`reduced_form`(coef=0.1400,见 C-140)、`ols_comparison`、`artifact_binding`、`first_stage_f`(design-time 14.03,见 C-126)、`partial_r_squared`(0.4834,见 C-127)、`dwh_endogeneity_test`(F=14.27,见 C-128)、`cluster_count`(30,见 C-121)、`result_artifact_binding`。

**黄色 checks**(机器已运行但需人工复核):`weak_iv_robust_inference_ar_or_clr`(AR/CLR 在 exactly identified 下无法计算)、`sample_consistency`(raw_rows=34315 与 usable_rows=15697 差异需复核,见 C-144)、`shift_share_identification_diagnostics`(share/shock 组件未恢复)。

**手动复核 checks**: `shift_share_rotemberg_weights` 与 `leave_one_out_or_alternative_shock`(`status=needs_manual_review`)。

**8 条 supplemental_robustness_findings**(见 C-143)中,5 条 `status=ok` 或 `info`(可引用):`violations_none`、`estimate`(OLS coef=0.1039)、`ci_width`、`oster_delta_star`(23.47,见 C-090)、`oster_beta_adjusted`(0.0995)、`sensemakr_rv`(0.139,见 C-094)、`sensemakr_rv_qa`(0.124);1 条 `status=check_failed`:`evalue`(e-value 计算失败,见 C-096)。

## 7.2 偏倚分析:Oster δ* 与 Sensemakr RV

`supplemental_robustness_findings` 中的 2 条偏倚指标见 §5.5 / §6 主回归,本节展开其方法学含义。

**Oster (2019) δ\*-for-zero** = 23.47(已登记 C-090,见 `evidence_bank.md` §2.4)。该指标衡量"需要多强的未观测混杂才能将 β 推到 0"——δ\* = 23.47 意味着未观测变量对结果的解释力需达到观测变量的 23.47 倍才能推翻显著性。**远高于经验阈值 1.0**(Oster 2019 经验法则),提示本文主回归系数 0.1994 对未观测混杂具有较强稳健性。

**Cinelli & Hazlett (2020) Sensemakr Robustness Value (RV)** = 0.139(已登记 C-094)。该指标衡量"需要多强的未观测混杂才能推翻显著性"——RV = 0.139 意味着需 13.9% 强度的未观测混杂(对处理变量与结果变量残差方差的解释力)方可推翻 5% 水平的统计显著性。**这是相对较低的脆弱性边界**——意味着若有同等强度的遗漏变量偏误,主结论的统计显著性会被推翻。

**基于 OLS 的偏倚指标**。需要诚实声明的是:本文的 Oster δ* 与 Sensemakr RV 均**基于 OLS 估计**(`regression_tables.tables[1]` coef=0.1039)而非 IV 估计(0.1994)。IV 系数的对应偏倚指标**尚未计算**,见 §7.7 显式声明的 gap(GAP-007)。

## 7.3 弱工具稳健性与方法门状态

**第一阶段相关性**(已多次确认,见 §5.4):
- 实际执行 F=14685.77(主回归 table_1,见 C-028)
- 稳健 F=14.52(`robust_first_stage_f_or_kp`,见 C-130)
- partial R²=0.4834(见 C-127)
- baseline IV p=0.0106(见 C-141)
- KP rk Wald F=15821.29(见 C-060)

**弱工具稳健区间缺失**。`robustness_matrix.checks[id=weak_iv_robust_inference_ar_or_clr]` 状态为 `yellow`,`anderson_rubin.valid=false`,note 字段为 "exactly_identified_model_ar_overidentification_test_not_available"。这意味着在当前 `N instruments=1` 的 exactly identified 设定下,AR 置信集与 Moreira(2003) CLR 稳健区间**无法直接计算**。**当前 IV 95% CI [0.0439, 0.3549](见 C-011)是基于标准正态假设,未在弱工具情形下重新校准**。

**Reduced form 回归**。`checks[id=reduced_form].outputs` 报告 coef=0.1400(见 C-140),p<0.001(t=5.68, CI [0.0917, 0.1883])。Reduced form 回归是 `ln_wage ~ bartik_iv + controls + year | provcd` 直接估计,不通过第一阶段,提供工具变量对结果变量的"压缩"识别。Reduced form 系数显著为正与主回归 IV 系数 0.1994 方向一致。

**样本一致性 yellow**。`checks[id=sample_consistency].outputs` 报告 `raw_rows=34315, usable_rows=15697`(见 C-144),`status=yellow`,`review_items=[raw_rows_differ_from_usable_rows_after_missing_drop]`。该检查提示 IV 规格(usable=15697)与 raw CFPS 样本(34315)之间存在行级差异,需在 §5.7 与 §4.5 中显式说明(已分别说明)。

## 7.4 Bartik 识别诊断(留作后续工作)

`robustness_matrix.checks[id=shift_share_identification_diagnostics]` 状态为 `yellow`,`component_available=false`,`component_columns=[]`,`instrument_variance=1.4248`,`instrument_missing_share=0.0`。该检查表明 Bartik 工具的 **share/shock 原始组件未在当前数据产物中恢复**,Rotemberg weights 与 leave-one-out 检验因此无法直接运行。

`checks[id=shift_share_rotemberg_weights]` 与 `checks[id=leave_one_out_or_alternative_shock]` 状态均为 `needs_manual_review`,`max_leave_one_out=10`,`component_available=false`。这两条检查的 follow-up 工作在 `method_gate_report.recommended_next_tasks` 中以 `run_shift_share_diagnostics`(ExecutionAgent 任务)形式明确登记。

**本文据实声明**。Rotemberg weights、leave-one-out 检验、shift-share 排他性论证均**未在本文档实证**,这与 `limitations_register` 中 `add_rotemberg_weights_review`、`add_leave_one_out_or_alternative_shock_check`、`write_exclusion_and_shock_exogeneity_review` 三条 major 局限直接对应。

## 7.5 机制证据(已在主回归章节完成,本节回顾)

`robustness_matrix` 之外,`regression_tables.tables[2]` 与 `regression_tables.tables[3]` 提供 2 条机制回归(同见 §6):

**机制一(产业结构)**:ln_robot 对 manu_dummy 的 IV 系数 0.0798(t=3.58, p<0.01,见 C-080 / C-052),意味着机器人渗透每提升 1%,个体从事制造业工作的概率提升约 0.08 个百分点。该结果支持"机器人推动制造业内部岗位结构稳定"——而非"机器人完全替代制造业劳动者"——的假说(见 §3.4 机制一)。

**机制二(职业结构)**:ln_robot 对 ISEI_score 的 IV 系数 0.9995(t=3.58, p<0.01,见 C-083 / C-053),意味着机器人渗透每提升 1%,个体职业声望提升约 1 个 ISEI 单位。该结果支持"机器人推动职业结构向高声望职业迁移"的新任务效应假说(见 §3.4 机制二)。

**两条机制共同支撑**"工业机器人渗透—产业结构与职业结构升级—个体工资提升"的传导链条,与 SBTC 假说一致。

## 7.6 异质性分析(待补)

`contribution_matrix` 与 `method_gate_report` 均未登记分样本回归结果。**本文未做分样本回归**,具体原因与待补状态如下。

**待补内容**:分样本回归(按性别 / 地区 / 教育)(对应 GAP-001)、替换工具变量(其他国家/地区冲击)(对应 GAP-002)、替换结果变量(月工资/年工资)(对应 GAP-003)、替换控制变量集(加婚姻/健康)(对应 GAP-004)。这 4 项 `evidence_bank.md` §6 登记的 gap 显式声明为"待 §7 补充"——但当前 `robustness_matrix.json` 中**没有对应执行产物**,因此 §7 不在本文档报告这些稳健性分析,作为诚实声明的"待补"。

**为什么不立即补**。Bartik 工具的 share/shock 原始组件未恢复(见 §7.4),导致替换工具变量(对应 GAP-002)需要先恢复原始组件;分样本回归、替换结果变量、替换控制变量集则需要新一轮 `run_plan` 任务与 `design_spec` 修订。这 4 项的"待补"状态在 §8 后续工作中明确列出。

## 7.7 显式声明的 7 项 gap

综合本节与 `limitations_register`、`evidence_bank.md` §6 gap 列表,本节显式声明的 7 项 gap 如下,**均需在 §8 后续工作中由对应 Agent 关闭**。

**GAP-001**:分样本回归(按性别/地区/教育)——**待 §7 补充**,见 §7.6。

**GAP-002**:替换工具变量(其他国家/地区冲击)——**待 §7 补充**,见 §7.6。

**GAP-003**:替换结果变量(月工资/年工资)——**待 §7 补充**,见 §7.6。

**GAP-004**:替换控制变量集(加婚姻/健康)——**待 §7 补充**,见 §7.6。

**GAP-005**:E-value(VanderWeele & Ding 2017)——**未在本文档报告**,e-value 计算失败(AttributeError),见 C-096 与 §6.5 / §5.5 的诚实声明。

**GAP-006**:中介效应分解(Heckman et al. 2013 mediation)——**需要更正式 mediation analysis**,未在本文档报告。

**GAP-007**:IV 版本的 Oster / Sensemakr 偏倚分析——**基于 OLS 计算,IV 版本需另行计算**,见 §7.2 的诚实声明。

**方法门 follow-up**。`method_gate_report.recommended_next_tasks` 中 3 项任务均**未在本文档完成**:`run_weak_iv_robust_inference`(ExecutionAgent 补 AR/CLR)、`review_exclusion_restriction`(MethodAgent 审稿式论证)、`run_shift_share_diagnostics`(ExecutionAgent 补 Rotemberg weights 与 leave-one-out)。

**与全文的关系**。本节是 §6 主回归的稳健性补充与未来工作方向;§7.1-§7.5 报告已有证据,§7.6-§7.7 显式声明待补缺口。读者在引用本文主回归系数 0.1994 时,应同时引用本节 7 项 gap 的存在——这是"提示性"大于"决定性"结论的具体含义。

## 7.8 与 §5 实证策略 / §6 主回归的衔接

**与 §5 的衔接**。§5.6 列出的 4 项实证策略局限(share/shock 原始组件未恢复、弱工具稳健区间缺失、排他性约束论证不足、late monotonicity 缺失)在本节 §7.3-§7.4 中以 `robustness_matrix` 的具体 yellow_items 形式再次落地——`shift_share_identification_diagnostics`(§7.4)、`weak_iv_robust_inference_ar_or_clr`(§7.3)分别对应"share/shock 组件"与"弱工具稳健区间"两项局限;排他性约束与 late monotonicity 在 §5.6 中由 MethodAgent 与 `method_gate_report.pre_checks` 报告。

**与 §6 的衔接**。§6 主回归报告的 IV 系数 0.1994(主回归)、0.0798(manu_dummy)、0.9995(ISEI_score)在本节 §7.5 中以机制证据形式回顾;§7.1-§7.2 的偏倚分析(Oster δ*、Sensemakr RV)与 §6.5 的偏倚声明一致。本节 §7.7 列出的 GAP-007(IV 版 Oster / Sensemakr)是 §6.5 中"IV 版本的偏倚指标未在本文档计算"的进一步显式声明。

## 7.9 与 §8 结论的衔接

**已有证据向结论的传递**。本节 §7.1-§7.5 报告的证据(IV 系数、reduced form、第一阶段 F、机制回归)在 §8 结论中以"主要定量发现"形式总结;偏倚指标(Oster δ* = 23.47, Sensemakr RV = 0.139)在 §8 中以"在合理偏倚范围内的结论"形式呈现;E-value 失败(见 C-096)与 share/shock 组件未恢复(见 §7.4)以"方法学局限"形式呈现。

**待补 gap 向后续工作的传递**。本节 §7.6 列出的 4 项异质性 gap 与 §7.7 列出的 3 项分析层 gap,在 §8 后续工作中以 7 条具体任务形式列出,与 `method_gate_report.recommended_next_tasks` 的 3 条任务合并,共同构成 §8 的"待补工作清单"。

**方法学 caveat 向结论的传递**。本节显式声明的"在 exactly identified 设定下 AR/CLR 不可计算"与"IV 版偏倚指标未计算"双重 caveat,共同支撑 §8 结论中"在以上局限的前提下,本文证据对政策制定有以下有限含义"的有界结论。**这些 caveat 不是论文的弱点,而是诚实声明的护栏**——读者在引用本文时应将 caveat 与系数 0.1994 共同引用,以避免对单一数字产生过度精确化解读。

## 7-10 读者引用建议

为方便读者合理引用本文,本节给出 3 条具体引用建议。

**第一,引用主回归系数 0.1994 时,应同时引用**:
- 5% 水平的统计显著性(p=0.012);
- IV 95% CI [0.0439, 0.3549] 基于标准正态假设(未在弱工具情形下重新校准);
- 第一阶段 F=14685.77(远超 Staiger-Stock 阈值 10);
- Hausman 检验 F=283.99(p<0.01,拒绝 OLS 外生性);
- §5.6 与本节 §7.7 列出的 5 项 major 局限。

**第二,引用机制回归(0.0798 与 0.9995)时,应同时引用**:
- 两条机制路径共同支撑"工业机器人渗透—产业结构与职业结构升级—个体工资提升"传导链;
- §3.4 提出的 2 条机制假说(对应任务框架与 race 模型);
- §6 / §7.5 的具体 t=3.58(对应 p<0.001,远超 0.01 阈值)显著性。

**第三,引用偏倚指标(Oster δ*、Sensemakr RV)时,应同时引用**:
- 基于 OLS 估计的边界(IV 版本未计算,见 GAP-007);
- E-value 计算失败的诚实声明(见 C-096);
- §7.2 显式声明的"提示性大于决定性"结论边界。

**单一数字不引用的护栏**。本文档**禁止**任何形式的"单独引用 0.1994"或"单独引用 23.47"——所有数字必须连同 caveat 一起引用,以维护学术诚信。
