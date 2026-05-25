# P3 React Workbench Design Contract

Status: accepted direction, implementation contract
Date: 2026-05-25
Scope: new `Product/web-react` surfaces only. Legacy `Product/web` remains as fallback until replaced.

## 1. Product Shape

The product is not a normal SaaS landing page. It is a local-first empirical research OS for a researcher who wants to move from a topic to evidence-bound research outputs.

The first screen must feel like a quiet command surface:

- User starts by entering a research topic, data clue, literature clue, or next task.
- The system then creates a draft research session.
- The workbench unfolds only after a concrete topic or task exists.
- Main screen should not show every capability at once.

Design principle:

> 主屏只承载当前决策。详情不占主屏。复杂证据进入右侧 Drawer、底部日志或按需展开区域。

## 2. Visual Language

The baseline visual language is the current React entry:

- 黑白灰 only.
- 低对比 graphite palette, roughly closer to 76% perceived contrast than pure black and white.
- DottedSurface as the first-screen environmental background.
- No color-coded status system in the first version.
- 不使用彩色状态色；status is expressed through opacity, weight, border, motion, and placement.
- No decorative gradient balls, generic cards, marketing hero, or product claim sections.
- 不做普通 SaaS landing page.

Forbidden visible language:

- 禁止防守性文案，例如“当前只是验证切片”“不展开 Agent”“不会静默改写正式状态”。
- Do not explain implementation limitations in the first viewport.
- Do not use long safety disclaimers on the start screen.
- Safety boundaries are shown only at review, approval, dispatch, and formal writeback moments.

## 3. Shell Model

The React workbench should use four stable regions:

1. **Main Workspace**
   - User's current decision.
   - One dominant action at a time.
   - Examples: 输入题目, 生成任务书, 确认变量角色, 审阅方法前提, 启动实验.

2. **Stage Navigation**
   - Compact sliding tabs.
   - Shows the research path without becoming a large sidebar.
   - Labels stay short: 任务书, 递归搜索, 数据变量, 方法设计, 执行实验, 结果解释, 论文草稿, 复现导出.

3. **Right Drawer**
   - Evidence, logs, provenance, method notes, artifact previews, agent audit.
   - 右侧 Drawer opens from a selected object.
   - Details do not live permanently on the main screen.

4. **Bottom / Inline Disclosures**
   - Small status summaries.
   - `details/summary` or compact disclosure controls for secondary information.
   - 默认只显示 what the user needs to decide.
   - 按需展开 raw evidence, logs, JSON, tool calls, or assumptions.

## 4. Universal Interaction Rules

Every module follows these interaction rules:

- 默认只显示 the 3-5 signals needed for the next human decision.
- 按需展开 evidence, raw logs, full reasoning, and debug details.
- 右侧 Drawer contains object details; it must be dismissible.
- 主屏只承载当前决策.
- 详情不占主屏.
- Formal state changes require explicit review.
- 正式层写回必须显式确认.
- Draft/exploratory outputs may be generated automatically, but formal promotion must show source, evidence level, risk, and review action.

Allowed action vocabulary:

- 创建
- 生成
- 审阅
- 确认
- 要求修改
- 驳回
- 启动
- 暂停
- 导出预检

Avoid vague action copy:

- “查看详情” as the only action when the real action is review, approve, or run.
- “继续” without stating what will be continued.
- “智能生成” without showing what object will be created.

## 5. Module Contracts

### 5.1 研究入口

Purpose:

Start a research session without overwhelming the user.

Main screen:

- DottedSurface background.
- Large research input.
- Attachment and mode controls.
- Compact stage navigation.

Default visible signals:

- Current input.
- Selected mode.
- Whether files or pasted text are attached.
- One primary submit action.

Hidden until needed:

- Formal writeback policy.
- Provider logs.
- Agent queue.
- Evidence raw files.

Primary interactions:

- 输入题目.
- Attach data or literature snippets.
- Choose local / auto / semi-auto mode.
- 生成任务书.

