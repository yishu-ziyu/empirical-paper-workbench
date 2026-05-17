# Decision Log

## 2026-05-17：Agent Task Queue 必须经过人工派工审阅

Decision: P2-V 让每个 Agent Task Queue item 默认 `can_execute=false`，并要求人工执行 `approve`、`needs_revision` 或 `reject` 的派工审阅动作。

Reason: approved SupervisorPlan 只能说明计划可以拆成任务，不能说明每个子 Agent 已被允许访问输入证据、产生产物或进入真实执行后端。

Rejected: 队列创建后直接允许子 Agent 执行。原因是这会让本地 Codex Supervisor 绕过人类审计，把“生成计划”误变成“授权执行”。

Rejected: `approve` 后立即调用 StatsPAI/StataMCP/Python 执行。原因是 P2-V 只解决执行前授权，执行后端选择、日志、结果文件和 evaluator checks 应在后续阶段独立 BDD/TDD。

## 2026-05-17：派工审阅不能改写正式研究状态

Decision: `PUT /agent-task-queue/tasks/{task_id}/dispatch-review` 只写回 `state/product/agent_task_queue.json` 中该任务的 `status`、`dispatch_review`、`dispatch_readiness`、`audit_log`。

Reason: VariableRoleSet、DesignSpec、RunPlan、SupervisorPlan 都是上游产品状态。派工审阅是执行前控制点，不应偷偷改变研究设定。

Rejected: 审阅通过后同步修改 RunPlan 或变量角色。原因是这会混淆“派工授权”和“研究设计变更”，也会破坏跨 Session 可审计性。

## 2026-05-17：默认折叠高噪声任务细节

Decision: 前端 Agent Task Queue 只默认展示状态、负责人、派工审阅和少量阻塞信息；输入证据、输出要求、风险和审计日志放进 `details`。

Reason: 用户明确指出页面信息会冲爆短时记忆。任务队列是控制台，不应一屏摊开所有 JSON 和审计细节。

Rejected: 默认展开所有任务详情。原因是这会重复 P2 前期的信息噪声问题，让用户无法判断下一步该点哪里。

## 2026-05-12：采用记忆外化作为长程开发协议

Decision: 本轮开发维护 `tasks/todo.md`、`tasks/handoff.md`、`tasks/decision-log.md`、`tasks/manifest.md`、`tasks/review.md`，把跨 Session 状态落地到仓库文件。

Reason: 用户明确要求基于“记忆外化与跨 Session 状态继承”方法运行长任务，避免上下文压缩或新窗口恢复时丢失状态。

Rejected: 只依赖聊天上下文继续开发。原因是本任务预期跨数小时，且需要明天继续验收。

## 2026-05-12：P0 先接现有 observability API，不重构整体 UI

Decision: 在现有 `实证执行` 页面增加真实 run selector、run header、step board、event stream、HITL gate、artifact/evidence 面板。

Reason: 后端 observability API 已存在且基线测试通过，最小产品闭环应先让真实执行过程可见。

Rejected: 重新设计 7 个页面或继续做静态美化。原因是用户强调当前重点不是静态好看，而是真实执行可视化。

## 2026-05-12：StatsPAI 作为方法引擎底座，不作为 UI mock 文案

Decision: 将 StatsPAI/CoPaper 阅读结果固化为开发约束：Agent/Skill 编排做“研究流程决策”，StatsPAI 风格方法引擎做“统一统计执行”，所有结果必须保留 evidence_level 和可追溯产物。

Reason: StatsPAI 文章和首页都强调 agent-native、统一 API、统一结果对象、出版级输出和方法级引用。

Rejected: 把 StatsPAI 当作营销文本直接放进页面。原因是产品系统需要吸收其架构方法，而不是增加静态宣传内容。

## 2026-05-12：历史 run 缺少观测文件时不报死错误

Decision: 前端选择到旧 run 且 `/observability` 返回 404 时，保留 run selector 和 run header，显示“缺少可观察执行轨迹”，并提示用户启动新的可观察 run。

Reason: 浏览器验收发现 8765 上旧服务曾创建 run store JSON，但没有 `state/runs/{run_id}` 下的 observability 文件；真实用户环境可能保留类似历史 run。

Rejected: 自动隐藏或删除旧 run。原因是旧 run 仍是本地文件证据，不能由前端静默篡改历史状态。

## 2026-05-12：用 8877 验证当前工作树，暂不干预 8765 旧进程

Decision: 本轮浏览器验收启动 `python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8877`，不 kill 8765 上的既有 Python 服务。

Reason: 8765 端口已被旧进程占用，且用户未要求清理进程；换端口能低风险验证当前代码。

Rejected: 直接结束 8765 进程。原因是它可能是用户正在使用的本地服务，非必要不做破坏性操作。

## 2026-05-12：Gate resolve 采用 project/run 作用域路由

Decision: P1 后端使用 `POST /api/v1/projects/{project_id}/runs/{run_id}/gates/{gate_id}/resolve`，payload 记录 `action` 和 `note`。

Reason: gate 是某个项目某次运行中的人工介入点，project/run 作用域比全局 gate id 更容易审计，也和现有 observability API 保持一致。

Rejected: `/api/v1/hitl/{gate_id}/confirm|reject`。原因是全局 gate id 难以表达 run 上下文，也不利于后续刷新同一个 run 的 observability。

## 2026-05-12：P1-A 前端不伪造 gate 成功状态

Decision: 前端点击 confirm/reject/adjust 后调用真实 resolve API，成功后重新读取当前 run 的 observability，而不是只在 DOM 中本地改状态。

Reason: CoPaper/StatsPAI 方法论都要求工作流状态可追溯；HITL gate 是运行轨迹的一部分，必须以 `gates.json`、`run_events.jsonl`、`run_manifest.json` 的真实写回为准。

Rejected: 前端 optimistic update 直接把 gate 标成 resolved。原因是会制造 UI 状态和本地证据文件不一致的风险。

## 2026-05-12：给本地静态资源加版本 query

Decision: `index.html` 引用 `/assets/styles.css?v=20260512-p1a` 和 `/assets/app.js?v=20260512-p1a`。

Reason: 浏览器验收时服务端已返回新版 JS，但页面仍执行旧缓存，继续显示“P1 接入”禁用按钮。

Rejected: 仅要求人工清缓存。原因是长程迭代需要可重复验收，不能让浏览器缓存成为隐性状态。

## 2026-05-12：P1-B 先做项目内本地数据选择，不做伪上传

Decision: `GET /datasets` 从项目 `Data/` 目录扫描真实文件并标记 `evidence_level=local_file`；`POST /runs` 接收项目相对 `dataset_path` 并把 `dataset_source` 写入 run response 和 manifest。

Reason: CoPaper/StatsPAI 范式的第一步是用户交付真实数据，系统基于真实数据推进研究流程。当前应先保证 run 的数据来源可追溯，而不是做一个没有后端文件落地的上传 UI。

Rejected: 前端只显示 mock dataset 或只在按钮文案里说“上传”。原因是会让用户误以为系统已经读取真实数据，违反 evidence_level 规则。

Rejected: 接收任意绝对路径。原因是会扩大本地文件访问边界，且不利于项目级审计。

## 2026-05-12：CSV shape 采用轻量本地检查

Decision: P1-B 只对 CSV 做行列数轻量检查，其他文件类型先返回文件证据和大小，不引入额外解析依赖。

Reason: 当前项目样例数据是 `Data/Final/analysis_sample.csv`，最小闭环需要先证明数据入口和 run source，不应为了 xlsx/dta 预览引入大范围依赖和复杂错误面。

Rejected: 立即支持所有统计文件的完整 schema preview。原因是实现面较大，应在 P1-C/P1-D 按 BDD 单独推进。

## 2026-05-12：run 数据源成为 observability 一等字段

Decision: `GET /observability` 顶层返回 `dataset_source`，同时保留 `manifest.dataset_source`，前端执行页直接渲染 Run 数据源面板。

Reason: 用户查看一次执行时，首先要确认这次 run 使用了哪个真实数据文件。让前端从 manifest 内部猜字段会把关键证据藏得太深。

Rejected: 只在数据页展示 dataset source。原因是数据页说明“可用数据”，执行页需要说明“本次执行实际使用的数据”。

