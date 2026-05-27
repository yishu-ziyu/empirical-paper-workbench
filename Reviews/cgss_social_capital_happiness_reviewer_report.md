# CGSS 审稿式修订报告

- 状态：`needs_human_revision_review`
- 草案层：`true`
- 正式层写回：`false`

## 审稿发现
### paper_structure
- 严重程度：`major`
- 发现：完整探索性稿已形成，但当前约 5399 个中文字符，仍低于正式论文包长度标准。
- 要求动作：按引言、文献、数据、方法、结果、稳健性和结论逐节扩写。

### literature_review
- 严重程度：`major`
- 发现：文献综述仍包含 3 类人工核验依赖，候选引用不能直接进入正式参考文献。
- 要求动作：核验 DOI、CNKI/Zotero 元数据、CGSS 官方来源和中文核心文献。

### data_and_variables
- 严重程度：`minor`
- 发现：CGSS2023、幸福感题项、社会资本题项和控制变量已经进入证据包，但正式稿仍需变量表。
- 要求动作：补齐题项原文、编码方向、缺失处理、样本筛选和描述性统计。

### identification_strategy
- 严重程度：`major`
- 发现：方法门状态为 yellow；当前只能支持条件相关，不能写成因果识别。
- 要求动作：明确 OLS/Ordered Logit 的主次关系，并加入横截面识别边界。

### result_interpretation
- 严重程度：`minor`
- 发现：OLS 与 Ordered Logit 结果方向一致，但需要避免把系数解释成政策处理效应。
- 要求动作：结果段落保留数字绑定，并解释有序模型系数的含义边界。

### robustness_gap
- 严重程度：`major`
- 发现：稳健性、异质性和机制检验尚未真实执行。
- 要求动作：排队分项社会资本、替代控制、地区/城乡异质性和机制路径检验。

### submission_standard_gap
- 严重程度：`major`
- 发现：当前仍是探索性草稿，未满足投稿级参考文献、表格、附录和复现说明标准。
- 要求动作：在 paper package 中补齐可复现 README、结果证据包、方法门和审稿队列。

### human_judgment_required
- 严重程度：`critical`
- 发现：主模型定位、引用采信、稳健性优先级和因果表述必须人工审阅。
- 要求动作：人工决定是否批准进入正式层或继续草案修订。
