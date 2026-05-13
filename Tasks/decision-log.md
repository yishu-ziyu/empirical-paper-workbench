# Decision Log

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

## 2026-05-13：Manuscript 只消费 approved FindingCard，并生成候选而非覆盖正文

Decision: 新增 `GET /api/v1/projects/{project_id}/manuscript-candidates`，只从 `review_status=approved` 且 `can_write_to_draft=true` 的 FindingCard 派生 `manuscript_section_candidate`，并在 Results & Draft 页面显示候选段落与 provenance。

Reason: P1-J 只证明某个统计论断可以进入写作，但它还不是最终正文。Manuscript 阶段需要一个中间候选层，让用户先看见由结果证据生成的段落，再决定是否确认、修改、写回或导出。

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
