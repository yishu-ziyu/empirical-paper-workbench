# P12-0 Design Tree / Pre-PRD BDD

## SDD

目标：P9 正式 VariableRoleSet 保存成功后，不能直接写 DesignSpec 或跑模型。必须先生成一份 P12-P16 设计树，说明后续每一支怎么走、什么时候回退、什么时候必须人工签收、哪些动作仍然禁止。

## 行为 1：设计树承接 P9 已保存状态

Given P11 source contract 已签收
And P9 formal VariableRoleSet 已保存
When 项目进入 P12-0
Then 设计树必须明确 `P9 已正式保存`
And 指向 `state/product/variable_roles.json`
And 说明下一步是 P12 DesignSpec Preflight，不是模型执行

验证的业务规则：正式变量表保存成功只打开设计规格入口，不等于可以跑回归。

## 行为 2：设计树覆盖 P12-P16 全链路

Given 后续链路包含方法规格、运行计划、模型执行、初稿导出和用户验收
When 用户查看 P12-0 设计树
Then 文档必须列出 P12、P13、P14、P15、P16
And 每个阶段都有验收标准
And 每个阶段都有回退或阻断路径

验证的业务规则：后续开发看的是分支树，不是一串模糊 todo。

## 行为 3：仍然禁止 run id 和模型执行

Given 当前只完成 P12-0 设计树
When 用户查看项目状态或仪表盘
Then 文档和仪表盘都必须说明不得创建 run id
And 不得运行模型
And P14 必须等 P13 RunPlan 人工批准后才允许

验证的业务规则：设计树不是执行授权。

## 边界条件

- 不新增依赖。
- 不写 `state/product/design_spec.json`。
- 不写 `state/product/run_plan.json`。
- 不创建 run id。
- 不执行模型。
- P12 DesignSpec Preflight 必须另起 BDD/TDD。
