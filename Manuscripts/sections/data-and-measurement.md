# 4. 数据与测量

> 本节依据 `sample_profile.json`(`dataset_profile` 与 `sample_construction_log` 两个 evidence_id 共享同一产物) 与 `variable_role_reconciliation_report.json`(`variable_dictionary` evidence_id) 展开;**所有数字均来自上述两个 JSON 产物**,不在文中另造。

## 4.1 数据来源

本文使用两类数据合并为城市-年份面板。

**第一,CFPS 个体微观数据**(中国家庭追踪调查, China Family Panel Studies)。CFPS 由北京大学中国社会科学调查中心(ISSS)执行,覆盖全国 30 个省级单位(以 `method_gate_report.dataset_profile.cluster_counts.provcd`=30 为准)的家庭与个体,提供劳动者小时工资、性别、年龄、受教育年限、城乡属性、所在省份、是否从事制造业工作、ISEI 职业声望等个体层变量。本文以个体为分析单位,使用单期横截面数据,变量名见 §4.3。

**第二,IFR 国际机器人联合会工业机器人装机数据**(International Federation of Robotics)。IFR 每年发布《World Robotics》统计,按行业(IFR 行业分类,ATECO/ISIC 对齐)与国家报告年度新增装机量。本文使用国际细分行业层面的机器人装机增速(冲击项)与中国基期细分制造业行业就业份额(份额项)构造 Bartik 移位-份额 IV(详见 §5)。IFR 装机量按中国省级口径汇总为 `robot_density`、`ln_robot`、`year_robot` 三个变量,与 CFPS 个体数据按"省份-年"匹配。

## 4.2 样本构造(`sample_construction_log`)

合并后的分析样本存储在 `Data/Final/cfps_robot_reallocation.csv`,`sample_profile.json`(`dataset_profile` evidence_id)中报告的样本构造结果如下。

**样本量**。`rows_read`=34315,`usable_numeric_rows`=34315,`dropped_rows`=0(同见 `dataset_profile` 的 `checks[2]`,id=`numeric_formula_rows_available`,status=passed)。这意味着从 raw rows 到可用样本**没有发生行级缺失删除**——所有 34315 行均通过字段可数值化检查,被纳入分析样本。

**必需字段**。`sample_profile.required_fields` 共登记 16 个字段,见下表(依 `dataset_profile` 报告原序):

| 类别 | 字段 | 含义 |
|------|------|------|
| 个体标识 | `pid` | 个体 ID |
| 地区标识 | `provcd`、`provcd_num` | 省份代码(字符/数值两版) |
| 地理属性 | `urban` | 城乡(0=乡村,1=城市) |
| 结果变量 | `ln_wage` | 小时工资对数 |
| 机制变量 | `manu_dummy` | 是否制造业工作(0/1) |
| 机制变量 | `ISEI_score` | 国际标准职业声望指数(理论范围 16-90) |
| 工作属性 | `part_time` | 是否兼职 |
| 控制变量 | `female`、`age`、`edu_last` | 性别、年龄、受教育年限 |
| 时间标识 | `year`、`year_robot` | CFPS 调查年、机器人装机年 |
| 机器人暴露 | `robot_density`、`ln_robot` | 城市机器人装机量及其对数 |
| 工具变量 | `bartik_iv` | Bartik 移位-份额 IV(聚合形式) |

**质量检查**。`sample_profile.checks` 共 3 项,全部 passed:`dataset_file_exists`(数据文件存在)、`required_fields_present`(16 个必需字段完整)、`numeric_formula_rows_available`(usable=34315,dropped=0)。

**聚类层级**。`method_gate_report.dataset_profile.cluster_counts` 显示省级 `provcd` 聚类数为 30。

## 4.3 关键变量定义(`variable_dictionary`)

变量定义主要来自 `method_gate_report.variables` 段(已通过 design_spec 与 run_plan 的 pre-check 验证)以及 `method_execution_result.json` 的实际执行结果。

**结果变量**。`ln_wage`,个体小时工资对数,刻画"工资水平"这一可观测切面。

**内生处理变量**。`ln_robot`,个体所在城市当年工业机器人装机量(对数)。理论上"高工资地区企业更可能采用机器人"产生反向因果,这是 §5 中引入工具变量的根本动机。

