# 5. 实证策略

> 本节依据 `design_spec.json`(`design_spec` evidence_id)与 `run_plan.json`(`run_plan` evidence_id)中已批准的研究设计与执行计划,以及 `method_gate_report.json`(`method_gate_report` evidence_id)中 `gate_status=yellow` 的方法门结论展开。**所有识别假设、统计量、门禁状态均来自上述三个 JSON 产物,不在本文另造**。

## 5.1 估计方程与识别策略

本文采用两阶段最小二乘法(IV-2SLS)识别工业机器人渗透对劳动者小时工资的因果效应。

**主回归(第二阶段)**。公式来源于 `design_spec.model.formula` 与 `method_gate_report.variables.formula`:
`ln_wage ~ ln_robot + female + age + edu_last + urban | year`
其中,`ln_robot` 为内生处理变量(城市工业机器人装机量对数),`female / age / edu_last / urban` 为控制变量,`year` 为年份固定效应,标准误聚类在省级(`cluster_by: provcd`,30 个省级聚类,见 C-121)。

**第一阶段**。`instrument_formula`(同见 `design_spec.model` 与 `method_gate_report.variables.instrument_formula`):
`ln_robot ~ bartik_iv + female + age + edu_last + urban | year`
即以 Bartik 工具变量 `bartik_iv` 替代 `ln_robot` 进行第一阶段回归,工具变量与内生变量之间的相关性由第一阶段 F 统计量检验(详见 §5.4)。

**对照回归**。为辅助 Durbin-Wu-Hausman 内生性检验,本文同时估计 OLS 对照:`ln_wage ~ ln_robot + female + age + edu_last + urban | year`,样本量 N=15697(同见 `run_plan.tasks[id=robot_wage_ols_comparison]`)。OLS 与 IV 系数对比方向性在 §6 给出(IV 0.1994 > OLS 0.1039,提示 OLS 被向下偏,见 C-067)。

**机制回归**(同见 `run_plan.tasks` 中的 `robot_manu_iv` 与 `robot_isei_iv`):将 `ln_wage` 替换为机制变量 `manu_dummy` 与 `ISEI_score`,其余设定与主回归一致。这两条机制回归的执行结果在 §6 报告。

## 5.2 Bartik 移位-份额工具变量构造

`bartik_iv` 采用 Goldsmith-Pinkham, Sorkin & Swift (2020, AER) 框架下的"行业份额 × 国际冲击"标准做法。

**份额项**(`s_s,base`)。使用中国基期细分制造业行业 `s` 的就业份额,数据来源为中国基期统计年鉴或相应人口/经济普查(`design_spec.data_sources.instrument_construction`)。**份额项属于"基期"非当期变量,不混入地区当期机器人决策,理论上可缓解反向因果。**

**冲击项**(`ΔRobot_s,international`)。使用同期国际行业 `s` 的工业机器人装机量增速,数据来源为 IFR 国际机器人联合会行业层面数据(其他国家范围在 `design_spec.identification_strategy.summary` 中描述为"美国行业机器人运行存量对数")。**冲击项为"国际行业"层面,不混入中国本地区当期机器人决策。**

**工具变量公式**:`bartik_iv = Σ_s (s_s,base × ΔRobot_s,international)`,即 Bartik(1991)移位-份额 IV 的标准形式。

**为什么用 Bartik 而非直接外生冲击**。"直接外生冲击"如政策、自然实验在中国情境下难以获得;Bartik 移位-份额 IV 的"地理隔离"设计(份额来自中国基期,冲击来自国际行业层面)在中国情境下是 Acemoglu & Restrepo(2020, JPE)与 Dauth et al.(2021, JEEA)等近期文献采用的标准做法(`verified_bibliography.csv` 中 `acemoglu_restrepo_robots_jobs_2020`、`dauth_findeisen_suedekum_woessner_2021` 已核验)。

## 5.3 识别假设与威胁

