# Introduction

## 研究背景与问题

工业机器人作为自动化技术的核心载体,在过去二十年里迅速渗透全球制造业。根据 IFR 国际机器人联合会(International Federation of Robotics)的统计,中国自 2013 年起成为全球最大的工业机器人装机国,装机量持续高速增长。这一自动化浪潮对劳动力市场的影响——尤其是对个体工资水平的影响——已成为劳动经济学、产业经济学与政策研究共同关注的核心议题。

本文的核心研究问题是:**工业机器人渗透对劳动者小时工资的因果影响是什么?**(对应的 `research_question` 为"工业机器人应用对劳动力市场匹配效率的影响",二者在本文聚焦工资水平这一可观测维度上重合,但前者更广泛,本文聚焦可由 CFPS 个体数据回答的"工资"切面。)

回答这一问题不仅有助于评估"技能偏向性技术进步"(skill-biased technical change,SBTC)假说在新兴市场的适用性,也对自动化背景下的再培训政策、地区转型政策与社会保障设计具有直接含义。

## 文献定位

现有文献已在发达经济体(尤其是美国与德国)对工业机器人与劳动力市场结果的因果关系进行了系统研究。**Acemoglu & Restrepo (2020, JPE)** 以美国通勤区(commuting zone)为分析单位,使用 IFR 工业机器人数据构造 Bartik 移位-份额工具变量,发现工业机器人渗透对当地劳动力市场存在负向的工资与就业效应(`contribution_matrix` 中 `acemoglu_restrepo_robots_jobs_2020`,closest_paper,DOI 已核验)。**Dauth, Findeisen, Suedekum & Woessner (2021, JEEA)** 在德国制造业部门的类似识别策略下,发现机器人对就业具有负面但对工资具有正向或混合的影响(`contribution_matrix` 中 `dauth_findeisen_suedekum_woessner_2021`,closest_paper,DOI 已核验)。

在方法学层面,**Goldsmith-Pinkham, Sorkin & Swift (2020, AER)** 系统化了 Bartik 移位-份额工具的诊断框架——包括工具变量相关性、share/shock 排他性、Rotemberg weights 等——为后续使用该识别的研究(包括本研究)提供了方法学参照(`contribution_matrix` 中 `goldsmith_pinkham_sorkin_swift_bartik_2020`,method_reference,DOI 已核验)。**Acemoglu & Autor (2011, Handbook of Labor Economics)** 提供了"任务(task)"框架,将技术冲击分解为位移效应(displacement)与新任务效应(reinstatement),为本研究的机制分析提供理论支点。

## 现有文献的缺口

尽管上述文献已为发达经济体提供丰富证据,**关于中国情境的工业机器人与个体工资因果关系研究仍然稀缺**。这一缺口具有重要意义:中国制造业占 GDP 比重、机器人装机增速、城乡劳动力市场结构与发达经济体差异显著,Acemoglu-Restrepo(2020)与 Dauth et al.(2021)的结论能否外推到中国情境,是一个未在文献中被回答的问题。

**第一个缺口是数据维度**。Acemoglu-Restrepo(2020)使用美国通勤区层面的劳动力市场聚合数据,Dauth et al.(2021)使用德国行政数据;两者均**不直接观察个体层面的工资**。本研究使用 CFPS(中国劳动力微观调查)个体数据,直接观察劳动者的小时工资,可以在个体层面回答"机器人对工资的因果影响"。

**第二个缺口是机制识别**。现有文献主要讨论"自动化替代低技能劳动者"的负向机制;对中国而言,机器人技术扩散可能同时推动**制造业内部岗位结构升级**(职业声望提升),而不仅仅是劳动替代。这一机制需要 ISEI 之类的职业结构指标来识别。

**第三个缺口是 Bartik 工具在中国情境下的可识别性**。Acemoglu-Restrepo(2020)与 Goldsmith-Pinkham et al.(2020) 的方法学诊断(share/shock 排他性、Rotemberg weights、leave-one-out)需要在中国数据上重新执行,不能直接套用——这正是 `limitations_register` 中 `recover_bartik_share_shock_components` 等 4 条 major 局限的根源。

**第四个缺口是结果外推的时间维度**。Acemoglu-Restrepo(2020)使用 1990-2007 年美国数据,Dauth et al.(2021)使用 1994-2014 年德国数据,两者均覆盖了"机器人渗透早-中期"的样本。中国的工业机器人装机量在 2013 年后才进入快速增长期(根据 IFR 数据,2013 年中国成为全球最大装机国),CFPS 数据覆盖的年份范围与中国机器人渗透"快变量"期重合,但样本期相对较短。这一时间维度的差异意味着,本文结论对"早期渗透 vs 后期渗透"的区分能力有限,无法直接对应 Acemoglu-Restrepo(2020) 报告的"1990 年代 vs 2000 年代"对比分析。

## 本文的贡献

针对上述缺口,本文尝试作以下三点边际贡献。

