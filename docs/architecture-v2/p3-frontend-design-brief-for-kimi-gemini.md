# P3 Frontend Design Brief for Kimi / Gemini

Date: 2026-05-25
Project: Local Empirical Research OS
Repo: `/Users/mahaoxuan/Desktop/经济学论文/实证论文项目模板`

## Your Role

You are responsible for high-fidelity frontend design and interaction polish.

Codex is responsible for:

- product state machine,
- API and backend wiring,
- tests,
- data contract,
- persistence,
- audit / evidence boundaries.

Do not treat the existing React demo visual style as final. It is only a low-fidelity behavior slice.

## Product We Are Building

This is not a normal SaaS landing page. It is a local-first empirical research OS.

The target user starts with a research topic, attaches local data / literature / method hints, then lets an LLM Supervisor produce a staged research plan. The system gradually moves through:

1. topic intake,
2. task brief confirmation,
3. SupervisorPlan generation,
4. recursive research search,
5. data and variable discovery,
6. method design,
7. execution experiment,
8. findings review,
9. manuscript draft,
10. export and reproducibility review.

The first version is mainly for the user and a few familiar researchers. It should feel powerful, serious, local, and research-native.

The product should not be designed as two different experiences for local and cloud. Design one coherent flow. The local version is the first implementation environment; the cloud version should reuse the same journey and state machine later.

## Visual Direction

The user strongly prefers:

- black / white / gray,
- clean and low-noise,
- futuristic but not flashy,
- low contrast compared with pure black-white,
- strong blank space,
- compact but not cramped,
- high-end research tool rather than SaaS dashboard.

Avoid:

- colorful SaaS gradients,
- purple / blue product look,
- marketing hero sections,
- decorative cards without information value,
- defensive copy explaining what the demo cannot do,
- long instruction text on the first screen,
- raw JSON / logs / implementation details in the main canvas.

## Existing User-Approved UI Direction

The user likes:

- a Claude-style dark input surface,
- attachment cards,
- pasted content previews,
- model selector,
- compact send button,
- sliding pill-style stage navigation,
- subtle dotted / particle-like background,
- semantic cards only after entering the analysis stage,
- black-white-gray as the default color system.

You may redesign the high-fidelity page, but preserve these interaction principles.

## Core Interaction Path

### 1. Intake Screen

Purpose: collect user intent.

The intake screen should show only:

- one strong question headline,
- one large research command input,
- attach button,
- settings / mode button,
- model / supervisor selector,
- send button.

Do not show:

- analysis cards,
- Agent queue,
- logs,
- evidence panels,
- method tables,
- dataset registries,
- dashboard widgets.

### 2. Task Brief Page

After the user submits a topic, the first page is not analysis cards. It is a task brief checkpoint.

Main canvas shows five decision signals:

- research topic,
- research boundary,
- data clue,
- method inclination,
- next step.

Right Inspector:

- desktop: fixed right inspector,
- mobile: drawer,
- default sections: evidence requirements, risks, formal layer boundary, dispatch notes.

Confirmed interaction:

- clicking a main signal highlights the corresponding Inspector item,
- main signal cards do not expand into long detail blocks,
- high-noise details stay in Inspector / drawer.

### 3. After Task Brief Confirmation

Confirmed product decision:

After the user confirms the task brief, the next stage is `SupervisorPlan` generation.

The Supervisor decides whether the research should proceed:

- literature-first,
- data-first,
- method-first,
- execution-precheck-first.

Do not jump directly to recursive search or variable discovery before this SupervisorPlan step.

### 4. SupervisorPlan Review

The confirmed design direction is:

- show a single total plan summary first,
- place a multi-stage task tree below it,
- collapse stage details by default,
- expand details only when the user asks,
- keep risks / assumptions / evidence requirements in the Inspector.

Do not make the first view a giant workflow graph. The user should first judge whether the route is reasonable, then inspect the task tree.

## Required Modules to Design

Design the interface system for these modules, but do not make them all visible at once:

1. Intake.
2. Task Brief.
3. SupervisorPlan Review.
4. Recursive Research Search.
5. Data and Variables.
6. Method Design.
7. Execution Experiment.
8. Findings Review.
9. Manuscript Draft.
10. Export / Reproducibility Review.
11. Agent / Audit Console.

Each module needs:

- default state,
- loading state,
- empty state,
- error state,
- selected / focused state,
- evidence / provenance access,
- human review action if it can affect formal research state.

## Draft vs Formal Boundary

This is critical.

Auto Mode may generate draft / exploratory outputs. It cannot silently overwrite formal research state.

Draft layer examples:

- topic draft,
- variable candidate,
- method candidate,
- exploratory finding,
- manuscript draft paragraph.

Formal layer examples:

- confirmed ResearchQuestion,
- approved VariableRoleSet,
- approved DesignSpec,
- approved RunPlan,
- approved Finding,
- export-ready Manuscript.

Any transition from draft to formal requires a visible human review action.

## Data and Evidence Language

Evidence levels must be visible when relevant:

- `mock`,
- `local_file`,
- `local_execution`,
- `external_source`,
- `unknown`.

But do not flood the main canvas with badges. Prefer:

- subtle status marks on the main item,
- detailed evidence in Inspector,
- provenance drawer for deep inspection.

## Technical Constraints

Current frontend path:

- `Product/web-react/src/`

Current preview route:

- `/react`

Useful existing files:

- `Product/web-react/src/App.tsx`
- `Product/web-react/src/components/ResearchCommandInput.tsx`
- `Product/web-react/src/components/SlideTabs.tsx`
- `Product/web-react/src/components/TaskBriefDemo.tsx`
- `Product/web-react/src/components/SemanticGlowCards.tsx`
- `Product/web-react/src/styles.css`

Codex will later connect the design to:

- `TopicSession`,
- `ResearchQuestionDraft`,
- `SupervisorPlanDraft`,
- Agent Task Queue,
- Evidence registry,
- audit events.

## Deliverable Expected From You

Please produce a high-fidelity frontend design plan, not only a pretty screenshot.

Output should include:

1. information architecture,
2. route / module map,
3. component hierarchy,
4. main layouts for desktop and mobile,
5. interaction states,
6. motion principles,
7. what should be hidden by default,
8. what should be visible on the main canvas,
9. Inspector / drawer behavior,
10. handoff notes for Codex API wiring.

If you produce code, keep it scoped to frontend presentation components and avoid changing backend state semantics.

## Acceptance Standard

The result is good only if:

- the first screen feels calm and focused,
- the user knows what to do next,
- the screen is not crowded,
- evidence and risk are accessible but not overwhelming,
- the system feels like a research OS, not a generic SaaS dashboard,
- every visual element carries product meaning,
- Codex can later wire real data into the component structure without redesigning everything.
