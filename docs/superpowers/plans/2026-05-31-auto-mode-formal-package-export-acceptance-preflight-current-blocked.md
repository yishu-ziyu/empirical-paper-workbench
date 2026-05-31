# Auto Mode Formal Package Export / Acceptance Preflight Current Blocked Record

## Stage

P7-X is the formal package export / acceptance preflight after P7-W.

User-facing effect: this node tells downstream components whether the verified formal package can move to explicit PDF export, DOCX export, package manifest generation, or manual acceptance. In the current run, P7-W is blocked and has no formal target verification records, so P7-X records a blocked preflight and does not export or accept anything.

## BDD Behaviors

### Behavior 1: Verified package creates export and acceptance plan

Given P7-W verified the promoted formal package
And formal target records are complete
When P7-X runs
Then it creates four pending plan items for PDF export, DOCX export, package manifest generation, and manual acceptance.

Business rule: export and acceptance start from a verified formal package only.

### Behavior 2: Blocked P7-W blocks export and acceptance preflight

Given P7-W is blocked
When P7-X runs
Then it reports `blocked_by_promoted_package_verification`
And creates no export acceptance plan.

Business rule: export cannot bypass formal package verification.

### Behavior 3: Missing, invalid, or unverified P7-W report blocks preflight

Given the P7-W report is missing, has the wrong schema, or is not verified
When P7-X runs
Then it blocks export and acceptance preflight.

Business rule: downstream commands need verified evidence, not a partial report.

### Behavior 4: Bad formal target records block preflight

Given P7-W claims the package is verified
When formal target records are missing, unverified, or outside `Submissions/formal_package/`
Then P7-X blocks preflight.

Business rule: export and acceptance require complete formal package target records.

### Behavior 5: Boundary violations block preflight

Given P7-W reports product, render, or model side effects
When P7-X runs
Then it blocks preflight.

Business rule: read-only verification must stay separate from export, render, and product state writes.

### Behavior 6: P7-X writes report and review only

Given P7-X runs in any state
When outputs are written
Then it writes preflight JSON and Markdown review only
And does not export PDF, DOCX, or product state.

Business rule: this node plans export or acceptance; it does not execute them.

## Current Run Boundary

- Current status: `blocked_by_promoted_package_verification`.
- Source P7-W status: `blocked_by_candidate_promotion_execute`.
- Source P7-W formal package verified: `false`.
- Source P7-W promoted formal targets verified: `false`.
- Source P7-W formal target record count: `0`.
- Formal package summary target count: `0`.
- Can enter formal package export acceptance: `false`.
- Requires explicit export or acceptance command: `false`.
- Export acceptance plan count: `0`.
- Export or acceptance executed: `false`.
- Rendered PDF: `false`.
- Rendered DOCX: `false`.
- This command wrote formal state: `false`.
- Product state writeback allowed: `false`.
- Existing `Submissions/formal_package/paper.pdf` and `Submissions/formal_package/paper.docx` are old files and were not modified by this run.
- Blocking reasons: `promoted_formal_package_verification_not_ready`, `formal_package_not_verified`, `promoted_formal_targets_not_verified`, `candidate_targets_not_promoted`, `source_formal_writeback_not_executed`.
