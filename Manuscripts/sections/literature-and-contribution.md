# 3. 文献回顾与本文贡献

> 本节依据 `contribution_matrix.md`(9 篇核验文献的对照表,见 C-133)与 `verified_bibliography.csv`(14 条已核验文献,见 C-134)组织文献谱系。**每篇文献的对照信息(变量、识别方法、与本文的差异)均来自 contribution_matrix.md 表格,本文不另造**。

## 3.1 与本文最直接相关的两篇文献(closest_papers)

`contribution_matrix.md` 中 `contribution_role=closest_paper` 共 2 篇(C-135),代表与本文研究问题、识别策略、数据类型最接近的 2 篇文献。

**Acemoglu & Restrepo (2020, JPE)**——`acemoglu_restrepo_robots_jobs_2020`,doi_verified。该文以美国通勤区(commuting zone, CZ)为分析单位,使用 IFR 工业机器人数据构造 Bartik 移位-份额工具变量,发现工业机器人渗透对当地劳动力市场存在负向的工资与就业效应。该文是 Bartik 移位-份额 IV 在机器人-劳动市场研究中的奠基性工作,本文**直接沿用其方法学**(见 §5),但以 CFPS 个体数据替换 CZ 聚合数据、以中国情境替换美国情境。其与本文的具体差异在 `contribution_matrix.md` 中登记为"美国 commuting-zone 机器人暴露;本研究用 CFPS 个体数据和中国语境重新映射工资结果"。

**Dauth, Findeisen, Suedekum & Woessner (2021, JEEA)**——`dauth_findeisen_suedekum_woessner_2021`,doi_verified。该文使用德国行政数据,采用类似的 Bartik 移位-份额 IV 识别策略,发现机器人对德国就业有负面影响但对工资有正向或混合影响。其与本文的差异在 `contribution_matrix.md` 中登记为"德国行政数据和本地劳动市场调整;本研究用于对照中国劳动力市场机制"——即作为发达经济体对照,验证中国机制证据的相对位置(本文机制回归见 §6)。

## 3.2 方法学参考(method_references)

`contribution_matrix.md` 中 `contribution_role=method_reference` 共 4 篇(C-136),提供本文方法学与分析框架的核心理论参照。

**Goldsmith-Pinkham, Sorkin & Swift (2020, AER)**——`goldsmith_pinkham_sorkin_swift_bartik_2020`,doi_verified。该文系统化了 Bartik 移位-份额工具的诊断框架——包括工具变量相关性、share/shock 排他性、Rotemberg weights 等——为后续使用该识别的研究(包括本研究)提供了方法学参照。本文**沿用其诊断框架的总体思路**,但承认 `limitations_register` 中 `add_rotemberg_weights_review`、`add_leave_one_out_or_alternative_shock_check` 等具体诊断尚未在本文档完成。

**Acemoglu & Autor (2011, Handbook of Labor Economics)**——`acemoglu_autor_tasks_2011`,doi_verified。该文是任务(task)框架的奠基性综述,将技术冲击分解为位移效应(displacement)与新任务效应(reinstatement),为本文机制分析提供理论支点。其与本文的差异登记为"理论框架,不是实证识别模板;用于定义技能、任务和技术冲击"。

**Acemoglu & Restrepo (2018, race 模型)**——`acemoglu_restrepo_race_2018`,doi_verified。该文是任务模型的正式化表达(自动化 vs 新任务的"竞赛")。其与本文的差异登记为"宏观任务模型;用于解释位移效应和新任务效应"——本文机制回归中"机器人渗透推动职业结构升级(ISEI 提升)"的发现,可视为新任务效应在中国情境下的微观证据。

**Autor & Dorn (2013, AER)**——`autor_dorn_service_jobs_2013`,doi_verified。该文是"任务极化"(task polarization)的实证奠基,使用美国 CZ 数据与职业任务内容指标。其与本文的差异登记为"自动化任务极化框架;本研究只在机制/异质性中借鉴,不直接复制设定"。

## 3.3 数据参考(data_reference)

**Graetz & Michaels (2018, RESTAT)**——`graetz_michaels_robots_work_2018`,doi_verified。该文使用国家-行业层面的机器人面板,研究机器人对生产率与劳动份额的影响。其与本文的差异登记为"国家-行业面板生产率/就业;本研究需要说明机器人变量与个体工资之间的连接"——即本文沿用其 IFR 数据源,但需要从"国家-行业"层下沉到"地区-个体"层,这一桥梁由 Bartik 移位-份额 IV 完成。