## 2026-05-12：P1-C 只做文件级 shape，不提前做变量编辑器

Decision: CSV 数据源写入 `row_count`、`column_count`、`role`，执行页展示这些最小数据理解证据。

Reason: 当前最小闭环需要证明系统读取了数据结构；变量级 schema/角色确认会影响 HITL gate 和后续模型配置，应该单独进入 P1-D。

Rejected: 在 P1-C 一次性加入变量编辑器。原因是范围会跨 UI、API、状态写回和建模配置，容易削弱 BDD/TDD 的可控性。

## 2026-05-12：变量角色先提升为可见证据，再做结构化编辑

Decision: P1-D 从 `dataset_intake` step metadata 提取 `key_variables`，在 observability 顶层返回 `variable_roles`，并在执行页展示 outcome、treatment、controls、instruments 与 `gate_dataset_fields` 状态。

Reason: CoPaper/StatsPAI 式流程要求用户先看见系统如何理解数据，再决定是否确认或调整。当前 run 已有变量角色 metadata，把它提升为一等对象是最小可追溯产品闭环。

Rejected: 直接实现变量编辑器并写回配置。原因是这会引入新的状态写回、审计日志和建模配置边界，应作为 P1-E 单独 BDD/TDD。

Rejected: 从当前 `paper.yaml` 重新推断历史 run 的变量角色。原因是会覆盖历史执行证据；P1-D 只使用本次 run 的 step/gate metadata。

## 2026-05-12：实证执行页改为紧凑执行控制台

Decision: P1-UI 对 `#view-empirical-execution` 使用 scoped system font、8px 小圆角、12px 面板内边距、两列执行上下文网格，并把 run 摘要、数据源、变量角色压缩为同一屏可扫读的信息区。

Reason: 浏览器截图显示原页面像论文卡片堆叠：serif 字体过重、卡片过大、信息密度低、Step/Event 被挤到首屏下方，不适合 CoPaper/StatsPAI 式执行工作台。

Rejected: 继续局部调大/调小单个卡片。原因是问题来自整体信息架构和密度，不是单个 CSS 数值。

Rejected: 重写整站视觉系统。原因是当前用户指出的问题集中在实证执行页，P1 应先收紧真实执行控制台，不扩大影响面。

## 2026-05-12：暂停继续堆功能，先重置产品主流程

Decision: 暂停直接进入 P1-E 实现，先写 `product-flow-reset-2026-05-12.md` 和下一步 workflow contract BDD，把产品重新收敛到 Dataset -> VariableRoleSet -> DesignSpec -> RunPlan -> Run -> Results -> Draft -> Export 的主链路。

Reason: 当前实现已经能观察 run，但产品感受仍然混乱，说明问题不是单个 UI 面板，而是产品对象顺序被倒置：Run/Step/Gate/Artifact 先暴露，VariableRoleSet、DesignSpec、RunPlan 没有成为用户主路径。

Rejected: 继续实现结构化变量角色 adjust API。原因是如果没有产品级 workflow contract，P1-E 会继续把功能加到执行页里，让混乱扩大。

Rejected: 只做视觉重排。原因是视觉问题来自流程和信息架构，而不是 CSS 本身。

## 2026-05-12：用 workflow_contract 作为产品状态源

Decision: `GET /api/v1/projects/{project_id}/overview` 返回 `workflow_contract`，前端首页、Data & Design、Execution 都从该契约读取下一步行动、canonical stages 和 run readiness。

Reason: 之前页面把 run selector、Step Board、Event Stream 暴露成主对象，导致用户看不到 CoPaper/StatsPAI 式的研究决策路径。workflow_contract 把 Dataset、VariableRoleSet、DesignSpec、RunPlan 提升为产品主链路。

Rejected: 继续让前端各页自己推断下一步。原因是会出现首页、数据页、执行页各自维护状态解释，越迭代越乱。

Rejected: 只把 `workflow_contract` 写成前端静态常量。原因是 next action 和 blockers 必须逐步由本地项目文件证据驱动，不能伪装真实状态。

## 2026-05-12：一阶导航改成 5 个工作区

Decision: 主导航改为 `Workspace Home / Data & Design / Execution / Results & Draft / Review & Export`，研究设计细节和 Agent 控制台降为工具入口，旧版页面保留在 secondary nav。

Reason: 用户指出当前面板和项目体验混乱；根因之一是一阶导航混合了产品阶段、技术面板和历史页。5 个工作区更接近 CoPaper/StatsPAI 的“从数据到论文”的操作路径。

Rejected: 保留七八个一阶技术页面。原因是它会继续让用户在 Run、Agent、Artifact 等内部对象之间跳转，而不是完成实证论文流程。

## 2026-05-12：数据卡片不再直接启动 run

Decision: Data & Design 页的数据卡片主行动改为“检查并确认变量角色”，原本从数据卡片直接启动试运行的路径降级为 Execution 的开发捷径。

Reason: 有数据之后的下一个真实研究决策是确认 VariableRoleSet，而不是立刻执行 dry-run。完整 run 需要变量角色、研究设计和 Run Plan 均确认。

Rejected: 保持“用此数据启动试运行”作为数据页主 CTA。原因是它把验证 observability 的开发动作误导成产品主流程。

## 2026-05-13：VariableRoleSet 作为项目级产品状态持久化

Decision: 新增 `GET/PUT /api/v1/projects/{project_id}/variable-roles`，把用户确认后的变量角色保存为 `state/product/variable_roles.json`，并让 `workflow_contract` 读取该状态推进到 `confirm_design_spec`。

Reason: CoPaper/StatsPAI 式实证流程要求先确认数据与变量，再确认识别设计。变量角色不能只存在于某次 run 的 HITL gate note 中，否则跨 Session 恢复和后续 DesignSpec 都没有稳定输入。

Rejected: 只把变量角色调整写入 `gates.json` 或 `run_events.jsonl`。原因是 run log 是执行证据，不是产品主流程的唯一状态源；`workflow_contract` 必须能在没有打开特定 run 的情况下恢复当前研究阶段。

Rejected: 继续从当前 run 的 `dataset_intake` metadata 推断已确认状态。原因是那只能说明 Agent 曾经提出候选变量，不能代表用户已经确认。

## 2026-05-13：DesignSpec 和 RunPlan 成为 full run 前置状态机

Decision: 新增 `GET/PUT /api/v1/projects/{project_id}/design-spec` 与 `GET/PUT /api/v1/projects/{project_id}/run-plan`，把确认后的研究问题、识别策略、模型设定和执行计划分别保存到 `state/product/design_spec.json`、`state/product/run_plan.json`，并让 `workflow_contract` 依次推进到 `confirm_run_plan` 和 `start_full_run`。

Reason: 用户要求产品完全按 CoPaper/StatsPAI 式实证流程构建。完整执行不能只因为数据和变量角色存在就启动，必须先确认研究设计和可审计执行计划，才能把 run 作为有研究语义的执行，而不是开发试运行。

Rejected: VariableRoleSet approved 后直接允许 full run。原因是缺少识别策略、模型公式、固定效应、聚类方式和任务产出清单，会让执行结果无法解释。

Rejected: 继续把 DesignSpec 留在旧 `/design` mock 数据里。原因是 mock 设计页不能驱动 workflow contract，也不能跨 Session 恢复用户已确认研究设计。

Rejected: 把 RunPlan 只作为前端临时表单状态。原因是后续 Findings、Manuscript、Artifacts、Agents 都需要知道本次 full run 是按哪个 approved plan 执行的。

## 2026-05-13：full run 采用调用式研究引擎集成，不嵌入 Feynman 源码

Decision: 新增 `POST /api/v1/projects/{project_id}/runs/full`，从 approved RunPlan 启动完整执行，并在 run response 与 manifest 中写入 `plan_binding`、`research_engine`、`execution_evidence_level`。`research_engine` 记录为 `Feynman-compatible research engine`，`integration_mode=callable_external`，`embedded=false`。

Reason: 用户提供的参考判断是短期走 Feynman 调用式集成，源码层面借鉴 provider、skill、workflow、provenance 设计，不直接 fork/嵌入整个 Feynman。本项目当前已有本地 `Program/run_paper.py` + StatsPAI pipeline，最小正确路径是先让 full run 从 RunPlan 可审计启动，再把外部研究引擎能力做成可替换 provider。

