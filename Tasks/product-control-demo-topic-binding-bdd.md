# P0-A Product Control Demo Topic Binding BDD

目标：在继续开发前，把当前产品演示固定到 `父母受教育水平对子女工资收入的影响`，并把旧题目污染暴露成可审计阻断，而不是让旧 state 被系统继续信任。

## 行为 1：当前演示题目必须有唯一绑定

Given 当前产品演示线是 `parent-education-wage`
When 运行 P0-A 题目绑定审计
Then 报告必须声明期望题目为 `父母受教育水平对子女工资收入的影响`
And 报告必须声明期望 slug 为 `parent-education-wage`
And 报告必须给出是否可以进入 P0-B 的布尔结论。

业务规则：项目主导者需要先知道系统现在服务哪个题目，后续 Agent Queue 才不会继续沿用旧任务。

## 行为 2：旧 ResearchQuestion 不能被静默当作当前题目

Given `state/product/research_question.json` 仍保存机器人、培训工资或其他旧题目
When 运行 P0-A 题目绑定审计
Then 审计状态必须是阻断
And critical issues 必须包含 `research_question_mismatch`
And 系统不得自动改写该 state 文件。

业务规则：P0-A 是控制门，不是静默迁移器；它先让污染显形，再交给人工确认下一步修复。

## 行为 3：旧 SupervisorPlan 和 Agent Task Queue 必须被识别为 stale

Given `state/product/supervisor_plan.json` 或 `state/product/agent_task_queue.json` 仍绑定旧研究问题
When 运行 P0-A 题目绑定审计
Then 审计必须把这些运行态文件标为 critical
And `can_proceed_to_p0b` 必须为 false。

业务规则：第二阶段 runtime 依赖 SupervisorPlan 和 Agent Queue；如果这里错，后面所有 Agent 分工都会偏题。

## 行为 4：当前题目材料里的旧变量和旧文献 stub 必须阻断

Given `Tasks/parent-education-wage` 目录下的变量、文献或设计文件还包含 robot、robot_density、CHARLS、CGSS 或 training wage stub
When 运行 P0-A 题目绑定审计
Then 审计必须报告对应 surface 的污染
And 不能进入 P0-B。

业务规则：当前 demo 材料不能一边叫父母教育工资，一边还残留机器人 DID 或训练工资样例。

## 行为 5：历史资料允许存在，但不能参与当前绑定

Given 历史说明、项目管理记录或已归档 CHARLS proof case 包含旧题目关键词
When 当前运行态和 `Tasks/parent-education-wage` 材料已经干净
Then P0-A 审计不能因为这些历史文件阻断。

业务规则：整理文件夹不是删除历史。历史可以保留，但必须和当前产品运行态分层。

## 行为 6：审计必须产出机器可读和人工可读证据

Given 运行 P0-A 题目绑定审计
When `persist=true`
Then 系统必须写出 `Results/json/product_control_demo_topic_binding_audit.json`
And 写出 `Reviews/product_control_demo_topic_binding_audit.md`
And 两份产物必须能说明 status、critical issue 和下一步。

业务规则：P0-A 的结论必须能被 UI、CLI、Agent Queue 和人工 Review 复用，而不是只停留在聊天里。