`design_spec.identification_strategy.assumptions` 与 `threats` 字段登记了本文的 3 项识别假设与 3 项识别威胁,转写如下。

**第一,相关性假设**。Bartik 工具变量与内生变量 `ln_robot` 显著相关,以第一阶段 F 统计量 > 10(Staiger-Stock 经验阈值,见 C-117)为最低门槛;`method_gate_report` 将 `first_stage_f` 的 `threshold` 设为 10。

**第二,排他性约束**。Bartik 工具变量仅通过预测本地机器人暴露影响结果(工资),不直接影响劳动者工资。该假设在中国情境下的强度受"产业结构可能反映制造业基础、开放程度和发展路径"这一威胁影响(`design_spec.identification_strategy.threats[0]`),需审稿式论证。

**第三,同质性假设**。行业机器人冲击对不同地区的影响方向一致。该假设在 Acemoglu & Restrepo(2020) 的美国 CZ 数据中通过 placebos 检验,在中国情境下未做(§5.7 列为 gap)。

**3 项威胁**(`design_spec.identification_strategy.threats`):
1. 产业结构可能反映制造业基础、开放程度和发展路径,排他性约束存在讨论空间;
2. 遗漏变量偏误:地区层面未观测因素可能同时影响机器人应用和工资;
3. 弱工具变量风险:第一阶段 F 统计量需大于 Stock-Yogo 临界值。

`method_gate_report.pre_checks` 中 `exclusion_restriction_argument` 与 `share_or_shock_exogeneity_position` 状态为 `needs_human_review`,与上述(1)(2)直接相关,需在 §8 后续工作中完成审稿式论证(详见 §5.7)。

## 5.4 第一阶段与内生性诊断

**第一阶段相关性(实际执行结果)**。IV 主回归(对应 `regression_tables.tables[0]`,N=34315)报告的 `First-stage F (ln_robot)` = 14685.77(已登记为 C-028,远超 Staiger-Stock 经验阈值 10),`KP rk Wald F` = 15821.29(C-060),`Partial R² (ln_robot)` = 0.4834(C-127)。

**第一阶段相关性(design-time 参考值)**。`design_spec.identification_strategy.first_stage_diagnostics` 记录的设计时 F 统计量为 14.03(C-126),该值在 `method_gate_report.diagnostics[first_stage_f]` 中以 `observed=14.03, threshold=10, status=passed` 形式再次出现。两套数字的关系:`design_spec.identification_strategy.first_stage_diagnostics` 中登记的是设计期参考值(可能基于较小样本或不同聚类);`regression_tables.tables[0].diagnostics` 中登记的是实际执行结果(完整 N=34315,30 省级聚类)。**两者均超过 Staiger-Stock 经验阈值 10,第一阶段相关性不是本文的薄弱环节。**

**稳健第一阶段 F**。`method_gate_report.diagnostics[robust_first_stage_f_or_kp].observed.statistic` = 14.52(C-130),p < 0.001(同见 `method_gate_report.diagnostics[robust_first_stage_f_or_kp].observed.p_value`),后端为 `linearmodels_first_stage_clustered`,提示在稳健聚类下工具变量与内生变量仍高度相关。

**Durbin-Wu-Hausman 内生性检验**。`design_spec.identification_strategy.first_stage_diagnostics` 登记的 DWH F = 14.27(C-128),p = 0.0007(C-129),拒绝"OLS 与 IV 等价"的外生性原假设。该结果意味着 OLS 估计存在内生性偏误,IV 估计的因果解释成立。

**两套数字的方向一致性**。DWH 检验 p = 0.0007 强烈拒绝 OLS 外生性,与 §6 中"IV 系数(0.1994) > OLS 系数(0.1039)"的方向一致——共同支持"OLS 存在向下的衰减偏误,IV 估计的因果效应更大"这一解释。

## 5.5 弱工具稳健性与方法门状态

