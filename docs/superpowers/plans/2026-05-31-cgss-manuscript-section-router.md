# CGSS Manuscript Section Router

## Stage

P6-J7 routes CGSS model evidence and literature draft packets into reviewable manuscript sections.

User-facing effect: this node gives the product its first paper-shaped output for the CGSS lane. Instead of leaving the user with raw model JSON, it creates four reviewable section drafts with evidence bindings and review questions.

## BDD Behaviors

### Behavior 1: Routes ready evidence into section drafts

Given the results evidence package is `ready_for_paper_draft_input`
And the literature review draft packet is reviewable
When P6-J7 runs
Then it creates literature, data, empirical strategy, and main results sections.

Business rule: paper drafting should consume structured evidence and literature packets, not ad hoc prose.

### Behavior 2: Blocks when model evidence is not ready

Given the results evidence package is missing or blocked
When P6-J7 runs
Then it returns `blocked_missing_results_evidence_package` and writes no section drafts.

Business rule: manuscript sections cannot be generated from incomplete model evidence.

### Behavior 3: Keeps sections in draft review state

Given P6-J7 creates section drafts
When the package is inspected
Then status is `needs_human_manuscript_section_review` and each section is `section_draft_ready_for_review`.

Business rule: generated sections need human review before assembly.

### Behavior 4: Preserves evidence bindings

Given P6-J7 writes a section
When the section is inspected
Then it contains explicit evidence bindings, citation placeholders, review notes, and human review questions.

Business rule: every section must remain auditable back to its sources.

### Behavior 5: Does not write formal manuscript state

Given P6-J7 completes successfully
When outputs are inspected
Then formal manuscript, verified bibliography, formal package, and `state/product/*` remain unchanged.

Business rule: section routing is a draft-layer operation, not final paper promotion.

## Boundary Conditions

- Current real run creates 4 reviewable sections.
- Current real run reports `2996` total Chinese characters in the JSON package.
- Current generated section files total `6036` characters by `wc -m`.
- Literature citations remain placeholders until citation binding review.
- The next stage should be human section review, not formal manuscript writeback.
