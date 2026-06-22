# P13-P16 Demo Closure BDD

## 目标

把父母教育工资 demo 线从 P12 预检继续推进到 P16 用户验收。系统必须先校验真实数据能否支持 RunPlan；能跑时执行最小 OLS，不能跑时交付半成品论文、红标问题清单和下一步补证动作，不能伪造模型结果。

## 行为 1：P13 必须清理旧题正式状态污染

Given `state/product/design_spec.json` 或 `state/product/run_plan.json` 属于旧机器人题目
When 用户运行 P13-P16 closure
Then 系统把旧正式状态归档到 `state/product/archive/p13_p16_stale_formal_state/`
And 当前闭环不得继续消费旧机器人 DesignSpec 或 RunPlan。

业务规则：产品闭环不能被旧题状态污染，否则用户会以为当前题目已经有可运行计划。

## 行为 2：P13 必须用真实 CSV 列校验 RunPlan

Given P12 预检公式需要 `ln_wage`、`parent_education`、`age`、`female`、`urban`、`edu_last`、`experience`
When 真实数据集缺少其中任意列
Then P13 返回 `blocked_missing_dataset_columns_for_run_plan`
And 不写正式 RunPlan，不创建 run id。

业务规则：RunPlan approval 不能只看变量角色签收，还必须看分析数据集里是否真的有列。

## 行为 3：P14 不能在 P13 阻断时运行模型

Given P13 因数据列缺失阻断
When 系统进入 P14
Then P14 写出 execution evidence ledger，状态为 `execution_blocked_missing_dataset_columns`
And `run_id=null`、`executed_regression=false`。

业务规则：模型执行必须由可运行 RunPlan 驱动，不能为了闭环伪造结果。

## 行为 4：P15 必须交付半成品论文和问题清单

Given P14 没有真实模型结果
When 系统进入 P15
Then 系统保留或生成半成品 `paper_draft.docx` 路径
And 写出红标问题清单，明确缺少哪些字段、为什么不能报告回归结果。

业务规则：证据不足时也要给用户可读交付物，而不是只给后端错误。

## 行为 5：P16 必须给出用户验收包

Given P15 已生成半成品交付包
When 系统进入 P16
Then P16 生成用户验收包，说明当前可验收内容、不能声称的内容和下一步补齐动作
And 标记 `can_claim_complete_paper=false`。

业务规则：闭环不是“强行完整论文”，而是把当前可交付状态和用户下一步讲清楚。

## 行为 6：控制台必须说人话

Given 项目已经推进到 P16 阻断分支
When 用户打开工作流控制台
Then 首屏必须显示“现在能交付什么”“还缺什么”“下一步做什么”
And 不再把主要空间留给开发阶段术语。

业务规则：控制台服务项目负责人，不服务 Agent 自嗨。

## 边界条件

- 不安装新依赖。
- 不使用旧机器人题目的 DesignSpec、RunPlan 或结果。
- 如果真实 CSV 缺列，不运行模型。
- 如果真实 CSV 列齐全，只允许运行 P12 中 ready 的 baseline OLS。
- DID/IV/RDD 继续阻断，不能因为推进到 P16 而自动启用。