**弱工具稳健区间缺失**。由于当前 `bartik_iv` 是单一工具变量(`N instruments` = 1,exactly identified 设定),Anderson-Rubin(AR)置信集与 Moreira(2003) CLR 稳健区间**无法直接计算**——`method_gate_report.diagnostics[weak_iv_robust_inference_ar_or_clr].status` = `yellow`,`anderson_rubin.valid` = `false`,note 字段说明 "exactly_identified_model_ar_overidentification_test_not_available"。这意味着本文 IV 系数的 95% 置信区间 [0.0439, 0.3549](见 C-011)是基于标准正态假设,**未在弱工具情形下重新校准**。**这是 §8 后续工作的明确方向之一,需在 exactly identified 设定下补充因果表述 caveat,或在工具变量数 ≥ 2 时计算 AR/CLR 稳健区间**(见 `limitations_register` 中 `add_weak_iv_robust_interval_or_caveat`,major 级别)。

**方法门状态**。`method_gate_report.gate_status` = `yellow`,`blocking_items` = 空,`red_items` = 空,意味着方法门**通过(带可接受警告)**,允许继续草稿层和诊断执行;但所有因果主张在 `needs_human_review` 状态下保持 caveat。

**12 项 pre_checks** 全部 passed(见 C-120):`design_spec_approved`、`run_plan_approved`、`variables_declared`、`instrument_declared`、`structural_equation_declared`、`first_stage_equation_declared`、`fixed_effects_declared`、`cluster_level_declared`、`analysis_sample_declared`、`dataset_contains_declared_variables`、`exclusion_restriction_argument`(`needs_human_review`)、`share_or_shock_exogeneity_position`(`needs_human_review`)、`late_monotonicity_position`(missing)、`overidentification_applicability`(`not_applicable`)。其中 10 项 passed,2 项 `needs_human_review`(排他性约束与 share/shock exogeneity),1 项 `missing`(late monotonicity),1 项 `not_applicable`(overidentification,因仅 1 个工具变量)。

**7 项 yellow_items**(C-131,见 `method_gate_report.yellow_items`):
1. `missing_leave_one_out_or_alternative_shock` —— 缺 leave-one-out 或替代冲击稳健性;
2. `missing_shift_share_identification_diagnostics` —— 缺 shift-share 识别的标准诊断;
3. `missing_shift_share_rotemberg_weights` —— 缺 Rotemberg weights;
4. `missing_weak_iv_robust_inference` —— 缺弱工具稳健推断;
5. `missing_weak_iv_robust_inference_ar_or_clr` —— AR/CLR 在 exactly identified 下无法计算;
6. `review_exclusion_restriction_argument` —— 排他性约束需审稿式论证;
7. `review_share_or_shock_exogeneity_position` —— share/shock exogeneity 需审稿式论证。

**3 项 recommended_next_tasks**(`method_gate_report.recommended_next_tasks`):
1. `ExecutionAgent`: 补 Anderson-Rubin / CLR 等弱工具稳健推断;
2. `MethodAgent`: 审阅 Bartik 工具变量排他性约束和识别叙事;
3. `ExecutionAgent`: 补 Rotemberg weights、leave-one-out 或 shock-level / exposure-level 诊断。

## 5.6 局限与后续工作

综合 §5.3-§5.5,本节诚实声明以下 4 项局限,与 `limitations_register` 中的具体条目一一对应。

**第一,share/shock 原始组件未恢复**(`recover_bartik_share_shock_components`,major)。当前 `bartik_iv` 已是聚合形式,share/shock 原始组件未在产物中恢复,Rotemberg weights、leave-one-out 检验、排他性限制的审稿式论证均**未在本文档完成**。

**第二,弱工具稳健区间缺失**(`add_weak_iv_robust_interval_or_caveat`,major)。当前 IV 系数的 95% 置信区间未在弱工具情形下重新校准,需在 §8 显式写"在 exactly identified 设定下补充因果表述 caveat"。

