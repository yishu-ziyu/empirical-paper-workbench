# Project Management Reset

日期：2026-06-17

## 目的

本文件把当前项目从多条历史线收敛回一个可继续开发的管理面。

这次整理只做项目管理和文档收敛，不改产品代码、不改研究结果、不写运行态状态。

## 当前结论

主仓库：

- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`

参考仓库：

- `/Users/mahaoxuan/Desktop/经济学论文/StatspAI_跑通一次_CHARLS_DID`
- 兼容旧入口：`/Users/mahaoxuan/Desktop/StatspAI_跑通一次_CHARLS_DID` 现在是指向新位置的符号链接。

二者关系：

- CHARLS DID 是第一阶段 proof case，也是第二层 runtime 的来源样例。
- `实证论文项目模板` 是后续主线，承接第二层 runtime 和第三层产品工作台。
- 文件夹层面已收拢到 `/Users/mahaoxuan/Desktop/经济学论文/` 下面；仓库内容仍保持分仓边界。
- 不把 CHARLS 数据、论文、表格和哈希基线复制进主仓库。
- 主仓库只继承可复用的 workflow、agent spec、tool adapter、orchestrator、plugin/package 和产品状态机。

## 三层边界

第一层：真实研究跑通层。

- 目标：证明一个真实题目能从 idea + 数据跑到论文、表图和复现包。
- 当前代表：CHARLS DID 样例。
- 状态：已证明可跑通，但它不是主产品仓库。

第二层：Agent workflow runtime 层。

- 目标：把十步实证论文流程变成可路由、可校验、可回退、可迁移的 Agent 工作流。
- 当前代表：`workflows/`、`scripts/20-33_*`、`.codex/`、`plugins/statspai-empirical-workflow-runtime/`。
- 状态：P0-P5 已迁入主仓库；当前可用的验收入口是 `python3 scripts/25_agent_runtime_preflight.py`。

第三层：产品工作台层。

- 目标：把第二层状态和人工检查点变成用户可理解、可审阅、可展示的产品体验。
- 当前代表：`Product/`、`docs/product-control/`、`Tasks/product-control-demo-line.md`。
- 状态：主线已从抽象功能堆叠转向固定 Demo 线。

## 当前主线

当前主线不是继续补 CHARLS，也不是继续扩散旧的机器人题目。

当前主线是：

> 产品控制台 Demo 线：父母受教育水平对子女工资收入的影响

这个题目用于验证：

- 题目绑定和旧题污染清除。
- 任务书和 Agent Queue 是否能被用户理解。
- 数据、变量、方法、执行、草稿是否都有证据边界。
- Evidence Audit 是否能阻止没有 evidence_id 的结论进入正式层。
- 作品集叙事是否能在 3 分钟内讲清产品价值。

## 当前事实

- `Tasks/todo.md` 顶部已有 `2026-06-17 Product Control Console -> Portfolio MVP Demo Line`。
- `Tasks/product-control-demo-line.md` 已定义 P0-A 到 P0-D。
- `Tasks/parent-education-wage-01-design-bdd.md` 和目标测试已证明 `01_design` 可路由到 `02_literature`。
- `Tasks/statspai-runtime-bootstrap-bdd.md` 已证明 CHARLS runtime 底座迁入主仓库，且没有复制 CHARLS 论文产物。
- `Tasks/current-stage.md` 旧顶部仍保留 2026-05-17 的 P2-Z 视角，后续只作为历史快照，不作为当前唯一入口。

## 立即执行顺序

### P0-A：项目题目绑定核验

目标：

- 把当前产品入口、CLI、任务书和 Agent Queue 都绑定到 `parent-education-wage`。
- 查出并阻断工业机器人、CGSS 幸福感、旧 auto mode 包等旧题污染。

验收：

- 新增或更新 BDD 文档。
- 先写失败测试。
- 页面/CLI/任务文件不再把旧题当当前题目。
- 旧题内容如果仍存在，只能作为历史样例、fixture 或待审计风险出现。

### P0-B：Demo Agent Queue

目标：

- 显示 6 个用户能理解的任务：任务书、数据变量、方法设计、执行预检、证据审计、草稿边界。

验收：

- 每个任务有 owner、input、output、status、blocker、artifact path。
- 选择/派工动作不等于执行，不自动改 ResearchQuestion、VariableRoleSet、DesignSpec、RunPlan 或 Manuscript。

### P0-C：Evidence Audit

目标：

- 生成机器可读和人可读的证据审计。

验收：

- `Results/json/product_control_demo_evidence_audit.json`
- `Reviews/product_control_demo_evidence_audit.md`
- 至少覆盖旧题污染、placeholder、evidence_id 缺失、结果文件缺失、样本量/系数冲突、未验证引用。

### P0-D：作品集验收包

目标：

- 形成可展示材料，不再只靠代码和聊天解释项目价值。

验收：

- `docs/product-control/07_作品集Demo脚本.md`
- 流程图。
- Agent 分工图。
- 证据审计截图或文字审计报告。
- 当前做到哪里 / 还差哪里。

## 并行但不抢主线的任务

- `02_literature`：为 `parent-education-wage` 补真实文献计划、候选池、BibTeX 和贡献矩阵。
- P2-AA：Agent Task Queue execution backend selection。
- P2-M：真实变量候选提升到正式 VariableRoleSet 的人工保存链路。

这些任务都重要，但当前先用 P0-A 到 P0-D 收拢产品 Demo 线。否则会继续在产品、论文、runtime、旧题之间扩散。

## 工作规则

- 功能、API、产品流程和用户可见交互必须按本仓库 BDD/TDD 规则执行。
- 文档整理、状态说明和项目管理记录可以不进入完整 BDD/TDD，但必须写入 `Tasks/`。
- 复杂任务默认进入动态工作流：先探测当前状态，再拆执行队列、验证队列、压力场景和回收路径。
- 长程任务必须在 `Tasks/round-log.md` 记录压力测试：dirty worktree、旧路径兼容、旧题污染、运行态残留、跨仓库边界、端口缓存或工具不可用等复杂环境不能被绕开。
- 完成复杂节点时必须说明本轮暴露了什么问题、修正了什么、哪些风险留到下一轮；不能只报告“测试通过”。
- 不把 runtime state 当源码提交。
- 不把 LLM 推断伪装成真实统计结果。
- 不把 data/profile 成功误写成研究变量确认。
- 不自动写回正式论文、正式 bibliography、正式 RunPlan 或正式产品状态。
- 不为了演示效果跳过证据审计。

## 验证入口

项目管理整理后的轻量验证：

```bash
python3 scripts/21_route_next_workflow.py
python3 scripts/25_agent_runtime_preflight.py
python3 -m pytest tests/test_statspai_runtime_bootstrap.py tests/test_parent_education_wage_01_design_runtime.py -q
```

产品功能改动后的最低验证：

```bash
python3 -m unittest discover -s tests -v
node --check Product/web/assets/app.js
```

UI 改动必须额外做浏览器验收并保存证据路径。

## 下一个开发入口

下一轮如果继续开发，先做：

> P0-A Product Control Demo topic binding audit

第一步不是写实现，而是写 BDD：

- Given 当前固定题目是 `父母受教育水平对子女工资收入的影响`
- When 用户打开首页、任务书、Agent Queue、Review/Evidence Audit
- Then 当前视图和 CLI 输出不得出现旧题污染；若出现，必须进入 critical audit issue
