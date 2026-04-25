# Topic Discovery Memo

## 1. 当前策略

这一步不先把题目写死，而是从你已经掌握的数据母库和文献母库里反推最值得做的方向。

判断标准不是“听起来像论文”，而是四个条件同时满足：

1. 数据真的在你手里
2. 文献已经形成足够支撑
3. 能做出清楚的识别策略
4. 对本科毕业论文来说工作量可控

## 2. 当前最强的数据簇

### 数据簇 A：工业机器人 / 自动化

核心路径：

- `/Users/mahaoxuan/Desktop/实证数据库/外部源数据/IFR工业机器人数据（1993-2023年）`
- `/Users/mahaoxuan/Desktop/实证数据库/外部源数据/工业机器人安装密度(2006-2023年)`
- `/Users/mahaoxuan/Desktop/实证数据库/外部源数据/上市公司-工业机器人渗透度（2007-2022年）`

特征：

- 主题集中
- 时间跨度明确
- 文件类型友好，已有 `.dta` / `.xlsx`
- 和你现有阅读文献的重合度最高

风险：

- 单独使用时往往只是“处理强度数据”
- 真正做论文通常还需要和城市、行业、企业或个体数据匹配

### 数据簇 B：CFPS

核心路径：

- `/Users/mahaoxuan/Desktop/实证数据库/A001CFPS中国家庭追踪调查`
- `/Users/mahaoxuan/Desktop/实证数据库/外部源数据/CFPS2020`
- `/Users/mahaoxuan/Desktop/实证数据库/外部源数据/CFPS2022`

特征：

- 面板性质强
- 个体、家庭、经济、社区维度都有
- 适合做劳动、收入、家庭决策、技能、就业状态等问题

风险：

- 变量处理工作量大
- 如果和机器人/自动化强度数据匹配，合并口径要设计得很细

### 数据簇 C：CLDS

核心路径：

- `/Users/mahaoxuan/Desktop/实证数据库/A005CLDS中国劳动力动态调查数据`

特征：

- 劳动力市场主题非常直接
- 个体劳动、职业、工资、就业特征更贴近研究问题
- 从主题上看，比 CFPS 更“劳动经济学导向”

风险：

- 数据结构和变量体系需要花时间摸清
- 做成严格面板或重复截面时，要先看年份间一致性

### 数据簇 D：CMDS / 流动人口

核心路径：

- `/Users/mahaoxuan/Desktop/实证数据库/A019-中国流动人口动态监测CMDS数据2011-2018年`

特征：

- 很适合做迁移、流动、就业转换、城市吸纳、匹配问题
- 如果你想把“机器人冲击”放在迁移或城市劳动力重配置上，它很有潜力

风险：

- 题目会更偏“流动人口 / 城市配置”，不如 CLDS 那么直接贴匹配效率

## 3. 当前最强的文献簇

### 文献簇 A：机器人与就业/工资/技能

代表性来源：

- `Robots and Jobs Evidence from US Labor Markets.pdf`
- `Competing with Robots Firm-Level Evidence from France.pdf`
- `The Adjustment of Labor Markets to Robots.pdf`
- `工业机器人使用与制造业就业_来自中国的证据_闫雪凌.pdf`
- `工业机器人、技能升级与工资溢价_巫瑞.pdf`
- `Han - 2022 - The Impact of Industrial Robots on the Skill-Based Wage Gap.pdf`

说明：

- 这是你当前最成熟的一簇
- 既有国际经典，也有中文实证延伸

### 文献簇 B：自动化、任务、技能重配

代表性来源：

- `Artificial Intelligence, Automation and Work.pdf`
- `A task-based approach to inequality.pdf`
- `Automation and New Tasks How Technology Displaces and Reinstates Labor.pdf`
- `Tasks_Automation_Rise_US_Wage_Inequality_Acemoglu_Restrepo_2022.pdf`
- `Skill Mismatch and Skill Transferability Review of Concepts and Measurements.pdf`

说明：

- 这簇更偏理论框架和机制解释
- 很适合给论文的理论机制和文献综述做骨架

### 文献簇 C：劳动力市场匹配效率

代表性来源：

