# P1-L Manuscript Candidate Review BDD

## 背景

P1-K 已经让 Manuscript 阶段只从 `review_status=approved` 且 `can_write_to_draft=true` 的 FindingCard 生成正文候选。候选段落仍然不是最终正文，必须再经过用户审阅，才能进入后续 promote/write-back/export。

## 行为 1：候选段落默认需要人工审阅

Given 已存在 approved FindingCard
When 用户读取 Manuscript candidates
Then 每个 candidate 的 `review_status` 应为 `needs_review`
And `can_promote` 应为 `false`
And 系统不得修改 `Manuscripts/generated/paper_draft.md`

业务规则：统计论断 approved 不等于文字表述 approved。

## 行为 2：用户 approve candidate 后允许进入后续 promote

Given 已存在 Manuscript candidate
When 用户提交 `approve` 和审阅备注
Then 系统应把 candidate review 保存到 `state/product/manuscript_candidate_reviews.json`
And 再次读取 candidate 时 `review_status=approved`
And `can_promote=true`
And provenance 应包含 `candidate_review`，证据等级为 `local_file`

业务规则：正文候选必须有独立文字审阅证据。

## 行为 3：用户 reject / needs_revision 后不能 promote

Given 已存在 Manuscript candidate
When 用户提交 `reject` 或 `needs_revision`
Then 再次读取 candidate 时 `can_promote=false`
And `review_status` 应反映用户决定

业务规则：不合格段落不能进入正文写回或导出。

## 行为 4：非法 candidate 或非法 action 必须被拒绝

Given 用户提交不存在的 candidate id 或未知 action
When 系统处理 review 请求
Then 应返回结构化错误
And 不应写入无效 review 状态

业务规则：审阅状态不能被前端任意字符串污染。

## 行为 5：前端必须显示 candidate review 操作

Given Results & Draft 页面显示 Manuscript candidates
When 用户查看 candidate 卡片
Then 页面应显示 `review_status`、`can-promote`、审阅备注输入框
And 提供 approve / needs_revision / reject 三个操作
And 操作成功后刷新 candidates

业务规则：用户必须在同一个研究对象上完成段落审阅，而不是跳到隐藏 API。

## 边界

- 本阶段不实现真正写回 `paper_draft.md`。
- 本阶段不导出 docx。
- 本阶段不调用 LLM 改写段落。
- 本阶段只新增 candidate review 状态，不改变 FindingCard review 语义。