## 3.4 综述与对照

**Acemoglu & Restrepo (2022,工资不平等)**——`acemoglu_restrepo_tasks_wage_inequality_2022`,doi_verified,`contribution_role=review_source`。该文综述自动化与工资不平等,提出"任务位移"会计框架。其与本文的差异登记为"美国工资不平等解释;本研究聚焦中国个体工资和机器人暴露"——本文的 ISEI 机制证据可视为对工资不平等框架在中国情境下的微观检验。

**Acemoglu, Lelarge & Restrepo (2020)**——`acemoglu_lelarge_restrepo_competing_2020`,doi_verified,`contribution_role=contrasting_result`。该文研究法国企业层面的机器人采用与竞争外溢效应。其与本文的差异登记为"企业采用和竞争外溢;本研究当前主链路是地区/个体暴露,不直接等同企业采用"——这是本文**重要的方法学边界**:本文识别的是地区-个体层面的机器人暴露对工资的因果效应,**不等同于企业层面的"机器人采用决策"对工人工资的因果效应**;后者属于企业级微观识别,需要企业层面的机器人投资数据(法国数据 LiSS 框架),不在本文能力范围。

## 3.5 本文贡献的对照定位

综合以上文献,本文尝试在以下 3 个维度上做出增量,均对照 closest_papers 与 method_references 的现有结论作明确声明。

**第一,数据维度的增量**。Acemoglu-Restrepo(2020) 使用美国 CZ 聚合数据,Dauth et al.(2021) 使用德国行政数据,两者**均不直接观察个体层面的工资**。本文使用 CFPS(中国劳动力微观调查)个体数据,直接观察劳动者的小时工资,可以在个体层面回答"机器人对工资的因果影响"——这是数据维度的直接延伸。

**第二,机制识别的增量**。现有文献主要讨论"自动化替代低技能劳动者"的负向机制(Autor-Dorn 2013 的极化框架);对中国而言,机器人技术扩散可能同时推动**制造业内部岗位结构升级**(职业声望提升,ISEI_score 提升),而不仅仅是劳动替代。本文在 §6 通过 manu_dummy 与 ISEI_score 两条机制回归,检验这一双重机制,这是对 SBTC 假说在中国情境下的机制证据补充。

**第三,识别策略的本土化适配**。本文沿用 Goldsmith-Pinkham et al.(2020) 的 Bartik 移位-份额 IV 诊断框架,但承认 `limitations_register` 中 `recover_bartik_share_shock_components`、`add_rotemberg_weights_review`、`add_leave_one_out_or_alternative_shock_check`、`write_exclusion_and_shock_exogeneity_review` 等 4 条 major 局限的根源在于:Bartik 工具在中国情境下的可识别性诊断不能直接套用美国/德国经验,需要中国数据的 share/shock 原始组件恢复与排他性论证。

**与已核验文献的对应**。本文的 9 篇核心对照文献(closest_papers 2 篇 + method_references 4 篇 + data_reference 1 篇 + review_source 1 篇 + contrasting_result 1 篇)均来自 `verified_bibliography.csv`(`Data/literature/processed/verified_bibliography.csv`,共 14 条已核验),所有 DOI 均已核验(见 C-133 / C-134)。

**与现有文献的差异显式声明**。本文与 Acemoglu-Restrepo(2020)、Dauth et al.(2021) 在国家情境、地理颗粒度、机制证据上互为补充,而非简单复制;在方法学上与 Goldsmith-Pinkham et al.(2020) 互为"应用 + 诊断待补"的关系;在理论框架上承接 Acemoglu-Autor(2011) 与 Acemoglu-Restrepo(2018) 的任务模型,但实证策略独立。

**未核验文献的边界**。`verified_bibliography.csv` 共 14 条已核验文献;若论文写作中需要引用此 14 条之外的文献(包括但不限于任何"经典"教科书引用、特定假说引用),**必须先通过 `mcp__paper-search` 二次核验并在 `verified_bibliography.csv` 追加条目,再返回 `contribution_matrix.md` 标注 `verification_status=doi_verified`**——这是 `verified_bibliography.csv` 与 `contribution_matrix.md` 双层"先登记后引用"机制的核心约束。

