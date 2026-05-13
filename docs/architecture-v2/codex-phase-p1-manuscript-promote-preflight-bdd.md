# Codex Phase P1-M BDD: Manuscript Candidate Promote Preflight

## 目标

将已人工确认的 Manuscript candidate 推进到“可进入导出前检查”的状态，但不得直接覆盖 `Manuscripts/generated/paper_draft.md`。Promote 是一个可审计的本地状态，不是最终写回。

## 行为用例

### 行为 1：未审阅 candidate 不能 promote

Given 一个项目已经有 approved FindingCard 并生成 Manuscript candidate  
And 该 candidate 尚未完成 candidate review  
When 用户请求 promote 该 candidate  
Then API 返回 `candidate_review_required`  
And `Manuscripts/generated/paper_draft.md` 内容保持不变

业务规则：正文候选必须先经过人工确认，不能因为 FindingCard 已 approved 就自动进入论文写回链路。

### 行为 2：approved candidate 可以生成 promote preflight

Given 一个 Manuscript candidate 的 review_status 为 `approved`  
When 用户请求 promote 该 candidate  
Then 系统写入 `state/product/manuscript_candidate_promotions.json`  
And 返回 `promotion_status=ready_for_export`  
And 返回 `can_export=true`、`can_write_back=false`  
And `Manuscripts/generated/paper_draft.md` 内容保持不变

业务规则：promote 只表示“该段落通过人工审阅并进入导出前检查”，不是自动覆盖草稿。

### 行为 3：rejected / needs_revision candidate 不能 promote

Given 一个 candidate 被标记为 `rejected` 或 `needs_revision`  
When 用户请求 promote  
Then API 返回 `candidate_review_required`  
And 不写入 promotion 状态

业务规则：需要修改或被拒绝的段落不能进入最终产物链路。

### 行为 4：不存在的 candidate 必须结构化拒绝

Given 用户请求 promote 一个不存在的 candidate_id  
When API 处理请求  
Then 返回 404 和 `manuscript_candidate_not_found`

业务规则：不能为不存在的派生候选创建孤立 promotion 记录。

### 行为 5：前端只提供 promote preflight，不提供直接覆盖草稿

Given Results & Draft 页面展示 Manuscript candidates  
When candidate 已 approved  
Then 页面显示 promote preflight 操作和 promotion 状态  
And 页面不出现 `overwrite-paper-draft` 或直接写回草稿的操作

业务规则：用户应看到下一步是进入导出前检查，而不是不透明地改写论文源文件。

## 边界条件

- 本阶段不生成 docx，也不改写 Markdown 正文。
- Promote 状态保存在 `state/product/`，证据等级为 `local_file`。
- 真正的 write-back / export package 应在后续 P1-N 中单独建 BDD。