Rejected: 把 Feynman 源码复制进项目。原因是它依赖 Pi runtime 和 `@mariozechner/*` 包，直接嵌入会扩大维护面。

Rejected: 继续把 dry-run 按钮当作 full run 主行动。原因是 dry-run 是 observability 开发捷径，不能代表基于 approved RunPlan 的完整实证执行。

Rejected: 让 full run 只返回 run_id，不写 provenance。原因是后续 Findings、Manuscript、Artifacts、Agents 都必须知道结果来自哪版 VariableRoleSet、DesignSpec 和 RunPlan。

## 2026-05-13：Results & Draft 先做证据绑定，不先做完整编辑器

Decision: 新增 `GET /api/v1/projects/{project_id}/results-draft` 和 Results & Draft 页面 evidence binding。API 只读取最新 successful full-run，生成最小 FindingCard，并把 `Manuscripts/generated/paper_draft.md` 的章节绑定到 `Results/json/analysis_result.json` 和 run provenance。

Reason: P1-H 已经证明完整执行可以从 approved RunPlan 启动；下一步需要让用户看到“哪些结果可以审阅”和“草稿内容来自哪次执行”。这比先做 Markdown 编辑器、评论系统或完整 Artifacts 页更能推进 CoPaper/StatsPAI 式主流程。

Rejected: 直接做完整 Manuscript 编辑器。原因是目前还缺 claim review 层，先允许自由编辑会弱化“论断必须绑定证据”的产品原则。

Rejected: 从草稿 Markdown 解析 finding。原因是草稿是文本产物，真正的系数、标准误、p 值和样本量应来自 `Results/json/analysis_result.json`。

Rejected: 在 Results & Draft 页面展示 mock finding。原因是结果页必须依赖 successful full-run；没有 full-run 时返回 409 `full_run_required`，避免伪装真实研究结论。

## 2026-05-13：FindingCard 必须经过 claim review 才能进入正文

Decision: 新增 FindingCard review 状态层和 `PUT /api/v1/projects/{project_id}/results-draft/findings/{finding_id}/review`，把 `approve/reject/needs_revision` 持久化到 `state/product/finding_reviews.json`。Results & Draft 读取 review 后显示 `review_status` 和 `can_write_to_draft`。

Reason: CoPaper/StatsPAI/Feynman-style 研究流程都强调自动执行结果不能直接变成论文论断。P1-I 已证明结果和草稿能绑定真实证据；P1-J 需要把“是否可写入正文”变成用户审阅决定，避免 Agent 或统计输出绕过人工判断。

Rejected: approve 后直接改写 `Manuscripts/generated/paper_draft.md`。原因是本阶段目标是 claim review，不是 Manuscript 编辑器；直接改写正文会混淆草稿源文件证据和用户审阅证据。

Rejected: 只在前端内存里保存审阅状态。原因是跨 Session 恢复必须读取项目文件，且 Review/Export 阶段需要稳定状态源。

Rejected: 对新 run 复用旧 review。原因是相同 finding id 在不同 run 中可能对应不同系数、样本或模型，当前实现要求 `run_id` 和 `artifact_path` 匹配才应用 review。

## 2026-05-16：ResearchQuestion 作为独立入口状态，不自动改写研究配置

Decision: 新增 `GET/PUT /api/v1/projects/{project_id}/research-question/current`，把首页确认的选题保存为 `state/product/research_question.json`，并让 overview 暴露 `research_question_state`。

Reason: P2-Q 已把首页改成“先确定研究选题”，但只存在前端 localStorage 会导致跨 Session 丢失，也无法让 SupervisorPlan、变量候选和执行计划绑定同一个研究上下文。

Rejected: 继续只用 localStorage 保存选题。原因是它不可审计、不可跨窗口继承，也不能成为后续 agent 计划的稳定输入。

Rejected: 保存 ResearchQuestion 后自动重建 VariableRoleSet、DesignSpec 或 RunPlan。原因是这会把“用户输入研究主题”误当成“用户批准研究设定”，风险是模型或工程逻辑偷偷改写研究配置。

Directive: 后续 SupervisorPlan 可以引用 ResearchQuestion，但不得因为 ResearchQuestion 变更而自动覆盖已确认的变量角色、研究设计或运行计划。

## 2026-05-13：Manuscript 只消费 approved FindingCard，并生成候选而非覆盖正文

Decision: 新增 `GET /api/v1/projects/{project_id}/manuscript-candidates`，只从 `review_status=approved` 且 `can_write_to_draft=true` 的 FindingCard 派生 `manuscript_section_candidate`，并在 Results & Draft 页面显示候选段落与 provenance。

Reason: P1-J 只证明某个统计论断可以进入写作，但它还不是最终正文。Manuscript 阶段需要一个中间候选层，让用户先看见由结果证据生成的段落，再决定是否确认、修改、写回或导出。

## 2026-05-14：真实数据字段画像不能自动进入研究状态

Decision: P2-I 新增 `dataset_import_profile`，但画像结果默认 `can_feed_variable_roles=false`；它只提供字段/质量预览，不自动改写 VariableRoleSet、DesignSpec 或 RunPlan。

Reason: 真实数据接入后仍需要人工确认变量含义、处理变量、结果变量和模型设定。字段画像只能证明“系统读到了什么”，不能代表“研究者确认了什么”。

Rejected: 画像成功后自动替换当前 VariableRoleSet。原因是这会把文件结构读取误当成研究语义确认，尤其是外部 CFPS/CHARLS 数据变量名需要人工解释。

## 2026-05-14：不为 DTA/XLSX/Parquet 伪造变量字典

Decision: P2-I 对 CSV 读取字段画像；对 DTA/XLSX/Parquet 等暂未接入安全读取器的格式返回 `blocked/not_profiled`、空 `fields` 和明确 `blocking_reason`。

Reason: 当前真实候选池大量是大体积 `.dta` 文件。没有安全读取器、行数上限和错误处理时，伪造字段列表会误导用户，也可能造成内存/性能风险。

Rejected: 用文件名或历史样例猜测变量字段。原因是这会破坏 evidence discipline，尤其不能把 mock 或推断内容展示成 `local_file` 证据。

## 2026-05-14：绑定引用画像必须重新校验哈希

Decision: `profile_external_dataset_import()` 在读取已绑定外部引用前重新计算 SHA256；如果源文件与 apply 时记录的哈希不一致，返回 409 `dataset_import_source_changed`。

Reason: 本地绑定引用不复制大文件，依赖原始路径稳定。画像阶段必须证明现在读取的文件仍是当时用户确认绑定的文件。

Rejected: 只检查路径存在。原因是同一路径可能被替换或覆盖，路径存在不能证明 provenance 仍然成立。

## 2026-05-13：先用本地 OLS adapter 把方法目录升级为执行证据

Decision: P2-C 新增最小 `python_ols_adapter`，在 approved OLS RunPlan 的 full run 成功后读取本地 CSV 和公式，计算 OLS 系数，写入 `Results/json/method_execution_result.json`，并在 run response 与 `run_manifest.json` 中暴露 `method_execution.evidence_level=local_execution`。

Reason: P2-B 的 `method_catalog` 只能说明方法前置条件是否具备，不能代表真实执行。CoPaper/StatsPAI 式产品必须让至少一个 ready 方法从数据产生可追溯本地执行产物，才算从“方法准入”进入“实证执行”。

Rejected: 把 `method_catalog` 直接标记为 `local_execution`。原因是它只是本地文件级前置条件判断，没有运行统计方法。

Rejected: 立即接入完整 StatsPAI/Stata/DID/IV/RDD/PSM/DML。原因是依赖、统计边界和失败模式更大，应先用 OLS baseline 建立可测试执行证据链，再逐步扩展。

Rejected: OLS 不可估时让 API 暴露 500。原因是真实产品应返回结构化 `method_execution_failed`，让用户知道是数据不足、公式不可估或共线设计，而不是后端崩溃。

## 2026-05-13：清洁工作台优先于继续增加视觉元素

