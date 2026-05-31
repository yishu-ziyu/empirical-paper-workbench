# CGSS Exploratory Paper Assembler

## Stage

P6-J8 assembles the CGSS manuscript section drafts into one reviewable exploratory paper.

User-facing effect: this node turns the product from four separate section drafts into a full paper draft that can be read, reviewed, and routed to PDF preflight or revision planning.

## BDD Behaviors

### Behavior 1: Assembles ready sections into a full paper

Given the manuscript section package is review-ready
And the results evidence package is ready for paper draft input
And the literature review packet is reviewable
When P6-J8 runs
Then it writes a complete exploratory paper Markdown file.

Business rule: the product should let the user review one coherent paper draft, not only scattered section fragments.

### Behavior 2: Preserves the evidence chain

Given P6-J8 creates a full paper draft
When the assembly JSON is inspected
Then it records manuscript sections, model evidence, literature packet, method gate, citation placeholders, and bibliography candidate bindings.

Business rule: paper text must stay traceable to evidence and review packets.

### Behavior 3: Enforces a minimum reviewable draft length

Given the assembled paper is produced
When paper metrics are inspected
Then the Chinese character count must meet the minimum exploratory-paper threshold.

Business rule: a paper assembly node should not pass a thin stitched outline as a reviewable full draft.

### Behavior 4: Blocks incomplete inputs

Given the section package, results evidence package, or literature packet is not ready
When P6-J8 runs
Then it returns a blocked status and writes no full paper text.

Business rule: a full paper cannot be assembled from incomplete source packets.

### Behavior 5: Does not promote to formal manuscript state

Given P6-J8 completes successfully
When outputs are inspected
Then formal manuscript, verified bibliography, formal package, and `state/product/*` remain unchanged.

Business rule: exploratory assembly is a draft-layer operation, not formal paper promotion.

## Boundary Conditions

- Current real run creates `Manuscripts/generated/cgss_social_capital_happiness_paper.md`.
- Current real run reports `5399` Chinese characters against a minimum of `5000`.
- Current real run assembles 4 sections.
- The status remains `needs_human_exploratory_paper_review`.
- The next stage should be human full-paper review, PDF preflight, method gate review, or revision queue generation, not formal writeback.
