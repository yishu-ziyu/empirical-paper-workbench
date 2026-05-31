# Topic-To-Paper Capability Audit

## Stage

P6-J1 audits whether a requested research topic can enter the paper-package workflow.

User-facing effect: this node prevents the product from pretending that any new topic can immediately become a paper. For the current CGSS social-capital and happiness topic, it explains that the first missing piece is topic-to-data binding.

## BDD Behaviors

### Behavior 1: Existing ready package reports remaining review gaps

Given the requested topic matches the current formal package
When P6-J1 audits the topic
Then it reports the formal package is reproducible with human review and lists remaining structure, literature, method, and revision gaps.

Business rule: a ready package is not the same as a fully accepted final paper.

### Behavior 2: Block before review when the formal package is not ready

Given the formal package summary is blocked
When P6-J1 audits any topic
Then it returns `blocked_before_paper_package_review` and preserves the blocking reasons.

Business rule: topic-level audit cannot skip package readiness.

### Behavior 3: New CGSS topic outputs a plain-language gap matrix

Given the current formal project is not the CGSS social-capital and happiness topic
When P6-J1 audits the CGSS topic
Then it returns `new_topic_requires_data_binding`, explains the target paper-package level, and lists the five capability gaps.

Business rule: new-topic onboarding must start with data, variables, methods, literature, and revision evidence, not direct drafting.

### Behavior 4: New CGSS topic routes first to DataAgent

Given the new topic points to CGSS
When P6-J1 builds agent routing
Then it sets `first_agent_to_call=DataAgent` and recommends `run_cgss_data_discovery`.

Business rule: data binding is the first reliable step for a new empirical topic.

### Behavior 5: Audit does not write formal state

Given P6-J1 writes JSON and Markdown review artifacts
When the command completes
Then it does not generate a paper, modify the formal package, accept the package, or write `state/product/*`.

Business rule: this is a diagnostic gate, not a formal writeback step.

## Boundary Conditions

- Current real CGSS topic is not the same as the existing robot labor-market package.
- Exit code `3` means the new topic needs data binding.
- P6-J1 emits a gap matrix and next CLI nodes.
- P6-J1 must not write formal package artifacts, formal research state, or product-state acceptance.