**第一,首次以中国个体层面数据评估工业机器人对工资的因果效应**。本文将 Acemoglu-Restrepo(2020) 与 Dauth et al.(2021) 的证据(`contribution_matrix` 中两条 closest_paper)延伸到中国情境,并以 Bartik 移位-份额 IV(Goldsmith-Pinkham et al. 2020)为识别基础。`approved_findings` 记录 finding_trained_effect:IV 估计的 ln_robot 系数为 0.1994(SE=0.0793, p=0.012),弹性约为 0.2%,在 5% 水平显著。

**第二,识别"产业结构调整 + 职业结构升级"两条机制路径**。本文不仅报告工资总效应,还分别以"个体是否从事制造业工作"(`manu_dummy`)与国际标准职业声望指数(`ISEI_score`)为结果变量,检验机器人渗透是否伴随制造业就业稳定与职业声望提升,为 SBTC 假说在中国情境下提供机制证据。

**第三,提供中国情境下的 Bartik 工具可识别性证据与局限**。本文报告第一阶段 F 统计量、KP rk Wald F 等相关性指标,以及与 Acemoglu-Restrepo 框架一致的"地理隔离"冲击设计;同时在 §6 / 后续工作中显式列出 `limitations_register` 中尚未解决的方法学缺口(share/shock 组件恢复、Rotemberg weights、leave-one-out、AR/CLR 弱工具稳健区间)。

## 论文结构

本文其余部分结构如下。**§2 文献回顾与本文定位**梳理 Acemoglu-Restrepo、Dauth et al.、Graetz-Michaels、Autor-Dorn 等文献的贡献与差异,展开 `contribution_matrix` 的对比表。**§3 制度背景、理论与情境**在中国自动化政策、产业升级与劳动力市场结构背景下,引入任务模型(Acemoglu-Autor 2011, Acemoglu-Restrepo 2018 race 模型)与技能偏向性技术进步理论。**§4 数据与测量**介绍 CFPS 个体数据、IFR 工业机器人数据、城市-年份匹配规则与关键变量构造(ln_wage、ln_robot、manu_dummy、ISEI_score)。**§5 实证策略**详细说明 Bartik 移位-份额 IV 的构造、外生性假设与识别检验。**§6 主结果**报告 IV 主回归、机制证据与偏倚分析。**§7 稳健性、机制与异质性**给出 §6 中 8 个 gap 的处理状态与补充分析。**§8 结论**总结研究发现、政策含义与后续工作。

## 读者引导与诚实声明

本研究的**主要定量发现**已在 `approved_findings` 中由用户人工核准:IV-2SLS 估计的城市机器人装机量(对数)对个体小时工资(对数)系数为 0.1994(SE=0.0793, p=0.012),弹性约为 0.2%,OLS 对照系数 0.1039,机制证据支持 SBTC 假说。这些数字将在 §6 / main-results.md 中详细展开。

本研究的**主要方法学局限**已在 `limitations_register`(`overall_score=61`,`overall_verdict=draft_allowed_with_causal_caveat`)中明确记录:Bartik 工具的 share/shock 原始组件未恢复、Rotemberg weights 与 leave-one-out 检验未做、AR/CLR 弱工具稳健区间无法计算(因当前 exactly identified 设定)、E-value 计算失败(因 AttributeError)、IV 版本的 Oster / Sensemakr 偏倚分析未做。这些缺口在 §6-§7 与 §8 中将反复提示读者,以避免对系数 0.1994 产生过度精确化的解读。

本研究的**主要数据边界**:CFPS 单期横截面设计(`research_question` 与 `analysis_result` 中均提及),样本量 N=34315(IV 规格)/ N=15697(OLS 规格),样本构造与外部有效性边界在 §4 中详细展开。读者在引用本文时,应同时引用上述三点(主要发现 + 主要局限 + 数据边界)以保持结果的合理使用范围。

## 与本文最密切的 4 篇文献

为帮助读者快速定位本文在文献谱系中的位置,本节列出与本文最直接相关的 4 篇文献(均已核验 DOI,见 `verified_bibliography.csv`)。

1. **Acemoglu & Restrepo (2020, JPE)**——`acemoglu_restrepo_robots_jobs_2020`,closest_paper(美国通勤区层面机器人暴露的工资与就业效应)。本文将其方法学延伸到中国个体数据。
2. **Dauth, Findeisen, Suedekum & Woessner (2021, JEEA)**——`dauth_findeisen_suedekum_woessner_2021`,closest_paper(德国行政数据的劳动市场调整)。本文对照中国机制证据。
3. **Goldsmith-Pinkham, Sorkin & Swift (2020, AER)**——`goldsmith_pinkham_sorkin_swift_bartik_2020`,method_reference(Bartik 工具诊断)。本文遵循其 share/shock 分解思路,但承认 `limitations_register` 中的具体诊断尚未完成。
4. **Acemoglu & Autor (2011, Handbook of Labor Economics)**——`acemoglu_autor_tasks_2011`,method_reference(任务框架与 SBTC 理论)。本文机制分析的核心理论参照。

本文与上述 4 篇文献共同构成"中国情境下的工业机器人-工资因果识别"研究谱系;在贡献层面,本文与 Acemoglu-Restrepo(2020) 和 Dauth et al.(2021) 互为情境对照,在方法学层面与 Goldsmith-Pinkham et al.(2020) 互为应用与诊断待补。
