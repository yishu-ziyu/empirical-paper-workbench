# 长时间迭代计划：实证研究工作台 MVP

> 当前计划日期：2026-05-16  
> 当前提交基线：`70c7e6c Make research intake the first product decision`  
> 当前本地验收入口：`http://127.0.0.1:8767/?v=20260516-p2q-topic1`

## 1. 长时间任务配置与执行约束

本项目已经具备长时间迭代所需的“记忆外化”基础，但需要严格执行，不能只写在聊天里。

### 已存在配置

- `/Users/mahaoxuan/Desktop/AGENTS.md`
  - 要求自主推进、不要在安全可逆的下一步反复询问。
  - 要求长任务用 `Tasks/todo.md`、`Tasks/handoff.md`、`Tasks/decision-log.md`、`Tasks/manifest.md`、`Tasks/review.md` 外化状态。
  - 要求每次提交使用 Lore Commit Protocol。
- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/AGENTS.md`
  - 本项目的更高优先级规则：新增功能、API、产品流程和可见交互默认 BDD + TDD。
  - 纯规划、只读检查、状态汇报和文档记录可以不走完整 BDD/TDD。
- `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板/Tasks/`
  - `todo.md`：阶段任务状态。
  - `handoff.md`：跨 Session 接手说明。
  - `decision-log.md`：不要重复探索的决策记录。
  - `manifest.md`：关键产物路径。
  - `review.md`：验证、风险、未覆盖项。
  - `lessons.md`：用户纠偏后的固定规则。
  - `workflow.md`：产品主链路。
  - `current-stage.md`：当前阶段摘要。
- `tmux` 服务
  - 当前 `empirical-workbench-8767` 会话托管本地 FastAPI 页面，避免普通后台进程被清理。

### 每轮固定节奏

每一轮开发都按这个顺序执行：

1. 读取 `AGENTS.md`、`Tasks/current-stage.md`、`Tasks/handoff.md`、`Tasks/workflow.md`、`Tasks/todo.md`。
2. 若任务超过两轮、预计超过一小时或已经重复失败，先读取 `docs/architecture-v2/long-run-optimization-protocol.md`，并在 `Tasks/round-log.md` 新增本轮记录。
3. 把本轮目标写入 `Tasks/todo.md`，只做一个可验收产品增量。
4. 写 3-8 条 BDD 行为，保存到 `docs/architecture-v2/codex-phase-*.md`。
5. 写自动化测试并先跑 RED，确认失败原因是功能缺失。
6. 写最小实现，跑 GREEN。
7. 跑相邻回归、全量回归、静态检查。
8. 用右侧内置浏览器或 Playwright 验收真实页面。
9. 更新 `Tasks/round-log.md`、`Tasks/handoff.md`、`Tasks/manifest.md`、`Tasks/review.md`、`Tasks/decision-log.md`。
10. `git status` 检查影响面，Lore commit，push。
11. 继续下一轮，除非遇到破坏性操作、外部凭证、真实数据覆盖、线上发布或研究判断分叉。

### 平台期与策略跃迁规则

当连续三轮同类尝试没有实质收益、同一错误重复出现、没有新增证据产物，或无法说清瓶颈位于数据/方法/执行/产品状态/文稿表达中的哪一层时，停止当前微调路线。

进入平台期后必须先分析日志、测试、结果文件或任务记录，定位当前瓶颈；然后选择一个结构性不同的下一步，例如从页面修补转向状态模型、从计划文档转向真实后端执行、从单方法验证转向稳健性矩阵。策略跃迁允许短暂打破非核心约束，但必须在 `Tasks/round-log.md` 写明被打破的约束、修复路径、回滚点和证据文件。

## 2. 产品主方向

我们最终不是做一个普通后台，也不是一个文件浏览器，而是一个“个人实证研究智能工作台”。

核心路径：

```text
研究选题
-> 数据与变量
-> 识别设计
-> 执行计划
-> 统计执行
-> 结果解释
-> 论文写作
-> 复现与导出
-> Agent 审计
```

核心原则：

- 用户第一步永远是“我要研究什么”，不是先看系统功能全集。
- 大模型 Supervisor 是中控，但只能提出计划、风险、证据要求和子 Agent 分工，不能直接篡改正式研究状态。
- StatsPAI / StataMCP / Python 是严谨执行后端，必须真实产生日志、结果文件、诊断和 evidence，不能只在 UI 中声明。
- 真实数据进入论文分析前必须经过：导入/绑定预检 -> 字段画像 -> 变量角色候选 -> 人工编辑保存 -> DesignSpec -> RunPlan。
- 所有 finding、draft、export 都必须绑定真实 run 和 evidence，不允许 mock 冒充研究证据。
- 前端继续收敛为 clean workbench：默认摘要、按需展开、右侧属性检查器、底部日志，不堆卡片。

## 3. 当前真实状态

已经完成：

- P2-Q：首页变成选题优先入口。
- P2-P：本地 Codex SupervisorPlan 可作为待审 artifact 生成，默认执行开关关闭。
- P2-N：StatsPAI 已进入 CSV OLS 独立验证路径。
- P2-L/P2-M：真实 DTA 字段画像可以生成变量角色候选，并可显式载入正式编辑器。
- P2-K：执行页能声明 active backend、candidate backend、数据预检和可复现入口。
- P1 系列：Finding review、Manuscript candidate review、export preflight、Review & Export 工作台已有最小闭环。

仍然缺：

- 选题还没有后端持久化为 ResearchQuestion / TopicSession。
- SupervisorPlan 还没有 approve / reject / needs_revision 审批状态机。
- approved SupervisorPlan 还没有驱动任务队列。
- 真实 CFPS 数据还没有完整进入变量角色、DesignSpec、RunPlan 和执行链。
- StatsPAI/StataMCP 还不是通用执行后端；当前主要是 CSV OLS 独立验证。
- DID / IV / RDD / PSM / DML 还没有方法级前置条件检查、执行器、结果解释和稳健性产物。
- Manuscript 还不是成熟协作编辑器；docx 导出仍在预检层。

## 4. 后续 MVP 迭代路线

### P2-R：ResearchQuestion / TopicSession 持久化

目的：把首页输入的选题从前端 localStorage 升级为后端可审计研究对象。

验收标准：

- `POST /api/v1/projects/{project_id}/research-questions` 创建或更新研究选题。
- `GET /api/v1/projects/{project_id}/research-questions/current` 可跨 Session 恢复。
- 首页确认选题后写入后端，不改写变量角色、设计方案或运行计划。
- UI 显示题目状态、来源、证据等级、最后更新时间。

为什么先做：没有持久化选题，后面的 SupervisorPlan、变量候选、DesignSpec 都缺少共同上下文。

### P2-S：SupervisorPlan 审批状态机

目的：让本地 Codex Supervisor 生成的计划进入人工确认，而不是停在 `needs_review`。

验收标准：

- `PUT /supervisor-plan/{plan_id}/review` 支持 `approve`、`reject`、`needs_revision`。
- 审批意见写入 `state/product/supervisor_plan_reviews.json`。
- 只有 approved plan 能进入后续任务队列。
- reject / needs_revision 必须保留审阅意见并阻止派工。

为什么第二步做：P2-R 提供研究对象，P2-S 再让中控计划绑定到这个对象。

### P2-T：Approved Plan -> Agent Task Queue

目的：把 approved SupervisorPlan 拆成可执行任务队列，而不是只显示计划文本。

验收标准：

- 新增 `state/product/agent_task_queue.json`。
- 每个任务包含 owner agent、input evidence、required output、blocked_by、status。
- 前端 Agents 页显示任务队列、阻塞项、下一步动作。
- 队列不能直接改写正式研究状态，只能生成候选 artifact 或执行请求。

为什么第三步做：这是从“有中控计划”到“多 Agent 工作流”的桥。

### P2-U：真实数据到正式研究状态闭环

目的：让真实 CFPS 字段候选真正进入正式 VariableRoleSet、DesignSpec 和 RunPlan 的可审阅链路。

验收标准：

- approved candidate 可在正式变量编辑器中搜索、调整、保存。
- 保存后生成新的 VariableRoleSet version。
- DesignSpec 必须消费指定 VariableRoleSet version。
- RunPlan 必须消费指定 DesignSpec version。
- 所有版本都可回溯到 dataset import/profile/candidate。

为什么第四步做：否则真实数据永远停在候选池，无法进入论文实证分析。

### P2-V：StatsPAI / StataMCP / Python 执行后端升级

目的：把统计执行从 demo OLS 扩展为严谨可复核执行层。

验收标准：

- 每个 backend 必须产生日志、结果 JSON、诊断、artifact manifest。
- StatsPAI 和 StataMCP 只有真实执行才显示 `local_execution`。
- OLS 支持 robust / cluster 标准误的边界声明。
- DID / IV / RDD / PSM / DML 必须先做 readiness check，blocked 方法显示缺什么。

为什么第五步做：前面的研究对象、计划、变量和设计都稳定后，执行层才有可信输入。

### P2-W：Findings / Manuscript / Export 绑定真实执行

目的：让论文写作从“候选段落”升级为“可审阅、可追溯、可导出的写作台”。

验收标准：

- Finding 只能从 approved execution 生成。
- Manuscript section 必须绑定 finding、table、figure、citation 和 evidence。
- docx export preflight 显示缺失引用、未批准 finding、mock/local/local_execution 边界。
- 导出前仍需人工确认，不覆盖源草稿。

为什么第六步做：只有执行证据可靠后，写作和导出才有意义。

### P2-X：Clean Workbench 第二轮视觉收敛

目的：把所有页面从“模块堆叠”收敛为研究生命周期工作台。

验收标准：

- Overview：只展示选题、当前阶段、下一步、风险和最近运行。
- Data：只围绕数据、变量和字段审阅。
- Design：只围绕识别策略和模型设定。
- Execution：只围绕 run、日志、结果和诊断。
- Findings：只围绕论断审阅。
- Manuscript：只围绕章节、引用、证据绑定。
- Artifacts：只围绕复现包和导出。
- Agents：只围绕任务队列、工具调用、成本和人工介入。

为什么持续做：视觉问题的根因是信息架构，不能靠局部美化解决。

## 5. 长时间迭代停止条件

可以自动继续：

- 本地代码改动。
- 测试、静态检查、浏览器验收。
- 更新 Tasks 交接文件。
- 提交和推送已验证的小步改动。

必须停下来说明：

- 需要覆盖或移动真实原始数据。
- 需要启用真实本地 Codex 执行并可能产生费用/外部调用。
- 需要调用 StataMCP、StatsPAI 或云服务但当前凭证/运行时不可用。
- 需要改变研究题目、变量角色、识别策略这类实质研究判断。
- 需要发布线上服务或接入外部生产系统。

## 6. 下一轮立即执行项

下一轮从 P2-R 开始：

1. 写 `ResearchQuestion / TopicSession` BDD。
2. 写失败测试：后端 API、状态文件、首页确认选题写入后端、跨 Session 恢复。
3. 实现最小后端服务和前端调用。
4. 浏览器验收首页确认选题后刷新仍保留。
5. 更新 Tasks 文件。
6. commit + push。
