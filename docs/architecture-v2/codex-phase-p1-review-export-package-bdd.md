# Codex Phase P1-O BDD: Review & Export Package

## 背景

P1-N 已经把 `ready_for_export` 的正文候选推进到 `preview_ready`，并生成：

- `Manuscripts/generated/previews/{candidate_id}.md`
- `state/product/export_package_manifest.json`

P1-O 的目标不是直接导出 Word，也不是自动覆盖源草稿，而是把 Review & Export 页面变成可视化验收入口：用户能看到最终导出包的候选内容、检查规则、证据路径和下一步人工动作。

## 行为 1：Review & Export API 只展示 preview_ready 的导出包

Given 项目中已有 `promotion_status=ready_for_export` 且 `export_status=preview_ready` 的 manuscript candidate  
When 前端请求 `GET /api/v1/projects/{project_id}/export-package`  
Then API 返回 `packages`  
And 每个 package 包含 `candidate_id`、`export_status=preview_ready`、`writeback_preview_path`、`manifest_path`、`can_write_back=false`  
And evidence_level 必须是 `local_file`

业务规则：Review & Export 只能消费已经完成 export preflight 的候选，不得伪造导出包。

## 行为 2：导出包必须带 evaluator 检查项

Given export package 已生成  
When 用户查看 Review & Export  
Then 系统展示 evaluator checks  
And checks 至少包含 preview 文件存在、manifest 存在、结果文件绑定、promotion 决策存在、未自动写回源草稿  
And 每个 check 都有 `status`、`evidence_level` 和可追溯路径

业务规则：借鉴 Frontier-Eng 的 evaluator 思路，导出前必须先看到检查规则和反馈，而不是只看到一个下载按钮。

## 行为 3：页面必须显示 Frontier-Eng 式迭代日志

Given export package 来自一次 full run 和 manuscript candidate  
When 用户查看 Review & Export  
Then 页面显示 `objective -> baseline -> evaluator -> next_iteration` 的迭代闭环  
And 显示当前 run_id、candidate_id、timestamp 和下一步人工动作

业务规则：系统要把“提出方案 -> 运行 -> 反馈 -> 再改”的科研工程闭环显式化，方便用户判断是否继续迭代。

## 行为 4：前端提供可视化验收入口

Given 用户打开 Review & Export 页面  
When export package 已经 `preview_ready`  
Then 页面显示 `export-package-workbench`  
And 页面显示 `export-evaluator-checks`、`frontier-iteration-log`、`writeback_preview_path`、`can_write_back=false`  
And 页面提供返回 Results & Draft 的操作 `data-open-results-draft`

业务规则：用户必须能通过页面亲自确认导出包来自哪里、检查是否通过、下一步该点哪里。

## 当前边界

- P1-O 不自动覆盖 `Manuscripts/generated/paper_draft.md`。
- P1-O 不直接生成最终 docx。
- P1-O 不调用 Feynman CLI；只吸收 Frontier-Eng 的 evaluator/iteration log 方法论。