Decision: 将 archive shell 的纸格背景、厚重阴影和大卡片嵌套降级为干净的工作台表面、右侧属性检查器和 record/list 结构；变量角色确认入口改为单列记录，不再使用易重叠的 auto 双列布局。

Reason: 用户截图显示变量角色入口文本和操作卡片发生重叠，说明此前“温暖纸张/档案感”过度装饰，已经干扰核心信息。参考 JupyterLab 的主工作区/侧边栏/属性检查器、Grafana 的信息 panel 思路和 OpenMetadata 的数据资产/质量证据视角后，本项目应优先变成可扫读研究工作台，而不是继续叠纸张纹理和大卡片。

Rejected: 继续沿用纸格背景和手账式大卡片。原因是它强化了视觉气质，但降低了大型研究系统的可读性和密度。

Rejected: 引入新的前端框架或重新做 landing page。原因是当前问题可在现有 vanilla 静态前端内修复，且项目原则要求小范围、可验证修改。

## 2026-05-13：清洁工作台优先于继续增加视觉元素

Decision: 将 archive shell 的纸格背景、厚重阴影和大卡片嵌套降级为干净的工作台表面、右侧属性检查器和 record/list 结构；变量角色确认入口改为单列记录，不再使用易重叠的 auto 双列布局。

Reason: 用户截图显示变量角色入口文本和操作卡片发生重叠，说明此前“温暖纸张/档案感”过度装饰，已经干扰核心信息。参考 JupyterLab 的主工作区/侧边栏/属性检查器、Grafana 的信息 panel 思路和 OpenMetadata 的数据资产/质量证据视角后，本项目应优先变成可扫读研究工作台，而不是继续叠纸张纹理和大卡片。

Rejected: 继续沿用纸格背景和手账式大卡片。原因是它强化了视觉气质，但降低了大型研究系统的可读性和密度。

Rejected: 引入新的前端框架或重新做 landing page。原因是当前问题可在现有 vanilla 静态前端内修复，且项目原则要求小范围、可验证修改。

Rejected: approve FindingCard 后直接覆盖 `Manuscripts/generated/paper_draft.md`。原因是这样会把 claim review 和正文编辑混在一起，且容易破坏源草稿的 `local_file` 证据边界。

Rejected: 从 rejected 或 needs_revision FindingCard 生成正文候选。原因是这会绕过人工审阅语义，把明确不允许写入的结果重新暴露为可写内容。

Rejected: 本阶段调用 LLM 改写正文。原因是当前需要先锁定 evidence binding 与状态机，LLM 改写应在 candidate review/promote 之后作为可审计能力接入。

## 2026-05-13：正文候选必须有独立 candidate review 状态

Decision: 新增 `PUT /api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/review`，把 candidate 的 `approve/reject/needs_revision` 决定保存到 `state/product/manuscript_candidate_reviews.json`，并让 candidates API 返回 `review_status`、`can_promote` 和 `candidate_review` provenance。

Reason: P1-J 的 FindingCard review 只说明“这个统计论断可以写”，P1-K 的 Manuscript candidate 只是“系统生成了一段候选文字”。文字是否准确、是否表达过度、是否缺少稳健性上下文，必须单独审阅。

Rejected: 复用 FindingCard 的 `can_write_to_draft` 直接允许写回。原因是统计结果可用不代表段落表述可用，二者审阅对象不同。

Rejected: candidate review 只存在前端内存。原因是跨 Session 恢复和后续 promote/export 都需要本地文件证据。

Rejected: approve candidate 后立刻改写 `paper_draft.md`。原因是写回属于更高风险操作，应先进入 promote/write-back/export preflight。

## 2026-05-13：Promote 是导出前检查，不是正文写回

Decision: 新增 `POST /api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/promote`，只允许 `review_status=approved` 且 `can_promote=true` 的 candidate 写入 `state/product/manuscript_candidate_promotions.json`，返回 `promotion_status=ready_for_export`、`can_export=true`、`can_write_back=false`。

Reason: P1-L 只说明候选段落通过人工审阅；P1-M 需要把“进入最终产物链路”变成可审计状态，同时继续阻止系统直接覆盖 `Manuscripts/generated/paper_draft.md`。这给下一步 write-back/export package 留出明确、安全的边界。

Rejected: approved candidate 后直接覆盖 `paper_draft.md`。原因是源草稿是 `local_file` 证据，直接覆盖会混淆原始草稿、候选段落和人工 promotion 决策。

Rejected: 允许 needs_revision/rejected candidate promote。原因是这会绕过 candidate review 的人工判断。

Rejected: 只在前端显示“已确认”而不写 promotion 文件。原因是跨 Session 恢复、Review/Export 页面和后续导出包都需要稳定的本地证据。

## 2026-05-13：Export preflight 只生成预览和 manifest，不写回源草稿

Decision: 新增 `POST /api/v1/projects/{project_id}/manuscript-candidates/{candidate_id}/export-preflight`，只允许 `promotion_status=ready_for_export` 且 `can_export=true` 的 candidate 生成 `Manuscripts/generated/previews/{candidate_id}.md` 和 `state/product/export_package_manifest.json`，返回 `export_status=preview_ready`、`can_write_back=false`。

Reason: P1-M 已把 candidate 推进到导出前状态，但真正进入最终产物前，用户需要先看到可审查的写回预览和导出包清单。这个阶段必须保留源草稿、候选段落、promotion 决策和 export preflight 证据之间的边界。

Rejected: `export-preflight` 直接覆盖 `Manuscripts/generated/paper_draft.md`。原因是源草稿是已有本地文件证据，自动覆盖会把预览动作和不可逆写回动作混在一起。

Rejected: 直接生成最终 docx。原因是当前还没有 Review & Export 页面的最终包浏览、显式写回审批和导出验证层，直接 docx 会绕过用户对 preview 的确认。

Rejected: 允许未 promote 的 candidate 生成 export package。原因是这会绕过 candidate review 和 promotion preflight 的两层人工状态。

## 2026-05-13：Review & Export 采用 Frontier-Eng evaluator workbench

Decision: 新增 `GET /api/v1/projects/{project_id}/export-package`，并在 Review & Export 页面渲染 `export-package-workbench`。页面显示 `preview_ready` package、5 个 evaluator checks、`evaluator_status=passed`、关键文件路径、`can_write_back=false`，以及 Frontier-Eng 式 `objective -> baseline -> evaluator -> feedback -> next_iteration` 迭代日志。

Reason: 用户补充 Frontier-Eng 方法论后，最终导出不应该只是一个“下载按钮”，而应该是个人科研工程闭环中的 evaluator checkpoint：先有 baseline/export preview，再用检查规则确认结果，再记录反馈和下一轮动作，最后由用户决定是否进入写回或 docx 导出。

Rejected: 在 Review & Export 直接生成 docx 或覆盖 `Manuscripts/generated/paper_draft.md`。原因是这会绕过 evaluator 和显式人工审批，把可逆预检动作变成高风险写回动作。

Rejected: 只在 Results & Draft 页面继续展示 export preflight。原因是 Results & Draft 是候选来源和证据绑定页，Review & Export 才应该承担最终包验收、复现清单、导出前检查和下一轮迭代日志。

Rejected: 只显示 manifest 路径，不显示 evaluator checks。原因是用户需要可视化确定感；导出包必须告诉用户“哪些检查通过”，而不是只暴露内部文件。

## 2026-05-13：界面先转向个人研究档案，而不是继续堆普通控制台卡片

Decision: 在不引入新框架、不改后端数据结构的前提下，把前端外壳升级为 `archive-shell`：左侧仍是研究生命周期导航，中间保留现有工作区，右侧新增 `archive-inspector`，展示当前页面的研究语义、相邻笔记、证据图例和收藏架。视觉层采用温暖纸张、细网格、档案条目和紧凑交互状态，而不是 SaaS hero、渐变球或营销卡片。

Reason: 用户指出当前页面“越设计越乱”，根因是研究对象、工程对象和执行日志堆在同一层。参考 Maggie Appleton、Andy Matuschak、read.cv 和豆瓣收藏架后，本项目更适合呈现为“可浏览的个人研究档案”：每个页面都应告诉用户当前研究对象、相邻材料、证据等级和下一步动作。