## 3.6 已核验但未列入对照表的方法学文献

`verified_bibliography.csv` 共 14 条已核验文献;其中 9 条已纳入 §3.1-§3.4 的对照组织,另有 5 条虽未进入 `contribution_matrix.md` 但在本文方法学与稳健性讨论中被引用,在此统一说明。

**Staiger & Stock (1997)**——经验弱工具阈值 F=10 的经典文献。该阈值在 §5.4 第一阶段 F 检验与 `method_gate_report.diagnostics[first_stage_f].threshold` 中作为参照,虽未直接对照"中国机器人-工资"研究问题,但作为方法学参照被本文引用(已登记为 C-117)。

**Cinelli & Hazlett (2020)**——Oster / Sensemakr 偏倚分析的近期综述。本文 §5.5 / §6 的偏倚指标(δ*=23.47, RV=0.139)均沿用其框架。该文献是 `evidence_bank.md` §2 robustness findings 的方法学参照。

**VanderWeele & Ding (2017)**——E-value 框架的提出文献。本文 §5.5 中"e-value 计算失败 (AttributeError)"的诚实声明即对应此框架——意味着在数据失败的情形下,本文不报告该指标的具体数字(已登记为 C-096 / C-097)。

**Ganzeboom, De Graaf & Treiman (1992)**——ISEI 量表的构造文献。本文 §4.8 与 §6 的 ISEI 机制回归中,该量表作为职业声望的标准化测度被使用,理论范围 [16, 90](已登记为 C-085 / C-115)。

**Imbens & Angrist (1994)**——LATE 框架的奠基文献。本文 §5.6 中"late monotonicity 论证缺失"对应此框架——尽管 Bartik 移位-份额 IV 通常不强调 LATE 解释,但严格因果表述仍需声明单调性假设。

**对照组织原则总结**。本文 `contribution_matrix.md` 与 `verified_bibliography.csv` 的双层组织遵循"先分类、再引用、最后核验"的原则:核心 9 篇以 contribution_role 分类(closest_paper / method_reference / data_reference / review_source / contrasting_result),分别承担"主对照 / 方法学支撑 / 数据源 / 综述框架 / 对照边界"的功能;5 篇方法学外围文献虽未进入对照表,但承担"具体诊断指标 / 量表测度 / 经验阈值"的功能。这一双层组织确保了论文中每一条引用都可追溯到"已核验 + 明确分类"的来源,降低了凭印象引用的风险。

## 3.7 文献谱系图与本文定位

为帮助读者快速定位本文在文献谱系中的位置,以下用文字描述文献之间的"代际关系"。

**第一代(理论框架)**。Acemoglu & Autor (2011) 任务框架 + Acemoglu & Restrepo (2018) race 模型,提供"位移效应 vs 新任务效应"的概念分解;Graetz & Michaels (2018) 提供国家-行业层面的机器人-生产率/就业证据。

**第二代(本主题实证)**。Acemoglu & Restrepo (2020) 美国 CZ 数据 + Dauth et al.(2021) 德国行政数据,确立 Bartik 移位-份额 IV 在机器人-劳动市场研究中的标准做法;Autor & Dorn (2013) 提供任务极化在 CZ 层面的实证证据。

**第三代(方法学深化)**。Goldsmith-Pinkham, Sorkin & Swift (2020) 系统化 Bartik 诊断框架;Acemoglu-Lelarge-Restrepo (2020) 从地区层面下沉到企业层面;Acemoglu & Restrepo (2022) 综述工资不平等与任务位移的会计框架。

**第四代(本文定位)**。本文沿用第二代 Bartik 移位-份额 IV 标准做法,沿用第三代 Goldsmith-Pinkham et al.(2020) 诊断框架的总体思路,但在**数据维度**(个体 vs 聚合)、**机制识别**(双机制 vs 单一负向)、**中国情境**(vs 发达经济体)3 个维度上做出增量。

**与 §1 引言节的关系**。本节按"代际"组织的文献谱系是 §1 中"现有文献的缺口"的展开——§1 的 4 个缺口(数据维度、机制识别、Bartik 工具可识别性、时间维度)分别对应本节第三代方法学深化与第四代本文定位之间的具体差异。
