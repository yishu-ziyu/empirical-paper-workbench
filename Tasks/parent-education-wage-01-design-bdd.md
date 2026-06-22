# parent-education-wage 01_design BDD

目标：把“父母的受教育水平对子女工资收入的影响”接入第二层运行时，让路由从 `01_design` 推进到 `02_literature`。

## 行为用例

### 行为 1：研究设计入口存在

Given 用户选择题目“父母的受教育水平对子女工资收入的影响”
When 运行时检查 `01_design`
Then 根目录必须存在 `research_design.md`、`causal_question.yaml`、`design_risk.md`

业务规则：一个 idea 只有落成三份设计入口文件，才算完成第一步。

### 行为 2：因果问题可机器读取

Given 研究设计已经写入根目录
When 代理读取 `causal_question.yaml`
Then 它必须能识别 treatment、outcome、population、primary_design、data_source

业务规则：后续 agent 不能靠读散文猜变量和识别策略。

### 行为 3：不能沿用串题变量

Given 旧任务材料里出现过工业机器人变量
When 本次 01_design 产物生成
Then 三份入口文件不得包含 `robot`、`机器人`、`bartik_iv`、`ln_robot`

业务规则：题目迁移必须清掉旧任务污染。

### 行为 4：artifact registry 登记完成

Given 三份入口文件已经存在
When router 解析 `tasks/artifact-registry.md`
Then `01` 步骤三项产物状态必须都是 `present`

业务规则：运行时只相信 registry 和文件系统，不相信聊天记录。

### 行为 5：下一步进入文献工作流

Given `01_design` 三项产物都存在且 registry 标记 present
When 执行 `python3 scripts/21_route_next_workflow.py`
Then 推荐工作流必须是 `02_literature`

业务规则：设计完成后，流水线应该前进到文献矩阵，而不是停在设计阶段。

## 边界条件

- 当前只完成运行时入口，不声称实证结果成立。
- 义务教育法分省实施时点尚未核验，列入 `design_risk.md`。
- CFPS 变量名需要在 04 数据门禁阶段用真实数据确认。
- 文献材料当前有 fallback stub，不能当成已完成文献综述。
