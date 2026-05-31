# Auto Mode Formal Promotion Preflight Current Defer Record

## Stage

P7-J checks whether the P7-I final review decision can enter formal writeback approval.

User-facing effect: this node converts the final review decision into a clear go/no-go result for formal promotion. In the current run, it correctly blocks promotion because the final review decision is still `defer`.

## BDD Behaviors

### Behavior 1: Approved final review only enables a later writeback approval request

Given the final review decision is `approve`
And reviewer and note metadata are present
When P7-J runs
Then it reports `ready_for_formal_writeback_approval`
And still keeps formal writeback disabled.

Business rule: final review approval is not the same as writing formal state.

### Behavior 2: Deferred final review blocks promotion

Given the final review decision is `defer`
When P7-J runs
Then it reports `blocked_by_final_review_decision`
And it does not expose any promotion scope.

Business rule: continuing the workflow must not silently approve a paper package.

### Behavior 3: Approval without reviewer or note blocks promotion

Given the final review decision says `approve`
But reviewer or note metadata is missing
When P7-J runs
Then it blocks promotion with human metadata reasons.

Business rule: final promotion paths need attributable human judgment.

### Behavior 4: Package manifest gaps block promotion

Given the final review decision is approved
But the package manifest has missing targets
When P7-J runs
Then it reports `blocked_by_package_manifest`.

Business rule: a broken package cannot enter formal writeback approval.

### Behavior 5: P7-J writes only preflight records

Given P7-J runs
When it writes outputs
Then it writes JSON and Markdown preflight records only
And does not write formal manuscript, product state, PDF, DOCX, DesignSpec, or RunPlan.

Business rule: this is still a gate, not a delivery writeback.

## Current Run Boundary

- Current status: `blocked_by_final_review_decision`.
- Current final review decision: `defer`.
- Can request formal writeback approval: `false`.
- Formal writeback allowed: `false`.
- Product state writeback allowed: `false`.
- Next action: obtain explicit human final review approval.
- Current promotion scope: empty because approval has not happened.
