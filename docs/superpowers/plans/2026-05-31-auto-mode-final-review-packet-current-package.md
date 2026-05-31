# Auto Mode Final Review Packet Current Package Refresh

## Stage

P7-I refreshes the Auto Mode final review packet against the current CGSS paper package manifest.

User-facing effect: this node connects the reviewable package from P6-M to the final human decision point. It does not approve the paper, promote formal outputs, or write product state.

## BDD Behaviors

### Behavior 1: Builds final review packet from ready chain and package manifest

Given the five-component acceptance chain is ready for human final review
And the CGSS paper package manifest is ready for human paper package review
When P7-I runs
Then it records `awaiting_human_final_review` and allows a human final decision request.

Business rule: a reviewable package should be connected to a single final decision packet.

### Behavior 2: Blocks when acceptance chain still has repair work

Given the acceptance chain has a repair queue
When P7-I runs
Then it blocks final review and lists repair reasons.

Business rule: final review cannot start while upstream repair work is still open.

### Behavior 3: Defaults to defer without writeback

Given no explicit human approval is provided
When P7-I runs with `defer`
Then it records `waiting_for_human_final_review_decision`, keeps `approved=false`, and writes no formal state.

Business rule: continuing the workflow is not the same as approving the final package.

### Behavior 4: Approve requires reviewer and note

Given a user selects `approve`
When reviewer or note metadata is missing
Then P7-I blocks approval.

Business rule: final promotion requires attributable human judgment.

### Behavior 5: Approval only routes to preflight

Given an approved final review has reviewer and note
When P7-I routes the decision
Then it only enables formal promotion preflight, not formal writeback.

Business rule: even approval must pass the next gated stage before formal outputs are written.

### Behavior 6: Revise and reject do not promote

Given the human decision is `revise` or `reject`
When P7-I routes the decision
Then it routes to repair or stop/rebuild without promotion.

Business rule: negative decisions must keep the system out of formal delivery paths.

## Boundary Conditions

- Current packet status is `awaiting_human_final_review`.
- Current decision is `defer`.
- Current decision status is `waiting_for_human_final_review_decision`.
- Current package file count is `9`.
- Current required review item count is `12`.
- Current promotion is not allowed.
- Current formal writeback and product state writeback remain false.
