# P3 Task Brief Guided Action Review

Date: 2026-05-25
Scope: `Product/web-react` task brief page after topic submission
Reviewer: Codex

## Current Finding

The current Task Brief page has a correct state boundary, but it fails as a guided product surface.

The user has already submitted a research topic, but the next screen still reads like a component demo:

- It tells the user that the main screen has five decision signals.
- It tells the user to click signal cards and inspect the right panel.
- It exposes terms such as `Task Brief`, `Inspector`, and `SupervisorPlan` as primary copy.
- It presents five cards with similar visual weight, but does not make one primary decision obvious.

This makes the user ask: "What am I supposed to do here?"

The problem is not only visual quality. The problem is that the page does not stage the user's decision.

## Product Rule

After topic submission, the Task Brief page must behave like a guided checkpoint, not like a dashboard.

The page should answer, in order:

1. What did I just ask the system to study?
2. What is still missing before analysis can start?
3. What does the system recommend doing next?
4. What exactly happens if I confirm?
5. Where can I inspect risks and evidence requirements if I want to?

## Required Information Architecture

### Main Canvas

The main canvas should show one guided decision, not five equally weighted dashboard cards.

Recommended structure:

1. **Primary decision header**
   - Example: `先补齐研究边界，再生成执行计划`
   - This should be written as a next action, not as a system explanation.

2. **Research question preview**
   - Show the submitted topic as a quote / compact object.
   - Do not let it dominate the page as another giant title if the global header already shows it.

3. **Missing inputs checklist**
   - Data source: not bound / detected from attachment / detected from text.
   - Sample and period: unknown / detected.
   - Method route: candidate only.
   - Formal writeback: locked until human review.

4. **Recommended next step**
   - Example: `生成 Supervisor 研究计划`
   - Explain the result in one short line: `系统会拆出文献、数据、变量、方法和执行预检任务，不会直接跑回归。`

5. **Primary action**
   - Button text should be user-facing Chinese:
     - Good: `生成研究计划`
     - Acceptable: `确认并生成研究计划`
     - Avoid: `确认任务书并生成 SupervisorPlan`

### Right Inspector

The right Inspector should stay, but it should not be the main instruction mechanism.

Default sections:

- `为什么需要确认`
- `缺少哪些证据`
- `可能的研究风险`
- `确认后会发生什么`

The Inspector should explain optional detail after the user has a clear main action.

### Stage Navigation

The stage navigation can stay visible, but it should not imply the user can freely jump into downstream analysis before the current gate is complete.

Required behavior:

- Downstream tabs may be visible but visually disabled or marked `待解锁`.
- If clicked early, show a compact reason: `先生成研究计划后再进入该阶段。`
- Do not silently show generic semantic cards when a stage is not actually ready.

## Copy Rules

Avoid internal or defensive language on the main canvas:

- Avoid: `主屏显示当前必须确认的五个决策信号`
- Avoid: `点击信号卡片可在右侧 Inspector 聚焦查看详情`
- Avoid: `草案层判断`
- Avoid: `候选，不写回`
- Avoid: `SupervisorPlan` as a primary button label

Use product/action language:

- `当前缺少数据、样本和时间范围`
- `方法只是初步线索，不能进入论文结论`
- `确认后，系统只生成研究计划和任务队列`
- `真实数据执行会在下一道人工确认前暂停`

## Interaction Contract

The user path should be:

1. User enters topic.
2. Task Brief shows one recommended next action.
3. User can optionally inspect evidence/risk details on the right.
4. User clicks `生成研究计划`.
5. System moves to SupervisorPlan Review.

The page should not require the user to understand the internal data model before taking the next action.

## Acceptance Criteria

The redesign is acceptable only if a first-time user can answer these questions within 5 seconds:

- I am confirming the research question and missing boundary information.
- The system is not yet running regression.
- The next click generates a research plan, not final analysis.
- Risks and evidence requirements are available, but not forced into the main reading path.

## Suggested BDD

### Behavior 1: The page presents one primary next action

Given a user submits a research topic without data files
When the Task Brief page opens
Then the main canvas should show a single recommended next action
And the primary button should use product language such as `生成研究计划`
And the page should not require reading the Inspector to know what to do.

### Behavior 2: Missing inputs are visible before planning

Given the topic has no attached data
When the Task Brief page opens
Then the page should show data source, sample/period, and method route as missing or candidate status
And these statuses should be readable as a checklist.

### Behavior 3: Internal implementation terms are not primary copy

Given the Task Brief page is visible
When the user scans the main canvas
Then copy such as `Inspector`, `Task Brief`, `SupervisorPlan`, `草案层判断`, and `候选，不写回` should not be required to understand the page.

### Behavior 4: Downstream stages are gated

Given the Task Brief is not confirmed
When the user tries to open recursive search, data variables, method design, or execution
Then the UI should explain that the research plan must be generated first
And it should not show unrelated analysis cards as if the stage were ready.

## Handoff To Gemini / Kimi

Redesign this page at the product-interaction level. Do not only polish card shadows, spacing, or contrast.

Keep:

- monochrome visual system,
- low contrast,
- large calm input-to-workbench transition,
- right Inspector as secondary detail,
- formal layer safety boundary.

Change:

- convert the page from a "five equal signal cards" dashboard into a guided checkpoint,
- make the next action obvious,
- hide implementation words from the main canvas,
- turn missing data/sample/method evidence into a readable checklist,
- make downstream tabs feel gated until the plan is generated.

Do not change backend semantics. Do not pretend real execution has started.