Rejected: 重新做普通 landing page 或大 hero。原因是这会把产品变成宣传页，不能帮助用户验证 Dataset -> RunPlan -> Results -> Draft -> Export 的真实研究链路。

Rejected: 复制 Maggie Appleton 的原始插画、品牌元素或完整页面结构。原因是参考的是知识花园/旁注/解释型布局气质，不是复刻具体作品。

Rejected: 为了视觉升级改用 React/Vite/Next。原因是当前产品是 FastAPI + 静态 HTML/CSS/vanilla JS，P1 需要小范围、可验证修改，不能扩大维护面。

Rejected: 本轮实现真正双向链接数据库。原因是右侧 `相邻笔记` 先承担产品导航和信息架构修正；真实 backlinks / graph 应在后续 Artifacts/Agents 或知识库层单独设计。

## 2026-05-13：数据质量画像是进入方法技能集前的准入对象

Decision: 在 `GET /api/v1/projects/{project_id}/datasets` 中新增 `quality_profile`，让 CSV 数据集返回样本量、字段数、缺失率、字段类型、检查项和 `readiness_status`；前端“数据与设计”页新增 `数据质量画像` 面板，并把它放在变量角色确认之前。

Reason: CoPaper/StatsPAI 式路径不是直接选择 DID/IV/RDD 等方法，而是先完成数据引入、字段理解、样本/缺失检查，再进入变量角色和方法选择。没有数据质量画像，RunPlan 的方法选择会变成对不透明数据的猜测。

Rejected: 直接进入 StatsPAI 方法执行。原因是当前还缺少数据质量准入、方法前置变量要求和可执行状态，直接执行会把方法引擎接成黑盒。

Rejected: 只在前端显示静态数据质量说明。原因是质量画像必须来自本地文件读取，并标记 `evidence_level=local_file`；否则会伪装成真实 EDA。

Rejected: 把 `dataset_quality_profile` / `confirm_variable_roles` 作为可见 UI 标签。原因是用户界面必须展示中文研究语义，内部契约名只留在 API 和代码路径中。

## 2026-05-13：写回审批和 docx 预检必须分开

Decision: 新增 `writeback_approval` 与 `docx_preflight` 两个独立状态。写回审批写入 `state/product/writeback_approvals.json`，只表示用户允许候选段落进入下一步；docx 预检写入 `state/product/docx_export_preflight.json`，只表示源草稿、写回预览、导出命令和目标 docx 路径都可追溯。

Reason: P1-O 已经有导出包和 evaluator checks，但用户仍需要明确的产品确定感：哪个动作只是审批，哪个动作只是预检，哪个动作才会真正改文件或生成 docx。拆开状态后，Review & Export 可以变成可审计的证据验收台。

Rejected: 点击 approve 后直接覆盖 `Manuscripts/generated/paper_draft.md`。原因是审批不等于写文件，自动覆盖会破坏源草稿与候选预览的证据边界。

Rejected: docx preflight 直接生成 `Submissions/paper_draft.docx`。原因是预检阶段只证明条件具备，不应该把“检查”伪装成“导出执行”。

Rejected: 在旧的拥挤卡片布局里继续塞按钮。原因是 Review & Export 需要先回答“证据在哪里、状态是什么、下一步动作是什么”，所以本轮改为 evidence table + decision panels。

## 2026-05-13：界面先转向个人研究档案，而不是继续堆普通控制台卡片

Decision: 在不引入新框架、不改后端数据结构的前提下，把前端外壳升级为 `archive-shell`：左侧仍是研究生命周期导航，中间保留现有工作区，右侧新增 `archive-inspector`，展示当前页面的研究语义、相邻笔记、证据图例和收藏架。视觉层采用温暖纸张、细网格、档案条目和紧凑交互状态，而不是 SaaS hero、渐变球或营销卡片。

Reason: 用户指出当前页面“越设计越乱”，根因是研究对象、工程对象和执行日志堆在同一层。参考 Maggie Appleton、Andy Matuschak、read.cv 和豆瓣收藏架后，本项目更适合呈现为“可浏览的个人研究档案”：每个页面都应告诉用户当前研究对象、相邻材料、证据等级和下一步动作。

Rejected: 重新做普通 landing page 或大 hero。原因是这会把产品变成宣传页，不能帮助用户验证 Dataset -> RunPlan -> Results -> Draft -> Export 的真实研究链路。

Rejected: 复制 Maggie Appleton 的原始插画、品牌元素或完整页面结构。原因是参考的是知识花园/旁注/解释型布局气质，不是复刻具体作品。

Rejected: 为了视觉升级改用 React/Vite/Next。原因是当前产品是 FastAPI + 静态 HTML/CSS/vanilla JS，P1 需要小范围、可验证修改，不能扩大维护面。

Rejected: 本轮实现真正双向链接数据库。原因是右侧 `相邻笔记` 先承担产品导航和信息架构修正；真实 backlinks / graph 应在后续 Artifacts/Agents 或知识库层单独设计。
## 2026-05-13：方法技能集先做前置条件目录，不伪装真实执行

Decision: 在 RunPlan 中新增 `method_catalog`，以 `local_file` 证据展示 OLS、DID、IV、RDD、PSM、DML 的方法说明、前置变量、ready/blocked 状态和阻塞原因。默认执行任务只包含当前具备条件的 OLS baseline，并显式写入 `method_id=ols`。

Reason: CoPaper/StatsPAI 式系统的核心不是让用户直接点一个黑盒方法，而是先把数据、变量、识别方法和前置条件变成可审查对象。当前项目尚未调用真实 StatsPAI/Stata 执行器，因此只能声明“方法准入判断”，不能宣称 DID/IV/RDD 已经运行。

Rejected: 直接把 DID/IV/RDD/PSM/DML 全部加入 RunPlan tasks。原因是当前样例数据缺少面板时间、工具变量和断点运行变量，加入执行任务会伪装可执行性。

Rejected: 把 `method_catalog` 标记为 `local_execution`。原因是本阶段没有真实执行外部方法引擎，只读取本地 DesignSpec/VariableRoleSet 做前置条件判断。

Rejected: 把方法目录放到 Execution 页面继续堆卡片。原因是 Execution 页面已经承载 RunPlan、运行轨迹和人工确认；方法准入更适合研究设计细节页。

## 2026-05-13：方法执行证据必须进入执行页和论断卡

Decision: 把 `method_execution_result.json` 作为独立方法证据接入 observability 和 FindingCard，而不是覆盖现有 `analysis_result.json`。

Reason: `analysis_result.json` 适合服务论文摘要和草稿绑定，`method_execution_result.json` 负责证明“哪个方法、公式、数据和 adapter 真正执行过”。两者分层后，用户能区分“结果摘要”和“方法执行证据”。

Rejected: 只在 artifacts 列表里显示 `method_execution_result.json`。原因是用户需要在执行页和结果论断卡直接看到公式、样本量和处理变量系数，而不是去文件浏览器里推断。

Rejected: 直接把 OLS 系数标为可写入正文。原因是还缺标准误、p 值、稳健标准误和 evaluator verdict。

Evidence: `observability.method_execution` 与 `findings[].method_evidence` 均返回 `engine=python_ols_adapter`、`formula=wage ~ trained + edu + experience`、`nobs=12`、`treatment_coefficient=1.8505076803`。

## 2026-05-13：OLS 论断必须携带 evaluator 证据

Decision: 扩展本地 `python_ols_adapter`，让 `method_execution_result.json` 不再只保存系数，而是同时保存标准误、t 统计量、p 值、95% 置信区间、残差诊断和命名 evaluator checks；FindingCard 的 `method_evidence` 直接绑定这些字段，并在页面以中文审阅摘要显示。

Reason: CoPaper/StatsPAI 式产品不能把“跑出一个系数”当作可写入论文的结果。用户需要在结果论断卡上直接看到这个估计是否具备最基本的统计推断证据，以及 evaluator 是否通过。

Rejected: 继续把 `analysis_result.json` 里的 coefficient/std_error/p_value 当作唯一结果来源。原因是它是摘要结果，不足以证明具体方法、公式、adapter 和诊断检查。

Rejected: 在 UI 中用窄网格展示所有方法证据字段。原因是 Results & Draft 卡片宽度有限，网格会重新制造拥挤和换行；审阅摘要更适合当前 clean workbench。

