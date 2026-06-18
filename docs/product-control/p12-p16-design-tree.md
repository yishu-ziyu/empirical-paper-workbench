# P12-0 Design Tree / Pre-PRD

## 当前真实状态

P9 已正式保存。正式变量角色集位于 `state/product/variable_roles.json`，状态为 `approved`，数据文件为 `Data/Final/cfps_robot_reallocation.csv`。

已保存的角色边界：

- outcome: `ln_wage`
- treatment: `parent_education`
- controls: `age`, `female`, `urban`, `edu_last`, `experience`
- source fields: `father_education`, `mother_education`
- construction: `parent_education = max(father_education, mother_education)`

这一步不是模型执行。P12-0 只画清 P12-P16 的设计树和阻断关系，不写正式 DesignSpec，不写 RunPlan，不创建 run id，不运行模型。

## 设计树

| 阶段 | 输入 | 产出 | 验收标准 | 回退路径 |
| --- | --- | --- | --- | --- |
| P12 DesignSpec Preflight | `state/product/variable_roles.json`、P11 source contract、P9 保存记录 | 可审阅的方法规格预检草案 | 写清 outcome/treatment/control 口径、可选方法、识别假设、不可运行原因；明确 `can_create_run_id=false` | 方法口径不清时回到 P12-0；变量角色不一致时回到 P9 |
| P13 RunPlan Approval | P12 预检草案 | 可人工批准的 RunPlan 候选 | 人工 reviewer/note/confirmation 完整；RunPlan 仍不能自动执行 | 审批未通过回到 P12 修订 |
| P14 Model Execution And Evidence Ledger | 已批准 RunPlan | run id、日志、结果表、证据账本 | 只在 P13 批准后创建 run id；输出可复现命令、输入数据哈希、结果文件路径 | 执行失败时生成问题清单，不伪造结果 |
| P15 Draft Generation And Export | P14 结果证据账本或阻断问题清单 | `paper_draft.docx` / `paper_draft.pdf` 或半成品论文 + 红标问题清单 | 初稿中的每个实证结论都能追溯到证据；证据不足处明确标红 | 证据不足回到 P14 或 P12/P13 补设计 |
| P16 User Acceptance And Satisfaction Loop | 初稿、证据账本、问题清单 | 用户签收、修改请求或下一轮补证任务 | 用户能判断“可提交/需修改/需补证”；满意度问题进入任务队列 | 修改请求回到 P15；方法或数据争议回到 P12 |

## 停机条件

必须停下问用户的情况：

- 需要删除或大规模重写现有文件。
- 需要安装新依赖。
- 需要访问外部服务、账号、密钥或付费 API。
- 同一阶段测试连续失败两次且无法定位到明确修复点。
- 当前目标和项目现有结构冲突。
- 需要用户做产品决策，例如是否接受某个方法口径、数据口径或论文交付标准。

## 不允许改动的范围

- 不覆盖 `state/product/variable_roles.json`，除非进入新的 P9/P12 明确审批流程。
- 不写 `state/product/design_spec.json`，P12-0 只是设计树，不是 DesignSpec。
- 不写 `state/product/run_plan.json`。
- 不创建 run id。
- 不运行模型。
- 不把半成品、候选稿或缺证据结论伪装成正式论文结果。

## P12 执行入口

下一步进入 P12 DesignSpec Preflight。该阶段必须重新走 SDD / BDD / TDD：

1. SDD：写清方法规格预检的业务目标、输入、输出、边界。
2. BDD：写 3-8 条 Given / When / Then 行为，解释每条验证的业务规则。
3. TDD：先写失败测试，确认失败原因是 P12 服务或产物尚不存在。
4. 实现：只写让测试通过的最小后端/API/UI/文档。
5. 复核：运行 scoped tests、编译、浏览器验收，并更新 `WORKFLOW_STATUS.md`、`Tasks/todo.md` 和仪表盘状态。
