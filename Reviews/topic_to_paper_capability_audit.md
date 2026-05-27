# Topic-to-Paper Capability Audit

- 题目：社会资本对居民主观幸福感的影响研究--基于CGSS数据的实证分析
- 当前状态：new_topic_requires_data_binding
- 当前题目复现能力：not_reproducible_until_topic_data_binding
- 任意新题目全自动成文：尚未成立
- 验收目标：先追求：硕士课程论文/毕业论文初稿级完整 PDF 包。

这不是不能写文章，而是还没有把 CGSS 新题目接入主链路。

这不是不能写文章，而是要先把题目、数据、变量、方法、文献和修订链路接起来。

## Gates

- topic_fit: new_topic_requires_data_binding
- formal_package: ready
- manual_acceptance: pending_human_review
- paper_structure_length: needs_work
- literature_review: needs_human_review
- method_gate: needs_human_review
- reviewer_revision_loop: ready_for_human_review
- final_artifacts: ready

## 差距矩阵

### 题目到数据绑定
- 负责人：DataAgent
- 当前状态：needs_work
- 现在是什么情况：题目指向 CGSS，但当前正式研究问题仍是：工业机器人应用对劳动力市场匹配效率的影响
- 下一步：扫描本地数据资产，确认 CGSS 文件、年份、样本口径和可用字段。
- 做到什么算过：产出 DatasetBinding 和字段画像，明确该题目使用哪个 CGSS 文件、哪些变量和多少样本。

### 专家级变量角色选择
- 负责人：Supervisor+MethodAgent
- 当前状态：needs_work
- 现在是什么情况：还需要把字段画像转成因变量、核心解释变量、控制变量和可能机制变量，并给出理由。
- 下一步：生成 VariableRoleSet 草案，并绑定数据画像、文献依据和识别逻辑。
- 做到什么算过：每个核心变量都有来源字段、测量解释、缺失率、方向预期和人工审阅状态。

### 方法族和前置条件
- 负责人：MethodAgent
- 当前状态：waiting_for_data_binding
- 现在是什么情况：需要根据 CGSS 数据结构判断适合 OLS/Ordered Logit/FE/IV/PSM/DID 等哪条路线。
- 下一步：先做 baseline 方法门，再列出不能进入的方法和需要补的证据。
- 做到什么算过：方法门输出 green/yellow/red，并说明每种方法的进入条件、诊断和稳健性要求。

### 文献综述闭环
- 负责人：LiteratureAgent
- 当前状态：needs_work
- 现在是什么情况：需要围绕社会资本、主观幸福感、CGSS 应用和中国情境建立可核验文献包。
- 下一步：生成 seed literature、CNKI/Scholar/Zotero 检索队列、候选参考文献和引用绑定。
- 做到什么算过：文献条目能核验来源，综述段落能绑定引用，参考文献候选进入人工批准队列。

### 审稿式修订和导出
- 负责人：ReviewerAgent+ExportAgent
- 当前状态：waiting_for_upstream
- 现在是什么情况：新题目需要先完成前四层，才能进入成文、审稿修订和 PDF 预检。
- 下一步：等数据、变量、方法和文献包就绪后，生成章节草稿、审稿意见和导出预检。
- 做到什么算过：修订队列全部有证据回应，PDF 包含正文、表图、参考文献、复现说明和审计记录。

## Agent Team 路由

- 第一位调用：DataAgent
- 原因：新题目第一步必须先找数据和字段，不应直接写文献综述或跑模型。
- DataAgent：把 CGSS 数据、字段和样本口径接到题目
- Supervisor+MethodAgent
- LiteratureAgent
- MethodAgent
- ReviewerAgent+ExportAgent

## Review Targets

- Submissions/formal_package/paper.pdf
- Submissions/formal_package/paper.docx

## Next Tasks

- run_cgss_data_discovery
- bind_topic_to_cgss_dataset
- discover_cgss_social_capital_happiness_variables
- draft_cgss_variable_roles
- build_cgss_literature_seed_package
- run_cgss_method_gate