Rejected: 把极小 p 值四舍五入成 `0`。原因是这会降低研究审阅可信度；当前改为保留显著数字，并由前端显示科学计数法。

Evidence: 最新真实 full run `run_a3674e9e78c6` 返回 `standard_errors.trained=0.0754664205`、`p_values.trained=8.83354660202e-133`、`confidence_intervals.trained=[1.7025934962, 1.9984218644]`、`evaluator.status=passed`，四项 checks 全部 passed。

## 2026-05-13：真实数据仓库先作为只读候选池接入

Decision: 在 `GET /api/v1/projects/{project_id}/datasets` 中新增 `external_catalog`，默认扫描 `/Users/mahaoxuan/Desktop/实证数据库`，把外部真实数据以只读候选池展示在“数据与设计”页；项目内数据仍只来自当前 repo 的 `Data/` 目录和 `paper.yaml` 配置。

Reason: 用户提供的真实数据目录非常适合作为测试与后续选题来源，但它不是当前论文项目已经确认使用的数据。先做只读 inventory/profile，可以让用户看见真实资产，又不破坏 provenance 边界。

Rejected: 直接把外部候选文件加入 `items` 当作项目数据。原因是这会让 UI 暗示变量角色、RunPlan 和 OLS 结果已经基于这些真实文件，实际上当前执行仍使用 `Data/Final/analysis_sample.csv`。

Rejected: 页面加载时深度读取全部 DTA/XLSX/Parquet 文件。原因是真实数据仓库有 223 个文件，包含数百 MB Stata 文件；深度读取会拖慢页面并增加编码/隐私风险。P2-F 只做轻量 catalog preview。

Rejected: 把外部候选池做成可编辑上传区。原因是当前阶段没有导入/绑定 manifest，也没有用户确认动作；候选池必须 `read_only=true`。

Evidence: live API 扫描到 `total_count=223`，Safari `数据与设计` 页显示 `/Users/mahaoxuan/Desktop/实证数据库`、CFPS DTA 候选文件、`本地文件`、`尚未画像` 和 `只读`。

## 2026-05-14：真实数据绑定必须先经过只读预检

Decision: 新增真实候选数据导入/绑定预检，预检写入 `state/product/dataset_import_preflights.json`，只记录来源、目标建议、策略、文件大小、证据等级和检查结果；预检阶段不复制、不移动、不绑定外部文件，也不更新 VariableRoleSet、DesignSpec 或 RunPlan。

Reason: 用户提供的 `/Users/mahaoxuan/Desktop/实证数据库` 是真实研究资产。产品需要给用户“我选的是这个文件、准备进入这个项目路径、检查都通过”的确定感，但不能把检查动作伪装成真实导入或执行。

Rejected: 点击候选文件后直接复制到 `Data/Raw/`。原因是复制是有副作用的导入动作，必须等 P2-H 明确人工确认、哈希/大小记录和失败回滚语义。

Rejected: 允许任意本地路径进入预检。原因是这会绕过真实数据候选池的 provenance 边界，并可能把无关或敏感文件带入项目。

Rejected: 预检成功后立即重建变量角色或 RunPlan。原因是预检只证明“导入准备就绪”，不证明数据已经进入项目，也不证明字段角色已确认。

Evidence: live API 对 CFPS DTA 候选文件返回 `status=ready_for_review`、`target.path=Data/Raw/cfps2010adult_202008.dta`、`will_create_project_file=false`、`will_mutate_source=false`；Safari 数据与设计页显示 `待人工确认` 和 4 项 passed checks。

## 2026-05-14：本地版可绑定桌面数据，线上版必须上传或云化

Decision: 在 P2-H 中把真实数据预检 apply 拆成 `copy_to_project_raw`、`bind_external_reference`、`cancel` 三种显式人工动作。本地版允许复制到当前项目或只绑定本机外部引用；线上版遇到本地路径 apply 时返回 409 `cloud_upload_required`。

Reason: 用户明确区分两个产品版本：纯本地版本可以连接本地数据和本地大模型；线上版本只能使用云服务，不能直接读取用户电脑上的文件路径。产品必须把这个边界做成 API 和 UI 状态，而不是只写在说明里。

Rejected: 让线上应用绑定 `/Users/...` 这类桌面路径。原因是线上服务器无法读取用户本机路径，继续保存为可执行数据源会制造假的 provenance。

Rejected: 预检后自动复制大文件到 `Data/Raw/`。原因是复制真实研究数据是有副作用的动作，必须由用户显式点击“确认导入到项目”。

Rejected: apply 后立刻让 VariableRoleSet、DesignSpec 或 RunPlan 消费新数据。原因是导入/绑定只证明数据源被接入，还不证明字段、样本口径和变量角色已确认。

Evidence: `tests/test_external_dataset_import_apply.py` 覆盖本地复制、只绑定引用、取消和云端拒绝；Safari 数据与设计页显示 `已接入`、`已绑定外部引用`、`模式：local` 和 SHA256。

## 2026-05-14：DTA 字段画像只读元数据，不等于实证执行

Decision: P2-J 只接入 Stata `.dta` 的 metadata-only 字段画像：用 `pyreadstat.read_dta(..., metadataonly=True)` 读取字段名、变量标签、Stata storage type、display format、样本数和字段数；画像仍标记 `evidence_level=local_file`，且 `can_feed_variable_roles=false`。

Reason: 用户提供的 CFPS 等真实数据大多是 `.dta`。如果系统只能显示文件名，就无法进入严谨变量确认；但如果直接读取全量数据或直接进入回归，又会把数据理解、变量角色和模型执行混在一起。metadata-only 是当前最小安全边界。

Rejected: 把 DTA 字段画像直接写入 VariableRoleSet。原因是变量角色是研究判断，不是读取器副作用，必须经过人工确认。

Rejected: 读取整张 DTA 大表来做画像。原因是真实数据可能很大，字段画像阶段只需要变量字典和样本规模，不应让页面加载或服务被大文件拖住。

Rejected: 把 Python metadata reader 当作完整实证分析。原因是严谨实证需要后续 StatsPAI/StatsAPI、StataMCP 或 Python 执行器产出可复现日志、诊断、稳健性和 evaluator checks。

Evidence: 真实 `cfps2011adult_202202(1).dta` 画像返回 `profiled/ready`、`row_count=1279`、`column_count=723`、`row_count_source=metadata_only`，字段含 `pid=个人id`、`fid=家户号`、`provcd=省国标码`。

## 2026-05-14：严谨实证执行必须声明真实后端和候选后端

Decision: 为 full run 增加 `rigorous_empirical_execution_contract`，把当前真实执行后端、候选后端、禁止事项、数据预检和可复现入口一起写入方法执行产物和页面。当前真实执行后端是 `python_ols_adapter`；StatsPAI/StatsAPI 与 StataMCP/Stata 只标记为候选后端。

Reason: 用户明确要求具体数据分析和实证必须严谨，可以使用 StatsPAI/StatsAPI、StataMCP/Stata 或 Python。严谨的第一步不是把这些名字放到 UI 上，而是证明“哪一个后端真的执行过、读取了哪些字段、丢弃了多少行、结果从哪里复现”。

Rejected: 因为本机安装/可检测到 StatsPAI 或 Stata 就把它们标记为 `local_execution`。原因是安装存在只证明候选能力，不证明本次 run 调用了该后端，也不证明它产生了日志和结果文件。

Rejected: 只保留 Python OLS 结果而不声明统计边界。原因是用户需要知道当前结果是最小 Python OLS adapter，不是完整 StatsPAI/Stata 流水线，也还没有 robust/cluster 标准误或固定效应。

Evidence: 真实 full run `run_5ac7052232c8` 返回 `active_backend=python_ols_adapter`，StatsPAI 和 StataMCP 为 candidate backend；`data_preflight.rows_read=12`、`usable_numeric_rows=12`、`dropped_rows=0`，`reproducibility.source_entrypoint=Product/backend/project_service.py::execute_ols_task`。

## 2026-05-14：变量角色候选必须和正式 VariableRoleSet 分离

Decision: 新增 `VariableRoleCandidate` 状态机，把真实 DTA 字段画像生成的 outcome/treatment/controls/instruments 先保存为候选状态，review 操作只更新 `state/product/variable_role_candidates.json`，不写回正式 `state/product/variable_roles.json`。