Formal boundary:

This module creates a draft session only. It does not promote variables, method design, run plan, findings, or manuscript sections.

### 5.2 任务队列

Purpose:

Turn an approved SupervisorPlan or topic session into actionable work.

Main screen:

- Queue summary.
- Next task.
- Blocked count.
- Owner agent.
- Human review gate.

Default visible signals:

- Task title.
- Owner.
- Status.
- Blocking reason if any.
- Next allowed action.

Right Drawer:

- Full task input.
- Expected output.
- Evidence requirements.
- Tool permissions.
- Audit trail.

Primary interactions:

- 创建任务队列.
- Assign or reassign owner.
- Approve task start.
- Pause task.
- Request revision.

Formal boundary:

Creating the queue does not execute subagents automatically unless the task is explicitly approved for execution.

### 5.3 递归搜索

Purpose:

Support the loop:

用户给题目 -> 系统发现相关变量 -> 变量指向可用数据 -> 数据指向可行方法 -> 方法暴露缺失证据 -> 缺失证据触发新搜索 -> 新文献/新变量/新数据再进入下一轮.

Main screen:

- Current search frontier.
- Search depth and iteration.
- Evidence gaps.
- Candidate next searches.

Default visible signals:

- Current query or seed.
- Source type.
- Evidence level.
- Confidence.
- Whether it can support formal research.

Right Drawer:

- Source excerpts.
- URL / DOI / CNKI metadata.
- Zotero match.
- Relevance reason.
- Rejection reason.

Primary interactions:

- 查看搜索证据.
- Add source to draft evidence.
- Reject source.
- Trigger next recursive search.

Formal boundary:

Search output is exploratory until reviewed. It cannot become a formal citation or research claim by itself.

### 5.4 数据与变量

Purpose:

Move from real data assets to auditable variable roles.

Main screen:

- Candidate datasets.
- Variable role candidates.
- Data quality summary.
- Missingness and sample scope.

Default visible signals:

- Dataset name.
- Row / column count.
- Evidence level.
- Candidate outcome / treatment / controls / instruments.
- Needs-review status.

Right Drawer:

- Raw field profile.
- Value distribution.
- Missingness table.
- Source file path.
- Import or profiling log.

Primary interactions:

- Bind dataset.
- Profile fields.
- 确认变量角色.
- Request new profiling.
- Promote candidate to reviewed role.

Formal boundary:

Auto Mode can suggest variables, but formal variable roles must be reviewed and explicitly promoted.

### 5.5 方法设计

Purpose:

Convert a research question and variable roles into an empirical design.

Main screen:

- Method family.
- Identification strategy.
- Required assumptions.
- Missing evidence.
- Recommended robustness checks.

Default visible signals:

- Method candidate.
- Why it fits the data.
- Key assumption.
- Blocking condition.
- Review status.

Right Drawer:

- Expert methodology notes.
- StatsPAI function schema.
- Method preconditions.
- Alternative method comparison.
- Literature-backed method references.

Primary interactions:

- 审阅方法前提.
- Approve method candidate.
- Request method patch.
- Compare method families.
- Create RunPlan draft.

Formal boundary:

Auto Mode may write methodology patch proposals, but canonical expert methodology library changes require human review before merge.

### 5.6 执行实验

Purpose:

Run empirical work with observable execution.

Main screen:

- Current run.
- Run status.
- Next executable step.
- Evaluation status.
- Artifact count.

Default visible signals:

- Run id.
- Backend: Python / StatsPAI / StataMCP / Stata / R.
- Status.
- Duration.
- Failed or blocked step.

Right Drawer:

- Logs.
- Tool calls.
- Parameters.
- Metrics.
- Generated artifacts.
- Repro command.

Primary interactions:

- 启动实验.
- Pause run.
- Retry failed step.
- Compare runs.
- Open artifact.

Formal boundary:

Execution can create local_execution evidence, but results remain draft until evaluator checks and human review pass.

### 5.7 结果解释

Purpose:

Separate statistical output from research claims.

Main screen:

- Finding candidates.
- Claim strength.
- Evidence bindings.
- Contradictions.
- Reviewer score.

Default visible signals:

- Claim sentence.
- Bound run.
- Coefficient direction.
- Robustness status.
- Needs-review flag.

Right Drawer:

- Regression table source.
- Figure source.
- Model spec.
- Sensitivity checks.
- Reviewer comments.

Primary interactions:

- 审阅 finding.
- Accept as draft claim.
- Request robustness.
- Reject finding.
- Send to manuscript.

Formal boundary:

No finding can become a manuscript claim without evidence binding and human review.

### 5.8 论文草稿

Purpose:

Write with provenance, not free-floating text.

Main screen:

- Manuscript outline.
- Current section.
- Draft status.
- Evidence bindings.

Default visible signals:

- Section title.
- Draft status.
- Bound findings.
- Missing citations.
- Export readiness.

Right Drawer:

- Evidence binder.
- Citation verification.
- Change history.
- Comments.
- Reviewer notes.

Primary interactions:

- Generate draft section.
- Edit section.
- 绑定证据.
- Request rewrite.
- Approve section draft.

Formal boundary:

Auto Mode can write exploratory paper draft and research report. Formal manuscript layer requires review, citation verification, and export precheck.

### 5.9 复现导出

Purpose:

Make the project reproducible and exportable.

Main screen:

- Export package status.
- Required files.
- Reproducibility gates.
- DOCX / LaTeX / Markdown readiness.

Default visible signals:

- Gate status.
- Missing artifact count.
- Evidence coverage.
- Export format readiness.

Right Drawer:

- Manifest.
- File provenance.
- Failed gate details.
- Export logs.

Primary interactions:

- 导出预检.
- Fix missing artifact.
- Create reproducibility package.
- Export docx.
- Export latex.

Formal boundary:

Export is blocked when required evidence, citations, code, or run artifacts are missing.

### 5.10 Agent 审计

Purpose:

Show what agents did without making chat the main product.

Main screen:

- Agent roster.
- Active task.
- Cost summary.
- Intervention inbox.

Default visible signals:

- Agent name.
- Current task.
- Permission scope.
- Cost.
- Human action needed.

Right Drawer:

- Tool call timeline.
- Prompt summary.
- Inputs and outputs.
- Errors.
- Audit log.

Primary interactions:

- Open audit.
- Approve tool use.
- Pause agent.
- Require revision.
- Promote reviewed output.

Formal boundary:

Agent output is draft unless promoted through the relevant module's review flow.

## 6. State Display Rules

Use these status labels across modules:

- empty
- draft
- exploratory
- running
- blocked
- needs_human_review
- approved
- rejected
- exported

Display rules:

- `exploratory` means useful but not paper-ready.
- `draft` means editable, not formal.
- `needs_human_review` means the user must decide.
- `approved` means usable by the next workflow step.
- `exported` means included in the reproducibility package.

Evidence badges:

- mock
- local_file
- local_execution
- external_source
- verified_citation
- human_reviewed

## 7. Implementation Sequence

Implement modules in this order:

1. Research entry -> draft topic session.
2. Right Drawer foundation.
3. Task queue.
4. Recursive search.
5. Data and variable review.
6. Method design review.
7. Execution run surface.
8. Finding review.
9. Manuscript evidence binder.
10. Export precheck.
11. Agent audit.

Reason:

The user must first feel the product is calm and directional. Concrete work should enter through one task, then unfold through reviewable objects.

## 8. Acceptance Checklist

Before implementing any module:

- Does the main screen show only the current decision?
- Are raw details moved to the Right Drawer or disclosure?
- Is there a single primary action?
- Is formal writeback explicitly confirmed?
- Are evidence level and status visible?
- Is there any defensive or implementation-limit copy on the main screen?
- Does the UI remain black/white/gray and low contrast?
- Does it avoid normal SaaS landing page patterns?

If any answer fails, redesign before implementation.
