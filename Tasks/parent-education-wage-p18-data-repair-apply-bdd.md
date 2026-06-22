# P18 Data Repair Apply Gate BDD

P18 的目标是把 P17 审阅后的数据修复候选应用成新的分析数据集，并让完整论文分支可以重新进入 P13-P16。它是本地确定性能力，不调用 AI，不改变 UI 设计。

## 行为 1：没有 P17 预检时不能写修复数据

Given 项目还没有 `parent_education_wage_p17_data_repair_preflight.json`
When 用户请求 P18 apply
Then 系统返回 blocked 状态
And 不创建 `Data/Interim/parent_education_wage_repaired.csv`
And 不修改 `Data/Final/cfps_robot_reallocation.csv`

业务规则：P18 只能应用已审阅的候选账本，不能凭空猜修复方案。

## 行为 2：缺少人工确认时不能写修复数据

Given P17 已生成修复候选账本
When 请求缺少 reviewer、note、confirmation 或 education years mapping confirmation
Then 系统拒绝写入
And 不创建新数据集
And 不更新 P12 dataset path

业务规则：P18 是正式写入门禁，必须保留人工确认痕迹。

## 行为 3：确认后只写 Data/Interim 新数据集

Given P17 推荐 `famconf_parent_highest_education`
And 用户确认 `edu_last -> education_years` 映射
When 用户执行 P18 apply
Then 系统创建 `Data/Interim/parent_education_wage_repaired.csv`
And 新数据集包含 `parent_education`、`education_years`、`experience`
And 原始 `Data/Final/cfps_robot_reallocation.csv` 哈希不变
And P18 写出 JSON 和 Review 审计产物

业务规则：修复数据只能写入 interim，不覆盖正式原始分析数据。

## 行为 4：P18 后 P13-P16 可以进入完整模型结果分支

Given P18 已经写出修复数据集
When 重新运行 P13-P16
Then P13 使用修复数据集
And P14 真实执行最小 OLS
And P16 返回 `can_claim_model_result=true`
And 系统仍不能跳过人工审阅声称投稿级完整论文

业务规则：产品功能完成的最小门槛是真实 run evidence，而不是 UI 上显示完成。

