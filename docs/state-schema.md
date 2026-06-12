# 状态契约

本文档定义当前实证研究 OS 的核心状态对象、落盘位置和 gate。它的作用是防止系统退化成“只会写一篇像论文的文本”。每个对象都必须能说明来源、证据等级、是否需要人工确认、是否允许进入正式层。

## 1. 核心对象

### ResearchQuestion

ResearchQuestion -> state/product/research_question.json。它记录题目、研究对象、因果方向、样本范围、数据线索、方法偏好和用户原始输入。没有 ResearchQuestion 时，后续阶段只能显示空态或提示用户先创建任务。

### VariableRoleSet

VariableRoleSet -> state/product/variable_roles.json。草案路径可以是 `state/product/variable_roles_drafts.json`，候选路径可以是 `state/product/variable_role_candidates.json`。它应包含 outcome、treatment、controls、instruments、fixed_effects、sample_filters、source_file、evidence_level、review_status。Data Gate 通过前，变量角色只能是 draft 或 needs_human_review。

### DesignSpec

DesignSpec -> state/product/design_spec.json。它包含识别策略、模型公式、样本单位、时间维度、处理变量定义、工具变量定义、DID/IV/RDD/PSM/DML 等方法前置条件。Design Gate 检查变量是否存在、方法是否匹配数据结构、核心假设是否被明确写出。

### RunPlan

RunPlan -> state/product/run_plan.json。它把 DesignSpec 转成可执行步骤：后端选择、脚本、参数、输入数据、输出表格、预期 artifact。RunPlan 可以由 Supervisor 或 DesignAgent 起草，但正式执行前需要可审计的 plan id 和状态。

### MethodExecutionResult

MethodExecutionResult -> Results/json/method_execution_result.json。StatsPAI 结果也可能落在 `Results/json/statspai_execution_result.json`，run 级结果可以挂在 `state/runs/{run_id}` 下。它包含模型、系数、标准误、p 值、样本量、固定效应、聚类方式、诊断、表格路径、图路径和 evidence_level。只有 local_execution 的结果才能进入结果解释。

### Finding

Finding -> Results/json/approved_findings.json。review 记录可以落在 `state/product/finding_reviews.json`。Finding 必须绑定 evidence_id、MethodExecutionResult、表格或图、解释文本、限制条件、claim_strength。没有证据绑定的 Finding 只能停留在 exploratory。

### ExportPackage

ExportPackage -> state/product/export_package_manifest.json。正式导出材料落在 `Submissions`，例如 `Submissions/formal_package/manifest.json`、PDF、DOCX、README、复现脚本、数据说明、表格和图。ExportPackage 只有通过 Export Gate 后才代表正式输出。

### AgentTask

AgentTask -> state/product/agent_task_queue.json。它记录 agent、skill、输入、输出、状态、阻塞原因、成本、权限、evidence_level、audit_events。AgentTask 是 Agent Task Queue 的数据源。

### Capability

Capability -> state/product/capabilities.json。它描述可用 skill、StatsPAI 函数、StataMCP、Python 脚本、文献检索器、导出器和 Verifier。Capability 需要包含 schema、适用方法、输入要求、输出类型和限制。

## 2. 文件分区

当前项目存在多类状态目录，不能混用：

- Product/state：项目与 workflow registry，包含 `projects.json`、`workflows/{workflow_id}/workflow.json`、`tasks.json`、`artifacts.json`。
- state/product：核心产品状态，包含 ResearchQuestion、VariableRoleSet、DesignSpec、RunPlan、SupervisorPlan、AgentTask、Capability、review、promotion、preflight、writeback approval。
- state/runs：可观察执行状态，包含 run index、run manifest、run steps、run events、gates。
- Results/json：执行和分析结果，包含 MethodExecutionResult、StatsPAI result、回归表、稳健性矩阵、verified literature、approved findings、formal writeback。
- Manuscripts：草稿层和生成论文片段。
- Submissions：候选 PDF、正式 PDF/DOCX、manifest、复现包和提交材料。

## 3. Gate

### Data Gate

检查数据和变量是否足够进入研究设计。最低要求：数据源存在、schema 可读、变量角色已确认、关键变量没有占位符、样本单位和时间范围明确。

### Design Gate

检查 DesignSpec 是否足够进入 RunPlan。最低要求：方法与数据结构匹配、处理变量/工具变量/固定效应定义清楚、核心识别假设写明、需要的诊断任务已加入队列。

### Execution Gate

检查 RunPlan 是否可以真实运行。最低要求：输入文件存在、后端可用、脚本可生成或已存在、输出路径确定、失败日志可写入、run id 可追踪。

### Result Gate

检查结果是否可以进入 Finding。最低要求：MethodExecutionResult 为 local_execution、主表存在、样本量和系数一致、稳健性状态明确、失败项不被包装成成功结论。

### Export Gate

检查正式层输出是否可以生成。最低要求：无占位符、引用已校验、evidence_id 都能找到真实结果、PDF/DOCX 预检通过、writeback approval 存在、复现包 manifest 完整。

## 4. 状态字段约定

建议所有核心对象使用统一状态：

- empty：尚未创建。
- draft：已生成草案。
- needs_human_review：需要用户或专家确认。
- approved：已确认，可进入下一阶段。
- running：正在执行。
- failed：执行失败，需要诊断。
- blocked：缺少输入、权限、数据或工具。
- deprecated：已弃用但保留历史。
- exported：已进入正式导出包。

证据字段建议命名为 `evidence_level`，常用值包括：

- mock：legacy/demo workflow artifact，不能当真实执行证据。
- local_file：本地文件、配置、人工确认记录或草稿状态。
- local_execution：本机实际运行生成的结果、日志、表格或图。
- local_aggregate：系统状态聚合结果，常用于状态栏。
- llm_supervisor：计划或队列由 LLM Supervisor 参与生成，需要保留模型、提示词或审计摘要。
- external_source：外部文献、网页、CNKI、Crossref、Scholar、GitHub 或其他公开来源。
- reviewed：用户、Verifier 或人工审阅明确确认。

正式层写回必须拒绝 `mock` 和缺失 evidence 的对象。`local_file` 也不等于 `local_execution`：本地文件可以证明“材料存在”，但不能证明“回归已经真实运行”。

## 5. 后续实现规则

新增功能先问三个问题：

1. 它创建或更新哪个 canonical object？
2. 它通过哪个 gate？
3. 它的证据等级是什么？

如果回答不出来，就先补状态契约，不要直接写 UI 或论文正文。
