# Phase P2-Z BDD: Verifier Export Gates

## 背景

Review & Export 页面不能只因为存在正文候选、写回预览或导出包清单，就把论文包视为可导出。对实证论文系统来说，最终导出前还需要一个显式 verifier gate：逐项核验结果绑定、复现清单、方法执行产物、草稿预览、证据等级和 docx 导出预检。

这个 gate 的产品含义是：导出按钮不是“有文件就亮”，而是“核验通过才允许进入人工 docx 导出”。失败项必须在导出动作之前可见，避免用户误把候选产物当成最终论文。

## Feature: Verifier Export Gates

### Scenario 1: Export verifier requires approved manuscript candidate

Given no manuscript candidate is approved for export
When the user requests verifier checks
Then the API returns 409 `export_candidate_required`
And no verifier state file is created

业务规则：没有 `ready_for_export` 正文候选时，系统不能生成“导出可用”的核验结论。

### Scenario 2: Verifier checks result binding

Given a `ready_for_export` manuscript candidate exists
When verifier checks run
Then the `result_binding` check passes only when the candidate maps to a FindingCard and result artifact
And the check records artifact paths and evidence levels

业务规则：论文段落必须能追到结果产物和 FindingCard，不能只有自然语言正文。

### Scenario 3: Verifier checks reproducibility package artifacts

Given an export package manifest exists
When verifier checks run
Then manifest, run plan, analysis result, method execution result, and draft preview are checked
And each check has a passed or failed status and artifact path

业务规则：导出包必须是可复现对象，至少要能找到执行计划、分析结果、方法执行结果和草稿预览。

### Scenario 4: Docx export preflight remains blocked until checks pass

Given verifier checks contain failures
When the user opens Review & Export
Then docx export is disabled
And the failed checks are visible before any export action

业务规则：docx 不是普通下载按钮；它必须被核验闸门控制，失败时显示阻断原因。

### Scenario 5: Frontend exposes verifier gates before export actions

Given Review & Export is opened
When verifier checks are loaded
Then the verifier gate panel appears before export package actions
And the docx final export action is disabled unless `can_export_docx=true`

业务规则：用户先看到核验结果，再看到导出动作，降低误操作风险。