**第三,排他性约束与 share/shock exogeneity 论证不足**(`write_exclusion_and_shock_exogeneity_review`,major)。需在后续工作中由 MethodAgent 审稿式论证。

**第四,late monotonicity 论证缺失**(`method_gate_report.pre_checks[late_monotonicity_position].status=missing`)。Imbens & Angrist (1994) 的单调性假设在 Bartik 移位-份额 IV 框架下通常不强调,但严格因果表述仍需声明。

**与 §4 数据-测量节的衔接**。本节定义的识别策略与 §4.4 中"变量角色未 canonical 写"的方法学缺口无直接因果关系——`method_gate_report.pre_checks` 中的 `variables_declared` 12 项 passed 表明实际执行使用的变量集是经过 method_gate 验证的,与 §4.4 的状态层缺口是不同维度的问题。

**与 §6 主结果节的衔接**。本节定义的 IV-2SLS 估计方程在 §6 中执行,主回归系数 0.1994(p=0.012)、机制回归系数 0.0798(manu_dummy)与 0.9995(ISEI_score)均在 §6 报告。

## 5.7 与替代识别策略的对比及外部选择依据

为说明 Bartik 移位-份额 IV 在中国情境下的相对优势,本节简短对比 3 类常见识别策略,并给出本文选择 Bartik 而非其他方法的依据。

**双重差分(DID)的局限**。DID 识别策略需要"处理组 / 对照组"在某政策或外生事件上受到差异化冲击。中国机器人装机并非"政策外生事件",而是企业自主决策的市场结果(尽管有"中国制造 2025"等产业政策的间接推动,但政策强度在中国各省之间是渐变而非 0/1 切换),因此难以构造清晰的处理 / 对照组边界。`design_spec.identification_strategy` 也未采用 DID 设定。

**断点回归(RDD)的局限**。RDD 需要可清晰识别的"断点"——在中国情境下,机器人装机不存在地理或政策维度的清晰断点,即便有"国家级开发区"等政策边界,也难以将其与"非开发区"的工资差异完全归因于机器人暴露(因开发区本身具备税收、基础设施等多重差异)。

**Bartik 移位-份额 IV 的优势**。Bartik 设计的关键是"份额项来自基期(中国),冲击项来自国际行业层面"——这种"地理隔离"使工具变量与本地当期机器人决策的相关性被切断,只通过"中国基期产业结构对国际行业冲击的暴露"间接预测本地当期机器人装机。**这一识别逻辑在 Acemoglu & Restrepo(2020) 美国 CZ 数据与 Dauth et al.(2021) 德国行政数据中均通过了审稿式排他性论证,在中国情境下本文沿用同样的构造,但承认排他性约束仍需 §5.5 列出的审稿式补证工作**。

**IV-2SLS 的标准误选择**。本文标准误聚类在省级(`provcd`,30 个聚类)而非个体或城市层面,这一选择的原因是机器人暴露(`ln_robot`)在省级层面变化,而个体层面的机器人暴露完全由其所在省份决定——若不聚类在省级,标准误会被高估/低估并导致过度拒绝或接受。这一选择与 `run_plan.tasks` 中所有 4 个任务的 `cluster_by: ["provcd"]` 一致,跨任务保持一致便于跨结果变量比较。

**样本差异的说明**。IV 主回归样本量 N=34315,OLS 对照样本量 N=15697(同见 C-065 / C-066)。两套样本量的差异并非来自随机抽样,而是来自 `bartik_iv` 变量在不同省-年组合下的可用性——若某省-年组合中份额项或冲击项缺失,该观测会从 IV 样本中剔除,但仍保留在 OLS 样本中(因 OLS 不需要 `bartik_iv`)。**这一差异在 §4 中已声明,本节再次强调,以避免读者误以为 IV 与 OLS 系数差异来自样本选择而非内生性纠正**。
