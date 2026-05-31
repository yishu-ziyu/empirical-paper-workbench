# CGSS Literature Source Verification Preflight

## Stage

P6-I8 builds a source-verification preflight from the CGSS literature seed package.

User-facing effect: this node turns candidate literature into a checklist of what must be verified before any citation can be treated as usable. It does not create a verified bibliography and does not write the manuscript.

## BDD Behaviors

### Behavior 1: Build source verification queue

Given the literature seed package is reviewable
When P6-I8 builds the preflight
Then it emits candidate bibliography records, manual review queue, CNKI queue, and Zotero/Scholar metadata queue.

Business rule: candidate sources need explicit verification work before they can support the paper.

### Behavior 2: Classify verification actions by source type

Given seed sources include official data, classic theory, measurement standards, Chinese literature, and method references
When P6-I8 creates candidate records
Then it assigns source-specific actions such as official page opening, DOI/publisher verification, CNKI/journal-page checking, and Zotero/Scholar lookup.

Business rule: different source types require different evidence checks.

### Behavior 3: Block when seed package is not reviewable

Given the literature seed package is missing or not in `needs_human_literature_review`
When P6-I8 runs
Then it blocks and produces no candidate bibliography.

Business rule: source verification cannot start from an invalid seed package.

### Behavior 4: Preserve formal-layer boundary

Given P6-I8 runs successfully
When it writes outputs
Then it writes only JSON/Markdown review artifacts and keeps verified bibliography, formal bibliography, manuscript, contribution matrix, and product state untouched.

Business rule: preflight is a checklist, not source verification completion.

## Boundary Conditions

- P6-I8 consumes only `cgss_social_capital_happiness_literature_seed_package.json`.
- P6-I8 emits candidate records and verification queues only.
- P6-I8 keeps `promotion.allowed=false`.
- P6-I8 must not write verified bibliography, contribution matrix, formal bibliography, formal manuscript, or `state/product/*`.
