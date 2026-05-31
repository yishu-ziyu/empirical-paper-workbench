# CGSS Literature Review Draft Packet

## Stage

P6-I10 builds a reviewable literature review draft packet from CGSS verified bibliography candidates.

User-facing effect: this node turns bibliography candidates into a structured literature-review writing blueprint. It provides paragraph blocks, citation keys, draft claims, draft paragraphs, and reviewer focus points. It does not write the formal manuscript section.

## BDD Behaviors

### Behavior 1: Build pending literature review draft packet

Given bibliography candidates are reviewable
When P6-I10 builds the draft packet
Then it emits a pending literature-review packet with paragraph blocks, length plan, open dependencies, and promotion gating.

Business rule: draft writing can be prepared before formal approval, but it must remain visibly pending.

### Behavior 2: Map paragraphs to candidate sources and claims

Given source-checked candidates have citation keys and paper uses
When P6-I10 creates paragraph blocks
Then each block records source ids, citation keys, draft claim, draft paragraph, and review focus.

Business rule: downstream writing should know which claim each citation is allowed to support.

### Behavior 3: Keep unresolved sources as open dependencies

Given some sources still need manual or database verification
When P6-I10 builds the packet
Then those sources stay in `open_dependencies` and block promotion.

Business rule: unresolved source work must not disappear when drafting begins.

### Behavior 4: Block when bibliography candidates are not reviewable

Given bibliography candidates are missing or not in `needs_human_bibliography_approval`
When P6-I10 runs
Then it blocks and emits no paragraph blocks.

Business rule: literature drafting cannot start from invalid bibliography candidates.

### Behavior 5: Preserve formal-layer boundary

Given P6-I10 runs successfully
When it writes outputs
Then it writes only JSON/Markdown review artifacts and keeps manuscript sections, citation plans, formal bibliography, and product state untouched.

Business rule: this stage prepares a draft packet, not a formal manuscript writeback.

## Boundary Conditions

- P6-I10 consumes only the verified bibliography candidates package as its upstream literature artifact.
- P6-I10 emits paragraph blocks and review guidance only.
- P6-I10 keeps `promotion.allowed=false`.
- P6-I10 requires human approval before any literature section or citation plan write.
- P6-I10 must not write `Manuscripts/sections/literature-and-contribution.md`, citation plan, formal bibliography, formal manuscript, or `state/product/*`.