Reason: 真实 CFPS 变量字典可以帮助缩小选择范围，但变量角色是研究判断，不是字段读取器或启发式推断的副作用。用户需要看到候选、审阅候选、确认候选，但正式研究状态必须等到显式变量角色编辑保存后才改变。

Rejected: 生成候选后自动覆盖正式 VariableRoleSet。原因是这会让系统把 `countyid`、`kt3_a_1` 这类启发式结果误当成论文可执行变量，风险很高。

Rejected: 只在前端内存里展示候选。原因是长时间任务和跨 session 需要可恢复状态，候选必须写入本地状态文件。

Rejected: 候选确认后立即重新生成 DesignSpec/RunPlan。原因是 `approved_candidate` 只是候选被审阅过，不是正式变量角色已经保存。

Evidence: Chrome + Computer Use 点击真实 CFPS `.dta` 的“生成变量角色候选”和“候选已确认”后，candidate 状态为 `approved_candidate`，但 `state/product/variable_roles.json` SHA256 与 mtime 均保持不变。

## 2026-05-14：候选写回正式变量角色集必须经过显式编辑器

Decision: P2-M 允许 `approved_candidate` 进入正式 VariableRoleSet，但入口必须是“载入正式编辑器 -> 人工调整 -> 保存变量角色集”。后端保存接口接收 `candidate_id`，校验候选已确认且可写回后，才把真实数据来源、candidate provenance、dataset import/profile id 和人工确认说明写入 `state/product/variable_roles.json`。

Reason: P2-L 已证明真实 DTA 字段可以形成候选，但候选仍是启发式。用户需要从候选开始编辑，而不是让系统自动把猜测变成论文变量角色。这个显式写回边界是 DesignSpec/RunPlan 消费真实数据前的必要防线。

Rejected: `approve_candidate` 后自动覆盖正式 VariableRoleSet。原因是这会把 `countyid` 这类机器猜测误提升为论文可执行变量。

Rejected: 只在前端切换字段，不把 `candidate_id` 写入正式角色集。原因是后续 DesignSpec、RunPlan、provenance 和审计无法追踪正式变量角色来自哪次真实字段候选。

Rejected: 继续要求 candidate 的 `dataset_path` 必须位于 `Data/Final`。原因是真实数据候选可能来自 `Data/Raw` 或本地外部绑定；保存边界应由 candidate 审批和 provenance 控制，而不是旧 demo 数据路径假设。

Evidence: Chrome + Computer Use 打开 `http://127.0.0.1:8765/?v=20260514-p2m`，点击“载入正式编辑器”后编辑器显示 `draft_from_candidate · local_file`、真实 CFPS DTA 路径、`candidate_id=variable_role_candidate_495092cb7af2` 和“保存后才写入正式变量角色集”。目标测试 8 OK，全量回归 198 OK。

## 2026-05-14：StatsPAI 必须从候选能力变成独立验证证据

Decision: 在 CSV OLS full run 中真实调用 StatsPAI/StatsAPI，写出 `Results/json/statspai_execution_result.json`，并把结果作为 `backend_validations` 展示在实证执行页；Python OLS adapter 仍是主执行路径，StatsPAI 是独立复核路径。

Reason: 用户指出“StatsPAI 为什么还是候选后端，为什么没有进入执行层”。如果系统只在 UI 中列出 StatsPAI，却没有运行和产物，就无法证明严谨实证执行。先从当前可控的 OLS/CSV 场景做独立验证，可以立即提升可信度，同时不伪装 DID/IV/RDD 等尚未完成的方法。

Rejected: 因为 StatsPAI 可安装就把所有方法标记为 `local_execution`。原因是可安装不等于本次 run 调用过，也不等于产生日志、结果和可复核产物。

Rejected: 用 StatsPAI 替换 Python adapter 作为唯一执行路径。原因是当前 Python adapter 已承载 run manifest、evaluator、FindingCard 绑定；StatsPAI 先做独立复核更稳，后续再抽象可替换后端。

Evidence: full run `run_bb423547439c` 的 observability 返回 `独立后端验证`、`passed`、`statspai.regress` 和 `Results/json/statspai_execution_result.json`；全量回归 203 tests OK。

## 2026-05-14：本地 Codex Supervisor 必须显式暴露，不能藏在工程状态机后面

Decision: 在 `workflow_contract` 中新增 `intelligence_layer`，并在首页新增“智能中控”面板，显式展示本地 Codex Supervisor、provider readiness、执行开关、阻塞原因和派工计划。当前本机 Codex CLI 可用，但 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC` 未启用，因此状态为 `blocked`。

Reason: 用户指出如果没有底层大模型/中控系统，产品会退化成纯逻辑条件驱动的工程体系，偏离最初构想。正确做法不是假装 Agent 已经在工作，而是把中控层作为一等产品对象，明确“可检测、未启用、下一步要真实派工”。

Rejected: 继续用静态 Agent 卡片暗示智能编排。原因是这无法证明模型是否可用、是否允许执行、是否生成计划，也无法给用户确定感。

Rejected: 默认打开本地 Codex 执行。原因是模型 subprocess 可能产生外部调用、费用和不确定输出；必须由环境开关显式启用，并把每次计划/派工写入可审计产物。

Evidence: `GET /api/v1/providers/local-codex` 返回 `available=true`、`execution_enabled=false`；overview API 返回 `intelligence_layer.status=blocked` 和 blocker `local_codex_execution_not_enabled`；Chrome 页面显示“本地 Codex Supervisor 未启用”和派工计划。

## 2026-05-16：SupervisorPlan 是待审计划，不是自动写回

Decision: 新增 `state/product/supervisor_plan.json` 作为本地 Codex Supervisor 的持久化计划产物。生成计划前必须显式启用 `EMPIRICAL_WORKFLOW_ENABLE_CODEX_EXEC=1`；生成后的计划状态为 `needs_review`，只包含阶段计划、风险、证据要求、子 Agent 分工、人工 gate 和下一步建议。

Reason: 用户指出系统必须有底层大模型中控，但不能让大模型绕过工程审计和人工确认。把 Codex 输出落为可审阅 artifact，可以让中控真实进入产品，同时保留 VariableRoleSet、DesignSpec、RunPlan 的确定性边界。

Rejected: 让 Supervisor 直接改写 `state/product/variable_roles.json`、`state/product/design_spec.json` 或 `state/product/run_plan.json`。原因是这些是用户确认过的正式研究状态，LLM 输出必须先进入人工审阅。

Rejected: 未启用执行开关时生成 mock plan。原因是这会把工程状态机伪装成真实智能中控，违反 evidence_level 和用户确定性要求。

Evidence: `tests/test_supervisor_plan.py` 覆盖默认阻断、启用后持久化、正式研究状态不变和前端审阅台；全量回归 208 tests OK；`POST /api/v1/projects/proj_undergraduate_thesis/supervisor-plan` 在默认环境返回 409 `local_codex_execution_not_enabled`。

## 2026-05-16：首页必须先给决策信号，再按需展开细节

Decision: 首页的智能中控和 SupervisorPlan 审阅台改为渐进披露。默认只展示状态、证据等级、主操作、阻塞数量和下一步摘要；Provider、派工、写入边界、证据要求、风险等细节放入原生 `details/summary`，由用户点击展开。

Reason: 用户指出当前页面把具体信息全部摊开，会冲击短时记忆，让人不知道下一步怎么用产品。研究工作台应先告诉用户“现在能不能继续、下一步做什么、哪里有风险”，而不是把审计字段当首屏主体。

Rejected: 继续通过缩小字体或压缩卡片解决拥挤。原因是根因不是样式密度，而是信息层级错误。

Rejected: 删除 Provider、派工、证据要求和风险等细节。原因是这些是审计材料，必须保留，只是不应默认暴露。

Evidence: 新增 BDD 和前端测试锁定 `查看中控详情`、`查看计划详情`；全量回归 210 tests OK；右侧内置浏览器验证两个详情块初始关闭，点击后可展开。

## 2026-05-16：首页必须先进入研究选题，而不是直接摊开全功能工作台

Decision: 首页新增 `research-topic-intake`，默认先让用户输入研究选题、从已有选题继续，或进入真实数据候选池。原有下一步研究决策、智能中控、SupervisorPlan、风险和证据审计移动到 `research-workbench-after-topic`，确认选题后才展示。

Reason: 用户指出当前产品一进来就铺开所有模块，会让用户不知道如何开始。实证研究产品的第一动作应该是“我要研究什么”，而不是先理解系统的 Agent、执行、证据和文件结构。

Rejected: 继续在首页压缩卡片、缩小字体或只做视觉清理。原因是根因是产品入口错误，不是样式密度。

Rejected: 删除智能中控、SupervisorPlan 和证据审计。原因是这些是研究可审计性的核心，只是不应该作为首屏默认信息。

Rejected: 选题确认后自动改写 VariableRoleSet、DesignSpec、RunPlan 或 SupervisorPlan。原因是本轮只有前端选题上下文，还没有后端 ResearchQuestion 审计状态。

Evidence: 新增 BDD 和 3 条前端契约测试；全量回归 213 tests OK；右侧内置浏览器验证初始只显示选题入口，确认选题后才展开研究判断区。

## 2026-05-16：SupervisorPlan 必须绑定已确认选题

Decision: SupervisorPlan 生成前必须存在 `status=confirmed` 的 `ResearchQuestion`，并把 `question`、`topic_session_id`、`version`、`evidence_level` 和 `path` 写入计划的输入证据。传给本地 Codex 的 prompt 也必须包含 `confirmed_research_question`。

Reason: 用户指出系统必须有大模型中控，但中控必须围绕用户确认的研究问题工作。没有选题绑定的计划只是泛化工作清单，无法支撑后续人工审批、Agent 派工和论文证据链。

Rejected: 让 SupervisorPlan 使用 project seed draft 作为默认研究问题。原因是 project seed 可能来自 `paper.yaml` 初始配置，不等于用户在当前产品流中确认过的题目。

Rejected: 只在前端显示选题，不写入 SupervisorPlan 输入证据。原因是后续任务队列、审计日志和跨 Session 恢复需要后端可追溯状态。

Evidence: `tests/test_supervisor_plan.py` 验证缺选题返回 409 `research_question_required`，生成计划包含 `input_research_question` 和 `research_question_version`，fake Codex 检查 prompt 必须包含 `confirmed_research_question` 和 `topic_session_v1`。

## 2026-05-16：SupervisorPlan 审批只授权派工，不修改研究状态

Decision: 新增 SupervisorPlan review 状态机。`approve` 把计划标记为 `approved` 并设置 `can_dispatch=true`；`needs_revision` 和 `reject` 都保留计划但阻断派工；每次审批写入 `human_review`、决策日志和下一步动作。

Reason: 本地 Codex Supervisor 已经能生成待审计划，但计划仍是 LLM 产物。进入任务队列前必须有人工审阅边界，否则系统会把“模型建议”误当成“已确认研究设计”。

Rejected: 生成 SupervisorPlan 后自动创建 Agent Task Queue。原因是没有人工审批的计划可能包含错误变量、错误方法或不完整证据要求。

Rejected: 审批时顺手改写 ResearchQuestion、VariableRoleSet、DesignSpec 或 RunPlan。原因是审批只回答“这份计划能否派工”，不能替用户修改正式研究对象。

Rejected: 在没有 `state/product/supervisor_plan.json` 时显示批准/驳回按钮。原因是用户不能审批一份不存在的计划；当前真实项目没有计划产物时应只显示生成入口。

Evidence: `python3 -m unittest tests.test_supervisor_plan -v` 13 tests OK；全量回归 226 tests OK，skipped=1；浏览器验收 `http://127.0.0.1:8767/?v=20260516-p2t-supervisor-review1` 在无计划状态下只显示生成入口，符合审批前置条件。

