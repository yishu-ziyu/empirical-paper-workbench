# CHARLS Proof Case To Agent Product Correction

日期：2026-06-18

## 结论

本项目的产品化路线被执行偏了。第一层 CLI 已经证明过：系统可以把一个真实题目和真实数据推进到接近课程论文级的 `paper.pdf`。第二层 Agent 和第三层 UI 不应该重写目标，也不应该把门禁、看板、状态卡当作最终成果。

正确目标是：

```text
第一层 CLI 成功路径
-> 第二层 Agent 调度同一套研究流水线
-> 第三层 UI 只消费稳定的 headless 状态、动作和产物
```

验收标准不是“能生成一个 PDF 文件”，而是“生成一份至少达到 CHARLS 医保样例质量下限的课程论文级初稿 PDF，并附带证据链、复现链和 claim audit”。

## CHARLS 医保样例的真实成功路径

样例路径：

- 项目：`/Users/mahaoxuan/Desktop/经济学论文/StatspAI_跑通一次_CHARLS_DID`
- 主论文：`paper.pdf`
- 主源码：`paper.tex`
- 运行清单：`run_manifest.json`
- 复现报告：`repro_report.md`
- Claim audit：`claim_audit.md`

从 `run_manifest.json` 看，第一层 CLI 不是一次 OLS 加 PDF，而是一条可复现论文流水线：

1. `01_data_contract.py`：确认数据入口、变量和原始数据边界。
2. `02_sample_construct.py`：构造分析样本。
3. `03_table1.py`：生成描述统计。
4. `04_data_gate.py`：做数据质量和样本门禁。
5. `05_event_study.py`：生成识别设计相关图形。
6. `06_table2.py`：生成主结果表。
7. `07_heterogeneity.py`：生成异质性结果。
8. `08_robustness.py`：生成稳健性和 placebo。
9. `09_supplemental.py` 到 `14_selection_model.py`：补充表、排版、修订稳健性和选择模型。
10. `15_verify_bibliography.py` + LaTeX build + `verify_repro.py`：引用核验、论文编译、哈希复现门禁。

它的最低质量特征：

- 有完整论文结构：摘要、引言、文献、背景、数据、方法、结果、稳健性、结论、参考文献。
- 有真实表图：Table 1、主结果表、稳健性表、异质性表、event-study 图、spec curve 等。
- 有方法诊断：DID/TWFE、placebo、two-way clustering、规格敏感性。
- 有 claim audit：每个核心 claim 必须绑定表、图、脚本、文献或审阅记录。
- 有复现门禁：脚本顺序、hash baseline、bibliography gate、LaTeX build gate。

## 当前父母教育工资样例的问题

当前 `Submissions/parent_education_wage_final_paper.pdf` 只证明 PDF 导出链路能工作，不证明论文质量达标。

当前稿件只有约 1000 个中文字符，章节是：

```text
摘要
数据与变量
方法
结果
审阅边界
证据路径
```

它缺少：

- 文献综述和 contribution matrix。
- 制度背景、理论机制或研究动机。
- 正式识别策略和方法门。
- 描述统计表、主结果表、稳健性表、异质性分析、图形。
- claim audit。
- bibliography verification。
- reproducibility hash gate。
- 课程论文级篇幅和结构。

因此它只能标记为 `pdf_export_smoke_only`，不能标记为 submission ready，也不能作为课程论文级交付物。

## 第二层 Agent 必须复用的能力

第二层 Agent 的职责不是把 UI 状态串起来，而是把 CLI 成功路径产品化成可调度任务：

1. ResearchIntentAgent：从题目生成研究问题、边界、成功标准。
2. LiteratureAgent：生成检索计划、候选文献、核验文献、贡献矩阵。
3. DataAgent：生成数据 contract、样本构造、变量定义、缺失报告。
4. MethodAgent：调用 StatsPAI / method gate / AER identification 规则，选择识别设计并写前置诊断。
5. ExecutionAgent：按 RunPlan 执行真实统计后端，输出表、图、日志和结果 JSON。
6. RobustnessAgent：生成稳健性、placebo、异质性、机制或替代规格。
7. ManuscriptAgent：基于证据写完整论文草稿，而不是写几段摘要。
8. ReviewerAgent：执行 paper quality gate、claim audit、method gate、evidence gate。
9. ReplicationAgent：生成 reproduce README、manifest、hash baseline 和 bibliography gate。
10. ExportAgent：只有通过质量门后，才生成 course-paper-ready PDF；否则输出修订队列。

## 技能路由

下一轮实现时，Agent 不能忽略已有 skills 和规则库：

- `StatsPAI_skill`：数据清洗后的 EDA、pre-flight、estimand-first、DAG、估计、诊断和稳健性。
- `aer-workflow`：路由 topic selection、identification、robustness、tables/figures、replication、submission。
- `docs/architecture-v2/method-gate-standard-2026-05-26.md`：方法门最低标准。
- `docs/architecture-v2/paper-package-quality-standard-2026-05-26.md`：论文包质量门。
- `docs/architecture-v2/north-star-cli-first-research-os-plan-2026-05-26.md`：CLI-first 到产品化的北极星。

## 下一步开发控制

下一步不继续修 UI，不继续扩展看板，不继续把 fixed demo adapter 当作完成。

必须先做：

1. 将当前父母教育 PDF 降级为 `pdf_export_smoke_only`。
2. 建立 `course_paper_quality_gate`，最小对齐 CHARLS 医保样例的结构、篇幅、表图、文献、方法、claim audit 和复现门。
3. 建立 `charls_like_pipeline_adapter`：把题目、数据集和方法候选映射到 10 个可执行 Agent 节点。
4. 用父母教育工资样例重新跑一轮，不以 PDF 生成成功为终点，而以质量门 `ready_for_course_paper_review` 为终点。

