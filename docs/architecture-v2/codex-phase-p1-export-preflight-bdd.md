# Codex Phase P1-N BDD: Export Preflight Preview

## 目标

将 `promotion_status=ready_for_export` 的 Manuscript candidate 生成可审计写回预览和 export package manifest。该阶段仍不得直接覆盖 `Manuscripts/generated/paper_draft.md`。

## 行为用例

### 行为 1：未 promote 的 candidate 不能生成 export preflight

Given 一个 Manuscript candidate 尚未进入 `ready_for_export`  
When 用户请求生成 export preflight  
Then API 返回 `candidate_promotion_required`  
And `Manuscripts/generated/paper_draft.md` 内容保持不变

业务规则：candidate review 通过后还必须经过 promote preflight，才能进入导出包链路。

### 行为 2：ready_for_export candidate 生成写回预览和 manifest

Given 一个 candidate 已经 `promotion_status=ready_for_export`  
When 用户请求生成 export preflight  
Then 系统生成 `Manuscripts/generated/previews/{candidate_id}.md`  
And 系统写入 `state/product/export_package_manifest.json`  
And API 返回 `export_status=preview_ready`、`can_write_back=false`  
And `Manuscripts/generated/paper_draft.md` 内容保持不变

业务规则：用户先看独立 preview 和 manifest，再决定是否进入真正写回或 docx export。

### 行为 3：不存在的 candidate 必须结构化拒绝

Given 用户请求一个不存在的 candidate_id  
When API 处理 export preflight  
Then 返回 404 和 `manuscript_candidate_not_found`

业务规则：不能为孤立 ID 创建导出包。

### 行为 4：前端显示 export preflight 操作和产物路径

Given Results & Draft 页面展示 ready_for_export candidate  
When 用户查看 candidate 卡片  
Then 页面显示生成写回预览的操作  
And export preflight 完成后显示 `preview_ready`、preview path 和 manifest path  
And 页面不出现 `overwrite-paper-draft`

业务规则：用户看到的是可检查产物，不是直接写回按钮。

## 边界条件

- 本阶段只生成 preview Markdown 和 manifest JSON。
- 真正写回 `paper_draft.md`、生成 docx 或发布 export package 应在后续阶段单独确认。
- Export preflight 的证据等级为 `local_file`。
