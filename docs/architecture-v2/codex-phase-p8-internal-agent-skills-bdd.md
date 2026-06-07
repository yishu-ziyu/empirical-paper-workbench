# Phase P8 Internal Agent Skills BDD

## 背景

外部项目如 Auto-Empirical-Research-Skills、AER-Skills、StatsPAI、Maigret、autoresearch 提供了经过实践验证的 Agent Skill、方法质量门、benchmark 和递归研究思路。我们的产品不应把这些内容当普通资料阅读，也不应整仓库复制进正式方法库，而应把它们转译为本产品的内部 Agent Skill 契约。

内部 Agent Skill 的职责是回答五个问题：

1. 什么时候调用。
2. 由哪个 Agent 调用。
3. 输入和产出是什么。
4. 哪些质量门必须过。
5. 什么时候必须收回到人工确认。

## 行为用例

### BDD-1: 外部来源必须保留为可审计来源

Given 系统内置一批由 AERS/AER-Skills/StatsPAI 等外部实践转译而来的内部 Agent Skill 候选
When 能力目录重新索引内部 Agent Skill Registry
Then 每个内部 Skill 必须保留 external_sources、license、attribution 和 transformation_log
And 系统必须明确它是 internal_draft，而不是已人工合并的 canonical 规则。

业务规则：外部优质实践可以被吸收，但来源、许可证和改写记录必须可追踪。

### BDD-2: 内部 Skill 默认不能静默改写正式层

Given Auto Mode 调用内部 Agent Skill
When Skill 需要修改变量角色、研究设计、运行计划或正式论文内容
Then 它只能输出 state_patch_proposal 或 artifact
And formal_write_targets 必须为空，直到人工 review 后才允许进入正式层。

业务规则：Agent 可以很能干，但不能偷偷替研究者改正式研究设定。

### BDD-3: Skill 必须绑定研究生命周期阶段和 Agent 分工

Given Supervisor 为一个研究题目生成执行计划
When 它浏览内部 Agent Skill Registry
Then 文献递归搜索、方法识别门、复现包门、投稿预检等 Skill 必须声明 applies_when.stage、owner_agent、allowed_agents 和 required_state。

业务规则：Skill 不是泛泛提示词，必须知道它在哪个阶段、由谁干、需要什么前置状态。

### BDD-4: 方法类 Skill 必须暴露质量门和 benchmark 来源

Given 研究计划涉及 DID、IV 或 RDD 等因果识别方法
When MethodAgent 选择内部方法 Skill
Then Skill 必须列出 machine_checkable、manual_review 和 benchmark 绑定
And high/critical 风险门未关闭时不得进入默认 RunPlan。

业务规则：方法判断要靠可检查的质量门，不靠“看起来懂计量”的文字。

### BDD-5: 能力目录必须把内部 Skill 作为产品能力展示

Given 用户进入 Agent 能力目录或 Supervisor 生成计划
When capability registry 重新索引
Then registry.sources 必须包含 internal_agent_skill_registry
And capabilities 必须包含 internal_agent_skill namespace 的条目
And 这些条目默认是 checklist/template，而不是 executable。

业务规则：先让系统能发现和编排这些 Skill，再逐步接执行器。

### BDD-6: 缺少内部 Skill Registry 不能影响现有产品运行

Given 内部 Skill Registry 文件不存在或格式不可读
When capability registry 重新索引
Then 系统必须返回 available=false 和空能力列表
And 不能影响 StatsPAI、AERS 和 product builtin 能力索引。

业务规则：这是增强层，不应让现有执行链因为 registry 缺失而崩。

## 第一批内部 Skill 候选

1. `recursive_research_search`: 从题目出发做递归文献、变量、数据和证据搜索。
2. `did_staggered_identification_gate`: 交错 DID / TWFE 风险 / CS-BJS 替代方案门。
3. `weak_iv_diagnostic_gate`: 弱工具变量、第一阶段、AR/LIML 稳健推断门。
4. `aer_abstract_submission_preflight`: AER-like 摘要、投稿格式、披露和表图预检。
5. `replication_package_gate`: 复现包、一键复现、环境锁定和审稿式质询门。

## 边界

- 第一版只做 registry、schema、capability indexing，不直接启动真实执行器。
- 第一版不复制 AERS 仓库，不把外部 Skill 原文塞进 prompt。
- 第一版不把 internal_draft 自动提升为 canonical。
- 第一版不改 UI。