- `Looking into the Black Box A Survey of the Matching Function.pdf`
- `What Drives Matching Efficiency A Tale of Composition and Dispersion.pdf`
- `Labor Market Heterogeneity and the Aggregate Matching Function.pdf`
- `Measuring Job-Finding Rates and Matching Efficiency with Heterogeneous Jobseekers.pdf`
- `AI and Labor Market Matching Efficiency.pdf`
- `城市规模与劳动力市场匹配效率.pdf`
- `工业机器人应用对劳动力市场匹配效率的影响_方福前.pdf`

说明：

- 这是你当前最有辨识度的“研究切口”
- 它能把机器人文献和劳动搜索匹配文献接起来

### 文献簇 D：机器人与劳动力重配置 / 迁移 / 婚姻 / 非正规就业

代表性来源：

- `工业机器人、劳动力市场差异与婚姻决策.pdf`
- `机器人如何重塑城市劳动力市场：移民工作任务的视角.pdf`
- `机器人与非正规就业.docx`
- `A Study on the Impact of Industrial Robot Applications on Labor Resource Allocation.pdf`

说明：

- 这簇更适合做扩展题或机制题
- 需要更强的数据匹配能力

## 4. 候选研究方向排序

### 方向 1：工业机器人应用对劳动力市场匹配效率的影响

推荐等级：`S`

为什么最强：

- 你已经有明显的主题偏好
- 数据和文献都已经往这个方向集中
- 研究问题清楚、辨识度高
- 既可以接国际机器人文献，也可以接搜索匹配文献

最可能的数据组合：

- 机器人强度数据：
  - `IFR工业机器人数据（1993-2023年）`
  - `工业机器人安装密度(2006-2023年)`
- 微观或劳动调查数据：
  - `CLDS`
  - 备选 `CFPS`

潜在单位：

- 省份-年份
- 城市-年份
- 个体-地区-年份

识别空间：

- 基准 DID / 双向固定效应
- 地区或行业暴露度
- Shift-share / Bartik 类设计

当前问题：

- “匹配效率”具体怎么测，必须尽快定清楚
- 需要决定是做宏观匹配效率还是个体层匹配结果

### 方向 2：工业机器人应用对工资分布 / 技能溢价的影响

推荐等级：`A`

为什么强：

- 文献成熟
- 指标设计相对清晰
- 比“匹配效率”更容易落到可操作变量上

最可能的数据组合：

- 机器人强度数据
- CFPS / CLDS 个体工资和教育变量

优点：

- 更容易形成基准回归
- 本科论文更容易控制工作量

缺点：

- 题目相对常规
- 新意可能弱于“匹配效率”

### 方向 3：工业机器人应用对就业重配置 / 非正规就业 / 劳动力流动的影响

推荐等级：`A-`

为什么值得留：

- 你已经有对应文献
- 和 CMDS / CFPS 的潜在连接很强

优点：

- 机制空间更丰富

缺点：

- 数据匹配和定义工作量更大
- 更容易超出本科论文的可控边界

### 方向 4：最低工资 / 劳动力市场分割 与匹配效率

推荐等级：`B+`

为什么不排前二：

- 数据也有
- 但你当前文献积累明显不如机器人线集中

适合：

- 作为备选策略
- 或者如果机器人线最后匹配不上微观数据时转向

## 5. 我的当前判断

如果现在就要决定“先往哪条线推进”，我会建议：

### 第一优先

**工业机器人应用对劳动力市场匹配效率的影响**

但这里的真正下一步不是马上写标题，而是把这个方向拆成两条可验证分支：

1. `宏观匹配效率版`
   - 地区 / 省份 / 行业层面
   - 更容易先跑出来

2. `微观匹配结果版`
   - 个体就业状态 / 工作转换 / 工资匹配
   - 更新颖，但更复杂

对于本科论文，我当前更推荐先从 `宏观匹配效率版` 起步，再决定是否下钻到微观。

## 6. 立刻要做的事

下一步不再是泛泛看目录，而是进入“可行性验证”：

1. 确定机器人强度数据里最适合的一份主数据
2. 确定 CLDS 或 CFPS 哪个更适合作为匹配结果承载数据
3. 明确“匹配效率”在你这篇论文里的操作化定义
4. 抽出一组最小变量，先拼出第一版分析样本

只有这四步过了，课题才算真正从“想法”变成“可做”。

