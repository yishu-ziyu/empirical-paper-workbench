# P1-P Writeback Approval / Docx Preflight BDD

## 背景

P1-O 已经把 approved finding 转成 `preview_ready` 导出包，但仍停留在“只生成预览、不允许写回”的保护状态。P1-P 要补上两个产品级验收闸口：

1. 用户必须显式审批 writeback，系统才可把导出包标记为允许进入正文写回。
2. docx 导出前必须先生成预检清单，检查源草稿、预览文件、导出命令和目标 docx 路径是否齐备。

这一步仍然不自动覆盖 `Manuscripts/generated/paper_draft.md`，也不直接生成 docx。它只把“可以写回 / 可以导出”从隐含按钮变成可追溯的人工验收状态。

## 行为 1：导出包默认暴露审批与 docx 预检状态

Given 项目已经存在 `preview_ready` 导出包  
When 用户读取 `GET /api/v1/projects/{project_id}/export-package`  
Then 每个 package 必须包含 `writeback_approval.status=not_requested`  
And 每个 package 必须包含 `docx_preflight.status=not_generated`  
And package 顶层 `can_write_back=false`  
And `available_actions` 明确列出 `request_writeback_approval`

业务规则：preview_ready 只代表“预览清单已生成”，不代表正文可以被写回。

## 行为 2：显式写回审批会持久化，但不覆盖源草稿

Given 项目已经存在 `preview_ready` 导出包  
When 用户调用 writeback approval API 并选择 `approve`  
Then 系统把审批写入 `state/product/writeback_approvals.json`  
And 返回 `writeback_approval.status=approved` 与 `can_write_back=true`  
And `Manuscripts/generated/paper_draft.md` 内容保持不变  
And 再次读取 export package 时可以看到该审批状态

业务规则：审批是状态写入，不是正文写回动作。

## 行为 3：docx 导出预检必须依赖 approved writeback

Given 项目存在 `preview_ready` 导出包但尚未 approved writeback  
When 用户调用 docx preflight API  
Then 系统返回 409 `writeback_approval_required`

Given 用户已经 approved writeback  
When 用户调用 docx preflight API  
Then 系统写入 `state/product/docx_export_preflight.json`  
And 返回 `docx_preflight.status=ready`  
And 清单包含 `source_draft_path`、`writeback_preview_path`、`expected_docx_path`、`export_command`  
And `evidence_level=local_file`

业务规则：docx 预检只证明“导出条件齐备”，不等于实际导出。

## 行为 4：拒绝或要求修改会阻断 docx 预检

Given 用户对 writeback approval 选择 `reject` 或 `needs_revision`  
When 用户调用 docx preflight API  
Then 系统返回 409 `writeback_approval_required`  
And package 仍显示 `can_write_back=false`

业务规则：只有 approved 状态才能进入 docx 预检。

## 行为 5：Review & Export 页面是证据验收台

Given 前端加载 Review & Export 页面  
When export package 已经存在  
Then 页面必须以 `review-export-evidence-bench` 展示导出包  
And 页面必须显示 `writeback-approval-panel` 与 `docx-preflight-panel`  
And 页面必须使用 `export-evidence-table` 汇总预览、manifest、结果产物、源草稿和 docx 目标路径  
And 页面必须提供 writeback approval 与 docx preflight 操作按钮  
And 页面不得出现 `overwrite-paper-draft`

业务规则：导出页的核心不是漂亮卡片，而是让用户确认“证据、审批、预检、下一步”四件事。

