# Conclusion

本文以中国劳动力微观调查(CFPS)与 IFR 国际机器人联合会工业机器人装机数据构建城市-年份匹配样本,采用 Bartik 移位-份额工具变量识别策略,系统评估工业机器人渗透对中国个体工资水平的影响。本节总结研究发现、讨论局限、提出政策含义,并明确后续工作方向。

## 主要发现

**主回归结果**(`approved_findings` 记录, finding_trained_effect;同见 `regression_tables` table_1)。IV-2SLS 估计的城市机器人装机量(对数)对个体小时工资(对数)系数为 0.1994(SE=0.0793, p=0.012,在 5% 水平显著),弹性约为 0.2%。OLS 系数为 0.1039(SE=0.0059, t=17.6, p<0.01)。IV 系数大于 OLS 系数,提示 OLS 存在向下的衰减偏误(attenuation bias)而非被高估。第一阶段 F 统计量 14685.77(远超 Staiger-Stock 经验阈值 10),工具变量与内生变量高度相关;Hausman 检验 F=283.99(p<0.01)拒绝 OLS 与 IV 等价的外生性原假设。

**机制证据**(`regression_tables` table_3 / table_4)。机器人渗透对个体从事制造业工作的概率具有显著正向影响(IV 系数 0.0798, t=3.58, p<0.01),对国际标准职业声望指数(ISEI_score)同样具有显著正向影响(IV 系数 0.9995, t=3.58, p<0.01),与"技能偏向性技术进步"假说一致。两条机制路径共同支撑"工业机器人渗透—产业结构与职业结构升级—个体工资提升"的传导链条。

**偏倚分析**(`analysis_result`)。基于 OLS 估计的偏倚指标显示,Oster delta*=23.47(远超经验阈值 1.0),Sensemakr 稳健值 RV=0.139(需 13.9% 强度未观测混杂方可推翻显著性,见 Cinelli & Hazlett 2020)。需要说明的是,该偏倚指标基于 OLS 估计,直接外推到 IV 估计需要 IV 版本的偏倚分析(目前**未在本文档报告**)。

## 研究局限

`limitations_register`(`overall_score=61`,`overall_verdict=draft_allowed_with_causal_caveat`,`blocks_export_or_formal_claims=true`)记录了本研究的方法学局限,涵盖以下方面。

**第一,Bartik 移位-份额识别的可重复性问题**(`limitations_register` 中 major 项 `recover_bartik_share_shock_components`、`add_rotemberg_weights_review`、`add_leave_one_out_or_alternative_shock_check`、`write_exclusion_and_shock_exogeneity_review`)。当前 `bartik_iv` 已是聚合形式,share/shock 原始组件未在产物中恢复,因此 Rotemberg weights、leave-one-out 检验、排他性限制的审稿式论证均**未在本文档完成**。这意味着 Bartik 工具的识别强度虽高,但 share/shock 层的诊断不完整。

**第二,弱工具稳健性问题**(`limitations_register` 中 major 项 `add_weak_iv_robust_interval_or_caveat`)。由于当前 exactly identified 设定(单一工具变量),无法直接计算 Anderson-Rubin(AR)置信集或 Moreira(2003) CLR 稳健区间。这意味着 IV 系数的 95% 置信区间 [0.0439, 0.3549] 是基于标准正态假设,未在弱工具情形下重新校准。`reviewer_scorecard_report`(`overall_score=61`,`confidence_level=medium`)建议在主结论中加入因果表述 caveat。

**第三,E-value 计算失败**(`analysis_result` _findings[evalue].severity=check_failed,因 AttributeError)。E-value(VanderWeele & Ding 2017)作为评估未观测混杂对结果推翻能力的重要指标,在本研究数据上**无法计算**,本文不报告该指标的具体数值。这是除 AR/CLR 之外的第二处"指标缺失",共同提示结论对弱工具 / 未观测混杂的稳健性证据**不完整**。

**第四,样本构造的外部有效性**(`limitations_register` 中 minor 项 `explain_missing_drop_and_analysis_sample`)。从 raw rows 到可用样本的流失过程、缺失处理规则在 `sample_construction_log` 中有记录,但**本文未单独撰写一节详述**;CFPS 单期横截面设计的外部有效性边界也未在文中明确讨论。