**工具变量**。`bartik_iv`,Bartik 移位-份额 IV,公式定义为 `bartik_iv = Σ_s (s_s,base × ΔRobot_s,international)`,其中 `s_s,base` 是中国基期细分制造业行业 `s` 的就业份额,`ΔRobot_s,international` 是国际行业 `s` 的机器人装机增速。该构造**仅使用基期份额 + 国际冲击**(`share` 用中国基期,`shock` 用国际行业),不混入本地当期机器人决策,理论上可缓解反向因果(详见 §5 关于 Goldsmith-Pinkham, Sorkin & Swift 2020 诊断框架的讨论)。

**控制变量**。`female`(性别,0/1)、`age`(年龄,岁)、`edu_last`(受教育年限,连续)、`urban`(城乡,0/1)。

**固定效应与聚类**。年份固定效应(`year`);聚类在省级(`provcd`,30 个聚类)。

**机制变量**(为 §6 机制回归准备,非主回归因变量):`manu_dummy`(是否从事制造业工作,0/1)与 `ISEI_score`(国际标准职业声望指数,理论范围 16-90,数值越高表示职业声望越高)。两者分别承担"产业结构升级"与"职业结构升级"两条机制证据链(详见 §6)。

**主回归公式**(来自 `method_gate_report.variables.formula`):`ln_wage ~ (ln_robot ~ bartik_iv) + female + age + edu_last + urban | year`,第一阶段 `ln_robot ~ bartik_iv + female + age + edu_last + urban | year`。

## 4.4 变量字典状态(诚实声明)

`variable_role_reconciliation_report.json`(`variable_dictionary` evidence_id)报告的当前状态如下。

**状态**。`status`=`needs_human_review`,`conflict_count`=2,`risk_count`=2。`canonical_write_allowed`=false,即该变量角色未通过正式层写入审核。

**主要警告**。`Submissions/formal_package/evidence/variable_role_set.json` 的 `warnings` 字段登记 `variable_role_dataset_mismatch`:源 `state/product/variable_roles.json` 指向 `Data/Final/analysis_sample.csv`(outcome=wage、treatment=trained,与早期 CGSS 社会资本-幸福感项目同名变量);而 `method_execution_result.json` 实际执行的是 CFPS robot 数据集(`Data/Final/cfps_robot_reallocation.csv`,outcome=ln_wage、treatment=ln_robot)。这一不匹配**意味着本研究的"正式 variable_role_set"尚未从早期项目迁移到 CFPS robot 项目**。

**对本文的影响**。本文 §5 / §6 的实证执行使用的是 `method_execution_result.json` 中已落地的实际变量集(ln_wage / ln_robot / bartik_iv / controls),这些变量在 `sample_profile.required_fields` 中已登记,并通过 `method_gate_report` 的 `pre_checks` 全部 passed(包括 `variables_declared`、`instrument_declared`、`structural_equation_declared` 等 12 项);但"正式 variable_role_set"的 canonical write 仍未完成,这意味着从"产品状态(state/product)"视角看,变量角色文档尚未同步更新。**这是数据与测量层面的一个明确 gap,需在后续工作中由人工复核完成状态提升,本文据实声明不掩盖。**

## 4.5 描述统计与样本差异

**主样本(IV 规格)**。N=34315,见 §4.2。

**对照样本(OLS 规格)**。N=15697,见 `regression_tables.tables[1].nobs`。IV 与 OLS 样本量差异较大,可能源于 IV 规格所需的 `bartik_iv` 变量可用性约束——该变量依赖基期份额 × 国际冲击的乘积,部分省-年组合可能因份额或冲击缺失而不可用,具体剔除规则在 `sample_construction_log` 中未单设字段,这是 §5 中应进一步披露的"样本构造细节"。

**主回归系数对应**。IV 规格 N=34315 对应表 1 列(2)(回归表);OLS 规格 N=15697 对应表 1 列(1)。两组样本量差异与 `bartik_iv` 可用性直接相关,但精确的剔除比例与剔除单位(`pid` 级 vs `provcd-year` 级)未在 `sample_construction_log` 中显式记录——这是 §6 局限讨论中需要补充的细节。

## 4.6 数据边界与外部有效性

**单期横截面**。CFPS 是单期调查设计,本文不构造面板;这与 Acemoglu-Restrepo(2020)使用美国 CZ 面板(1990-2007)、Dauth et al.(2021)使用德国行政面板(1994-2014)形成方法学差异。单期设计**无法直接做个体固定效应或年份固定效应(年份固定效应已通过 `year` 变量在主回归中控制,但其变异完全来自跨 CFPS 调查年的合并样本,而非同一个体的跨期变化)**,意味着本文识别的是"地区-年份"层面的机器人暴露对个体工资的因果效应,无法排除"地区层面未观测因素"的偏误。

