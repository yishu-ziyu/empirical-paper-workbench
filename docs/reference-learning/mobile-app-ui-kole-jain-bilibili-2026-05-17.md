# Mobile App UI Reference Learning

Date: 2026-05-17

Sources:

- Bilibili: `https://www.bilibili.com/video/BV16BRQBSEVy/`
- Kole Jain resources: `https://www.kolejain.com/resources?scrollTo=mobile-app-ui`
- YouTube watch link from Kole Jain resource metadata: `https://youtu.be/Gfsd8NNuD9g`
- Figma reference link from Kole Jain resource metadata: `https://www.figma.com/design/WwEtNcIqpDNxYZx4ZpiE7m/Mobile-App-UI?node-id=0-1&t=YZJpSU3Hd5nKhoud-1`

Local-only downloads:

- `artifacts/reference-learning/bilibili-bv16brqbsevy/`
- `artifacts/reference-learning/kolejain-resources/`

## What Was Downloaded

- Bilibili video: `BV16BRQBSEVy-8分钟带你了解移动应用UI的一切（新手友好）.mp4`
- Bilibili metadata: `metadata.json`, `.info.json`, thumbnail
- Extracted audio: `audio.wav`
- Local transcript: `transcript.txt`, `transcript.srt`, `transcript.json`
- Kole Jain resource HTML and parsed resource manifest
- Mobile App UI `.fig` file and five preview images
- Mobile App UI contact sheet: `mobile-app-ui-contact-sheet.png`

## Source Structure

The Bilibili video is an 8-minute beginner-friendly breakdown of mobile app UI. Its own timeline is:

- 0:00 opening
- 0:20 navigation
- 1:32 scale
- 2:13 content
- 3:30 one page, one task
- 5:11 gestures
- 6:02 motion
- 6:27 empty states

The Kole Jain resources page is not just a video page. It is a structured resource shelf with 19 downloadable Figma resources. The `mobile-app-ui` entry includes:

- title: `Mobile App UI`
- slug: `mobile-app-ui`
- watch link: `https://youtu.be/Gfsd8NNuD9g`
- Figma link: `Mobile-App-UI`
- download: `/images/uploads/Mobile App UI.fig`
- five preview screens

## Product Lessons For Our Empirical Workbench

### 1. Do Not Compress More Into Smaller Space

The video makes a clear point: on smaller screens, text and touch targets often need to be larger, not smaller. The equivalent for our product is that we should not solve density by reducing font size or squeezing cards. We need fewer visible decisions per screen.

Applied rule:

- Default screens show only the next 1-3 decisions.
- Evidence, logs, JSON, model prompts, and provenance stay behind expanders, drawers, or inspector panels.
- Dense content appears only after the user chooses the object they want to inspect.

### 2. One Surface, One Primary Task

The strongest transferable rule is "one page, one task." Our previous UI failed when a page tried to be dashboard, file browser, execution log, agent console, and report viewer at the same time.

Applied rule:

- Overview: choose or resume a research topic.
- Data: choose/bind/profile a dataset.
- Variables: confirm variable roles.
- Design: confirm identification and model specification.
- Execution: launch and inspect runs.
- Findings: review claims.
- Manuscript: promote approved text.
- Review & Export: verify reproducibility package.
- Agents: inspect agent plans, tasks, tools, costs, and gates.

### 3. Navigation Should Be Contextual

The video contrasts desktop sidebars with mobile bottom navigation and context-specific actions. For our product, this does not mean blindly copying mobile bottom tabs. It means the main action should change with the current research object.

Applied rule:

- When no topic exists, primary action is "确认研究选题".
- When topic exists but no SupervisorPlan exists, primary action is "生成 SupervisorPlan".
- When a plan exists but is not approved, primary actions are "批准计划 / 要求修改 / 驳回计划".
- When a plan is approved, primary action becomes "创建 Agent 任务队列".
- When a run finishes, primary action becomes "审阅 Finding / 生成正文候选".

### 4. Touch Target Lesson Becomes Click Target And Cognitive Target

The video recommends at least 44px touch areas. In our desktop workbench, the analogous constraint is not only physical clicking but cognitive clicking: buttons must be visually separable, action labels must be concrete, and the page must not present too many equal-weight actions.

Applied rule:

- Primary action: one dominant button.
- Secondary actions: text or outline buttons grouped near the object they affect.
- Dangerous or blocking actions: explicit wording and visible state change.

### 5. Gestures Translate To Drawers And Object-Scoped Panels

Mobile gestures like swipe back, bottom sheets, and long press are ways to keep the main screen clean while making detail accessible. For our web product, the equivalent is:

- Right inspector for selected object metadata.
- Bottom drawer for logs and tool calls.
- Inline details for evidence requirements and JSON snippets.
- Object-scoped action panels instead of a global chat-first interface.

### 6. Empty States Need A Real Next Action

The video emphasizes that empty states should not only say "nothing here"; they should explain what is missing and offer a next step.

Applied rule:

- No ResearchQuestion: show topic input and examples.
- No SupervisorPlan: show why plan is missing and a generate button.
- No approved plan: show review actions, not task queue.
- No run: show required prerequisites.
- No findings: show which run or evaluator is needed.
- No export package: show which manuscript candidate must be approved first.

### 7. Motion Should Clarify State, Not Decorate

The video discusses dynamic transitions and gesture feedback. For our product, motion should be restrained and functional:

- Expand/collapse details smoothly.
- Highlight state changes after approvals.
- Keep long logs and provenance in drawers.
- Avoid decorative animation that competes with research evidence.

## Concrete Next Product Moves

1. P2-U Agent Task Queue should follow the "one task per surface" rule:
   - Queue list summary first.
   - Selected task detail in inspector.
   - Logs behind drawer.
   - One primary action based on status.

2. Data and Variables should split:
   - Dataset selection/binding is one task.
   - Variable role confirmation is another task.
   - Do not show all field metadata until a dataset or variable is selected.

3. Review & Export should become an empty-state-driven validation surface:
   - If no package exists, show prerequisites.
   - If package exists, show only pass/fail gates first.
   - Detailed manifest, logs, files, and provenance are expanders.

4. Mobile/narrow viewport should not attempt to preserve the desktop workbench:
   - Collapse sidebar.
   - Hide inspector by default.
   - Use object-focused single-column pages.
   - Keep one dominant action visible.

## Design Boundary

Kole Jain's resource is useful for interaction principles and density control. We should not copy its dark visual style, app content, exact screens, text, brand, or Figma structure. Our product should remain a clean empirical research workbench: evidence-first, restrained, object-scoped, and auditable.