## 2026-05-17：移动 UI 参考学习的可复用结论

Decision: 把 Bilibili/Kole Jain Mobile App UI 参考资料转化为产品信息架构原则，而不是复制视觉风格。核心原则是：一屏一个主任务、默认隐藏高噪声明细、主操作随对象状态变化、空状态必须给出下一步。

Reason: 用户指出当前页面容易把信息一次性铺满，冲爆短时记忆。移动 UI 教程虽然面向手机，但它对小屏和注意力的约束正好能修正我们产品的信息密度问题。

Rejected: 直接复制 Kole Jain 的暗色界面、移动 app 内容或 Figma 结构。原因是我们的产品是实证研究工作台，需要证据、审计、状态机和可复现产物，而不是通用任务笔记 app。

Rejected: 用缩小字号和压缩间距解决拥挤。原因是视频中的核心观点是小屏上内容往往要更大，真正要减少的是同时出现的决策数量。

Evidence: 视频、音频、转写、Kole Jain `.fig` 和 5 张预览图已保存到本地 `artifacts/reference-learning/`；可提交学习笔记为 `docs/reference-learning/mobile-app-ui-kole-jain-bilibili-2026-05-17.md`。

## 2026-05-17：Agent Task Queue 是 approved SupervisorPlan 的派工草案，不是自动执行器

Decision: 新增 `state/product/agent_task_queue.json` 作为 approved SupervisorPlan 的可审阅派工草案。只有 `status=approved` 且 `can_dispatch=true` 的 SupervisorPlan 能创建队列；队列项记录 owner agent、角色、任务摘要、输入证据、输出要求、风险、阻塞项和审计日志。前端默认只展示摘要、负责人、阻塞和状态，高噪声明细进入按需展开。

Reason: 用户要求把本地 Codex Supervisor 从“计划建议”推进到“可执行任务组织”，但不能让 LLM 直接篡改变量角色、设计方案或执行计划。Agent Task Queue 是计划和执行之间的审计边界：它把任务拆出来给人检查，不代表已经派工或已经执行。

Rejected: 生成 SupervisorPlan 后自动创建任务队列。原因是未经人工 approve 的计划仍可能包含错误变量、错误方法或不完整证据要求。

Rejected: 创建队列后立即启动子 Agent。原因是用户需要先看到任务摘要、输入证据、输出要求和阻塞项；自动执行会绕过任务级人工 gate。

Rejected: 复用旧 workflow mock tasks 作为产品任务队列。原因是旧 tasks 属于 demo 工作流，不绑定 approved SupervisorPlan 和当前研究证据链，容易把 mock 状态伪装成真实派工。

Evidence: `python3 -m unittest tests.test_agent_task_queue -v` 8 tests OK；`python3 -m unittest discover -s tests -v` 234 tests OK，skipped=1；浏览器真实项目显示 `缺少 SupervisorPlan` 且按钮 disabled；受控 approved-plan 场景点击创建后显示 2 个任务、2 个详情默认折叠、无 console error。

## 2026-05-17：真实字段候选 promotion 只能生成草稿，不能覆盖正式变量角色

Decision: 新增 `state/product/variable_roles_drafts.json`，让 approved `VariableRoleCandidate` 通过显式 promotion 生成可编辑 `VariableRoleSet` 草稿。正式 `state/product/variable_roles.json` 只能由用户在正式变量角色编辑器中保存写入，并记录 source candidate 与 draft provenance。

Reason: 真实 CFPS 字段候选仍是启发式。它能缩小审阅范围，但不能自动成为论文分析变量。把“候选建议 -> 可编辑草稿 -> 正式保存”拆成三层，可以让用户看见每一步的证据边界，同时保留跨 Session 恢复能力。

Rejected: 点击 `候选已确认` 后自动覆盖正式 VariableRoleSet。原因是这会把字段名/标签规则猜出来的变量角色误提升为正式研究设定。

Rejected: Promotion 后立刻重建 DesignSpec 或 RunPlan。原因是方法设计和执行计划都依赖用户确认后的正式变量角色，不能由候选草稿副作用触发。

Rejected: 只在前端内存里放草稿。原因是长时间任务和跨 Session 需要可恢复的 draft 状态。

Evidence: `tests/test_real_variable_role_promotion.py` 覆盖 approved candidate promotion、正式 state 不被覆盖、保存后 provenance 和前端候选/正式分离；全量回归 243 tests OK；浏览器点击 promotion 后 `badResponses=[]`、`consoleErrors=[]`。
