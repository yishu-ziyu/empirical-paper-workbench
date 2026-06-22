# P17 Data Repair Preflight BDD

## 目标

P17 承接 P13-P16 阻断交付分支，进入数据修复预检。它只生成可审阅的数据修复候选账本，判断 `parent_education` 与 `experience` 能否从本地 CFPS 源表和当前分析样本中可追踪地补齐；不直接覆盖 `Data/Final/cfps_robot_reallocation.csv`，不重跑 P13-P16，不创建 run id，不运行模型。

当前只读检查结论：

- 当前分析样本 `Data/Final/cfps_robot_reallocation.csv` 有 34315 行、16 列，年份为 2020 和 2022，含 `pid/year/age/edu_last/ln_wage`，缺 `parent_education` 和 `experience`。
- 2020/2022 CFPS person 表可按 `pid` 合并，并含 `qv102`（您14岁时父亲教育程度）和 `qv202`（您14岁时母亲教育程度）。
- 2020/2022 CFPS famconf 表可按 `pid` 合并，并含 `tb4_a20_f/tb4_a20_m` 与 `tb4_a22_f/tb4_a22_m`（父亲/母亲最高学历），覆盖率高于 person 表的 `qv102/qv202`。
- `experience` 可从当前样本已有 `age` 与 `edu_last` 派生候选，但必须记录公式、负值处理和缺失处理，不能静默写入正式数据。

## 行为用例

### 行为 1：识别当前阻断字段和可用修复源

Given P16 验收包显示真实 CSV 缺 `parent_education` 和 `experience`
When 用户运行 P17 数据修复预检
Then 系统读取当前 CSV 表头、P12 公式和 P13 缺列清单，并输出待修复字段列表。

业务规则：P17 必须从上一阶段真实阻断出发，不能另起一个与 P13-P16 无关的数据清洗任务。

### 行为 2：为父母教育字段生成候选来源和覆盖率

Given 本地 CFPS 2020/2022 源表存在 person 与 famconf 候选字段
When P17 扫描候选来源
Then 系统为 `parent_education` 输出至少两类候选：`qv102/qv202` 个人问卷候选、`tb4_a20_f/tb4_a20_m` 与 `tb4_a22_f/tb4_a22_m` 家庭关系表候选，并记录按 `pid/year` 或 `pid` 合并后的覆盖率。

业务规则：父母教育不能只写“有候选”，必须让审阅者看见来自哪个源表、哪个字段、覆盖了多少当前样本。

### 行为 3：父母教育构造只进入候选账本

Given 候选源字段中存在父亲教育和母亲教育
When P17 生成修复建议
Then 系统建议 `parent_education = max(father_education, mother_education)` 作为候选构造，并把负值、`79` 等异常编码列为清洗规则待审阅项。

业务规则：P5/P11 已签收的口径是 `max(father_education, mother_education)`，P17 可以沿用该口径生成候选，但不能在未经审阅时覆盖正式 CSV。

### 行为 4：为 experience 生成可审阅派生候选

Given 当前 CSV 已有 `age` 和 `edu_last`
When P17 生成 `experience` 修复建议
Then 系统输出候选公式、缺失/异常处理和覆盖率，例如 `experience = max(age - education_years - 6, 0)`，并标记它是派生候选而非原始调查字段。

业务规则：`experience` 是模型控制变量，若来自派生公式，必须在证据账本中显式说明来源和限制。

### 行为 5：预检不改正式数据、不解锁模型

Given P17 运行前 P13-P16 处于阻断分支
When P17 生成数据修复预检
Then 只允许写 `Results/json/parent_education_wage_p17_data_repair_preflight.json` 和 `Reviews/parent_education_wage_p17_data_repair_preflight.md`，不得修改 `Data/Final/cfps_robot_reallocation.csv`，不得写 DesignSpec/RunPlan，不得创建 run id。

业务规则：数据修复要先给人审，不允许把候选合并静默变成正式模型数据。

### 行为 6：修复预检给出下一步分支

Given P17 已生成候选账本
When 审阅者查看结果
Then 系统明确给出下一步：若覆盖率和清洗规则可接受，进入 P18 数据修复 apply gate；若覆盖不足，返回 P4/P11 补 source metadata 或人工换源。

业务规则：P17 的完成标准是让下一步能决策，不是直接宣称完整论文分支已经恢复。

## 需要确认的边界条件

- `parent_education` 优先使用 person 表 `qv102/qv202`，还是 famconf 表 `tb4_a20_f/tb4_a20_m`、`tb4_a22_f/tb4_a22_m`；当前只读检查显示 famconf 覆盖率更高。
- 负值编码和 `79` 的处理规则：是否统一视为缺失。
- `experience` 的派生公式是否采用 `max(age - education_years - 6, 0)`；`edu_last` 是学历等级，不一定等于受教育年限，是否需要先映射为 education years。
- P18 是否允许写一个新的修复后数据文件，例如 `Data/Interim/parent_education_wage_repaired.csv`，而不是覆盖 `Data/Final/cfps_robot_reallocation.csv`。

## 不允许改动范围

- 不覆盖 `Data/Final/cfps_robot_reallocation.csv`。
- 不写正式 `state/product/design_spec.json`。
- 不写正式 `state/product/run_plan.json`。
- 不创建 run id。
- 不运行 OLS 或其他模型。
- 不把 P17 候选账本当作完整论文证据。