**第五,Oster / Sensemakr 仅基于 OLS 估计**。`analysis_result` 中的偏倚指标(见本文 §5.5 / main-results.md §5.5)是基于 OLS 系数 0.1039 计算的;本研究 IV 系数 0.1994 的对应偏倚指标**未计算**。

## 政策含义

在以上局限的前提下,本文证据对政策制定仍有以下有限含义。第一,**自动化并非必然压低个体工资**——本研究 IV 证据显示,在中国当前发展阶段,工业机器人渗透伴随本地个体工资的微弱正向响应(弹性 0.2%);机制证据(制造业就业稳定 + 职业声望提升)进一步表明,自动化推动的是职业结构升级而非简单的劳动替代。第二,**教育与培训政策具有缓冲意义**——ln_robot 提升 1% 带来的 ISEI 提升(约 1 个单位)相当于多接受 0.18 年教育,提示针对低技能劳动者的再培训项目可与自动化政策协同推进。第三,**地区层面的渐进过渡**——IV 系数大于 OLS 系数提示本地企业自动化决策与高工资地区存在相互选择,直接外推到全国或长期效应需谨慎。

## 后续工作

基于 `limitations_register` 列出的方法学缺口,后续工作方向明确包括:(1) 恢复 Bartik share/shock 原始组件,补做 Rotemberg weights 与 leave-one-out 检验;(2) 在 exactly identified 设定下补充因果表述 caveat,或在工具变量数≥2 时计算 AR/CLR 稳健区间;(3) 排查 E-value 失败的 AttributeError 根因,补报偏倚分析证据;(4) 撰写样本构造与外部有效性边界的专门小节;(5) 计算 IV 版本的 Oster / Sensemakr 偏倚指标。

**审稿与导出状态**:`reviewer_scorecard_report` 中 `blocks_export_or_formal_claims=true`——在上述(1)-(5)未完成前,本文档不应被当作"可正式发表的成果"对待,而应作为方法学讨论与未来工作的起点。

## 局限与已有证据的对应关系

为方便读者交叉核验,下表将本节列出的 5 项局限与 `limitations_register` 中的具体条目做对应。

| 局限 | `limitations_register` 中对应条目 | 当前处理 |
|------|----------------------------------|----------|
| Bartik share/shock 原始组件缺失 | `recover_bartik_share_shock_components` (major) | **未在本文档解决** |
| Rotemberg weights 缺失 | `add_rotemberg_weights_review` (major) | **未在本文档解决** |
| Leave-one-out / alternative shock 缺失 | `add_leave_one_out_or_alternative_shock_check` (major) | **未在本文档解决** |
| 排他性限制 / shock exogeneity 论证不足 | `write_exclusion_and_shock_exogeneity_review` (major) | **未在本文档解决** |
| 弱工具稳健区间 (AR/CLR) 缺失 | `add_weak_iv_robust_interval_or_caveat` (major) | **未在本文档解决**,改用因果表述 caveat |
| 样本构造 / 外部有效性边界 | `explain_missing_drop_and_analysis_sample` (minor) | 部分讨论,但未单设小节 |
| IV 版 Oster / Sensemakr 缺失 | (隐含) | **未在本文档解决** |
| E-value 计算失败 | (隐含,见 `analysis_result`) | 已在 §5.5 / main-results.md 中明确声明 |

**对应统计**:本节 5 项局限中,前 5 项直接对应 `limitations_register` 中 major 级别的 5 条具体建议(并已合并为方法学 caveat 写回主结论),后 3 项为该 register 之外但同性质的方法学缺口。

最后需要强调,本文结论的"提示性"价值大于"决定性"价值:即便 IV 系数在 5% 水平显著且偏倚指标显示需极强未观测混杂方可推翻显著性,Bartik 工具的 share/shock 层诊断缺失、弱工具稳健区间缺失、E-value 失败这三重方法学缺口共同表明,系数 0.1994 的具体数值不应被作为"精确因果效应"对待,而应作为"在当前数据与方法下的最合理上限估计"来理解。读者在引用本文结果时,应同时引用上述局限,以避免对该系数产生过度精确化的解读。
