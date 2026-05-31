# Auto Mode Formal Package Export / Acceptance Router Current Blocked Record

## Stage

P7-Y is the formal package export / acceptance router after P7-X.

User-facing effect: this node records an explicit human route choice for PDF export, DOCX export, package manifest generation, or manual acceptance. In the current run, P7-X is blocked and has no export acceptance plan, so P7-Y records a blocked router report and does not select any route.

## BDD Behaviors

### Behavior 1: Ready defer waits without route

Given P7-X is ready
When the user chooses `defer`
Then P7-Y waits without recording a route.

Business rule: a ready package can still wait for human route choice.

### Behavior 2: Confirmed PDF route records route without export

Given P7-X is ready
And the route request is confirmed with reviewer and note
When the user chooses `pdf_export`
Then P7-Y records `formal_pdf_export_preflight`
And does not export a PDF.

Business rule: routing is not execution.

### Behavior 3: Blocked P7-X blocks route recording

Given P7-X is blocked
When P7-Y runs
Then it reports `blocked_by_export_acceptance_preflight`
And records no route.

Business rule: route selection cannot bypass export acceptance preflight.

### Behavior 4: Unknown or missing plan actions block route

Given P7-X is ready
When the decision is unknown or not present in the P7-X plan
Then P7-Y blocks route recording.

Business rule: only planned export or acceptance actions can be routed.

### Behavior 5: Non-defer routes require confirmation and metadata

Given P7-X is ready
When a non-defer route lacks confirmation, reviewer, or note
Then P7-Y blocks route recording.

Business rule: export and acceptance routing must be explicit and attributable.

### Behavior 6: Boundary violations block router

Given P7-X reports export, render, formal write, or product state side effects
When P7-Y runs
Then it blocks route recording.

Business rule: P7-X must remain a clean preflight before route selection.

### Behavior 7: P7-Y writes report and review only

Given P7-Y runs in any state
When outputs are written
Then it writes router JSON and Markdown review only
And does not export, accept, or write product state.

Business rule: this node selects a route; it does not execute it.

## Current Run Boundary

- Current status: `blocked_by_export_acceptance_preflight`.
- Decision: `defer`.
- Source P7-X status: `blocked_by_promoted_package_verification`.
- Source P7-X can enter export acceptance: `false`.
- Source P7-X export acceptance plan count: `0`.
- Can route export or acceptance: `false`.
- Route recorded: `false`.
- Routed action: empty.
- Export or acceptance executed: `false`.
- Rendered PDF: `false`.
- Rendered DOCX: `false`.
- This command wrote formal state: `false`.
- Product state writeback allowed: `false`.
- Existing `Submissions/formal_package/paper.pdf`, `Submissions/formal_package/paper.docx`, and `Submissions/formal_package/manifest.json` are old files and were not modified by this run.
- Blocking reasons: `export_acceptance_preflight_not_ready`, `export_acceptance_preflight_cannot_enter`, `export_acceptance_preflight_missing_explicit_command_requirement`.