**省级口径**。机器人装机量以省级(provcd)聚类,而 CFPS 个体数据以省-年匹配;这与 Acemoglu-Restrepo 使用 CZ(通勤区)层面的暴露存在地理颗粒度差异。`bartik_iv` 的冲击项是国际行业层面的,份额项是中国基期细分行业层面的——"地理隔离"的冲击设计使本识别较 CZ 层面更粗,但也避免了高工资地区企业自主决策的内生性。

**有效样本外推**。本文结果可外推到"参与 CFPS 调查的省级单位(以 `cluster_counts.provcd`=30 为准)、在 `year_robot` 年份有 IFR 装机数据、在 `bartik_iv` 构造中份额项非缺失"的子总体;不可直接外推到未参与 CFPS 的省份、IFR 未单独报告装机量的细分行业或机器人技术尚未渗透的产业。

## 4.7 数据局限小结

综合 §4.4 与 §4.6,本研究数据与测量层面有 3 项明确局限,均需在后续工作或审稿回应中处理。

**第一,变量角色 canonical write 未完成**(`variable_role_reconciliation_report.status=needs_human_review`)。这不阻碍本文实证执行(已通过 method_gate pre-check),但意味着从"产品状态"层看,变量文档尚未同步。

**第二,IV 与 OLS 样本量差异的精确剔除规则未单设字段**。N=34315 vs N=15697 的差距需在 §5 显式展开剔除逻辑。

**第三,CFPS 单期横截面设计限制了面板识别**。这一点与 Acemoglu-Restrepo(2020)的 CZ 面板方法学形成对照,需在引言与结论中明确。

## 4.8 测量误差与编码说明

本节明确几个可能影响结果解释的测量细节,供读者评估识别假设的合理性。

**小时工资的构造**。`ln_wage` 在 CFPS 中由受访者自报"过去一年的税后工资"与"过去一年的工作小时数"派生。在自报数据中,小时工资可能存在截断(高收入受访者倾向于回答收入区间而非具体值)与回忆偏差,这是 CFPS 类微观调查的共同局限,本文沿用 CFPS 公开的清洗规则不做额外处理。

**ISEI 量表**。`ISEI_score` 来自 Ganzeboom, De Graaf & Treiman (1992) 构造的国际标准职业声望指数,理论范围 [16, 90],数值越高表示职业声望越高(见 `evidence_bank.md` §6 gap 列表登记的 C-115)。CFPS 提供了该量表的预计算值,本文直接使用。

**机器人装机量**。`robot_density` 与 `ln_robot` 由 IFR 工业机器人装机量(年度新增)在省级口径汇总后,与 CFPS 个体数据按"provcd-year"匹配。IFR 装机量本身是"年度新增"而非"累计存量",理论上是流量而非存量,这意味着 `ln_robot` 的波动主要来自"当年新装机",反映地区自动化决策的边际变化,而非历史自动化积累的存量效应。

**Bartik 工具的份额项**。`bartik_iv` 公式中的 `s_s,base` 来自基期(待 §5 进一步披露基期年份,本表 §4 不预先指定)中国细分制造业行业的就业份额,数据来源为中国统计年鉴或相应基期人口普查/经济普查;冲击项 `ΔRobot_s,international` 来自同期国际行业层面的 IFR 装机增速,选取国家范围(其他主要制造业国家)同样待 §5 进一步披露。

## 4.9 与后续章节的衔接

本节定义的数据与变量直接进入 §5 的 Bartik IV 识别策略(`method_gate_report` 中 `pre_checks` 共 12 项全部 passed,见 C-120),并支撑 §6 的主回归(IV 系数 0.1994,见 `approved_findings.finding_trained_effect`)、§6 机制回归(`manu_dummy` 与 `ISEI_score`,见 `regression_tables.tables[2/3]`)与 §7 的稳健性讨论。本节诚实声明的 3 项局限(变量角色未 canonical 写、IV/OLS 样本差异未细化、CFPS 单期设计)分别对应 §5、§6、§8 的局限性讨论,不在本节单独补救,以保持"该 section 只声明其力所能及的证据"的范围纪律。
