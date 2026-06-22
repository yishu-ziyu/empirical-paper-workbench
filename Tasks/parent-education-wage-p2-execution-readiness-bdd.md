# P2 执行准入 BDD：父母教育工资 Demo 线

日期：2026-06-17

## 阶段目标

P2 的目标不是跑模型，而是解除或精确记录 P1-C 的执行阻塞：补真实字段候选、形成变量口径 draft、清理设计草案旧题污染，并给出是否可进入真实方法执行的准入结论。

## 行为 1：字段补证只生成候选，不直接写正式变量角色

Given P1-B 显示 `father_education`、`mother_education`、`parent_education`、`hukou` 缺失
When P2 扫描本地字段来源和已存在的 variable role candidates
Then 系统必须为每个缺失字段生成补证状态、候选来源和下一步动作，但不能写 `state/product/variable_roles.json`

业务规则：字段补证是证据层，不是正式变量确认。

## 行为 2：变量口径只能形成 draft，不能替用户做产品决策

Given 父母教育字段尚未全部绑定
When P2 生成变量口径建议
Then outcome、treatment、controls 和 moderators 可以进入 draft，但父母教育合成规则必须标为需要人工确认

业务规则：父母教育用父亲、母亲、最高值、均值还是分列进入模型，是研究口径决策，不能静默提升为正式状态。

## 行为 3：设计草案必须清理旧 robot 题目污染

Given `Tasks/parent-education-wage/design.json` 的 code stub 残留 `robot_exposure`、`bartik_iv` 或 `robot_density`
When P2 执行设计草案修复
Then 修复后的草案不能再包含这些旧题变量，并且必须保留不写正式 DesignSpec 的边界

业务规则：旧题污染必须从当前任务草案中移除，否则执行准入判断不可信。

## 行为 4：执行准入必须保留 blocked ledger

Given 父母教育核心字段仍未真实绑定
When P2 生成执行准入账本
Then 系统必须输出 `execution_preflight_allowed=false`、不创建 run id，并说明阻塞原因

业务规则：没有核心字段时，正确结果是 blocked ledger，不是假执行。

## 行为 5：Product Control 暴露 P2 状态

Given P2 是 P1-C 之后的下一阶段
When 用户打开当前 React 产品控制面
Then 前端必须能看到 P2 执行准入状态，并且刷新必须通过显式 POST

业务规则：P2 是产品控制台下一阶段，不应只存在 CLI 或隐藏 JSON。

## 待确认边界

- 父母教育最终合成口径需要人工确认；本阶段只给 draft。
- 若真实数据源没有父母教育字段，本阶段只能输出数据缺失阻断，不替换研究题目。
- 本阶段可以修复 `Tasks/parent-education-wage/design.json` 草案，但不写 `state/product/design_spec.json`。
