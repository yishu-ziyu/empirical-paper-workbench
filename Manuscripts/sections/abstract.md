# Abstract

本文以中国劳动力微观调查(CFPS)与 IFR 国际机器人联合会工业机器人装机数据构建城市-年份匹配样本,系统评估工业机器人渗透对中国个体工资水平的影响。

**研究问题**。在中国当前自动化快速渗透的发展阶段,工业机器人采用是否提升劳动者小时工资?该问题对"技能偏向性技术进步"假说在中国情境下的适用性、以及自动化红利在个体间的分配具有直接含义。

**识别策略**。本文采用 Acemoglu & Restrepo (2020, JPE) 与 Dauth et al. (2021, JEEA) 在机器人研究中的标准做法,构造 Bartik 移位-份额工具变量(`method_gate_report` 中 method_subtype=bartik_shift_share_iv;份额项来自基期中国细分制造业行业就业份额,冲击项来自国际行业层面的机器人装机增速),以"地理隔离"的冲击设计缓解反向因果(高工资地区企业更有能力承担自动化投资)与遗漏变量(地区技术偏好、产业结构)问题。该方法学基础见 Goldsmith-Pinkham, Sorkin & Swift (2020, AER) 关于 Bartik 工具的诊断框架。

**数据与样本**。CFPS 个体数据合并城市-年份工业机器人装机量;主回归样本量 N=34315(IV 规格,见 `regression_tables` table_1 / table_3 / table_4),对比样本 N=15697(OLS 规格,见 `regression_tables` table_2)。

**主回归结果**(`approved_findings` 记录, finding_trained_effect;同见 `regression_tables` table_1 中 ln_robot 行)。IV-2SLS 估计的城市机器人装机量(对数)对个体小时工资(对数)系数为 0.1994(SE=0.0793, p=0.012,在 5% 水平显著),弹性约为 0.2%。OLS 系数为 0.1039(SE=0.0059, t=17.6, p<0.01,见 `regression_tables` table_2)。IV 系数绝对值大于 OLS 系数,提示 OLS 存在向下的衰减偏误(attenuation bias),而非被高估——这一方向性结论与 Bartik 工具在 OLS 上的常见偏误形态一致。第一阶段 F 统计量为 14685.77(远超 Staiger-Stock 经验阈值 10),Hausman 检验 F=283.99(p<0.01),拒绝 OLS 与 IV 等价的外生性原假设。

**机制证据**(`regression_tables` table_3 / table_4)。IV 估计显示,机器人渗透每提升 1%,个体从事制造业工作的概率提升约 0.08 个百分点(IV 系数 0.0798, t=3.58, p<0.01,机制一:产业结构),职业声望指数(ISEI_score)提升约 1 个单位(IV 系数 0.9995, t=3.58, p<0.01,机制二:职业结构)。两条机制路径共同支持"技能偏向性技术进步"假说,与中国当前制造业内部岗位结构升级的宏观叙事一致。

**稳健性**(`analysis_result`)。偏倚分析显示 Oster delta*=23.47(远高于经验阈值 1.0),Sensemakr 稳健值 RV=0.139(需 13.9% 强度未观测混杂方可推翻显著性,见 Cinelli & Hazlett 2020)。E-value(VanderWeele & Ding 2017)在本研究数据上计算失败(因 AttributeError,见 `analysis_result` _findings[evalue].severity=check_failed),本文不报告该指标的具体数值。**待 §6 补充**的稳健性检验包括:分样本回归(按性别、地区、教育)、替换工具变量、替换结果变量、替换控制变量集。

**方法门禁**(`method_gate_report`)。IV / Bartik 移位-份额方法的 pre_checks 全部 passed(design_spec_approved, run_plan_approved, variables_declared),blocking_items 为空,gate_status=yellow(通过,带可接受警告),formal_state_write=false(本研究不修改产品状态)。

**贡献**。本文将 Acemoglu-Restrepo(2020)、Dauth et al.(2021) 等关于工业机器人对工资影响的证据(均已核验,见 `verified_bibliography.csv` 中 acemoglu_restrepo_robots_jobs_2020、dauth_findeisen_suedekum_woessner_2021)延伸到中国情境,并以 Bartik 移位-份额 IV 为识别基础(Goldsmith-Pinkham et al. 2020)。本研究受限于单期 CFPS 横截面设计,中介效应分解与异质性分析的更细致处理留待后续工作。
